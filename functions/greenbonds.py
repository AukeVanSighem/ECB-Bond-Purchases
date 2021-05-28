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


def draw_spaghetti_plot_greenbonds():
    greenbonds_spaghetti_data_frame = get_number_greenbonds_with_year()
    
    plt.bar(range(len(greenbonds_spaghetti_data_frame)), list(greenbonds_spaghetti_data_frame.values()), align='center')
    plt.xticks(range(len(greenbonds_spaghetti_data_frame)), list(greenbonds_spaghetti_data_frame.keys()))

    plt.show