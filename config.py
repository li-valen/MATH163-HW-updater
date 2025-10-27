"""
Configuration file for Homework Monitor
"""

# Website to monitor
TARGET_URL = "https://dicas.com/ccp/courses/discrete1/index.php"

# Website authentication (HTTP Basic Auth)
AUTH_USERNAME = "ccpstudent"
AUTH_PASSWORD = "Friedrich_Gauss"

# Monitoring settings
CHECK_INTERVAL_MINUTES = 360  # How often to check for changes (6 hours)
REQUEST_TIMEOUT = 30  # Timeout for web requests
SELENIUM_WAIT_TIME = 3  # How long to wait for page to load with Selenium

# File paths
STATE_FILE = "website_state.json"
LOG_FILE = "monitor_log.txt"

# Web interface settings
WEB_HOST = "0.0.0.0"
WEB_PORT = 5000
WEB_DEBUG = True

# Notification settings (customize as needed)
NOTIFICATION_METHODS = {
    "console": True,  # Print to console
    "log_file": True,  # Write to log file
    "desktop": False,  # Desktop notification (requires additional setup)
    "email": True,  # Email notification (requires SMTP setup)
    "webhook": False,  # Webhook notification (requires webhook URL)
    "sms": False,  # SMS notification via email-to-SMS (T-Mobile gateway discontinued)
}

# Email settings (for email-to-SMS and email notifications)
EMAIL_SETTINGS = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "xinfinitypro@gmail.com",  # Your email (e.g., yourname@gmail.com)
    "password": "wpginpvdxncwecuc",  # Your Gmail app password (get from Google Account settings)
    "to_email": "xinfinitypro@gmail.com",  # Where to send notifications
    "to_sms": "2677529395@tmomail.net",  # Email-to-SMS for phone number +12677529395
}

# Webhook settings (if webhook notifications are enabled)
WEBHOOK_URL = ""  # Your webhook URL (e.g., Discord, Slack, etc.)

# Twilio settings (for SMS notifications)
TWILIO_SETTINGS = {
    "account_sid": "",  # Twilio Account SID
    "auth_token": "",   # Twilio Auth Token
    "from_number": "",  # Your Twilio phone number (e.g., +15551234567)
    "to_number": "+12677529395",    # Destination phone number (e.g., +15557654321)
    "message_template": "HOMEWORK UPDATE: Your professor's site changed at {timestamp}. {url}"
}

# User agent for web requests
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
