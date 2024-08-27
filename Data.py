import config
import requests
import pandas as pd

pd.set_option('display.max_columns', None)

class StockData:
    def __init__(self, ticker):
        self.ticker = ticker
        self.testing = False # temporary measure in place to avoid timeout from too many calls to alpha_vantage
        if self.testing:
            self.error = None 
            self.data = pd.read_csv('stock_dataframe_test.csv',index_col=0)
            self.data.index = pd.to_datetime(self.data.index)
        else:
            self.data, self.error  = self.fetchData()
            if self.data is not None:
                self.data.to_csv("stock_dataframe_test.csv")
    
    def getTicker(self):
        return self.ticker

    def fetchData(self):
        """
        Fetches daily stock data for a given ticker symbol using alpha vantage API and formats the data into a pandas dataframe
        """
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={self.ticker}&outputsize=full&apikey={config.API_KEY}"
        try:
            r = requests.get(url)
            r.raise_for_status()
            data = r.json()

            if "Time Series (Daily)" not in data:
                error_message = f"Error: Unable to retrieve data for {self.ticker}. The API returned: {data.get('Error Message', 'Unknown error')}"
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
    

