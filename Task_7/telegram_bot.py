import asyncio
from telegram import Bot
from telegram.error import TelegramError
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

class TelegramBot:
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.chat_id = TELEGRAM_CHAT_ID
    
    async def send_newsletter(self, newsletter_content: str):
        """Send newsletter to Telegram group"""
        try:
            # Split long messages if needed (Telegram has a 4096 character limit)
            if len(newsletter_content) > 4000:
                # Split into chunks
                chunks = [newsletter_content[i:i+4000] for i in range(0, len(newsletter_content), 4000)]
                
                for i, chunk in enumerate(chunks):
                    if i == 0:
                        await self.bot.send_message(
                            chat_id=self.chat_id,
                            text=chunk,
                            parse_mode='Markdown'
                        )
                    else:
                        await self.bot.send_message(
                            chat_id=self.chat_id,
                            text=f"*Continued...*\n\n{chunk}",
                            parse_mode='Markdown'
                        )
                    await asyncio.sleep(1)  # Small delay between messages
            else:
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=newsletter_content,
                    parse_mode='Markdown'
                )
            
            print("Newsletter sent successfully to Telegram!")
            return True
            
        except TelegramError as e:
            print(f"Telegram error: {e}")
            return False
        except Exception as e:
            print(f"Error sending newsletter: {e}")
            return False
    
    async def test_connection(self):
        """Test bot connection"""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text="🤖 Newsletter bot is active and ready!"
            )
            print("Test message sent successfully!")
            return True
        except Exception as e:
            print(f"Error testing connection: {e}")
            return False

def send_newsletter_sync(newsletter_content: str):
    """Synchronous wrapper for sending newsletter"""
    bot = TelegramBot()
    return asyncio.run(bot.send_newsletter(newsletter_content))