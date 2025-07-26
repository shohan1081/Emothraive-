from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.timezone import localdate

class MoodEntry(models.Model):
    MOOD_CHOICES = [
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('neutral', 'Neutral'),
        ('Angry', 'Angry'),
        ('Anxious', 'Anxious'),
        # Add more mood choices as needed
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mood_entries')
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES)
    date = models.DateField(default=localdate)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'date']
        ordering = ['date']

    def clean(self):
        # Ensure only one mood entry per user per day
        if MoodEntry.objects.filter(user=self.user, date=self.date).exclude(pk=self.pk).exists():
            raise ValidationError('You can only add one mood entry per day.')

    def __str__(self):
        return f'{self.user.username} - {self.date} - {self.mood}'