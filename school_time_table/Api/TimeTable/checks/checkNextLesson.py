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

        lesson_type = request.query_params.get('type')
        entity_id = request.query_params.get('id')

        current_time = datetime.now().time().replace(microsecond=0)

        if lesson_type == 'class':
            entity = Group.objects.select_related('branch').get(pk=entity_id)
            filter_field = 'group'
        else:
            entity = Flow.objects.select_related('branch').get(pk=entity_id)
            filter_field = 'flow'

        branch_hours = Hours.objects.filter(
            branch=entity.branch
        ).order_by('order')

        current_hour = branch_hours.filter(
            start_time__lte=current_time,
            end_time__gte=current_time
        ).first()

        if not current_hour:
            return Response({"msg": "No next lesson"})

        next_hour = branch_hours.filter(
            order__gt=current_hour.order
        ).order_by('order').first()

        if not next_hour:
            return Response({"msg": "No next lesson"})

        lesson = ClassTimeTable.objects.filter(
            week=week_day,
            hours=next_hour,
            **{filter_field: entity}
        ).select_related('room', 'hours', 'week').first()

        if not lesson:
            return Response({"msg": "No next lesson"})

        return Response({
            "day": lesson.week.name_uz,
            "room": lesson.room.name,
            "hour": lesson.hours.start_time.strftime("%H:%M")
        })
