from django.urls import path
from subjects.views import SyncSubjectsAndLevelsView,SubjectLevelList,SubjectList

urlpatterns = [
    path('sync/subjects/', SyncSubjectsAndLevelsView.as_view(), name='sync_subjects'),
    path('subject/', SubjectList.as_view(), name='subject-list'),
    path('subject-level/', SubjectLevelList.as_view(), name='subject-level-list'),

]
