import vectorbt as vbt
import numpy as np
from strategy.strategies import *

class Backtester():
    def __init__(self, strategy):
        self.strategy = strategy
        
        self.data = self.strategy.getData()
        self.entries, self.exits = self.generateEntryExit()

    
    def generateEntryExit(self):
        """
        Generate the entry and exit signals for the strategy
        """
        
        signals = self.strategy.generateSignalSeries()

        entry = signals == 1
        exit = signals == -1

        return entry, exit
    
    def run(self, initial_cash, percentage_commission, start_data=None, end_data=None):
        """
        Run the backtest using the strategy
        """
        if start_data and end_data:
            data = self.data.loc[start_data:end_data]
            entries = self.entries.loc[start_data:end_data]
            exits = self.exits.loc[start_data:end_data]
        elif start_data:
            data = self.data.loc[start_data:]
            entries = self.entries.loc[start_data:]
            exits = self.exits.loc[start_data:] 
        elif end_data:
            data = self.data.loc[:end_data]
            entries = self.entries.loc[:end_data]
            exits = self.exits.loc[:end_data]
        else:
            data = self.data
            entries = self.entries
            exits = self.exits
        
        commission = percentage_commission / 100
        portfolio = vbt.Portfolio.from_signals(data['Close'], entries, exits, init_cash=initial_cash, fees=commission)
        return portfolio
    





