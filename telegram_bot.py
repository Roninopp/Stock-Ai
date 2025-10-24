"""
Telegram Bot Module
Handles all Telegram interactions and sends trading signals
"""

import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode
from datetime import datetime
import traceback

from signal_scanner import SignalScanner
from data_fetcher import DataFetcher
from logs import logger, performance_tracker
import config

class TradingBot:
    def __init__(self):
        """Initialize the trading bot"""
        self.scanner = SignalScanner()
        self.data_fetcher = DataFetcher()
        self.is_running = False
        self.application = None
        self.chat_id = config.TELEGRAM_CHAT_ID
        
        logger.info("Trading Bot initialized")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🤖 *Welcome to Nifty 50 Trading Bot!*

This bot scans Nifty 50 stocks for high-probability trading opportunities using:
✅ Reversal candlestick patterns
✅ ICT concepts (Order Blocks, Liquidity Grabs, Break & Retest)
✅ Technical indicators (RSI, Volume)
✅ Support/Resistance levels

*Commands:*
/autotrade on - Start auto-trading signals
/autotrade off - Stop auto-trading signals
/status - Check bot status
/logs - View recent logs
/scan - Manual scan (one-time)
/help - Show this help message

*Ready to find profitable setups!* 🚀
        """
        await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)
        logger.info(f"Bot started by user: {update.effective_user.id}")
    
    async def autotrade_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /autotrade on/off command"""
        if not context.args:
            await update.message.reply_text(
                "Usage: /autotrade on OR /autotrade off"
            )
            return
        
        command = context.args[0].lower()
        
        if command == 'on':
            if self.is_running:
                await update.message.reply_text("✅ Auto-trading is already running!")
            else:
                self.is_running = True
                await update.message.reply_text(
                    "✅ *Auto-trading STARTED!*\n\n"
                    "🔍 Scanning Nifty 50 stocks every minute...\n"
                    "📊 You'll receive signals when opportunities are found.\n"
                    "⚡ Lightning fast detection enabled!",
                    parse_mode=ParseMode.MARKDOWN
                )
                logger.info("Auto-trading started")
                
                # Start the scanning loop
                asyncio.create_task(self.trading_loop())
                
        elif command == 'off':
            if not self.is_running:
                await update.message.reply_text("⚠️ Auto-trading is already stopped!")
            else:
                self.is_running = False
                await update.message.reply_text(
                    "🛑 *Auto-trading STOPPED!*\n\n"
                    "Bot has been paused. Use /autotrade on to restart.",
                    parse_mode=ParseMode.MARKDOWN
                )
                logger.info("Auto-trading stopped")
        else:
            await update.message.reply_text(
                "❌ Invalid command. Use: /autotrade on OR /autotrade off"
            )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        stats = performance_tracker.get_stats()
        market_status, market_msg = self.data_fetcher.get_market_status()
        
        status_emoji = "🟢" if self.is_running else "🔴"
        market_emoji = "🟢" if market_status else "🔴"
        
        status_message = f"""
📊 *BOT STATUS*

{status_emoji} Auto-trading: {'RUNNING' if self.is_running else 'STOPPED'}
{market_emoji} Market: {market_msg}

📈 *Performance Stats:*
• Scans completed: {stats['scans_completed']}
• Signals sent: {stats['total_signals']}
• Avg scan time: {stats['avg_scan_time']:.2f}s
• API calls: {stats['total_api_calls']}
• Errors: {stats['total_errors']}

⏰ Current time: {datetime.now().strftime('%H:%M:%S')}
📅 Date: {datetime.now().strftime('%d %b %Y')}
        """
        
        await update.message.reply_text(status_message, parse_mode=ParseMode.MARKDOWN)
    
    async def logs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /logs command"""
        recent_logs = logger.get_recent_logs(count=15)
        
        if not recent_logs:
            await update.message.reply_text("📝 No logs available yet.")
            return
        
        logs_message = "📝 *Recent Logs:*\n\n" + "\n".join(recent_logs[-15:])
        
        # Split message if too long
        if len(logs_message) > 4000:
            logs_message = logs_message[-4000:]
        
        await update.message.reply_text(logs_message, parse_mode=ParseMode.MARKDOWN)
    
    async def scan_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /scan command - manual one-time scan"""
        await update.message.reply_text("🔍 Starting manual scan of all Nifty 50 stocks...")
        
        signals = self.scanner.scan_all_stocks()
        
        if signals:
            await update.message.reply_text(f"✅ Found {len(signals)} trading opportunities!")
            for signal in signals:
                await self.send_signal(signal)
        else:
            await update.message.reply_text(
                "❌ No trading opportunities found in this scan.\n"
                "Market conditions may not be favorable right now."
            )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
