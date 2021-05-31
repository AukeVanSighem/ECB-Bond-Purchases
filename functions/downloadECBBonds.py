import requests,datetime,re
import os
import pandas as pd

dictionaryBondsECB = {}
dictionaryDatesBondsAdded = {}

def downloadDataToDictionary(url,dictionaryCompanyInfo,dictionaryDateAdded,date):
    """This function gets the csv from a url and places the new data in dictionaries 
    
    Param:
    - url: url leading to csv
    - dictionaryCompanyInfo: keys = ISIN, value = [NCB,ISSUER,MATURITY DATE,COUPON RATE]
    - dictionaryDateAdded: keys = ISIN, value = [date] with date the date it first appeared 
    in weekly overview"""

    r = requests.get(url) # create HTTP response object
    nameCompany = '' # make a string for the company name 
                     # (do this here so that is in scope of whole function)
    if r.status_code != 200: return # if website wasn't accessed in the right way, 
                                    # stop the function
    # this for loop loops through all the lines of the retrieved csv-file, except for the heading
    for line in r.text.split('\r\n')[1:]:
        if not re.search(r'[a-z]',line): continue # if the line doesn't contain letters, 
                                                  # go to the next line
        if re.search(r',+$',line): line = re.sub(r',+$',r'',line) # remove commas at end of line
        splitLine = line.split(',')
        if len(splitLine) < 5: continue # We expect at least 5 items as we want 5 columns 
                                        # and name could lead to additional columns
        if re.search(r'(?:\".*,.*\")',line): # searches commas between " as these are part of the name 
                                             # and shouldn't be split
            nameCompany = re.search(r'(?:\".*,.*\")',line).group(0) 
                                             # name of the company is between the ""
            nameCompany = re.sub(r"\"","",nameCompany) # remove the ""
        else:
            for str in splitLine:
                re.sub('\"','',str)
            nameCompany = splitLine[2]
        if (splitLine[1] not in dictionaryCompanyInfo): # only add new ISINs to the dictionary
            dictionaryCompanyInfo[splitLine[1]] = [splitLine[0], nameCompany, splitLine[-2], splitLine[-1]]
            dictionaryDateAdded[splitLine[1]] = [date]

def downloadDataFromWebsites():
    """iterate over the websites holding weekly overview of CSPP holdings and save it to two dictionaries
   (one for holdings and one for dates aqcuired)"""

    dateToDownload = datetime.date(2017, 6, 23)
    change_url_date = datetime.date(2020, 3, 27)
    end_date = datetime.date(2021,4,23)
    delta = datetime.timedelta(days=7)
    while dateToDownload <= change_url_date:
        date = dateToDownload.strftime("%Y%m%d")
        url = "https://www.ecb.europa.eu/mopo/pdf/CSPPholdings_"+date+".csv"
        downloadDataToDictionary(url,dictionaryBondsECB,dictionaryDatesBondsAdded,dateToDownload)
        dateToDownload += delta
    dateToDownload+delta
    while dateToDownload <= end_date:
        date = dateToDownload.strftime("%Y%m%d")
        url = "https://www.ecb.europa.eu/mopo/pdf/CSPP_PEPP_corporate_bond_holdings_"+date+".csv"
        downloadDataToDictionary(url,dictionaryBondsECB,dictionaryDatesBondsAdded,dateToDownload)
        dateToDownload += delta

def dictionariesToDataframe():
    """converts dictionaries on CSPP holdings to dataframes 
    
    return:
    - [holdingsECB, holdingsECBDates]"""

    matrixData = [] # 2D array with row per ISIN and columns for different data
    for ISIN, dataInDictionary in dictionaryBondsECB.items():
        item = [ISIN] + dataInDictionary
        matrixData.append(item)
    holdingsECB = pd.DataFrame(matrixData, columns=["ISIN","NCB","ISSUER","MATURITY DATE","COUPON RATE"])
    matrixData = [] # 2D array with row per ISIN and columns for different data
    for ISIN, dataInDictionary in dictionaryDatesBondsAdded.items():
        item = [ISIN] + dataInDictionary
        matrixData.append(item)
    holdingsECBDates = pd.DataFrame(matrixData, columns=["ISIN","Date"])
    return [holdingsECB, holdingsECBDates]

def exportCSV(parent, holdingsECB, holdingsECBDates):
    """saves the given dataframes to csv files in output folder
    
    Param:
    - parent: path to folder where files should be saved
    - holdingsECB: dataframe with info on holdings that should be saved as csv
    - holdingsECBDates: dataframe with info on dates of holdings that should be saved as csv"""

    holdingsECB.to_csv(parent + "holdingsECB.csv", index=False,sep=";")
    holdingsECBDates.to_csv(parent + "holdingsECBDates.csv", index=False,sep="\t")

def getPath():
    """returns the path to an output folder where all output data is saved"""

    path = __file__
    parent = os.path.join(path, os.pardir)
    parent = os.path.join(parent, os.pardir)
    return parent + "\output\\"

def download_ECB_Bonds():
    """function returns info on holdings owned by ECB in CSPP program"""

    parent = getPath()
    if not (os.path.isfile(parent + "holdingsECB.csv") & os.path.isfile(parent + "holdingsECBDates.csv")):
        downloadDataFromWebsites()
        holdings, dates = dictionariesToDataframe()
        exportCSV(parent, holdings, dates)
    else:
        holdings = pd.read_csv(parent + "holdingsECB.csv", sep=";")
    return holdings


