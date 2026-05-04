from collections import defaultdict
from django.shortcuts import get_object_or_404
from rest_framework import generics, views, response, status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Case, When, Value, IntegerField, Avg

from group.models import Group, GroupSubjects, Student
from terms.models import Assignment, Test, Term
from terms.serializers import TestCreateUpdateSerializer, TermSerializer
from teachers.models import Teacher
from school_time_table.models import ClassTimeTable

class TeacherEducationYears(views.APIView):
    permission_classes = [IsAuthenticated]

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


class TeacherListTerm(generics.ListAPIView):
    queryset = Term.objects.all()
    serializer_class = TermSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        academic_year = self.kwargs.get('academic_year')
        return self.queryset.filter(academic_year=academic_year)


class TeacherListTest(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            return response.Response({"detail": "Siz teacher emassiz"}, status=status.HTTP_403_FORBIDDEN)

        term_id = kwargs.get('term')
        
        # Faqat o'qituvchiga tegishli guruhlarni olamiz
        groups = teacher.group_set.filter(deleted=False).order_by('class_number__number')

        result = []

        for group in groups:
            group_data = {
                "title": group.name if group.name else f"{group.class_number.number} {group.color.name}",
                "id": group.id, 
                "type": "group", 
                "children": []
            }

            # Bu guruhda o'qituvchi o'tadigan fanlarni ClassTimeTable orqali aniqlaymiz
            teacher_subjects_ids = ClassTimeTable.objects.filter(
                teacher=teacher, 
                group=group
            ).values_list('subject_id', flat=True).distinct()
            
            group_subjects = GroupSubjects.objects.filter(
                group=group, 
                subject_id__in=teacher_subjects_ids
            ).select_related('subject').distinct('subject')

            if not group_subjects.exists():
                # Agar ClassTimeTable da yo'q bo'lsa, lekin guruhga biriktirilgan bo'lsa, 
                # balki o'qituvchining barcha fanlarini ko'rsatish kerakdir?
                # User "unga tegishli fanlar" dedi.
                teacher_subjects = teacher.subject.all()
                group_subjects = GroupSubjects.objects.filter(
                    group=group, 
                    subject__in=teacher_subjects
                ).select_related('subject').distinct('subject')

            for group_subject in group_subjects:
                subject = group_subject.subject

                tests = Test.objects.filter(group=group, subject=subject, term_id=term_id, deleted=False)

                table_data = [
                    {
                        "id": test.id, 
                        "name": test.name, 
                        "weight": test.weight, 
                        "date": test.date
                    } for test in tests
                ]

                group_data["children"].append({
                    "title": subject.name, 
                    "id": subject.id, 
                    "type": "subject", 
                    "tableData": table_data
                })

            if group_data["children"]:
                result.append(group_data)

        return response.Response(result, status=status.HTTP_200_OK)


class TeacherCreateTest(generics.CreateAPIView):
    queryset = Test.objects.all()
    serializer_class = TestCreateUpdateSerializer
    permission_classes = [IsAuthenticated]


class TeacherUpdateTest(generics.UpdateAPIView):
    queryset = Test.objects.all()
    serializer_class = TestCreateUpdateSerializer
    permission_classes = [IsAuthenticated]


class TeacherDeleteTest(generics.DestroyAPIView):
    queryset = Test.objects.all()
    serializer_class = TestCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        test = self.get_object()
        test.deleted = True
        test.save()
        return response.Response({"message": "Test deleted successfully"}, status=status.HTTP_200_OK)


class TeacherStudentAssignmentView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        group_id = kwargs.get('group_id')
        test_id = kwargs.get('test_id')

        group = get_object_or_404(
            Group.objects.prefetch_related('students__user'),
            id=group_id
        )

        tests = Assignment.objects.filter(
            student__in=group.students.all(),
            test_id=test_id
        )

        test_map = {t.student_id: t for t in tests}

        result = []
        for student in group.students.all():
            assignment = test_map.get(student.id)

            if assignment:
                assignment_data = {
                    "id": assignment.id,
                    "percentage": assignment.percentage,
                    "date": assignment.date,
                    "is_editable": assignment.percentage == 0
                }
            else:
                assignment_data = {
                    "is_editable": True
                }

            result.append({
                "id": student.id,
                "name": student.user.name,
                "surname": student.user.surname,
                "assignment": assignment_data
            })

        return response.Response(result, status=status.HTTP_200_OK)


class TeacherAssignmentCreateView(views.APIView):
    permission_classes = [IsAuthenticated]

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

            assignment, created = Assignment.objects.update_or_create(
                test_id=test_id, 
                student_id=student_id,
                defaults={"percentage": percentage}
            )

            results.append({
                "student_id": student_id, 
                "assignment_id": assignment.id, 
                "created": created,
                "result": percentage * assignment.test.weight / 100
            })

        response_data = {"success": results, "errors": errors}

        return response.Response(response_data, status=status.HTTP_200_OK)


class TeacherTermsByGroupView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            return response.Response({"detail": "Siz teacher emassiz"}, status=status.HTTP_403_FORBIDDEN)

        group_id = kwargs.get('group_id')
        term_id = kwargs.get('term_id')
        subject_id = kwargs.get('subject_id', None)

        if not teacher.group_set.filter(id=group_id).exists():
             return response.Response({"detail": "Bu guruh sizga tegishli emas"}, status=status.HTTP_403_FORBIDDEN)

        group = Group.objects.get(id=group_id)
        students = group.students.all()

        response_data = []

        for student in students:
            if subject_id:
                assignments = Assignment.objects.filter(
                    student=student, 
                    test__term_id=term_id,
                    test__subject_id=subject_id
                ).select_related('test__subject')
            else:
                teacher_subjects_ids = ClassTimeTable.objects.filter(
                    teacher=teacher, 
                    group=group
                ).values_list('subject_id', flat=True).distinct()
                
                assignments = Assignment.objects.filter(
                    student=student, 
                    test__term_id=term_id,
                    test__subject_id__in=teacher_subjects_ids
                ).select_related('test__subject')

            subjects_data = defaultdict(
                lambda: {"subject_name": "", "assignments": [], "total_result": 0, "count": 0, "average_result": 0})

            for assignment in assignments:
                subj_id = assignment.test.subject.id
                calculated_result = (assignment.test.weight * assignment.percentage) / 100

                subjects_data[subj_id]["subject_name"] = assignment.test.subject.name
                subjects_data[subj_id]["assignments"].append(
                    {"test_name": assignment.test.name, "percentage": assignment.percentage,
                     "calculated_result": round(calculated_result, 2)})
                subjects_data[subj_id]["total_result"] += calculated_result
                subjects_data[subj_id]["count"] += 1

            for subj_id, subj_data in subjects_data.items():
                if subj_data["count"] > 0:
                    subj_data["average_result"] = subj_data["total_result"]
                del subj_data["total_result"]
                del subj_data["count"]

            response_data.append({
                "id": student.id, 
                "first_name": student.user.name, 
                "last_name": student.user.surname,
                "subjects": list(subjects_data.values())
            })

        return response.Response(response_data, status=status.HTTP_200_OK)


