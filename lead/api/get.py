from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from lead.models import Lead, LeadCall
from lead.serializers import LeadListSerializer, LeadCallListSerializer


class LeadListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Lead.objects.all()
    serializer_class = LeadListSerializer

    def get(self, request, *args, **kwargs):

        queryset = Lead.objects.all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        serializer = LeadListSerializer(queryset, many=True)
        return Response(serializer.data)


class LeadRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Lead.objects.all()
    serializer_class = LeadListSerializer

    def retrieve(self, request, *args, **kwargs):
        lead = self.get_object()
        lead_data = self.get_serializer(lead).data
        return Response(lead_data)


class LeadCallListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = LeadCall.objects.all()
    serializer_class = LeadCallListSerializer

    def get_queryset(self):
        queryset = LeadCall.objects.all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        lead_id = self.request.query_params.get('lead_id', None)
        if lead_id is not None:
            queryset = queryset.filter(lead_id=lead_id)

        serializer = LeadCallListSerializer(queryset, many=True)
        return Response(serializer.data)

    def get(self, request, *args, **kwargs):

        queryset = LeadCall.objects.all()
        serializer = LeadCallListSerializer(queryset, many=True)
        return Response(serializer.data)


class LeadCallRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = LeadCall.objects.all()
    serializer_class = LeadCallListSerializer

    def retrieve(self, request, *args, **kwargs):
        lead_call = self.get_object()
        lead_call_data = self.get_serializer(lead_call).data
        return Response(lead_call_data)
