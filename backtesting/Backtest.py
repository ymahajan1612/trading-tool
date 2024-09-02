import vectorbt as vbt
from Data import StockData
from strategies.Strategy import *

stock = StockData('AMZN')

class Backtest():
    def __init__(self, strategy):
        self.strategy = strategy
        self.data = self.strategy.getData()
        self.entries, self.exits = self.generateEntryExit()

    
    def generateEntryExit(self):
        signals = self.strategy.generateSignalSeries()

        entry = signals == 1
        exit = signals == -1

        return entry, exit
    
    def run(self):
        portfolio = vbt.Portfolio.from_signals(self.data['Close'], self.entries, self.exits, init_cash=1000, fees=0.001)
        return portfolio
    



SMA = SMACrossOverStrategy(stock, 10, 50)
MACD = MACDStrategy(stock)
BollingerBand = BollingerBandStrategy(stock)
BollingerBand.generatePlot(30)



