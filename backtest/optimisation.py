from strategy.strategies import *
from strategy.factory import StrategyFactory
from backtest.Backtest import Backtester
import numpy as np

class WalkForwardOptimisation:
    def __init__(self, strategy_str, parameter_grid, initial_cash, percentage_commission, stock):
        self.strategy_str = strategy_str
        self.parameter_grid = parameter_grid
        self.initial_cash = initial_cash
        self.percentage_commission = percentage_commission
        self.strategy_factory = StrategyFactory()
        self.stock = stock

    def optimiseParametersInSample(self, in_sample_start=None, in_sample_end=None):
        """
        Find the optimal parameters for the strategy in the range specified
        """
        best_performance = -np.inf
        best_params = None

        for params in self.parameter_grid:
            # create the strategy with the parameters
            strategy = self.strategy_factory.createStrategy(self.strategy_str, self.stock, **params)
            bt = Backtester(strategy)
            portfolio = bt.run(self.initial_cash, self.percentage_commission, start_data=in_sample_start, end_data=in_sample_end)
            performance = portfolio.total_return()

            if performance > best_performance:
                best_performance = performance
                best_params = params

        return best_params, best_performance
    
    def ApplyParametersOutOfSample(self, best_params, out_sample_start=None, out_sample_end=None):
        """
        Apply the best parameters out of sample
        """
        strategy = self.strategy_factory.createStrategy(self.strategy_str, self.stock, **best_params)
        bt = Backtester(strategy)
        portfolio = bt.run(self.initial_cash, self.percentage_commission, start_data=out_sample_start, end_data=out_sample_end)
        return portfolio
    
    def walkForwardOptimisation(self, in_sample_window, out_sample_window):
        """
        Perform walk forward optimisation
        """

        all_portfolios = []
        param_performance_map = {}

        total_data_size = len(self.stock.getDataFrame())

        for i in range(0, total_data_size - (in_sample_window + out_sample_window)):
            in_sample_start = i
            in_sample_end = i + in_sample_window
            out_sample_start = in_sample_end
            out_sample_end = in_sample_end + out_sample_window

            best_params, best_performance = self.optimiseParametersInSample(in_sample_start, in_sample_end)
            portfolio = self.ApplyParametersOutOfSample(best_params, out_sample_start, out_sample_end)
            all_portfolios.append(portfolio)
            param_performance_map[best_performance] = best_params

        return all_portfolios, param_performance_map
