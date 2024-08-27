import os
API_KEY = os.getenv('ALPHA_VANTAGE_KEY')
if not API_KEY:
    raise ValueError("API_KEY not set")