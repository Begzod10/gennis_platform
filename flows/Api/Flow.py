from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from permissions.response import QueryParamFilterMixin
from ..models import Flow
from ..serializers import FlowCreateUpdateSerializer, FlowsSerializer
from ..serializers_list import FlowsSerializerTest, FlowsSerializerProfile


class FlowListCreateView(QueryParamFilterMixin, generics.ListCreateAPIView):
    filter_mappings = {
        'teacher': 'teacher__id',
        'subject': 'subject__id',

    }

    permission_classes = [IsAuthenticated]

    queryset = Flow.objects.all()
    serializer_class = FlowCreateUpdateSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return FlowsSerializer
        return FlowCreateUpdateSerializer

    def create(self, request, *args, **kwargs):
        write_serializer = self.get_serializer(data=request.data, partial=True)
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)
        instance = Flow.objects.get(pk=write_serializer.data['id'])
        read_serializer = FlowsSerializer(instance)

        return Response({'flow': read_serializer.data, 'msg': 'Patok muvaffaqqiyatli kiritildi'})


class FlowListView(QueryParamFilterMixin, generics.ListCreateAPIView):
    filter_mappings = {
        'teacher': 'teacher__id',
        'subject': 'subject__id',
        'branch': 'branch__id'

    }
    permission_classes = [IsAuthenticated]

    queryset = Flow.objects.all().order_by('order')
    serializer_class = FlowsSerializerTest

    # def get_queryset(self):
    #     queryset = Flow.objects.all()
    #     location_id = self.request.query_params.get('location_id', None)
    #     branch_id = self.request.query_params.get('branch_id', None)
    #     if not branch_id:
    #         branch_id = self.request.user.branch_id
    #
    #     if branch_id is not None:
    #         queryset = queryset.filter(branch_id=branch_id)
    #     if location_id is not None:
    #         queryset = queryset.filter(location_id=location_id)
    #
    #     return queryset


class FlowProfile(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Flow.objects.all()
    serializer_class = FlowCreateUpdateSerializer

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return FlowCreateUpdateSerializer
        return FlowsSerializerProfile

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        instance.refresh_from_db()
        read_serializer = FlowsSerializerProfile(instance)
        return Response(read_serializer.data)
