from django.urls import path

from subjects.views import SyncSubjectsAndLevelsView, SubjectRetrieveUpdateDestroyAPIView, CreateSubjectList
from .api.get import SubjectLevelListAPIView, SubjectLevelRetrieveAPIView, LevelsForSubject
from .api.createdeleteupdate import SubjectLevelDestroyView, SubjectLevelUpdateView, SubjectLevelCreateView

urlpatterns = [
    path('sync/subjects/', SyncSubjectsAndLevelsView.as_view(), name='sync_subjects'),
    path('subject/', CreateSubjectList.as_view(), name='subject-list-create'),
    path('subject/<int:pk>/', SubjectRetrieveUpdateDestroyAPIView.as_view(), name='subject-retrieve-update-destroy'),
    path('subject_level_create/', SubjectLevelCreateView.as_view(), name='subject-level-create'),
    path('subject_level_level_update/<int:pk>/', SubjectLevelUpdateView.as_view(), name='subject-level-update'),
    path('subject_level_delete/<int:pk>/', SubjectLevelDestroyView.as_view(), name='subject-level-delete'),
    path('subject_level/<int:pk>/', SubjectLevelRetrieveAPIView.as_view(), name='subject-level'),
    path('level-for-subject/<int:pk>/', LevelsForSubject.as_view(), name='level-for-subject'),
    path('subject_level_list/', SubjectLevelListAPIView.as_view(), name='subject-level-list'),
]
