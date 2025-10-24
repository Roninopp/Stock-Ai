"""
Setup Verification Script
Run this to test if everything is configured correctly
"""

import sys

def test_imports():
    """Test if all required packages are installed"""
    print("Testing imports...")
    
    required_packages = [
        ('yfinance', 'yfinance'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('telegram', 'python-telegram-bot'),
        ('matplotlib', 'matplotlib'),
    ]
    
    missing = []
    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
            print(f"  ✅ {package_name}")
        except ImportError:
            print(f"  ❌ {package_name} - MISSING")
            missing.append(package_name)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("\n✅ All packages installed!\n")
    return True

def test_config():
    """Test if config is properly set"""
    print("Testing configuration...")
    
    try:
        import config
        
        # Check Telegram token
        if config.TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
            print("  ❌ Telegram Bot Token - NOT CONFIGURED")
            print("     Edit config.py and add your bot token from @BotFather")
            return False
        else:
            print(f"  ✅ Telegram Bot Token - Configured")
        
        # Check chat ID
        if config.TELEGRAM_CHAT_ID == "YOUR_CHAT_ID_HERE":
            print("  ❌ Telegram Chat ID - NOT CONFIGURED")
            print("     Edit config.py and add your chat ID from @userinfobot")
            return False
        else:
            print(f"  ✅ Telegram Chat ID - Configured")
        
        # Check other settings
        print(f"  ✅ Scan Interval: {config.SCAN_INTERVAL}s")
        print(f"  ✅ Stocks to scan: {len(config.NIFTY_50_STOCKS)}")
        print(f"  ✅ Chart generation: {'Enabled' if config.ENABLE_CHART_GENERATION else 'Disabled'}")
        
        print("\n✅ Configuration looks good!\n")
        return True
        
    except Exception as e:
        print(f"  ❌ Error loading config: {str(e)}")
        return False

def test_data_fetch():
    """Test if we can fetch stock data"""
    print("Testing data fetching...")
    
    try:
        from data_fetcher import DataFetcher
        
        fetcher = DataFetcher()
        
        # Try fetching data for one stock
        print("  Fetching sample data for RELIANCE...")
        df = fetcher.fetch_stock_data("RELIANCE.NS", period="1d", interval="5m")
        
        if df is not None and len(df) > 0:
            print(f"  ✅ Data fetched successfully! ({len(df)} candles)")
        else:
            print("  ❌ No data received")
            return False
        
        print("\n✅ Data fetching works!\n")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return False

def test_modules():
    """Test if all modules can be imported"""
    print("Testing bot modules...")
    
    modules = [
        'config',
        'logs',
        'data_fetcher',
        'pattern_detector',
        'ict_analyzer',
        'indicators',
        'chart_generator',
        'signal_scanner',
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"  ✅ {module}.py")
        except Exception as e:
            print(f"  ❌ {module}.py - Error: {str(e)}")
            all_ok = False
    
    if all_ok:
        print("\n✅ All modules loaded successfully!\n")
    else:
        print("\n❌ Some modules failed to load\n")
    
    return all_ok

def main():
    """Run all tests"""
    print("\n" + "="*50)
    print("🤖 Trading Bot Setup Verification")
    print("="*50 + "\n")
    
    results = []
    
    # Run tests
    results.append(("Package Installation", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Module Loading", test_modules()))
    results.append(("Data Fetching", test_data_fetch()))
    
    # Summary
    print("\n" + "="*50)
    print("📊 SUMMARY")
    print("="*50)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n" + "="*50)
        print("🎉 ALL TESTS PASSED!")
        print("="*50)
        print("\nYour bot is ready to run!")
        print("\nStart the bot with: python telegram_bot.py")
        print("Then send /start to your bot on Telegram\n")
    else:
        print("\n" + "="*50)
        print("⚠️  SOME TESTS FAILED")
        print("="*50)
        print("\nPlease fix the issues above before running the bot.")
        print("Check QUICKSTART.md for help.\n")

if __name__ == "__main__":
    main()
