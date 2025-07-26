from django.contrib import admin
from .models import GratitudeEntry, BreathingExercise, Affirmation, DailyTaskCompletion

admin.site.register(GratitudeEntry)
admin.site.register(BreathingExercise)
admin.site.register(Affirmation)
admin.site.register(DailyTaskCompletion)