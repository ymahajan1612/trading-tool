from alpha_vantage.timeseries import TimeSeries
import config
import pandas as pd
import requests


def fetch_data(ticker):
    url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&outputsize=full&apikey={key}".format(key=config.API_KEY,ticker=ticker)
    r = requests.get(url)
    data = r.json()
    dataframe = pd.DataFrame(data['Time Series (Daily)']).T
    dataframe.columns = ['Open', ' High', 'Low', 'Close', 'Volume']
    return dataframe


def calculate_SMA(stock_data_full, num_points = 200):
    # calculates short term (10 days), medium (50 days) and long (num_points days) SMA values
    stock_data = stock_data_full.head(num_points)
    for i, row in enumerate(stock_data.iterrows()):
         short_SMA = stock_data_full()

full_data = fetch_data('AAPL')
calculate_SMA(full_data)