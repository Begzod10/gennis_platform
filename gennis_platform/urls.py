"""
URL configuration for gennis_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework_simplejwt.views import TokenVerifyView

from gennis_platform.schema import OnlyPartiesSchemaGenerator
from group.gennis.AddToGroupApi import UpdateGroupDataAPIView, GetGroupDataAPIView
from user.Api.read import GetUserAPIView, SetObserverView
from user.Api.write import CustomTokenObtainPairView
from user.views import CustomTokenRefreshView

urlpatterns = [
    # path('api/silk/', include('silk.urls', namespace='silk')),

    path('api/admin/', admin.site.urls),
    path('api/Users/', include('user.urls')),
    path('api/System/', include('system.urls')),
    path('api/Location/', include('location.urls')),
    path('api/Language/', include('language.urls')),
    path('api/Branch/', include('branch.urls')),
    path('api/Payments/', include('payments.urls')),
    path('api/Students/', include('students.urls')),
    path('api/parents/', include('parents.urls')),
    path('api/Teachers/', include('teachers.urls')),
    path('api/Capital/', include('capital.urls')),
    path('api/Class/', include('classes.urls')),
    path('api/Permissions/', include('permissions.urls')),
    path('api/Subjects/', include('subjects.urls')),
    path('api/Group/', include('group.urls')),
    path('api/Rooms/', include('rooms.urls')),
    path('api/TimeTable/', include('time_table.urls')),
    path('api/Attendance/', include('attendances.urls')),
    path('api/Lead/', include('lead.urls')),
    path('api/Books/', include('books.urls')),
    path('api/Tasks/', include('tasks.urls')),
    path('api/Observation/', include('observation.urls')),
    path('api/Overhead/', include('overhead.urls')),
    path('api/Flow/', include('flows.urls')),
    path('api/Lesson_plan/', include('lesson_plan.urls')),
    path('api/SchoolTimeTable/', include('school_time_table.urls')),
    path('api/Calendar/', include('Calendar.urls')),
    path('api/Bot/', include('bot.urls')),
    path('api/Ui/', include('ui.urls')),
    # path('api/Transfer/', include('transfer.urls')),
    path('api/Encashment/', include('encashment.urls')),
    path('api/Mobile/', include('mobile.urls')),
    path('api/terms/', include('terms.urls')),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/get_user/', GetUserAPIView.as_view(), name='get_user'),
    path('api/set_observer/<int:user_id>/', SetObserverView.as_view(), name='set_observer'),
    path('api/update_group_datas/', UpdateGroupDataAPIView.as_view(), name='update_group_datas'),
    path('api/get_group_datas/<int:group_id>/', GetGroupDataAPIView.as_view(), name='get_group_datas'),
    path('api/v1/investor/', include('api.v1.investor.urls')),
    path('api/Parties/', include('parties.urls')),
    path('api/reports/', include('report.urls')),
    path('api/surveys/', include('surveys.urls')),
    path('api/call/', include('tasks.admin.urls')),
    # path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    path(
        'api/schema/',
        SpectacularAPIView.as_view(generator_class=OnlyPartiesSchemaGenerator),
        name='schema'
    ),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
