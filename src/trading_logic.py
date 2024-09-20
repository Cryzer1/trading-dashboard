import pandas as pd
import numpy as np
from .sentiment_analyzer import SentimentAnalyzer
from abc import ABC, abstractmethod

class TradingStrategy(ABC):
    def __init__(self, initial_usd, initial_btc_usd):
        self.usd = initial_usd
        self.btc = initial_btc_usd / initial_usd  # Convert USD value to BTC amount

    @abstractmethod
    def make_decision(self, row):
        pass

    def execute_trade(self, decision, price, date):
        if decision == 'buy' and self.usd > 0:
            btc_to_buy = (self.usd * 0.2) / price  # Buy with 20% of available USD
            self.btc += btc_to_buy
            self.usd -= btc_to_buy * price
        elif decision == 'sell' and self.btc > 0:
            btc_to_sell = self.btc * 0.2  # Sell 20% of available BTC
            self.usd += btc_to_sell * price
            self.btc -= btc_to_sell
        return self.usd + self.btc * price

class SimpleMovingAverageStrategy(TradingStrategy):
    def __init__(self, initial_usd, initial_btc_usd):
        super().__init__(initial_usd, initial_btc_usd)

    def make_decision(self, row):
        if row['SMA_short'] > row['SMA_long']:
            return 'buy'
        elif row['SMA_short'] < row['SMA_long']:
            return 'sell'
        return 'hold'

class RSIStrategy(TradingStrategy):
    def __init__(self, initial_usd, initial_btc_usd, oversold=30, overbought=70):
        super().__init__(initial_usd, initial_btc_usd)
        self.oversold = oversold
        self.overbought = overbought

    def make_decision(self, row):
        rsi = row['RSI']
        if rsi < self.oversold:
            return 'buy'
        elif rsi > self.overbought:
            return 'sell'
        return 'hold'

class MACDStrategy(TradingStrategy):
    def __init__(self, initial_usd, initial_btc_usd):
        super().__init__(initial_usd, initial_btc_usd)
        self.previous_macd = None
        self.previous_signal = None

    def make_decision(self, row):
        current_macd = row['MACD']
        current_signal = row['Signal_Line']
        
        if self.previous_macd is not None and self.previous_signal is not None:
            if current_macd > current_signal and self.previous_macd <= self.previous_signal:
                decision = 'buy'
            elif current_macd < current_signal and self.previous_macd >= self.previous_signal:
                decision = 'sell'
            else:
                decision = 'hold'
        else:
            decision = 'hold'
        
        self.previous_macd = current_macd
        self.previous_signal = current_signal
        return decision

class BollingerBandsStrategy(TradingStrategy):
    def __init__(self, initial_usd, initial_btc_usd):
        super().__init__(initial_usd, initial_btc_usd)

    def make_decision(self, row):
        if row['price'] < row['BB_lower']:
            return 'buy'
        elif row['price'] > row['BB_upper']:
            return 'sell'
        return 'hold'

class SentimentBasedStrategy(TradingStrategy):
    def __init__(self, initial_usd, initial_btc_usd):
        super().__init__(initial_usd, initial_btc_usd)
        self.sentiment_analyzer = SentimentAnalyzer()

    def make_decision(self, row):
        sentiment_index = self.sentiment_analyzer.get_fear_and_greed_index(row['date'])
        if sentiment_index is None:
            return 'hold'  # If we can't get sentiment data, we'll hold
        try:
            sentiment_index = int(sentiment_index)  # Ensure sentiment_index is an integer
            if sentiment_index < 20:  # Extreme fear
                return 'buy'
            elif sentiment_index > 80:  # Extreme greed
                return 'sell'
        except ValueError:
            print(f"Invalid sentiment index value: {sentiment_index}")
        return 'hold'

# You can add more strategy classes here