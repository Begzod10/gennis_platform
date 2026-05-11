from collections import defaultdict

from django.shortcuts import get_object_or_404
from rest_framework import generics, views, response, status

from group.models import Group, GroupSubjects, Student, GroupRating
from .functions import create_multiple_years
from .models import Assignment
from .serializers import TestCreateUpdateSerializer, Test, TermSerializer, Term
from django.db.models import Case, When, Value, IntegerField, Avg, Q
from flows.models import Flow


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
        term = get_object_or_404(Term, id=kwargs.get('term'))
        branch_id = kwargs.get('branch')

        groups = (
            Group.objects
            .filter(deleted=False, branch_id=branch_id)
            .select_related('class_number', 'color')
            .order_by('class_number__number')
        )
        group_ids = list(groups.values_list('id', flat=True))

        flows = (
            Flow.objects
            .filter(branch_id=branch_id)
            .select_related('subject')
            .order_by('order', 'id')
        )
        flow_ids = list(flows.values_list('id', flat=True))

        gs_qs = (
            GroupSubjects.objects
            .filter(group_id__in=group_ids)
            .select_related('subject')
            .distinct('group_id', 'subject_id')
        )
        gs_by_group = defaultdict(list)
        for gs in gs_qs:
            gs_by_group[gs.group_id].append(gs)

        tests_qs = (
            Test.objects
            .filter(term=term, deleted=False)
            .filter(Q(group_id__in=group_ids) | Q(flow_id__in=flow_ids))
            .values('id', 'name', 'weight', 'date', 'group_id', 'flow_id', 'subject_id')
        )

        tests_by_group_subject = defaultdict(list)
        tests_by_flow_subject = defaultdict(list)
        for t in tests_qs:
            row = {
                "id": t['id'],
                "name": t['name'],
                "weight": t['weight'],
                "date": t['date'],
            }
            if t['group_id']:
                tests_by_group_subject[(t['group_id'], t['subject_id'])].append(row)
            elif t['flow_id']:
                tests_by_flow_subject[(t['flow_id'], t['subject_id'])].append(row)

        result = []

        for group in groups:
            class_no = getattr(group.class_number, 'number', None)
            color_name = getattr(group.color, 'name', None)
            display_name = group.name or f"{class_no or '?'} {color_name or '?'}"

            children = [
                {
                    "title": gs.subject.name,
                    "id": gs.subject.id,
                    "type": "subject",
                    "tableData": tests_by_group_subject.get((group.id, gs.subject_id), []),
                }
                for gs in gs_by_group.get(group.id, [])
            ]

            result.append({
                "title": display_name,
                "id": group.id,
                "type": "group",
                "children": children,
            })

        for flow in flows:
            subj = flow.subject
            if not subj:
                continue
            result.append({
                "title": flow.name,
                "id": flow.id,
                "type": "flow",
                "children": [{
                    "title": subj.name,
                    "id": subj.id,
                    "type": "subject",
                    "tableData": tests_by_flow_subject.get((flow.id, subj.id), []),
                }],
            })

        return response.Response(result, status=status.HTTP_200_OK)


class StudentAssignmentView(views.APIView):
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


