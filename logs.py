import logging
import sys
from datetime import datetime
from pathlib import Path
import traceback
from functools import wraps
import config

class TradingBotLogger:
    def __init__(self, log_file=config.LOG_FILE, log_level=config.LOG_LEVEL):
        """Initialize the logger with file and console handlers"""
        
        # Create logs directory if it doesn't exist
        log_path = Path(log_file).parent
        log_path.mkdir(parents=True, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger('TradingBot')
        self.logger.setLevel(getattr(logging, log_level))
        
        # Clear existing handlers
        self.logger.handlers = []
        
        # File handler with detailed formatting
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Console handler with simpler formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Log storage for /logs command
        self.recent_logs = []
        self.max_recent_logs = 50
        
    def info(self, message):
        """Log info message"""
        self.logger.info(message)
        self._add_to_recent(f"INFO: {message}")
        
    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)
        self._add_to_recent(f"⚠️ WARNING: {message}")
        
    def error(self, message, exc_info=False):
        """Log error message"""
        self.logger.error(message, exc_info=exc_info)
        self._add_to_recent(f"❌ ERROR: {message}")
        
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)
        
    def critical(self, message):
        """Log critical message"""
        self.logger.critical(message)
        self._add_to_recent(f"🚨 CRITICAL: {message}")
        
    def _add_to_recent(self, message):
        """Add message to recent logs for /logs command"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.recent_logs.append(f"[{timestamp}] {message}")
        if len(self.recent_logs) > self.max_recent_logs:
            self.recent_logs.pop(0)
    
    def get_recent_logs(self, count=20):
        """Get recent logs for Telegram /logs command"""
        return self.recent_logs[-count:]
    
    def log_signal(self, stock, signal_type, pattern, entry, sl, tp, reason):
        """Log trading signal"""
        message = f"📊 SIGNAL: {signal_type} {stock} | Pattern: {pattern} | Entry: {entry} | SL: {sl} | TP: {tp}"
        self.info(message)
        
    def log_scan_start(self, stock_count):
        """Log scan start"""
        self.info(f"🔍 Starting scan of {stock_count} stocks...")
        
    def log_scan_complete(self, duration, signals_found):
        """Log scan completion"""
        self.info(f"✅ Scan complete in {duration:.2f}s | Signals found: {signals_found}")
        
    def log_error_with_trace(self, error, context=""):
        """Log error with full traceback"""
        error_msg = f"{context}: {str(error)}\n{traceback.format_exc()}"
        self.error(error_msg)

def log_exceptions(func):
    """Decorator to log exceptions in functions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.log_error_with_trace(e, f"Exception in {func.__name__}")
            raise
    return wrapper

# Global logger instance
logger = TradingBotLogger()

# Performance tracking
class PerformanceTracker:
    def __init__(self):
        self.scan_times = []
        self.api_calls = 0
        self.signals_sent = 0
        self.errors = 0
        
    # THIS IS THE FIXED LINE:
    def record_scan_time(self, duration):
        self.scan_times.append(duration)
        if len(self.scan_times) > 100:
            self.scan_times.pop(0)
    
    def get_avg_scan_time(self):
        if not self.scan_times:
            return 0
        return sum(self.scan_times) / len(self.scan_times)
    
    def increment_api_calls(self):
        self.api_calls += 1
    
    def increment_signals(self):
        self.signals_sent += 1
    
    def increment_errors(self):
        self.errors += 1
    
    def get_stats(self):
        return {
            "avg_scan_time": self.get_avg_scan_time(),
            "total_api_calls": self.api_calls,
            "total_signals": self.signals_sent,
            "total_errors": self.errors,
            "scans_completed": len(self.scan_times)
        }

performance_tracker = PerformanceTracker()

# THIS IS THE OTHER FIX:
# The "ENDOFFILE" line that was here has been removed.
