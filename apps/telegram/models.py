from django.db import models

class TelegramLog(models.Model):
    event_type = models.CharField(max_length=100)
    event_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'telegram_log'

