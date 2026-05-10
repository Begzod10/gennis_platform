from django.urls import include, path
from rest_framework.routers import DefaultRouter

from website_sources.cms_views import (
    AdminComponentDefinitionViewSet,
    AdminDynamicFormViewSet,
    AdminGlobalSettingViewSet,
    AdminMediaAssetViewSet,
    AdminMenuViewSet,
    AdminPageSectionViewSet,
    AdminPageViewSet,
    AdminReusableBlockViewSet,
    AdminThemeSettingViewSet,
    AdminTranslationViewSet,
    AdminNewsViewSet,
    AdminAdmissionViewSet,
    AdminContactMessageViewSet,
    CurrentThemeView,
    DynamicFormSubmitView,
    NavigationView,
    PageRenderView,
    ReusableBlockView,
    PublicGlobalSettingView
)

router = DefaultRouter()
router.register('admin/components', AdminComponentDefinitionViewSet, basename='cms-admin-components')
router.register('admin/themes', AdminThemeSettingViewSet, basename='cms-admin-themes')
router.register('admin/menus', AdminMenuViewSet, basename='cms-admin-menus')
router.register('admin/blocks', AdminReusableBlockViewSet, basename='cms-admin-blocks')
router.register('admin/pages', AdminPageViewSet, basename='cms-admin-pages')
router.register('admin/sections', AdminPageSectionViewSet, basename='cms-admin-sections')
router.register('admin/forms', AdminDynamicFormViewSet, basename='cms-admin-forms')
router.register('admin/media', AdminMediaAssetViewSet, basename='cms-admin-media')
router.register('admin/settings', AdminGlobalSettingViewSet, basename='cms-admin-settings')
router.register('admin/translations', AdminTranslationViewSet, basename='cms-admin-translations')
router.register('admin/news', AdminNewsViewSet, basename='cms-admin-news')
router.register('admin/admissions', AdminAdmissionViewSet, basename='cms-admin-admissions')
router.register('admin/contacts', AdminContactMessageViewSet, basename='cms-admin-contacts')

urlpatterns = [
    path('', include(router.urls)),
    path('pages/<slug:slug>/render/', PageRenderView.as_view(), name='cms-page-render'),
    path('themes/current/', CurrentThemeView.as_view(), name='cms-current-theme'),
    path('navigation/<slug:key>/', NavigationView.as_view(), name='cms-navigation'),
    path('blocks/<slug:key>/', ReusableBlockView.as_view(), name='cms-block'),
    path('settings/<slug:key>/', PublicGlobalSettingView.as_view(), name='cms-public-setting'),
    path('forms/<slug:key>/submit/', DynamicFormSubmitView.as_view(), name='cms-form-submit'),
]
