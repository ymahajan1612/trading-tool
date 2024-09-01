import streamlit as st
from page import Page
from apps import add_stock_data, view_stock_data

page = Page()

page.add_page("Add Stock Data", add_stock_data.app)

page.run()