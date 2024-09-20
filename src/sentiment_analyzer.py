import requests
from datetime import datetime, timedelta

class SentimentAnalyzer:
    def __init__(self):
        self.base_url = "https://api.alternative.me/fng/"
        self.cache = {}

    def get_fear_and_greed_index(self, date):
        if date in self.cache:
            return self.cache[date]

        try:
            response = requests.get(f"{self.base_url}?date={date.strftime('%d-%m-%Y')}")
            data = response.json()
            if data['data']:
                sentiment_value = int(data['data'][0]['value'])
                self.cache[date] = sentiment_value
                return sentiment_value
            else:
                print(f"No sentiment data available for {date}")
                return None
        except Exception as e:
            print(f"Error fetching sentiment data for {date}: {str(e)}")
            return None

    def interpret_sentiment(self, sentiment_index):
        if sentiment_index is None:
            return "Unknown"
        elif sentiment_index <= 20:
            return "Extreme Fear"
        elif sentiment_index <= 40:
            return "Fear"
        elif sentiment_index <= 60:
            return "Neutral"
        elif sentiment_index <= 80:
            return "Greed"
        else:
            return "Extreme Greed"