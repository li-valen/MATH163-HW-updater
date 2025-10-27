#!/usr/bin/env python3
"""
Simplified Homework Monitor - Uses only requests (no Selenium)
This version avoids ChromeDriver issues by using only HTTP requests
"""

import requests
from bs4 import BeautifulSoup
import hashlib
import json
import time
import os
from datetime import datetime
import schedule
import config
import smtplib
from email.mime.text import MIMEText

class SimpleHomeworkMonitor:
    def __init__(self, url, check_interval_minutes=360):
        self.url = url
        self.check_interval = check_interval_minutes
        self.state_file = config.STATE_FILE
        self.log_file = config.LOG_FILE
        self.last_hash = None
        self.last_content = None
        
        # Load previous state
        self.load_state()
    
    def log(self, message):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        try:
            print(log_message)
        except UnicodeEncodeError:
            # Fallback for systems that can't handle Unicode
            safe_message = message.encode('ascii', 'ignore').decode('ascii')
            print(f"[{timestamp}] {safe_message}")
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_message + "\n")
    
    def load_state(self):
        """Load previous website state from file"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                    self.last_hash = state.get("hash")
                    self.last_content = state.get("content")
                    self.log(f"Loaded previous state - Hash: {self.last_hash[:16] if self.last_hash else 'None'}...")
            except Exception as e:
                self.log(f"Error loading state: {e}")
                self.last_hash = None
                self.last_content = None
    
    def save_state(self, hash_value, content):
        """Save current website state to file"""
        state = {
            "hash": hash_value,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.log(f"Error saving state: {e}")
    
    def get_page_content(self):
        """Get page content using multiple request strategies"""
        strategies = [
            # Strategy 1: Standard browser headers
            {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            },
            # Strategy 2: Different user agent
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            },
            # Strategy 3: Mobile user agent
            {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        ]
        
        for i, headers in enumerate(strategies, 1):
            try:
                self.log(f"Trying request strategy {i}...")
                
                session = requests.Session()
                session.headers.update(headers)
                
                # Add authentication if configured
                auth = None
                if hasattr(config, 'AUTH_USERNAME') and hasattr(config, 'AUTH_PASSWORD'):
                    if config.AUTH_USERNAME and config.AUTH_PASSWORD:
                        from requests.auth import HTTPBasicAuth
                        auth = HTTPBasicAuth(config.AUTH_USERNAME, config.AUTH_PASSWORD)
                        self.log(f"Using HTTP Basic Auth as {config.AUTH_USERNAME}")
                
                response = session.get(self.url, timeout=30, allow_redirects=True, auth=auth)
                
                self.log(f"Strategy {i} - Status: {response.status_code}, Length: {len(response.text)}")
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    content = soup.get_text(strip=True)
                    self.log(f"Strategy {i} successful - Content length: {len(content)}")
                    return content
                elif response.status_code == 401:
                    self.log(f"Strategy {i} - 401 Unauthorized (may be normal)")
                    # Even with 401, we might get some content
                    if len(response.text) > 100:  # If we got substantial content
                        soup = BeautifulSoup(response.text, 'html.parser')
                        for script in soup(["script", "style"]):
                            script.decompose()
                        content = soup.get_text(strip=True)
                        self.log(f"Strategy {i} - Using 401 response content: {len(content)}")
                        return content
                else:
                    self.log(f"Strategy {i} - Unexpected status: {response.status_code}")
                    
            except Exception as e:
                self.log(f"Strategy {i} - Error: {e}")
                continue
        
        self.log("All request strategies failed")
        return None
    
    def calculate_hash(self, content):
        """Calculate SHA-256 hash of content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def check_for_changes(self):
        """Check if the website has changed"""
        self.log("Checking for changes...")
        
        current_content = self.get_page_content()
        if current_content is None:
            self.log("Failed to fetch page content")
            return False
        
        current_hash = self.calculate_hash(current_content)
        
        if self.last_hash is None:
            # First run - save initial state
            self.last_hash = current_hash
            self.last_content = current_content
            self.save_state(current_hash, current_content)
            self.log("Initial state saved - monitoring started")
            return False
        
        if current_hash != self.last_hash:
            self.log("🎉 WEBSITE UPDATED! Changes detected!")
            self.log(f"Previous hash: {self.last_hash[:16]}...")
            self.log(f"Current hash:  {current_hash[:16]}...")
            
            # Save new state
            self.last_hash = current_hash
            self.last_content = current_content
            self.save_state(current_hash, current_content)
            
            # Send notification
            self.send_notification()
            return True
        else:
            self.log("No changes detected")
            return False
    
    def send_notification(self):
        """Send notification about changes"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Console notification
        try:
            print("\n" + "="*50)
            print("HOMEWORK UPDATE DETECTED!")
            print("="*50)
            print(f"Time: {timestamp}")
            print(f"URL: {self.url}")
            print("="*50 + "\n")
        except UnicodeEncodeError:
            print("\n" + "="*50)
            print("HOMEWORK UPDATE DETECTED!")
            print("="*50)
            print(f"Time: {timestamp}")
            print(f"URL: {self.url}")
            print("="*50 + "\n")
        
        # Email notification (reliable)
        if config.NOTIFICATION_METHODS.get("email", False):
            try:
                email_settings = config.EMAIL_SETTINGS
                smtp_server = email_settings.get("smtp_server", "")
                smtp_port = email_settings.get("smtp_port", 587)
                username = email_settings.get("username", "")
                password = email_settings.get("password", "")
                to_email = email_settings.get("to_email", "")
                
                if smtp_server and username and password and to_email:
                    # Create email message
                    msg = MIMEText(f"HOMEWORK UPDATE: Your professor's site changed at {timestamp}.\n\nCheck it out: {self.url}")
                    msg['From'] = username
                    msg['To'] = to_email
                    msg['Subject'] = "Homework Update Alert - Discrete Math I"
                    
                    # Send email via SMTP
                    server = smtplib.SMTP(smtp_server, smtp_port)
                    server.starttls()
                    server.login(username, password)
                    server.send_message(msg)
                    server.quit()
                    
                    self.log("Email notification sent successfully!")
                else:
                    self.log("Email not sent - missing email config values")
            except Exception as e:
                self.log(f"Failed to send email: {e}")
        
        # SMS notification via email-to-SMS (FREE - may be unreliable)
        if config.NOTIFICATION_METHODS.get("sms", False):
            try:
                email_settings = config.EMAIL_SETTINGS
                smtp_server = email_settings.get("smtp_server", "")
                smtp_port = email_settings.get("smtp_port", 587)
                username = email_settings.get("username", "")
                password = email_settings.get("password", "")
                to_sms = email_settings.get("to_sms", "")
                
                if smtp_server and username and password and to_sms:
                    # Create message
                    msg = MIMEText(f"HOMEWORK UPDATE: Your professor's site changed at {timestamp}. {self.url}")
                    msg['From'] = username
                    msg['To'] = to_sms
                    msg['Subject'] = "Homework Update Alert"
                    
                    # Send email-to-SMS via SMTP
                    server = smtplib.SMTP(smtp_server, smtp_port)
                    server.starttls()
                    server.login(username, password)
                    server.send_message(msg)
                    server.quit()
                    
                    self.log("SMS sent successfully via email-to-SMS!")
                else:
                    self.log("SMS not sent - missing email config values (username, password, or to_sms)")
            except Exception as e:
                self.log(f"Failed to send SMS: {e}")
        
        # Log notification
        self.log("Notification sent!")
    
    def start_monitoring(self):
        """Start the monitoring process"""
        self.log(f"Starting simple homework monitor for {self.url}")
        self.log(f"Check interval: {self.check_interval} minutes")
        
        # Schedule the check
        schedule.every(self.check_interval).minutes.do(self.check_for_changes)
        
        # Run initial check
        self.check_for_changes()
        
        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute for scheduled tasks
        except KeyboardInterrupt:
            self.log("Monitoring stopped by user")
        except Exception as e:
            self.log(f"Error in monitoring loop: {e}")

def main():
    # Configuration from config.py
    URL = config.TARGET_URL
    CHECK_INTERVAL = config.CHECK_INTERVAL_MINUTES
    
    # Create and start monitor
    monitor = SimpleHomeworkMonitor(URL, CHECK_INTERVAL)
    monitor.start_monitoring()

if __name__ == "__main__":
    main()
