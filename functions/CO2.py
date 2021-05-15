from functions import readEikonData
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression


def get_company_co2_data():
    co2_data = readEikonData.get_eikon_data_complete()[["ISSUER", "CO2", "CO2_1"]] #compnay name and CO2 subset 
    company_co2_data = co2_data.drop_duplicates(subset= ["ISSUER"]) #Unique company name subset 
    company_co2_data = company_co2_data[(company_co2_data.CO2 != '0') & (company_co2_data.CO2_1 != '0')] #not null value for CO2
    company_co2_data = company_co2_data.reset_index() #resets index
    company_co2_data = company_co2_data.drop(columns=["index"]) #removes extra column
    company_co2_data = company_co2_data.replace(to_replace = '[,]', value ='.', regex=True) #making decimal points legible
    company_co2_data['CO2'] =company_co2_data['CO2'].astype(float) #converting numbers to floats 
    company_co2_data['CO2_1'] =company_co2_data['CO2_1'].astype(float)
    return company_co2_data

company_co2_data = get_company_co2_data()

def get_slopes():
    #overall slope increase or decrease 
    slopes = company_co2_data['CO2_1'] - company_co2_data['CO2']
    print("The overall sum of slopes is: " + str(slopes.sum()) +". This shows an overall decrease in total emissions.") #shows an overall decrease in total emissions **Could cluster by sector. Hard to do anything else with 2 data points*
    return slopes

slopes = get_slopes()

def make_CO2_spaghetti_plot():
    #making data easier to graph 
    co2graph_data = company_co2_data[["CO2", "CO2_1"]]
    co2graph_data = co2graph_data.transpose()
    co2graph_data.insert(0, "x", [0, 1], True)


    plt.style.use('seaborn-darkgrid')
    palette = plt.get_cmap('Set1')

    #spaghetti plot of CO2 emissions 
    plt.figure(figsize=(20,20))
    for column in co2graph_data.drop(columns=["x"], axis=1):
        plt.plot(co2graph_data["x"], co2graph_data[column], marker='', linewidth=1, alpha=0.9)
        
    plt.show()

def make_CO2_histogram():
    plt.hist(x=slopes, bins=7,alpha=0.7)
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.title(r'Histogram of the change in nomalized CO$_2$ emission during the CSPP')
    plt.show()

def plot_2020_2015():
    plt.plot(company_co2_data["CO2"],company_co2_data["CO2_1"],'o')
    plt.title("emission of 2021 as a function of the emission in 2015", size=15)
    plt.xlabel("emission in 2015", size=15)
    plt.ylabel("emission in 2021",size=15)
    plt.show()

def make_linear_fit():
    # We will use the module Linear Regression of sklearn to perform the analysis
    # Initialize the model
    ols = LinearRegression()
    # Fit the model to the data
    ols.fit(company_co2_data["CO2"].values.reshape(-1, 1),company_co2_data["CO2_1"])

    print('Fit is of the form:',np.round(ols.intercept_,3),'+',np.round(ols.coef_[0],3),'x')

    plt.figure(figsize=(10,5))

    # plot of data
    plt.plot(company_co2_data["CO2"],company_co2_data["CO2_1"],'o',label="data")

    # plot of fit
    x = np.arange(0,max((company_co2_data["CO2"])+100))
    y = ols.intercept_ + ols.coef_[0]*x
    plt.plot(x,y,'r-',label="fit")

    # making a nice figure
    plt.title("emission of 2021 as a function of the emission in 2015", size=15)
    plt.xlabel("emission in 2015", size=15)
    plt.ylabel("emission in 2021",size=15)
    plt.legend(fontsize="15")

    plt.show()