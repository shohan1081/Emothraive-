import os
import io
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psych_consult_project.settings')
import django
django.setup()

apps_to_dump = [
    'users',
    'subscriptions',
    'workbook',
    'reminders',
    'music',
    'tasks',
    'therapy',
    'mood_tracker',
]

output_file = 'app_data.json'

with io.open(output_file, 'w', encoding='utf8') as f:
    call_command(
        'dumpdata',
        *apps_to_dump,
        indent=2,
        format='json',
        natural_foreign=True,
        natural_primary=True,
        stdout=f
    )

print(f"Data dumped to {output_file} with UTF-8 encoding.")
