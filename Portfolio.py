class TestPortfolio:
    def __init__(self, initial_capital) -> None:
        self.value = initial_capital
        self.value_history = [initial_capital]
        self.holdings = dict() # dictionary mapping ticker : number_of_shares
    
    def buy(self,ticker, price, num_shares, commission):
        total_cost = (price * num_shares)
        total_cost += (total_cost * commission)
        if self.value >= total_cost:
            self.value -= total_cost
            self.holdings[ticker] = self.holdings.get(ticker,0) + num_shares
    
    def sell(self,ticker, price, num_shares, commission):
        if ticker in self.holdings and self.holdings[ticker] >= num_shares:
            revenue = price * num_shares
            revenue -= (revenue * commission)
            self.value += revenue
            self.holdings[ticker] -= num_shares
            if self.holdings[ticker] == 0:
                del self.holdings[ticker]
    
    def updateValue(self, current_prices):
        for ticker, num_shares in self.holdings.items():
            self.value += num_shares * current_prices[ticker]
        self.value_history.append(self.value)

    def getPortfolioValue(self):
        return self.value
    
    def getHoldings(self):
        return self.holdings

    def printPortfolioSummary(self):
        # print("Change in portfolio over time: {change}".format(change = self.))
        print("Portfolio is worth: ${portolio_value}".format(portfolio_value = self.value))
        print("Holdings: {holdings}".format(holdings=self.holdings))