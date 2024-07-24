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
