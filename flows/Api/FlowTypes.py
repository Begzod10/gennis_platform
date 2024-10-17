from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

<<<<<<< HEAD
# from ..serializers_list import FlowTypesSerializer
=======
# from ..serializer import FlowTypesSerializer
>>>>>>> eb52be4df82a4b677e6154cbf495bab8ebf20d81
from ..models import FlowTypes


# class FlowTypesListCreateView(generics.ListCreateAPIView):
#     queryset = FlowTypes.objects.all()
#     serializer_class = FlowTypesSerializer
#
#
# class FlowTypesListView(generics.ListCreateAPIView):
#     queryset = FlowTypes.objects.all()
#     serializer_class = FlowTypesSerializer
#
#
# class FlowTypesDelete(generics.RetrieveDestroyAPIView):
#     queryset = FlowTypes.objects.all()
#     serializer_class = FlowTypesSerializer
