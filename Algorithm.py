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
    

class SMACrossOverAlgorithm(Algorithm):
    def __init__(self, data, short_window, long_window):
        super().__init__(data, short_window, long_window)

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


class MACDAlgorithm(Algorithm):
    def __init__(self, data, short_window=12, long_window=26, signal_window=9):
        self.signal_window = signal_window
        super().__init__(data, short_window, long_window)
        
    def preprocessData(self):
        self.data['EMA_200'] = self.calculateEMA(200) 
        self.data['MACD'] = self.calculateEMA(self.short_window) - self.calculateEMA(self.long_window)
        self.data['signal_line'] = self.data['MACD'].ewm(span=self.signal_window, adjust=False).mean()
        self.data['MACD_histogram'] = self.data['MACD'] - self.data['signal_line']
        self.data.fillna(0, inplace=True)
        self.data = self.data.tail(200)

    def generateSignal(self):
        curr = self.data.iloc[-1]
        prev = self.data.iloc[-2]

        if (prev['MACD'] < prev['signal_line']) and (curr['MACD'] > curr['signal_line']) and (curr['MACD_histogram'] < 0) and (curr['Closing'] > curr['EMA_200']):
            return 1  # Buy signal
        if (prev['MACD'] > prev['signal_line']) and (curr['MACD'] < curr['signal_line']) and (curr['MACD_histogram'] > 0) and (curr['Closing'] < curr['EMA_200']):
            return -1  # Sell signal
        return 0  # Hold signal
