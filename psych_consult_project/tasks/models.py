from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.timezone import localdate

# Gratitude Log
class GratitudeEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gratitude_entries')
    content = models.TextField()
    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'date']

    def __str__(self):
        return f"{self.user.username} - {self.date}"

# Breathing Exercise Guide
class BreathingExercise(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    duration_minutes = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# Positive Affirmations
class Affirmation(models.Model):
    text = models.TextField()
    date = models.DateField()
    completed_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='completed_affirmations', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

# Daily Task Completion
class DailyTaskCompletion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='daily_tasks')
    date = models.DateField(auto_now_add=True)
    gratitude_completed = models.BooleanField(default=False)
    breathing_exercise_count = models.PositiveIntegerField(default=0)
    affirmation_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'date']

    def __str__(self):
        return f'{self.user.username} - {self.date}'