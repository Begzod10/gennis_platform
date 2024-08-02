from rest_framework import generics
from lead.serializers import LeadSerializer, LeadCallSerializer
from lead.models import Lead, LeadCall


class LeadCreateView(generics.CreateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer


class LeadUpdateView(generics.UpdateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer


class LeadDestroyView(generics.DestroyAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer


class LeadCallCreateView(generics.CreateAPIView):
    queryset = LeadCall.objects.all()
    serializer_class = LeadCallSerializer


class LeadCallUpdateView(generics.UpdateAPIView):
    queryset = LeadCall.objects.all()
    serializer_class = LeadCallSerializer


class LeadCallDestroyView(generics.DestroyAPIView):
    queryset = LeadCall.objects.all()
    serializer_class = LeadCallSerializer
