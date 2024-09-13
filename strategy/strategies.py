from abc import ABC, abstractmethod
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import copy

class Strategy(ABC):
    """
    Abstract class for a trading strategy that can be implemented by different strategies.
    """
    def __init__(self,stock):
        self.stock = stock
        self.num_days = 1500
        self.historical_data = copy.deepcopy(stock.getDataFrame())
        self.preprocessData()
    
    def getData(self):
        return self.historical_data
    
    def getTicker(self):
        return self.stock.getTicker()

    def getDataSize(self):
        return self.num_days

    def generateSignalSeries(self):
        signals = [0]
        for i in range(1, len(self.historical_data)):
            signals.append(self.generateSignal(current_index=i))
        
        return pd.Series(signals, index=self.historical_data.index[:])

    def calculateSMA(self, window):
        """
        Calculates the Simple Moving Average over a given window
        """
        return self.historical_data['Close'].rolling(window=window).mean()
    
    def calculateEMA(self, window):
        """
        Calculates a weighted average,
        by giving more weight to the recent points in a window
        """
        return self.historical_data['Close'].ewm(span=window, adjust=False).mean()
    
    # Abstract methods
    @abstractmethod
    def getName(self):
        raise NotImplementedError()
    
    @abstractmethod
    def getDataAsDict(self):
        raise NotImplementedError()

    @abstractmethod
    def preprocessData(self):
        """
        Method to calculate the necessary indicators for the strategy
        """
        raise NotImplementedError()
    
    
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
        self.short_window = short_window
        self.long_window = long_window
        super().__init__(stock)

    def preprocessData(self):
        self.historical_data['SMA_short'] = self.calculateSMA(self.short_window)
        self.historical_data['SMA_long'] = self.calculateSMA(self.long_window)
        self.historical_data = self.historical_data.tail(self.num_days)

    def getDataAsDict(self):
        return {
            'SMA_short': self.getData()['SMA_short'].to_list(),
            'SMA_long': self.getData()['SMA_long'].to_list()
        }  

    def getName(self):
        return "SMA Crossover Strategy"      

    def getShortWindow(self):
        return self.short_window

    def getLongWindow(self):
        return self.long_window
    
    def generateSignal(self, current_index = -1):
        """
        In this strategy for a buy signal The short-term SMA must cross above the long-term SMA
        For a sell signal the short-term SMA must cross below the long-term SMA
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
    
    def generatePlot(self, plot_window):
        stock_data_plot = self.historical_data.tail(plot_window).copy()
        
        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=stock_data_plot.index,
            open=stock_data_plot['Open'],
            high=stock_data_plot['High'],
            low=stock_data_plot['Low'],
            close=stock_data_plot['Close'],
            name='Candlesticks'
        ))

         # Plot short SMA
        fig.add_trace(go.Scatter(
            x=stock_data_plot.index,
            y=stock_data_plot['SMA_short'],
            mode='lines',
            name=f'{self.short_window}-day SMA',
            line=dict(color='yellow')))

        # Plot long SMA
        fig.add_trace(go.Scatter(
            x=stock_data_plot.index,
            y=stock_data_plot['SMA_long'],
            mode='lines',
            name=f'{self.long_window}-day SMA',
            line=dict(color='green')))

        fig.update_layout(
            title=f'SMA Crossover Strategy for {self.stock.getTicker()}',
            xaxis_title='Date',
            yaxis_title='Price',
            xaxis_rangeslider_visible=False)

        return fig




class MACDStrategy(Strategy):
    def __init__(self, stock, short_window=12, long_window=26, signal_window=9):
        self.signal_window = signal_window
        self.short_window = short_window
        self.long_window = long_window
        super().__init__(stock)
        
    def preprocessData(self):
        self.historical_data['EMA_200'] = self.calculateEMA(200) 
        self.historical_data['MACD'] = self.calculateEMA(self.short_window) - self.calculateEMA(self.long_window)
        self.historical_data['Signal_line'] = self.historical_data['MACD'].ewm(span=self.signal_window, adjust=False).mean()
        self.historical_data['MACD_histogram'] = self.historical_data['MACD'] - self.historical_data['Signal_line']

        self.historical_data = self.historical_data.tail(self.num_days)

    def getName(self):
        return "MACD Strategy"

    def getDataAsDict(self):
        return {
            'MACD': self.getData()['MACD'].to_list(),
            'Signal_line': self.getData()['Signal_line'].to_list(),
            'MACD_histogram': self.getData()['MACD_histogram'].to_list()
        }

    def generateSignal(self, current_index = -1):
        """
        In this strategy for a buy signal:
        1. The MACD must cross above the Signal Line
        2. The current closing price is above the 200-day EMA
        For a sell signal:
        1. The MACD must cross below the Signal Line
        2. The current closing price is below the 200-day EMA
        """
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

    def generatePlot(self, plot_window):
        stock_data_plot = self.historical_data.tail(plot_window).copy()
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.75, 0.25], subplot_titles=('Stock Price', 'MACD'), vertical_spacing=0.1)


        # Plot candlestick chart
        fig.add_trace(go.Candlestick(
            x=stock_data_plot.index,
            open=stock_data_plot['Open'],
            high=stock_data_plot['High'],
            low=stock_data_plot['Low'],
            close=stock_data_plot['Close'],
            name='Candlestick'), row=1, col=1)

        # Plot MACD line
        fig.add_trace(go.Scatter(
            x=stock_data_plot.index,
            y=stock_data_plot['MACD'],
            mode='lines',
            name='MACD',
            line=dict(color='blue')), row=2, col=1)

        # Plot Signal line
        fig.add_trace(go.Scatter(
            x=stock_data_plot.index,
            y=stock_data_plot['Signal_line'],
            mode='lines',
            name='Signal Line',
            line=dict(color='orange')), row=2, col=1)

        # Plot MACD Histogram 
        fig.add_trace(go.Bar(
            x=stock_data_plot.index,
            y=stock_data_plot['MACD_histogram'],
            name='MACD Histogram',
            marker_color=stock_data_plot['MACD_histogram'].apply(lambda x: 'green' if x > 0 else 'red')), row=2, col=1)

        # Update layout
        fig.update_layout(
            height =900,
            xaxis_title='Date',
            yaxis_title='Price',
            xaxis2_title='Date', 
            yaxis2_title='MACD',   
            xaxis_rangeslider_visible=False)


        return fig



class BollingerBandStrategy(Strategy):
    def __init__(self, stock, window=20, standard_deviations=2):
        self.window = window
        self.standard_deviations = standard_deviations
        self.RSI_threshold_high = 70
        self.RSI_threshold_low = 30
        self.band_width_threshold = 0.15
        super().__init__(stock)
    
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
        self.historical_data = self.historical_data.tail(self.num_days)

    def getName(self):
        return "Bollinger Band Strategy"
    
    def getDataAsDict(self):
        return {
            'UB': self.getData()['UB'].to_list(),
            'LB': self.getData()['LB'].to_list(),
            'RSI': self.getData()['RSI'].to_list()
        }
    
    def generateSignal(self, current_index = -1):
        """
        In this strategy for a buy signal: 
        1. The prevous candle must close below the bollinger band
        2. The RSI value for the previous day must be below the threshold (30)
        vice verse for a sell signal.
        """
        curr = self.historical_data.iloc[current_index]
        prev = self.historical_data.iloc[current_index-1]

        # 1
        prev_close_below_band = prev['Close'] < prev['LB']
        # 2
        prev_rsi_below_threshold = prev['RSI'] < self.RSI_threshold_low



        # Generate a buy signal
        if (prev_close_below_band and 
            prev_rsi_below_threshold):
            return 1


        # Same check for sell signal
        prev_close_above_band = prev['Close'] > prev['UB']
        prev_rsi_above_threshold = prev['RSI'] > self.RSI_threshold_high


        # Generate a sell signal
        if (prev_close_above_band and 
            prev_rsi_above_threshold):
            return -1 
    
        return 0 


    def generatePlot(self,plot_window):
        stock_data_plot = self.historical_data.tail(plot_window).copy()
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.75, 0.25], subplot_titles=('Bollinger Bands', 'RSI'), vertical_spacing=0.1)

        fig.add_trace(go.Candlestick(
            x=stock_data_plot.index,
            open=stock_data_plot['Open'],
            high=stock_data_plot['High'],
            low=stock_data_plot['Low'],
            close=stock_data_plot['Close'],
            name='Candlestick'), row=1, col=1)

        # Plot Bollinger Bands
        fig.add_trace(go.Scatter(
            x=stock_data_plot.index,
            y=stock_data_plot['UB'],
            mode='lines',
            name='Upper Bollinger Band',
            line=dict(color='purple')), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=stock_data_plot.index,
            y=stock_data_plot['LB'],
            mode='lines',
            name='Lower Bollinger Band',
            line=dict(color='red')), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=stock_data_plot.index,
            y=stock_data_plot['SMA'],
            mode='lines',
            name=f'{self.window}-day SMA',
            line=dict(color='blue')), row=1, col=1)

        # Plot RSI in the second subplot
        fig.add_trace(go.Scatter(
            x=stock_data_plot.index,
            y=stock_data_plot['RSI'],
            mode='lines',
            name='RSI',
            line=dict(color='orange')), row=2, col=1)

        # Add RSI threshold lines (70 and 30)
        fig.add_hline(y=self.RSI_threshold_high, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=self.RSI_threshold_low, line_dash="dash", line_color="green", row=2, col=1)

        # Update layout
        fig.update_layout(
            height =900,
            title=f'Bollinger Bands Strategy for {self.stock.getTicker()}',
            xaxis_title='Date',
            yaxis_title='Price',
            xaxis2_title='Date',  # RSI X-axis title
            yaxis2_title='RSI',   # RSI Y-axis title
            xaxis_rangeslider_visible=False)

        return fig
