from abc import ABC, abstractmethod


class Algorithm(ABC):
    def __init__(self,data, short_window=None, long_window=None):
        self.data = data
        self.short_window = short_window
        self.long_window = long_window
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


class MACDStrategy(Algorithm):
    def __init__(self, data, short_window=12, long_window=26, signal_window=9):
        self.signal_window = signal_window
        super().__init__(data.copy(), short_window, long_window)
        
    def preprocessData(self):
        self.data['EMA_200'] = self.calculateEMA(200) 
        self.data['MACD'] = self.calculateEMA(self.short_window) - self.calculateEMA(self.long_window)
        self.data['Signal_line'] = self.data['MACD'].ewm(span=self.signal_window, adjust=False).mean()
        self.data['MACD_histogram'] = self.data['MACD'] - self.data['signal_line']
        self.data.fillna(0, inplace=True)
        self.data = self.data.tail(200)

    def generateSignal(self):
        curr = self.data.iloc[-1]
        prev = self.data.iloc[-2]

        if (prev['MACD'] < prev['signal_line'] and 
            curr['MACD'] > curr['signal_line'] and 
            curr['MACD_histogram'] < 0 and 
            curr['Closing'] > curr['EMA_200']):
            return 1  # Buy signal
        
        if (prev['MACD'] > prev['signal_line'] and 
            curr['MACD'] < curr['signal_line'] and 
            curr['MACD_histogram'] > 0 and 
            curr['Closing'] < curr['EMA_200']):
            return -1  # Sell signal
        
        return 0  # Hold signal



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





