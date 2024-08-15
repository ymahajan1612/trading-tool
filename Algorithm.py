from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import matplotlib.dates as dates

class Algorithm(ABC):
    def __init__(self,data, short_window=None, long_window=None):
        self.data = data
        self.short_window = short_window
        self.long_window = long_window
        self.plot_window = 60
        self.preprocessData()
    
    def getData(self):
        return self.data 

    def getShortWindow(self):
        return self.short_window

    def getLongWindow(self):
        return self.long_window

    @abstractmethod
    def preprocessData(self):
        raise NotImplementedError()
    
    def calculateSMA(self, window):
        return self.data['Close'].rolling(window=window).mean()
    
    def calculateEMA(self, window):
        """
        Calculates a weighted average,
        by giving more weight to the recent points in a window
        """
        return self.data['Close'].ewm(span=window, adjust=False).mean()
    
    @abstractmethod
    def generateSignal(self):
        raise NotImplementedError()
    
    @abstractmethod
    def generatePlot(self):
        raise NotImplementedError()
    

class SMACrossOverStrategy(Algorithm):
    def __init__(self, data, short_window, long_window):
        super().__init__(data.copy(), short_window, long_window)

    def preprocessData(self):
        self.data['SMA_short'] = self.calculateSMA(self.short_window)
        self.data['SMA_long'] = self.calculateSMA(self.long_window)

        self.data = self.data.tail(200)
    
    def generateSignal(self):
        """
        Returns:
        int: 1 for buy signal, -1 for sell signal, and 0 for hold.
        """
        curr = self.data.iloc[-1]
        prev = self.data.iloc[-2]

        # Generate Buy Signal
        if (prev.SMA_short < prev.SMA_long) and (curr.SMA_short > curr.SMA_long):
            return 1

        # Generate Sell Signal
        if (prev.SMA_short > prev.SMA_long) and (curr.SMA_short < curr.SMA_long):
            return -1

        # Hold
        return 0
    
    def generatePlot(self):
        stock_data_plot = self.data.tail(self.plot_window).copy()
        stock_data_plot['Date'] = dates.date2num(stock_data_plot.index)
        print(stock_data_plot)
        fig, ax = plt.subplots(figsize=(14, 8))
        ax.plot(stock_data_plot['Date'], stock_data_plot['SMA_short'], label='{}-day SMA'.format(self.short_window), color='blue')
        ax.plot(stock_data_plot['Date'], stock_data_plot['SMA_long'], label='{}-day SMA'.format(self.long_window), color='purple')

        # Custom candlestick plot
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
        ax.set_title('SMA Crossover Strategy')
        ax.legend()
        plt.xticks(rotation=45)
        plt.show()



class MACDStrategy(Algorithm):
    def __init__(self, data, short_window=12, long_window=26, signal_window=9):
        self.signal_window = signal_window
        super().__init__(data.copy(), short_window, long_window)
        
    def preprocessData(self):
        self.data['EMA_200'] = self.calculateEMA(200) 
        self.data['MACD'] = self.calculateEMA(self.short_window) - self.calculateEMA(self.long_window)
        self.data['Signal_line'] = self.data['MACD'].ewm(span=self.signal_window, adjust=False).mean()
        self.data['MACD_histogram'] = self.data['MACD'] - self.data['Signal_line']
        self.data.fillna(0, inplace=True)
        self.data = self.data.tail(200)

    def generateSignal(self):
        curr = self.data.iloc[-1]
        prev = self.data.iloc[-2]

        if (prev['MACD'] < prev['Signal_line'] and 
            curr['MACD'] > curr['Signal_line'] and 
            curr['MACD_histogram'] < 0 and 
            curr['Closing'] > curr['EMA_200']):
            return 1  # Buy signal
        
        if (prev['MACD'] > prev['Signal_line'] and 
            curr['MACD'] < curr['Signal_line'] and 
            curr['MACD_histogram'] > 0 and 
            curr['Closing'] < curr['EMA_200']):
            return -1  # Sell signal
        
        return 0  # Hold signal

    def generatePlot(self):
        stock_data_plot = self.data.tail(self.plot_window).copy()
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
        ax.set_title('MACD Strategy')
        ax.legend()
        plt.xticks(rotation=45)
        plt.show()



