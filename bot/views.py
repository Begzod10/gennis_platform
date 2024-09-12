from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from students.models import Student
from django.db.models import Q
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.exceptions import AuthenticationFailed
from werkzeug.security import check_password_hash
from user.models import CustomUser


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
        username = request.data.get('username')
        password = request.data.get('password')
        user = CustomUser.objects.get(username=username)
        if user.password.startswith('sha256$'):
            if check_password_hash(user.password, password):
                new_password = make_password(password)
                user.password = new_password
                user.save()
                data = super().validate(request)
                refresh = self.get_token(self.user)
                data['refresh'] = str(refresh)
                data['access'] = str(refresh.access_token)
                return data
            else:
                raise AuthenticationFailed("No active account found with the given credentials")
        elif user.password.startswith('pbkdf2:sha256'):
            if check_password(password, user.password):
                new_password = make_password(password)
                user.password = new_password
                user.save()
                data = super().validate(request)
                refresh = self.get_token(self.user)
                data['refresh'] = str(refresh)
                data['access'] = str(refresh.access_token)
                return data
            else:
                raise AuthenticationFailed("No active account found with the given credentials")
        else:
            data = super().validate(request)
            refresh = self.get_token(self.user)
            data['refresh'] = str(refresh)
            data['access'] = str(refresh.access_token)
            return data
        return Response({'data': data})


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
