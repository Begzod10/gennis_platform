from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from parents.models import Parent
from students.models import Student, DeletedStudent
from parents.serializers.crud import StudentSerializerMobile
from attendances.models import AttendancePerMonth
from rest_framework.views import APIView
from django.utils import timezone
from datetime import date
from django.db.models.functions import ExtractMonth, ExtractYear
from rest_framework.response import Response
from mobile.parents.serializers import ClassTimeTableSerializer, StudentDailyAttendanceMobileSerializer, \
    AttendancePerMonthParentSerializer
from school_time_table.models import ClassTimeTable
from attendances.models import StudentDailyAttendance
from terms.models import Assignment, Term
from terms.serializers import TermSerializer
from collections import defaultdict


class ChildrenListView(generics.ListAPIView):
    serializer_class = StudentSerializerMobile
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            parent = Parent.objects.get(user=self.request.user)
            return parent.children.all()
        except Parent.DoesNotExist:
            return Student.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ChildrenDebtMonthView(APIView):
    serializer_class = AttendancePerMonthParentSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student_id = request.query_params.get('student_id')
        student = Student.objects.get(pk=student_id)
        group = student.groups_student.first()
        today = timezone.localdate()
        academic_start_year = today.year if today.month >= 9 else (today.year - 1)

        ay_param = self.request.query_params.get("ay")
        if ay_param and ay_param.isdigit():
            academic_start_year = int(ay_param)

        start_date = date(academic_start_year, 9, 1)  # inclusive
        end_date = date(academic_start_year + 1, 7, 1)  # exclusive
        if not group:
            deleted_student = DeletedStudent.objects.filter(student_id=student_id).order_by("-deleted_date").first()
            qs = (AttendancePerMonth.objects.filter(student_id=student_id, group_id=deleted_student.group_id,
                                                    month_date__gte=start_date, month_date__lt=end_date, ).annotate(
                month_number=ExtractMonth('month_date'),
                year_number=ExtractYear('month_date'), ).order_by('month_date'))
        else:
            qs = (
                AttendancePerMonth.objects.filter(student_id=student_id, group_id=group.id, month_date__gte=start_date,
                                                  month_date__lt=end_date, ).annotate(
                    month_number=ExtractMonth('month_date'),
                    year_number=ExtractYear('month_date'), ).order_by('month_date'))

        # Optional: ?month=1..12 mapped to the correct year in this academic window
        month_str = self.request.query_params.get("month")
        if month_str and month_str.isdigit():
            m = int(month_str)
            if 1 <= m <= 12:
                year_for_month = academic_start_year if m in (9, 10, 11, 12) else academic_start_year + 1
                qs = qs.filter(month_date__year=year_for_month, month_date__month=m)
        return Response(self.serializer_class(qs, many=True).data)


class ChildrenTodayTimeTableView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Verify the student belongs to this parent
            student_id = request.query_params.get('student_id')
            parent = Parent.objects.get(user=request.user)
            if not parent.children.filter(id=student_id).exists():
                return Response(
                    {'error': 'Student not found or not your child'},
                    status=403
                )
            # Get today's date
            today = date.today()
            # Get today's timetable for the student
            timetable = ClassTimeTable.objects.filter(
                students__id=student_id,
                date=today
            ).select_related(
                'hours', 'room', 'teacher', 'subject', 'group', 'week'
            ).order_by('hours__start_time')  # Order by lesson time

            serializer = ClassTimeTableSerializer(timetable, many=True)

            return Response({
                'student_id': student_id,
                'date': today,
                'lessons': serializer.data
            })
        except Parent.DoesNotExist:
            return Response({'error': 'Parent profile not found'}, status=404)


class ChildrenAttendanceMonthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get parameters from request
            student_id = request.query_params.get('student_id')
            month = request.query_params.get('month')
            year = request.query_params.get('year')

            # Validate required parameters
            if not student_id:
                return Response(
                    {'error': 'student_id is required'},
                    status=400
                )

            # Use current month/year if not provided
            today = date.today()
            month = int(month) if month else today.month
            year = int(year) if year else today.year

            # Validate month and year
            if not (1 <= month <= 12):
                return Response(
                    {'error': 'month must be between 1 and 12'},
                    status=400
                )

            # Verify the student belongs to this parent
            parent = Parent.objects.get(user=request.user)
            if not parent.children.filter(id=student_id).exists():
                return Response(
                    {'error': 'Student not found or not your child'},
                    status=403
                )

            # Get attendances through monthly_summary relation
            attendances = StudentDailyAttendance.objects.filter(
                monthly_summary__student_id=student_id,
                monthly_summary__year=year,
                monthly_summary__month=month,

            ).select_related('monthly_summary').order_by('day')

            serializer = StudentDailyAttendanceMobileSerializer(attendances, many=True)

            return Response({
                'student_id': student_id,
                'month': month,
                'year': year,
                'attendances': serializer.data
            })

        except Parent.DoesNotExist:
            return Response({'error': 'Parent profile not found'}, status=404)
        except ValueError:
            return Response({'error': 'Invalid month or year format'}, status=400)


# https://school.gennis.uz/api/terms/education-years/


class ListTermChildren(generics.ListAPIView):
    queryset = Term.objects.all()
    serializer_class = TermSerializer

    def get_queryset(self):
        academic_year = self.request.query_params.get('academic_year')
        return self.queryset.filter(academic_year=academic_year)


class TermsByChildren(APIView):
    def get(self, request, *args, **kwargs):
        student_id = request.query_params.get('student_id')
        term_id = request.query_params.get('term_id')
        subject_id = request.query_params.get('subject_id', None)

        student = Student.objects.get(pk=student_id)
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

        return Response(response_data, status=status.HTTP_200_OK)
