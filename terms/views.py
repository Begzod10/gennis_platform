import io
import os
from collections import defaultdict

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.colors import black
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader, PdfWriter
from rest_framework import generics, views, response, status

from group.models import Group, GroupSubjects, GroupRating
from students.models import Student
from .functions import create_multiple_years
from .models import Assignment
from .serializers import TestCreateUpdateSerializer, Test, TermSerializer, Term
from django.db.models import Case, When, Value, IntegerField, Avg, Q
from flows.models import Flow

CERTIFICATE_TEMPLATE = os.path.join(settings.BASE_DIR, 'media', 'certificates', 'certificate_template.pdf')
FONT_DIR = os.path.join(settings.BASE_DIR, 'terms', 'fonts')

# PDF page dimensions (A4 portrait, points)
PAGE_W = 595.5
PAGE_H = 842.25
CENTER_X = PAGE_W / 2

# Register template-matching fonts once (script for the name, Poppins for body)
NAME_FONT = 'GreatVibes'
BODY_FONT = 'Poppins-Italic'
try:
    pdfmetrics.registerFont(TTFont(NAME_FONT, os.path.join(FONT_DIR, 'GreatVibes-Regular.ttf')))
    pdfmetrics.registerFont(TTFont(BODY_FONT, os.path.join(FONT_DIR, 'Poppins-Italic.ttf')))
except Exception:
    # Fall back to built-in fonts if the TTF files are missing
    NAME_FONT = 'Times-BoldItalic'
    BODY_FONT = 'Times-Italic'

ACADEMIC_YEAR = "2025-2026"

GRADE_THRESHOLDS = [
    (90, "A*"),
    (80, "A"),
    (70, "B"),
    (60, "C"),
    (50, "D"),
    (40, "E"),
    (30, "F"),
    (20, "G"),
    (0,  "U"),
]

GRADE_DESCRIPTIONS = {
    "A*": "Juda yuqori natija",
    "A":  "Excellent",
    "B":  "Very Good",
    "C":  "Good / Pass",
    "D":  "Satisfactory",
    "E":  "Minimum Pass",
    "F":  "Pass (IGCSE)",
    "G":  "Pass (IGCSE)",
    "U":  "Ungraded",
}


def _get_grade(score: float) -> str:
    for threshold, grade in GRADE_THRESHOLDS:
        if score >= threshold:
            return grade
    return "U"


def _get_level(class_number) -> str:
    if class_number is None:
        return "N/A"
    if 1 <= class_number <= 4:
        return "Primary"
    if 5 <= class_number <= 8:
        return "Secondary"
    if 9 <= class_number <= 11:
        return "Advanced"
    return "N/A"


def _student_group_scope(student):
    """
    O'quvchi HOZIR a'zo bo'lgan guruhlar (+ flow) testlari uchun Q filtri.
    Eski guruhdan qolib ketgan assignmentlar hisobga qo'shilmasligi uchun.
    """
    ids = list(student.groups_student.values_list('id', flat=True))
    return Q(test__group_id__in=ids) | Q(test__group_id__isnull=True)


def _compute_final_grade(student):
    """
    2025-2026 o'quv yili yakuniy bahosini hisoblaydi.
    Har chorak: Σ(fan ballari) / fanlar soni; yakuniy: chorak o'rtachalarining
    o'rtachasi. Ma'lumot bo'lmasa (None, None) qaytadi.
    """
    group_scope = _student_group_scope(student)
    total_avg = 0.0
    counted = 0
    for term in Term.objects.filter(academic_year=ACADEMIC_YEAR):
        assignments = (
            Assignment.objects
            .filter(student=student, test__term=term, test__deleted=False)
            .filter(group_scope)
            .select_related('test__subject')
        )
        subject_scores = defaultdict(float)
        subject_weights = defaultdict(int)
        seen_tests = defaultdict(set)
        for a in assignments:
            key = a.test.name.strip().lower().replace(' ', '')
            if key in seen_tests[a.test.subject_id]:
                continue
            seen_tests[a.test.subject_id].add(key)
            subject_scores[a.test.subject_id] += (a.test.weight * a.percentage) / 100
            subject_weights[a.test.subject_id] += a.test.weight
        if subject_scores:
            normalized = [
                score * 100 / subject_weights[sid]
                for sid, score in subject_scores.items()
                if subject_weights[sid] > 0
            ]
            if normalized:
                total_avg += sum(normalized) / len(normalized)
                counted += 1
    if counted == 0:
        return None, None
    final_score = total_avg / counted
    return final_score, _get_grade(final_score)


