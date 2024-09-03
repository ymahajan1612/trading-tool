from strategy.Strategy import BollingerBandStrategy, SMACrossOverStrategy, MACDStrategy
from Data import StockData
import streamlit as st
from DatabaseHandler import DBHandler
import time
# st.set_page_config(page_title="Stock Trading Strategies Tool", page_icon="📈", layout="wide")
def app():


    strategy_mapping = {
        "Bollinger Band Strategy": BollingerBandStrategy,
        "SMA Crossover Strategy": SMACrossOverStrategy,
        "MACD Strategy": MACDStrategy
    }

    def addStockToDatabase(stock_ticker, strategy_str, strategy_params):
        stock = StockData(stock_ticker)
        error = stock.getError()
        if error:
            st.error(error,icon="🚨")
        else:
            strategy = strategy_mapping[strategy_str](stock, **strategy_params)
            database_client = DBHandler()
            error = database_client.insertStrategy(strategy, strategy_params)
            if not error:
                st.success(f"{strategy_str} for {stock_ticker} successfully added!",icon="🚀")
                time.sleep(2)
                st.rerun()
            else:
                st.error(error,icon="🚨")

    strategy_params = dict()

    st.markdown("<h1 style='text-align: center;'>Stock Trading Strategies Tool 📈</h1>", unsafe_allow_html=True)

    st.markdown("<h2 style='text-align: left;'>Select a Stock Ticker Symbol</h2>", unsafe_allow_html=True)
    stock_ticker = st.text_input(label = "Stock Ticker",value="AAPL",label_visibility="collapsed").upper()

    st.markdown("<h2 style='text-align: left;'>Select a Trading Strategy</h2>", unsafe_allow_html=True)
    strategy_str = st.selectbox("Select Strategy", ["Bollinger Band Strategy", "SMA Crossover Strategy", "MACD Strategy"],label_visibility="collapsed")

    st.markdown("<h2 style='text-align: left;'>Select the Parameters for the Trading Strategy</h2>", unsafe_allow_html=True)

    if strategy_str == "SMA Crossover Strategy":
        strategy_params["short_window"] = st.slider("SMA Short Window", min_value=1, max_value=50, value=10, step=1)
        strategy_params["long_window"] = st.slider("SMA Long Window", min_value=1, max_value=200, value=50, step=1)
    elif strategy_str == "MACD Strategy":
        strategy_params["short_window"] = st.slider("EMA Short Window (Default: 12)", min_value=1, max_value=50, value=12, step=1)
        strategy_params["long_window"] = st.slider("EMA Long Window (Default: 26) ", min_value=1, max_value=200, value=26, step=1)
        strategy_params["signal_window"] = st.slider("Signal Window (Default: 9)", min_value=1, max_value=50, value=9, step=1)
    elif strategy_str == "Bollinger Band Strategy":
        strategy_params["window"] = st.slider("Bollinger Band Window", min_value=1, max_value=50, value=20, step=1)
        strategy_params["standard_deviations"] = st.slider("Number of Standard Deviations", min_value=1, max_value=5, value=2, step=1)


    enabled = True if stock_ticker and strategy_str else False

    save_button = st.button("Add Data", disabled=not enabled)

    if save_button:
        addStockToDatabase(stock_ticker, strategy_str, strategy_params)



        

    