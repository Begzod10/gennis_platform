from django.urls import path

from subjects.views import SyncSubjectsAndLevelsView, SubjectLevelList, SubjectList, SubjectOne, SubjectLevelOne

urlpatterns = [
    path('sync/subjects/', SyncSubjectsAndLevelsView.as_view(), name='sync_subjects'),
    path('subject/', SubjectList.as_view(), name='subject-list'),
    path('subject-level/', SubjectLevelList.as_view(), name='subject-level-list'),
    path('subject/<int:pk>/', SubjectOne.as_view(),
         name='subject-retrieve'),
    path('subject-level/<int:pk>/', SubjectLevelOne.as_view(), name='subject-level-retrieve'),
]
