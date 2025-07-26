import logging
from rest_framework import generics, status
from datetime import datetime

logger = logging.getLogger(__name__)
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import IntegrityError, transaction
from django.db.models import Sum, F
from django.utils import timezone

from .models import GratitudeEntry, BreathingExercise, Affirmation, DailyTaskCompletion
from .serializers import (
    GratitudeEntrySerializer, BreathingExerciseSerializer,
    AffirmationSerializer, DailyTaskCompletionSerializer
)

# Gratitude Log
class GratitudeEntryListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GratitudeEntrySerializer

    def get_queryset(self):
        return GratitudeEntry.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        today = timezone.localtime(timezone.now()).date()
        if GratitudeEntry.objects.filter(user=request.user, date=today).exists():
            return Response({
                "message": "You have already submitted a gratitude entry for today."
            }, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

class GratitudeComplete(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        completed = request.data.get('completed', False)
        local_time_str = request.headers.get('X-Local-Time')
        logger.info(f"Received X-Local-Time header: {local_time_str}")
        
        if not local_time_str:
            return Response({"message": "X-Local-Time header is missing."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            today = datetime.strptime(local_time_str, '%d/%m/%Y').date()
            logger.info(f"Parsed date from X-Local-Time (DD/MM/YYYY): {today}")
        except ValueError:
            try:
                today = datetime.strptime(local_time_str, '%m/%d/%Y').date()
                logger.info(f"Parsed date from X-Local-Time (MM/DD/YYYY): {today}")
            except ValueError as e:
                logger.error(f"ValueError parsing X-Local-Time '{local_time_str}': {e}")
                return Response({"message": "Invalid X-Local-Time format."}, status=status.HTTP_400_BAD_REQUEST)

        if completed:
            with transaction.atomic():
                try:
                    task = DailyTaskCompletion.objects.get(user=request.user, date=today)
                    task.gratitude_completed = True
                    task.save()
                except DailyTaskCompletion.DoesNotExist:
                    try:
                        task = DailyTaskCompletion.objects.create(
                            user=request.user, date=today,
                            gratitude_completed=True
                        )
                    except IntegrityError: # Catch the race condition
                        task = DailyTaskCompletion.objects.get(user=request.user, date=today)
                        task.gratitude_completed = True
                        task.save()
            return Response({"message": "Gratitude task marked as complete."}, status=status.HTTP_200_OK)
        return Response({"message": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

# Breathing Exercise Guide
class BreathingExerciseList(generics.ListAPIView):
    queryset = BreathingExercise.objects.all()
    serializer_class = BreathingExerciseSerializer
    permission_classes = [IsAuthenticated]

class BreathingExerciseComplete(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        completed = request.data.get('completed', False)
        local_time_str = request.headers.get('X-Local-Time')

        if not local_time_str:
            return Response({"message": "X-Local-Time header is missing."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            today = datetime.strptime(local_time_str, '%d/%m/%Y').date()
            logger.info(f"Parsed date from X-Local-Time (DD/MM/YYYY): {today}")
        except ValueError:
            try:
                today = datetime.strptime(local_time_str, '%m/%d/%Y').date()
                logger.info(f"Parsed date from X-Local-Time (MM/DD/YYYY): {today}")
            except ValueError as e:
                logger.error(f"ValueError parsing X-Local-Time '{local_time_str}': {e}")
                return Response({"message": "Invalid X-Local-Time format."}, status=status.HTTP_400_BAD_REQUEST)

        if completed:
            with transaction.atomic():
                try:
                    task = DailyTaskCompletion.objects.get(user=request.user, date=today)
                    task.breathing_exercise_count = F('breathing_exercise_count') + 1
                    task.save()
                    task.refresh_from_db() # Refresh to get the updated count
                except DailyTaskCompletion.DoesNotExist:
                    try:
                        task = DailyTaskCompletion.objects.create(
                            user=request.user, date=today,
                            breathing_exercise_count=1
                        )
                    except IntegrityError: # Catch the race condition
                        task = DailyTaskCompletion.objects.get(user=request.user, date=today)
                        task.breathing_exercise_count = F('breathing_exercise_count') + 1
                        task.save()
                        task.refresh_from_db()
            return Response({"message": "Breathing exercise session recorded.", "count": task.breathing_exercise_count}, status=status.HTTP_200_OK)
        return Response({"message": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

class BreathingExerciseLifetimeCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        total_count = DailyTaskCompletion.objects.filter(user=request.user).aggregate(total=Sum('breathing_exercise_count'))['total'] or 0
        return Response({"lifetime_count": total_count}, status=status.HTTP_200_OK)

# Positive Affirmations
class AffirmationList(generics.ListAPIView):
    serializer_class = AffirmationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Affirmation.objects.filter(date__lte=timezone.now().date())

class AffirmationToday(generics.RetrieveAPIView):
    serializer_class = AffirmationSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        completed_affirmations_ids = user.completed_affirmations.values_list('id', flat=True)

        # Try to get an affirmation that the user has not completed
        instance = Affirmation.objects.exclude(id__in=completed_affirmations_ids).order_by('?').first()

        # If all affirmations have been completed by the user, reset their completed list
        if not instance:
            user.completed_affirmations.clear() # Clear all completed affirmations for this user
            # Now, try to get a random affirmation again (all are now available)
            instance = Affirmation.objects.order_by('?').first()

        return instance

class AffirmationComplete(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        completed = request.data.get('completed', False)
        affirmation_id = request.data.get('affirmation_id')
        local_time_str = request.headers.get('X-Local-Time')

        if not local_time_str:
            return Response({"message": "X-Local-Time header is missing."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            today = datetime.strptime(local_time_str, '%d/%m/%Y').date()
            logger.info(f"Parsed date from X-Local-Time (DD/MM/YYYY): {today}")
        except ValueError:
            try:
                today = datetime.strptime(local_time_str, '%m/%d/%Y').date()
                logger.info(f"Parsed date from X-Local-Time (MM/DD/YYYY): {today}")
            except ValueError as e:
                logger.error(f"ValueError parsing X-Local-Time '{local_time_str}': {e}")
                return Response({"message": "Invalid X-Local-Time format."}, status=status.HTTP_400_BAD_REQUEST)

        if completed and affirmation_id:
            try:
                with transaction.atomic():
                    affirmation = Affirmation.objects.get(id=affirmation_id)
                    affirmation.completed_by.add(request.user)
                    try:
                        task = DailyTaskCompletion.objects.get(user=request.user, date=today)
                        task.affirmation_completed = True
                        task.save()
                    except DailyTaskCompletion.DoesNotExist:
                        try:
                            task = DailyTaskCompletion.objects.create(
                                user=request.user, date=today,
                                affirmation_completed=True
                            )
                        except IntegrityError: # Catch the race condition
                            task = DailyTaskCompletion.objects.get(user=request.user, date=today)
                            task.affirmation_completed = True
                            task.save()
                return Response({"message": "Affirmation marked as complete."}, status=status.HTTP_200_OK)
            except Affirmation.DoesNotExist:
                return Response({"message": "Affirmation not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"message": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

# Daily Task Completion
class DailyTaskCompletionView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DailyTaskCompletionSerializer

    def get_queryset(self):
        return DailyTaskCompletion.objects.filter(user=self.request.user)