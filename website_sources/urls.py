"""
urls.py — Barcha endpointlar

Asosiy urls.py ga shu faylni include qiling:
    path('api/', include('urls')),
"""
from django.urls import path
from website_sources.views import (
    NewsListCreateView, NewsDetailView, NewsTogglePublishView,
    ImageUploadView, PublicNewsListView, PublicNewsDetailView,
    CategoryListView, PublicAdmissionCreateView,
    AdminAdmissionListView, AdminAdmissionDetailView, AdminAdmissionStatusView,
    PublicContactCreateView,
    AdminContactListView, AdminContactStatusView,
    PublicJobPositionListView, PublicCareerApplyView, PublicTalentPoolView,
    AdminJobPositionListCreateView, AdminJobPositionDetailView,
    AdminCareerApplicationListView, AdminStatsView, CategoryListCreateView, CategoryDetailView
)

urlpatterns = [

    # ── ADMIN STATS ────────────────────────────────────────────────────────────
    path('admin/stats/', AdminStatsView.as_view(), name='admin-stats'),

    # ── NEWS (ADMIN) ───────────────────────────────────────────────────────────
    path('news/', NewsListCreateView.as_view(), name='news-list-create'),
    path('news/<int:pk>/', NewsDetailView.as_view(), name='news-detail'),
    path('news/<int:pk>/toggle-publish/', NewsTogglePublishView.as_view(), name='news-toggle-publish'),

    # ── IMAGE UPLOAD ───────────────────────────────────────────────────────────
    path('upload/image/', ImageUploadView.as_view(), name='upload-image'),

    # ── PUBLIC NEWS ────────────────────────────────────────────────────────────
    path('public/news/', PublicNewsListView.as_view(), name='public-news-list'),
    path('public/news/<int:pk>/', PublicNewsDetailView.as_view(), name='public-news-detail-id'),
    path('public/news/slug/<slug:slug>/', PublicNewsDetailView.as_view(), name='public-news-detail-slug'),

    # ── CATEGORIES ─────────────────────────────────────────────────────────────
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('admin/categories/', CategoryListCreateView.as_view(), name='admin-category-list-create'),
    # GET / PUT / PATCH / DELETE
    path('admin/categories/<int:pk>/', CategoryDetailView.as_view(), name='admin-category-detail'),

    # ── ADMISSIONS ─────────────────────────────────────────────────────────────
    path('admissions/', PublicAdmissionCreateView.as_view(), name='public-admission-create'),
    path('admin/admissions/', AdminAdmissionListView.as_view(), name='admin-admission-list'),
    path('admin/admissions/<int:pk>/', AdminAdmissionDetailView.as_view(), name='admin-admission-detail'),
    path('admin/admissions/<int:pk>/status/', AdminAdmissionStatusView.as_view(), name='admin-admission-status'),

    # ── CONTACT ────────────────────────────────────────────────────────────────
    path('contact/', PublicContactCreateView.as_view(), name='public-contact-create'),
    path('admin/contacts/', AdminContactListView.as_view(), name='admin-contact-list'),
    path('admin/contacts/<int:pk>/status/', AdminContactStatusView.as_view(), name='admin-contact-status'),

    # ── CAREERS (PUBLIC) ───────────────────────────────────────────────────────
    path('careers/positions/', PublicJobPositionListView.as_view(), name='public-job-positions'),
    path('careers/apply/', PublicCareerApplyView.as_view(), name='public-career-apply'),
    path('careers/talent-pool/', PublicTalentPoolView.as_view(), name='public-talent-pool'),

    # ── CAREERS (ADMIN) ────────────────────────────────────────────────────────
    path('admin/careers/positions/', AdminJobPositionListCreateView.as_view(), name='admin-job-positions'),
    path('admin/careers/positions/<int:pk>/', AdminJobPositionDetailView.as_view(), name='admin-job-position-detail'),
    path('admin/careers/applications/', AdminCareerApplicationListView.as_view(), name='admin-career-applications'),
]
