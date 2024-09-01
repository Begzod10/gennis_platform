from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Calendar.models import Day, TypeDay
from Calendar.serializers import TypeDaySerializer


class TypeDayCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = TypeDay.objects.all()
    serializer_class = TypeDaySerializer


class TypeDayUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = TypeDay.objects.all()
    serializer_class = TypeDaySerializer


class TypeDayDestroyView(generics.DestroyAPIView):

    permission_classes = [IsAuthenticated]
    queryset = TypeDay.objects.all()
    serializer_class = TypeDaySerializer



class ChangeTypeView(APIView):
    permission_classes = [IsAuthenticated]

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


class DeleteTypeView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        day_ids = request.data.get('days')
        result = []

        if not day_ids:
            return Response({"error": "No days provided"}, status=status.HTTP_400_BAD_REQUEST)

        for day_id in day_ids:
            day = Day.objects.get(pk=day_id)
            if day.day_name == 'Sunday':
                day_type = TypeDay.objects.filter(type="Dam").first()
            else:
                day_type = TypeDay.objects.filter(type="Ish kuni").first()

            day.type_id = day_type
            day.save()

            result.append({
                'day_id': day.id,
                'day_name': day.day_name,
                'day_number': day.day_number,
                'month': day.month.month_number,
                'type_name': day.type_id.type,
                'type_color': day.type_id.color
            })

        return Response(result, status=status.HTTP_200_OK)
