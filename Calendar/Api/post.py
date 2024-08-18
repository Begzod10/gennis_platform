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


# class ChangeTypeView(APIView):
#     def post(self, request):
#         day_id = request.data.get('day_id')
#         type_id = request.data.get('type_id')
#         Day.objects.filter(id=day_id).update(type_id=type_id)
#         color = TypeDay.objects.get(id=type_id).color
#         return Response({'color': color}, status=status.HTTP_200_OK)

class ChangeTypeView(APIView):
    def post(self, request):
        day_ids = request.data.get('days')
        name = request.data.get('name')
        color = request.data.get('color')
        result = []

        if not day_ids:
            return Response({"error": "No days provided"}, status=status.HTTP_400_BAD_REQUEST)

        day_type, created = TypeDay.objects.get_or_create(type=name, color=color)

        for day_id in day_ids:
            Day.objects.filter(pk=day_id).update(type_id=day_type)
            day = Day.objects.get(pk=day_id)

            result.append({
                'day_id': day.id,
                'day_name': day.day_name,
                'day_number': day.day_number,
                'month': day.month.month_number,
                'type_name': day.type_id.type,
                'type_color': day.type_id.color
            })

        return Response(result, status=status.HTTP_200_OK)
