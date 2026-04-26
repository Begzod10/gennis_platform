from django.urls import path
from .views import GeminiTokenAPIView, GeminiTemplateView

app_name = 'gemini'

urlpatterns = [
    path('token/', GeminiTokenAPIView.as_view(), name='gemini-token'),
    path('app/', GeminiTemplateView.as_view(), name='gemini-app'),
]
