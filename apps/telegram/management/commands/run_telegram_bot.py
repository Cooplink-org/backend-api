import os
import sys
import asyncio
import signal
from django.core.management.base import BaseCommand
from django.conf import settings
import structlog

logger = structlog.get_logger(__name__)

class Command(BaseCommand):
    help = 'Start the Telegram bot with polling'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--mode',
            type=str,
            choices=['polling', 'webhook'],
            default='polling',
            help='Bot operation mode (polling or webhook)'
        )
        parser.add_argument(
            '--webhook-url',
            type=str,
            help='Webhook URL for webhook mode'
        )
    
    def handle(self, *args, **options):
        if not settings.TELEGRAM_BOT_TOKEN:
            self.stdout.write(
                self.style.ERROR('TELEGRAM_BOT_TOKEN not configured in settings')
            )
            return
        
        mode = options['mode']
        self.stdout.write(
            self.style.SUCCESS(f'Starting Telegram bot in {mode} mode...')
        )
        
        # Start bot using python-telegram-bot's built-in method
        from telegram.ext import Application
        from apps.telegram.bot import setup_bot_handlers
        
        try:
            # Create application
            application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
            
            # Setup handlers
            setup_bot_handlers(application)
            
            self.stdout.write(
                self.style.SUCCESS('🤖 Bot configured successfully!')
            )
            
            if mode == 'polling':
                self.stdout.write(
                    self.style.SUCCESS('🚀 Starting polling mode...')
                )
                
                # Start polling with proper error handling and loop management
                try:
                    application.run_polling(
                        allowed_updates=['message', 'callback_query'],
                        drop_pending_updates=True,
                        stop_signals=None,  # Disable signal handling
                        close_loop=False    # Prevent automatic loop closure
                    )
                except asyncio.exceptions.CancelledError:
                    logger.info("Bot polling cancelled")
                except Exception as polling_error:
                    logger.error(f"Polling error: {polling_error}")
                finally:
                    # Proper cleanup
                    try:
                        loop = asyncio.get_event_loop()
                        if not loop.is_closed():
                            pending = asyncio.all_tasks(loop)
                            if pending:
                                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                    except Exception:
                        pass
            
            elif mode == 'webhook':
                webhook_url = options.get('webhook_url') or settings.TELEGRAM_WEBHOOK_URL
                if not webhook_url:
                    self.stdout.write(
                        self.style.ERROR('Webhook URL not provided')
                    )
                    return
                
                self.stdout.write(
                    self.style.SUCCESS(f'🌐 Setting webhook to: {webhook_url}')
                )
                
                # Set webhook
                async def set_webhook():
                    try:
                        await application.initialize()
                        await application.bot.set_webhook(
                            url=f"{webhook_url.rstrip('/')}/api/telegram/webhook/"
                        )
                        await application.shutdown()
                    except Exception as webhook_error:
                        logger.error(f"Webhook setup error: {webhook_error}")
                
                # Run with new event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(set_webhook())
                finally:
                    loop.close()
                
                self.stdout.write(
                    self.style.SUCCESS('✅ Webhook mode configured successfully!')
                )
                
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('🛑 Bot stopped by user')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Bot error: {str(e)}')
            )
            logger.error("Bot startup failed", error=str(e))
