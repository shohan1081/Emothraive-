from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatView, TherapySessionViewSet

app_name = 'therapy'

router = DefaultRouter()
router.register(r'sessions', TherapySessionViewSet, basename='therapy-session')

urlpatterns = [
    path('chat/', ChatView.as_view(), name='chat'),
    path('', include(router.urls)),
]
