#!/usr/bin/env python3
"""
Web Interface for Homework Monitor
Provides a simple web interface to view monitoring status and logs
"""

from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime
import subprocess
import threading
import time

app = Flask(__name__)

class MonitorController:
    def __init__(self):
        self.monitor_process = None
        self.is_running = False
    
    def start_monitor(self):
        """Start the monitoring process"""
        if not self.is_running:
            try:
                # Try multiple Python paths
                python_paths = [
                    os.path.join(os.getcwd(), 'venv', 'bin', 'python3'),
                    os.path.join(os.getcwd(), 'venv', 'bin', 'python'),
                    'python3',
                    'python'
                ]
                
                python_path = None
                for path in python_paths:
                    if os.path.exists(path) or path in ['python3', 'python']:
                        # Test if this Python can import our modules
                        try:
                            result = subprocess.run([path, '-c', 'import sys; sys.path.insert(0, "."); import config; print("OK")'], 
                                                  capture_output=True, text=True, timeout=10)
                            if result.returncode == 0:
                                python_path = path
                                break
                        except:
                            continue
                
                if not python_path:
                    raise Exception("No working Python interpreter found")
                
                print(f"Using Python: {python_path}")
                
                # Start the monitor process
                self.monitor_process = subprocess.Popen(
                    [python_path, 'simple_monitor.py'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=os.getcwd(),
                    text=True
                )
                
                # Give it a moment to start and check if it's still running
                import time
                time.sleep(3)
                
                if self.monitor_process.poll() is None:
                    self.is_running = True
                    print("Monitor started successfully")
                    return True
                else:
                    # Process exited immediately, get error
                    stdout, stderr = self.monitor_process.communicate()
                    error_msg = f"Monitor process exited immediately. stdout: {stdout}, stderr: {stderr}"
                    print(error_msg)
                    raise Exception(error_msg)
                    
            except Exception as e:
                error_msg = f"Error starting monitor: {e}"
                print(error_msg)
                # Log the error to a file for debugging
                with open('monitor_error.log', 'a') as f:
                    f.write(f"{datetime.now()}: {error_msg}\n")
                return False
        return False
    
    def stop_monitor(self):
        """Stop the monitoring process"""
        if self.is_running and self.monitor_process:
            try:
                self.monitor_process.terminate()
                self.is_running = False
                return True
            except Exception as e:
                print(f"Error stopping monitor: {e}")
                return False
        return False

monitor_controller = MonitorController()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def get_status():
    """Get current monitoring status"""
    # Check if state file exists and get info
    state_info = {}
    if os.path.exists('website_state.json'):
        try:
            with open('website_state.json', 'r') as f:
                state = json.load(f)
                state_info = {
                    'last_check': state.get('timestamp', 'Unknown'),
                    'hash': state.get('hash', 'Unknown')[:16] + '...' if state.get('hash') else 'Unknown',
                    'monitoring': monitor_controller.is_running
                }
        except Exception as e:
            state_info = {'error': str(e)}
    
    return jsonify(state_info)

@app.route('/api/logs')
def get_logs():
    """Get recent log entries"""
    logs = []
    if os.path.exists('monitor_log.txt'):
        try:
            with open('monitor_log.txt', 'r') as f:
                lines = f.readlines()
                # Return last 50 lines
                logs = [line.strip() for line in lines[-50:]]
        except Exception as e:
            logs = [f"Error reading logs: {e}"]
    
    return jsonify(logs)

@app.route('/api/start', methods=['POST'])
def start_monitoring():
    """Start monitoring"""
    success = monitor_controller.start_monitor()
    return jsonify({'success': success})

@app.route('/api/stop', methods=['POST'])
def stop_monitoring():
    """Stop monitoring"""
    success = monitor_controller.stop_monitor()
    return jsonify({'success': success})

@app.route('/api/debug')
def debug_info():
    """Get debug information"""
    debug_info = {
        'python_paths': {
            'venv_python3': os.path.join(os.getcwd(), 'venv', 'bin', 'python3'),
            'venv_python': os.path.join(os.getcwd(), 'venv', 'bin', 'python'),
            'system_python3': 'python3',
            'system_python': 'python'
        },
        'files_exist': {
            'simple_monitor.py': os.path.exists('simple_monitor.py'),
            'config.py': os.path.exists('config.py'),
            'venv': os.path.exists('venv'),
            'venv_bin': os.path.exists(os.path.join('venv', 'bin')),
        },
        'working_directory': os.getcwd(),
        'monitor_running': monitor_controller.is_running
    }
    
    # Test Python interpreters
    python_tests = {}
    for name, path in debug_info['python_paths'].items():
        try:
            if os.path.exists(path) or path in ['python3', 'python']:
                result = subprocess.run([path, '-c', 'import sys; print(sys.version)'], 
                                      capture_output=True, text=True, timeout=5)
                python_tests[name] = {
                    'available': True,
                    'version': result.stdout.strip() if result.returncode == 0 else 'Error',
                    'error': result.stderr if result.returncode != 0 else None
                }
            else:
                python_tests[name] = {'available': False}
        except Exception as e:
            python_tests[name] = {'available': False, 'error': str(e)}
    
    debug_info['python_tests'] = python_tests
    
    return jsonify(debug_info)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
