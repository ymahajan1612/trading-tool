import streamlit as st
from page import Page
from apps import add_stock_data, view_stock_data
from DatabaseHandler import DBHandler

page = Page()

database_client = DBHandler()
stock_strategies = database_client.getAllStockStrategies()
print(stock_strategies)
page.add_page("Add Stock Data", add_stock_data.app)

for ticker, ticker_entry in stock_strategies.items():
    for entry in ticker_entry:
        entry_params = entry[2]
        params_str = ""
        for param, value in entry_params.items():
            if "_" in param:
                param = param.replace("_", " ")
            if param != list(entry_params.keys())[-1]:
                params_str += f"{param}: {value}, "
            else:
                params_str += f"{param}: {value}"
        page.add_page(f"View {entry[1]} for {ticker} ({params_str})", view_stock_data.app, stock_strategy_id=entry[0])



page.run()