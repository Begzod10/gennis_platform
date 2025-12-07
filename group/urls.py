from django.urls import path

from .gennis.AddToGroupApi import AddToGroupApi
from .gennis.CreatGroups import CreatGroups, CreateGroupReasonList, GroupReasonRetrieveUpdateDestroyAPIView, \
    CreateCourseTypesList, CourseTypesRetrieveUpdateDestroyAPIView
from .gennis.DeleteGroups import DeleteGroups
from .gennis.DeleteStudentFromGroup import DeleteStudentFromGroup
from .gennis.GetCheckedStudentsForClassTimeTable import GetCheckedStudentsForClassTimeTable, CheckedStudentsMoveToGroup
from .gennis.GetChekedStudentsTeachers import GetCheckedStudentsTeachers
from .gennis.GetGroupsForTeacher import GetGroupsForTeacher
from .gennis.GroupProfile import GroupProfile
from .gennis.MoveToGroupApi import MoveToGroupApi
from .gennis.TeacherGroupChange import TeacherGroupChange
from .school.ClassesList import ClassesView, AddClassesList, CreateGroupTeacherListView, ClassesView2
from .views import GroupStudentsClassRoom, GroupListView, GroupSubjectAddView, GroupSubjectRemoveView, \
    AddClassTypeToGroup

urlpatterns = [
    path('groups/create/', CreatGroups.as_view(), name='create'),
    path('groups/profile/<int:pk>/', GroupProfile.as_view(), name='profile'),
    path('groups/delete/<int:pk>/', DeleteGroups.as_view(), name='delete'),
    path('groups/teacher_change/<int:pk>/', TeacherGroupChange.as_view(), name='change'),
    path('groups/add-to-group/<int:pk>/', AddToGroupApi.as_view(), name='add-to-group-Api'),
    path('groups/move-to-group/<int:pk>/', MoveToGroupApi.as_view(), name='movie-to-group-Api'),
    path('group_reason/', CreateGroupReasonList.as_view(), name='group-reason-list-create'),
    path('group_reason/<int:pk>/', GroupReasonRetrieveUpdateDestroyAPIView.as_view(), name='group-reason-detail'),
    path('delete_student_from_group/<int:pk>/', DeleteStudentFromGroup.as_view(), name='delete_student_from_group'),
    path('course_types/', CreateCourseTypesList.as_view(), name='course-types-list-create'),
    path('course_types/<int:pk>/', CourseTypesRetrieveUpdateDestroyAPIView.as_view(), name='course-types-detail'),
    path('filtered_teachers_students/<int:branch_id>/<int:subject_id>/',
         GetCheckedStudentsTeachers.as_view(), name='filtered_teachers_students'),
    path('groups_for_teacher/<int:teacher_id>/<int:group_id>/',
         GetGroupsForTeacher.as_view(), name='groups_for_teacher'),
    path('classes/', ClassesView.as_view(), name='classes'),
    path('classes2/', ClassesView2.as_view(), name='classes'),
    path('filtered_students_for_class_time_table/', GetCheckedStudentsForClassTimeTable.as_view(),
         name='filtered_students_for_class_time_table'),
    path('filtered_students_move_to_class/', CheckedStudentsMoveToGroup.as_view(),
         name='filtered_students_move_to_class'),
    path('add/class/filtered/', AddClassesList.as_view(), name='add_class_filtered'),
    path('create/class/teachers/', CreateGroupTeacherListView.as_view(), name='create_class_teachers'),
    path('group-students/<int:pk>/', GroupStudentsClassRoom.as_view(), name='group-students'),
    path('groups_by_class_type/', GroupListView.as_view(), name='groups_by_class_type'),
    path('groups_add_subject/', GroupSubjectAddView.as_view(), name="groups_add_subject"),
    path('groups_remove_subject/', GroupSubjectRemoveView.as_view(), name="groups_add_subject"),
    path('group_add_class_type/', AddClassTypeToGroup.as_view(), name='groups_by_class_type'),
]
