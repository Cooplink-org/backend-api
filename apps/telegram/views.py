import json
import logging
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views import View
from telegram import Update
from .bot import setup_telegram_bot
import asyncio
import structlog
from asgiref.sync import sync_to_async

logger = structlog.get_logger(__name__)

# Initialize the bot application
bot_application = None

def get_bot_application():
    global bot_application
    if bot_application is None:
        bot_application = setup_telegram_bot()
    return bot_application

@csrf_exempt
@require_http_methods(["POST"])
def webhook_view(request):
    """
    Handle incoming Telegram webhook updates
    """
    try:
        # Parse the JSON payload
        data = json.loads(request.body.decode('utf-8'))
        
        # Create Update object
        update = Update.de_json(data, None)
        
        # Get bot application
        application = get_bot_application()
        
        if application:
            # Process the update asynchronously in a thread-safe way
            async def process_update_async():
                try:
                    await application.process_update(update)
                except Exception as e:
                    logger.error(f"Error processing update: {str(e)}")
            
            # Run the async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(process_update_async())
            finally:
                loop.close()
            
            return HttpResponse("OK", status=200)
        else:
            logger.error("Bot application not initialized")
            return HttpResponse("Bot not configured", status=500)
            
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook request")
        return HttpResponse("Invalid JSON", status=400)
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return HttpResponse("Internal error", status=500)

@require_http_methods(["GET"])
def bot_status_view(request):
    """
    Check bot status and configuration
    """
    try:
        application = get_bot_application()
        
        status_data = {
            "bot_configured": application is not None,
            "token_configured": bool(settings.TELEGRAM_BOT_TOKEN),
            "webhook_url": getattr(settings, 'TELEGRAM_WEBHOOK_URL', None),
            "status": "active" if application else "inactive"
        }
        
        return JsonResponse(status_data)
        
    except Exception as e:
        logger.error(f"Error checking bot status: {str(e)}")
        return JsonResponse({
            "error": str(e),
            "status": "error"
        }, status=500)

@require_http_methods(["GET"])
def bot_commands_view(request):
    """
    Get list of available bot commands
    """
    try:
        from .bot import BOT_COMMANDS
        
        commands_data = {
            "commands": [
                {
                    "command": cmd.command,
                    "description": cmd.description
                }
                for cmd in BOT_COMMANDS
            ],
            "total_commands": len(BOT_COMMANDS)
        }
        
        return JsonResponse(commands_data)
        
    except Exception as e:
        logger.error(f"Error getting bot commands: {str(e)}")
        return JsonResponse({
            "error": str(e)
        }, status=500)

# Optional: Set webhook URL (for deployment)
async def set_webhook():
    """
    Set the webhook URL for the Telegram bot
    """
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_WEBHOOK_URL:
        logger.warning("Bot token or webhook URL not configured")
        return False
    
    try:
        application = get_bot_application()
        if application:
            webhook_url = f"{settings.TELEGRAM_WEBHOOK_URL.rstrip('/')}/telegram/webhook/"
            await application.bot.set_webhook(url=webhook_url)
            logger.info(f"Webhook set to: {webhook_url}")
            return True
    except Exception as e:
        logger.error(f"Error setting webhook: {str(e)}")
        return False

# Optional: Remove webhook (for development)
async def remove_webhook():
    """
    Remove the webhook URL for the Telegram bot
    """
    try:
        application = get_bot_application()
        if application:
            await application.bot.delete_webhook()
            logger.info("Webhook removed")
            return True
    except Exception as e:
        logger.error(f"Error removing webhook: {str(e)}")
        return False
