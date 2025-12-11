from rest_framework.response import Response
from rest_framework.views import APIView

from parents.models import Parent
from parents.serializers.crud import ParentSerializer
from students.models import Student, StudentPayment
from students.serializer.lists import ActiveListSerializer
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

        available = Student.objects.exclude(id__in=existing_ids)

        return Response(ActiveListSerializer(available, many=True).data)


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
