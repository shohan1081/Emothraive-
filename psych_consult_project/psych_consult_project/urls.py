# psych_consult_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path("", lambda request: JsonResponse({"message": "Psych Consult API is live!"})),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls', namespace='users')),
    # path('accounts/', include('allauth.urls')),  # Commented out to avoid conflict
    path('api/subscriptions/', include('subscriptions.urls', namespace='subscriptions')),
    path('api/workbook/', include('workbook.urls', namespace='workbook')),
    path('api/reminders/', include('reminders.urls', namespace='reminders')),
    path('api/music/', include('music.urls', namespace='music')),
    path('api/tasks/', include('tasks.urls', namespace='tasks')),
    path('api/therapy/', include('therapy.urls', namespace='therapy')),
    path('api/mood-tracker/', include('mood_tracker.urls', namespace='mood_tracker')),
    
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)