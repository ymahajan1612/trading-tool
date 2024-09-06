import streamlit as st
from data.DatabaseHandler import DBHandler
from strategy.strategies import *
from strategy.factory import StrategyFactory
from data.Data import StockData
from backtest.Backtest import Backtester 

def app(stock_strategy_id):
    """
    This method is the function for the View Stock Data page. This page allows users to view the stock data and strategy
    """
    database_client = DBHandler()

    ticker, strategy_name, params = database_client.getStockStrategy(stock_strategy_id)
    # create a stock object
    stock = StockData(ticker)
    last_updated = stock.getFetchTime()
    # Check if there is an error in the stock data
    error = stock.getError()
    if error:
        st.error(error, icon="🚨")
    else:
        
        factory = StrategyFactory()
        strategy = factory.createStrategy(strategy_name, stock, **params)
        st.write(f"last updated: {last_updated}")
        delete_button = st.button("Delete Strategy", key="delete")

        st.subheader("Plot for {} with {}".format(ticker, strategy_name))

        # slider for the user to adjust the plot window
        days_to_plot = st.slider("Adjust Plot Window", min_value=10, max_value=120, value=100, step=1)
        plot = strategy.generatePlot(days_to_plot)
        st.pyplot(plot)

        if delete_button:
            database_client.removeStockStrategy(stock_strategy_id=stock_strategy_id)
            st.rerun()
        

        # This section is for the user to backtest the strategy

        st.subheader("Backtest This Strategy")
        # create a slider to adjust the initial cash
        initial_cash = st.slider("Initial Cash", min_value=1000, max_value=10000, value=1000, step=100)
        # create a slider for comission fees with minimum 0% and maximum 5% and default 2%
        fees = st.slider("Commission Fees (%)", min_value=0.0, max_value=5.0, value=2.0, step=0.1)

        backtest_button = st.button("Run Backtest")

        if backtest_button:
            backtester = Backtester(strategy)
            with st.spinner("Running backtest..."):
                portfolio = backtester.run(initial_cash, fees)
                backtest_results = portfolio.stats()
    
            st.dataframe(backtest_results, use_container_width=True)
