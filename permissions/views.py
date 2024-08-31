from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from permissions.models import ManySystem, ManyLocation, ManyBranch
from permissions.response import GetModelsMixin
from system.serializers import SystemSerializersUsers
from user.functions.functions import check_auth


class SystemListUser(generics.ListAPIView):
    queryset = ManySystem.objects.all()
    serializer_class = SystemSerializersUsers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        queryset = ManySystem.objects.filter(user=user).all()
        data = []
        for info in queryset:
            data.append({

                'id': info.system.id,
                'name': info.system.name,
                'number': info.system.number
            })
        return Response(data)


class LocationListUser(generics.RetrieveAPIView):
    queryset = ManyLocation.objects.all()
    serializer_class = SystemSerializersUsers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        queryset = ManyLocation.objects.filter(user=user, location__system_id=self.kwargs['pk']).all()
        data = []
        for info in queryset:
            data.append({

                'id': info.location.id,
                'name': info.location.name,
                'number': info.location.number
            })
        return Response(data)


class BranchListUser(generics.RetrieveAPIView):
    queryset = ManyBranch.objects.all()
    serializer_class = SystemSerializersUsers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        queryset = ManyBranch.objects.filter(user=user, branch__location_id=self.kwargs['pk']).all()
        data = []
        for info in queryset:
            data.append({

                'id': info.branch.id,
                'name': info.branch.name,
                'number': info.branch.number
            })
        return Response(data)


class DynamicModelListView(GetModelsMixin,APIView):

    def post(self, request, *args, **kwargs):
        model_names = self.filter()

        return Response(model_names)

    # def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     return Response(queryset)
