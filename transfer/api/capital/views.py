from rest_framework import generics
from .serializers import OldCapitalSerializerTransfer
from capital.models import OldCapital


class OldCapitalCreateView(generics.CreateAPIView):
    queryset = OldCapital.objects.all()
    serializer_class = OldCapitalSerializerTransfer
