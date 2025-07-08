from rest_framework import serializers
from .models import TelegramLog


class TelegramLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramLog
        fields = ('id', 'event_type', 'event_data', 'created_at')
