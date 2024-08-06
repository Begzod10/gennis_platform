from django.urls import path

from transfer.api.teacher.views import TeacherCreateView

urlpatterns = [
    path('teachers/create/', TeacherCreateView.as_view(), name='teacher-create'),

]
