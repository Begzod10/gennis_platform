from datetime import datetime

from rest_framework import generics, status
from rest_framework.response import Response

from lesson_plan.models import LessonPlan
from lesson_plan.serializers import LessonPlanGetSerializer
from school_time_table.models import ClassTimeTable



class GetLessonPlanView(generics.RetrieveAPIView):
    serializer_class = LessonPlanGetSerializer

    # permission_classes = [IsAuthenticated]

    def get_object(self):
        day = self.request.data.get('day') or self.request.query_params.get('day')
        month = self.request.data.get('month') or self.request.query_params.get('month')
        year = self.request.data.get('year') or self.request.query_params.get('year')
        group_id = self.request.data.get('group_id') or self.request.query_params.get('group_id')

        time_table = ClassTimeTable.objects.get(id=group_id)
        date = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d")
        return LessonPlan.objects.filter(group_id=time_table.group_id, date=date).first()

    def get(self, request, *args, **kwargs):
        lesson_plan = self.get_object()
        if not lesson_plan:
            return Response({"msg": "Lesson plan not found"}, status=status.HTTP_200_OK)

        current_date = datetime.now().date()
        status_flag = current_date < lesson_plan.date
        return Response({"lesson_plan": LessonPlanGetSerializer(lesson_plan).data, "status": status_flag})


class LessonPlanListView(generics.ListAPIView):
    serializer_class = LessonPlanGetSerializer

    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        group_id = self.kwargs['group_id']
        # update_lesson_plan(374)
        group = ClassTimeTable.objects.get(id=group_id)
        group_id = group.group.id
        date = self.kwargs.get('date')
        if date:
            date = datetime.strptime(date, "%Y-%m")
            return LessonPlan.objects.filter(group_id=group_id, date__year=date.year, date__month=date.month)
        return LessonPlan.objects.filter(group_id=group_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        days = sorted([lp.date.day for lp in queryset])
        months = sorted(list(set([lp.date.month for lp in queryset])))
        years = sorted(list(set([lp.date.year for lp in queryset])))

        return Response({"month_list": months, "years_list": years, "month": months[0] if months else None,
                         "year": years[0] if years else None, "days": days})


from rest_framework.views import APIView
from lesson_plan.serializers import TeacherLessonPlanRangeSerializer

class TeacherLessonPlanRangeView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        teacher_id = request.query_params.get('teacher_id')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        if not teacher_id:
            return Response({"error": "teacher_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not start_date_str or not end_date_str:
            return Response({"error": "Both start_date and end_date are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)

        if start_date > end_date:
            return Response({"error": "start_date must be before or equal to end_date"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve lesson plans
        lesson_plans = LessonPlan.objects.filter(
            teacher_id=teacher_id,
            date__range=[start_date, end_date]
        ).select_related(
            'teacher__user', 
            'group', 
            'flow', 
            'class_time_table__hours', 
            'class_time_table__room', 
            'class_time_table__subject', 
            'class_time_table__week'
        ).order_by('date')

        serializer = TeacherLessonPlanRangeSerializer(lesson_plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
