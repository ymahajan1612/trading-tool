import config
import requests
import pandas as pd
import os
import pickle as pkl
pd.set_option('display.max_columns', None)

class StockData:
    CACHE_DIR = "stock_data_cache"
    def __init__(self, ticker):
        self.ticker = ticker
        self.testing = False
        if self.testing:
            self.error = None 
            self.data = pd.read_csv('stock_dataframe_test.csv',index_col=0)
            self.data.index = pd.to_datetime(self.data.index)
        else:
            #1. Check if data for a stock is stored in cache and is up to date (less than 24 hrs old)
            #2. If data is not stored in cache, fetch data from alpha vantage API
            #3. Store the data in cache
            cached_data = self.loadDataFromCache()
            if cached_data is not None:
                self.data = cached_data
                self.error = None
            else:
                self.data, self.error  = self.fetchData()
                if self.error is None:
                    self.saveDataToCache()
    
    def getTicker(self):
        return self.ticker
    
    def loadDataFromCache(self):
        """
        Check if data for a stock is stored in cache and is up to date (less than 24 hrs old)
        and return the data if it exist and is up to date
        """
        file_path = "{directory}/{symbol}.pkl".format(directory=self.CACHE_DIR,symbol = self.getTicker())
        if os.path.exists(file_path):
            print("Loading data from cache")
            with open(file_path, 'rb') as stock_data:
                cached_content = pkl.load(stock_data)
                if pd.Timestamp.now() - cached_content['Time'] < pd.Timedelta(days=1):
                    return cached_content['Data']
        return None


    def saveDataToCache(self):
        """
        Save the stock data to cache
        """
        file_path = "{directory}/{symbol}.pkl".format(directory = self.CACHE_DIR, symbol = self.getTicker())
        with open(file_path, 'wb') as stock_data:
            pkl.dump({'Time': pd.Timestamp.now(), 'Data': self.data}, stock_data)


    def fetchData(self):
        """
        Fetches daily stock data for a given ticker symbol using alpha vantage API and formats the data into a pandas dataframe
        """
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={self.getTicker()}&outputsize=full&apikey={config.API_KEY}"
        try:
            r = requests.get(url)
            r.raise_for_status()
            data = r.json()

            if "Time Series (Daily)" not in data:
                error_message = f"Error: Unable to retrieve data for {self.getTicker()}. Please check if the ticker symbol is correct."
                return None, error_message

            # Formatting Data
            stock_dataframe = pd.DataFrame(data['Time Series (Daily)']).T
            stock_dataframe.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            stock_dataframe = stock_dataframe.astype(float)  # convert all data to float
            stock_dataframe.index = pd.to_datetime(stock_dataframe.index)  # Convert index to datetime
            stock_dataframe = stock_dataframe.sort_index()  # Sort the DataFrame by date
            stock_dataframe.index.name = "Date"

            return stock_dataframe, None
        
        except requests.exceptions.HTTPError as e:
            return None, "Error: Unable to retrieve data due to HTTP Error: {error}.".format(error=e)
        except requests.exceptions.RequestException as e:
            return None, "Error: Unable to retrieve data due to Request Exception: {error}.".format(error=e)
        except ValueError as e:
            return None, "Error: Unable to retrieve data due to Value Error: {error}.".format(error=e)
        except Exception as e:
            return None, "Error: Unable to retrieve data due to an unknown error: {error}.".format(error=e)
        
    def getError(self):
        return self.error
    
    def getDataFrame(self):
        return self.data
    

