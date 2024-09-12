from strategy.strategies import *
from strategy.factory import StrategyFactory
from backtest.Backtest import Backtester
import numpy as np
from itertools import product

class WalkForwardOptimisation:
    def __init__(self, strategy_str,stock):
        self.strategy_str = strategy_str
        self.parameter_grid = self.createParameterGrid()
        self.initial_cash = 10000
        self.percentage_commission = 2
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
    
    def createParameterGrid(self):
        if self.strategy_str == "SMA Crossover Strategy":
            short_window = np.arange(1, 50, 5)
            long_window = np.arange(1, 200, 5)
            return [{"short_window": short, "long_window": long} for short, long in product(short_window, long_window) if short < long]
        elif self.strategy_str == "MACD Strategy":
            ema_short_window = np.arange(1, 50, 5)
            ema_long_window = np.arange(1, 200, 5)
            signal_window = np.arange(1, 50, 5)
            return [{"short_window": short, "long_window": long, "signal_window": signal} for short, long, signal in product(ema_short_window, ema_long_window, signal_window) if short < long]
        elif self.strategy_str == "Bollinger Band Strategy":
            window = np.arange(1, 50, 1)
            standard_deviations = np.arange(1, 5, 1)
            return [{"window": window, "standard_deviations": std} for window, std in product(window, standard_deviations)]

    def run(self, in_sample_percentage, out_sample_percentage):
        """
        Perform walk forward optimisation
        """

        all_portfolios = []
        performance_parameter_map = {}

        total_data_size = self.strategy_factory.createStrategy(self.strategy_str, self.stock, **self.parameter_grid[0]).getDataSize()
        half_window = int(total_data_size / 2)

        in_sample_window = int(half_window * in_sample_percentage)
        out_sample_window = int(half_window * out_sample_percentage)
        step_size = int(out_sample_window / 2)

        i = 0

        while i + in_sample_window + out_sample_window <= total_data_size:
            in_sample_start = i
            in_sample_end = i + in_sample_window
            out_sample_start = in_sample_end
            out_sample_end = min(out_sample_start + out_sample_window, total_data_size)  
            best_params, best_performance = self.optimiseParametersInSample(in_sample_start, in_sample_end)
            performance_parameter_map[best_performance] = best_params

            portfolio = self.ApplyParametersOutOfSample(best_params, out_sample_start, out_sample_end)
            all_portfolios.append(portfolio)

            i += step_size
        return all_portfolios, performance_parameter_map
    

