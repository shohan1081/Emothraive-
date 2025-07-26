from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.utils.timezone import localdate
from datetime import timedelta

from .models import MoodEntry
from .serializers import MoodEntrySerializer, MoodSummarySerializer

class MoodEntryListCreate(generics.ListCreateAPIView):
    serializer_class = MoodEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MoodEntry.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Enforce daily limit at the view level as well for better error handling
        today = localdate()
        if MoodEntry.objects.filter(user=self.request.user, date=today).exists():
            return Response(
                {"message": "You can only add one mood entry per day."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save(user=self.request.user, date=today)

class MoodEntryDetail(generics.RetrieveAPIView):
    serializer_class = MoodEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MoodEntry.objects.filter(user=self.request.user)

class MoodSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        days = request.query_params.get('days', 7) # Default to past 7 days
        try:
            days = int(days)
        except ValueError:
            return Response({"message": "'days' parameter must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days - 1)

        mood_entries = MoodEntry.objects.filter(
            user=request.user,
            date__range=[start_date, end_date]
        )

        if not mood_entries.exists():
            return Response({"message": "No mood entries for the selected period."}, status=status.HTTP_404_NOT_FOUND)

        # Calculate most frequent emotion
        mood_counts = mood_entries.values('mood').annotate(count=Count('mood')).order_by('-count')
        most_frequent_emotion = mood_counts[0]['mood'] if mood_counts else None

        # Calculate average mood (simple numerical mapping for now)
        # You might want a more sophisticated approach for mood averaging
        mood_mapping = {'sad': 1, 'happy': 2, 'wow': 3} # Example mapping
        total_mood_score = sum(mood_mapping.get(entry.mood, 0) for entry in mood_entries)
        average_mood_score = total_mood_score / mood_entries.count()

        # Convert average score back to a descriptive string (example)
        if average_mood_score <= 1.5:
            average_mood = "Mostly Sad"
        elif average_mood_score <= 2.5:
            average_mood = "Neutral/Happy"
        else:
            average_mood = "Very Happy/Wow"

        # Prepare mood counts for response
        mood_counts_dict = {item['mood']: item['count'] for item in mood_counts}

        summary_data = {
            "average_mood": average_mood,
            "most_frequent_emotion": most_frequent_emotion,
            "mood_counts": mood_counts_dict
        }

        serializer = MoodSummarySerializer(summary_data)
        return Response(serializer.data, status=status.HTTP_200_OK)