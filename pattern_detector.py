import pandas as pd
import numpy as np
from logs import logger, log_exceptions

class PatternDetector:
    def __init__(self):
        """Initialize pattern detector"""
        self.patterns_detected = []
    
    @log_exceptions
    def detect_patterns(self, df):
        """
        Detect all reversal candlestick patterns
        Returns: list of detected patterns with details
        """
        patterns = []
        
        if len(df) < 5:
            return patterns
        
        # Get last few candles for pattern detection
        last_candles = df.tail(5)
        
        # Detect each pattern type
        if self._is_bullish_engulfing(last_candles):
            patterns.append({
                'name': 'Bullish Engulfing',
                'type': 'BUY',
                'strength': 'Strong',
                'candle_index': -1
            })
        
        if self._is_bearish_engulfing(last_candles):
            patterns.append({
                'name': 'Bearish Engulfing',
                'type': 'SELL',
                'strength': 'Strong',
                'candle_index': -1
            })
        
        if self._is_hammer(last_candles):
            patterns.append({
                'name': 'Hammer',
                'type': 'BUY',
                'strength': 'Medium',
                'candle_index': -1
            })
        
        if self._is_shooting_star(last_candles):
            patterns.append({
                'name': 'Shooting Star',
                'type': 'SELL',
                'strength': 'Medium',
                'candle_index': -1
            })
        
        if self._is_morning_star(last_candles):
            patterns.append({
                'name': 'Morning Star',
                'type': 'BUY',
                'strength': 'Very Strong',
                'candle_index': -1
            })
        
        if self._is_evening_star(last_candles):
            patterns.append({
                'name': 'Evening Star',
                'type': 'SELL',
                'strength': 'Very Strong',
                'candle_index': -1
            })
        
        if self._is_bullish_pin_bar(last_candles):
            patterns.append({
                'name': 'Bullish Pin Bar',
                'type': 'BUY',
                'strength': 'Strong',
                'candle_index': -1
            })
        
        if self._is_bearish_pin_bar(last_candles):
            patterns.append({
                'name': 'Bearish Pin Bar',
                'type': 'SELL',
                'strength': 'Strong',
                'candle_index': -1
            })
        
        return patterns
    
    def _is_bullish_engulfing(self, candles):
        """Detect bullish engulfing pattern"""
        if len(candles) < 2:
            return False
        
        prev = candles.iloc[-2]
        curr = candles.iloc[-1]
        
        prev_bearish = prev['Close'] < prev['Open']
        curr_bullish = curr['Close'] > curr['Open']
        engulfs = (curr['Open'] <= prev['Close'] and curr['Close'] >= prev['Open'])
        curr_body = abs(curr['Close'] - curr['Open'])
        curr_range = curr['High'] - curr['Low']
        strong_body = curr_body > (curr_range * 0.6)
        
        return prev_bearish and curr_bullish and engulfs and strong_body
    
    def _is_bearish_engulfing(self, candles):
        """Detect bearish engulfing pattern"""
        if len(candles) < 2:
            return False
        
        prev = candles.iloc[-2]
        curr = candles.iloc[-1]
        
        prev_bullish = prev['Close'] > prev['Open']
        curr_bearish = curr['Close'] < curr['Open']
        engulfs = (curr['Open'] >= prev['Close'] and curr['Close'] <= prev['Open'])
        curr_body = abs(curr['Close'] - curr['Open'])
        curr_range = curr['High'] - curr['Low']
        strong_body = curr_body > (curr_range * 0.6)
        
        return prev_bullish and curr_bearish and engulfs and strong_body
    
    def _is_hammer(self, candles):
        """Detect hammer pattern"""
        if len(candles) < 1:
            return False
        
        candle = candles.iloc[-1]
        body = abs(candle['Close'] - candle['Open'])
        high_shadow = candle['High'] - max(candle['Close'], candle['Open'])
        low_shadow = min(candle['Close'], candle['Open']) - candle['Low']
        
        small_body = body < (candle['High'] - candle['Low']) * 0.3
        long_lower_shadow = low_shadow > (body * 2)
        short_upper_shadow = high_shadow < body
        
        return small_body and long_lower_shadow and short_upper_shadow
    
    def _is_shooting_star(self, candles):
        """Detect shooting star pattern"""
        if len(candles) < 1:
            return False
        
        candle = candles.iloc[-1]
        body = abs(candle['Close'] - candle['Open'])
        high_shadow = candle['High'] - max(candle['Close'], candle['Open'])
        low_shadow = min(candle['Close'], candle['Open']) - candle['Low']
        
        small_body = body < (candle['High'] - candle['Low']) * 0.3
        long_upper_shadow = high_shadow > (body * 2)
        short_lower_shadow = low_shadow < body
        
        return small_body and long_upper_shadow and short_lower_shadow
    
    def _is_morning_star(self, candles):
        """Detect morning star pattern"""
        if len(candles) < 3:
            return False
        
        first = candles.iloc[-3]
        second = candles.iloc[-2]
        third = candles.iloc[-1]
        
        first_bearish = first['Close'] < first['Open']
        first_body = abs(first['Close'] - first['Open'])
        second_body = abs(second['Close'] - second['Open'])
        second_small = second_body < (first_body * 0.3)
        third_bullish = third['Close'] > third['Open']
        third_body = abs(third['Close'] - third['Open'])
        third_large = third_body > (first_body * 0.5)
        closes_high = third['Close'] > (first['Open'] + first['Close']) / 2
        
        return first_bearish and second_small and third_bullish and third_large and closes_high
    
    def _is_evening_star(self, candles):
        """Detect evening star pattern"""
        if len(candles) < 3:
            return False
        
        first = candles.iloc[-3]
        second = candles.iloc[-2]
        third = candles.iloc[-1]
        
        first_bullish = first['Close'] > first['Open']
        first_body = abs(first['Close'] - first['Open'])
        second_body = abs(second['Close'] - second['Open'])
        second_small = second_body < (first_body * 0.3)
        third_bearish = third['Close'] < third['Open']
        third_body = abs(third['Close'] - third['Open'])
        third_large = third_body > (first_body * 0.5)
        closes_low = third['Close'] < (first['Open'] + first['Close']) / 2
        
        return first_bullish and second_small and third_bearish and third_large and closes_low
    
    def _is_bullish_pin_bar(self, candles):
        """Detect bullish pin bar"""
        if len(candles) < 1:
            return False
        
        candle = candles.iloc[-1]
        total_range = candle['High'] - candle['Low']
        low_shadow = min(candle['Close'], candle['Open']) - candle['Low']
        high_shadow = candle['High'] - max(candle['Close'], candle['Open'])
        
        long_lower_wick = low_shadow > (total_range * 0.6)
        small_upper = high_shadow < (total_range * 0.2)
        bullish_close = candle['Close'] >= candle['Open']
        
        return long_lower_wick and small_upper and bullish_close
    
    def _is_bearish_pin_bar(self, candles):
        """Detect bearish pin bar"""
        if len(candles) < 1:
            return False
        
        candle = candles.iloc[-1]
        total_range = candle['High'] - candle['Low']
        low_shadow = min(candle['Close'], candle['Open']) - candle['Low']
        high_shadow = candle['High'] - max(candle['Close'], candle['Open'])
        
        long_upper_wick = high_shadow > (total_range * 0.6)
        small_lower = low_shadow < (total_range * 0.2)
        bearish_close = candle['Close'] <= candle['Open']
        
        return long_upper_wick and small_lower and bearish_close
ENDOFFILE
