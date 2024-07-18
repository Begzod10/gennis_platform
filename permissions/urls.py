from django.urls import path

from .Api.Tables import Tables
from .Api.DescriptionTables import DescriptionTables
from .Api.CreatGroupAndAddPermissions import CreatGroupAndAddPermissions
from .Api.AddUserJob import AddUserGroup
urlpatterns = [
    path('tables/', Tables.as_view(), name='tables'),
    path('description_for_table/', DescriptionTables.as_view(), name='description_for_table'),
    path('create_group_and_add_permissions/', CreatGroupAndAddPermissions.as_view(), name='create_group_and_add_permissions'),
    path('add_user_job/', AddUserGroup.as_view(), name='add_user_job'),
]
