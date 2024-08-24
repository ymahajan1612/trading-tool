from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import pandas as pd
import copy

class Strategy(ABC):
    def __init__(self,stock, short_window=None, long_window=None):
        self.stock = stock
        self.historical_data = copy.deepcopy(stock.getDataFrame())
        self.short_window = short_window
        self.long_window = long_window
        self.plot_window = 60
        self.preprocessData()
    
    def getData(self):
        return self.historical_data

    def generateSignalSeries(self):
        signals = [0]
        for i in range(1, len(self.historical_data)):
            signals.append(self.generateSignal(current_index=i))
        
        return pd.Series(signals, index=self.historical_data.index[:])

    @abstractmethod
    def preprocessData(self):
        raise NotImplementedError()
    
    def calculateSMA(self, window):
        return self.historical_data['Close'].rolling(window=window).mean()
    
    @abstractmethod
    def generateSignal(self, current_index = -1):
        """
        Passing current index in data as optional argument for backtesting. 
        For some current_index = i, prev = self.historical_data[i-1] and 
        curr = self.historical_data[i]
        """
        raise NotImplementedError()
    
    @abstractmethod
    def generatePlot(self):
        raise NotImplementedError()
    

class SMACrossOverStrategy(Strategy):
    def __init__(self, stock, short_window, long_window):
        super().__init__(stock, short_window, long_window)

    def preprocessData(self):
        self.historical_data['SMA_short'] = self.calculateSMA(self.short_window)
        self.historical_data['SMA_long'] = self.calculateSMA(self.long_window)
        self.historical_data = self.historical_data.tail(200)
        

    def getShortWindow(self):
        return self.short_window

    def getLongWindow(self):
        return self.long_window
    
    def generateSignal(self, current_index = -1):
        """
        Returns:
        int: 1 for buy signal, -1 for sell signal, and 0 for hold.
        """
        curr = self.historical_data.iloc[current_index]
        prev = self.historical_data.iloc[current_index-1]

        # Generate Buy Signal
        if (prev.SMA_short < prev.SMA_long) and (curr.SMA_short > curr.SMA_long):
            return 1

        # Generate Sell Signal
        if (prev.SMA_short > prev.SMA_long) and (curr.SMA_short < curr.SMA_long):
            return -1

        # Hold
        return 0
    
    def generatePlot(self):
        stock_data_plot = self.historical_data.tail(self.plot_window).copy()
        stock_data_plot['Date'] = dates.date2num(stock_data_plot.index)
        print(stock_data_plot)
        fig, ax = plt.subplots(figsize=(14, 8))
        ax.plot(stock_data_plot['Date'], stock_data_plot['SMA_short'], label='{}-day SMA'.format(self.short_window), color='blue')
        ax.plot(stock_data_plot['Date'], stock_data_plot['SMA_long'], label='{}-day SMA'.format(self.long_window), color='purple')

        for idx in range(len(stock_data_plot)):
            row = stock_data_plot.iloc[idx]
            if self.generateSignal(current_index=idx) == 1:
                ax.plot(row['Date'], row['Close'], marker='^', markersize=10, color='g')
            elif self.generateSignal(current_index=idx) == -1:
                ax.plot(row['Date'], row['Close'], marker='v', markersize=10, color='r')
            
 
        for idx, row in stock_data_plot.iterrows():
            colour = 'g' if row['Close'] >= row['Open'] else 'r'
            lower = min(row['Open'], row['Close'])
            height = abs(row['Close'] - row['Open'])
            ax.add_patch(plt.Rectangle((row['Date'] - 0.3, lower), 0.6, height, color=colour))
            ax.plot([row['Date'], row['Date']], [row['Low'], lower], color='k')
            ax.plot([row['Date'], row['Date']], [row['High'], lower + height], color='k')
        plt.plot(stock_data_plot['Date'], stock_data_plot['Close'], label='Close Price', color='black', linestyle='-', linewidth=1)

        ax.set_xlabel('Date')
        ax.xaxis_date()  # Convert the x-axis to date format
        ax.xaxis.set_major_formatter(dates.DateFormatter('%Y-%m-%d'))  # Format dates
        ax.set_ylabel('Price')
        ax.set_title('SMA Crossover Strategy for {}'.format(self.stock.getTicker()))
        ax.legend()
        plt.xticks(rotation=45)
        plt.show()



class MACDStrategy(Strategy):
    def __init__(self, stock, short_window=12, long_window=26, signal_window=9):
        self.signal_window = signal_window
        super().__init__(stock, short_window, long_window)
        
    def preprocessData(self):
        self.historical_data['EMA_200'] = self.calculateEMA(200) 
        self.historical_data['MACD'] = self.calculateEMA(self.short_window) - self.calculateEMA(self.long_window)
        self.historical_data['Signal_line'] = self.historical_data['MACD'].ewm(span=self.signal_window, adjust=False).mean()
        self.historical_data['MACD_histogram'] = self.historical_data['MACD'] - self.historical_data['Signal_line']

        self.historical_data = self.historical_data.tail(400)

    
    def calculateEMA(self, window):
        """
        Calculates a weighted average,
        by giving more weight to the recent points in a window
        """
        return self.historical_data['Close'].ewm(span=window, adjust=False).mean()

    def generateSignal(self, current_index = -1):
        curr = self.historical_data.iloc[current_index]
        prev = self.historical_data.iloc[current_index-1]

        if (prev['MACD'] < prev['Signal_line'] and 
            curr['MACD'] > curr['Signal_line'] and 
            curr['Close'] > curr['EMA_200']):
            return 1  # Buy signal
        
        if (prev['MACD'] > prev['Signal_line'] and 
            curr['MACD'] < curr['Signal_line'] and 
            curr['Close'] < curr['EMA_200']):
            return -1  # Sell signal
        
        return 0  # Hold signal

    def generatePlot(self):
        stock_data_plot = self.historical_data.tail(self.plot_window).copy()
        stock_data_plot['Date'] = dates.date2num(stock_data_plot.index)

        fig, ax = plt.subplots(figsize=(14, 8))
        ax.plot(stock_data_plot['Date'], stock_data_plot['MACD'], label='MACD', color='blue')
        ax.plot(stock_data_plot['Date'], stock_data_plot['Signal_line'], label='Signal Line', color='orange')
        
        for idx, row in stock_data_plot.iterrows():
            colour = 'g' if row['MACD_histogram'] > 0 else 'r'
            ax.bar(row['Date'], row['MACD_histogram'], color=colour, width=1)

        ax.axhline(y=0, color='black', linewidth=1, linestyle="-")
        ax.xaxis_date()  # Convert the x-axis to date format
        ax.xaxis.set_major_formatter(dates.DateFormatter('%Y-%m-%d'))  # Format dates
        ax.set_xlabel('Date')
        ax.set_ylabel('MACD Value')
        ax.set_title('MACD Strategy for {}'.format(self.stock.getTicker()))
        ax.legend()
        plt.xticks(rotation=45)
        plt.show()



