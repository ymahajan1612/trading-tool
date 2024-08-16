import config
from Algorithm import BollingerBandStrategy, SMACrossOverStrategy, MACDStrategy
import pandas as pd
import requests
pd.set_option('display.max_columns', None)

# temporary measure in place to avoid timeout from too many calls to alpha_vantage
testing_on_going = False

def fetchData(ticker):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&outputsize=full&apikey={config.API_KEY}"
    r = requests.get(url)
    data = r.json()

    # Formatting Data
    stock_dataframe = pd.DataFrame(data['Time Series (Daily)']).T
    stock_dataframe.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    stock_dataframe = stock_dataframe.astype(float)  # convert all data to float
    stock_dataframe.index = pd.to_datetime(stock_dataframe.index)  # Convert index to datetime
    stock_dataframe = stock_dataframe.sort_index()  # Sort the DataFrame by date
    stock_dataframe.index.name = "Date"

    stock_dataframe.to_csv("stock_dataframe_test.csv")

    return stock_dataframe


if not testing_on_going:
    full_data = fetchData('VOD')
else:
    full_data = pd.read_csv('stock_dataframe_test.csv',index_col=0)
    full_data.index = pd.to_datetime(full_data.index)


BollingerBand = BollingerBandStrategy(full_data)
BollingerBand.generatePlot()