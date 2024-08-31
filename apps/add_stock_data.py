from Strategy import BollingerBandStrategy, SMACrossOverStrategy, MACDStrategy
from Data import StockData
import streamlit as st
from test_stock_data import add_stock

def app():
    # st.set_page_config(page_title="Stock Trading Strategies Tool", page_icon="📈", layout="wide")
    strategy_mapping = {
        "Bollinger Band Strategy": BollingerBandStrategy,
        "SMA Crossover Strategy": SMACrossOverStrategy,
        "MACD Strategy": MACDStrategy
    }

    strategy_params = dict()

    st.markdown("<h1 style='text-align: center;'>Stock Trading Strategies Tool 📈</h1>", unsafe_allow_html=True)

    st.markdown("<h2 style='text-align: left;'>Select a Stock Ticker Symbol</h2>", unsafe_allow_html=True)
    stock_ticker = st.text_input(label = "Stock Ticker",value="AAPL",label_visibility="collapsed")

    st.markdown("<h2 style='text-align: left;'>Select a Trading Strategy</h2>", unsafe_allow_html=True)
    strategy = st.selectbox("Select Strategy", ["Bollinger Band Strategy", "SMA Crossover Strategy", "MACD Strategy"],label_visibility="collapsed")

    st.markdown("<h2 style='text-align: left;'>Select the Parameters for the Trading Strategy</h2>", unsafe_allow_html=True)

    if strategy == "SMA Crossover Strategy":
        strategy_params["short_window"] = st.slider("SMA Short Window", min_value=1, max_value=50, value=10, step=1)
        strategy_params["long_window"] = st.slider("SMA Long Window", min_value=1, max_value=200, value=50, step=1)
    elif strategy == "MACD Strategy":
        strategy_params["short_window"] = st.slider("EMA Short Window (Default: 12)", min_value=1, max_value=50, value=12, step=1)
        strategy_params["long_window"] = st.slider("EMA Long Window (Default: 26) ", min_value=1, max_value=200, value=26, step=1)
        strategy_params["signal_window"] = st.slider("Signal Window (Default: 9)", min_value=1, max_value=50, value=9, step=1)
    elif strategy == "Bollinger Band Strategy":
        strategy_params["window"] = st.slider("Bollinger Band Window", min_value=1, max_value=50, value=20, step=1)
        strategy_params["standard_deviations"] = st.slider("Number of Standard Deviations", min_value=1, max_value=5, value=2, step=1)

    st.markdown("<h2 style='text-align: left;'>Select The Number Of Data Points to Plot</h2>", unsafe_allow_html=True)
    days = st.slider("Data Points", min_value=30, max_value=100, value=90, step=1,label_visibility="collapsed")

    enabled = True if stock_ticker and strategy else False

    execute_button_clicked = st.button("Done",key="execute_button",disabled=not enabled)

    if execute_button_clicked:
        stock = StockData(stock_ticker)
        error = stock.getError()
        if error:
            st.error(error,icon="🚨")
        else:
            add_stock(stock_ticker, strategy)
            strategy = strategy_mapping[strategy](stock, **strategy_params)
        

    