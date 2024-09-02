from strategy.Strategy import SMACrossOverStrategy, MACDStrategy, BollingerBandStrategy

map = {
        "Bollinger Band Strategy": BollingerBandStrategy,
        "SMA Crossover Strategy": SMACrossOverStrategy,
        "MACD Strategy": MACDStrategy
    }

def get_strategy(strategy_name):
    return map[strategy_name]