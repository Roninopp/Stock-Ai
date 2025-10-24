"""
Technical Indicators Module
RSI and Volume confirmation for signals
"""

import pandas as pd
import numpy as np
from logs import logger, log_exceptions
import config

class IndicatorAnalyzer:
    def __init__(self):
        """Initialize indicator analyzer"""
        self.rsi_period = config.RSI_PERIOD
        self.rsi_oversold = config.RSI_OVERSOLD
        self.rsi_overbought = config.RSI_OVERBOUGHT
        self.volume_multiplier = config.VOLUME_SPIKE_MULTIPLIER
    
    @log_exceptions
    def calculate_rsi(self, df, period=None):
        """
        Calculate RSI (Relative Strength Index)
        """
        if period is None:
            period = self.rsi_period
        
        if len(df) < period + 1:
            return pd.Series([50] * len(df), index=df.index)
        
        # Calculate price changes
        delta = df['Close'].diff()
        
        # Separate gains and losses
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # Calculate RS and RSI
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @log_exceptions
    def check_volume_confirmation(self, df):
        """
        Check if current volume is significantly higher than average
        Returns: bool, volume_ratio
        """
        if len(df) < 20:
            return False, 1.0
        
        # Calculate average volume (last 20 periods excluding current)
        avg_volume = df['Volume'].iloc[-21:-1].mean()
        
        # Current volume
        current_volume = df['Volume'].iloc[-1]
        
        # Calculate ratio
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        
        # Volume spike if current volume > multiplier * average
        has_spike = volume_ratio >= self.volume_multiplier
        
        return has_spike, volume_ratio
    
    @log_exceptions
    def get_confirmation(self, df, signal_type):
        """
        Get indicator confirmation for a signal
        Returns: dict with confirmation details
        """
        confirmation = {
            'rsi_confirmed': False,
            'volume_confirmed': False,
            'rsi_value': None,
            'volume_ratio': None,
            'strength': 'None'
        }
        
        if len(df) < 20:
            return confirmation
        
        # Calculate RSI
        rsi_values = self.calculate_rsi(df)
        current_rsi = rsi_values.iloc[-1]
        confirmation['rsi_value'] = round(current_rsi, 2)
        
        # Check RSI confirmation based on signal type
        if signal_type == 'BUY' or signal_type == 'BULLISH':
            # For buy signals, RSI should be oversold or moving up from oversold
            confirmation['rsi_confirmed'] = current_rsi < self.rsi_oversold + 10
            
        elif signal_type == 'SELL' or signal_type == 'BEARISH':
            # For sell signals, RSI should be overbought or moving down from overbought
            confirmation['rsi_confirmed'] = current_rsi > self.rsi_overbought - 10
        
        # Check volume confirmation
        volume_confirmed, volume_ratio = self.check_volume_confirmation(df)
        confirmation['volume_confirmed'] = volume_confirmed
        confirmation['volume_ratio'] = round(volume_ratio, 2)
        
        # Calculate overall strength
        confirmations = sum([
            confirmation['rsi_confirmed'],
            confirmation['volume_confirmed']
        ])
        
        if confirmations == 2:
            confirmation['strength'] = 'Strong'
        elif confirmations == 1:
            confirmation['strength'] = 'Medium'
        else:
            confirmation['strength'] = 'Weak'
        
        return confirmation
    
    @log_exceptions
    def calculate_support_resistance(self, df, lookback=None):
        """
        Calculate support and resistance levels
        Uses swing highs/lows clustering
        """
        if lookback is None:
            lookback = config.SR_LOOKBACK
        
        if len(df) < lookback:
            lookback = len(df)
        
        recent_data = df.tail(lookback)
        
        # Find swing highs and lows
        swing_highs = []
        swing_lows = []
        
        for i in range(2, len(recent_data) - 2):
            high = recent_data['High'].iloc[i]
            low = recent_data['Low'].iloc[i]
            
            # Check if it's a swing high
            if (high > recent_data['High'].iloc[i-1] and 
                high > recent_data['High'].iloc[i-2] and
                high > recent_data['High'].iloc[i+1] and 
                high > recent_data['High'].iloc[i+2]):
                swing_highs.append(high)
            
            # Check if it's a swing low
            if (low < recent_data['Low'].iloc[i-1] and 
                low < recent_data['Low'].iloc[i-2] and
                low < recent_data['Low'].iloc[i+1] and 
                low < recent_data['Low'].iloc[i+2]):
                swing_lows.append(low)
        
        # Cluster levels (group nearby levels together)
        resistance_levels = self._cluster_levels(swing_highs) if swing_highs else []
        support_levels = self._cluster_levels(swing_lows) if swing_lows else []
        
        return support_levels, resistance_levels
    
    def _cluster_levels(self, levels, threshold=0.005):
        """
        Cluster nearby price levels together
        threshold: percentage difference to consider levels as same
        """
        if not levels:
            return []
        
        levels = sorted(levels)
        clustered = []
        current_cluster = [levels[0]]
        
        for i in range(1, len(levels)):
            # Check if this level is close to the current cluster
            if abs(levels[i] - current_cluster[0]) / current_cluster[0] <= threshold:
                current_cluster.append(levels[i])
            else:
                # Save average of current cluster and start new one
                clustered.append(np.mean(current_cluster))
                current_cluster = [levels[i]]
        
        # Don't forget the last cluster
        clustered.append(np.mean(current_cluster))
        
        return clustered
    
    @log_exceptions
    def is_near_support_resistance(self, current_price, support_levels, resistance_levels):
        """
        Check if current price is near support or resistance
        Returns: ('support'/'resistance'/None, level, distance_percentage)
        """
        threshold = config.SR_TOUCH_THRESHOLD / 100  # Convert to decimal
        
        # Check resistance levels
        for level in resistance_levels:
            distance = abs(current_price - level) / level
            if distance <= threshold:
                return 'resistance', level, distance * 100
        
        # Check support levels
        for level in support_levels:
            distance = abs(current_price - level) / level
            if distance <= threshold:
                return 'support', level, distance * 100
        
        return None, None, None