def _build_pdf_certificate(student, level: str, class_number, grade: str = None, director_fio: str = None) -> io.BytesIO:
    """
    Shablonga o'quvchining ismi, "completed the <level> year <N> with grade <G>."
    qatori va filial direktori FIO ni joylashtiradi.

    Koordinatalar (pdfplumber top → reportlab y = PAGE_H - top):
      Ism:            top 438-498  → rl y 344-404   (GreatVibes 56pt)
      Tavsif qatori:  top 527-540  → rl y 302-315   (Poppins-Italic 13pt)
      Direktor FIO:   top 708-721  → rl y 121-134   (Poppins-Italic 11pt)
    """
    overlay_buf = io.BytesIO()
    c = rl_canvas.Canvas(overlay_buf, pagesize=(PAGE_W, PAGE_H))

    # ── 1) O'quvchining ismi ──────────────────────────────────────────────────
    name = f"{(student.user.name or '').strip()} {(student.user.surname or '').strip()}".strip()
    size = 56
    c.setFont(NAME_FONT, size)
    max_w = PAGE_W - 150
    while c.stringWidth(name, NAME_FONT, size) > max_w and size > 20:
        size -= 1
        c.setFont(NAME_FONT, size)
    c.setFillColor(black)
    c.drawCentredString(CENTER_X, 360, name)

    # ── 2) "completed the <level> year <N> with grade <G>." ──────────────────
    # Cover the baked-in placeholder "has completed..." line at pdfplumber top=527
    from reportlab.lib.colors import Color as RLColor
    cream = RLColor(0.976, 0.953, 0.918)
    c.setFillColor(cream)
    c.rect(100, 298, 400, 22, fill=1, stroke=0)  # covers top=527→rl y=298-320

    level_word = (level or '').lower()
    year_no = class_number if class_number is not None else ''
    base = f"completed the {level_word} year {year_no}".rstrip()
    line = f"{base} with grade {grade}." if grade else f"{base}."
    line_size = 13
    c.setFont(BODY_FONT, line_size)
    max_line_w = PAGE_W - 90
    while c.stringWidth(line, BODY_FONT, line_size) > max_line_w and line_size > 9:
        line_size -= 0.5
        c.setFont(BODY_FONT, line_size)
    c.setFillColor(black)
    c.drawCentredString(CENTER_X, 305, line)

    # ── 3) Direktor FIO — chiziq va ism ──────────────────────────────────────
    if director_fio:
        c.setStrokeColor(black)
        c.setLineWidth(0.8)
        c.line(100, 136, 280, 136)          # signature line above name
        c.setFillColor(black)
        c.setFont(BODY_FONT, 11)
        c.drawString(100, 121, director_fio.upper())

    c.save()
    overlay_buf.seek(0)

    # ── Overlay'ni shablon ustiga birlashtiramiz ──────────────────────────────
    # NOTE: pypdf merge_page PREPENDS, so to put overlay ON TOP we merge
    # the template INTO the overlay (template becomes background).
    template_reader = PdfReader(CERTIFICATE_TEMPLATE)
    overlay_reader = PdfReader(overlay_buf)

    overlay_page = overlay_reader.pages[0]
    overlay_page.merge_page(template_reader.pages[0])

    writer = PdfWriter()
    writer.add_page(overlay_page)

    out_buf = io.BytesIO()
    writer.write(out_buf)
    out_buf.seek(0)
    return out_buf


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

            if not isinstance(percentage, (int, float)) or not (0 <= percentage <= 100):
                errors.append(
                    {"index": index, "error": "percentage 0 dan 100 gacha bo'lishi kerak", "data": item})
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
        subject_id = kwargs.get('subject_id', None)

        group = get_object_or_404(Group.objects.prefetch_related('students__user'), id=group_id)
        students = list(group.students.all())
        student_ids = [s.id for s in students]

        assignments_qs = Assignment.objects.filter(
            student_id__in=student_ids,
            test__term_id=term_id,
            test__deleted=False,
            test__group_id=group_id,
        ).select_related('test__subject')
        if subject_id:
            assignments_qs = assignments_qs.filter(test__subject_id=subject_id)

        assignments_by_student = defaultdict(list)
        for assignment in assignments_qs:
            assignments_by_student[assignment.student_id].append(assignment)

        response_data = []

        for student in students:
            subjects_data = defaultdict(
                lambda: {"subject_name": "", "assignments": [], "total_result": 0, "total_weight": 0, "average_result": 0})

            for assignment in assignments_by_student[student.id]:
                subj_id = assignment.test.subject.id
                calculated_result = (assignment.test.weight * assignment.percentage) / 100

                subjects_data[subj_id]["subject_name"] = assignment.test.subject.name
                subjects_data[subj_id]["assignments"].append(
                    {"test_name": assignment.test.name, "percentage": assignment.percentage,
                     "calculated_result": round(calculated_result, 2)})
                subjects_data[subj_id]["total_result"] += calculated_result
                subjects_data[subj_id]["total_weight"] += assignment.test.weight

            for subj_id, subj_data in subjects_data.items():
                if subj_data["total_weight"] > 0:
                    subj_data["average_result"] = round(subj_data["total_result"] * 100 / subj_data["total_weight"], 2)
                del subj_data["total_result"]
                del subj_data["total_weight"]

            response_data.append({"id": student.id, "first_name": student.user.name, "last_name": student.user.surname,
                                  "subjects": list(subjects_data.values())})

        return response.Response(response_data, status=status.HTTP_200_OK)


