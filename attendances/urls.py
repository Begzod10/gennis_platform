from django.urls import path

from .Api.AttendanceDatas import AttendanceDatas, AttendanceDatasForGroup, AttendanceDatasForAllGroup
from .Api.AttendanceDelete import AttendanceDelete
from .Api.AttendanceList import AttendanceList, AttendanceListForAllGroups,AttendanceListSchool
from .Api.ToAttend import ToAttend, ToAttendSchool
from .Api.attend_dates import WeekdaysInMonthAPIView

urlpatterns = [
    path('to_attend/<int:group_id>/', ToAttend.as_view(), name='to-attend'),
    path('to_attend_school/<int:group_id>/', ToAttendSchool.as_view(), name='to-attend-school'),
    path('attendance_list/<int:group_id>/', AttendanceList.as_view(), name='attendance_list'),
    path('attendance_list_school/<int:group_id>/', AttendanceListSchool.as_view(), name='attendance_list'),
    path('attendance_list_all/<int:student_id>/', AttendanceListForAllGroups.as_view(),
         name='attendance_list_all_groups'),
    path('attendance_datas/<int:group_id>/', AttendanceDatas.as_view(), name='attendance_datas'),
    path('attendance_datas_group/<int:group_id>/', AttendanceDatasForGroup.as_view(), name='attendance_datas'),
    path('attendance_datas_group_all/<int:student_id>/', AttendanceDatasForAllGroup.as_view(), name='attendance_datas'),
    path('attendance_delete/<int:group_id>/', AttendanceDelete.as_view(), name='attendance_delete'),
    path('school-to-attend-days/<int:group_id>/', WeekdaysInMonthAPIView.as_view(), name='school-to-attend-days'),
]
