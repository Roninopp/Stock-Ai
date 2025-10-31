"""
Configuration file for Nifty 50 Trading Bot
"""

import os

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "6506132532:AAGjfMXlSkefR5uldDwCRhxdk7YRES5385k")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "-1003103484269")

# --- NEW APPROVAL SETTINGS ---
# Get your ID from @userinfobot on Telegram
ADMIN_USER_ID = 6837532865  # <--- !!! IMPORTANT: REPLACE THIS WITH YOUR OWN TELEGRAM ID !!!
APPROVAL_FILE = "/home/admin01/Stock-Ai/approved_users.json"
# -----------------------------

# Trading Configuration
NIFTY_50_STOCKS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
    "ICICIBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS",
    "AXISBANK.NS", "LT.NS", "ASIANPAINT.NS", "MARUTI.NS", "HCLTECH.NS",
    "SUNPHARMA.NS", "BAJFINANCE.NS", "TITAN.NS", "ULTRACEMCO.NS", "NESTLEIND.NS",
    "WIPRO.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "TECHM.NS",
    "M&M.NS", "BAJAJFINSV.NS", "TATASTEEL.NS", "COALINDIA.NS", "ADANIPORTS.NS",
    "DIVISLAB.NS", "INDUSINDBK.NS", "DRREDDY.NS", "GRASIM.NS", "CIPLA.NS",
    "EICHERMOT.NS", "JSWSTEEL.NS", "HINDALCO.NS", "HEROMOTOCO.NS", "BRITANNIA.NS",
    "TATAMOTORS.NS", "APOLLOHOSP.NS", "SBILIFE.NS", "BPCL.NS", "UPL.NS",
    "BAJAJ-AUTO.NS", "TATACONSUM.NS", "ADANIENT.NS", "HDFCLIFE.NS", "LTIM.NS"
]

# Scanning Configuration
SCAN_INTERVAL = 60  # seconds (1 minute)
TIMEFRAME = "1"  # 5-minute candles
LOOKBACK_PERIODS = 100  # Number of candles to analyze

# Strategy Parameters
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
VOLUME_SPIKE_MULTIPLIER = 1.5  # Volume should be 1.5x average

# Support/Resistance Configuration
SR_LOOKBACK = 50  # Periods to look back for S/R levels
SR_TOUCH_THRESHOLD = 0.5  # % threshold for price near S/R

# Risk Management
MIN_RISK_REWARD_RATIO = 1.5  # Minimum 1:1.5 RR
STOP_LOSS_PERCENTAGE = 0.8  # 0.8% stop loss
TARGET_PERCENTAGE_1 = 1.2  # 1.2% first target
TARGET_PERCENTAGE_2 = 2.0  # 2.0% second target

# Chart Configuration
CHART_SAVE_PATH = "/home/admin01/charts/"
CHART_STYLE = "yahoo"  # Chart style

# Logging Configuration
LOG_FILE = "/home/admin01/trading_bot.log"
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

# Performance Settings
MAX_WORKERS = 10  # Number of parallel workers for scanning
ENABLE_CHART_GENERATION = True  # Set to False for faster performance

# Data Source
DATA_SOURCE = "yahoo"  # Using Yahoo Finance
CACHE_DURATION = 25  # Cache data for 5 minutes
