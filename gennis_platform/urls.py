from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework_simplejwt.views import TokenVerifyView
from schema_graph.views import Schema
# from gennis_platform.views import index
from group.gennis.AddToGroupApi import UpdateGroupDataAPIView, GetGroupDataAPIView
from user.Api.read import GetUserAPIView, SetObserverView
from user.Api.write import CustomTokenObtainPairView
from user.views import CustomTokenRefreshView
from .swagger import urlpatterns as doc_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('Users/', include('user.urls')),
    path('System/', include('system.urls')),
    path('Location/', include('location.urls')),
    path('Language/', include('language.urls')),
    path('Branch/', include('branch.urls')),
    path('Payments/', include('payments.urls')),
    path('Students/', include('students.urls')),
    path('Teachers/', include('teachers.urls')),
    path('Capital/', include('capital.urls')),
    path('Class/', include('classes.urls')),
    path('Permissions/', include('permissions.urls')),
    path('Subjects/', include('subjects.urls')),
    path('Group/', include('group.urls')),
    path('Rooms/', include('rooms.urls')),
    path('TimeTable/', include('time_table.urls')),
    path('Attendance/', include('attendances.urls')),
    path('Lead/', include('lead.urls')),
    path('Books/', include('books.urls')),
    path('Tasks/', include('tasks.urls')),
    path('Observation/', include('observation.urls')),
    path('Overhead/', include('overhead.urls')),
    path('Flow/', include('flows.urls')),
    path('Lesson_plan/', include('lesson_plan.urls')),
    path('SchoolTimeTable/', include('school_time_table.urls')),
    path('Calendar/', include('Calendar.urls')),
    path('Transfer/', include('transfer.urls')),
    path('Encashment/', include('encashment.urls')),
    path('Mobile/', include('mobile.urls')),
    path("schema/", Schema.as_view()),
    path('Api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('Api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('Api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/get_user/', GetUserAPIView.as_view(), name='get_user'),
    path('api/set_observer/<int:user_id>/', SetObserverView.as_view(), name='set_observer'),
    path('api/update_group_datas/', UpdateGroupDataAPIView.as_view(), name='update_group_datas'),
    path('api/get_group_datas/<int:group_id>/', GetGroupDataAPIView.as_view(), name='get_group_datas'),
]

# Add index view for any undefined URL patterns
# urlpatterns += [re_path(r'^.*$', index)]

# Include the Swagger documentation URLs
urlpatterns += doc_urls

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
