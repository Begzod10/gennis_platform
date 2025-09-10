from django.shortcuts import get_object_or_404
from rest_framework import generics, views, response, status

from group.models import Group, GroupSubjects, Student
from .functions import create_multiple_years
from .models import Assignment
from .serializers import TestCreateUpdateSerializer, Test, TermSerializer, Term


class CreateTest(generics.CreateAPIView):
    queryset = Test.objects.all()
    serializer_class = TestCreateUpdateSerializer


class UpdateTest(generics.UpdateAPIView):
    queryset = Test.objects.all()
    serializer_class = TestCreateUpdateSerializer


class EducationYears(generics.ListAPIView):
    queryset = Term.objects.all()
    serializer_class = TermSerializer

    def get(self, request, *args, **kwargs):
        result = Term.objects.values('academic_year').distinct()
        return response.Response(result, status=status.HTTP_200_OK)


class ListTerm(generics.ListAPIView):
    queryset = Term.objects.all()
    serializer_class = TermSerializer

    def get_queryset(self):
        create_multiple_years(2025)
        academic_year = self.kwargs.get('academic_year')
        return self.queryset.filter(academic_year=academic_year)


class DeleteTest(generics.DestroyAPIView):
    queryset = Test.objects.all()
    serializer_class = TestCreateUpdateSerializer

    def delete(self, request, *args, **kwargs):
        test = self.get_object()
        test.deleted = True
        test.save()
        return response.Response({"message": "Test deleted successfully"}, status=status.HTTP_200_OK)


class ListTest(views.APIView):
    def get(self, request, *args, **kwargs):
        term = kwargs.get('term')
        branch = kwargs.get('branch')

        result = []

        groups = Group.objects.filter(deleted=False, branch=branch).all()

        for group in groups:
            group_data = {
                "title": group.name if group.name else f"{group.class_number.number} {group.class_number.class_types.name}",
                "id": group.id, "type": "group", "children": []}

            group_subjects = (GroupSubjects.objects.filter(group=group).select_related('subject').distinct('subject'))

            for group_subject in group_subjects:
                subject = group_subject.subject

                tests = Test.objects.filter(group=group, subject=subject, term=term, deleted=False)

                table_data = [{"id": test.id, "name": test.name, "weight": test.weight, "date": test.date} for test in
                              tests]

                group_data["children"].append(
                    {"title": subject.name, "id": subject.id, "type": "subject", "tableData": table_data})

            result.append(group_data)

        return response.Response(result, status=status.HTTP_200_OK)


class StudentAssignmentView(views.APIView):
    def get(self, request, *args, **kwargs):
        group_id = kwargs.get('group_id')
        test_id = kwargs.get('test_id')

        group = get_object_or_404(Group.objects.prefetch_related('students__user'), id=group_id)

        tests = Assignment.objects.filter(student__in=group.students.all(), test_id=test_id)

        test_map = {t.student_id: t for t in tests}

        result = []
        for student in group.students.all():
            assignment = test_map.get(student.id)
            result.append({"id": student.id, "name": student.user.name, "surname": student.user.surname,
                           "assignment": {"id": assignment.id, "percentage": assignment.percentage,
                                          "date": assignment.date} if assignment else None})

        return response.Response(result, status=status.HTTP_200_OK)


class AssignmentCreateView(views.APIView):
    def post(self, request, *args, **kwargs):
        data = request.data

        if not isinstance(data, list):
            return response.Response({"error": "Request body list bo'lishi kerak"}, status=status.HTTP_400_BAD_REQUEST)

        results = []
        errors = []

        for index, item in enumerate(data, start=1):
            test_id = item.get('test_id')
            percentage = item.get('percentage')
            student_id = item.get('student_id')

            if not test_id or not student_id or percentage is None:
                errors.append(
                    {"index": index, "error": "test_id, student_id va percentage maydonlari majburiy", "data": item})
                continue

            assignment, created = Assignment.objects.update_or_create(test_id=test_id, student_id=student_id,
                                                                      defaults={"percentage": percentage, })

            results.append({"student_id": student_id, "assignment_id": assignment.id, "created": created})

        response_data = {"success": results, "errors": errors}

        return response.Response(response_data, status=status.HTTP_200_OK)


class TermsByGroup(views.APIView):
    def get(self, request, *args, **kwargs):
        group_id = kwargs.get('group_id')
        term_id = kwargs.get('term_id')

        group = Group.objects.get(id=group_id)
        students = group.students.all()

        response_data = []

        for student in students:
            assignments = Assignment.objects.filter(student=student, test__term_id=term_id).select_related(
                'test__subject')

            student_data = {"id": student.id, "first_name": student.user.name, "last_name": student.user.surname,
                "assignments": [], "average_result": 0}

            total_result = 0
            count = 0

            for assignment in assignments:
                result = (assignment.test.weight * assignment.percentage) / 100

                student_data["assignments"].append(
                    {"subject_name": assignment.test.subject.name, "test_name": assignment.test.name,
                        "percentage": assignment.percentage, "calculated_result": round(result, 2)})

                total_result += result
                count += 1

            if count > 0:
                student_data["average_result"] = round(total_result / count, 2)

            response_data.append(student_data)

        return response.Response(response_data, status=status.HTTP_200_OK)


class TermsByStudent(views.APIView):
    def get(self, request, *args, **kwargs):
        student_id = kwargs.get('student_id')
        term_id = kwargs.get('term_id')

        student = Student.objects.get(id=student_id)
        assignments = Assignment.objects.filter(student=student, test__term_id=term_id).select_related('test__subject')

        response_data = {"student": {"first_name": student.user.first_name, "last_name": student.user.last_name, },
            "assignments": [], "total_result": 0, "average_result": 0}

        total_result = 0
        count = 0

        for assignment in assignments:
            result = (assignment.test.weight * assignment.percentage) / 100

            response_data["assignments"].append(
                {"subject_name": assignment.test.subject.name, "test_name": assignment.test.name,
                    "percentage": assignment.percentage, "calculated_result": round(result, 2)})

            total_result += result
            count += 1

        if count > 0:
            response_data["total_result"] = round(total_result, 2)
            response_data["average_result"] = round(total_result / count, 2)

        return response.Response(response_data, status=status.HTTP_200_OK)
