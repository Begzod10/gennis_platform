from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from students.models import Student
from django.db.models import Q
from user.models import CustomUser
from django.contrib.auth import authenticate
from time_table.models import GroupTimeTable, WeekDays
from attendances.models import AttendancePerMonth
import datetime


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


class get_attendances_with_student_username(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        student = Student.objects.filter(telegram_username=username).first()
        if student:
            attendances = AttendancePerMonth.objects.filter(student=student, status=False).all()
            data = []
            for attendance in attendances:
                data.append({
                    'month_date': attendance.month_date,
                    'total_debt': attendance.total_debt,
                    'remaining_debt': attendance.remaining_debt,
                    'payment': attendance.payment,
                    'group': attendance.group.name,
                })
            balance = 0
            for payment in attendances:
                balance += payment.payment
            for remaining_debt in attendances:
                balance -= remaining_debt.remaining_debt
            return Response({'attendances': data, 'balance': balance, 'status': True})
        else:
            return Response({'table': "Serverda hatolik", 'status': False})


class check_student(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        student = Student.objects.filter(telegram_username=username).first()
        if student:
            return Response({'status': True, 'student': f"{student.user.name} {student.user.surname}"})
        else:
            return Response({'status': False})


class logout_student(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        student = Student.objects.filter(telegram_username=username).first()
        if student:
            student.telegram_username = None
            student.save()
            return Response({'status': True})
        else:
            return Response({'status': False})


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


class get_table_week_with_student_username(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        student = Student.objects.filter(telegram_username=username).first()
        if student:
            groups = student.groups_student.all()
            print(groups)
            data = []
            return Response({'table': data, 'status': True})
        else:
            return Response({'table': "Serverda hatolik", 'status': False})


class get_table_with_student_username(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        student = Student.objects.filter(telegram_username=username).first()
        if student:
            groups = student.groups_student.all()
            data = []
            if groups:
                for group in groups:
                    today = datetime.datetime.now()
                    name_en = today.strftime("%A")
                    week = WeekDays.objects.get(name_en=name_en)
                    group_time_table = GroupTimeTable.objects.filter(group=group, week=week).first()
                    if group_time_table:
                        data.append({
                            'group_name': group.name,
                            'start_time': group_time_table.start_time,
                            'end_time': group_time_table.end_time,
                            'room': group_time_table.room.name,
                            'subject': group.subject.name,
                            'level': group.level.name,
                            'teacher': [f"{teacher.user.name} {teacher.user.surname}" for teacher in
                                        group.teacher.all()],
                            'language': group.language.name if group.language else None
                        })
                    else:
                        return Response({'table': "Bugun dars yo'q", 'status': False})
                return Response({'table': data, 'status': True})
            else:
                return Response({'table': "Dars yo'q", 'status': False})
        else:
            return Response({'table': "Serverda hatolik", 'status': False})


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
