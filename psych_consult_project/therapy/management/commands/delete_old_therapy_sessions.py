from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from therapy.models import TherapySession
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Deletes therapy sessions older than 30 days.'

    def handle(self, *args, **options):
        thirty_days_ago = timezone.now() - timedelta(days=30)
        old_sessions = TherapySession.objects.filter(updated_at__lt=thirty_days_ago)
        
        count, _ = old_sessions.delete()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} old therapy sessions.'))
        logger.info(f'Successfully deleted {count} old therapy sessions.')
