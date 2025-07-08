import os
import sys
import threading
import time
import subprocess
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import structlog

logger = structlog.get_logger(__name__)

class Command(BaseCommand):
    help = 'Run Django development server with Telegram bot'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--port',
            type=str,
            default='8000',
            help='Django server port (default: 8000)'
        )
        parser.add_argument(
            '--host',
            type=str,
            default='127.0.0.1',
            help='Django server host (default: 127.0.0.1)'
        )
        parser.add_argument(
            '--bot-mode',
            type=str,
            choices=['polling', 'webhook'],
            default='polling',
            help='Telegram bot mode (default: polling)'
        )
        parser.add_argument(
            '--no-bot',
            action='store_true',
            help='Start Django server without Telegram bot'
        )
    
    def handle(self, *args, **options):
        # Set environment variable to prevent auto-bot startup from apps.py
        os.environ['DJANGO_BOT_MANAGEMENT_MODE'] = 'true'
        
        port = options['port']
        host = options['host']
        bot_mode = options['bot_mode']
        no_bot = options['no_bot']
        
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting Cooplink Development Environment')
        )
        self.stdout.write(f'📡 Django server: http://{host}:{port}')
        
        if not no_bot:
            if not settings.TELEGRAM_BOT_TOKEN:
                self.stdout.write(
                    self.style.WARNING('⚠️  Telegram bot token not configured - starting without bot')
                )
                no_bot = True
            else:
                self.stdout.write(f'🤖 Telegram bot: {bot_mode} mode')
        
        # Start Django server in a separate thread
        django_thread = threading.Thread(
            target=self.start_django_server,
            args=(host, port),
            daemon=True
        )
        django_thread.start()
        
        # Give Django server time to start
        time.sleep(2)
        
        if not no_bot:
            # Start Telegram bot
            try:
                self.stdout.write(
                    self.style.SUCCESS('🤖 Starting Telegram bot...')
                )
                call_command('run_telegram_bot', mode=bot_mode)
            except KeyboardInterrupt:
                self.stdout.write(
                    self.style.WARNING('🛑 Shutting down...')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Bot error: {str(e)}')
                )
        else:
            try:
                self.stdout.write(
                    self.style.SUCCESS('✅ Django server running (bot disabled)')
                )
                # Keep the main thread alive
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stdout.write(
                    self.style.WARNING('🛑 Shutting down...')
                )
    
    def start_django_server(self, host, port):
        """Start Django development server"""
        try:
            call_command('runserver', f'{host}:{port}', verbosity=1, use_reloader=False)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Django server error: {str(e)}')
            )
