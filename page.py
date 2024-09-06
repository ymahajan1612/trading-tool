import streamlit as st

class Page:
    """
    This class is used to create a page object that will store the different pages of the application
    """
    def __init__(self):
        # List to store all the pages
        self.pages = []
        st.set_page_config(
            page_title="Stock-Strategy Analysis Tool",
            page_icon="📈",
            layout="wide"
        )
    
    def addPage(self, title, func, **function_parameters):
        """
        Adds a page. Certain pages may require parameters to be 
        passed to their functions so this method accepts a dictionary of parameters as keyword arguments
        """
        self.pages.append({
            "title": title,
            "func": func,
            "function_parameters": function_parameters
        })
    
    def run(self):
        # Display the navigation bar containing the different pages
        app = st.selectbox(
            'Navigation',
            self.pages,
            format_func=lambda page: page['title']
        )
        # Run the selected page passing the parameters if they exist
        app['func'](**app['function_parameters']) if app["function_parameters"] else app['func']()