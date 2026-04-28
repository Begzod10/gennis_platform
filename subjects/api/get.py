from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from subjects.models import SubjectLevel
from subjects.serializers import SubjectLevelListSerializer


class LevelsForSubject(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    # queryset = SubjectLevel.objects.all()
    serializer_class = SubjectLevelListSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return SubjectLevel.objects.filter(subject_id=pk).all()


class SubjectLevelListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = SubjectLevel.objects.all()
    serializer_class = SubjectLevelListSerializer

    def get(self, request, *args, **kwargs):
        queryset = SubjectLevel.objects.all()
        serializer = SubjectLevelListSerializer(queryset, many=True)
        return Response(serializer.data)


class SubjectLevelRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = SubjectLevel.objects.all()
    serializer_class = SubjectLevelListSerializer

    def retrieve(self, request, *args, **kwargs):
        subject_level = self.get_object()
        subject_level_data = self.get_serializer(subject_level).data
        return Response(subject_level_data)
