from rest_framework import generics
from branch.serializers import BranchSerializer
from branch.models import Branch


class BranchCreateView(generics.CreateAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer


class BranchUpdateView(generics.UpdateAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer


class BranchDestroyView(generics.DestroyAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer

class StudentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def delete(self, request, *args, **kwargs):
        student = self.get_object()
        DeletedNewStudent.objects.create(student=student)  # new studentni ochirish
        return Response({"detail": "Student was deleted successfully"}, status=status.HTTP_200_OK)


class StudentHistoryGroupsRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentHistoryGroups.objects.all()
    serializer_class = StudentHistoryGroupsSerializer


class StudentCharityRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentCharity.objects.all()
    serializer_class = StudentCharitySerializer


class StudentPaymentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentPayment.objects.all()
    serializer_class = StudentPaymentSerializer


class DeletedStudentDestroy(generics.DestroyAPIView):
    queryset = DeletedStudent.objects.all()
    serializer_class = DeletedStudentSerializer
