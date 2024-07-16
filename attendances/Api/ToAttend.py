from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

import jwt
import json

from .functions.CheckAndCreateAttendancePerMonth import check_and_create_attendance_per_month


class ToAttend(APIView):
    def post(self, request, group_id):
        data = json.loads(request.body)
        check_and_create_attendance_per_month(group_id, students=data['students'], date=data['date'])
        print(data)
        return Response({'data': 'true'})

    def get(self, request, group_id):
        # check_and_create_attendance_per_month(group_id, student_id=)

        return Response({'data': 'true'})
