from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from students.models import Student
from django.db.models import Q
from django.contrib.auth import authenticate
from time_table.models import GroupTimeTable, WeekDays
from attendances.models import AttendancePerMonth
import datetime
from user.models import CustomUser
from school_time_table.models import ClassTimeTable


class get_user_with_telegram_username(APIView):

    def post(self, request, *args, **kwargs):
        telegram_id = request.data.get('telegram_id')
        students = Student.objects.filter(
            Q(father_telegram_id=telegram_id) | Q(mother_telegram_id=telegram_id)
        ).order_by('pk').all()
        if students:
            list = []
            for student in students:
                list.append({
                    'full_name': f"{student.user.name} {student.user.surname}",
                    'username': student.user.username
                })
            return Response({'status': True, 'students': list})
        else:
            return Response({'status': False})


class get_attendances_with_student_username(APIView):

    def post(self, request, *args, **kwargs):
        telegram_id = request.data.get('telegram_id')
        student = Student.objects.filter(telegram_id=telegram_id).first()
        parent = False
        if not student:
            student = Student.objects.filter(
                Q(father_telegram_id=telegram_id) | Q(mother_telegram_id=telegram_id) and
                Q(father_choose=True) | Q(mother_choose=True)
            ).first()
            parent = True
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
            return Response({'attendances': data, 'balance': balance, 'status': True, 'parent': parent})
        else:
            return Response({'table': "Serverda hatolik", 'status': False, 'parent': parent})


class check_student(APIView):
    def post(self, request, *args, **kwargs):
        telegram_id = request.data.get('telegram_id')
        student = Student.objects.filter(telegram_id=telegram_id).first()

        if student:
            return Response({'status': True, 'student': f"{student.user.name} {student.user.surname}"})
        else:
            return Response({'status': False})


class parent_active(APIView):
    def post(self, request, *args, **kwargs):
        telegram_id = request.data.get('telegram_id')
        student = Student.objects.filter(
            Q(father_telegram_id=telegram_id) | Q(mother_telegram_id=telegram_id) and Q(mother_choose=True) | Q(
                father_choose=True)
        ).first()
        if student:
            return Response({'status': True})
        else:
            return Response({'status': False})


