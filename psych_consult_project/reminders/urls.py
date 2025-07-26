from rest_framework.routers import DefaultRouter
from .views import ReminderViewSet

app_name = "reminders"

router = DefaultRouter()
router.register(r'', ReminderViewSet, basename='reminder')

urlpatterns = router.urls
