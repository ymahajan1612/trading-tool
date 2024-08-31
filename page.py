import streamlit as st

class Page:
    def __init__(self):
        self.pages = []
    
    def add_page(self, title, func):
        self.pages.append({
            "title": title,
            "func": func
        })
    
    def run(self):
        app = st.selectbox(
            'Navigation',
            self.pages,
            format_func=lambda page: page['title']
        )

        app['func']()