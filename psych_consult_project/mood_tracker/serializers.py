from rest_framework import serializers
from .models import MoodEntry
from django.db.models import Count

class MoodEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = MoodEntry
        fields = ['id', 'mood', 'date', 'created_at']
        read_only_fields = ['id', 'created_at']

class MoodSummarySerializer(serializers.Serializer):
    average_mood = serializers.CharField()
    most_frequent_emotion = serializers.CharField()
    mood_counts = serializers.DictField(child=serializers.IntegerField())