class BollingerBandStrategy(Algorithm):
    def __init__(self, data):
        self.window = 20
        self.RSI_threshold_high = 70
        self.RSI_threshold_low = 30
        self.band_width_threshold = 0.0015
        super().__init__(data.copy(),None,None)
    
    def preprocessData(self):
        self.data['SMA'] = self.calculateSMA(20)
        self.data['SD'] = self.data['Close'].rolling(window=self.window).std()

        self.data['UB'] = self.data['SMA'] + (2 * self.data['SD'])
        self.data['LB'] = self.data['SMA'] - (2 * self.data['SD'])

        self.data['Band_width'] = (self.data['UB'] - self.data['LB']) / self.data['SMA']

        changes = self.data['Close'].diff()
        gains = changes.where(changes > 0, 0) 
        losses = changes.where(changes < 0, 0) 

        average_gains = gains.rolling(window=self.window, min_periods=1).mean()
        average_losses = losses.rolling(window=self.window, min_periods=1).mean()

        relative_strength = average_gains/average_losses
        self.data['RSI'] = 100 - (100/(1+relative_strength))
        self.data = self.data.tail(200)
    
    def generateSignal(self):
        """
        In this strategy for a buy signal: 
        1. The prevous candle must close below the bollinger band
        2. The RSI value for the previous day must be below the threshold (30)
        3. The bollinger band width is greater than the threshold to avoid trading low volatility periods
        4. Current closes above previous high
        vice verse for a sell signal.
        """
        curr = self.data.iloc[-1]
        prev = self.data.iloc[-2]

        # 1
        prev_close_below_band = prev['Close'] < prev['LB']
        # 2
        prev_rsi_below_threshold = prev['RSI'] < self.RSI_threshold_low
        # 3
        band_width_above_threshold = curr['Band_width'] > self.band_width_threshold
        # 4
        current_close_above_prev_high = curr['Close'] > prev['High']

        # Generate a buy signal
        if (prev_close_below_band and 
            prev_rsi_below_threshold and
            band_width_above_threshold and
            current_close_above_prev_high):
            return 1


        # Same check for sell signal
        prev_close_above_band = prev['Close'] > prev['UB']
        prev_rsi_above_threshold = prev['RSI'] > self.RSI_threshold_high
        current_close_below_prev_low = curr['Close'] < prev['Low']


        # Generate a sell signal
        if (prev_close_above_band and 
            prev_rsi_above_threshold and
            band_width_above_threshold and
            current_close_below_prev_low):
            return -1 
    
        return 0 

    def generatePlot(self):
        stock_data_plot = self.data.tail(self.plot_window).copy()
        stock_data_plot['Date'] = dates.date2num(stock_data_plot.index)

        fig, ax = plt.subplots(figsize=(14, 8))
        
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
        plt.plot(stock_data_plot['Date'], stock_data_plot['Close'], label='Close Price', color='black', linestyle='-', linewidth=1)
        #     # Plot RSI as a secondary y-axis
        # ax2 = ax.twinx()
        # ax2.plot(stock_data_plot['Date'], stock_data_plot['RSI'], label='RSI', color='orange')
        # ax2.axhline(y=self.RSI_threshold_high, color='red', linestyle='--')
        # ax2.axhline(y=self.RSI_threshold_low, color='green', linestyle='--')
        # ax2.set_ylabel('RSI')

        # Final formatting
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.set_title('Bollinger Bands Strategy')
        ax.legend(loc='upper left')
        ax.legend(loc='upper right')
        ax.xaxis_date()
        ax.xaxis.set_major_formatter(dates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)
        plt.show()
