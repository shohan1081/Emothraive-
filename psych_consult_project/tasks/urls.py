from django.urls import path
from .views import (
    GratitudeEntryListCreate, GratitudeComplete, BreathingExerciseList,
    BreathingExerciseComplete, BreathingExerciseLifetimeCountView, AffirmationList, AffirmationToday,
    AffirmationComplete, DailyTaskCompletionView
)

app_name = 'tasks'

urlpatterns = [
    path('gratitude/', GratitudeEntryListCreate.as_view(), name='gratitude-list-create'),
    path('gratitude/complete/', GratitudeComplete.as_view(), name='gratitude-complete'),
    path('breathing-exercises/', BreathingExerciseList.as_view(), name='breathing-list'),
    path('breathing-exercises/complete/', BreathingExerciseComplete.as_view(), name='breathing-complete'),
    path('breathing-exercises/lifetime-count/', BreathingExerciseLifetimeCountView.as_view(), name='breathing-lifetime-count'),
    path('affirmations/', AffirmationList.as_view(), name='affirmation-list'),
    path('affirmations/today/', AffirmationToday.as_view(), name='affirmation-today'),
    path('affirmations/complete/', AffirmationComplete.as_view(), name='affirmation-complete'),
    path('total-daily-tasks/', DailyTaskCompletionView.as_view(), name='total-daily-task-completion'),
]