from rest_framework import generics, mixins
from rest_framework.response import Response

from permissions.functions.CheckUserPermissions import check_user_permissions
from students.models import StudentPayment, StudentHistoryGroups, StudentCharity, Student
from students.serializers import StudentPaymentListSerializer, StudentHistoryGroupsListSerializer, \
    StudentCharityListSerializer, StudentListSerializer
from subjects.serializers import SubjectSerializer
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


class FilteredStudentsListView(mixins.ListModelMixin, generics.GenericAPIView):
    serializer_class = SubjectSerializer

    def get_queryset(self):
        location_id = self.kwargs['branch_id']
        students = Student.objects.filter(
            user__branch_id=location_id,
            user__isnull=False,
            subject__isnull=False,
            deleted_student_student_new__isnull=True
        ).select_related('user').prefetch_related('subject').order_by('-id')

        subjects_with_students = {}
        i=0
        for student in students:
            i+=1
            print(StudentListSerializer(student).data)
            for subject in student.subject.all():
                if subject.id not in subjects_with_students:
                    subjects_with_students[subject.id] = {
                        "id": subject.id,
                        "name": subject.name,
                        "students": []
                    }
                subjects_with_students[subject.id]["students"].append(StudentListSerializer(student).data)
        return list(subjects_with_students.values())

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
