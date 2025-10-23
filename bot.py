#!/usr/bin/env python3
"""
DeepSeek Telegram Bot
A production-ready Telegram bot that integrates with DeepSeek API for AI responses.
"""

import os
import logging
import asyncio
import signal
import sys
from typing import Optional

import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')

# Validate required environment variables
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY environment variable is required")


class DeepSeekClient:
    """Client for interacting with DeepSeek API"""
    
    def __init__(self, api_key: str, base_url: str = DEEPSEEK_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    async def get_response(self, message: str) -> Optional[str]:
        """
        Get AI response from DeepSeek API
        
        Args:
            message: User's input message
            
        Returns:
            AI response text or None if error occurs
        """
        payload = {
            "model": DEEPSEEK_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful and professional AI assistant. Provide clear, concise, and accurate responses."
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            "stream": False,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            return data['choices'][0]['message']['content']
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error occurred: {e}")
            return None
        except KeyError as e:
            logger.error(f"Unexpected response format: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.acclose()


class TelegramBot:
    """Main Telegram bot class"""
    
    def __init__(self):
        self.deepseek_client = DeepSeekClient(DEEPSEEK_API_KEY)
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup message handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self._start_command))
        self.application.add_handler(CommandHandler("help", self._help_command))
        
        # Message handler for all text messages
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self._handle_message
        ))
    
    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = (
            "🤖 Welcome to AMGA AI Bot!\n\n"
            "I'm an AI assistant. "
            "Just send me a message and I'll help you with your questions.\n\n"
            "Use /help to see available commands."
        )
        await update.message.reply_text(welcome_message)
    
    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = (
            "📚 Available Commands:\n\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n\n"
            "💡 Just send me any message and I'll respond using DeepSeek AI!"
        )
        await update.message.reply_text(help_message)
    
    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming text messages"""
        user_message = update.message.text
        
        # Show typing indicator
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, 
            action="typing"
        )
        
        # Get AI response
        logger.info(f"Processing message from user {update.effective_user.id}: {user_message[:50]}...")
        ai_response = await self.deepseek_client.get_response(user_message)
        
        if ai_response:
            # Send the response (Telegram has a 4096 character limit per message)
            if len(ai_response) <= 4096:
                await update.message.reply_text(ai_response)
            else:
                # Split long messages
                for i in range(0, len(ai_response), 4096):
                    await update.message.reply_text(ai_response[i:i+4096])
        else:
            error_message = (
                "❌ Sorry, I encountered an error while processing your request. "
                "Please try again in a moment."
            )
            await update.message.reply_text(error_message)
    
    async def start(self):
        """Start the bot"""
        logger.info("Starting DeepSeek Telegram Bot...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        logger.info("Bot is now running and polling for messages")
    
    async def stop(self):
        """Stop the bot gracefully"""
        logger.info("Stopping bot...")
        await self.application.updater.stop()
        await self.application.stop()
        await self.application.shutdown()
        await self.deepseek_client.close()
        logger.info("Bot stopped gracefully")


# Global bot instance
bot_instance = None


async def main():
    """Main function to run the bot"""
    global bot_instance
    
    try:
        bot_instance = TelegramBot()
        await bot_instance.start()
        
        # Keep the bot running
        while True:
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
    finally:
        if bot_instance:
            await bot_instance.stop()


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    if bot_instance:
        asyncio.create_task(bot_instance.stop())
    sys.exit(0)


if __name__ == '__main__':
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        sys.exit(1)
