from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from subjects.models import SubjectLevel
from subjects.serializers import SubjectLevelSerializer


class SubjectLevelCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = SubjectLevel.objects.all()
    serializer_class = SubjectLevelSerializer


class SubjectLevelUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = SubjectLevel.objects.all()
    serializer_class = SubjectLevelSerializer


class SubjectLevelDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = SubjectLevel.objects.all()
    serializer_class = SubjectLevelSerializer
