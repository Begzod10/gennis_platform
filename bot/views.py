from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from students.models import Student
from django.db.models import Q


class get_user_with_telegram_username(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        students = Student.objects.filter(
            Q(father_username=username) | Q(mother_username=username)
        ).order_by('pk').all()
        if students:
            status = True
        else:
            status = False
        return Response({'status': status})


class get_user_with_passport_number(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        passport_number = request.data.get('passport_number')
        username = request.data.get('username')
        students = Student.objects.filter(
            Q(father_passport_number=passport_number) | Q(mother_passport_number=passport_number)
        ).order_by('pk').all()
        if students:
            status = True
            for student in students:
                if student.father_passport_number == passport_number:
                    student.father_username = username
                else:
                    student.mother_username = username
                student.save()
        else:
            status = False
        return Response({'status': status})
