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
from schema_graph.views import Schema

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from .swagger import urlpatterns as doc_urls
from user.Api.write import CustomTokenObtainPairView

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
    path('Subjects/', include('subjects.urls')),
    path('Group/', include('group.urls')),
    path('Rooms/', include('rooms.urls')),
    path('TimeTable/', include('time_table.urls')),
    path('Attendance/', include('attendances.urls')),
    path('Lead/', include('lead.urls')),
    path('Books/', include('books.urls')),
    path('Permissions/', include('permissions.urls')),
    path('Lead/', include('lead.urls')),
    path('Books/', include('books.urls')),
    path('Attendance/', include('attendances.urls')),
    path('Tasks/', include('tasks.urls')),
    path('Observation/', include('observation.urls')),
    path('Overhead/', include('overhead.urls')),
    path('Flow/', include('flows.urls')),
    path('Lesson_plan/', include('lesson_plan.urls')),
    path('SchoolTimeTable/', include('school_time_table.urls')),
    path('Calendar/', include('Calendar.urls')),
    path('Transfer/', include('transfer.urls')),
    path('Encashment/', include('encashment.urls')),
    path("schema/", Schema.as_view()),
    path('Api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('Api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('Api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
urlpatterns += doc_urls

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
