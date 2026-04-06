from django.urls import path
from . import views

urlpatterns = [
    path('admin/surveys/',
         views.AdminSurveyListCreateView.as_view(),
         name='admin-survey-list-create'),

    path('admin/surveys/<int:pk>/',
         views.AdminSurveyDetailView.as_view(),
         name='admin-survey-detail'),

    path('admin/surveys/<int:pk>/submissions/',
         views.AdminSurveySubmissionsView.as_view(),
         name='admin-survey-submissions'),

    path('admin/surveys/<int:pk>/statistics/',
         views.AdminSurveyStatisticsView.as_view(),
         name='admin-survey-statistics'),

    path('admin/submissions/<int:pk>/',
         views.AdminSubmissionDetailView.as_view(),
         name='admin-submission-detail'),

    path('mobile/surveys/my-statistics/',
         views.MobileMyStatisticsView.as_view(),
         name='mobile-my-statistics'),

    path('mobile/surveys/',
         views.MobileSurveyListView.as_view(),
         name='mobile-survey-list'),

    path('mobile/surveys/<int:pk>/',
         views.MobileSurveyDetailView.as_view(),
         name='mobile-survey-detail'),

    path('mobile/surveys/<int:pk>/teachers/',
         views.MobileTeacherListForSurveyView.as_view(),
         name='mobile-survey-teachers'),

    path('mobile/surveys/<int:pk>/submit/',
         views.MobileSurveySubmitView.as_view(),
         name='mobile-survey-submit'),
]