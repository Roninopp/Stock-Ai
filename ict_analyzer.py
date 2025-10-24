"""
ICT (Inner Circle Trader) Concepts Module
Implements Order Blocks, Liquidity Grabs, Break & Retest
"""

import pandas as pd
import numpy as np
from logs import logger, log_exceptions

class ICTAnalyzer:
    def __init__(self):
        """Initialize ICT analyzer"""
        pass
    
    @log_exceptions
    def analyze(self, df):
        """
        Analyze chart for ICT concepts
        Returns: dict with detected ICT setups
        """
        ict_signals = {
            'order_blocks': [],
            'liquidity_grabs': [],
            'break_retest': []
        }
        
        if len(df) < 20:
            return ict_signals
        
        # Detect Order Blocks
        order_blocks = self._detect_order_blocks(df)
        ict_signals['order_blocks'] = order_blocks
        
        # Detect Liquidity Grabs (stop hunts)
        liquidity_grabs = self._detect_liquidity_grabs(df)
        ict_signals['liquidity_grabs'] = liquidity_grabs
        
        # Detect Break and Retest
        break_retest = self._detect_break_and_retest(df)
        ict_signals['break_retest'] = break_retest
        
        return ict_signals
    
    def _detect_order_blocks(self, df):
        """
        Detect Order Blocks (OB)
        OB = Last bearish/bullish candle before strong impulse move
        """
        order_blocks = []
        
        # Look for bullish order blocks (last down candle before strong up move)
        for i in range(10, len(df) - 5):
            current = df.iloc[i]
            next_candles = df.iloc[i+1:i+6]
            
            # Current candle is bearish
            is_bearish = current['Close'] < current['Open']
            
            if is_bearish:
                # Check if followed by strong bullish move (3+ bullish candles)
                bullish_count = sum(next_candles['Close'] > next_candles['Open'])
                strong_move = bullish_count >= 3
                
                # Check if price moved significantly up
                price_move = (next_candles['Close'].max() - current['Close']) / current['Close']
                significant_move = price_move > 0.02  # 2% move
                
                if strong_move and significant_move:
                    # Check if current price is near this order block
                    current_price = df.iloc[-1]['Close']
                    ob_high = current['High']
                    ob_low = current['Low']
                    
                    # Price near order block (within 1%)
                    near_ob = (current_price >= ob_low * 0.99 and 
                              current_price <= ob_high * 1.01)
                    
                    if near_ob:
                        order_blocks.append({
                            'type': 'BULLISH',
                            'price': current['Close'],
                            'high': ob_high,
                            'low': ob_low,
                            'strength': 'Strong' if price_move > 0.03 else 'Medium'
                        })
        
        # Look for bearish order blocks (last up candle before strong down move)
        for i in range(10, len(df) - 5):
            current = df.iloc[i]
            next_candles = df.iloc[i+1:i+6]
            
            # Current candle is bullish
            is_bullish = current['Close'] > current['Open']
            
            if is_bullish:
                # Check if followed by strong bearish move (3+ bearish candles)
                bearish_count = sum(next_candles['Close'] < next_candles['Open'])
                strong_move = bearish_count >= 3
                
                # Check if price moved significantly down
                price_move = (current['Close'] - next_candles['Close'].min()) / current['Close']
                significant_move = price_move > 0.02  # 2% move
                
                if strong_move and significant_move:
                    # Check if current price is near this order block
                    current_price = df.iloc[-1]['Close']
                    ob_high = current['High']
                    ob_low = current['Low']
                    
                    # Price near order block (within 1%)
                    near_ob = (current_price >= ob_low * 0.99 and 
                              current_price <= ob_high * 1.01)
                    
                    if near_ob:
                        order_blocks.append({
                            'type': 'BEARISH',
                            'price': current['Close'],
                            'high': ob_high,
                            'low': ob_low,
                            'strength': 'Strong' if price_move > 0.03 else 'Medium'
                        })
        
        return order_blocks
    
    def _detect_liquidity_grabs(self, df):
        """
        Detect Liquidity Grabs (stop hunts)
        Price spikes above/below recent high/low then reverses quickly
        """
        liquidity_grabs = []
        
        if len(df) < 15:
            return liquidity_grabs
        
        # Get recent data
        recent = df.tail(15)
        
        # Find recent swing high (last 10 candles before current)
        lookback = df.tail(12).head(10)
        swing_high = lookback['High'].max()
        swing_low = lookback['Low'].min()
        
        # Check last 2 candles for liquidity grab
        last_candle = df.iloc[-1]
        prev_candle = df.iloc[-2]
        
        # Bullish liquidity grab (swept low then reversed up)
        if last_candle['Low'] < swing_low * 0.998:  # Went below swing low
            if last_candle['Close'] > last_candle['Open']:  # But closed bullish
                # Check if it's a strong reversal
                wick_size = last_candle['Close'] - last_candle['Low']
                body_size = abs(last_candle['Close'] - last_candle['Open'])
                
                if wick_size > body_size * 1.5:  # Long lower wick
                    liquidity_grabs.append({
                        'type': 'BULLISH',
                        'grabbed_level': swing_low,
                        'reversal_price': last_candle['Close'],
                        'strength': 'Strong'
                    })
        
        # Bearish liquidity grab (swept high then reversed down)
        if last_candle['High'] > swing_high * 1.002:  # Went above swing high
            if last_candle['Close'] < last_candle['Open']:  # But closed bearish
                # Check if it's a strong reversal
                wick_size = last_candle['High'] - last_candle['Close']
                body_size = abs(last_candle['Close'] - last_candle['Open'])
                
                if wick_size > body_size * 1.5:  # Long upper wick
                    liquidity_grabs.append({
                        'type': 'BEARISH',
                        'grabbed_level': swing_high,
                        'reversal_price': last_candle['Close'],
                        'strength': 'Strong'
                    })
        
        return liquidity_grabs
    
    def _detect_break_and_retest(self, df):
        """
        Detect Break and Retest of key levels
        Price breaks a level, pulls back to test it, then continues
        """
        break_retest = []
        
        if len(df) < 20:
            return break_retest
        
        # Identify key levels from last 15 candles
        lookback = df.tail(20).head(15)
        recent = df.tail(5)
        
        # Find potential support/resistance levels
        highs = lookback['High']
        lows = lookback['Low']
        
        # Cluster analysis for key levels (simplified)
        key_resistance = highs.nlargest(3).mean()
        key_support = lows.nsmallest(3).mean()
        
        current_price = df.iloc[-1]['Close']
        prev_prices = recent['Close'].values
        
        # Check for bullish break and retest
        # Price was below support, broke above, retested, now moving up
        if len(prev_prices) >= 4:
            # Was below key support
            was_below = prev_prices[-4] < key_support
            
            # Broke above
            broke_above = prev_prices[-3] > key_support * 1.005
            
            # Retested (came back close to level)
            retested = (prev_prices[-2] >= key_support * 0.995 and 
                       prev_prices[-2] <= key_support * 1.01)
            
            # Currently moving up
            moving_up = current_price > prev_prices[-2]
            
            if was_below and broke_above and retested and moving_up:
                break_retest.append({
                    'type': 'BULLISH',
                    'level': key_support,
                    'current_price': current_price,
                    'strength': 'Strong'
                })
        
        # Check for bearish break and retest
        if len(prev_prices) >= 4:
            # Was above key resistance
            was_above = prev_prices[-4] > key_resistance
            
            # Broke below
            broke_below = prev_prices[-3] < key_resistance * 0.995
            
            # Retested (came back close to level)
            retested = (prev_prices[-2] >= key_resistance * 0.99 and 
                       prev_prices[-2] <= key_resistance * 1.005)
            
            # Currently moving down
            moving_down = current_price < prev_prices[-2]
            
            if was_above and broke_below and retested and moving_down:
                break_retest.append({
                    'type': 'BEARISH',
                    'level': key_resistance,
                    'current_price': current_price,
                    'strength': 'Strong'
                })
        
        return break_retest
    
    def get_ict_score(self, ict_signals, signal_type):
        """
        Calculate ICT confirmation score
        Returns: score (0-3) based on number of ICT concepts detected
        """
        score = 0
        
        # Check order blocks
        for ob in ict_signals['order_blocks']:
            if ob['type'] == signal_type:
                score += 1
                break
        
        # Check liquidity grabs
        for lg in ict_signals['liquidity_grabs']:
            if lg['type'] == signal_type:
                score += 1
                break
        
        # Check break and retest
        for br in ict_signals['break_retest']:
            if br['type'] == signal_type:
                score += 1
                break
        
        return score
