from django.db.models import Prefetch
from rest_framework.response import Response
from rest_framework.views import APIView

from group.models import Group
from parents.models import Parent
from parents.serializers.crud import ParentSerializer, StudentSerializer
from students.models import Student, StudentPayment, DeletedNewStudent, DeletedStudent
from students.serializers import StudentPaymentSerializer


class RemoveStudentsView(APIView):
    def post(self, request, id):
        parent = Parent.objects.get(id=id)
        student_id = request.data.get("student_id")

        student = Student.objects.filter(id=student_id).first()

        if student:
            parent.children.remove(student)

        return Response(ParentSerializer(parent).data)


class AddStudentsView(APIView):
    def post(self, request, id):
        parent = Parent.objects.get(id=id)
        student_ids = request.data.get("student_ids", [])

        students = Student.objects.filter(id__in=student_ids)

        for s in students:
            parent.children.add(s)

        return Response(ParentSerializer(parent).data)


class AvailableStudentsView(APIView):
    def get(self, request, id):
        parent = Parent.objects.get(id=id)

        existing_ids = parent.children.values_list("id", flat=True)

        deleted_student_ids = DeletedStudent.objects.filter(student__groups_student__isnull=True,
                                                            deleted=False).values_list('student_id', flat=True)

        deleted_new_student_ids = DeletedNewStudent.objects.values_list('student_id', flat=True)

        active_students = Student.objects.select_related('user', 'user__language', 'class_number').prefetch_related(
            'user__student_user',
            Prefetch('groups_student', queryset=Group.objects.select_related('class_number', 'color').order_by('id'),
                     to_attr='prefetched_groups')).exclude(id__in=deleted_student_ids).exclude(
            id__in=deleted_new_student_ids).filter(groups_student__isnull=False,user__branch_id=parent.user.branch.id).exclude(id__in=existing_ids).distinct().order_by(
            'class_number__number')

        return Response(StudentSerializer(active_students, many=True).data)


class StudentPaymentListView(APIView):
    def get(self, request):
        user_id = request.query_params.get("id")
        payment = request.query_params.get("payment") == "true"

        student = Student.objects.filter(user_id=user_id).first()

        payments = StudentPayment.objects.filter(
            student_id=student.id,
            payment=payment
        )

        return Response(StudentPaymentSerializer(payments, many=True).data)
