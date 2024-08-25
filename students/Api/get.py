from datetime import datetime
import json
from rest_framework import generics, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from permissions.functions.CheckUserPermissions import check_user_permissions
from rooms.models import Room
from students.models import StudentPayment, StudentHistoryGroups, StudentCharity, Student
from students.serializers import StudentPaymentListSerializer, StudentHistoryGroupsListSerializer, \
    StudentCharityListSerializer, StudentListSerializer
from subjects.serializers import SubjectSerializer
from time_table.models import GroupTimeTable
from user.functions.functions import check_auth
from teachers.models import Teacher
from teachers.serializers import TeacherSerializerRead
from system.models import System
from subjects.models import Subject


class StudentRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentListSerializer

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['student', 'subject', 'customuser']
        permissions = check_user_permissions(user, table_names)
        student = self.get_object()
        student_data = self.get_serializer(student).data
        return Response({'student': student_data, 'permissions': permissions})


class StudentCharityListAPIView(generics.ListAPIView):
    queryset = StudentCharity.objects.all()
    serializer_class = StudentCharityListSerializer

    def get_queryset(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['studentcharity', 'student', 'group']
        permissions = check_user_permissions(user, table_names)
        student_id = self.request.query_params.get('student_id', None)
        if student_id is not None:
            queryset = StudentCharity.objects.filter(student_id=student_id)
        else:
            queryset = StudentCharity.objects.all()
        serializer = StudentCharityListSerializer(queryset, many=True)
        return Response({'studentcharitys': serializer.data, 'permissions': permissions})

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['studentcharity', 'student', 'group']
        permissions = check_user_permissions(user, table_names)

        queryset = StudentCharity.objects.all()
        serializer = StudentCharityListSerializer(queryset, many=True)
        return Response({'studentcharitys': serializer.data, 'permissions': permissions})


class StudentCharityAPIView(generics.RetrieveAPIView):
    queryset = StudentCharity.objects.all()
    serializer_class = StudentCharityListSerializer

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['studentcharity', 'student', 'group']
        permissions = check_user_permissions(user, table_names)
        student_charity = self.get_object()
        student_charity_data = self.get_serializer(student_charity).data
        return Response({'studentcharity': student_charity_data, 'permissions': permissions})


class StudentHistoryGroupsListAPIView(generics.ListAPIView):
    queryset = StudentHistoryGroups.objects.all()
    serializer_class = StudentHistoryGroupsListSerializer

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['studenthistorygroups', 'student', 'group', 'teacher']
        permissions = check_user_permissions(user, table_names)

        queryset = StudentHistoryGroups.objects.all()
        serializer = StudentHistoryGroupsListSerializer(queryset, many=True)
        return Response({'studenthistorygroups': serializer.data, 'permissions': permissions})


class StudentHistoryGroupsAPIView(generics.RetrieveAPIView):
    queryset = StudentHistoryGroups.objects.all()
    serializer_class = StudentHistoryGroupsListSerializer

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['studenthistorygroups', 'student', 'group', 'teacher']
        permissions = check_user_permissions(user, table_names)
        student_history_groups = self.get_object()
        student_history_groups_data = self.get_serializer(student_history_groups).data
        return Response({'studenthistorygroup': student_history_groups_data, 'permissions': permissions})


class StudentPaymentListAPIView(generics.ListAPIView):
    queryset = StudentPayment.objects.all()
    serializer_class = StudentPaymentListSerializer

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['studentpayment', 'student', 'paymenttypes']
        permissions = check_user_permissions(user, table_names)

        queryset = StudentPayment.objects.all()
        serializer = StudentPaymentListSerializer(queryset, many=True)
        return Response({'branches': serializer.data, 'permissions': permissions})


class StudentPaymentAPIView(generics.RetrieveAPIView):
    queryset = StudentPayment.objects.all()
    serializer_class = StudentPaymentListSerializer

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['branch', 'location']
        permissions = check_user_permissions(user, table_names)
        create_branches = self.get_object()
        create_branches_data = self.get_serializer(create_branches).data
        return Response({'branches': create_branches_data, 'permissions': permissions})


# class FilteredStudentsListView(mixins.ListModelMixin, generics.GenericAPIView):
#     serializer_class = SubjectSerializer
#
#     def get_queryset(self):
#         location_id = self.kwargs['branch_id']
#         students = Student.objects.filter(
#             user__branch_id=location_id,
#             user__isnull=False,
#             subject__isnull=False,
#             deleted_student_student_new__isnull=True
#         ).select_related('user').prefetch_related('subject').order_by('-id')
#
#         subjects_with_students = {}
#         i = 0
#         for student in students:
#             i += 1
#             for subject in student.subject.all():
#                 if subject.id not in subjects_with_students:
#                     subjects_with_students[subject.id] = {
#                         "id": subject.id,
#                         "name": subject.name,
#                         "students": []
#                     }
#                 subjects_with_students[subject.id]["students"].append(StudentListSerializer(student).data)
#         return list(subjects_with_students.values())
#
#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)


class FilteredStudentsListView(APIView):
    def post(self, request, branch_id):
        # location_id = branch_id
        location_id = self.request.query_params.get('branch')
        print(location_id)
        teachers_list = []

        subjects = Subject.objects.filter(student__subject__student__isnull=False).all()

        subjects_with_students = {
            subject.id: {
                "id": subject.id,
                "name": subject.name,
                "students": [],
                "subject_status": False
            }
            for subject in subjects
        }

        errors = {
            'rooms': [],
        }

        time_tables = json.loads(request.body)

        students = Student.objects.filter(
            user__branch_id=location_id,
            deleted_student_student__isnull=True,
            subject__student__isnull=False
        ).select_related('user').prefetch_related('subject', 'group_time_table').distinct()
        print(students.count())
        room_ids = [t['room'] for t in time_tables]
        rooms = Room.objects.filter(id__in=room_ids)

        room_time_tables = GroupTimeTable.objects.filter(
            week_id__in=[t['week'] for t in time_tables],
            room__in=rooms,
            start_time__gte=min([t['start_time'] for t in time_tables]),
            end_time__lte=max([t['end_time'] for t in time_tables])
        )

        teachers = Teacher.objects.filter(user__branch_id=location_id).prefetch_related('group_time_table')

        for student in students:
            student_data = StudentListSerializer(student).data
            should_add_student = False

            for time_table in time_tables:
                room = next((r for r in rooms if r.id == time_table['room']), None)

                if room:
                    room_time_table = next(
                        (rt for rt in room_time_tables if rt.room == room and rt.week_id == time_table['week']
                         and rt.start_time >= datetime.strptime(time_table['start_time'], "%H:%M")
                         and rt.end_time <= datetime.strptime(time_table['end_time'], "%H:%M")), None)
                    if room_time_table:
                        errors['rooms'].append(
                            f'Bu voxta {room.name} xonasida {room_time_table.group.name}ni darsi bor')

                time_table_st = student.group_time_table.filter(
                    week_id=time_table['week'],
                    start_time__gte=time_table['start_time'],
                    end_time__lte=time_table['end_time']
                ).first()

                if time_table_st:
                    student_data['extra_info'] = {
                        'status': False,
                        'reason': f"{student.user.name} {student.user.surname} o'quvchini {time_table.group.name} guruhida darsi bor"
                    }
                else:
                    student_data['extra_info'] = {
                        'status': True,
                        'reason': ''
                    }

                if not should_add_student:
                    should_add_student = True

            if should_add_student:
                for subject in student.subject.all():
                    subjects_with_students[subject.id]["students"].append(student_data)
                    subjects_with_students[subject.id]["subject_status"] = True

        for teacher in teachers:
            teacher_data = TeacherSerializerRead(teacher).data
            time_table_tch = teacher.group_time_table.filter(
                week_id=time_table['week'],
                start_time__gte=time_table['start_time'],
                end_time__lte=time_table['end_time']
            ).first()

            if time_table_tch:
                teacher_data['extra_info'] = {
                    'status': False,
                    'reason': f"{teacher.user.name} {teacher.user.surname} o'quvchini {time_table.group.name} guruhida darsi bor"
                }
            else:
                teacher_data['extra_info'] = {
                    'status': True,
                    'reason': ''
                }

            if not teacher_data in teachers_list:
                teachers_list.append(teacher_data)

        return Response({
            'subjects_with_students': subjects_with_students.values(),
            'teachers': teachers_list,
            'errors': errors
        })


class SchoolStudents(generics.ListAPIView):
    serializer_class = StudentListSerializer

    def get_queryset(self):
        system = System.objects.get(name='School')
        return Student.objects.filter(system_id=system.pk)


class StudentsForSubject(generics.ListAPIView):
    serializer_class = StudentListSerializer

    def get_queryset(self):
        subject_id = self.kwargs['subject_id']
        branch_id = self.kwargs['branch_id']
        return Student.objects.filter(subject__student__in=[subject_id], user__branch_id=branch_id)