class TermsByStudent(views.APIView):
    def get(self, request, *args, **kwargs):
        student_id = kwargs.get('student_id')
        term_id = kwargs.get('term_id')
        subject_id = kwargs.get('subject_id', None)

        student = get_object_or_404(Student, id=student_id)

        group_scope = _student_group_scope(student)

        if subject_id:
            assignments = Assignment.objects.filter(
                student=student,
                test__term_id=term_id,
                test__deleted=False,
                test__subject_id=subject_id
            ).filter(group_scope).select_related('test__subject')
        else:
            assignments = Assignment.objects.filter(
                student=student,
                test__term_id=term_id,
                test__deleted=False
            ).filter(group_scope).select_related('test__subject')

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
            "total_weight": 0,
            "average_result": 0
        })

        total_result_all = 0
        total_weight_all = 0

        for assignment in assignments:
            subject_id = assignment.test.subject.id
            calculated_result = (assignment.test.weight * assignment.percentage) / 100

            subjects_data[subject_id]["subject_name"] = assignment.test.subject.name
            subjects_data[subject_id]["assignments"].append({
                "test_name": assignment.test.name,
                "test_id":assignment.test.id,
                "percentage": assignment.percentage,
                "calculated_result": round(calculated_result, 2)
            })
            subjects_data[subject_id]["total_result"] += calculated_result
            subjects_data[subject_id]["total_weight"] += assignment.test.weight

            total_result_all += calculated_result
            total_weight_all += assignment.test.weight

        for subject_id, subj_data in subjects_data.items():
            if subj_data["total_weight"] > 0:
                subj_data["average_result"] = round(subj_data["total_result"] * 100 / subj_data["total_weight"], 2)
            del subj_data["total_weight"]
            del subj_data["total_result"]
            response_data["subjects"].append(subj_data)

        if total_weight_all > 0:
            response_data["total_result"] = round(total_result_all, 2)
            response_data["average_result"] = round(total_result_all * 100 / total_weight_all, 2)

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


