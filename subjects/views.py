import requests
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from subjects.models import Subject, SubjectLevel
from subjects.serializers import SubjectSerializer, SubjectLevelSerializer
from user.functions.functions import check_auth
from permissions.functions.CheckUserPermissions import check_user_permissions


class SyncSubjectsAndLevelsView(APIView):
    def get(self, request, *args, **kwargs):
        subjects_url = 'http://192.168.68.100:5001/get_subjects/'
        level_url = 'http://192.168.68.100:5001/api/info_level_subject'
        try:
            # Fetch subjects data
            subjects_response = requests.get(subjects_url)
            subjects_response.raise_for_status()
            subjects_data = subjects_response.json().get('subjects', [])
            for subject_data in subjects_data:
                subject_name = subject_data.get('name')
                subject, created = Subject.objects.get_or_create(name=subject_name)
                level_response = requests.get(f"{level_url}/{subject_data.get('id')}")
                level_response.raise_for_status()
                level_data = level_response.json().get('levels', [])

                for level_info in level_data:
                    level_name = level_info.get('name')

                    SubjectLevel.objects.get_or_create(
                        name=level_name, subject_id=subject
                    )

            return Response({
                'message': 'Subjects and levels synchronized successfully.',
            }, status=status.HTTP_200_OK)

        except requests.exceptions.RequestException as e:
            return Response({'error': f'Error fetching data: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except (KeyError, ValueError, AttributeError) as e:
            return Response({'error': f'Error parsing data: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
