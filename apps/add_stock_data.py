from data.Data import StockData
from strategy.factory import StrategyFactory
import streamlit as st
from data.DatabaseHandler import DBHandler
from backtest.optimisation import WalkForwardOptimisation
import math
import time

def app():
    """
    The main function for the Add Stock Data page. This page allows users to add stock and strategy to track
    """

    def addStockToDatabase(strategy, strategy_str, strategy_params):
        """
        Adds a stock and strategy to the database given the stock ticker, strategy string, and strategy parameters
        """
        # Getting the stock data and checking for errors, displaying an error message if there is one
        stock_ticker = strategy.getTicker()
        # Creating a database client and inserting the strategy, displaying an error message if there is one during insertion
        database_client = DBHandler()
        error = database_client.insertStrategy(strategy, strategy_params)
        if not error:
            st.success(f"{strategy_str} for {stock_ticker} successfully added!",icon="🚀")
            time.sleep(2)
            st.rerun()
        else:
            st.error(error,icon="🚨")

    # This dictionary will store the parameters for the selected strategy
    strategy_params = dict()

    # Creating a strategy factory
    factory = StrategyFactory()

    st.markdown("<h1 style='text-align: center;'>Stock Trading Strategies Tool 📈</h1>", unsafe_allow_html=True)

    st.markdown("<h2 style='text-align: left;'>Select a Stock Ticker Symbol</h2>", unsafe_allow_html=True)
    stock_ticker = st.text_input(label = "Stock Ticker",value="AAPL",label_visibility="collapsed").upper()

    st.markdown("<h2 style='text-align: left;'>Select a Trading Strategy</h2>", unsafe_allow_html=True)
    strategy_str = st.selectbox("Select Strategy", factory.getStrategyNames(),label_visibility="collapsed")

    optimise = False
    optimise_button = st.button("Optimise Parameters", disabled=not stock_ticker)
    if optimise_button:
        stock = StockData(stock_ticker)
        if stock.getError():
            st.error(stock.getError(), icon="🚨")
        else:
            optimise = True
            with st.spinner("Optimising Parameters..."):
                optimiser = WalkForwardOptimisation(strategy_str, stock)
                all_portfolios, performance_parameter_map = optimiser.run(0.7, 0.3)
                # get the parameters with the best performance
                best_performance = max(list(performance_parameter_map.keys()))
                best_params = performance_parameter_map[best_performance]

            st.success(f"Optimisation Complete! Best {strategy_str} Parameters for {stock_ticker}: {best_params} with return: {round(best_performance,3) * 100}%",icon="🚀")

    st.markdown("<h2 style='text-align: left;'>Select the Parameters for the Trading Strategy</h2>", unsafe_allow_html=True)

    if strategy_str == "SMA Crossover Strategy":
        short_window_value = 10
        long_window_value = 50
        if optimise:
            short_window_value = best_params["short_window"]
            long_window_value = best_params["long_window"]
        strategy_params["short_window"] = st.slider("SMA Short Window", min_value=1, max_value=50, value=short_window_value, step=1)
        strategy_params["long_window"] = st.slider("SMA Long Window", min_value=1, max_value=200, value=long_window_value, step=1)
    elif strategy_str == "MACD Strategy":
        short_window_value = 12
        long_window_value = 26
        signal_window_value = 9
        if optimise:
            short_window_value = best_params["short_window"]
            long_window_value = best_params["long_window"]
            signal_window_value = best_params["signal_window"]
        strategy_params["short_window"] = st.slider("EMA Short Window (Default: 12)", min_value=1, max_value=50, value=short_window_value, step=1)
        strategy_params["long_window"] = st.slider("EMA Long Window (Default: 26) ", min_value=1, max_value=200, value=long_window_value, step=1)
        strategy_params["signal_window"] = st.slider("Signal Window (Default: 9)", min_value=1, max_value=50, value=signal_window_value, step=1)
    elif strategy_str == "Bollinger Band Strategy":
        window_value = 20
        standard_deviations_value = 2
        if optimise:
            window_value = best_params["window"]
            standard_deviations_value = best_params["standard_deviations"]
        strategy_params["window"] = st.slider("Bollinger Band Window", min_value=1, max_value=50, value=window_value, step=1)
        strategy_params["standard_deviations"] = st.slider("Number of Standard Deviations", min_value=1, max_value=5, value=standard_deviations_value, step=1)


    enabled = True if stock_ticker and strategy_str else False

    save_button = st.button("Add Data", disabled=not enabled)

    if save_button:
        # Creating a stock with the given stock ticker, checking for errors
        stock = StockData(stock_ticker)
        if stock.getError():
            st.error(stock.getError(), icon="🚨")
        else:    
            # Creating a strategy with the given strategy string and parameters, and adding the stock to the database
            strategy = factory.createStrategy(strategy_str, stock, **strategy_params)
            addStockToDatabase(strategy, strategy_str, strategy_params)



        

    