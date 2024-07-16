from alpha_vantage.timeseries import TimeSeries
import config
import pandas as pd
import requests


def get_data(ticker):
    url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={key}".format(key=config.API_KEY,ticker=ticker)
    r = requests.get(url)
    data = r.json()
    return pd.DataFrame(data['Time Series (Daily)']).T

data = get_data('AAPL')

