import json
from datetime import datetime

from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rooms.models import Room
from students.models import StudentPayment, StudentHistoryGroups, StudentCharity, Student
from students.serializers import StudentPaymentListSerializer, StudentHistoryGroupsListSerializer, \
    StudentCharityListSerializer, StudentListSerializer
from subjects.models import Subject
from teachers.models import Teacher
from teachers.serializers import TeacherSerializerRead
from time_table.models import GroupTimeTable
from ..serializers_list import StudentPaymentListSerializerTest


class StudentRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Student.objects.all()
    serializer_class = StudentListSerializer

    def retrieve(self, request, *args, **kwargs):
        student = self.get_object()
        student_data = self.get_serializer(student).data
        return Response(student_data)


class StudentCharityListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = StudentCharity.objects.all()
    serializer_class = StudentCharityListSerializer

    def get_queryset(self, request, *args, **kwargs):

        student_id = self.request.query_params.get('student_id', None)
        if student_id is not None:
            queryset = StudentCharity.objects.filter(student_id=student_id)
        else:
            queryset = StudentCharity.objects.all()

        serializer = StudentCharityListSerializer(queryset, many=True)
        return Response(serializer.data)

    def get(self, request, *args, **kwargs):

        queryset = StudentCharity.objects.all()
        serializer = StudentCharityListSerializer(queryset, many=True)
        return Response(serializer.data)


class StudentCharityAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = StudentCharity.objects.all()
    serializer_class = StudentCharityListSerializer

    def retrieve(self, request, *args, **kwargs):
        student_charity = self.kwargs.get('pk')
        charity = StudentCharity.objects.filter(student=student_charity).first()
        student_charity_data = self.get_serializer(charity).data
        return Response(student_charity_data)


class StudentHistoryGroupsListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = StudentHistoryGroups.objects.all()
    serializer_class = StudentHistoryGroupsListSerializer

    def get(self, request, *args, **kwargs):
        queryset = StudentHistoryGroups.objects.all()

        serializer = StudentHistoryGroupsListSerializer(queryset, many=True)
        return Response(serializer.data)


class StudentHistoryGroupsAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = StudentHistoryGroups.objects.all()
    serializer_class = StudentHistoryGroupsListSerializer

    def retrieve(self, request, *args, **kwargs):
        student_history_groups = self.get_object()

        student_history_groups_data = self.get_serializer(student_history_groups, many=True).data

        return Response(student_history_groups_data)

    def get_object(self):
        user_id = self.kwargs.get('pk')
        return StudentHistoryGroups.objects.filter(student=user_id)


class StudentPaymentListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = StudentPayment.objects.all()
    serializer_class = StudentPaymentListSerializer

    def get(self, request, *args, **kwargs):
        queryset = StudentPayment.objects.filter(deleted=False, status=False,
                                                 branch=request.user.branch).all().order_by("-date")

        serializer = StudentPaymentListSerializerTest(queryset, many=True)
        return Response(serializer.data)


class StudentDeletedPaymentListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = StudentPayment.objects.all()
    serializer_class = StudentPaymentListSerializer

    def get(self, request, *args, **kwargs):
        queryset = StudentPayment.objects.filter(deleted=True).all()

        serializer = StudentPaymentListSerializer(queryset, many=True)
        return Response(serializer.data)


class StudentPaymentAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = StudentPayment.objects.all()
    serializer_class = StudentPaymentListSerializer

    def retrieve(self, request, *args, **kwargs):

        status = self.request.query_params.get('status', None)

        queryset = self.get_object()
        if status is not None:
            queryset = queryset.filter(deleted=status)

        serializer = StudentPaymentListSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_object(self):
        user_id = self.kwargs.get('pk')
        try:
            return StudentPayment.objects.filter(student_id=user_id).all()
        except StudentPayment.DoesNotExist:
            raise NotFound('Student payment not found for the given student_id')


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
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # location_id = branch_id
        location_id = self.request.query_params.get('branch')
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
            deleted_student_student__deleted=True,
            subject__student__isnull=False
        ).select_related('user').prefetch_related('subject', 'group_time_table').distinct()
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
                         and rt.start_time >= datetime.strptime(time_table['start_time'], "%H:%M").time()
                         and rt.end_time <= datetime.strptime(time_table['end_time'], "%H:%M").time()), None)
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
    permission_classes = [IsAuthenticated]

    serializer_class = StudentListSerializer

    def get_queryset(self):
        branch_id = self.request.query_params.get('branch')
        return Student.objects.filter(user__branch_id=branch_id, deleted_student_student__deleted=True,
                                      groups_student__isnull=True)


class StudentsForSubject(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = StudentListSerializer

    def get_queryset(self):
        subject_id = self.kwargs['subject_id']
        branch_id = self.kwargs['branch_id']
        return Student.objects.filter(subject__student__in=[subject_id], user__branch_id=branch_id)
