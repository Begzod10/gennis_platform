from django.urls import path

from .Api.Tables import Tables
from .Api.DescriptionTables import DescriptionTables
from .Api.CreatGroupAndAddPermissions import AddPermissions, Jobs, JobProfile
from .Api.AddUserJob import AddUserGroup
from .Api.AddPermissionManagersAndDirectors import AddPermissionManagersAndDirectors
from permissions.views import SystemListUser,LocationListUser,BranchListUser,DynamicModelListView
urlpatterns = [
    path('tables/', Tables.as_view(), name='tables'),
    path('description_for_table/', DescriptionTables.as_view(), name='description_for_table'),
    path('add_permissions/<int:pk>', AddPermissions.as_view(),
         name='add_permissions'),

    path('add_user_job/', AddUserGroup.as_view(), name='add_user_job'),
    path('add_permissions_managers_and_directors/', AddPermissionManagersAndDirectors.as_view(),
         name='add_permissions_managers_and_directors'),
    path('jobs/', Jobs.as_view(),
         name='jobs'),
    path('job_profile/<int:pk>', JobProfile.as_view(),
         name='job_profile'),
    path('user_systems/', SystemListUser.as_view(), name='user_systems'),
    path('user_locations/<int:pk>/', LocationListUser.as_view(), name='user_systems'),
    path('user_branchs/<int:pk>/', BranchListUser.as_view(), name='user_systems'),
    path('models/', DynamicModelListView.as_view(), name='dynamic-model-list'),

]
