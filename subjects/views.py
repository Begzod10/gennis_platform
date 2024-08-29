import requests
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from subjects.models import Subject, SubjectLevel
from subjects.serializers import SubjectSerializer, SubjectLevelSerializer
from user.functions.functions import check_auth
from permissions.functions.CheckUserPermissions import check_user_permissions


class DataSyncView(APIView):
    def post(self, request):
        data_type = request.data.get('type')
        if data_type == "subject":
            subjects = request.data.get('subject', [])
            for subject_data in subjects:
                subject, created = Subject.objects.get_or_create(
                    classroom_id=subject_data['id'],
                    defaults={
                        'name': subject_data['name'],
                        'ball_number': 2,
                    }
                )
                if not created:
                    subject.disabled = subject_data.get('disabled', subject.disabled)
                    subject.classroom_id = subject_data['id']
                    subject.name = subject_data['name']
                    subject.save()

        elif data_type == "levels":
            levels = request.data.get('levels', [])
            for level_data in levels:
                subject_data = level_data.get('subject')
                subject, _ = Subject.objects.get_or_create(
                    classroom_id=subject_data['id'],
                    defaults={
                        'name': subject_data['name'],
                        'ball_number': 2,
                    }
                )
                subject.disabled = subject_data.get('disabled', subject.disabled)
                subject.classroom_id = subject_data['id']
                subject.name = subject_data['name']
                subject.save()

                level, created = SubjectLevel.objects.get_or_create(
                    classroom_id=level_data['id'],
                    subject=subject,
                    defaults={
                        'name': level_data['name'],
                    }
                )
                if not created:
                    level.disabled = level_data.get('disabled', level.disabled)
                    level.classroom_id = level_data['id']
                    level.name = level_data['name']
                    level.save()

        return Response({"msg": "Zo'r"}, status=status.HTTP_200_OK)



class CreateSubjectList(generics.ListCreateAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['subject']
        permissions = check_user_permissions(user, table_names)

        queryset = Subject.objects.all()
        serializer = SubjectSerializer(queryset, many=True)
        return Response({'subjects': serializer.data, 'permissions': permissions})


class SubjectRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['subject']
        permissions = check_user_permissions(user, table_names)
        subject = self.get_object()
        subject_data = self.get_serializer(subject).data
        return Response({'subject': subject_data, 'permissions': permissions})
