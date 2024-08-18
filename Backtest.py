from Portfolio import TestPortfolio
class Backtester():
    def __init__(self, strategy, stock, initial_capital):
        self.strategy = strategy
        print(self.strategy)
        self.stock = stock
        self.data = self.strategy.getData()########################################################
        self.portfolio = TestPortfolio(initial_capital)

    def run(self):

        for i in range(1, len(self.data)):
            current_price = self.data['Close'][i]
            signal = self.strategy.generateSignal(current_index = i)
            if signal == 0:
                continue
            if signal == 1:
                self.portfolio.buy(self.stock.ticker, current_price,num_shares=10, commission=0.002)
            if signal == -1 and self.stock.getTicker() in self.portfolio.getHoldings():
                self.portfolio.sell(self.stock.ticker, current_price, num_shares=5,commission=0.002)
        print(self.portfolio.getHoldings())
        print(self.portfolio.getPortfolioValue())

