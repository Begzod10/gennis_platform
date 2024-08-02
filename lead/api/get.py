from rest_framework import generics
from lead.serializers import LeadListSerializer, LeadCallListSerializer
from lead.models import Lead, LeadCall
from user.functions.functions import check_auth
from rest_framework.response import Response
from permissions.functions.CheckUserPermissions import check_user_permissions


class LeadListAPIView(generics.ListAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadListSerializer

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)
        table_names = ['lead', 'branch', 'subject']
        permissions = check_user_permissions(user, table_names)

        queryset = Lead.objects.all()
        serializer = LeadListSerializer(queryset, many=True)
        return Response({'leads': serializer.data, 'permissions': permissions})


class LeadRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadListSerializer

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['lead', 'branch', 'subject']
        permissions = check_user_permissions(user, table_names)
        lead = self.get_object()
        lead_data = self.get_serializer(lead).data
        return Response({'lead': lead_data, 'permissions': permissions})


class LeadCallListAPIView(generics.ListAPIView):
    queryset = LeadCall.objects.all()
    serializer_class = LeadCallListSerializer

    def get_queryset(self):
        queryset = LeadCall.objects.all()
        lead_id = self.request.query_params.get('lead_id', None)
        if lead_id is not None:
            queryset = queryset.filter(lead_id=lead_id)

        user, auth_error = check_auth(self.request)
        if auth_error:
            return Response(auth_error)

        table_names = ['lead', 'leadcall']
        permissions = check_user_permissions(user, table_names)
        serializer = LeadCallListSerializer(queryset, many=True)
        return Response({'leadcalls': serializer.data, 'permissions': permissions})

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['lead', 'leadcall']
        permissions = check_user_permissions(user, table_names)
        queryset = LeadCall.objects.all()
        serializer = LeadCallListSerializer(queryset, many=True)
        return Response({'leadcalls': serializer.data, 'permissions': permissions})


class LeadCallRetrieveAPIView(generics.RetrieveAPIView):
    queryset = LeadCall.objects.all()
    serializer_class = LeadCallListSerializer

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['lead', 'leadcall']
        permissions = check_user_permissions(user, table_names)
        lead_call = self.get_object()
        lead_call_data = self.get_serializer(lead_call).data
        return Response({'leadcall': lead_call_data, 'permissions': permissions})
