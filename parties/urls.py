from rest_framework.routers import DefaultRouter
from .views import PartyViewSet, PartyTaskViewSet

router = DefaultRouter()
router.register(r'parties', PartyViewSet)
router.register(r'party-tasks', PartyTaskViewSet)

urlpatterns = router.urls