from functions import pieCharts

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
    data_frame["green"] = None # Default greenness of sector is None
    for i in range(0, data_frame.shape[0]):
            if data_frame.index[i] in get_sector_green_dict().keys():
                data_frame["green"][i]=get_sector_green_dict()[data_frame.index[i]]
    print(data_frame)