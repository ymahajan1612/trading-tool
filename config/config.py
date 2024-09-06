import os
"""
This file contains the configuration for the project. It contains the API key for the Alpha Vantage API
"""
API_KEY = os.getenv('ALPHA_VANTAGE_KEY')
if not API_KEY:
    raise ValueError("API_KEY not set")