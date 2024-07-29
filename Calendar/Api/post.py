from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from Calendar.models import Day, TypeDay
from Calendar.serializers import TypeDaySerializer


class TypeDayCreateView(generics.CreateAPIView):
    queryset = TypeDay.objects.all()
    serializer_class = TypeDaySerializer


class TypeDayUpdateView(generics.UpdateAPIView):
    queryset = TypeDay.objects.all()
    serializer_class = TypeDaySerializer


class TypeDayDestroyView(generics.DestroyAPIView):
    queryset = TypeDay.objects.all()
    serializer_class = TypeDaySerializer


class ChangeTypeView(APIView):
    def post(self, request):
        day_id = request.data.get('day_id')
        type_id = request.data.get('type_id')
        Day.objects.filter(id=day_id).update(type_id=type_id)
        color = TypeDay.objects.get(id=type_id).color
        return Response({'color': color}, status=status.HTTP_200_OK)
