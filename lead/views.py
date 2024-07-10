from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from gennis_platform.permission import IsAdminOrReadOnly
from .serializers import (Lead, LeadSerializer,LeadCall,LeadCallSerializer)


class CreateLeadList(generics.ListCreateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    # permission_classes = (
    #     IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)


class LeadRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    # permission_classes = (
    #     IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)
    #

class CreateLeadCallList(generics.ListCreateAPIView):
    queryset = LeadCall.objects.all()
    serializer_class = LeadCallSerializer
    def get_queryset(self):
        queryset = LeadCall.objects.all()
        lead_id = self.request.query_params.get('lead_id', None)
        if lead_id is not None:
            queryset = queryset.filter(lead_id=lead_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save()
    # permission_classes = (
    #     IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)


class LeadCallRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LeadCall.objects.all()
    serializer_class = LeadCallSerializer
    # permission_classes = (
    #     IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)
    #

