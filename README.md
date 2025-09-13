# 📚 Homework Monitor

A Python-based web monitoring tool that detects changes on your professor's website and notifies you when homework is posted.

## Features

- 🔍 **Change Detection**: Monitors the website for any content changes using content hashing
- 🌐 **HTTP Requests**: Uses `requests` library for fast and reliable website monitoring
- 📊 **Web Dashboard**: Beautiful web interface to view monitoring status and logs
- 📝 **Logging**: Comprehensive logging of all monitoring activities
- ⚙️ **Configurable**: Easy-to-modify settings for different monitoring needs
- 🔄 **Persistent State**: Remembers the last known state to detect changes accurately
- 📱 **SMS Notifications (Twilio)**: Get text messages when homework is posted
- ⏰ **6-Hour Auto-Refresh**: Checks for updates every 6 hours automatically

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure SMS (Twilio)

Edit `config.py` and set `TWILIO_SETTINGS` values:
- `account_sid`, `auth_token`
- `from_number` (your Twilio number)
- `to_number` (your phone)

### 3. Run the Monitor

**Easy Start:**
```bash
./run_monitor.sh
```

**Manual Options:**
```bash
# Command line monitoring (checks every 6 hours)
python simple_monitor.py

# Web interface (with dashboard)
python web_interface.py
# Then open http://localhost:5000 in your browser
```

### 4. Configure Settings

Edit `config.py` to customize:
- Check interval (default: 6 hours)
- Target URL
- Twilio credentials
- Notification methods
- Web interface settings

## How It Works

1. **Content Fetching**: The tool fetches the webpage content using `requests` with multiple fallback strategies
2. **Change Detection**: It calculates a SHA-256 hash of the page content and compares it with the previous hash
3. **State Persistence**: The current state is saved to `website_state.json` for persistence across restarts
4. **Notifications**: When changes are detected, notifications are sent based on your configuration
5. **Logging**: All activities are logged to `monitor_log.txt` for debugging and monitoring

## Files Structure

```
discrete/
├── simple_monitor.py        # Main monitoring script (requests only)
├── web_interface.py         # Web dashboard
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── run_monitor.sh          # Easy startup script
├── templates/
│   └── dashboard.html      # Web interface template
├── website_state.json      # Saved state (created automatically)
├── monitor_log.txt         # Activity logs (created automatically)
└── README.md              # This file
```

## Configuration Options

### Monitoring Settings
- `CHECK_INTERVAL_MINUTES`: How often to check for changes (default: 360 = 6 hours)
- `TARGET_URL`: The website to monitor
- `REQUEST_TIMEOUT`: Timeout for web requests

### Notification Methods
- `console`: Print notifications to console
- `log_file`: Write notifications to log file
- `desktop`: Desktop notifications (requires additional setup)
- `email`: Email notifications (requires SMTP configuration)
- `webhook`: Webhook notifications (Discord, Slack, etc.)
- `sms`: SMS notifications via Twilio

### Twilio Settings
- `account_sid`: Your Twilio Account SID
- `auth_token`: Your Twilio Auth Token
- `from_number`: Your Twilio phone number (E.164 format)
- `to_number`: Destination phone number (E.164 format)
- `message_template`: Message text template

## Usage Examples

### Basic Monitoring
```bash
# Start monitoring with default settings
python simple_monitor.py
```

### Web Dashboard
```bash
# Start web interface
python web_interface.py

# Open browser to http://localhost:5000
```

### Custom Configuration
```python
# Edit config.py to change settings
CHECK_INTERVAL_MINUTES = 15  # Check every 15 minutes
TARGET_URL = "https://your-professor-site.com"
```

## Troubleshooting

### Common Issues

1. **ChromeDriver Issues**: The tool automatically downloads ChromeDriver, but you can also install it manually
2. **Permission Errors**: Make sure the script has write permissions for the current directory
3. **Network Timeouts**: Increase `REQUEST_TIMEOUT` in config.py if the website is slow

### Logs

Check `monitor_log.txt` for detailed information about what the monitor is doing:
```bash
tail -f monitor_log.txt
```

## Advanced Features

### Custom Notifications

You can extend the notification system by modifying the `send_notification()` method in `simple_monitor.py`:

```python
def send_notification(self):
    # Add your custom notification logic here
    # Examples: email, SMS, push notifications, etc.
    pass
```

### Scheduled Monitoring

For production use, consider setting up a cron job or systemd service:

```bash
# Add to crontab to run every hour
0 * * * * cd /path/to/discrete && python simple_monitor.py
```

## Requirements

- Python 3.7+
- Internet connection

## License

This project is open source and available under the MIT License.
