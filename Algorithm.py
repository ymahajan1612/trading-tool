from abc import ABC, abstractmethod

class Algorithm(ABC):
    def __init__(self,data, short_window, long_window):
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
    

class SMACrossOver(Algorithm):
    def __init__(self, data, short_window, long_window):
        super().__init__(data, short_window, long_window)

    def preprocessData(self):
        self.data['SMA_short'] = self.calculateSMA(self.short_window)
        self.data['SMA_long'] = self.calculateSMA(self.long_window)

        self.data = self.data.tail(90)
    
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


class MACD(Algorithm):
    def __init__(self, data, short_window=12, long_window=26, signal_window=9):
        self.signal_window = signal_window
        super().__init__(data, short_window, long_window)
        


    def preprocessData(self):
        self.data['EMA_short'] = self.calculateEMA(self.short_window)
        self.data['EMA_long'] = self.calculateEMA(self.long_window)
        self.data['MACD'] = self.data['EMA_short'] - self.data['EMA_long']
        self.data['signal_line'] = self.data['MACD'].ewm(span=self.signal_window, adjust=False).mean()
        
    def generateSignal(self):
        curr = self.data.iloc[-1]
        prev = self.data.iloc[-2]

        if (prev['MACD'] < prev['Signal_Line']) and (curr['MACD'] > curr['Signal_Line']) and (curr['MACD_Histogram'] > 0):
            # Generate a buy signal when there an up-trend (Histogram is above 0) and MACD crosses above signal
            return 1  # Buy signal
        if (prev['MACD'] > prev['Signal_Line']) and (curr['MACD'] < curr['Signal_Line']) and (curr['MACD_Histogram'] < 0):
            return -1  # Sell signal
        return 0  # Hold signal