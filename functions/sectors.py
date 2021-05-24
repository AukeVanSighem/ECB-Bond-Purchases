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
        "Technology Equipment": 0
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
    sector_mappings_with_years = sector_mappings_with_years.reindex(columns = columns_of_interest)
    return sector_mappings_with_years

def get_number_bonds_bought_by_sector_over_years(sector, sector_mappings, years_issuer_bought):
    sector_mappings_with_years = get_sector_mappings_with_years(sector_mappings, years_issuer_bought)
    companies_in_sector = sector_mappings_with_years[sector_mappings_with_years["hasPrimaryBusinessSector"]==sector]
    year_x_count = {"2017": 0, "2018": 0, "2019": 0, "2020": 0, "2021": 0}
    for company_index in companies_in_sector.index:
        for year_x in ["2017", "2018", "2019", "2020", "2021"]:
            for year in sector_mappings_with_years["YEARS"][company_index]:
                if str(year) == str(year_x):
                    year_x_count[year_x] += 1
    return year_x_count

# Get number of companies of which bonds were bought per sector per year
def get_number_companies_bonds_bought_per_year(primary_business_sector, sector_mappings, years_issuer_bought):
    # sectors_spaghetti_data_frame = pd.DataFrame({'x': range(2017,2022)})
    sectors_spaghetti_data_frame = pd.DataFrame({'x': ["2017", "2018", "2019", "2020", "2021"]})
    for sector in primary_business_sector.index:
        sectors_spaghetti_data_frame[sector] = [0,0,0,0,0]
        year_x_count_sector = get_number_bonds_bought_by_sector_over_years(sector, sector_mappings, years_issuer_bought)
        for i in range(0, len(sectors_spaghetti_data_frame["x"])):
            sectors_spaghetti_data_frame[sector][i] = year_x_count_sector[str(i+2017)]
    return sectors_spaghetti_data_frame

# spaghetti plot of number bonds bought per sector
# primary_business_sector = Pandas data frame with the entire counts of sectors in which the ECB invested to calculate percentages
# sector_mappings = Pandas data frame with all the information on all the bought bonds: Issuer, LEI, hasPrimaryBusinessSector, ...
# years_issuer_bought = Pandas data frame with for every issuer the years in which their bonds were bought
# sectors_to_show = Pandas data frame of indexes representing every sector for which a line should be shown in the plot. If no parameter is given,
# all the sectors from the primary_business_sector data frame
def draw_spaghetti_plot_sectors(primary_business_sector, sector_mappings, years_issuer_bought, sectors_to_show = pd.DataFrame()):
    if sectors_to_show.empty:
        sectors_to_show = primary_business_sector.index

    sectors_spaghetti_data_frame = get_number_companies_bonds_bought_per_year(primary_business_sector, sector_mappings, years_issuer_bought)
    total_count = [1] * len(sectors_spaghetti_data_frame["x"])
    for i in range(0, len(total_count)):
        if (summation_row := sum(sectors_spaghetti_data_frame.loc[i, sectors_spaghetti_data_frame.columns != "x"])) != 0: # Avoid division by zero
            total_count[i] = summation_row

    plt.style.use('seaborn-darkgrid')
    palette = plt.get_cmap('Set1')
    plt.figure(figsize=(20,10))

    # Change line style every 10 sectors
    i = 0
    line_style = '-'
    for column in sectors_to_show:
        i += 1
        if (i > 10):
            if (i <= 20): 
                line_style = ':'
            elif (i <= 30):
                line_style = '-.'

        y = sectors_spaghetti_data_frame[column]/total_count*100
        plt.plot(sectors_spaghetti_data_frame["x"], y, marker='', linewidth=1, alpha=0.9, label=column, linestyle = line_style)
   
    plt.legend()
    plt.xlabel("Time (years)")
    plt.ylabel("Percentage of bonds (%)")
    plt.title("Percentage of bonds bought over the years in different sectors.")
    plt.show()
    plt.close()