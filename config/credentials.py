import os
from dotenv import load_dotenv

load_dotenv()

# API keys and credentials
EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY")
EXCHANGE_SECRET_KEY = os.getenv("EXCHANGE_SECRET_KEY")