# AMGA Telegram Bot

A production-ready Telegram bot that integrates with DeepSeek API to provide AI-powered responses.

## Features

- 🤖 AI-powered responses using DeepSeek API
- 💬 Handles all text messages (not just commands)
- 🔒 Secure API key management using environment variables
- ⚡ Asynchronous and non-blocking operations
- 🛡️ Robust error handling and logging
- 🚀 Easy deployment with screen sessions

## Prerequisites

- Python 3.8 or higher
- Telegram Bot Token from [BotFather](https://t.me/botfather)
- DeepSeek API Key from [DeepSeek](https://platform.deepseek.com/)

## Quick Start

### 1. Clone and Setup

```bash
git clone <your-repository-url>
cd amga-bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit the `.env` file with your actual API keys:

```env
TELEGRAM_BOT_TOKEN=7865472613:''
DEEPSEEK_API_KEY=''
```

### 4. Run the Bot

```bash
python bot.py
```

## Linux Server Deployment with Screen

For production deployment on a Linux server, use `screen` to keep the bot running:

### 1. Create a Screen Session

```bash
screen -S telegram-bot
```

### 2. Run the Bot

```bash
python bot.py
```

### 3. Detach from Screen

Press `Ctrl+A` then `D` to detach from the screen session. The bot will continue running.

### 4. Reattach to Screen

To check on the bot or stop it:

```bash
screen -r telegram-bot
```

### 5. Stop the Bot

While attached to the screen session, press `Ctrl+C` to stop the bot gracefully.

## Bot Commands

- `/start` - Welcome message and bot introduction
- `/help` - Show available commands and usage
- Any text message - Get AI response from DeepSeek

## Configuration Options

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot API token | Required |
| `DEEPSEEK_API_KEY` | DeepSeek API key | Required |
| `DEEPSEEK_BASE_URL` | DeepSeek API base URL | `https://api.deepseek.com/v1` |
| `DEEPSEEK_MODEL` | DeepSeek model to use | `deepseek-chat` |

## Security Notes

- 🔐 API keys are stored in `.env` file which is gitignored
- 🚫 Never commit your `.env` file to version control
- 🔒 Use the provided `.env.example` as a template

## Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check if API keys are correctly set in `.env`
   - Verify internet connectivity
   - Check DeepSeek API status

2. **Import errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version (requires 3.8+)

3. **Screen session issues**
   - List all screen sessions: `screen -ls`
   - Kill a stuck session: `screen -X -S session_name quit`

### Logs

The bot outputs logs to the console with timestamps and error details. Check these logs for debugging.

## Development

The bot uses:
- `python-telegram-bot` for Telegram integration
- `httpx` for async HTTP requests to DeepSeek API
- `python-dotenv` for environment variable management

## License

MIT License - feel free to use and modify as needed.
