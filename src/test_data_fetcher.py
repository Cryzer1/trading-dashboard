import sys
import os
import pandas as pd
from datetime import datetime
import streamlit as st
from .sentiment_analyzer import SentimentAnalyzer

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from .crypto_data_fetcher import CryptoDataFetcher
from .trading_logic import TradingLogic
from config import config

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_and_analyze_data():
    fetcher = CryptoDataFetcher()
    sentiment_analyzer = SentimentAnalyzer()
    try:
        historical_data = fetcher.get_historical_data(
            coin_id=config.COIN_ID,
            vs_currency=config.VS_CURRENCY,
            days=365  # Fetch 1 year of data for better backtesting
        )
        
        if not historical_data:
            st.warning("Error: No historical data returned.")
            return None
        
        # Convert the list of dictionaries to a DataFrame
        df = pd.DataFrame(historical_data)
        df['date'] = pd.to_datetime(df['date'])
        
        # Sort the DataFrame by date
        df = df.sort_values('date')
        
        # Initialize the trading strategy with $50 USD and $50 worth of BTC
        initial_total = 100
        strategy = TradingLogic(initial_usd=initial_total/2, initial_btc_usd=initial_total/2)
        
        # Run the backtest
        df['decision'] = ''
        df['portfolio_value'] = 0.0
        df['sentiment'] = ''
        
        for i, row in df.iterrows():
            decision = strategy.make_decision(row['price'], row['date'])
            portfolio_value = strategy.execute_trade(decision, row['price'], row['date'])
            sentiment_index = sentiment_analyzer.get_fear_and_greed_index(row['date'])
            sentiment = sentiment_analyzer.interpret_sentiment(sentiment_index)
            df.at[i, 'decision'] = decision
            df.at[i, 'portfolio_value'] = portfolio_value
            df.at[i, 'sentiment'] = sentiment
        
        # Normalize the price and portfolio value
        initial_price = df['price'].iloc[0]
        df['normalized_price'] = df['price'] / initial_price * 100
        df['normalized_portfolio'] = df['portfolio_value'] / initial_total * 100

        return df

    except Exception as e:
        st.error(f"Error fetching and analyzing data: {str(e)}")
        return None

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_data_for_dashboard():
    df = fetch_and_analyze_data()
    if df is not None:
        # Rename columns to match the expected format in the dashboard
        df = df.rename(columns={
            'date': 'Date',
            'price': 'Close',
            'normalized_price': 'NormalizedPrice',
            'normalized_portfolio': 'NormalizedPortfolio',
            'decision': 'Signal',
            'sentiment': 'Sentiment'
        })
        return df
    else:
        return pd.DataFrame()  # Return an empty DataFrame if there's an error

if __name__ == "__main__":
    df = fetch_and_analyze_data()
    if df is not None:
        print(df.head())
        print("Data fetched and analyzed successfully.")
    else:
        print("Failed to fetch and analyze data.")