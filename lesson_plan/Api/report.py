from datetime import datetime
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from school_time_table.models import ClassTimeTable
from time_table.models import WeekDays
from lesson_plan.models import LessonPlan
from branch.models import Branch

class DailyLessonPlanReportView(APIView):
    """
    Returns a report of lesson plans for a given branch and date.
    Filters ClassTimeTable by branch and weekday.
    """
    def get(self, request):
        branch_id = request.query_params.get('branch_id')
        date_str = request.query_params.get('date') # Expected format: YYYY-MM-DD

        if not branch_id:
            return Response({"error": "branch_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            target_date = datetime.now().date()

        # Get weekday name to filter ClassTimeTable
        weekday_name = target_date.strftime('%A')
        try:
            week_day = WeekDays.objects.get(name_en=weekday_name)
        except WeekDays.DoesNotExist:
            return Response({"error": f"Weekday {weekday_name} not found in database"}, status=status.HTTP_404_NOT_FOUND)

        # Filter ClassTimeTable for the branch and day
        # Exclude entries where both group and flow are null
        timetables = ClassTimeTable.objects.filter(
            branch_id=branch_id,
            week=week_day
        ).filter(
            Q(group__isnull=False) | Q(flow__isnull=False)
        ).select_related('teacher__user', 'group', 'flow', 'subject', 'hours').order_by('hours__order')

        # Get all lesson plans for these timetables on the target date
        lesson_plans = LessonPlan.objects.filter(
            class_time_table__in=timetables,
            date=target_date
        ).filter(
            Q(group__isnull=False) | Q(flow__isnull=False)
        ).distinct()
        lp_map = {lp.class_time_table_id: lp for lp in lesson_plans}

        # Grouping by teacher
        teacher_map = {}

        for tt in timetables:
            teacher_id = tt.teacher.id if tt.teacher else None
            if not teacher_id:
                continue

            if teacher_id not in teacher_map:
                teacher_map[teacher_id] = {
                    "id": teacher_id,
                    "full_name": tt.teacher.user.get_full_name() if tt.teacher.user else "N/A",
                    "phone": tt.teacher.user.phone if tt.teacher.user else "N/A",
                    "lessons": []
                }

            lp = lp_map.get(tt.id)
            
            has_lesson_plan = False
            ai_score = None
            ai_conclusion = None
            status_text = "no_plan"
            
            if lp:
                # Check if it has content
                if lp.objective or lp.main_lesson or lp.homework:
                    has_lesson_plan = True
                    if lp.ball is not None:
                        status_text = "evaluated"
                    else:
                        status_text = "pending"
                
                ai_score = lp.ball
                ai_conclusion = lp.conclusion

            teacher_map[teacher_id]["lessons"].append({
                "timetable_id": tt.id,
                "group": {
                    "id": tt.group.id if tt.group else None,
                    "name": tt.group.name if tt.group else None
                },
                "flow": {
                    "id": tt.flow.id if tt.flow else None,
                    "name": tt.flow.name if tt.flow else None
                },
                "subject": {
                    "id": tt.subject.id if tt.subject else None,
                    "name": tt.subject.name if tt.subject else "N/A"
                },
                "hours": {
                    "start": tt.hours.start_time.strftime('%H:%M') if tt.hours else "N/A",
                    "end": tt.hours.end_time.strftime('%H:%M') if tt.hours else "N/A"
                },
                "has_lesson_plan": has_lesson_plan,
                "ai_score": ai_score,
                "ai_conclusion": ai_conclusion,
                "status": status_text,
                "date": target_date.strftime('%Y-%m-%d')
            })

        return Response(list(teacher_map.values()), status=status.HTTP_200_OK)
