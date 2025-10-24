"""
Data Fetcher Module
Fetches real-time stock data from Yahoo Finance
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from logs import logger, log_exceptions, performance_tracker
import config
import time

class DataFetcher:
    def __init__(self):
        """Initialize data fetcher with caching"""
        self.cache = {}
        self.cache_duration = config.CACHE_DURATION
        self.last_fetch_time = {}
    
    @log_exceptions
    def fetch_stock_data(self, symbol, period='5d', interval='5m'):
        """
        Fetch stock data from Yahoo Finance
        Uses caching to reduce API calls
        """
        cache_key = f"{symbol}_{interval}"
        current_time = time.time()
        
        # Check if we have cached data that's still valid
        if cache_key in self.cache:
            if current_time - self.last_fetch_time.get(cache_key, 0) < self.cache_duration:
                logger.debug(f"Using cached data for {symbol}")
                return self.cache[cache_key]
        
        try:
            # Fetch data from Yahoo Finance
            logger.debug(f"Fetching fresh data for {symbol}")
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            performance_tracker.increment_api_calls()
            
            if df.empty:
                logger.warning(f"No data received for {symbol}")
                return None
            
            # Clean and prepare data
            df = self._prepare_data(df)
            
            # Cache the data
            self.cache[cache_key] = df
            self.last_fetch_time[cache_key] = current_time
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            performance_tracker.increment_errors()
            return None
    
    def _prepare_data(self, df):
        """
        Clean and prepare the dataframe
        """
        # Reset index to make Datetime a column
        df = df.reset_index()
        
        # Ensure we have the required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_columns:
            if col not in df.columns:
                logger.error(f"Missing required column: {col}")
                return None
        
        # Remove any rows with NaN values
        df = df.dropna(subset=required_columns)
        
        # Ensure data types
        for col in ['Open', 'High', 'Low', 'Close']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')
        
        return df
    
    @log_exceptions
    def fetch_current_price(self, symbol):
        """
        Fetch just the current price (faster than full history)
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d', interval='1m')
            
            if data.empty:
                return None
            
            current_price = data['Close'].iloc[-1]
            return float(current_price)
            
        except Exception as e:
            logger.error(f"Error fetching current price for {symbol}: {str(e)}")
            return None
    
    def clear_cache(self):
        """Clear the data cache"""
        self.cache = {}
        self.last_fetch_time = {}
        logger.info("Data cache cleared")
    
    @log_exceptions
    def get_stock_info(self, symbol):
        """
        Get basic stock information
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'currency': info.get('currency', 'INR')
            }
        except Exception as e:
            logger.error(f"Error fetching info for {symbol}: {str(e)}")
            return {
                'name': symbol,
                'sector': 'Unknown',
                'industry': 'Unknown',
                'currency': 'INR'
            }
    
    @log_exceptions
    def validate_symbol(self, symbol):
        """
        Validate if a stock symbol exists and has data
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d')
            return not data.empty
        except:
            return False
    
    def get_market_status(self):
        """
        Check if Indian market is open
        NSE trading hours: 9:15 AM - 3:30 PM IST
        """
        now = datetime.now()
        
        # Check if it's a weekday (Monday = 0, Sunday = 6)
        if now.weekday() >= 5:  # Saturday or Sunday
            return False, "Market closed - Weekend"
        
        # Check time (simplified - doesn't account for holidays)
        market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
        
        if now < market_open:
            return False, f"Market opens at 9:15 AM (in {(market_open - now).seconds // 60} minutes)"
        elif now > market_close:
            return False, "Market closed for the day"
        else:
            return True, "Market is open"
