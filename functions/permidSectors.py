from re import S
from OpenPermID import OpenPermID
import geocoder
import pandas as pd
import numpy as np
import os

# Gain access to the permid database
opid = OpenPermID()
opid.set_access_token("r95vEAhvmucG8iNGtsP17hjbgUGMhz4j")

# Get Eikon information on holdings
def get_holdings_Eikon(s3Directory):
    holdingsEikon = pd.read_csv(s3Directory + "Data/EIKON/holdingsECBGeneralInfo.txt",sep="\t").iloc[:, :-3]
    holdingsEikon.rename(columns = {'Legal Entity ID': 'LEI'}, inplace = True)
    return holdingsEikon


# Get a dataframe with a non-redundant list of all the company names and their legal entity ID.
def get_companies_LEI(holdingsECB):
    companies_LEI = holdingsECB[['ISIN', 'ISSUER']].merge(get_holdings_Eikon()[['ISIN', 'LEI']], how = 'left', on = 'ISIN')
    companies_LEI = companies_LEI[['ISSUER', 'LEI']].drop_duplicates('ISSUER')
    return companies_LEI

def get_LEI_mappings():
    LEIs = get_holdings_Eikon()['LEI'].dropna().astype('string').unique()

    lei_input = pd.DataFrame({})
    localID = 1
    for lei in LEIs:
        lei_input = lei_input.append(pd.DataFrame({'LocalID': localID, 'Standard Identifier': 'LEI:' + lei}, index = [0]))
        localID += 1
        
    while True:
        try:    
            lei_df, err = opid.match(lei_input)
            break
        except JSONDecodeError:
            continue

    lei_mappings = pd.DataFrame({})
    lei_mappings['LEI'] = pd.Series(LEIs)
    lei_mappings['CompanyName'] = lei_df['Match OrgName']
    lei_mappings = pd.concat([lei_mappings, lei_df['Match OpenPermID'].astype('string').apply(lambda x: x.split('/')[-1])], axis = 1)
    lei_mappings.rename(columns = {'Match OpenPermID': 'PermID'}, inplace = True)
    return lei_mappings

def get_sector_lookups():
    permids = get_LEI_mappings().PermID.astype('string')
    sector_lookups = pd.DataFrame({})
    unsuccessful_lookups = []

    for permid in permids:
        
        # In case of connection error, allow it to try at most 5 times
        err, count = 0, 0
        while (err != None and count < 5):
            try:
                count = count - 1
                output, err = opid.lookup(permid)
            except JSONDecodeError:
                continue
        if err != None:
            unsuccessful_lookups.append(permid)
            continue

        if "hasPrimaryBusinessSector" in output.columns:
            sector_info = output.loc[:, 'hasPrimaryBusinessSector': 'hasPrimaryIndustryGroup']
            sector_info = sector_info.applymap(lambda x: x.split('/')[-1])
        if "isIncorporatedIn" in output.columns:
            loc_info = output.loc[:, 'isIncorporatedIn': 'isDomiciledIn']
            loc_info = loc_info.applymap(lambda x: x.split('/')[-2])
            
        row = pd.DataFrame({'PermID': [permid]})
        row = pd.concat([row, sector_info], axis = 1) if type(sector_info) == pd.DataFrame else row
        row = pd.concat([row, loc_info], axis = 1) if type(loc_info) == pd.DataFrame else row
        sector_lookups = sector_lookups.append(row)
        
        sector_info, loc_info = None, None

    return sector_lookups

def convert_sector_lookups():
    sector_lookups = get_sector_lookups()
    sector_lookups_converted = sector_lookups.copy()
    sector_types = sector_lookups.columns[1:4]
    for sector_type in sector_types:
        sector_dict = {}
        sectors = sector_lookups.loc[:, sector_type].dropna().astype('string').unique()
        for sector in sectors:
            while True:
                try:
                    output, err = opid.lookup(sector)
                    break
                except JSONDecodeError:
                    continue
            sector_dict[sector] = output.iloc[0, -1]
        sector_lookups_converted[sector_type] = sector_lookups[sector_type].fillna('missing').astype('string').apply(lambda x: np.NaN if x == 'missing' else sector_dict[x])

    loc_types = sector_lookups.columns[4:]
    for loc_type in loc_types:
        loc_dict = {}
        locs = sector_lookups.loc[:, loc_type].dropna().astype('string').unique()
        for loc in locs:
            g = geocoder.geonames(loc, method='details', key='brian1998716')
            loc_dict[loc] = g.address
        sector_lookups_converted[loc_type] = sector_lookups[loc_type].fillna('missing').astype('string').apply(lambda x: np.NaN if x == 'missing' else loc_dict[x])

    return sector_lookups_converted

def get_sector_mappings(holdingsECB):
    path = __file__
    parent = os.path.join(path, os.pardir)
    parent = os.path.join(parent, os.pardir)
    if not (os.path.isfile(parent+'\output\sector_mappings_data.xlsx')):
        sector_mappings = get_LEI_mappings().merge(convert_sector_lookups(), how = 'left', on = 'PermID')
        sector_mappings = get_companies_LEI(holdingsECB).merge(sector_mappings, how = 'left', on = 'LEI')
        sector_mappings.to_excel(parent+'\output\sector_mappings_data.xlsx', engine='xlsxwriter')
    else:
        sector_mappings = pd.read_excel(parent+'\output\sector_mappings_data.xlsx', header=0)
    return sector_mappings