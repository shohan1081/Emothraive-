from rest_framework import serializers
from .models import TherapyChatMessage, TherapySession

class TherapyChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TherapyChatMessage
        fields = ['id', 'user_message', 'ai_response', 'timestamp']
        read_only_fields = ['timestamp']

class TherapySessionSerializer(serializers.ModelSerializer):
    messages = TherapyChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = TherapySession
        fields = ['id', 'title', 'created_at', 'updated_at', 'messages']
        read_only_fields = ['created_at', 'updated_at']

class TherapySessionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TherapySession
        fields = ['id', 'title', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
