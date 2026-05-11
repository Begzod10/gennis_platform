from collections import defaultdict
from django.shortcuts import get_object_or_404
from rest_framework import generics, views, response, status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Case, When, Value, IntegerField, Avg, Count, Q

from flows.models import Flow
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
        teacher = Teacher.objects.filter(user=request.user, deleted=False).first()
        if not teacher:
            return response.Response(
                {"detail": "Siz teacher emassiz"},
                status=status.HTTP_403_FORBIDDEN,
            )

        term_id = kwargs.get('term')
        term = get_object_or_404(Term, id=term_id)

        # Source-of-truth group ids: ClassTimeTable lessons ∪ legacy Group.teacher M2M
        group_ids_via_ctt = set(
            ClassTimeTable.objects
            .filter(teacher=teacher, group__isnull=False)
            .values_list('group_id', flat=True)
            .distinct()
        )
        group_ids_via_m2m = set(
            Group.objects
            .filter(teacher=teacher, deleted=False)
            .values_list('id', flat=True)
        )
        all_group_ids = group_ids_via_ctt | group_ids_via_m2m

        groups = (
            Group.objects
            .filter(id__in=all_group_ids, deleted=False)
            .select_related('class_number', 'color')
            .order_by('class_number__number')
        )
        group_ids = list(groups.values_list('id', flat=True))

        # (group_id, subject_id) pairs the teacher actually teaches, from ClassTimeTable
        ctt_pairs = (
            ClassTimeTable.objects
            .filter(teacher=teacher, group_id__in=group_ids)
            .values_list('group_id', 'subject_id')
            .distinct()
        )
        subject_ids_by_group = defaultdict(set)
        all_subject_ids = set()
        for gid, sid in ctt_pairs:
            if sid is None:
                continue
            subject_ids_by_group[gid].add(sid)
            all_subject_ids.add(sid)

        teacher_subject_ids = set(teacher.subject.values_list('id', flat=True))
        all_subject_ids |= teacher_subject_ids

        # One bulk query for GroupSubjects covering every (group, subject) cell we may render
        gs_qs = (
            GroupSubjects.objects
            .filter(group_id__in=group_ids, subject_id__in=all_subject_ids)
            .select_related('subject')
        )
        gs_by_group = defaultdict(dict)  # group_id -> {subject_id: GroupSubjects}
        for gs in gs_qs:
            gs_by_group[gs.group_id].setdefault(gs.subject_id, gs)

        # Flows belonging to this teacher
        flows = list(
            Flow.objects
            .filter(teacher=teacher)
            .select_related('subject')
        )
        flow_ids = [f.id for f in flows]

        # Single Test query for everything (group-tests + flow-tests) in this term
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

        # Groups section
        for group in groups:
            primary = subject_ids_by_group.get(group.id, set())
            subject_map = gs_by_group.get(group.id, {})
            primary_subjects = [subject_map[sid] for sid in primary if sid in subject_map]

            if primary_subjects:
                subjects = primary_subjects
            else:
                subjects = [
                    gs for sid, gs in subject_map.items() if sid in teacher_subject_ids
                ]

            children = []
            for gs in subjects:
                subj = gs.subject
                children.append({
                    "title": subj.name,
                    "id": subj.id,
                    "type": "subject",
                    "tableData": tests_by_group_subject.get((group.id, subj.id), []),
                })

            if not children:
                continue

            class_no = getattr(group.class_number, 'number', None)
            color_name = getattr(group.color, 'name', None)
            display_name = group.name or f"{class_no or '?'}-{color_name or '?'}"

            result.append({
                "title": display_name,
                "id": group.id,
                "type": "group",
                "children": children,
            })

        # Flows section
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
                teacher_group_subject_ids = set(
                    ClassTimeTable.objects
                    .filter(teacher=teacher, group=group)
                    .values_list('subject_id', flat=True)
                    .distinct()
                )
                teacher_flow_subject_ids = set(
                    Flow.objects
                    .filter(teacher=teacher, students=student, subject__isnull=False)
                    .values_list('subject_id', flat=True)
                    .distinct()
                )
                teacher_subjects_ids = teacher_group_subject_ids | teacher_flow_subject_ids

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




