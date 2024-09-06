import streamlit as st
from page import Page
from apps import add_stock_data, view_stock_data
from data.DatabaseHandler import DBHandler



page = Page()

# Creating a database client and getting all the stock strategy instances from the database
database_client = DBHandler()

stock_strategies = database_client.getAllStockStrategies()

page.addPage("Add Stock Data", add_stock_data.app)

for ticker, ticker_entry in stock_strategies.items():

    #For each stock ticker, add a section in the navigation bar to view the stock data

    for entry in ticker_entry:
        # Get the parameters for the stock strategy
        entry_params = entry[2]
        # Create a string representation of the parameters to display in the navigation bar
        params_str = ""
        for param, value in entry_params.items():
            if "_" in param:
                param = param.replace("_", " ")
            if param != list(entry_params.keys())[-1]:
                params_str += f"{param}: {value}, "
            else:
                params_str += f"{param}: {value}"
        # Add a page for that stock strategy entry
        page.addPage(f"View {entry[1]} for {ticker} ({params_str})", view_stock_data.app, stock_strategy_id=entry[0])



page.run()