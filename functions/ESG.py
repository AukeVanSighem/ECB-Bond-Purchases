import matplotlib.pyplot as plt
import numpy as np

def cleaning_esg_data(df):
    column_names_esg_company_data = ["ISSUER", "ESG Score 2015", "ESG Score 2016", "ESG Score 2017", 
                                "ESG Score 2018", "ESG Score 2019", "ESG Score 2020", 
                                "ESG Score 2021"]
    #started cleaning data as above 
    esg_data = df[column_names_esg_company_data]
    esg_company_data = esg_data.drop_duplicates(subset= ["ISSUER"])
    esg_company_data = esg_company_data.replace(to_replace = '[,]', value ='.', regex=True)

    # replace zeros with nans, as these are easier to replace
    esg_company_data = esg_company_data.replace(to_replace = '0', value = np.nan) 

    # remove rows with no data for ESG score
    esg_company_data.dropna(axis=0, how='all', 
                            subset=column_names_esg_company_data[1:8], inplace=True)

    #converting all numbers to floats 
    for column_name in column_names_esg_company_data[1:8]:
        esg_company_data[column_name] = esg_company_data[column_name].astype(float)

    # interpolate data that is missing
    esg_company_data.iloc[:,1:] = esg_company_data.iloc[:,1:].interpolate(method='linear', axis=1, limit_direction='both',
                                                                          inplace=False)
    #TODO: If we want to keep this apart, we can make a new variable holding the filled in dataframe

    # reset the indexes
    esg_company_data = esg_company_data.reset_index()
    esg_company_data = esg_company_data.drop(columns=["index"])
    
    return esg_company_data

def plot_ESG(esg_company_data_holdings):
    plt.figure(figsize=(10,10))
    years = range(2015,2022)
    for index,row in esg_company_data_holdings.iterrows():
        plt.plot(years,row[1:8])
    plt.show()

def plot_ESG_error_bars(esg_company_data_eligible, esg_company_data_holdings):
    plt.figure(figsize=(10,5))

    years = range(2015,2022)

    mean_holdings = esg_company_data_holdings.mean().values
    error_holdings = esg_company_data_holdings.std().values

    mean_eligible = esg_company_data_eligible.mean().values
    error_eligible = esg_company_data_eligible.std().values

    plt.errorbar(years, mean_holdings, yerr=error_holdings, ecolor='r', capsize=10, label="holdings")

    plt.errorbar(years, mean_eligible, yerr=error_eligible, ecolor='y', capsize=10, label="eligible")

    plt.legend()

    plt.show()