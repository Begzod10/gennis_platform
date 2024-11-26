from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from attendances.models import AttendancePerMonth
from attendances.serializers import AttendancePerMonthSerializer


# Create your views here.


class DeleteAttendanceMonthApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AttendancePerMonth.objects.all()
    serializer_class = AttendancePerMonthSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"msg": "O'chirildi"}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        attendance = AttendancePerMonth.objects.filter(id=instance.id).first()
        attendance.old_money = attendance.total_debt
        attendance.total_debt = data['total_debt']
        attendance.save()

        return Response({'msg': 'Muvaffaqiyatli o\'zgartirildi'}, status=status.HTTP_200_OK)
