import pandas as pd
import numpy as np
from .sentiment_analyzer import SentimentAnalyzer
from abc import ABC, abstractmethod

class TradingStrategy(ABC):
    def __init__(self, initial_usd, initial_btc_usd):
        self.usd = initial_usd
        self.btc = initial_btc_usd / initial_usd  # Convert USD value to BTC amount

    @abstractmethod
    def make_decision(self, price, date):
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
    def __init__(self, initial_usd, initial_btc_usd, short_window=10, long_window=50):
        super().__init__(initial_usd, initial_btc_usd)
        self.short_window = short_window
        self.long_window = long_window
        self.prices = []

    def make_decision(self, price, date):
        self.prices.append(price)
        if len(self.prices) > self.long_window:
            short_ma = sum(self.prices[-self.short_window:]) / self.short_window
            long_ma = sum(self.prices[-self.long_window:]) / self.long_window
            if short_ma > long_ma:
                return 'buy'
            elif short_ma < long_ma:
                return 'sell'
        return 'hold'

class RSIStrategy(TradingStrategy):
    def __init__(self, initial_usd, initial_btc_usd, window=14, oversold=30, overbought=70):
        super().__init__(initial_usd, initial_btc_usd)
        self.window = window
        self.oversold = oversold
        self.overbought = overbought
        self.prices = []

    def make_decision(self, price, date):
        self.prices.append(price)
        if len(self.prices) > self.window:
            gains = []
            losses = []
            for i in range(1, self.window + 1):
                change = self.prices[-i] - self.prices[-i-1]
                if change >= 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(-change)
            avg_gain = sum(gains) / self.window
            avg_loss = sum(losses) / self.window
            rs = avg_gain / avg_loss if avg_loss != 0 else 0
            rsi = 100 - (100 / (1 + rs))
            if rsi < self.oversold:
                return 'buy'
            elif rsi > self.overbought:
                return 'sell'
        return 'hold'

# You can add more strategy classes here