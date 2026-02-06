from datetime import datetime

from rest_framework import generics, status
from rest_framework.response import Response

from lesson_plan.models import LessonPlan
from lesson_plan.serializers import LessonPlanGetSerializer
from school_time_table.models import ClassTimeTable

from lesson_plan.functions.utils import update_lesson_plan


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
