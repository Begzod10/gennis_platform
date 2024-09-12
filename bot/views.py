from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from students.models import Student
from django.db.models import Q
from user.models import CustomUser
from django.contrib.auth import authenticate


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


class get_user_with_username_and_password(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        tg_username = request.data.get('tg_username')
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            student = Student.objects.get(user=user)
            student.telegram_username = tg_username
            student.save()
            data = {'full_name': f"{user.name} {user.surname}"}
            return Response({'data': data, 'status': True})
        else:
            return Response({'data': 'Invalid username or password', 'status': False})


class get_table_with_student_username(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        student = Student.objects.filter(telegram_username=username).first()
        if student:
            groups = student.groups_student.all()
            print(groups)
            data = []
            for group in groups:
                data.append({
                    'group_name': group.name,
                    'subject': group.subject.name,
                    'level': group.level.name,
                    'teacher': [f"{teacher.user.name} {teacher.user.surname}" for teacher in group.teacher.all()],
                    'language': group.language.name if group.language else None
                })
            return Response({'table': data, 'status': True})
        else:
            return Response({'table': "Register error", 'status': False})


class get_user_with_passport_number(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        passport_number = request.data.get('passport_number')
        username = request.data.get('username')
        students = Student.objects.filter(
            Q(father_passport_number=passport_number) | Q(mother_passport_number=passport_number)
        ).order_by('pk').all()
        list = []
        if students:
            status = True
            for student in students:
                if student.father_passport_number == passport_number:
                    student.father_username = username
                else:
                    student.mother_username = username
                student.save()
                list.append({'full_name': student.user.name + ' ' + student.user.surname})
        else:
            status = False
        return Response({'status': status, 'students': list})
