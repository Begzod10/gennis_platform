from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from ui.models import Vacancy, Message
from ui.serializers import VacancySerializer, MessageSerializer


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