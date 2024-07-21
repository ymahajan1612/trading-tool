
import config
import pandas as pd
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import numpy as np
pd.set_option('display.max_columns', None)
short_term = 10
mid_term = 50
long_term = 100

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
    stock_dataframe.index.name = "Date"
    if testing:
        stock_dataframe.to_csv("stock_dataframe_test.csv")
    return  stock_dataframe



def calculateSMA(stock_dataframe):
    # Calculate SMAs
    stock_dataframe['SMA_short'] = stock_dataframe['Close'].rolling(window=short_term).mean()
    stock_dataframe['SMA_mid'] = stock_dataframe['Close'].rolling(window=mid_term).mean()
    stock_dataframe['SMA_long'] = stock_dataframe['Close'].rolling(window=long_term).mean()

    trimmed_data = stock_dataframe.tail(long_term)

    return trimmed_data


def generatePlot(stock_data):
    stock_data_plot = stock_data.copy()
    stock_data_plot['Date'] = dates.date2num(stock_data_plot.index)

    fig, ax = plt.subplots(figsize=(14, 8))

    # Plot the candlestick chart
    for idx, row in stock_data_plot.iterrows():
        if row['Close'] >= row['Open']:
            color = 'g'
            lower = row['Open']
            height = row['Close'] - row['Open']
        else:
            color = 'r'
            lower = row['Close']
            height = row['Open'] - row['Close']
        
        ax.add_patch(plt.Rectangle((row['Date'] - 0.3, lower), 0.6, height, color=color))
        ax.plot([row['Date'], row['Date']], [row['Low'], lower], color='k')
        ax.plot([row['Date'], row['Date']], [row['High'], lower + height], color='k')

    ax.plot(stock_data_plot['Date'], stock_data_plot['SMA_short'], label='{}-day SMA'.format(short_term), color='blue')
    ax.plot(stock_data_plot['Date'], stock_data_plot['SMA_mid'], label='{}-day SMA'.format(str(mid_term)), color='orange')
    ax.plot(stock_data_plot['Date'], stock_data_plot['SMA_long'], label='{}-day SMA'.format(long_term), color='purple')

    # Formatting the date on x-axis
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(dates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)

    # Adding labels and legend
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.set_title('Stock Price with SMAs')
    ax.legend()

    # Show the plot
    plt.show()
    

    
if not testing_on_going:
    full_data = fetchData('AAPL',True)
else:
    full_data = pd.read_csv('stock_dataframe_test.csv',index_col=0)
    full_data.index = pd.to_datetime(full_data.index)


sma_calculated = calculateSMA(full_data)


generatePlot(sma_calculated)
