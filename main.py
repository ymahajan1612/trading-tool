import streamlit as st
from page import Page
from apps import add_stock_data, view_stock_data
from test_stock_data import test_saved_data

page = Page()

page.add_page("Add Stock Data", add_stock_data.app)

for stock, strategy in test_saved_data.items():
    page.add_page(f"{stock} : {strategy}", view_stock_data.app)

page.run()