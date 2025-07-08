from django.apps import AppConfig
from django.conf import settings
import threading
import structlog

logger = structlog.get_logger(__name__)

class TelegramConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.telegram'
    
    def ready(self):
        """Initialize Telegram bot when Django starts"""
        # Prevent multiple initializations
        if hasattr(self, '_telegram_initialized'):
            return
        self._telegram_initialized = True
        
        # Only start bot if ENABLE_TELEGRAM_BOT is True and token is configured
        # Also check if we're NOT using the management command
        import os
        if (
            getattr(settings, 'ENABLE_TELEGRAM_BOT', False) and 
            getattr(settings, 'TELEGRAM_BOT_TOKEN', None) and
            not os.environ.get('DJANGO_BOT_MANAGEMENT_MODE', False)
        ):
            # Delay initialization to avoid database access during app startup
            import threading
            import time
            
            def delayed_init():
                time.sleep(2)  # Wait for Django to fully initialize
                try:
                    from .bot import setup_telegram_bot, get_application, start_polling_in_thread
                    
                    # Initialize the bot application
                    app = get_application()
                    if app:
                        # If in debug mode or no webhook URL, use polling
                        if settings.DEBUG or not getattr(settings, 'TELEGRAM_WEBHOOK_URL', None):
                            logger.info("Starting Telegram bot in polling mode (development)")
                            start_polling_in_thread()
                            mode = 'polling'
                        else:
                            logger.info("Telegram bot configured for webhook mode (production)")
                            mode = 'webhook'
                        
                        # Log bot initialization (delayed)
                        try:
                            from .models import TelegramLog
                            TelegramLog.objects.create(
                                event_type='bot_startup',
                                event_data={'status': 'initialized', 'mode': mode}
                            )
                        except Exception as e:
                            logger.warning(f"Could not log bot startup: {e}")
                        
                        logger.info(f"Telegram bot initialized successfully in {mode} mode")
                    else:
                        logger.warning("Failed to initialize Telegram bot")
                    
                except Exception as e:
                    logger.error(f"Failed to initialize Telegram bot: {str(e)}")
            
            # Start initialization in a separate thread
            init_thread = threading.Thread(target=delayed_init, daemon=True)
            init_thread.start()
