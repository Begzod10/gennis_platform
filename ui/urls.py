from rest_framework.routers import DefaultRouter

from .views import FrontedPageTypeViewSet, FrontedPageViewSet, FrontedPageImageViewSet

router = DefaultRouter()
router.register(r'fronted-page-types', FrontedPageTypeViewSet, basename='frontedpagetype')
router.register(r'fronted-pages', FrontedPageViewSet, basename='frontedpage')
router.register(r'fronted-page-images', FrontedPageImageViewSet, basename='frontedpageimage')

urlpatterns = router.urls
