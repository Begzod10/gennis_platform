import pprint

from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import GroupSubjectSerializer, GroupListSerializer
from group.models import Group, GroupSubjects
from rest_framework import generics
from classes.models import ClassNumber, ClassNumberSubjects


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
        if 'class_type_id' in request.query_params:
            queryset = Group.objects.filter(class_type_id=self.request.query_params['class_type_id'],
                                            branch_id=self.request.query_params['branch_id']).order_by(
                'class_number_id').all()
        else:
            queryset = Group.objects.filter(branch_id=self.request.query_params['branch_id']).order_by(
                'class_number_id').all()
        class_numbers = ClassNumber.objects.filter(branch_id=self.request.query_params['branch_id']).all()

        for class_number in class_numbers:
            class_number_subjects = ClassNumberSubjects.objects.filter(class_number=class_number).all()
            for class_number_subject in class_number_subjects:
                groups = Group.objects.filter(class_number_id=class_number.id).all()
                for group in groups:
                    GroupSubjects.objects.get_or_create(
                        hours=class_number_subject.hours,
                        group_id=group.id,
                        subject_id=class_number_subject.subject_id
                    )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class GroupSubjectAddView(APIView):
    def post(self, request, *args, **kwargs):
        subjects = request.data['subjects']
        group = Group.objects.get(pk=request.query_params.get('group_id'))
        for subject in subjects:
            GroupSubjects.objects.get_or_create(
                group=group,
                subject_id=subject['value'],
                hours=subject.get('hours', 0)
            )
        data = GroupListSerializer(group).data
        return Response(data)


class GroupSubjectRemoveView(APIView):
    def post(self, request, *args, **kwargs):
        subject = request.data['subject_id']
        group = Group.objects.get(pk=request.data['group_id'])
        pprint.pprint(request.data)
        group_subject = GroupSubjects.objects.filter(group_id=group.id, subject_id=subject)
        group_subject.delete()
        data = GroupListSerializer(group).data
        return Response({
            "msg": "success"
        })
