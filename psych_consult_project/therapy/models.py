from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class TherapySession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='therapy_sessions')
    title = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at'] # Order by most recently updated sessions

    def __str__(self):
        return self.title or f"Session {self.id}"

class TherapyChatMessage(models.Model):
    session = models.ForeignKey(TherapySession, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    user_message = models.TextField()
    ai_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message in {self.session.title or self.session.id} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
