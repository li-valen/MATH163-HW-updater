#!/bin/bash

# Homework Monitor Startup Script
# This script sets up and runs the homework monitor

echo "📚 Starting Homework Monitor..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
mkdir -p templates

# Ask user which mode to run
echo ""
echo "Choose monitoring mode:"
echo "1) Command line monitoring (background)"
echo "2) Web interface (with dashboard)"
echo "3) Both (monitor in background + web interface)"
echo "4) Configure Twilio SMS settings"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo "🚀 Starting command line monitoring..."
        python simple_monitor.py
        ;;
    2)
        echo "🚀 Starting web interface..."
        echo "📱 Open http://localhost:5000 in your browser"
        python web_interface.py
        ;;
    3)
        echo "🚀 Starting both monitoring and web interface..."
        echo "📱 Open http://localhost:5000 in your browser"
        # Start monitor in background
        python simple_monitor.py &
        MONITOR_PID=$!
        echo "📊 Monitor PID: $MONITOR_PID"
        # Start web interface
        python web_interface.py
        ;;
    4)
        echo "📝 Opening config.py to set Twilio credentials..."
        ${EDITOR:-vi} config.py
        ;;
    *)
        echo "❌ Invalid choice. Exiting."
        exit 1
        ;;
esac
