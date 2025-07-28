from django.apps import AppConfig
from django.conf import settings

class SiteSettingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'site_settings'
    verbose_name = 'Site Settings'

    def ready(self):
        # Import SiteSetting model here to avoid AppRegistryNotReady error
        from .models import SiteSetting
        
        # Load settings from database into Django settings
        for setting in SiteSetting.objects.all():
            setattr(settings, setting.name, setting.value)