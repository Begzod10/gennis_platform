from django.shortcuts import get_object_or_404
from rest_framework import generics, views, response, status

from group.models import Group, GroupSubjects
from .models import Assignment
from .serializers import TestCreateUpdateSerializer, Test, TermSerializer, Term


class CreateTest(generics.CreateAPIView):
    queryset = Test.objects.all()
    serializer_class = TestCreateUpdateSerializer


class UpdateTest(generics.UpdateAPIView):
    queryset = Test.objects.all()
    serializer_class = TestCreateUpdateSerializer


from datetime import date
from .models import Term


def create_terms_for_year(start_year: int):
    """
    start_year bo'yicha o'quv yilining 4 choragini yaratadi.
    Masalan: 2024 -> academic_year = "2024-2025"
    """
    academic_year = f"{start_year}-{start_year + 1}"

    # O'zbekiston taqvimiga mos chorak sanalari
    terms_data = [
        # 1-chorak
        {
            "quarter": 1,
            "start_date": date(start_year, 9, 2),
            "end_date": date(start_year, 10, 26),
        },
        # 2-chorak
        {
            "quarter": 2,
            "start_date": date(start_year, 11, 4),
            "end_date": date(start_year, 12, 28),
        },
        # 3-chorak
        {
            "quarter": 3,
            "start_date": date(start_year + 1, 1, 13),
            "end_date": date(start_year + 1, 3, 22),
        },
        # 4-chorak
        {
            "quarter": 4,
            "start_date": date(start_year + 1, 3, 31),
            "end_date": date(start_year + 1, 6, 2),
        },
    ]

    created_terms = []
    for term_data in terms_data:
        term, created = Term.objects.get_or_create(
            quarter=term_data["quarter"],
            academic_year=academic_year,
            defaults={
                "start_date": term_data["start_date"],
                "end_date": term_data["end_date"],
            }
        )
        created_terms.append(term)

    return created_terms


def create_multiple_years(start_year: int, count: int = 2):
    """
    Bir nechta o'quv yilini ketma-ket yaratadi.
    start_year: boshlang'ich yil
    count: nechta yil yaratish kerakligi (default=2)
    """
    for i in range(count):
        create_terms_for_year(start_year + i)

class ListTerm(generics.ListAPIView):
    queryset = Term.objects.all()
    serializer_class = TermSerializer
    def get(self, request, *args, **kwargs):
        create_multiple_years(2024)
        return super().get(request, *args, **kwargs)


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

            group_subjects = GroupSubjects.objects.filter(group=group).select_related('subject')

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
