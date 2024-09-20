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

class MACDStrategy(TradingStrategy):
    def __init__(self, initial_usd, initial_btc_usd, fast_period=12, slow_period=26, signal_period=9):
        super().__init__(initial_usd, initial_btc_usd)
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.prices = []
        self.macd = []
        self.signal_line = []

    def make_decision(self, price, date):
        self.prices.append(price)
        if len(self.prices) > self.slow_period:
            fast_ema = pd.Series(self.prices).ewm(span=self.fast_period, adjust=False).mean().iloc[-1]
            slow_ema = pd.Series(self.prices).ewm(span=self.slow_period, adjust=False).mean().iloc[-1]
            self.macd.append(fast_ema - slow_ema)
            if len(self.macd) > self.signal_period:
                self.signal_line.append(pd.Series(self.macd).ewm(span=self.signal_period, adjust=False).mean().iloc[-1])
                if self.macd[-1] > self.signal_line[-1] and self.macd[-2] <= self.signal_line[-2]:
                    return 'buy'
                elif self.macd[-1] < self.signal_line[-1] and self.macd[-2] >= self.signal_line[-2]:
                    return 'sell'
        return 'hold'

class BollingerBandsStrategy(TradingStrategy):
    def __init__(self, initial_usd, initial_btc_usd, window=20, num_std=2):
        super().__init__(initial_usd, initial_btc_usd)
        self.window = window
        self.num_std = num_std
        self.prices = []

    def make_decision(self, price, date):
        self.prices.append(price)
        if len(self.prices) >= self.window:
            rolling_mean = pd.Series(self.prices).rolling(window=self.window).mean().iloc[-1]
            rolling_std = pd.Series(self.prices).rolling(window=self.window).std().iloc[-1]
            upper_band = rolling_mean + (rolling_std * self.num_std)
            lower_band = rolling_mean - (rolling_std * self.num_std)
            if price < lower_band:
                return 'buy'
            elif price > upper_band:
                return 'sell'
        return 'hold'

class SentimentBasedStrategy(TradingStrategy):
    def __init__(self, initial_usd, initial_btc_usd):
        super().__init__(initial_usd, initial_btc_usd)
        self.sentiment_analyzer = SentimentAnalyzer()

    def make_decision(self, price, date):
        sentiment_index = self.sentiment_analyzer.get_fear_and_greed_index(date)
        if sentiment_index < 20:  # Extreme fear
            return 'buy'
        elif sentiment_index > 80:  # Extreme greed
            return 'sell'
        return 'hold'

# You can add more strategy classes here