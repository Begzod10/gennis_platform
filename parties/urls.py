from rest_framework.routers import DefaultRouter
from .views import (
    PartyViewSet, PartyMemberViewSet,
    PartyTaskViewSet, CompetitionViewSet, CompetitionResultViewSet,
    StudentSelectViewSet, GroupSelectViewSet,
)

router = DefaultRouter()
router.register(r'parties',              PartyViewSet,             basename='party')
router.register(r'members',              PartyMemberViewSet,       basename='member')
router.register(r'party-tasks',          PartyTaskViewSet,         basename='party-task')
router.register(r'competitions',         CompetitionViewSet,       basename='competition')
router.register(r'competition-results',  CompetitionResultViewSet, basename='competition-result')
router.register(r'students',             StudentSelectViewSet,     basename='student-select')
router.register(r'groups',               GroupSelectViewSet,       basename='group-select')

urlpatterns = router.urls

