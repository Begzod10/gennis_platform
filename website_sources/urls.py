from django.urls import include, path
from website_sources.views import (
    NewsListCreateView, NewsDetailView, NewsTogglePublishView,
    ImageUploadView, PublicNewsListView, PublicNewsDetailView,
    CategoryListView, PublicAdmissionCreateView,
    AdminAdmissionListView, AdminAdmissionDetailView, AdminAdmissionStatusView,
    PublicContactCreateView,
    AdminContactListView, AdminContactStatusView,
    PublicJobPositionListView, PublicCareerApplyView, PublicTalentPoolView,
    AdminJobPositionListCreateView, AdminJobPositionDetailView,
    AdminCareerApplicationListView, AdminStatsView, CategoryListCreateView, CategoryDetailView, PublicCareerUpdateView,
    TalentPoolDetailView,
    NewsImageUploadView, CareerApplicationCVUploadView, TalentPoolCVUploadView,
    # PublicSchoolStatisticListView, PublicTestimonialListView, PublicWhyChooseListView,
    # PublicPartnerListView, PublicLeadershipListView, PublicTranslationsView,
    # PageDetailView, MenuView,
    PageSectionListCreateView, PageSectionDetailView,
    PageSectionMultipleImageUploadView, PageSectionImageDeleteView
)

urlpatterns = [
    # path('pages/<slug:slug>/', PageDetailView.as_view(), name='page-detail'),
    # path('menus/<slug:key>/', MenuView.as_view(), name='menu-detail'),
    # path('cms/', include('website_sources.cms_urls')),

    # ── ADMIN STATS ────────────────────────────────────────────────────────────
    path('admin/stats/', AdminStatsView.as_view(), name='admin-stats'),

    # ── NEWS (ADMIN) ───────────────────────────────────────────────────────────
    path('news/', NewsListCreateView.as_view(), name='news-list-create'),
    path('news/<int:pk>/', NewsDetailView.as_view(), name='news-detail'),
    path('news/<int:pk>/toggle-publish/', NewsTogglePublishView.as_view(), name='news-toggle-publish'),
    path('news/<int:pk>/upload-image/', NewsImageUploadView.as_view(), name='news-upload-image'),

    # ── IMAGE UPLOAD ───────────────────────────────────────────────────────────
    path('upload/image/', ImageUploadView.as_view(), name='upload-image'),

    # ── PUBLIC NEWS ────────────────────────────────────────────────────────────
    path('public/news/', PublicNewsListView.as_view(), name='public-news-list'),
    path('public/news/<int:pk>/', PublicNewsDetailView.as_view(), name='public-news-detail-id'),
    path('public/news/slug/<slug:slug>/', PublicNewsDetailView.as_view(), name='public-news-detail-slug'),

    # ── CATEGORIES ─────────────────────────────────────────────────────────────
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('admin/categories/', CategoryListCreateView.as_view(), name='admin-category-list-create'),
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
    path('careers/<int:pk>/', PublicCareerUpdateView.as_view(), name='public-career-update'),
    path('applications/<int:pk>/upload-cv/', CareerApplicationCVUploadView.as_view(), name='application-upload-cv'),

    path('careers/talent-pool/', PublicTalentPoolView.as_view(), name='public-talent-pool'),
    path('careers/talent-pool/<int:pk>/', TalentPoolDetailView.as_view(), name='public-talent-pool'),
    path('talent-pool/<int:pk>/upload-cv/', TalentPoolCVUploadView.as_view(), name='talent-pool-upload-cv'),

    # ── NEW PUBLIC ENDPOINTS ───────────────────────────────────────────────────
    # path('public/stats/', PublicSchoolStatisticListView.as_view(), name='public-stats'),
    # path('public/testimonials/', PublicTestimonialListView.as_view(), name='public-testimonials'),
    # path('public/why-choose/', PublicWhyChooseListView.as_view(), name='public-why-choose'),
    # path('public/partners/', PublicPartnerListView.as_view(), name='public-partners'),
    # path('public/leadership/', PublicLeadershipListView.as_view(), name='public-leadership'),
    # path('public/translations/', PublicTranslationsView.as_view(), name='public-translations'),

    # ── CAREERS (ADMIN) ────────────────────────────────────────────────────────
    path('admin/careers/positions/', AdminJobPositionListCreateView.as_view(), name='admin-job-positions'),
    path('admin/careers/positions/<int:pk>/', AdminJobPositionDetailView.as_view(), name='admin-job-position-detail'),
    path('admin/careers/applications/', AdminCareerApplicationListView.as_view(), name='admin-career-applications'),

    # ── PAGE SECTIONS ──────────────────────────────────────────────────────────
    path('page-sections/', PageSectionListCreateView.as_view(), name='page-section-list-create'),
    path('page-sections/<int:pk>/', PageSectionDetailView.as_view(), name='page-section-detail'),
    path('page-sections/<int:pk>/upload-images/', PageSectionMultipleImageUploadView.as_view(), name='page-section-upload-images'),
    path('page-sections/images/<int:pk>/', PageSectionImageDeleteView.as_view(), name='page-section-image-delete'),
]