class BollingerBandStrategy(Strategy):
    def __init__(self, stock):
        self.window = 30
        self.RSI_threshold_high = 70
        self.RSI_threshold_low = 30
        self.band_width_threshold = 0.15
        super().__init__(stock,None,None)
    
    def preprocessData(self):
        self.historical_data['SMA'] = self.calculateSMA(self.window)
        self.historical_data['SD'] = self.historical_data['Close'].rolling(window=self.window).std()

        self.historical_data['UB'] = self.historical_data['SMA'] + (2 * self.historical_data['SD'])
        self.historical_data['LB'] = self.historical_data['SMA'] - (2 * self.historical_data['SD'])

        self.historical_data['Band_width'] = (self.historical_data['UB'] - self.historical_data['LB']) / self.historical_data['SMA']

        delta = self.historical_data['Close'].diff()
        delta.dropna(inplace=True)

        positive = delta.copy()
        negative = delta.copy()

        positive[positive < 0] = 0
        negative[negative > 0] = 0

        average_gain = positive.rolling(window=14).mean()
        average_loss = abs(negative.rolling(window=14).mean())
        relative_strength = average_gain/average_loss
        RSI = 100.0 - (100.0/(1.0 + relative_strength))
        self.historical_data['RSI'] = RSI
        self.historical_data = self.historical_data.tail(500)

        
    
    def generateSignal(self, current_index = -1):
        """
        In this strategy for a buy signal: 
        1. The prevous candle must close below the bollinger band
        2. The RSI value for the previous day must be below the threshold (30)
        3. The bollinger band width is greater than the threshold to avoid trading low volatility periods
        4. Current closes above previous high
        vice verse for a sell signal.
        """
        curr = self.historical_data.iloc[current_index]
        prev = self.historical_data.iloc[current_index-1]

        # 1
        prev_close_below_band = prev['Close'] < prev['LB']
        # 2
        prev_rsi_below_threshold = prev['RSI'] < self.RSI_threshold_low
        # 3
        band_width_above_threshold = True 
        #curr['Band_width'] > self.band_width_threshold


        # Generate a buy signal
        if (prev_close_below_band and 
            prev_rsi_below_threshold and
            band_width_above_threshold):
            return 1


        # Same check for sell signal
        prev_close_above_band = prev['Close'] > prev['UB']
        prev_rsi_above_threshold = prev['RSI'] > self.RSI_threshold_high


        # Generate a sell signal
        if (prev_close_above_band and 
            prev_rsi_above_threshold and
            band_width_above_threshold):
            return -1 
    
        return 0 

    def generatePlot(self):
        stock_data_plot = self.historical_data.tail(self.plot_window).copy()
        stock_data_plot['Date'] = dates.date2num(stock_data_plot.index)

        fig, (ax, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
        # Plot the Bollinger Bands and the SMA
        ax.plot(stock_data_plot['Date'], stock_data_plot['SMA'], label='20-day SMA', color='blue')
        ax.plot(stock_data_plot['Date'], stock_data_plot['UB'], label='Upper Bollinger Band', color='purple')
        ax.plot(stock_data_plot['Date'], stock_data_plot['LB'], label='Lower Bollinger Band', color='red')


        # Plot the candlestick chart
        for idx, row in stock_data_plot.iterrows():
            color = 'g' if row['Close'] >= row['Open'] else 'r'
            lower = min(row['Open'], row['Close'])
            height = abs(row['Close'] - row['Open'])
            ax.add_patch(plt.Rectangle((row['Date'] - 0.3, lower), 0.6, height, color=color))
            ax.plot([row['Date'], row['Date']], [row['Low'], lower], color='k')
            ax.plot([row['Date'], row['Date']], [row['High'], lower + height], color='k')
        ax.plot(stock_data_plot['Date'], stock_data_plot['Close'], label='Close Price', color='black', linestyle='-', linewidth=1)
        # Plot RSI as a secondary y-axis
        ax2.plot(stock_data_plot['Date'], stock_data_plot['RSI'], label='RSI', color='orange')
        ax2.axhline(y=self.RSI_threshold_high, color='red', linestyle='--')
        ax2.axhline(y=self.RSI_threshold_low, color='green', linestyle='--')
        ax2.set_ylabel('RSI')

        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.set_title('Bollinger Bands Strategy for {}'.format(self.stock.getTicker()))
        ax.legend(loc='upper left')
        ax2.legend(loc='upper left')
        ax.xaxis_date()
        ax.xaxis.set_major_formatter(dates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)
        plt.show()

