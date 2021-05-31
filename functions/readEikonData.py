import os
import pandas as pd

# The path to the folder in the S3 bucket in which the data is stored
eikon_data_folder = "https://s3groupsweden.s3.eu-central-1.amazonaws.com/Data/EIKON/"

# Get dataframes with the data in the files holdingsECBEnvironment.txt and holdingsECBGeneralInfo.txt
def get_eikon_data_general():
    eikon_data_environment = pd.read_csv(eikon_data_folder+"holdingsECBEnvironment.txt",sep="\t")
    eikon_data_environment.dropna(axis=1, how='all', inplace=True) # Remove empty columns at the end of the file
    eikon_data_general = pd.read_csv(eikon_data_folder+"holdingsECBGeneralInfo.txt",sep="\t")
    eikon_data_general.dropna(axis=1, how='all', inplace=True) # Remove empty columns at the end of the file
    return [eikon_data_environment, eikon_data_general]

eikon_data_environment, eikon_data_general = get_eikon_data_general()

# Get the data in which the ECB invested from EIKON in one dataframe
def get_eikon_data_complete():
    eikon_data_complete = eikon_data_general.merge(eikon_data_environment, "left", "ISIN") #append environment
    eikon_data_complete.rename(columns={'CO2.1': 'CO2_1'}, inplace=True) #changed column name to prevent syntax errors
    return eikon_data_complete

# Get the data from the eligible universe in one dataframe
def get_data_eligible_complete():
    eligible_environment = pd.read_csv(eikon_data_folder+"eligibleUniverseEnvironment.txt",sep="\t")
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


def get_dates_isin_data_frame():
    years_isin_bought = {}
    for index,row in get_dates().merge(eikon_data_general[["ISSUER","ISIN"]],"left","ISIN").iterrows():
        isin = row["ISIN"]
        year = row["Date"].year
        if isin in years_isin_bought:
            if year not in years_isin_bought[isin]:
                years_isin_bought[isin].append(year)
        else:
            years_isin_bought[isin] = [year]

    # convert dictionary to pd.DataFrame
    matrixDatai = []
    for isin, years in years_isin_bought.items():
        item = [isin] + [years]
        matrixDatai.append(item)
    years_isin_bought = pd.DataFrame(matrixDatai,columns=["ISIN","YEARS"])
    return years_isin_bought