import logging
from config import config
from crypto_data_fetcher import CryptoDataFetcher
from trading_logic import TradingLogic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoTradingBot:
    def __init__(self):
        self.crypto_data_fetcher = CryptoDataFetcher()
        self.trading_logic = TradingLogic()

    def run(self):
        logger.info("Starting Crypto Trading Bot")
        try:
            # Fetch historical data
            historical_data = self.crypto_data_fetcher.get_historical_data(
                coin_id=config.COIN_ID,
                vs_currency=config.VS_CURRENCY,
                days=config.HISTORICAL_DAYS
            )
            
            logger.info(f"Fetched {len(historical_data)} days of historical data")

            # Simulate trading based on historical data
            for data_point in historical_data:
                date = data_point['date']
                price = data_point['price']
                
                # Make trading decision
                decision = self.trading_logic.make_decision(price)
                
                # Execute trade (simulated)
                self.trading_logic.execute_trade(decision, price)
                
                logger.info(f"Date: {date}, Price: {price}, Decision: {decision}")

            logger.info("Historical data simulation completed")

        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    bot = CryptoTradingBot()
    bot.run()