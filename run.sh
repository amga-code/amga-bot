#!/bin/bash

# DeepSeek Telegram Bot Startup Script
# Use this script to easily start the bot on Linux servers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_status "Python $PYTHON_VERSION detected"
}

# Check if virtual environment exists, create if not
setup_venv() {
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    print_status "Activating virtual environment..."
    source venv/bin/activate
}

# Install dependencies
install_deps() {
    print_status "Installing dependencies..."
    pip install -r requirements.txt
}

# Check if .env file exists
check_env() {
    if [ ! -f ".env" ]; then
        print_error ".env file not found!"
        print_warning "Please copy .env.example to .env and add your API keys:"
        echo "  cp .env.example .env"
        echo "  # Edit .env with your TELEGRAM_BOT_TOKEN and DEEPSEEK_API_KEY"
        exit 1
    fi
    
    # Validate that required environment variables are set
    if ! grep -q "TELEGRAM_BOT_TOKEN=" .env || ! grep -q "DEEPSEEK_API_KEY=" .env; then
        print_error "Required environment variables are not set in .env file"
        print_warning "Please set TELEGRAM_BOT_TOKEN and DEEPSEEK_API_KEY in .env"
        exit 1
    fi
    
    print_status "Environment configuration validated"
}

# Start the bot
start_bot() {
    print_status "Starting DeepSeek Telegram Bot..."
    print_warning "Press Ctrl+C to stop the bot"
    echo ""
    
    python3 bot.py
}

# Main execution
main() {
    echo "🤖 DeepSeek Telegram Bot Startup Script"
    echo "========================================"
    echo ""
    
    check_python
    setup_venv
    install_deps
    check_env
    start_bot
}

# Handle script interruption
trap 'print_status "Bot stopped by user"; exit 0' INT

# Run main function
main
