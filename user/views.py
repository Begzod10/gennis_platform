import jwt
from django.conf import settings
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from user.serializers import CustomUserSerializer
from .serializers import UserSalaryUpdateSerializers, UserSalary
from branch.models import Branch
from teachers.models import Teacher, TeacherAttendance
from .models import CustomUser as User
from students.models import Student
from attendances.models import StudentDailyAttendance, StudentMonthlySummary


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def get_user_from_refresh_token(self, refresh_token):
        try:
            decoded_data = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )
            user_id = decoded_data.get("user_id")

            CustomUser = get_user_model()
            user = CustomUser.objects.get(id=user_id)
            return user, None
        except jwt.ExpiredSignatureError:
            return None, {"detail": "Refresh token has expired."}
        except jwt.InvalidTokenError:
            return None, {"detail": "Invalid refresh token."}
        except ObjectDoesNotExist:
            return None, {"detail": "User not found."}

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        user, auth_error = self.get_user_from_refresh_token(refresh_token)
        if auth_error:
            return Response(auth_error, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        user_serializer = CustomUserSerializer(user)
        response_data = user_serializer.data
        # response_data.update({
        #     "access": str(serializer.validated_data.get('access')),
        #     "refresh_token": str(RefreshToken.for_user(user)),
        # })
        return Response({"user": response_data, "access": str(serializer.validated_data.get('access')),
                         "refresh_token": str(RefreshToken.for_user(user)), },
                        status=status.HTTP_200_OK)


class UserSalaryUpdateView(generics.UpdateAPIView):
    serializer_class = UserSalaryUpdateSerializers
    queryset = UserSalary.objects.all()


class UserFaceIdView(APIView):
    def post(self, request, *args, **kwargs):
        face_id = request.data.get('id')
        branch_id = request.data.get('branch_id')
        entry_time = request.data.get('entry_time')
        leave_time = request.data.get('leave_time')

        # Validate required fields
        if not all([face_id, branch_id, entry_time]):
            return Response(
                {'error': 'Missing required fields: id, branch_id, entry_time'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Parse datetime
        date_obj = parse_datetime(entry_time)
        if not date_obj:
            return Response(
                {'error': 'Invalid entry_time format'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Make timezone aware
        tz = timezone.get_current_timezone()
        if timezone.is_naive(date_obj):
            date_obj = timezone.make_aware(date_obj, tz)
        else:
            date_obj = date_obj.astimezone(tz)

        # Extract date components
        day = date_obj.date()
        year = date_obj.year
        month = date_obj.month

        # try:
            # Get branch
        branch = Branch.objects.get(id=branch_id)

        # Get user
        user = User.objects.get(face_id=face_id, branch_id=branch.id)

        # Try to get teacher
        teacher = None
        try:
            teacher = Teacher.objects.get(user_id=user.id)
        except Teacher.DoesNotExist:
            pass

        # Try to get student
        student = None
        try:
            student = Student.objects.get(user_id=user.id)
        except Student.DoesNotExist:
            pass

        # If neither teacher nor student found
        if not teacher and not student:
            return Response(
                {'error': 'User is neither a teacher nor a student'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Handle teacher attendance
        if teacher:
            # Parse leave_time if provided
            leave_time_obj = None
            if leave_time:
                leave_time_obj = parse_datetime(leave_time)
                if leave_time_obj:
                    if timezone.is_naive(leave_time_obj):
                        leave_time_obj = timezone.make_aware(leave_time_obj, tz)
                    else:
                        leave_time_obj = leave_time_obj.astimezone(tz)

            teacher_attendance, created = TeacherAttendance.objects.get_or_create(
                teacher=teacher,
                day=day,
                entry_time__date=day,
                defaults={
                    'entry_time': date_obj,
                    'leave_time': leave_time_obj,
                    'status': True,
                    'system': branch.location.system
                }
            )

            # Update if already exists
            if not created:
                if not teacher_attendance.entry_time:
                    teacher_attendance.entry_time = date_obj
                if leave_time_obj:
                    teacher_attendance.leave_time = leave_time_obj
                teacher_attendance.status = True
                teacher_attendance.save()

        # Handle student attendance
        if student:
            if not student.groups_student.exists():
                return Response(
                    {'error': 'Student has no assigned group'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get or create monthly summary
            summary, created = StudentMonthlySummary.objects.get_or_create(
                student=student,
                group=student.groups_student.first(),  # Get first group
                year=year,
                month=month,
                defaults={"stats": {}}
            )

            status_present = True

            # Get or create daily attendance
            daily, created = StudentDailyAttendance.objects.get_or_create(
                monthly_summary=summary,
                day=day,
                defaults={
                    "status": status_present,
                    "entry_time": date_obj,
                    "leave_time": parse_datetime(leave_time) if leave_time else None,
                }
            )

            # Update if already exists
            if not created:
                daily.status = status_present
                if not daily.entry_time:
                    daily.entry_time = date_obj
                if leave_time:
                    leave_time_obj = parse_datetime(leave_time)
                    if leave_time_obj:
                        if timezone.is_naive(leave_time_obj):
                            leave_time_obj = timezone.make_aware(leave_time_obj, tz)
                        daily.leave_time = leave_time_obj
                daily.save()

        # Return response
        response_data = {'success': True}
        if teacher:
            response_data['teacher_face_id'] = teacher.user.face_id
        if student:
            response_data['student_face_id'] = student.user.face_id

        return Response(response_data, status=status.HTTP_200_OK)

        # except Branch.DoesNotExist:
        #     return Response(
        #         {'error': 'Branch not found'},
        #         status=status.HTTP_404_NOT_FOUND
        #     )
        # except User.DoesNotExist:
        #     return Response(
        #         {'error': 'User with this face_id not found in this branch'},
        #         status=status.HTTP_404_NOT_FOUND
        #     )
        # except Exception as e:
        #     return Response(
        #         {'error': str(e)},
        #         status=status.HTTP_500_INTERNAL_SERVER_ERROR
        #     )
