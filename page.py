import streamlit as st

class Page:
    def __init__(self):
        self.pages = []
        st.set_page_config(
            page_title="Stock Data Analysis",
            page_icon="📈",
            layout="wide"
        )
    
    def add_page(self, title, func, **function_parameters):
        self.pages.append({
            "title": title,
            "func": func,
            "function_parameters": function_parameters
        })
    
    def run(self):
        app = st.selectbox(
            'Navigation',
            self.pages,
            format_func=lambda page: page['title']
        )

        app['func'](**app['function_parameters']) if app["function_parameters"] else app['func']()