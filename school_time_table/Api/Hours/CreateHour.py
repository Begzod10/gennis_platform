<<<<<<< HEAD
from rest_framework import generics

from rest_framework.response import Response
from rest_framework.views import APIView



from ...models import Hours
from ...serializers import HoursSerializers



class HourListCreateView(generics.ListCreateAPIView):
    queryset = Hours.objects.all().order_by('order')
    serializer_class = HoursSerializers






class HoursView(APIView):
    def get(self, request):
        hours_queryset = Hours.objects.all()

        high_hours = hours_queryset.filter(types__name='high')
        initial_hours = hours_queryset.filter(types__name='initial')

        high_data = HoursSerializers(high_hours, many=True).data
        initial_data = HoursSerializers(initial_hours, many=True).data

        result = {
            'high': high_data,
            'initial': initial_data
        }

        return Response(result)

=======
from rest_framework import generics

from rest_framework.response import Response
from rest_framework.views import APIView



from ...models import Hours
from ...serializers import HoursSerializers



class HourListCreateView(generics.ListCreateAPIView):
    queryset = Hours.objects.all().order_by('order')
    serializer_class = HoursSerializers






class HoursView(APIView):
    def get(self, request):
        hours_queryset = Hours.objects.all()

        high_hours = hours_queryset.filter(types__name='high')
        initial_hours = hours_queryset.filter(types__name='initial')

        high_data = HoursSerializers(high_hours, many=True).data
        initial_data = HoursSerializers(initial_hours, many=True).data

        result = {
            'high': high_data,
            'initial': initial_data
        }

        return Response(result)

>>>>>>> 2ec172c7ff13fdfb0800640eb3dcd1a861fd6f29