class TeacherGroupsAndFlowsView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        teacher = Teacher.objects.filter(user=request.user, deleted=False).first()
        if not teacher:
            return response.Response(
                {"detail": "Siz teacher emassiz"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Source of truth: any group this teacher has a ClassTimeTable lesson for.
        # Unioned with the legacy Group.teacher M2M for safety on older records.
        group_ids_via_ctt = set(
            ClassTimeTable.objects
            .filter(teacher=teacher, group__isnull=False)
            .values_list('group_id', flat=True)
            .distinct()
        )
        group_ids_via_m2m = set(
            Group.objects
            .filter(teacher=teacher, deleted=False)
            .values_list('id', flat=True)
        )
        all_group_ids = group_ids_via_ctt | group_ids_via_m2m

        groups = (
            Group.objects
            .filter(id__in=all_group_ids, deleted=False)
            .select_related('class_number', 'color')
            .annotate(students_count_=Count('students', distinct=True))
            .order_by('class_number__number')
        )
        group_ids = list(groups.values_list('id', flat=True))

        # Bulk-fetch (group_id, subject_id) pairs taught by this teacher
        ctt_pairs = (
            ClassTimeTable.objects
            .filter(teacher=teacher, group_id__in=group_ids)
            .values_list('group_id', 'subject_id')
            .distinct()
        )
        subject_ids_by_group = defaultdict(set)
        all_subject_ids = set()
        for gid, sid in ctt_pairs:
            if sid is None:
                continue
            subject_ids_by_group[gid].add(sid)
            all_subject_ids.add(sid)

        teacher_subject_ids = set(teacher.subject.values_list('id', flat=True))
        all_subject_ids |= teacher_subject_ids

        # Single bulk fetch of GroupSubjects for every group + every relevant subject
        gs_qs = (
            GroupSubjects.objects
            .filter(group_id__in=group_ids, subject_id__in=all_subject_ids)
            .select_related('subject')
        )
        gs_by_group = defaultdict(dict)  # group_id -> {subject_id: GroupSubjects}
        for gs in gs_qs:
            gs_by_group[gs.group_id].setdefault(gs.subject_id, gs)

        groups_data = []
        for group in groups:
            primary = subject_ids_by_group.get(group.id, set())
            subject_map = gs_by_group.get(group.id, {})
            primary_subjects = [subject_map[sid] for sid in primary if sid in subject_map]

            if primary_subjects:
                subjects = primary_subjects
            else:
                subjects = [
                    gs for sid, gs in subject_map.items() if sid in teacher_subject_ids
                ]

            class_no = getattr(group.class_number, 'number', None)
            color_name = getattr(group.color, 'name', None)
            display_name = group.name or f"{class_no or '?'}-{color_name or '?'}"

            groups_data.append({
                "id": group.id,
                "name": display_name,
                "type": "group",
                "students_count": group.students_count_,
                "subjects": [
                    {"id": gs.subject.id, "name": gs.subject.name}
                    for gs in subjects
                ],
            })

        flows = (
            Flow.objects
            .filter(teacher=teacher)
            .select_related('subject', 'level')
            .annotate(students_count_=Count('students', distinct=True))
        )

        flows_data = [
            {
                "id": flow.id,
                "name": flow.name,
                "type": "flow",
                "students_count": flow.students_count_,
                "subjects": (
                    [{"id": flow.subject.id, "name": flow.subject.name}]
                    if flow.subject_id else []
                ),
            }
            for flow in flows
        ]

        return response.Response({
            "groups": groups_data,
            "flows": flows_data,
        }, status=status.HTTP_200_OK)
