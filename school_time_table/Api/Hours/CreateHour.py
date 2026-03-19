from rest_framework import generics

from rest_framework.response import Response
from rest_framework.views import APIView

from ...models import Hours
from ...serializers import HoursSerializers


class HourListCreateView(generics.ListCreateAPIView):
    serializer_class = HoursSerializers

    def get_queryset(self):
        queryset = Hours.objects.order_by('order')

        branch_id = self.request.query_params.get('branch')
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)

        return queryset


class HoursView(APIView):
    def get(self, request):
        branch_id = request.query_params.get('branch')

        hours_queryset = Hours.objects.all()

        if branch_id:
            hours_queryset = hours_queryset.filter(branch_id=branch_id)

        high_hours = hours_queryset.filter(types__name='high')
        initial_hours = hours_queryset.filter(types__name='initial')

        high_data = HoursSerializers(high_hours, many=True).data
        initial_data = HoursSerializers(initial_hours, many=True).data

        return Response({
            'high': high_data,
            'initial': initial_data
        })
