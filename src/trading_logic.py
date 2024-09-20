import pandas as pd
import numpy as np
from .sentiment_analyzer import SentimentAnalyzer

class TradingLogic:
    def __init__(self, initial_usd=50, initial_btc_usd=50):
        self.usd_balance = initial_usd
        self.btc_amount = 0  # This will be set in the first execute_trade call
        self.initial_btc_usd = initial_btc_usd
        self.sentiment_analyzer = SentimentAnalyzer()
        self.trade_percentage = 0.2  # Trade 20% of available balance/BTC each time

    def make_decision(self, price, date):
        sentiment_index = self.sentiment_analyzer.get_fear_and_greed_index(date)
        sentiment = self.sentiment_analyzer.interpret_sentiment(sentiment_index)
        
        if sentiment == "Greed" and self.btc_amount > 0:
            return 'sell'  # Sell BTC to buy USD when greedy
        elif sentiment == "Fear" and self.usd_balance > 0:
            return 'buy'  # Buy BTC with USD when fearful
        else:
            return 'hold'

    def execute_trade(self, decision, price, date):
        if self.btc_amount == 0:  # First trade, initialize BTC amount
            self.btc_amount = self.initial_btc_usd / price

        if decision == 'sell' and self.btc_amount > 0:
            btc_to_sell = self.btc_amount * self.trade_percentage
            usd_gained = btc_to_sell * price
            self.btc_amount -= btc_to_sell
            self.usd_balance += usd_gained
        elif decision == 'buy' and self.usd_balance > 0:
            usd_to_spend = self.usd_balance * self.trade_percentage
            btc_bought = usd_to_spend / price
            self.usd_balance -= usd_to_spend
            self.btc_amount += btc_bought
        
        total_value_usd = (self.btc_amount * price) + self.usd_balance
        return total_value_usd