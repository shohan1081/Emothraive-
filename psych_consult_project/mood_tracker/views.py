from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.utils.timezone import localdate # Keep for reference, but won't be used for entry date
from datetime import timedelta, datetime # Import datetime

from .models import MoodEntry
from .serializers import MoodEntrySerializer, MoodSummarySerializer

class MoodEntryListCreate(generics.ListCreateAPIView):
    serializer_class = MoodEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MoodEntry.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Get the local date from the 'x-local-time' header
        local_date_str = self.request.headers.get('x-local-time')
        if not local_date_str:
            return Response(
                {"message": "x-local-time header is missing."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Assuming format is DD/MM/YYYY
            user_local_date = datetime.strptime(local_date_str, '%d/%m/%Y').date()
        except ValueError:
            return Response(
                {"message": "Invalid x-local-time format. Expected DD/MM/YYYY."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Enforce daily limit using the user's local date
        if MoodEntry.objects.filter(user=self.request.user, date=user_local_date).exists():
            return Response(
                {"message": f"You have already added a mood entry for {user_local_date.strftime('%Y-%m-%d')}."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save(user=self.request.user, date=user_local_date)

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

        # Get the local date from the 'x-local-time' header for summary calculation
        local_date_str = request.headers.get('x-local-time')
        if not local_date_str:
            # Fallback to server's local date if header is missing
            end_date = timezone.now().date()
        else:
            try:
                end_date = datetime.strptime(local_date_str, '%d/%m/%Y').date()
            except ValueError:
                # Fallback to server's local date if format is invalid
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