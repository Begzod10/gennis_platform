from rest_framework import generics
from subjects.serializers import SubjectLevelSerializer
from subjects.models import SubjectLevel


class SubjectLevelCreateView(generics.CreateAPIView):
    queryset = SubjectLevel.objects.all()
    serializer_class = SubjectLevelSerializer


class SubjectLevelUpdateView(generics.UpdateAPIView):
    queryset = SubjectLevel.objects.all()
    serializer_class = SubjectLevelSerializer


class SubjectLevelDestroyView(generics.DestroyAPIView):
    queryset = SubjectLevel.objects.all()
    serializer_class = SubjectLevelSerializer
