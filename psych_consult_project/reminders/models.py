from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Reminder(models.Model):
    REPEAT_CHOICES = [
        ('once', 'Only Once'),
        ('daily', 'Daily'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminders')
    task_name = models.CharField(max_length=255)
    time = models.TimeField()
    timezone = models.CharField(max_length=100, default='Asia/Dhaka')
    repeat_type = models.CharField(max_length=10, choices=REPEAT_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)  # required if repeat_type is daily
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.task_name