class AssignmentCreateView(views.APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        print(data)

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
                    subj_data["average_result"] =subj_data["total_result"]
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
                subj_data["average_result"] = subj_data["total_result"]
            del subj_data["count"]
            del subj_data["total_result"]
            response_data["subjects"].append(subj_data)

        if count_all > 0:
            response_data["total_result"] = round(total_result_all, 2)
            response_data["average_result"] =total_result_all

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

class EducationQualityOverview(views.APIView):
    def get(self, request, *args, **kwargs):
        def get_param(names):
            for name in names:
                val = request.query_params.get(name)
                if val and val not in ['undefined', 'null', '', 'all']:
                    return val
            return None

        branch_id = get_param(['branch_id', 'branch'])
        subject_id = get_param(['subject_id', 'subject'])
        class_id = get_param(['class_id', 'class', 'group_id'])
        teacher_id = get_param(['teacher_id', 'teacher'])
        term_id = get_param(['term_id', 'term'])

        # Include group-tests (non-deleted group) and flow-tests
        assignments = Assignment.objects.filter(test__deleted=False).filter(
            Q(test__group__deleted=False) | Q(test__flow__isnull=False)
        )

        if branch_id:
            assignments = assignments.filter(
                Q(test__group__branch_id=branch_id) | Q(test__flow__branch_id=branch_id)
            )
        if subject_id:
            assignments = assignments.filter(test__subject_id=subject_id)
        if class_id:
            assignments = assignments.filter(test__group_id=class_id)
        if teacher_id:
            assignments = assignments.filter(
                Q(test__group__teacher=teacher_id) | Q(test__flow__teacher_id=teacher_id)
            )
        if term_id:
            assignments = assignments.filter(test__term_id=term_id)

        avg_percentage = assignments.aggregate(Avg('percentage'))['percentage__avg'] or 0
        avg_rating = avg_percentage / 20
        return response.Response({
            "rating": round(avg_rating, 1),
            "max_rating": 5,
            "description": "5 ballik tizimda maktab reytingi"
        }, status=status.HTTP_200_OK)


class EducationQualityDetails(views.APIView):
    def get(self, request, *args, **kwargs):
        term_id = kwargs.get('term_id')
        term = get_object_or_404(Term, id=term_id)

        def get_param(names):
            for name in names:
                val = request.query_params.get(name)
                if val and val not in ['undefined', 'null', '', 'all']:
                    return val
            return None

        subject_id = get_param(['subject_id', 'subject'])
        class_id = get_param(['class_id', 'class', 'group_id'])
        teacher_id = get_param(['teacher_id', 'teacher'])
        branch_id = get_param(['branch_id', 'branch'])

        assignments = Assignment.objects.filter(
            test__term_id=term_id, test__deleted=False
        ).filter(
            Q(test__group__deleted=False) | Q(test__flow__isnull=False)
        )

        if branch_id:
            assignments = assignments.filter(
                Q(test__group__branch_id=branch_id) | Q(test__flow__branch_id=branch_id)
            )
        if teacher_id:
            assignments = assignments.filter(
                Q(test__group__teacher=teacher_id) | Q(test__flow__teacher_id=teacher_id)
            )
        if class_id:
            assignments = assignments.filter(test__group_id=class_id)
        if subject_id:
            assignments = assignments.filter(test__subject_id=subject_id)

        chart_data = []
        chart_type = "subjects"

        if subject_id:
            chart_type = "classes"
            group_data = (
                assignments.filter(test__group__isnull=False)
                .values('test__group__name', 'test__group__class_number__number')
                .annotate(avg=Avg('percentage'))
                .order_by('test__group__class_number__number')
            )
            for item in group_data:
                label = item['test__group__name'] or f"{item['test__group__class_number__number']}-sinf"
                chart_data.append({"label": label, "value": round((item['avg'] or 0) / 20, 1)})

            flow_data = (
                assignments.filter(test__flow__isnull=False)
                .values('test__flow__name')
                .annotate(avg=Avg('percentage'))
                .order_by('test__flow__name')
            )
            for item in flow_data:
                chart_data.append({
                    "label": item['test__flow__name'],
                    "value": round((item['avg'] or 0) / 20, 1),
                })

        elif teacher_id:
            chart_type = "performance"
            group_data = (
                assignments.filter(test__group__isnull=False)
                .values('test__group__name', 'test__subject__name')
                .annotate(avg=Avg('percentage'))
            )
            for item in group_data:
                label = f"{item['test__subject__name']} ({item['test__group__name']})"
                chart_data.append({"label": label, "value": round((item['avg'] or 0) / 20, 1)})

            flow_data = (
                assignments.filter(test__flow__isnull=False)
                .values('test__flow__name', 'test__subject__name')
                .annotate(avg=Avg('percentage'))
            )
            for item in flow_data:
                label = f"{item['test__subject__name']} ({item['test__flow__name']})"
                chart_data.append({"label": label, "value": round((item['avg'] or 0) / 20, 1)})

        elif class_id:
            chart_type = "subjects"
            data = (
                assignments.values('test__subject__name')
                .annotate(avg=Avg('percentage'))
            )
            for item in data:
                chart_data.append({"label": item['test__subject__name'], "value": round((item['avg'] or 0) / 20, 1)})

        else:
            data = (
                assignments.values('test__subject__name')
                .annotate(avg=Avg('percentage'))
                .order_by('-avg')
            )
            for item in data:
                if item['test__subject__name']:
                    chart_data.append({"label": item['test__subject__name'], "value": round((item['avg'] or 0) / 20, 1)})

        return response.Response({
            "term": TermSerializer(term).data,
            "charts": [
                {
                    "type": chart_type,
                    "data": chart_data
                }
            ]
        }, status=status.HTTP_200_OK)