class StudentCertificateView(views.APIView):
    """
    GET /api/terms/certificate/<student_id>/

    Shablon asosida PDF sertifikat qaytaradi. Sertifikatda o'quvchining ismi,
    darajasi (level + year) va yakuniy bahosi (A*, A, B ...) bo'ladi.
    Daraja: class_number bo'yicha (1-4 Primary, 5-8 Secondary, 9-11 Advanced).
    """

    def get(self, request, student_id):
        student = get_object_or_404(
            Student.objects.select_related('user__branch', 'class_number'),
            id=student_id
        )

        class_number = student.class_number.number if student.class_number else None
        level = _get_level(class_number)
        _, grade = _compute_final_grade(student)

        branch = student.user.branch if student.user else None
        director_fio = (branch.director_fio or '').strip() if branch else ''

        buf = _build_pdf_certificate(student, level, class_number, grade, director_fio=director_fio or None)

        name = f"{student.user.name}_{student.user.surname}".replace(' ', '_')
        resp = HttpResponse(buf.read(), content_type='application/pdf')
        resp['Content-Disposition'] = f'attachment; filename="certificate_{name}_{ACADEMIC_YEAR}.pdf"'
        return resp


class CertificateDataView(views.APIView):
    """
    GET /api/terms/certificate-data/<student_id>/

    2025-2026 o'quv yili bo'yicha har chorak, har fan, har test batafsil
    breakdown + pastida PDF sertifikat yuklab olish havolasi.
    """

    def get(self, request, student_id):
        student = get_object_or_404(
            Student.objects.select_related('user', 'class_number'),
            id=student_id
        )

        terms = list(Term.objects.filter(academic_year=ACADEMIC_YEAR).order_by('quarter'))
        group_scope = _student_group_scope(student)

        quarters = []
        total_avg = 0.0
        counted_terms = 0

        for term in terms:
            assignments = (
                Assignment.objects
                .filter(student=student, test__term=term, test__deleted=False)
                .filter(group_scope)
                .select_related('test__subject')
                .order_by('test__subject__name', 'test__name')
            )

            # Group by subject, deduplicate tests by normalized name (case-insensitive)
            subjects_map = defaultdict(lambda: {
                'subject_name': '',
                'tests': [],
                '_total_score': 0.0,
                '_total_weight': 0,
                '_seen': set(),
            })

            for a in assignments:
                sid = a.test.subject_id
                key = a.test.name.strip().lower().replace(' ', '')
                if key in subjects_map[sid]['_seen']:
                    continue
                subjects_map[sid]['_seen'].add(key)
                score = round((a.test.weight * a.percentage) / 100, 2)
                subjects_map[sid]['subject_name'] = a.test.subject.name
                subjects_map[sid]['tests'].append({
                    'test_name': a.test.name,
                    'weight': a.test.weight,
                    'percentage': a.percentage,
                    'calculated_score': score,
                })
                subjects_map[sid]['_total_score'] += score
                subjects_map[sid]['_total_weight'] += a.test.weight

            subject_list = []
            for sd in subjects_map.values():
                total_w = sd.pop('_total_weight')
                total_s = sd.pop('_total_score')
                sd.pop('_seen')
                sd['subject_score'] = round(total_s * 100 / total_w, 2) if total_w > 0 else 0.0
                subject_list.append(sd)

            subject_count = len(subject_list)
            if subject_count > 0:
                term_avg = round(sum(s['subject_score'] for s in subject_list) / subject_count, 2)
                total_avg += term_avg
                counted_terms += 1
                term_grade = _get_grade(term_avg)
            else:
                term_avg = None
                term_grade = None

            quarters.append({
                'quarter': term.quarter,
                'subjects': subject_list,
                'subject_count': subject_count,
                'quarter_avg': term_avg,
                'quarter_grade': term_grade,
            })

        if counted_terms == 0:
            return response.Response(
                {"detail": "Bu o'quvchi uchun 2025-2026 o'quv yilida hech qanday baho topilmadi."},
                status=status.HTTP_404_NOT_FOUND
            )

        final_score = round(total_avg / counted_terms, 2)
        grade = _get_grade(final_score)
        level = _get_level(student.class_number.number if student.class_number else None)

        certificate_url = request.build_absolute_uri(
            f'/api/terms/certificate/{student_id}/'
        )

        return response.Response({
            'student': {
                'id': student.id,
                'name': student.user.name,
                'surname': student.user.surname,
                'level': level,
            },
            'academic_year': ACADEMIC_YEAR,
            'quarters': quarters,
            'final_score': final_score,
            'final_grade': grade,
            'grade_description': GRADE_DESCRIPTIONS.get(grade, ''),
            'certificate_url': certificate_url,
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
