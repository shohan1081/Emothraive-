from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkbookListView, FavoriteWorkbookViewSet

app_name = 'workbook'

urlpatterns = [
    path('workbooks/', WorkbookListView.as_view(), name='workbook-list'),
    path('favorites/', FavoriteWorkbookViewSet.as_view({'get': 'list', 'post': 'add_workbook', 'delete': 'remove_workbook'}), name='favorite-workbook-list'),
]