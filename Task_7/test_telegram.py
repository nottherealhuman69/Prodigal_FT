#!/usr/bin/env python3

import asyncio
from telegram_bot import TelegramBot

async def test_telegram_connection():
    """Test Telegram bot connection"""
    print("🤖 Testing Telegram Bot Connection...")
    
    try:
        bot = TelegramBot()
        success = await bot.test_connection()
        
        if success:
            print("✅ Telegram bot is working correctly!")
            print("✅ Test message sent to the chat.")
        else:
            print("❌ Failed to send test message.")
            
    except Exception as e:
        print(f"❌ Error testing Telegram bot: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check if TELEGRAM_BOT_TOKEN is correct in .env")
        print("2. Check if TELEGRAM_CHAT_ID is correct in .env")
        print("3. Make sure the bot is added to the chat/group")
        print("4. Make sure the bot has permission to send messages")

if __name__ == "__main__":
    asyncio.run(test_telegram_connection())