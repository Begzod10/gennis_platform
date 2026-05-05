from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportViewSet, AdminRequestViewSet, RequestCommentViewSet

router = DefaultRouter()
router.register(r'reports', ReportViewSet)
router.register(r'admin-requests', AdminRequestViewSet)
router.register(r'request-comments', RequestCommentViewSet)



urlpatterns = [
    path('', include(router.urls)),
]