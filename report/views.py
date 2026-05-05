from rest_framework import viewsets

from .models import Report, AdminRequest, RequestComment
from .serializers import ReportSerializer, AdminRequestSerializer, RequestCommentSerializer


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer


class AdminRequestViewSet(viewsets.ModelViewSet):
    queryset = AdminRequest.objects.all()
    serializer_class = AdminRequestSerializer
    filterset_fields = ['branch', 'user', 'status']


class RequestCommentViewSet(viewsets.ModelViewSet):
    queryset = RequestComment.objects.all()
    serializer_class = RequestCommentSerializer
    filterset_fields = ['request', 'user']


