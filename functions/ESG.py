import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

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

def linReg_esg_company_data(esg_company_data):
    list_of_coef = []
    list_of_intercepts = []
    years = np.arange(0,7)
    # We will use the module Linear Regression of sklearn to perform the analysis
    # Initialize the model
    ols = LinearRegression()
    # Fit the model to the data
    for index,row in esg_company_data.iterrows():
        resultOfFit = ols.fit(years.reshape(-1, 1),row[1:8])
        list_of_coef.append(resultOfFit.coef_[0])
        list_of_intercepts.append(resultOfFit.intercept_)
    return list_of_coef,list_of_intercepts

def get_list_of_coef_holdings(esg_company_data_eligible, esg_company_data_holdings):
    list_of_coef_holdings, list_of_intercepts_holdings = linReg_esg_company_data(esg_company_data_holdings)
    list_of_coef_eligible, list_of_intercepts_eligible = linReg_esg_company_data(esg_company_data_eligible)
    return list_of_coef_holdings, list_of_intercepts_holdings, list_of_coef_eligible, list_of_intercepts_eligible

def coefficients_box_plot(esg_company_data_eligible, esg_company_data_holdings):
    list_of_coef_holdings, list_of_intercepts_holdings, list_of_coef_eligible, list_of_intercepts_eligible = get_list_of_coef_holdings(esg_company_data_eligible, esg_company_data_holdings)
    plt.figure()

    plt.boxplot([list_of_coef_holdings, list_of_coef_eligible], "y")
    plt.xticks(ticks=[1,2], labels=["holdings", "eligible"])

    plt.show()

def covariance_matrix_plot(esg_company_data_eligible, esg_company_data_holdings):
    list_of_coef_holdings, list_of_intercepts_holdings, list_of_coef_eligible, list_of_intercepts_eligible = get_list_of_coef_holdings(esg_company_data_eligible, esg_company_data_holdings)
    plt.figure()

    plt.plot(list_of_intercepts_holdings,list_of_coef_holdings, 'b.')
    plt.plot(list_of_intercepts_eligible,list_of_coef_eligible, 'y.')

    plt.show()

def get_correlation_coefficients(esg_company_data_eligible, esg_company_data_holdings):
    list_of_coef_holdings, list_of_intercepts_holdings, list_of_coef_eligible, list_of_intercepts_eligible = get_list_of_coef_holdings(esg_company_data_eligible, esg_company_data_holdings)
    
    print("holdings:\n", np.corrcoef(list_of_coef_holdings, list_of_intercepts_holdings),
      "\n eligible:\n", np.corrcoef(list_of_coef_eligible, list_of_intercepts_eligible))

def get_ESG_scores_per_year(years_issuer_bought, esg_company_data_holdings):
    esg_company_data_holdings_with_years = years_issuer_bought.merge(esg_company_data_holdings,"inner","ISSUER")

    esg_scores_per_year = {'2015':[],'2016':[],'2017':[],'2018':[],'2019':[],'2020':[],'2021':[]}

    for index,row in esg_company_data_holdings_with_years.iterrows():
        years = row["YEARS"]
        for year in years:
            year = str(year)
            esg_scores_per_year[year].append(row["ESG Score "+year])
    return esg_scores_per_year

def get_average_and_std_esg_per_year(years_issuer_bought, esg_company_data_holdings):
    average_esg_per_year = []
    std_esg_per_year = []
    esg_scores_per_year = get_ESG_scores_per_year(years_issuer_bought, esg_company_data_holdings)
    for key in esg_scores_per_year.keys():
        average_esg_per_year.append(np.mean(esg_scores_per_year[key]))
        std_esg_per_year.append(np.std(esg_scores_per_year[key]))
    return average_esg_per_year, std_esg_per_year

def average_company_esg_score_plot(years_issuer_bought, esg_company_data_holdings):
    average_esg_per_year, std_esg_per_year = get_average_and_std_esg_per_year(years_issuer_bought, esg_company_data_holdings)

    plt.figure()

    years = range(2015,2022)

    plt.errorbar(x=years,y=average_esg_per_year,yerr=std_esg_per_year,capsize=10)

    plt.title("Average ESG score of the companies that the ECB invested in during that year\n")
    plt.xlabel("Years")
    plt.ylabel("ESG score")
    plt.xticks(years)
    plt.ylim(0,100)

    plt.show()