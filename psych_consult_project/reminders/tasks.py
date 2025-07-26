import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Reminder
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

User = get_user_model()

@shared_task
def send_reminder_email(reminder_id):
    try:
        reminder = Reminder.objects.get(id=reminder_id)
        user = reminder.user
        subject = f'Reminder: {reminder.task_name}'
        message = f'Hi {user.username},\n\nThis is a reminder for your task: "{reminder.task_name}" scheduled at {reminder.time}.\n\nThank you,\nThe Psych Consult Team'
        
        logger.info(f"Attempting to send reminder email for reminder ID: {reminder_id}")
        logger.info(f"Recipient email: {user.email}")
        logger.info(f"Subject: {subject}")
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        logger.info(f"Successfully sent reminder email for reminder ID: {reminder_id}")
    except Reminder.DoesNotExist:
        logger.warning(f"Reminder with ID {reminder_id} not found. Skipping email.")
        pass
    except Exception as e:
        logger.error(f"Error sending reminder email for reminder ID {reminder_id}: {e}", exc_info=True)
