import streamlit as st
from DatabaseHandler import DBHandler
from strategy.Strategy import *
from strategy.strategy_mapping import get_strategy
from Data import StockData
from Backtest import Backtester 
def app(stock_strategy_id):
    database_client = DBHandler()
    ticker, strategy_name, params = database_client.getStockStrategy(stock_strategy_id)
    stock = StockData(ticker)
    last_updated = stock.getFetchTime()
    error = stock.getError()
    if error:
        st.error(error, icon="🚨")
    else:
        strategy = get_strategy(strategy_name)(stock, **params)
        st.write(f"last updated: {last_updated}")
        delete_button = st.button("Delete Strategy", key="delete")

        st.subheader("Plot for {} with {}".format(ticker, strategy_name))

        days_to_plot = st.slider("Adjust Plot Window", min_value=10, max_value=120, value=100, step=1)
        plot = strategy.generatePlot(days_to_plot)
        st.pyplot(plot)

        if delete_button:
            database_client.removeStockStrategy(stock_strategy_id=stock_strategy_id)
            st.rerun()
        
        st.subheader("Backtest This Strategy")
        # create a slider to adjust the initial cash
        initial_cash = st.slider("Initial Cash", min_value=1000, max_value=10000, value=1000, step=100)
        # create a slider for comission fees with minimum 0% and maximum 5% and default 2%
        fees = st.slider("Commission Fees (%)", min_value=0.0, max_value=5.0, value=2.0, step=0.1)

        backtest_button = st.button("Run Backtest")

        if backtest_button:
            backtester = Backtester(strategy)
            portfolio = backtester.run(initial_cash, fees)
            backtest_results = portfolio.stats()
            st.dataframe(backtest_results, width=20000, height=500)
