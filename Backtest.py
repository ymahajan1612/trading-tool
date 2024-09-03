import vectorbt as vbt
from Data import StockData
from strategy.Strategy import *

stock = StockData('AMZN')

class Backtester():
    def __init__(self, strategy):
        self.strategy = strategy
        self.data = self.strategy.getData()
        self.entries, self.exits = self.generateEntryExit()

    
    def generateEntryExit(self):
        signals = self.strategy.generateSignalSeries()

        entry = signals == 1
        exit = signals == -1

        return entry, exit
    
    def run(self, initial_cash, percentage_commission):
        commission = percentage_commission / 100
        portfolio = vbt.Portfolio.from_signals(self.data['Close'], self.entries, self.exits, init_cash=initial_cash, fees=commission)
        return portfolio
    





