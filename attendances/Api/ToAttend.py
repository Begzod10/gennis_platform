from rest_framework import generics
from rest_framework import generics

from ..models import AttendancePerDay
from ..serializers import AttendancePerDayCreateUpdateSerializer


# class ToAttend(APIView):
#     def post(self, request, group_id):
#         data = json.loads(request.body)
#         return Response(check_and_create_attendance_per_month(group_id, students=data['students'], date=data['date']))
#
#     def get(self, request, group_id):
#         group = Group.objects.get(pk=group_id)
#         serializer = StudentSerializer(group.students.all(), many=True)
#         return Response({'students': serializer.data})


class ToAttend(generics.ListCreateAPIView):
    serializer_class = AttendancePerDayCreateUpdateSerializer
    queryset = AttendancePerDay.objects.all()

    def get_queryset(self):
        id = self.request.query_params.get('id')
        if id is not None:
            return AttendancePerDay.objects.filter(group_id=id)
        return AttendancePerDay.objects.all()
