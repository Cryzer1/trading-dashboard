import sys
import os
import pandas as pd
from datetime import datetime
import streamlit as st
from .sentiment_analyzer import SentimentAnalyzer
from .trading_logic import SimpleMovingAverageStrategy, RSIStrategy, MACDStrategy, BollingerBandsStrategy, SentimentBasedStrategy

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from .crypto_data_fetcher import CryptoDataFetcher
from config import config

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_historical_data():
    fetcher = CryptoDataFetcher()
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
        
        return df

    except Exception as e:
        st.error(f"Error fetching historical data: {str(e)}")
        return None

@st.cache_data(ttl=3600)  # Cache for 1 hour
def analyze_strategy(df, strategy_class, **strategy_params):
    sentiment_analyzer = SentimentAnalyzer()
    initial_total = 100
    strategy = strategy_class(initial_usd=initial_total/2, initial_btc_usd=initial_total/2, **strategy_params)
    
    decisions = []
    portfolio_values = []
    sentiments = []
    
    for _, row in df.iterrows():
        decision = strategy.make_decision(row['price'], row['date'])
        portfolio_value = strategy.execute_trade(decision, row['price'], row['date'])
        sentiment_index = sentiment_analyzer.get_fear_and_greed_index(row['date'])
        sentiment = sentiment_analyzer.interpret_sentiment(sentiment_index)
        decisions.append(decision)
        portfolio_values.append(portfolio_value)
        sentiments.append(sentiment)
    
    df = df.copy()
    df['decision'] = decisions
    df['portfolio_value'] = portfolio_values
    df['sentiment'] = sentiments
    
    # Normalize the price and portfolio value
    initial_price = df['price'].iloc[0]
    df['normalized_price'] = df['price'] / initial_price * 100
    df['normalized_portfolio'] = df['portfolio_value'] / initial_total * 100

    return df

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_data_for_dashboard(selected_strategies):
    df = fetch_historical_data()
    if df is not None:
        strategies = {
            'Simple Moving Average': (SimpleMovingAverageStrategy, {'short_window': 10, 'long_window': 50}),
            'RSI': (RSIStrategy, {'window': 14, 'oversold': 30, 'overbought': 70}),
            'MACD': (MACDStrategy, {'fast_period': 12, 'slow_period': 26, 'signal_period': 9}),
            'Bollinger Bands': (BollingerBandsStrategy, {'window': 20, 'num_std': 2}),
            'Sentiment Based': (SentimentBasedStrategy, {}),
        }
        
        results = {}
        for strategy_name in selected_strategies:
            strategy_class, strategy_params = strategies[strategy_name]
            strategy_df = analyze_strategy(df, strategy_class, **strategy_params)
            results[strategy_name] = strategy_df.rename(columns={
                'date': 'Date',
                'price': 'Close',
                'normalized_price': 'NormalizedPrice',
                'normalized_portfolio': f'NormalizedPortfolio_{strategy_name}',
                'decision': f'Signal_{strategy_name}',
                'sentiment': 'Sentiment'
            })
        
        # Add Bitcoin price data
        results['Bitcoin'] = df.rename(columns={
            'date': 'Date',
            'price': 'Close',
            'normalized_price': 'NormalizedPrice'
        })
        
        return results
    else:
        return {}

if __name__ == "__main__":
    df = fetch_historical_data()
    if df is not None:
        print(df.head())
        print("Data fetched successfully.")
    else:
        print("Failed to fetch data.")