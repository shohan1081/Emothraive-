# Generated by Django 5.2.4 on 2025-07-21 19:47

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('therapy', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='therapychatmessage',
            name='user',
        ),
        migrations.CreateModel(
            name='TherapySession',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='therapy_sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-updated_at'],
            },
        ),
        migrations.AddField(
            model_name='therapychatmessage',
            name='session',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='therapy.therapysession'),
        ),
    ]
