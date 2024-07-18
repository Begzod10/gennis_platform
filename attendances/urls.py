from django.urls import path

from .Api.ToAttend import ToAttend
from .Api.AttendanceList import AttendanceList
from .Api.AttendanceDatas import AttendanceDatas
from .Api.AttendanceDelete import AttendanceDelete

urlpatterns = [
    path('to_attend/<int:group_id>/', ToAttend.as_view(), name='to-attend'),
    path('attendance_list/<int:group_id>/', AttendanceList.as_view(), name='attendance_list'),
    path('attendance_datas/<int:group_id>/', AttendanceDatas.as_view(), name='attendance_datas'),
    path('attendance_delete/<int:group_id>/', AttendanceDelete.as_view(), name='attendance_delete'),
]
