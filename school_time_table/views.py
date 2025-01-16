from datetime import timedelta

from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ClassTimeTable, Hours


class TimeTableAPIView(APIView):
    def get(self, request, pk):
        today = timezone.now().date()

        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)

        timetable = []
        current_date = start_date

        all_hours = Hours.objects.all().order_by('start_time')

        while current_date <= end_date:
            lessons = ClassTimeTable.objects.filter(date=current_date, group_id=pk).order_by('hours__start_time')
            day_lessons = []

            lessons_by_hour = {lesson.hours: lesson for lesson in lessons}

            for hour in all_hours:
                if hour in lessons_by_hour:
                    lesson = lessons_by_hour[hour]
                    day_lessons.append({
                        'time': f"{lesson.hours.start_time.strftime('%H:%M')} - {lesson.hours.end_time.strftime('%H:%M')}",
                        'subject': lesson.subject.name if lesson.subject else None,
                        'teacher': f"{lesson.teacher.user.name + ' ' + lesson.teacher.user.surname}" if lesson.teacher else None,
                        'teacher_color': lesson.teacher.color if lesson.teacher else None,
                        'room': lesson.room.name if lesson.room else None,
                    })
                else:
                    day_lessons.append({
                        'time': f"{hour.start_time.strftime('%H:%M')} - {hour.end_time.strftime('%H:%M')}",
                        'subject': None,
                        'teacher': None,
                        'teacher_color': None,
                        'room': None,
                    })

            timetable.append({
                'day': current_date.strftime('%A'),
                'lessons': day_lessons
            })

            current_date += timedelta(days=1)

        response_data = {
            'times': [f"{hour.start_time.strftime('%H:%M')} - {hour.end_time.strftime('%H:%M')}" for hour in all_hours],
            'days': timetable
        }
        return Response(response_data)
