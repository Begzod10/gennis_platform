from django.urls import path

from .Api.Flow import FlowListCreateView, FlowListView, FlowProfile
from flows.Api.checks.GetCheckedStudentsForClassTimeTable import GetFlowCheckedStudentsForClassTimeTable
from .Api.checks.checkStudentsMoveToFlow import CheckStudentsMoveToFlow

from .Api.checks.GetCheckedTeacherForClassTimeTable import GetCheckedTeacherForClassTimeTable
from .Api.DeleteFlow import DeleteFlow

urlpatterns = [
    path('flow-list-create/', FlowListCreateView.as_view(), name='flow'),
    path('flow-list/', FlowListView.as_view(), name='flow-list'),
    path('flow-profile/<int:pk>', FlowProfile.as_view(), name='flow-profile'),
    path('checked-students-for-time_table/', GetFlowCheckedStudentsForClassTimeTable.as_view(),
         name='checked-students-for-time_table'),
    path('move-to-flow/', CheckStudentsMoveToFlow.as_view(),
         name='move-to-flow'),
    path('checked-teachers/', GetCheckedTeacherForClassTimeTable.as_view(),
         name='checked-teachers'),
    path('flow-delete/<int:pk>', DeleteFlow.as_view(),
         name='flow-delete'),
]
