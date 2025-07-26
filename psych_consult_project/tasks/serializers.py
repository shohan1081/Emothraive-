from rest_framework import serializers
from .models import GratitudeEntry, BreathingExercise, Affirmation, DailyTaskCompletion
from django.utils import timezone

# Gratitude Log
class GratitudeEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = GratitudeEntry
        fields = ['id', 'content', 'date', 'created_at']
        read_only_fields = ['id', 'date', 'created_at']

# Breathing Exercise Guide
class BreathingExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BreathingExercise
        fields = ['id', 'title', 'description', 'duration_minutes', 'created_at']
        read_only_fields = ['id', 'created_at']

# Positive Affirmations
class AffirmationSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = Affirmation
        fields = ['id', 'text', 'date', 'is_completed', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_is_completed(self, obj):
        user = self.context['request'].user
        return user in obj.completed_by.all()

# Daily Task Completion
class DailyTaskCompletionSerializer(serializers.ModelSerializer):
    breathing_completed = serializers.SerializerMethodField()

    class Meta:
        model = DailyTaskCompletion
        fields = ['id', 'date', 'gratitude_completed', 'breathing_completed', 'breathing_exercise_count', 'affirmation_completed']
        read_only_fields = ['id', 'date']

    def get_breathing_completed(self, obj):
        return obj.breathing_exercise_count > 0