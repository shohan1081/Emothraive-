from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import MusicViewSet, FavoritePlaylistViewSet

app_name = 'music'

router = DefaultRouter()
router.register(r'', MusicViewSet, basename='music')

urlpatterns = [
    path('favorites/', FavoritePlaylistViewSet.as_view({'get': 'list', 'post': 'add_music', 'delete': 'remove_music'}), name='favorite-playlist-list'),
] + router.urls
