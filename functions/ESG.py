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

    nb_of_rows_before_removing_nans = esg_company_data.shape[0]
    nb_of_cells_before_removing_nans = esg_company_data.size

    # remove rows with no data for ESG score
    esg_company_data.dropna(axis=0, how='all', 
                            subset=column_names_esg_company_data[1:8], inplace=True)
    
    nb_of_rows_after_removing_nans = esg_company_data.shape[0]

    #converting all numbers to floats 
    for column_name in column_names_esg_company_data[1:8]:
        esg_company_data[column_name] = esg_company_data[column_name].astype(float)

    nb_of_nans_left = esg_company_data.isna().sum().sum()

    # interpolate data that is missing
    esg_company_data.iloc[:,1:] = esg_company_data.iloc[:,1:].interpolate(method='linear', axis=1, limit_direction='both',
                                                                          inplace=False)

    # reset the indexes
    esg_company_data = esg_company_data.reset_index()
    esg_company_data = esg_company_data.drop(columns=["index"])

    print("nb of rows without ESG scores: ", (nb_of_rows_before_removing_nans-nb_of_rows_after_removing_nans))
    print("percentage of rows without ESG scores: ", 
                (nb_of_rows_before_removing_nans-nb_of_rows_after_removing_nans)/nb_of_rows_before_removing_nans)
    print("nb of nans filled in using interpolation: ", nb_of_nans_left)
    print("percentage of nans filled in using interpolation: ", nb_of_nans_left/nb_of_cells_before_removing_nans)
    
    return esg_company_data

def get_ESG_scores_per_year(years_issuer_bought, esg_company_data_holdings):
    esg_company_data_holdings_with_years = years_issuer_bought.merge(esg_company_data_holdings,"inner","ISSUER")

    esg_scores_per_year = {'2017':[],'2018':[],'2019':[],'2020':[],'2021':[]}

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

def average_company_esg_score_plot(years_issuer_bought, esg_company_data_holdings,esg_company_data_eligible):
    """ Make a plot of esg scores per year, comparing eligible and holdings
    
    For the eligible universe, it plots the evolution of the mean of ESG scores of the 
    companies that have sufficient data available. For holdings, it plots the mean ESG 
    score of companies that ECB bought bonds of that year."""

    mean_ESG_holdings, error_ESG_holdings = get_average_and_std_esg_per_year(years_issuer_bought, esg_company_data_holdings)

    mean_ESG_eligible = esg_company_data_eligible.mean().values
    error_ESG_eligible = esg_company_data_eligible.std().values

    plt.figure(figsize=(10,5))

    years_holdings = range(2017,2022)
    years_eligible = range(2015,2022)

    plt.errorbar(x=years_holdings,y=mean_ESG_holdings,yerr=error_ESG_holdings,capsize=10,
                                    label="average of holdings invested in during that year")
    plt.errorbar(x=years_eligible,y=mean_ESG_eligible,yerr=error_ESG_eligible,capsize=10,
                                    label="data on companies in eligible universe")

    plt.title("Comparison of the ESG scores of the companies that the ECB invested in vs. the eligible universe\n")
    plt.xlabel("Years")
    plt.ylabel("ESG score")
    plt.xticks(years_eligible)
    plt.ylim(0,100)
    plt.legend()

    plt.show()