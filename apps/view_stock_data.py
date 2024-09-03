import streamlit as st
from DatabaseHandler import DBHandler
from strategy.Strategy import *
from strategy.strategy_mapping import get_strategy
from Data import StockData
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
        # Add a slider to adjust number of days to plot
        days_to_plot = st.slider("Number of days to plot", min_value=10, max_value=120, value=100, step=1)
        plot = strategy.generatePlot(days_to_plot)
        st.pyplot(plot)
        delete_button = st.button("Delete Strategy", key="delete")
        if delete_button:
            database_client.removeStockStrategy(stock_strategy_id=stock_strategy_id)
            st.rerun()