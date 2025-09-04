from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import GroupSubjectSerializer, GroupListSerializer
from group.models import Group
from rest_framework import generics


class GroupStudentsClassRoom(APIView):
    def get(self, request, *args, **kwargs):
        pk = kwargs['pk']
        list = []
        group = Group.objects.get(pk=pk)
        for student in group.students.all():
            list.append({
                'id': student.id,
                'name': student.user.name,
                "surname": student.user.surname,
                "father_name": student.user.father_name,
                "phone_number": student.user.phone,
                "birth_date": student.user.birth_date.isoformat(),
                "balance": student.id,
                "username": student.user.username

            })
        return Response(list)


class GroupListView(generics.ListAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupListSerializer

    def list(self, request, *args, **kwargs):
        queryset = Group.objects.filter(branch_id=self.request.query_params['branch_id']).all()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

# class