class parent_choose(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        telegram_id = request.data.get('telegram_id')
        user = CustomUser.objects.filter(username=username).first()
        student = Student.objects.filter(user=user).first()
        students = Student.objects.filter(
            Q(father_telegram_id=telegram_id) | Q(mother_telegram_id=telegram_id)
        ).order_by('pk').all()
        for item in students:
            if item.father_telegram_id == telegram_id:
                item.father_choose = False
                item.save()
            else:
                item.mother_choose = False
                item.save()
        if student:
            if student.father_telegram_id == telegram_id:
                student.father_choose = True
            else:
                student.mother_choose = True
            student.save()
            return Response({'status': True, 'student': f"{user.name} {user.surname}"})
        else:
            return Response({'status': False})


class logout_parent(APIView):
    def post(self, request, *args, **kwargs):
        telegram_id = request.data.get('telegram_id')
        students = Student.objects.filter(
            Q(father_telegram_id=telegram_id) | Q(mother_telegram_id=telegram_id)
        ).order_by('pk').all()
        for item in students:
            if item.father_telegram_id == telegram_id:
                item.father_choose = False
                item.father_telegram_id = None
                item.save()
            else:
                item.mother_choose = False
                item.mother_telegram_id = None
                item.save()
        return Response({'status': True})


class logout_student(APIView):
    def post(self, request, *args, **kwargs):
        telegram_id = request.data.get('telegram_id')
        student = Student.objects.filter(telegram_id=telegram_id).first()
        if student:
            student.telegram_id = None
            student.save()
            return Response({'status': True})
        else:
            return Response({'status': False})


class get_user_with_username_and_password(APIView):

    def post(self, request, *args, **kwargs):
        telegram_id = request.data.get('telegram_id')
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            student = Student.objects.get(user=user)
            student.telegram_id = telegram_id
            student.save()
            data = {'full_name': f"{user.name} {user.surname}"}
            return Response({'data': data, 'status': True})
        else:
            return Response({'data': 'Invalid username or password', 'status': False})


class get_table_week_with_student_username(APIView):
    def post(self, request, *args, **kwargs):
        telegram_id = request.data.get('telegram_id')
        student = Student.objects.filter(telegram_id=telegram_id).first()
        parent = False
        if not student:
            student = Student.objects.filter(
                Q(father_telegram_id=telegram_id) | Q(mother_telegram_id=telegram_id) and
                Q(father_choose=True) | Q(mother_choose=True)
            ).first()
            parent = True
        if student:
            groups = student.groups_student.all()
            data = []
            if groups:
                for group in groups:
                    week = WeekDays.objects.get(order=request.data.get('day'))
                    group_time_table = ClassTimeTable.objects.filter(group=group, week=week).first()
                    if group_time_table:
                        subject = None
                        if group.subject:
                            subject = group.subject.name
                        level = None
                        if group.level:
                            level = group.level.name
                        data.append({
                            'group_name': group.name,
                            'start_time': group_time_table.hours.start_time,
                            'end_time': group_time_table.hours.end_time,
                            'room': group_time_table.room.name,
                            'subject': subject,
                            'level': level,
                            'teacher': [f"{teacher.user.name} {teacher.user.surname}" for teacher in
                                        group.teacher.all()],
                            'language': group.language.name if group.language else None
                        })
                if data:
                    return Response({'table': data, 'day': week.name_uz, 'status': True, 'parent': parent})
                else:
                    return Response({'table': "Bu kunda dars yo'q", 'status': False, 'parent': parent})
            else:
                return Response({'table': "Dars yo'q", 'status': False, 'parent': parent})
        else:
            return Response({'table': "Serverda hatolik", 'status': False})


class get_table_with_student_username(APIView):
    def post(self, request, *args, **kwargs):
        telegram_id = request.data.get('telegram_id')
        student = Student.objects.filter(telegram_id=telegram_id).first()
        parent = False

        if not student:
            student = Student.objects.filter(
                Q(father_telegram_id=telegram_id) | Q(mother_telegram_id=telegram_id) and
                Q(father_choose=True) | Q(mother_choose=True)
            ).first()
            parent = True
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
                        subject = None
                        if group.subject:
                            subject = group.subject.name
                        level = None
                        if group.level:
                            level = group.level.name
                        data.append({
                            'group_name': group.name,
                            'start_time': group_time_table.hours.start_time,
                            'end_time': group_time_table.hours.end_time,
                            'room': group_time_table.room.name,
                            'subject': subject,
                            'level': level,
                            'teacher': [f"{teacher.user.name} {teacher.user.surname}" for teacher in
                                        group.teacher.all()],
                            'language': group.language.name if group.language else None
                        })
                if data:
                    return Response({'table': data, 'status': True, 'parent': parent})
                else:
                    return Response({'table': "Bugun dars yo'q", 'status': False, 'parent': parent})
            else:
                return Response({'table': "Dars yo'q", 'status': False, 'parent': parent})
        else:
            return Response({'table': "Serverda hatolik", 'status': False})


class get_user_with_passport_number(APIView):

    def post(self, request, *args, **kwargs):
        passport_number = request.data.get('passport_number')
        telegram_id = request.data.get('telegram_id')
        students = Student.objects.filter(
            Q(father_passport_number=passport_number) | Q(mother_passport_number=passport_number)
        ).order_by('pk').all()
        list = []
        if students:
            status = True
            for student in students:
                if student.father_passport_number == passport_number:
                    student.father_telegram_id = telegram_id
                else:
                    student.mother_telegram_id = telegram_id
                student.save()
                list.append({
                    'full_name': f"{student.user.name} {student.user.surname}",
                    'username': student.user.username
                })
        else:
            status = False
        return Response({'status': status, 'students': list})
