from django.urls import path

from .Api.ToAttend import ToAttend
from .Api.AttendanceList import AttendanceList
from .Api.AttendanceDatas import AttendanceDatas

urlpatterns = [
    path('to_attend/<int:group_id>/', ToAttend.as_view(), name='to-attend'),
    path('attendance_list/<int:group_id>/', AttendanceList.as_view(), name='attendance_list'),
    path('attendance_datas/<int:group_id>/', AttendanceDatas.as_view(), name='attendance_datas'),
]
