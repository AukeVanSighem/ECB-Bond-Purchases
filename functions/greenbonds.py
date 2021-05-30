import pandas as pd
import matplotlib.pyplot as plt

from functions import downloadECBBonds
from functions import readEikonData

holdingsECB = downloadECBBonds.download_ECB_Bonds()

def compareGreenbondsEuronextvsEIKON():
    euronext_greenbonds = pd.read_excel("data/Euronext-Green-Bond-List.xlsx", header=0)
    ecb_euronext_greenbonds = holdingsECB[(holdingsECB["ISIN"].isin(euronext_greenbonds["ISIN"]))]
    
    EIKON_greenbonds = readEikonData.eikon_data_environment[["ISIN", "Green Bond Flag"]]
    EIKON_greenbonds= EIKON_greenbonds.rename(columns={'Green Bond Flag' : 'Green_Bond_Flag'})

    EIKON_greenbonds = EIKON_greenbonds[(EIKON_greenbonds.Green_Bond_Flag == "Y")]

    ecb_EIKON_greenbonds = holdingsECB[(holdingsECB["ISIN"].isin(EIKON_greenbonds["ISIN"]))]
    print("Euronext greenbonds: " + str(len(ecb_euronext_greenbonds.index)) + " vs EIKON greenbonds: " + str(len(ecb_EIKON_greenbonds.index)))

def get_number_greenbonds_with_year():
    EIKON_greenbonds = readEikonData.eikon_data_environment[["ISIN", "Green Bond Flag"]]
    EIKON_greenbonds= EIKON_greenbonds.rename(columns={'Green Bond Flag' : 'Green_Bond_Flag'})

    EIKON_greenbonds = EIKON_greenbonds[(EIKON_greenbonds.Green_Bond_Flag == "Y")]

    ecb_EIKON_greenbonds = holdingsECB[(holdingsECB["ISIN"].isin(EIKON_greenbonds["ISIN"]))]

    greenbonds_with_year = ecb_EIKON_greenbonds.merge(readEikonData.get_dates_isin_data_frame(), how ="left", on = "ISIN")
    year_x_count = {"2017": 0, "2018": 0, "2019": 0, "2020": 0, "2021": 0}
    for greenbonds_index in greenbonds_with_year.index:
        for year_x in ["2017", "2018", "2019", "2020", "2021"]:
            for year in greenbonds_with_year["YEARS"][greenbonds_index]:
                if str(year) == str(year_x):
                    year_x_count[year_x] += 1
    return year_x_count

def get_number_bonds_with_year():
    bonds_with_year = holdingsECB.merge(readEikonData.get_dates_isin_data_frame(), how = "left", on = "ISIN")
    year_x_count = {"2017": 0, "2018": 0, "2019": 0, "2020": 0, "2021": 0}
    for bonds_index in bonds_with_year.index:
        for year_x in ["2017", "2018", "2019", "2020", "2021"]:
            for year in bonds_with_year["YEARS"][bonds_index]:
                if str(year) == str(year_x):
                    year_x_count[year_x] += 1
    return year_x_count

def get_percentages_greenbonds_on_bonds_per_year():
    number_bonds_with_year_dataframe = pd.DataFrame({'year' : list(get_number_bonds_with_year().keys()), 'count' : list(get_number_bonds_with_year().values())})
    number_greenbonds_with_year_dataframe = pd.DataFrame({'year' : list(get_number_greenbonds_with_year().keys()), 'count' : list(get_number_greenbonds_with_year().values())})

    data = [number_greenbonds_with_year_dataframe["year"], ((number_greenbonds_with_year_dataframe["count"]/number_bonds_with_year_dataframe["count"])*100)]

    headers = ["year", "percentage"]

    percentages_greenbonds_on_bonds_per_year = pd.concat(data, axis=1, keys=headers)
    return percentages_greenbonds_on_bonds_per_year

def draw_spaghetti_plot_greenbonds():
    greenbonds_spaghetti_data_frame = get_percentages_greenbonds_on_bonds_per_year()
    
    greenbonds_spaghetti_data_frame.plot(kind='bar',x='year',y='percentage')
    plt.title("Percentage of greenbonds in comparison to all bonds per year\n")

    plt.show
	