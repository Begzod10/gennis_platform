from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from ui.models import Vacancy, Message, News
from ui.serializers import VacancySerializer, MessageSerializer, NewsSerializer


class VacancyListCreateAPIView(ListCreateAPIView):
    queryset = Vacancy.objects.all().order_by('-id')
    serializer_class = VacancySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [AllowAny()]
class MessageListCreateAPIView(ListCreateAPIView):
    queryset = Message.objects.all().order_by('-id')
    serializer_class = MessageSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [AllowAny()]
class NewsListCreateAPIView(ListCreateAPIView):
    queryset = News.objects.all().order_by('-id')
    serializer_class = NewsSerializer
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

class NewsDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = News.objects.all().order_by('-id')
    serializer_class = NewsSerializer
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]