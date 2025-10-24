"""
Signal Scanner Module
Main trading signal detection engine
"""

import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import time

from data_fetcher import DataFetcher
from pattern_detector import PatternDetector
from ict_analyzer import ICTAnalyzer
from indicators import IndicatorAnalyzer
from chart_generator import ChartGenerator
from logs import logger, log_exceptions, performance_tracker
import config

class SignalScanner:
    def __init__(self):
        """Initialize the signal scanner with all modules"""
        self.data_fetcher = DataFetcher()
        self.pattern_detector = PatternDetector()
        self.ict_analyzer = ICTAnalyzer()
        self.indicator_analyzer = IndicatorAnalyzer()
        self.chart_generator = ChartGenerator()
        
        self.stocks = config.NIFTY_50_STOCKS
        self.scan_interval = config.SCAN_INTERVAL
        self.max_workers = config.MAX_WORKERS
        
        logger.info(f"Signal Scanner initialized with {len(self.stocks)} stocks")
    
    @log_exceptions
    def scan_stock(self, symbol):
        """
        Scan a single stock for trading opportunities
        Returns: signal dict if found, None otherwise
        """
        try:
            # Fetch data
            df = self.data_fetcher.fetch_stock_data(
                symbol, 
                period='5d', 
                interval=config.TIMEFRAME
            )
            
            if df is None or len(df) < 50:
                return None
            
            # Calculate support and resistance
            support_levels, resistance_levels = self.indicator_analyzer.calculate_support_resistance(df)
            
            # Check if price is near S/R
            current_price = df['Close'].iloc[-1]
            sr_type, sr_level, distance = self.indicator_analyzer.is_near_support_resistance(
                current_price, support_levels, resistance_levels
            )
            
            if sr_type is None:
                return None  # Not near any key level
            
            # Detect candlestick patterns
            patterns = self.pattern_detector.detect_patterns(df)
            
            if not patterns:
                return None  # No pattern detected
            
            # Analyze ICT concepts
            ict_signals = self.ict_analyzer.analyze(df)
            
            # Check each detected pattern
            for pattern in patterns:
                signal_type = pattern['type']
                
                # Validate signal direction matches S/R context
                if sr_type == 'support' and signal_type != 'BUY':
                    continue
                if sr_type == 'resistance' and signal_type != 'SELL':
                    continue
                
                # Get indicator confirmation
                indicator_conf = self.indicator_analyzer.get_confirmation(df, signal_type)
                
                # Check if we have at least 1 indicator confirmation
                if not (indicator_conf['rsi_confirmed'] or indicator_conf['volume_confirmed']):
                    continue
                
                # Calculate ICT score
                ict_score = self.ict_analyzer.get_ict_score(ict_signals, signal_type)
                
                # Require at least 1 ICT confirmation
                if ict_score < 1:
                    continue
                
                # Calculate entry, stop loss, and target
                entry_price = current_price
                
                if signal_type == 'BUY':
                    stop_loss = entry_price * (1 - config.STOP_LOSS_PERCENTAGE / 100)
                    target_1 = entry_price * (1 + config.TARGET_PERCENTAGE_1 / 100)
                    target_2 = entry_price * (1 + config.TARGET_PERCENTAGE_2 / 100)
                else:  # SELL
                    stop_loss = entry_price * (1 + config.STOP_LOSS_PERCENTAGE / 100)
                    target_1 = entry_price * (1 - config.TARGET_PERCENTAGE_1 / 100)
                    target_2 = entry_price * (1 - config.TARGET_PERCENTAGE_2 / 100)
                
                # Calculate risk:reward
                risk = abs(entry_price - stop_loss)
                reward = abs(target_1 - entry_price)
                rr_ratio = reward / risk if risk > 0 else 0
                
                # Check minimum RR ratio
                if rr_ratio < config.MIN_RISK_REWARD_RATIO:
                    continue
                
                # Build signal
                signal = {
                    'symbol': symbol.replace('.NS', ''),
                    'signal_type': signal_type,
                    'pattern_name': pattern['name'],
                    'pattern_strength': pattern['strength'],
                    'entry_price': round(entry_price, 2),
                    'stop_loss': round(stop_loss, 2),
                    'target_1': round(target_1, 2),
                    'target_2': round(target_2, 2),
                    'risk_reward': round(rr_ratio, 2),
                    'sr_type': sr_type,
                    'sr_level': round(sr_level, 2),
                    'rsi_value': indicator_conf['rsi_value'],
                    'volume_ratio': indicator_conf['volume_ratio'],
                    'ict_score': ict_score,
                    'ict_data': ict_signals,
                    'support_levels': [round(l, 2) for l in support_levels],
                    'resistance_levels': [round(l, 2) for l in resistance_levels],
                    'timestamp': datetime.now(),
                    'dataframe': df  # For chart generation
                }
                
                # Build confirmation reason
                confirmations = []
                if indicator_conf['rsi_confirmed']:
                    confirmations.append(f"RSI {indicator_conf['rsi_value']}")
                if indicator_conf['volume_confirmed']:
                    confirmations.append(f"Volume spike {indicator_conf['volume_ratio']}x")
                
                ict_confirmations = []
                if ict_signals['order_blocks']:
                    ict_confirmations.append("Order Block")
                if ict_signals['liquidity_grabs']:
                    ict_confirmations.append("Liquidity Grab")
                if ict_signals['break_retest']:
                    ict_confirmations.append("Break & Retest")
                
                signal['confirmations'] = confirmations
                signal['ict_confirmations'] = ict_confirmations
                
                logger.log_signal(
                    symbol, signal_type, pattern['name'],
                    entry_price, stop_loss, target_1,
                    f"S/R: {sr_type}, ICT: {ict_score}, Indicators: {len(confirmations)}"
                )
                
                return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error scanning {symbol}: {str(e)}")
            performance_tracker.increment_errors()
            return None
    
    @log_exceptions
    def scan_all_stocks(self):
        """
        Scan all stocks in parallel
        Returns: list of signals
        """
        start_time = time.time()
        signals = []
        
        logger.log_scan_start(len(self.stocks))
        
        # Parallel scanning
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_stock = {
                executor.submit(self.scan_stock, stock): stock 
                for stock in self.stocks
            }
            
            for future in as_completed(future_to_stock):
                stock = future_to_stock[future]
                try:
                    signal = future.result()
                    if signal:
                        signals.append(signal)
                        performance_tracker.increment_signals()
                except Exception as e:
                    logger.error(f"Exception scanning {stock}: {str(e)}")
        
        # Record scan time
        duration = time.time() - start_time
        performance_tracker.record_scan_time(duration)
        
        logger.log_scan_complete(duration, len(signals))
        
        return signals
    
    def generate_signal_chart(self, signal):
        """
        Generate chart for a signal
        """
        if not config.ENABLE_CHART_GENERATION:
            return None
        
        try:
            chart_path = self.chart_generator.generate_signal_chart(
                signal['dataframe'],
                signal['symbol'],
                signal
            )
            return chart_path
        except Exception as e:
            logger.error(f"Error generating chart for {signal['symbol']}: {str(e)}")
            return None
