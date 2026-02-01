from django.urls import path

from .Api.AttendanceDatas import AttendanceDatas, AttendanceDatasForGroup, AttendanceDatasForAllGroup
from .Api.AttendanceDelete import AttendanceDelete
from .Api.AttendanceList import AttendanceList, AttendanceListForAllGroups, AttendanceListSchool
from .Api.ToAttend import ToAttend, ToAttendSchool
from .Api.attend_dates import WeekdaysInMonthAPIView
from .views import DeleteAttendanceMonthApiView, AttendanceYearListView, GroupStudentsForChangeDebtView, \
    AttendanceDayAPIView, AttendancePeriodsView, GroupMonthlyAttendanceView, AttendanceCreateView, AttendanceDeleteView, \
    AttendanceDatesView, BranchDailyStatsView, GroupAttendanceView, ChangeStudentDebitFromClassProfile, GroupLessonsAPIView

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
    path('attendance_per_month_delete/<int:pk>/', DeleteAttendanceMonthApiView.as_view(),
         name='attendance_delete<str>'),
    path('attendance_per_month_change/<int:pk>/', ChangeStudentDebitFromClassProfile.as_view(),
         name='change<str>'),
    path('attendance_year_list/<int:group_id>/', AttendanceYearListView.as_view(), name='attendance_year_list'),
    path('attendance_year_list_all/<int:group_id>/', GroupStudentsForChangeDebtView.as_view(),
         name='attendance_year_list_s'),
    path('attendance-days-mobile/<int:group_id>/', AttendanceDayAPIView.as_view(), name='attendance-days'),

    path("attendance/periods/", AttendancePeriodsView.as_view(), name="attendance-periods"),
    path("attendance/periods-all/", AttendanceDatesView.as_view(), name="attendance-dates"),
    path("attendance/monthly/", GroupMonthlyAttendanceView.as_view(), name="attendance-monthly"),
    path(
        "attendance/branch-daily/<int:branch_id>/",
        BranchDailyStatsView.as_view(),
        name="branch-daily-stats"
    ),
    path(
        "attendance/group-attendance/<int:group_id>/",GroupLessonsAPIView.as_view(),name="group-attendance" ),

    # CRUD for daily attendance
    path("attendance/create/", AttendanceCreateView.as_view(), name="attendance-create"),
    path("attendance/create-list/", GroupAttendanceView.as_view(), name="attendance-create"),
    path("attendance/<int:id>/delete/", AttendanceDeleteView.as_view(), name="attendance-delete"),
]
