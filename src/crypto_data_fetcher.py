import requests
from datetime import datetime, timedelta

class CryptoDataFetcher:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"

    def get_historical_data(self, coin_id, vs_currency, days):
        endpoint = f"{self.base_url}/coins/{coin_id}/market_chart"
        params = {
            "vs_currency": vs_currency,
            "days": days,
            "interval": "daily"
        }
        
        response = requests.get(endpoint, params=params)
        response.raise_for_status()  # Raise an exception for bad responses
        
        data = response.json()
        
        # Process the data into the format expected by test_data_fetcher.py
        processed_data = []
        for timestamp, price in data['prices']:
            date = datetime.fromtimestamp(timestamp / 1000)  # Convert milliseconds to seconds
            processed_data.append({
                'date': date,
                'price': price
            })
        
        return processed_data

    def get_latest_price(self, coin_id, vs_currency):
        endpoint = f"{self.base_url}/simple/price"
        params = {
            "ids": coin_id,
            "vs_currencies": vs_currency
        }
        
        response = requests.get(endpoint, params=params)
        response.raise_for_status()  # Raise an exception for bad responses
        
        data = response.json()
        return data[coin_id][vs_currency]