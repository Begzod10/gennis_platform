from collections import defaultdict

from django.shortcuts import get_object_or_404
from rest_framework import generics, views, response, status

from group.models import Group, GroupSubjects, Student
from .functions import create_multiple_years
from .models import Assignment
from .serializers import TestCreateUpdateSerializer, Test, TermSerializer, Term
from django.db.models import Case, When, Value, IntegerField


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
        current_year = "2025-2026"

        result = (
            Term.objects
            .values('academic_year')
            .distinct()
            .annotate(
                custom_order=Case(
                    When(academic_year=current_year, then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField()
                )
            )
            .order_by('custom_order', '-academic_year')
        )

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

        groups = Group.objects.filter(deleted=False, branch=branch).all().order_by('class_number__number')

        for group in groups:
            group_data = {
                "title": group.name if group.name else f"{group.class_number.number} {group.color.name}",
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

            results.append({"student_id": student_id, "assignment_id": assignment.id, "created": created,
                            "result": percentage * assignment.test.weight / 100})

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
            subject_id = kwargs.get('subject_id', None)
            if subject_id:
                assignments = Assignment.objects.filter(student=student, test__term_id=term_id,
                                                        test__subject_id=subject_id).select_related(
                    'test__subject')
            else:
                assignments = Assignment.objects.filter(student=student, test__term_id=term_id).select_related(
                    'test__subject')

            subjects_data = defaultdict(
                lambda: {"subject_name": "", "assignments": [], "total_result": 0, "count": 0, "average_result": 0})

            for assignment in assignments:
                subject_id = assignment.test.subject.id
                calculated_result = (assignment.test.weight * assignment.percentage) / 100

                subjects_data[subject_id]["subject_name"] = assignment.test.subject.name
                subjects_data[subject_id]["assignments"].append(
                    {"test_name": assignment.test.name, "percentage": assignment.percentage,
                     "calculated_result": round(calculated_result, 2)})
                subjects_data[subject_id]["total_result"] += calculated_result
                subjects_data[subject_id]["count"] += 1

            for subj_id, subj_data in subjects_data.items():
                if subj_data["count"] > 0:
                    subj_data["average_result"] = round(subj_data["total_result"] / subj_data["count"], 2)
                del subj_data["total_result"]
                del subj_data["count"]

            response_data.append({"id": student.id, "first_name": student.user.name, "last_name": student.user.surname,
                                  "subjects": list(subjects_data.values())})

        return response.Response(response_data, status=status.HTTP_200_OK)


class TermsByStudent(views.APIView):
    def get(self, request, *args, **kwargs):
        student_id = kwargs.get('student_id')
        term_id = kwargs.get('term_id')
        subject_id = kwargs.get('subject_id', None)

        student = Student.objects.get(id=student_id)
        if subject_id:

            assignments = Assignment.objects.filter(
                student=student,
                test__term_id=term_id,
                test__subject_id=subject_id
            ).select_related('test__subject')
        else:
            assignments = Assignment.objects.filter(
                student=student,
                test__term_id=term_id
            ).select_related('test__subject')

        response_data = {
            "student": {
                "first_name": student.user.first_name,
                "last_name": student.user.last_name,
            },
            "subjects": [],
            "total_result": 0,
            "average_result": 0
        }

        subjects_data = defaultdict(lambda: {
            "subject_name": "",
            "assignments": [],
            "total_result": 0,
            "count": 0,
            "average_result": 0
        })

        total_result_all = 0
        count_all = 0

        for assignment in assignments:
            subject_id = assignment.test.subject.id
            calculated_result = (assignment.test.weight * assignment.percentage) / 100

            subjects_data[subject_id]["subject_name"] = assignment.test.subject.name
            subjects_data[subject_id]["assignments"].append({
                "test_name": assignment.test.name,
                "percentage": assignment.percentage,
                "calculated_result": round(calculated_result, 2)
            })
            subjects_data[subject_id]["total_result"] += calculated_result
            subjects_data[subject_id]["count"] += 1

            total_result_all += calculated_result
            count_all += 1

        for subject_id, subj_data in subjects_data.items():
            if subj_data["count"] > 0:
                subj_data["average_result"] = round(subj_data["total_result"] / subj_data["count"], 2)
            del subj_data["count"]
            del subj_data["total_result"]
            response_data["subjects"].append(subj_data)

        if count_all > 0:
            response_data["total_result"] = round(total_result_all, 2)
            response_data["average_result"] = round(total_result_all / count_all, 2)

        return response.Response(response_data, status=status.HTTP_200_OK)


class GroupSubjectsApiView(views.APIView):
    def get(self, request, *args, **kwargs):
        group_id = kwargs.get('group_id')
        group = Group.objects.get(id=group_id)

        subjects = GroupSubjects.objects.filter(group=group).select_related('subject').values(
            'subject__id', 'subject__name'
        )

        subjects_data = [
            {"id": subj["subject__id"], "name": subj["subject__name"]} for subj in subjects
        ]

        return response.Response(subjects_data, status=status.HTTP_200_OK)
