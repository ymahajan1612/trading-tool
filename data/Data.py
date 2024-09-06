import config.config as config
import requests
import pandas as pd
import os
import pickle as pkl
pd.set_option('display.max_columns', None)

class StockData:
    """
    This class is used to fetch and store stock data for a given ticker symbol
    """
    # Directory to store the stock data cache
    CACHE_DIR = "data/stock_data_cache"

    def __init__(self, ticker):
        self.ticker = ticker
        # Fetch the stock data
        # Check if the data is stored in cache and is up to date
        cached_data = self.loadDataFromCache()
        if cached_data is not None:
            self.fetch_time, self.data = cached_data
            self.error = None   

        # If the data is not in cache or is outdated, fetch the data from the API
        else:
            self.data, self.error  = self.fetchData()
            if self.error is None:
                # Save the data to cache
                self.saveDataToCache()
                self.fetch_time = pd.Timestamp.now().date()
    
    def getTicker(self):
        return self.ticker

    def getFetchTime(self):
        return self.fetch_time
    
    def loadDataFromCache(self):
        """
        Check if data for a stock is stored in cache and is up to date 
        and return the data if it exist and is up to date
        """
        file_path = "{directory}/{symbol}.pkl".format(directory=self.CACHE_DIR,symbol = self.getTicker())
        if os.path.exists(file_path):
            with open(file_path, 'rb') as stock_data:
                cached_content = pkl.load(stock_data)
                if pd.Timestamp.now().date() == cached_content['fetchDate']:
                    return cached_content['fetchDate'], cached_content['Data']
        return None


    def saveDataToCache(self):
        """
        Save the stock data to cache
        """
        file_path = "{directory}/{symbol}.pkl".format(directory = self.CACHE_DIR, symbol = self.getTicker())
        with open(file_path, 'wb') as stock_data:
            pkl.dump({'fetchDate': pd.Timestamp.now().date(), 'Data': self.data}, stock_data)


    def fetchData(self):
        """
        Fetches daily stock data for a given ticker symbol using alpha vantage API and formats the data into a pandas dataframe
        """
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={self.getTicker()}&outputsize=full&apikey={config.API_KEY}"
        try:
            r = requests.get(url)
            r.raise_for_status()
            data = r.json()

            # Checks for errors in fetching the data and returns an error message
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

            #  Return the stock data and no error message if the data is successfully fetched
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
    

