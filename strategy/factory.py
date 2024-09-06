from strategy.strategies import SMACrossOverStrategy, MACDStrategy, BollingerBandStrategy

class StrategyFactory:
    """
    Factory class for creating instances of trading strategies dynamically during runtime.
    The class uses a dictionary to map the strategy name to the corresponding strategy class.
    """
    def __init__(self):
        self._strategy_map = {
            "Bollinger Band Strategy": BollingerBandStrategy,
            "SMA Crossover Strategy": SMACrossOverStrategy,
            "MACD Strategy": MACDStrategy
        }

    def createStrategy(self, strategy_name, stock, **strategy_params):
        """
        Creates an instance of the strategy given the strategy name, stock data, and strategy parameters.
        The strategy parameters are provided as keyword arguments, and the strategy name is used to map to the corresponding strategy class.
        """
        return self._strategy_map[strategy_name](stock, **strategy_params)

    def getStrategyNames(self):
        """
        Returns a list of the strategy names available in the factory.
        """
        return list(self._strategy_map.keys())