import json

from rest_framework.response import Response
from rest_framework.views import APIView

from students.models import Student
from students.serializers import StudentListSerializer
from teachers.models import Teacher
from teachers.serializers import TeacherSerializerRead


class GetCheckedStudentsTeachers(APIView):
    def post(self, request, branch_id, subject_id):
        location_id = branch_id
        teachers_list = []
        students_list = []
        data = json.loads(request.body)
        time_tables = data['time_tables']
        ignore_students = data['ignore_students']
        ignore_teacher = data['ignore_teacher']
        students = Student.objects.filter(
            user__branch_id=location_id,
            deleted_student_student__isnull=True,
            subject__student__in=[subject_id]
        ).exclude(id__in=ignore_students).distinct()
        for student in students:
            should_add_student = False
            student_data = StudentListSerializer(student).data
            for time_table in time_tables:

                time_table_st = student.group_time_table.filter(week_id=time_table['week'],
                                                                start_time__gte=time_table['start_time'],
                                                                end_time__lte=time_table['end_time']).first()

                if time_table_st:
                    student_data['extra_info'] = {
                        'status': False,
                        'reason': f"{student.user.name} {student.user.surname} o'quvchini {time_table.group.name} guruhida darsi bor"
                    }
                else:
                    student_data['extra_info'] = {
                        'status': True,
                        'reason': ''
                    }
                if not should_add_student:
                    should_add_student = True
            if should_add_student:
                students_list.append(student_data)
        teachers = Teacher.objects.filter(user__branch_id=location_id, subject__in=[subject_id]).exclude(
            id=ignore_teacher)
        for teacher in teachers:
            teacher_data = TeacherSerializerRead(teacher).data
            should_add_teacher = False
            for time_table in time_tables:
                time_table_tch = teacher.group_time_table.filter(week_id=time_table['week'],
                                                                 start_time__gte=time_table['start_time'],
                                                                 end_time__lte=time_table['end_time']).first()
                if time_table_tch:
                    print(time_table_tch)
                    teacher_data['extra_info'] = {
                        'status': False,
                        'reason': f"{teacher.user.name} {teacher.user.surname} o'quvchini {time_table_tch.group.name} guruhida darsi bor"
                    }
                else:
                    teacher_data['extra_info'] = {
                        'status': True,
                        'reason': ''
                    }
                if not should_add_teacher:
                    should_add_teacher = True
            if should_add_teacher:
                teachers_list.append(teacher_data)

        return Response(
            {'students': students_list, 'teachers': teachers_list})
