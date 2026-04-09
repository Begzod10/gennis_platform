import pprint

from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import GroupSubjectSerializer, GroupListSerializer
from group.models import Group, GroupSubjects
from rest_framework import generics
from classes.models import ClassNumber, ClassNumberSubjects
from students.models import StudentSubject
from django.db.models import Q, Case, When, Value, BooleanField
from rest_framework.exceptions import ValidationError


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
    serializer_class = GroupListSerializer

    def get_queryset(self):
        branch_id = self.request.query_params.get("branch_id")
        if not branch_id:
            raise ValidationError({"branch_id": "This query param is required."})

        class_type_id = self.request.query_params.get("class_type_id")

        base = (
            Group.objects.filter(branch_id=branch_id, deleted=False)
            .select_related("class_number", "color", "class_type")
            .prefetch_related("group_subjects__subject")
        )

        if class_type_id:
            qs = base.filter(
                Q(class_type_id=class_type_id) | Q(class_type_id__isnull=True)
            ).annotate(
                status_class_type=Case(
                    When(class_type_id=class_type_id, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            )
        else:
            qs = base.filter(class_type_id__isnull=True).annotate(
                status_class_type=Value(False, output_field=BooleanField())
            )

        return qs.order_by("class_number_id")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data})


class GroupSubjectAddView(APIView):
    def post(self, request, *args, **kwargs):
        subjects = request.data.get('subjects', [])
        group_id = request.query_params.get('group_id')
        group = Group.objects.get(pk=group_id)

        for subject in subjects:
            subject_id = subject['value']
            hours = subject.get('hours', 0)

            group_subject, created = GroupSubjects.objects.get_or_create(
                group=group,
                subject_id=subject_id,
                defaults={'hours': hours}
            )
            if not created:
                group_subject.hours = hours
                group_subject.save()

            for st in group.students.all():
                student_subject, st_created = StudentSubject.objects.get_or_create(
                    student=st,
                    group_subjects=group_subject,
                    subject_id=subject_id,
                    defaults={'hours': hours}
                )
                if not st_created:
                    student_subject.hours = hours
                    student_subject.save()

        data = GroupListSerializer(group).data
        return Response(data)


class GroupSubjectRemoveView(APIView):
    def post(self, request, *args, **kwargs):
        subject = request.data['subject_id']
        group = Group.objects.get(pk=request.data['group_id'])
        group_subject = GroupSubjects.objects.filter(group_id=group.id, subject_id=subject)
        group_subject.delete()
        data = GroupListSerializer(group).data
        return Response({
            "msg": "O'zgartirildi",
        })


class AddClassTypeToGroup(APIView):
    def post(self, request, *args, **kwargs):
        group = Group.objects.get(pk=request.data['group_id'])
        if group.class_type_id:
            group.class_type_id = None
        else:
            group.class_type_id = request.data['class_type_id']
        group.save()
        return Response({
            "msg": "success"
        })
