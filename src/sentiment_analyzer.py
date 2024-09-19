import requests
from datetime import datetime, timedelta

class SentimentAnalyzer:
    def __init__(self):
        self.base_url = "https://api.alternative.me/fng/"
        self.sentiment_data = self.load_yearly_sentiment()

    def load_yearly_sentiment(self):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        params = {
            'limit': 365,
            'date_format': 'us',
            'format': 'json'
        }
        try:
            response = requests.get(self.base_url, params=params)
            data = response.json()
            sentiment_data = {}
            for item in data['data']:
                try:
                    # Try multiple date formats
                    date = self.parse_date(item['timestamp'])
                    sentiment_data[date] = int(item['value'])
                except ValueError:
                    print(f"Warning: Unable to parse date {item['timestamp']}")
            return sentiment_data
        except Exception as e:
            print(f"Error fetching Fear and Greed Index: {str(e)}")
            return {}

    def parse_date(self, date_string):
        date_formats = ['%d-%m-%Y', '%m-%d-%Y', '%Y-%m-%d']
        for date_format in date_formats:
            try:
                return datetime.strptime(date_string, date_format).date()
            except ValueError:
                continue
        raise ValueError(f"Unable to parse date: {date_string}")

    def get_fear_and_greed_index(self, date):
        return self.sentiment_data.get(date.date(), None)

    def interpret_sentiment(self, index):
        if index is None:
            return "Unknown"
        elif index <= 60:
            return "Fear"
        elif index >= 70:
            return "Greed"
        else:
            return "Neutral"