from Strategy import BollingerBandStrategy, SMACrossOverStrategy, MACDStrategy
from Data import StockData
import streamlit as st


st.sidebar.write("This is a sidebar")

st.markdown("<h1 style='text-align: center;'>Stock Trading Strategies Tool</h1>", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: left;'>Select a Stock Ticker Symbol</h2>", unsafe_allow_html=True)
stock_ticker = st.text_input(label = "",value="AAPL")

st.markdown("<h2 style='text-align: left;'>Select a Trading Strategy</h2>", unsafe_allow_html=True)
strategy = st.selectbox("", ["Bollinger Band Strategy", "SMA Crossover Strategy", "MACD Strategy"])

st.markdown("<h2 style='text-align: left;'>Select the Parameters for the Trading Strategy</h2>", unsafe_allow_html=True)

if strategy == "SMA Crossover Strategy":
    short_window = st.slider("SMA Short Window", min_value=1, max_value=50, value=10, step=1)
    long_window = st.slider("SMA Long Window", min_value=1, max_value=200, value=50, step=1)
elif strategy == "MACD Strategy":
    short_window = st.slider("EMA Short Window (Default: 12)", min_value=1, max_value=50, value=12, step=1)
    long_window = st.slider("EMA Long Window (Default: 26) ", min_value=1, max_value=200, value=26, step=1)
    signal_window = st.slider("Signal Window (Default: 9)", min_value=1, max_value=50, value=9, step=1)
elif strategy == "Bollinger Band Strategy":
    window = st.slider("Bollinger Band Window", min_value=1, max_value=50, value=20, step=1)
    num_std = st.slider("Number of Standard Deviations", min_value=1, max_value=5, value=2, step=1)

st.markdown("<h2 style='text-align: left;'>Select The Number Of Data Points to Plot</h2>", unsafe_allow_html=True)
days = st.slider("", min_value=30, max_value=100, value=90, step=1)