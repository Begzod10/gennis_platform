from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from lead.models import Lead, LeadCall
from lead.serializers import LeadSerializer, LeadCallSerializer


class LeadCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Lead.objects.all()
    serializer_class = LeadSerializer


class LeadUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Lead.objects.all()
    serializer_class = LeadSerializer


class LeadDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Lead.objects.all()
    serializer_class = LeadSerializer


class LeadCallCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = LeadCall.objects.all()
    serializer_class = LeadCallSerializer


class LeadCallUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = LeadCall.objects.all()
    serializer_class = LeadCallSerializer


class LeadCallDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = LeadCall.objects.all()
    serializer_class = LeadCallSerializer
