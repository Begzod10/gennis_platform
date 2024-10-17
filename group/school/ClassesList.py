from rest_framework import generics

from group.models import Group
from group.serializers_list.serializers_self import AddClassesSerializers

from rest_framework.permissions import IsAuthenticated
from permissions.response import QueryParamFilterMixin


class ClassesView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Group.objects.filter(class_number__isnull=False)
    serializer_class = AddClassesSerializers


# class AddClassesList(QueryParamFilterMixin, generics.ListAPIView):
#     permission_classes = [IsAuthenticated]
#     filter_mappings = {
#         'branch': 'branch_id'
#     }
#     queryset = Group.objects.filter(class_number__isnull=True)
#     serializer_class = AddClassesSerializers
class AddClassesList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Group.objects.filter(class_number__isnull=True)
    serializer_class = AddClassesSerializers

    def get_queryset(self, ):
        branch_id = self.request.query_params.get('branch_id', None)
        return Group.objects.filter(branch_id=branch_id, class_number__isnull=True)
