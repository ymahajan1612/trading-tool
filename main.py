from Algorithm import BollingerBandStrategy, SMACrossOverStrategy, MACDStrategy
from Data import StockData
from Backtest import Backtester

Stock = StockData('LGEN')

BollingerBand = BollingerBandStrategy(Stock)
backtesting = Backtester(BollingerBand, Stock, 1000)
backtesting.run()