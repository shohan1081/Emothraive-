from rest_framework import serializers
from .models import Reminder
import datetime

class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = '__all__'
        read_only_fields = ('user',)

    def validate(self, data):
        if data.get('repeat_type') == 'daily' and not data.get('end_date'):
            raise serializers.ValidationError("End date is required for daily reminders.")
        
        if data.get('repeat_type') == 'once' and data.get('end_date'):
            raise serializers.ValidationError("End date must be null for one-time reminders.")

        if data.get('start_date') and data.get('start_date') < datetime.date.today():
            raise serializers.ValidationError("Start date cannot be in the past.")

        if data.get('end_date') and data.get('start_date') and data.get('end_date') < data.get('start_date'):
            raise serializers.ValidationError("End date must be on or after the start date.")

        return data
