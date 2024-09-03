from datetime import datetime
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from flows.models import Flow
from school_time_table.models import ClassTimeTable, Hours
from time_table.models import WeekDays
from group.models import Group


class CheckNextLesson(APIView):
    def post(self, request, *args, **kwargs):
        weekday_name = datetime.today().strftime('%A')
        week_day = WeekDays.objects.get(name_en=weekday_name)
        lesson_type = self.request.query_params.get('type')
        entity_id = self.request.query_params.get('id')
        current_time = datetime.now().time().replace(microsecond=0)

        current_hour = Hours.objects.filter(start_time__lte=current_time, end_time__gte=current_time).first()
        if not current_hour:
            return Response({"msg": "No next lesson"})

        next_hour = Hours.objects.filter(order__gt=current_hour.order).order_by('order').first()
        if not next_hour:
            return Response({"msg": "No next lesson"})

        def get_lesson(filter_field, filter_value):
            return ClassTimeTable.objects.filter(
                week=week_day, hours=next_hour, **{filter_field: filter_value}
            ).first()

        if lesson_type == 'class':
            group = Group.objects.get(pk=entity_id)
            lesson = get_lesson('group', group)
        else:
            flow = Flow.objects.get(pk=entity_id)
            lesson = get_lesson('flow', flow)
        if not lesson:
            return Response({"msg": "No next lesson"})

        return Response({
            "day": lesson.week.name_uz,
            "room": lesson.room.name,
            "hour": lesson.hours.start_time.strftime("%H:%M")
        })
