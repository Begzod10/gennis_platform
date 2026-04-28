from datetime import datetime

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from group.models import Group
from time_table.models import WeekDays


class CheckGroupNextLesson(APIView):
    def get(self, request):

        group = get_object_or_404(Group, pk=self.request.query_params.get('id'))
        weekday_name = datetime.today().strftime('%A')
        week_day = WeekDays.objects.get(name_en=weekday_name)
        if not group.group_time_table.all():
            return Response({"msg": "No next lesson"})
        orders = [time_table.week.order for time_table in group.group_time_table.all()]

        def get_next_or_smallest_number(numbers, current):

            numbers = sorted(numbers)

            next_numbers = [num for num in numbers if num > current]

            if next_numbers:
                return min(next_numbers)
            else:
                return numbers[0]

        next_number = get_next_or_smallest_number(orders, week_day.order)
        next_week = WeekDays.objects.get(order=next_number)
        next_lesson = group.group_time_table.filter(week=next_week).first()

        if not next_lesson:
            return Response({"msg": "No next lesson"})
        return Response({'room': next_lesson.room.name, 'hour': next_lesson.start_time.strftime('%H:%M'),
                         'day': next_lesson.week.name_uz})
