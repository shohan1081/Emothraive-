
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psych_consult_project.settings')
import django
django.setup()

from django.utils import timezone
import pytz

dhaka_tz = pytz.timezone('Asia/Dhaka')
print(f"Application time (Asia/Dhaka): {timezone.now().astimezone(dhaka_tz).strftime('%Y-%m-%d %H:%M:%S %Z')}")
