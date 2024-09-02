import streamlit as st
from DatabaseHandler import DBHandler
from strategy.Strategy import *
from strategy.strategy_mapping import get_strategy
from Data import StockData
def app(stock_strategy_id):
    database_client = DBHandler()
    ticker, strategy_name, params, time_stamp = database_client.getStockStrategy(stock_strategy_id)
    stock = StockData(ticker)
    error = stock.getError()
    if error:
        st.error(error, icon="🚨")
    else:
        st.write(f"Last Updated: {time_stamp}")
        strategy = get_strategy(strategy_name)(stock, **params)
        plot = strategy.generatePlot()
        st.pyplot(plot)
        delete_button = st.button("Delete Strategy", key="delete")
        if delete_button:
            database_client.removeStockStrategy(stock_strategy_id=stock_strategy_id)
            st.rerun()