import os
import pandas as pd

def get_eikon_data_folder():
    path = __file__
    parent = os.path.join(path, os.pardir)
    parent = os.path.join(parent, os.pardir)
    return parent + "/data/"

eikon_data_folder = get_eikon_data_folder()

def get_eikon_data_general():
    eikon_data_environment = pd.read_csv(eikon_data_folder+"holdingsECBEnvironment.txt",sep="\t")
    # TODO: remove right, empty columns from data frame
    eikon_data_general = pd.read_csv(eikon_data_folder+"holdingsECBGeneralInfo.txt",sep="\t")
    return [eikon_data_environment, eikon_data_general]

eikon_data_environment, eikon_data_general = get_eikon_data_general()

def get_eikon_data_complete():
    eikon_data_complete = eikon_data_general.merge(eikon_data_environment, "left", "ISIN") #append environment
    eikon_data_complete.rename(columns={'CO2.1': 'CO2_1'}, inplace=True) #changed column name to prevent syntax errors
    return eikon_data_complete

def get_data_eligible_complete():
    eligible_environment = pd.read_csv(get_eikon_data_folder()+"eligibleUniverseEnvironment.txt",sep="\t")
    eligible_general = pd.read_csv(eikon_data_folder+"eligibleUniverseGeneralInfo.txt",sep="\t")
    eligible_complete = eligible_general.merge(eligible_environment, "left", "ISIN")
    eligible_complete.rename(columns={"Issuer": "ISSUER"}, inplace=True)
    return eligible_complete

# Read the dates
def get_dates():
    holdings_date_info = pd.read_csv(eikon_data_folder+"holdingsECBDates.csv",sep="\t")
    holdings_date_info["Date"] = pd.to_datetime(holdings_date_info["Date"])
    return holdings_date_info

# Get a dataframe with issuers and their list of years in which the ECB bought their bonds
def get_dates_data_frame():
    # make a dictionary: key = ISSUER, value is list of years in which it was bought
    years_issuer_bought = {}
    for index,row in get_dates().merge(eikon_data_general[["ISSUER","ISIN"]],"left","ISIN").iterrows():
        issuer = row["ISSUER"]
        year = row["Date"].year
        if issuer in years_issuer_bought:
            if year not in years_issuer_bought[issuer]:
                years_issuer_bought[issuer].append(year)
        else:
            years_issuer_bought[issuer] = [year]

    # convert dictionary to pd.DataFrame
    matrixData = []
    for issuer, years in years_issuer_bought.items():
        item = [issuer] + [years]
        matrixData.append(item)
    years_issuer_bought = pd.DataFrame(matrixData,columns=["ISSUER","YEARS"])
    return years_issuer_bought


