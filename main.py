
import config
import pandas as pd
import requests
import matplotlib.pyplot as plt
import numpy as np
pd.set_option('display.max_columns', None)
# Define SMA periods
short_term = 10
mid_term = 50
long_term = 200
# temporary measure in place to avoid timeout from too many calls to alpha_vantage
testing_on_going = True

def fetchData(ticker,testing=False):
    # Fetch data with enough history to calculate SMAs
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&outputsize=full&apikey={config.API_KEY}"
    r = requests.get(url)
    data = r.json()
    stock_dataframe = pd.DataFrame(data['Time Series (Daily)']).T
    stock_dataframe.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    stock_dataframe = stock_dataframe.astype(float)  # Convert all data to float
    stock_dataframe.index = pd.to_datetime(stock_dataframe.index)  # Convert index to datetime
    stock_dataframe = stock_dataframe.sort_index()  # Sort the DataFrame by date
    if testing:
        stock_dataframe.to_csv("stock_dataframe_test.csv")
    return  stock_dataframe



def calculateSMA(stock_dataframe,short_term = 10,mid_term = 50, long_term = 200):
    # Calculate SMAs
    stock_dataframe['SMA_short'] = stock_dataframe['Close'].rolling(window=short_term).mean()
    stock_dataframe['SMA_mid'] = stock_dataframe['Close'].rolling(window=mid_term).mean()
    stock_dataframe['SMA_long'] = stock_dataframe['Close'].rolling(window=long_term).mean()

    trimmed_data = stock_dataframe.tail(long_term)

    return trimmed_data


def generatePlot(stock_data):
    last_50_entries = stock_data.tail(50).copy()
    last_50_entries['candle_stick'] = last_50_entries['Close'] - last_50_entries['Open']
    print(last_50_entries)

if not testing_on_going:
    full_data = fetchData('AAPL',True)
else:
    full_data = pd.read_csv('stock_dataframe_test.csv')

sma_calculated = calculateSMA(full_data)

generatePlot(sma_calculated)
