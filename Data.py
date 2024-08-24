import config
import requests
import pandas as pd

pd.set_option('display.max_columns', None)

class StockData:
    def __init__(self, ticker):
        self.ticker = ticker
        self.testing = False # temporary measure in place to avoid timeout from too many calls to alpha_vantage
        if self.testing: 
            self.data = pd.read_csv('stock_dataframe_test.csv',index_col=0)
            self.data.index = pd.to_datetime(self.data.index)
        else:
            self.data = self.fetchData()
            self.data.to_csv("stock_dataframe_test.csv")
    
    def getTicker(self):
        return self.ticker

    def fetchData(self):
        """
        Fetches daily stock data for a given ticker symbol using alpha vantage API and formats the data into a pandas dataframe
        """
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={self.ticker}&outputsize=full&apikey={config.API_KEY}"
        r = requests.get(url)
        data = r.json()

        # Formatting Data
        stock_dataframe = pd.DataFrame(data['Time Series (Daily)']).T
        stock_dataframe.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        stock_dataframe = stock_dataframe.astype(float)  # convert all data to float
        stock_dataframe.index = pd.to_datetime(stock_dataframe.index)  # Convert index to datetime
        stock_dataframe = stock_dataframe.sort_index()  # Sort the DataFrame by date
        stock_dataframe.index.name = "Date"

        return stock_dataframe
    
    def getDataFrame(self):
        return self.data
    

