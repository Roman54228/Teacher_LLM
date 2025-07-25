#!/usr/bin/env python3
"""
Startup script for Interview Prep Telegram Bot
This script can be used to run both the web app and telegram bot
"""

import os
import sys
import threading
import time
from telegram_app import app
from telegram_bot import main as run_telegram_bot

def run_web_app():
    """Run the Flask web application"""
    print("Starting Telegram Mini App web server...")
    app.run(host='0.0.0.0', port=5000, debug=False)

def run_bot():
    """Run the Telegram bot"""
    print("Starting Telegram bot...")
    # Wait a bit for web app to start
    time.sleep(2)
    
    # Check if bot token is available
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("⚠️  TELEGRAM_BOT_TOKEN not found. Bot will not start.")
        print("To enable Telegram bot:")
        print("1. Create a bot with @BotFather")
        print("2. Set TELEGRAM_BOT_TOKEN environment variable")
        print("3. Set WEB_APP_URL to your Replit domain")
        return
    
    run_telegram_bot()

def main():
    """Main function to start both services"""
    print("🎯 Interview Prep - Telegram Mini App")
    print("=====================================")
    
    # Check environment variables
    required_vars = ['YANDEX_API_KEY', 'YANDEX_FOLDER_ID']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("AI explanations will not work without these variables.")
    
    # Start web app in main thread
    run_web_app()

if __name__ == '__main__':
    main()