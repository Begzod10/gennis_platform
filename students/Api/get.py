import json

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from permissions.functions.CheckUserPermissions import check_user_permissions
from rooms.models import Room
from students.models import StudentPayment, StudentHistoryGroups, StudentCharity, Student
from students.serializers import StudentPaymentListSerializer, StudentHistoryGroupsListSerializer, \
    StudentCharityListSerializer, StudentListSerializer
from subjects.models import Subject
from system.models import System
from teachers.models import Teacher
from teachers.serializers import TeacherSerializerRead
from user.functions.functions import check_auth


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
            location_id = self.request.query_params.get('location_id', None)
            branch_id = self.request.query_params.get('branch_id', None)

            if branch_id is not None:
                queryset = queryset.filter(branch_id=branch_id)
            if location_id is not None:
                queryset = queryset.filter(location_id=location_id)
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
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
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

        student_history_groups_data = self.get_serializer(student_history_groups, many=True).data

        return Response({'studenthistorygroup': student_history_groups_data, 'permissions': permissions})

    def get_object(self):
        user_id = self.kwargs.get('pk')
        return StudentHistoryGroups.objects.filter(student=user_id)


class StudentPaymentListAPIView(generics.ListAPIView):
    queryset = StudentPayment.objects.all()
    serializer_class = StudentPaymentListSerializer

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['studentpayment', 'student', 'paymenttypes']
        permissions = check_user_permissions(user, table_names)

        queryset = StudentPayment.objects.filter(deleted=False).all()[:200]
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        serializer = StudentPaymentListSerializer(queryset, many=True)
        return Response({'branches': serializer.data, 'permissions': permissions})


class StudentDeletedPaymentListAPIView(generics.ListAPIView):
    queryset = StudentPayment.objects.all()
    serializer_class = StudentPaymentListSerializer

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['studentpayment', 'student', 'paymenttypes']
        permissions = check_user_permissions(user, table_names)

        queryset = StudentPayment.objects.filter(deleted=True).all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
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
        location_id = branch_id
        teachers_list = []
        subjects_with_students = {}
        errors = {'rooms': [], }
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
            subject__isnull=False
        )
        for time_table in time_tables:

            room = Room.objects.get(id=time_table['room'])
            room_time_table = room.grouptimetable_set.filter(week_id=time_table['week'],
                                                             start_time__gte=time_table['start_time'],
                                                             end_time__lte=time_table['end_time']).first()
            if room_time_table:
                errors['rooms'].append(f'Bu voxta {room.name} xonasida {room_time_table.group.name}ni  darsi bor')

            students = Student.objects.filter(user__branch_id=location_id,  # user__isnull=False,
                                              subject__student__isnull=False  # deleted_student_student_new__isnull=True
                                              )
            for student in students:
                student_data = StudentListSerializer(student).data
                time_table_st = student.group_time_table.filter(week_id=time_table['week'],
                                                                start_time__gte=time_table['start_time'],
                                                                end_time__lte=time_table['end_time']).first()
                if time_table_st:
                    student_data['extra_info'] = {'status': False,
                                                  'reason': f"{student.user.name} {student.user.surname} o'quvchini {time_table.group.name} guruhida darsi bor"}
                else:
                    student_data['extra_info'] = {'status': True, 'reason': ''}
                for subject in student.subject.all():
                    if subject.id not in subjects_with_students:
                        subjects_with_students[subject.id] = {"id": subject.id, "name": subject.name, "students": []}
                    if not student_data in subjects_with_students[subject.id]["students"]:
                        subjects_with_students[subject.id]["students"].append(student_data)
                    subjects_with_students[subject.id]["students"].append(student_data)
                    subjects_with_students[subject.id]["subject_status"] = True
            teachers = Teacher.objects.filter(user__branch_id=location_id)
            for teacher in teachers:
                teacher_data = TeacherSerializerRead(teacher).data
                time_table_tch = teacher.group_time_table.filter(week_id=time_table['week'],
                                                                 start_time__gte=time_table['start_time'],
                                                                 end_time__lte=time_table['end_time'])
                if time_table_tch:
                    teacher_data['extra_info'] = {'status': False,
                                                  'reason': f"{teacher.user.name} {teacher.user.surname} o'quvchini {time_table.group.name} guruhida darsi bor"}
                else:
                    teacher_data['extra_info'] = {'status': True, 'reason': ''}
                if not teacher_data in teachers_list:
                    teachers_list.append(teacher_data)
        return Response(
            {'subjects_with_students': subjects_with_students.values(), 'teachers': teachers_list, 'errors': errors})


class SchoolStudents(generics.ListAPIView):
    serializer_class = StudentListSerializer

    def get_queryset(self):
        system = System.objects.get(name='School')
        return Student.objects.filter(system_id=system.pk)
