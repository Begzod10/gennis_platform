from django.urls import path
from .views import VacancyListCreateAPIView, MessageListCreateAPIView

urlpatterns = [
    path('vacancies/', VacancyListCreateAPIView.as_view(), name='vacancy-list-create'),
    path('messages/', MessageListCreateAPIView.as_view(), name='message-list-create'),

]