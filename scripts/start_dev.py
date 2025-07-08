#!/usr/bin/env python
"""
Cooplink Development Server Startup Script
Runs Django server and Telegram bot together with proper process management
"""

import os
import sys
import django
import asyncio
import threading
import signal
import time
import subprocess
from multiprocessing import Process
from pathlib import Path

# Add project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.dev')
django.setup()

from django.core.management import execute_from_command_line
from django.conf import settings
import structlog

logger = structlog.get_logger(__name__)

class CooplinkDevServer:
    def __init__(self, host='127.0.0.1', port='8000', bot_mode='polling'):
        self.host = host
        self.port = port
        self.bot_mode = bot_mode
        self.django_process = None
        self.bot_process = None
        self.shutdown_requested = False
        
    def start_django_server(self):
        """Start Django development server in a separate process"""
        try:
            print(f"🚀 Starting Django server at http://{self.host}:{self.port}")
            execute_from_command_line([
                'manage.py', 'runserver', f'{self.host}:{self.port}', '--noreload'
            ])
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"❌ Django server error: {e}")
    
    def start_telegram_bot(self):
        """Start Telegram bot in a separate process"""
        try:
            if not settings.TELEGRAM_BOT_TOKEN:
                print("⚠️  Telegram bot token not configured - skipping bot")
                return
            
            print(f"🤖 Starting Telegram bot in {self.bot_mode} mode")
            execute_from_command_line([
                'manage.py', 'run_telegram_bot', f'--mode={self.bot_mode}'
            ])
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"❌ Bot error: {e}")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n🛑 Shutdown signal received...")
        self.shutdown_requested = True
        
        if self.django_process and self.django_process.is_alive():
            print("📡 Stopping Django server...")
            self.django_process.terminate()
            
        if self.bot_process and self.bot_process.is_alive():
            print("🤖 Stopping Telegram bot...")
            self.bot_process.terminate()
        
        # Give processes time to clean up
        time.sleep(2)
        
        if self.django_process and self.django_process.is_alive():
            self.django_process.kill()
            
        if self.bot_process and self.bot_process.is_alive():
            self.bot_process.kill()
        
        print("✅ All services stopped")
        sys.exit(0)
    
    def run(self):
        """Main run method"""
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("=" * 50)
        print("🚀 COOPLINK DEVELOPMENT ENVIRONMENT")
        print("=" * 50)
        print(f"📡 Django: http://{self.host}:{self.port}")
        print(f"🤖 Bot Mode: {self.bot_mode}")
        print(f"🔧 Settings: {settings.SETTINGS_MODULE}")
        print("=" * 50)
        
        try:
            # Start Django server
            self.django_process = Process(target=self.start_django_server)
            self.django_process.start()
            
            # Give Django time to start
            time.sleep(3)
            
            # Start Telegram bot if token is configured
            if settings.TELEGRAM_BOT_TOKEN:
                self.bot_process = Process(target=self.start_telegram_bot)
                self.bot_process.start()
            else:
                print("⚠️  Skipping Telegram bot (no token configured)")
            
            print("✅ All services started successfully!")
            print("Press Ctrl+C to stop all services")
            
            # Keep main process alive
            while not self.shutdown_requested:
                time.sleep(1)
                
                # Check if processes are still alive
                if self.django_process and not self.django_process.is_alive():
                    print("❌ Django server died unexpectedly")
                    break
                    
                if self.bot_process and not self.bot_process.is_alive():
                    print("❌ Telegram bot died unexpectedly")
                    # Bot can die and restart, so don't break
        
        except KeyboardInterrupt:
            print("\n🛑 User requested shutdown...")
        except Exception as e:
            print(f"❌ Critical error: {e}")
        finally:
            self.signal_handler(None, None)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Cooplink Development Server')
    parser.add_argument('--host', default='127.0.0.1', help='Django server host')
    parser.add_argument('--port', default='8000', help='Django server port')
    parser.add_argument('--bot-mode', choices=['polling', 'webhook'], 
                       default='polling', help='Telegram bot mode')
    
    args = parser.parse_args()
    
    server = CooplinkDevServer(
        host=args.host,
        port=args.port,
        bot_mode=args.bot_mode
    )
    
    server.run()

if __name__ == '__main__':
    main()
