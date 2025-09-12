from datetime import timedelta
from group.models import Group, GroupSubjects, GroupSubjectsCount
from students.models import Student, StudentSubject, StudentSubjectCount
from flows.models import Flow
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime
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


class TimeTableDataView(APIView):
    def get(self, request):
        subject_id = self.request.query_params.get('subject_id')
        group_id = self.request.query_params.get('group_flow')
        type_list = self.request.query_params.get('type')
        date = self.request.query_params.get('date')
        time_table_id = self.request.query_params.get('time_table_id')
        class_time_table = ClassTimeTable.objects.get(id=time_table_id)

        if not class_time_table:
            group = None
            flow = None
            if type_list == 'group':
                group = Group.objects.get(pk=group_id)
            else:
                flow = Flow.objects.get(pk=group_id)

            subject_id = flow.subject_id if not subject_id else subject_id
            students = group.students.all() if group else flow.students.all()
            date = datetime.strptime(date, '%Y-%m-%d')
            month_date = date.strftime('%Y-%m')
            month_date = datetime.strptime(month_date, '%Y-%m')
        else:
            group = class_time_table.group
            subject_id = class_time_table.subject_id if not subject_id else subject_id
            students = class_time_table.students.all()
            month = class_time_table.date.month
            year = class_time_table.date.year
            month_date = datetime(year, month, 1)
        info = {"students": []}
        if group:
            group_subjects = GroupSubjects.objects.filter(group=group, subject_id=subject_id).first()
            group_subjects = GroupSubjectsCount.objects.filter(group_subjects=group_subjects,
                                                               date=month_date).count()
            info['group_subjects'] = group_subjects if group_subjects else 0
        if subject_id:
            for student in students:
                student_subject = StudentSubject.objects.filter(student=student,
                                                                subject_id=subject_id).first()
                student_subject_count = StudentSubjectCount.objects.filter(date=month_date,
                                                                           student_subjects=student_subject).count()
                info['students'].append({
                    'student': student.user.name + ' ' + student.user.surname,
                    'hours': student_subject_count if student_subject_count else 0,
                    "total_hours": student_subject.hours
                })

        return Response(info)
