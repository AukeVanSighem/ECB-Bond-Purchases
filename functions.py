#Functions for the MDA project
import matplotlib.pyplot as plt # TODO: add to requirements if used
from sklearn.linear_model import LinearRegression

# This function gets the csv from the url and places the new data in a dictionary with keys = ISIN,
# and value = [NCB, ISSUER, MATURITY DATE, COUPON RATE]
def downloadDataToDictionary(url,dictionary):
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
        if (splitLine[1] not in dictionary): # only add new ISINs to the dictionary
            dictionary[splitLine[1]] = [splitLine[0], nameCompany, splitLine[-2], splitLine[-1]]
            
            
#Representatives of Industries and Sectors
            
def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        if (pct > 2.4):
            return '{p:.2f}%'.format(p=pct)
        else:
            return ''
    return my_autopct

def get_all_sectors(sector_type):
    sector_mappings['number']=1 # TODO: count them in a cleaner way
    sectors = sector_mappings[[sector_type, 'number']].groupby([sector_type]).sum()
    sectors = sectors.sort_values("number", axis=0, ascending=False, inplace=False, kind='quicksort', na_position='last', ignore_index=False, key=None)
    return sectors
    
def make_pie_chart(column_name):
    fig = plt.figure(figsize=(9,9))
    ax = plt.subplot(111)

    sectors = get_all_sectors(column_name)
    
    sectors.plot(kind='pie', y='number', ax=ax, autopct=make_autopct(sectors['number']), fontsize=12, legend=False, rotatelabels=True, pctdistance=0.8)
    plt.axis("off")
    plt.title(column_name+"\n\n\n")
    
    
    
def get_all_sectors_EU(sector_type): #TODO: make function one with previous
    historical_emissions_EU["number"]=1 # TODO: count them in a cleaner way
    sectors_EU = historical_emissions_EU[[sector_type, "number"]].groupby([sector_type]).sum()
    sectors_EU = sectors_EU.sort_values("number", axis=0, ascending=False, inplace=False, kind='quicksort', na_position='last', ignore_index=False, key=None)
    return sectors_EU


def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        if (pct > 2.4):
            return '{p:.2f}%'.format(p=pct)
        else:
            return ''
    return my_autopct

def get_all_sectors(sector_type):
    sector_data['number']=1 # TODO: count them in a cleaner way
    sectors = sector_data[[sector_type, 'number']].groupby([sector_type]).sum()
    sectors = sectors.sort_values("number", axis=0, ascending=False, inplace=False, kind='quicksort', na_position='last', ignore_index=False, key=None)
    return sectors
    
def make_pie_chart(column_name):
    fig = plt.figure(figsize=(9,9))
    ax = plt.subplot(111)

    sectors = get_all_sectors(column_name)
    
    sectors.plot(kind='pie', y='number', ax=ax, autopct=make_autopct(sectors['number']), fontsize=12, legend=False, rotatelabels=True, pctdistance=0.8)
    plt.axis("off")
    plt.title(column_name+"\n\n\n")
    
#Which Industries and Sectors are green?

 def show_table(column_names, row_names, content):
    fig, ax = plt.subplots() 
    ax.set_axis_off() 
    table = ax.table( 
        cellText = content,  
        rowLabels = row_names,  
        colLabels = column_names, 
        rowColours =["c"] * len(row_names),  
        colColours =["c"] * len(column_names), 
        cellLoc ='center',  
        loc ='upper left')         

    ax.set_title('Percentage of industries or sectors that is green', 
                 fontweight ="bold") 

    plt.show() 
    
    
 #Cleanig the data 

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
    
    return esg_company_datadef cleaning_esg_data(df):
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



#ECG Evolution of each company

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