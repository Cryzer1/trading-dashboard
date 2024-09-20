import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st
from concurrent.futures import ProcessPoolExecutor, as_completed
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

def precompute_indicators(df):
    # Precompute common indicators
    df['SMA_short'] = df['price'].rolling(window=10).mean()
    df['SMA_long'] = df['price'].rolling(window=50).mean()
    df['RSI'] = compute_rsi(df['price'], window=14)
    df['MACD'], df['Signal_Line'] = compute_macd(df['price'])
    df['BB_upper'], df['BB_lower'] = compute_bollinger_bands(df['price'])
    return df

def compute_rsi(prices, window=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def compute_macd(prices, fast_period=12, slow_period=26, signal_period=9):
    fast_ema = prices.ewm(span=fast_period, adjust=False).mean()
    slow_ema = prices.ewm(span=slow_period, adjust=False).mean()
    macd = fast_ema - slow_ema
    signal_line = macd.ewm(span=signal_period, adjust=False).mean()
    return macd, signal_line

def compute_bollinger_bands(prices, window=20, num_std=2):
    rolling_mean = prices.rolling(window=window).mean()
    rolling_std = prices.rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)
    return upper_band, lower_band

def analyze_strategy(df, strategy_class, **strategy_params):
    strategy = strategy_class(initial_usd=50, initial_btc_usd=50, **strategy_params)
    decisions = []
    portfolio_values = []

    for _, row in df.iterrows():
        decision = strategy.make_decision(row)
        portfolio_value = strategy.execute_trade(decision, row['price'], row['date'])
        decisions.append(decision)
        portfolio_values.append(portfolio_value)

    df = df.copy()
    df['decision'] = decisions
    df['portfolio_value'] = portfolio_values
    df['normalized_portfolio'] = df['portfolio_value'] / 100 * 100  # Normalize to percentage

    return df

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_data_for_dashboard(selected_strategies):
    df = fetch_historical_data()
    if df is not None:
        df = precompute_indicators(df)
        strategies = {
            'Simple Moving Average': (SimpleMovingAverageStrategy, {}),
            'RSI': (RSIStrategy, {}),
            'MACD': (MACDStrategy, {}),
            'Bollinger Bands': (BollingerBandsStrategy, {}),
            'Sentiment Based': (SentimentBasedStrategy, {}),
        }
        
        results = {}
        
        with ProcessPoolExecutor() as executor:
            future_to_strategy = {executor.submit(analyze_strategy, df, strategy_class, **strategy_params): strategy_name 
                                  for strategy_name, (strategy_class, strategy_params) in strategies.items() 
                                  if strategy_name in selected_strategies}
            
            for future in as_completed(future_to_strategy):
                strategy_name = future_to_strategy[future]
                try:
                    strategy_df = future.result()
                    results[strategy_name] = strategy_df.rename(columns={
                        'date': 'Date',
                        'price': 'Close',
                        'normalized_price': 'NormalizedPrice',
                        'normalized_portfolio': f'NormalizedPortfolio_{strategy_name}',
                        'decision': f'Signal_{strategy_name}',
                    })
                except Exception as exc:
                    st.error(f'{strategy_name} generated an exception: {exc}')
        
        # Add Bitcoin price data
        initial_price = df['price'].iloc[0]
        df['normalized_price'] = df['price'] / initial_price * 100
        results['Bitcoin'] = df.rename(columns={
            'date': 'Date',
            'price': 'Close',
            'normalized_price': 'NormalizedPrice',
            'volume': 'Volume'
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