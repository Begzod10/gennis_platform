import json

from rest_framework.views import APIView
from rest_framework.response import Response

from django.contrib.auth.models import Group
from user.models import CustomUser


class AddUserGroup(APIView):
    def post(self, request):
        data = json.loads(request.body)
        user = CustomUser.objects.get(pk=11)
        group = Group.objects.get(pk=data['job_id'])
        user.groups.add(group)
        return Response({'job': ''})

    def get(self, request):
        jobs = Group.objects.all()
        return Response({'jobs': [{'id': job.id, 'name': job.name} for job in jobs]})
