from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Reminder
from .serializers import ReminderSerializer
from rest_framework.permissions import IsAuthenticated
from .tasks import send_reminder_email
import datetime
import pytz
from django.conf import settings
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    list=extend_schema(
        summary="List all reminders",
        description="Retrieve a list of all reminders for the authenticated user.",
        tags=["Reminders"]
    ),
    retrieve=extend_schema(
        summary="Retrieve a specific reminder",
        description="Retrieve details of a single reminder by its ID.",
        tags=["Reminders"]
    ),
    create=extend_schema(
        summary="Create a new reminder",
        description="Create a new reminder for the authenticated user. Supports one-time and daily repeating reminders.",
        tags=["Reminders"]
    ),
    update=extend_schema(
        summary="Update an existing reminder",
        description="Update all fields of an existing reminder by its ID.",
        tags=["Reminders"]
    ),
    partial_update=extend_schema(
        summary="Partially update an existing reminder",
        description="Update some fields of an existing reminder by its ID.",
        tags=["Reminders"]
    ),
    destroy=extend_schema(
        summary="Delete a reminder",
        description="Delete a reminder by its ID.",
        tags=["Reminders"]
    )
)
class ReminderViewSet(viewsets.ModelViewSet):
    serializer_class = ReminderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reminder.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        tz_name = self.request.headers.get('x-timezone', 'UTC')
        try:
            pytz.timezone(tz_name)
        except pytz.UnknownTimeZoneError:
            tz_name = 'UTC'
        reminder = serializer.save(user=self.request.user, timezone=tz_name)
        self._schedule_reminder_task(reminder)

    def perform_update(self, serializer):
        reminder = serializer.save()
        self._schedule_reminder_task(reminder)

    def perform_destroy(self, instance):
        # Revoke any pending tasks for this reminder
        # This requires storing task IDs, which is more complex.
        # For now, we'll just delete the reminder.
        instance.delete()

    def _schedule_reminder_task(self, reminder):
        # Combine date and time
        reminder_datetime = datetime.datetime.combine(reminder.start_date, reminder.time)

        # Make it timezone-aware
        try:
            tz = pytz.timezone(reminder.timezone)
        except pytz.UnknownTimeZoneError:
            tz = pytz.timezone(settings.TIME_ZONE) # Fallback to default

        # Localize the datetime
        localized_reminder_datetime = tz.localize(reminder_datetime)

        # Convert to UTC for Celery scheduling
        utc_reminder_datetime = localized_reminder_datetime.astimezone(pytz.utc)

        # Schedule the task
        if reminder.repeat_type == 'once':
            send_reminder_email.apply_async((reminder.id,), eta=utc_reminder_datetime)
        elif reminder.repeat_type == 'daily':
            # For daily reminders, we'll schedule the first one
            # and then the task itself will reschedule for subsequent days.
            # This is a simplified approach. A more robust solution would use Celery Beat
            # or a custom task that reschedules itself.
            send_reminder_email.apply_async((reminder.id,), eta=utc_reminder_datetime)
