from Strategy import BollingerBandStrategy, SMACrossOverStrategy, MACDStrategy
from Data import StockData


Stock = StockData('AAPL')
SMA = SMACrossOverStrategy(Stock, 10, 30)

