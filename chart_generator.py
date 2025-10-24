"""
Chart Generator Module
Creates beautiful charts with marked support/resistance and patterns
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc
import pandas as pd
import numpy as np
from datetime import datetime
from logs import logger, log_exceptions
import config
from pathlib import Path

class ChartGenerator:
    def __init__(self):
        """Initialize chart generator"""
        # Create charts directory
        self.chart_path = Path(config.CHART_SAVE_PATH)
        self.chart_path.mkdir(parents=True, exist_ok=True)
        
        # Chart styling
        plt.style.use('dark_background')
        self.colors = {
            'bullish': '#26a69a',
            'bearish': '#ef5350',
            'support': '#4CAF50',
            'resistance': '#F44336',
            'order_block': '#FFC107',
            'signal': '#00BCD4'
        }
    
    @log_exceptions
    def generate_signal_chart(self, df, stock_symbol, signal_data):
        """
        Generate a chart with all markings for a signal
        
        signal_data should contain:
        - signal_type: 'BUY' or 'SELL'
        - entry_price
        - stop_loss
        - target
        - support_levels
        - resistance_levels
        - pattern_name
        - ict_data (optional)
        """
        try:
            # Create figure
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), 
                                           gridspec_kw={'height_ratios': [3, 1]})
            
            # Prepare data for candlestick
            df_plot = df.tail(60).copy()  # Last 60 candles
            df_plot['Date_num'] = mdates.date2num(df_plot.index if isinstance(df_plot.index, pd.DatetimeIndex) 
                                                  else pd.to_datetime(df_plot['Datetime']))
            
            ohlc = df_plot[['Date_num', 'Open', 'High', 'Low', 'Close']].values
            
            # Plot candlesticks
            candlestick_ohlc(ax1, ohlc, width=0.0008, 
                           colorup=self.colors['bullish'], 
                           colordown=self.colors['bearish'],
                           alpha=0.8)
            
            # Plot support levels
            if signal_data.get('support_levels'):
                for level in signal_data['support_levels']:
                    ax1.axhline(y=level, color=self.colors['support'], 
                              linestyle='--', linewidth=1.5, alpha=0.7, 
                              label='Support' if level == signal_data['support_levels'][0] else '')
            
            # Plot resistance levels
            if signal_data.get('resistance_levels'):
                for level in signal_data['resistance_levels']:
                    ax1.axhline(y=level, color=self.colors['resistance'], 
                              linestyle='--', linewidth=1.5, alpha=0.7,
                              label='Resistance' if level == signal_data['resistance_levels'][0] else '')
            
            # Plot entry, stop loss, and target
            entry = signal_data.get('entry_price')
            stop_loss = signal_data.get('stop_loss')
            target = signal_data.get('target')
            
            if entry:
                ax1.axhline(y=entry, color=self.colors['signal'], 
                          linestyle='-', linewidth=2, label='Entry')
            
            if stop_loss:
                ax1.axhline(y=stop_loss, color='red', 
                          linestyle='-.', linewidth=2, label='Stop Loss')
            
            if target:
                ax1.axhline(y=target, color='lime', 
                          linestyle='-.', linewidth=2, label='Target')
            
            # Plot order blocks if available
            if signal_data.get('ict_data', {}).get('order_blocks'):
                for ob in signal_data['ict_data']['order_blocks']:
                    if ob['type'] == signal_data['signal_type']:
                        ax1.axhspan(ob['low'], ob['high'], 
                                  color=self.colors['order_block'], 
                                  alpha=0.2, label='Order Block')
                        break
            
            # Highlight the signal candle
            signal_candle_idx = -1
            signal_date = df_plot['Date_num'].iloc[signal_candle_idx]
            signal_high = df_plot['High'].iloc[signal_candle_idx]
            
            marker = '^' if signal_data['signal_type'] == 'BUY' else 'v'
            marker_color = 'lime' if signal_data['signal_type'] == 'BUY' else 'red'
            y_pos = df_plot['Low'].iloc[signal_candle_idx] * 0.998 if signal_data['signal_type'] == 'BUY' else df_plot['High'].iloc[signal_candle_idx] * 1.002
            
            ax1.scatter(signal_date, y_pos, marker=marker, 
                       s=200, color=marker_color, zorder=5, 
                       edgecolors='white', linewidths=2)
            
            # Format x-axis
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax1.xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            # Titles and labels
            signal_emoji = '🟢' if signal_data['signal_type'] == 'BUY' else '🔴'
            ax1.set_title(f"{signal_emoji} {signal_data['signal_type']} SIGNAL - {stock_symbol}\n"
                         f"Pattern: {signal_data.get('pattern_name', 'N/A')} | "
                         f"Entry: ₹{entry:.2f} | SL: ₹{stop_loss:.2f} | TP: ₹{target:.2f}",
                         fontsize=14, fontweight='bold', pad=20)
            
            ax1.set_ylabel('Price (₹)', fontsize=11)
            ax1.legend(loc='upper left', fontsize=9)
            ax1.grid(True, alpha=0.3)
            
            # Volume subplot
            colors_volume = [self.colors['bullish'] if df_plot['Close'].iloc[i] >= df_plot['Open'].iloc[i] 
                           else self.colors['bearish'] for i in range(len(df_plot))]
            
            ax2.bar(df_plot['Date_num'], df_plot['Volume'], 
                   color=colors_volume, alpha=0.6, width=0.0008)
            
            ax2.set_ylabel('Volume', fontsize=11)
            ax2.set_xlabel('Time', fontsize=11)
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax2.xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
            ax2.grid(True, alpha=0.3)
            
            # Tight layout
            plt.tight_layout()
            
            # Save chart
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{stock_symbol}_{signal_data['signal_type']}_{timestamp}.png"
            filepath = self.chart_path / filename
            
            plt.savefig(filepath, dpi=100, bbox_inches='tight', 
                       facecolor='#1e1e1e', edgecolor='none')
            plt.close(fig)
            
            logger.debug(f"Chart saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error generating chart: {str(e)}", exc_info=True)
            plt.close('all')
            return None
    
    def cleanup_old_charts(self, days=1):
        """
        Delete charts older than specified days
        """
        try:
            cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
            
            deleted = 0
            for chart_file in self.chart_path.glob('*.png'):
                if chart_file.stat().st_mtime < cutoff_time:
                    chart_file.unlink()
                    deleted += 1
            
            if deleted > 0:
                logger.info(f"Cleaned up {deleted} old charts")
                
        except Exception as e:
            logger.error(f"Error cleaning up charts: {str(e)}")
