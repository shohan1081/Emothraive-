from celery import shared_task
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

@shared_task
def delete_old_therapy_sessions_task():
    logger.info("Running delete_old_therapy_sessions_task...")
    try:
        call_command('delete_old_therapy_sessions')
        logger.info("delete_old_therapy_sessions_task completed successfully.")
    except Exception as e:
        logger.error(f"Error in delete_old_therapy_sessions_task: {e}")
