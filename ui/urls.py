from django.urls import path
from .views import VacancyListCreateAPIView, MessageListCreateAPIView, NewsListCreateAPIView, NewsDetailAPIView

urlpatterns = [
    path('vacancies/', VacancyListCreateAPIView.as_view(), name='vacancy-list-create'),
    path('messages/', MessageListCreateAPIView.as_view(), name='message-list-create'),
    path('news/', NewsListCreateAPIView.as_view(), name='news-list-create'),
    path('news/<int:pk>/', NewsDetailAPIView.as_view(), name='news-detail'),

]