📚 *HELP & COMMANDS*

*Main Commands:*
/start - Initialize bot
/autotrade on - Start continuous scanning
/autotrade off - Stop scanning (saves VPS RAM)
/status - View bot status and stats
/logs - View recent activity logs
/scan - Run one-time manual scan
/help - Show this help

*How it works:*
1️⃣ Bot scans all Nifty 50 stocks every minute
2️⃣ Detects reversal patterns at key S/R levels
3️⃣ Confirms with ICT concepts (Order Blocks, etc.)
4️⃣ Validates with RSI and Volume
5️⃣ Sends you high-probability signals with charts

*Signal Quality:*
✅ Every signal has multiple confirmations
✅ Clear entry, stop-loss, and targets
✅ Visual chart with marked levels
✅ Risk:Reward ratio calculated

*Tips:*
• Keep auto-trading ON during market hours
• Turn OFF when market closed to save resources
• Check /logs if you notice any issues

Happy Trading! 📈
        """
        await update.message.reply_text(help_message, parse_mode=ParseMode.MARKDOWN)
    
    async def send_signal(self, signal):
        """
        Send a trading signal to Telegram
        """
        try:
            # Format signal message
            signal_emoji = "🟢" if signal['signal_type'] == 'BUY' else "🔴"
            
            message = f"""
{signal_emoji} *{signal['signal_type']} SIGNAL - {signal['symbol']}*

📊 *Pattern:* {signal['pattern_name']} ({signal['pattern_strength']})
🎯 *S/R Context:* Price at {signal['sr_type'].title()} (₹{signal['sr_level']})

💰 *Entry:* ₹{signal['entry_price']}
🛑 *Stop Loss:* ₹{signal['stop_loss']} (-{abs(signal['entry_price'] - signal['stop_loss']):.2f})
🎯 *Target 1:* ₹{signal['target_1']} (+{abs(signal['target_1'] - signal['entry_price']):.2f})
🎯 *Target 2:* ₹{signal['target_2']} (+{abs(signal['target_2'] - signal['entry_price']):.2f})

📈 *Risk:Reward:* 1:{signal['risk_reward']}

✅ *Confirmations:*
• {', '.join(signal['confirmations'])}

🎯 *ICT Concepts:*
• {', '.join(signal['ict_confirmations'])} (Score: {signal['ict_score']}/3)

⏰ *Time:* {signal['timestamp'].strftime('%I:%M %p')}
            """
            
            # Generate and send chart
            chart_path = self.scanner.generate_signal_chart(signal)
            
            if chart_path:
                with open(chart_path, 'rb') as chart_file:
                    await self.application.bot.send_photo(
                        chat_id=self.chat_id,
                        photo=chart_file,
                        caption=message,
                        parse_mode=ParseMode.MARKDOWN
                    )
            else:
                # Send text only if chart generation failed
                await self.application.bot.send_message(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode=ParseMode.MARKDOWN
                )
            
            logger.info(f"Signal sent for {signal['symbol']}")
            
        except Exception as e:
            logger.error(f"Error sending signal: {str(e)}")
            logger.error(traceback.format_exc())
    
    async def trading_loop(self):
        """
        Main trading loop - runs continuously while auto-trading is on
        """
        logger.info("Trading loop started")
        
        while self.is_running:
            try:
                # Check if market is open
                market_open, market_msg = self.data_fetcher.get_market_status()
                
                if not market_open:
                    logger.info(f"Market closed: {market_msg}")
                    await asyncio.sleep(300)  # Check again in 5 minutes
                    continue
                
                # Scan all stocks
                signals = self.scanner.scan_all_stocks()
                
                # Send signals
                if signals:
                    for signal in signals:
                        await self.send_signal(signal)
                        await asyncio.sleep(2)  # Small delay between signals
                
                # Wait for next scan
                await asyncio.sleep(config.SCAN_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in trading loop: {str(e)}")
                logger.error(traceback.format_exc())
                await asyncio.sleep(60)  # Wait a bit before retrying
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        logger.error(traceback.format_exc())
    
    def run(self):
        """
        Start the Telegram bot
        """
        logger.info("Starting Telegram bot...")
        
        # Create application
        self.application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
        
        # Add command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("autotrade", self.autotrade_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("logs", self.logs_command))
        self.application.add_handler(CommandHandler("scan", self.scan_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Add error handler
        self.application.add_error_handler(self.error_handler)
        
        logger.info("Bot is ready! Waiting for commands...")
        
        # Start the bot
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = TradingBot()
    bot.run()
