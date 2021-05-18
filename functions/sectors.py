import pandas as pd
import matplotlib.pyplot as plt


# Returns a dictionary with all the sectors from PermID (https://en.wikipedia.org/wiki/The_Refinitiv_Business_Classification) and gives every sector a score for greennes.
# -1 means not green
# 0 means neutral
# 1 means green
def get_sector_green_dict():
    dictionary = {
        # Primary business sector
        "Energy - Fossil Fuels": -1,
        "Renewable Energy": 1,
        "Uranium": 1,
        "Chemicals": -1,
        "Mineral Resources": -1,
        "Applied Resources": -1,
        "Industrial Goods": -1,
        "Industrial & Commercial Services": 0,
        "Transportation": 1,
        "Automobiles & Auto Parts": -1,
        "Cyclical Consumer Products": -1,
        "Cyclical Consumer Services": 0,
        "Retailers": 0,
        "Food & Beverages": 0,
        "Personal & Household Products & Services": 0,
        "Food & Drug Retailing": 0,
        "Consumer Goods Conglomerates": 0,
        "Banking & Investment Services": 0,
        "Insurance": 0,
        "Collective Investments": 0,
        "Investment Holding Companies": 0,
        "Healthcare Services & Equipment": 0,
        "Pharmaceuticals & Medical Research": 0,
        "Technology Equipment": 0,
        "Software & IT Services": 0,
        "Financial Technology (Fintech) & Infrastructure":  0,
        "Telecommunications Services": 0,
        "Utilities": 1,
        "Real Estate": 0,
        "Institutions, Associations & Organizations": 0,
        "Government Activity": 0,
        "Academic & Educational Services": 0,
        "Technology Equipment": 0,
        # Primary economic sector
        "Energy": -1,
        "Basic Materials": -1, # Materials
        "Capital Goods": -1,
        "Commercial and Professional Services": 0,
        "Automobiles and Components": -1,
        "Consumer Durables and Apparel": -1,
        "Consumer Services": 0,
        "Retailing": 0,
        "Food, Beverage, and Tobacco": 0,
        "Household and Personal Products": 0,
        "Food and Staples Retailing": 0,
        "Household and Personal Products": 0,
        "Banks": 0,
        "Insurance": 0,
        "Financials": 0, # Diversified Financials
        "Healthcare": 0, # Health Care Equipment and Services
        "Pharmaceuticals, Biotechnology, and Life Sciences": 0,
        "Technology": 0, # Technology Hardware and Equipment
        "Software and Services": 0,
        "Telecommunications Services": 0,
        "Semiconductors & Semiconductor Equipment": 0
    }
    return dictionary

def map_green_dict_to_data_frame(data_frame):
    new_data_frame = data_frame.copy()
    new_data_frame["green"] = None # Default greenness of sector is None
    for i in range(0, new_data_frame.shape[0]):
            if data_frame.index[i] in get_sector_green_dict().keys():
                new_data_frame.loc[data_frame.index[i], "green"] = get_sector_green_dict()[data_frame.index[i]]
    return new_data_frame

def get_sector_mappings_with_years(sector_mappings, years_issuer_bought):
    sector_mappings_with_years = sector_mappings.merge(years_issuer_bought, how = "left", on = "ISSUER")
    columns_of_interest = ["ISSUER", "LEI", "hasPrimaryBusinessSector", "hasPrimaryEconomicSector", "hasPrimaryIndustryGroup", "number", "YEARS"]
    sector_mappings_with_years.loc[:, columns_of_interest]
    return sector_mappings_with_years

def get_number_bonds_bought_by_sector_over_years(sector, sector_mappings, years_issuer_bought):
    sector_mappings_with_years = get_sector_mappings_with_years(sector_mappings, years_issuer_bought)
    companies_in_sector = sector_mappings_with_years[sector_mappings_with_years["hasPrimaryBusinessSector"]==sector]
    year_x_count = {"2015": 0, "2016": 0, "2017": 0, "2018": 0, "2019": 0, "2020": 0, "2021": 0}
    for company_index in companies_in_sector.index:
        for year_x in ["2015", "2016", "2017", "2018", "2019", "2020", "2021"]:
            for year in sector_mappings_with_years["YEARS"][company_index]:
                if str(year) == str(year_x):
                    year_x_count[year_x] += 1
    return year_x_count

# Get number of companies of which bonds were bought per sector per year
def get_number_companies_bonds_bought_per_year(primary_business_sector, sector_mappings, years_issuer_bought):
    sectors_spaghetti_data_frame = pd.DataFrame({'x': range(2015,2022)})
    for sector in primary_business_sector.index:
        sectors_spaghetti_data_frame[sector] = [0,0,0,0,0,0,0]
        year_x_count_sector = get_number_bonds_bought_by_sector_over_years(sector, sector_mappings, years_issuer_bought)
        for x in sectors_spaghetti_data_frame.x:
            sectors_spaghetti_data_frame[sector][x-2015] = year_x_count_sector[str(x)]
    return sectors_spaghetti_data_frame

# spaghetti plot of number bonds bought per sector 
def draw_spaghetti_plot_sectors(primary_business_sector, sector_mappings, years_issuer_bought):
    sectors_spaghetti_data_frame = get_number_companies_bonds_bought_per_year(primary_business_sector, sector_mappings, years_issuer_bought)
    plt.style.use('seaborn-darkgrid')
    palette = plt.get_cmap('Set1')

    #spaghetti plot of CO2 emissions 
    plt.figure(figsize=(20,20))
    for column in sectors_spaghetti_data_frame.drop(columns=["x"], axis=1):
        plt.plot(sectors_spaghetti_data_frame["x"], sectors_spaghetti_data_frame[column], marker='', linewidth=1, alpha=0.9)
        
    plt.show()