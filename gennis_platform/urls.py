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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
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
    path('Subjects/', include('subjects.urls')),
    path('Group/', include('group.urls')),
    path('Rooms/', include('rooms.urls')),
    path('TimeTable/', include('time_table.urls')),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
# =======
# from .swagger import urlpatterns as doc_urls
#
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
#
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', include('user.urls')),
#     path('api/', include('system.urls')),
#     path('api/', include('location.urls')),
#     path('api/', include('language.urls')),
#     path('api/', include('branch.urls')),
#     path('api/', include('payments.urls')),
#     path('api/', include('students.urls')),
#     path('api/', include('teachers.urls')),
#     path('api/', include('subjects.urls')),
#     path('api/', include('group.urls')),
#     path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#     path('api/v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
# >>>>>>> 1914f79b58b269d6eea0f0c66ac3e15c862c1be9
# ]
urlpatterns += doc_urls

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
