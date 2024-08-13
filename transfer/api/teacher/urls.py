from django.urls import path, include

from transfer.api.teacher.views import TeacherCreateView,TeacherBranchCreateView

urlpatterns = [
    path('teachers/create/', TeacherCreateView.as_view(), name='teacher-create'),
    path('teachers/add-branch/', TeacherBranchCreateView.as_view(), name='teacher-add-branch'),

    path('', include('transfer.api.teacher.salary.urls')),

]
