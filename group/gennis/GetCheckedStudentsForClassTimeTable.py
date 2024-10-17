import json
from datetime import datetime
from rest_framework.response import Response
from rest_framework.views import APIView

from students.models import Student, StudentHistoryGroups
from students.serializers import StudentListSerializer
from teachers.models import Teacher
from teachers.serializers import TeacherSerializerRead
from group.models import Group
from group.serializers import GroupClassSerializer
from rest_framework.permissions import IsAuthenticated

class GetCheckedStudentsForClassTimeTable(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        students_list = []
        branch_id = self.request.query_params.get('branch')
        group_id = self.request.query_params.get('group')
        data = json.loads(request.body)
        ignore_students = data['ignore_students']
        students = Student.objects.filter(groups_student__isnull=True, user__branch_id=branch_id,
                                          deleted_student_student__deleted=True,deleted_student_student_new__isnull=True).exclude(
            id__in=ignore_students).distinct()
        group = Group.objects.get(id=group_id)
        for student in students:
            should_add_student = False
            student_data = StudentListSerializer(student).data
            class_time_tables = student.class_time_table.filter(flow__isnull=False).all()
            if not should_add_student:
                should_add_student = True
            if class_time_tables:
                for class_time_table in class_time_tables:
                    group_time_table = group.classtimetable_set.filter(hours_id=class_time_table.hours_id,
                                                                       week_id=class_time_table.week_id,
                                                                       branch_id=branch_id, flow__isnull=False).first()

                    if group_time_table:
                        student_data['extra_info'] = {
                            'status': False,
                            'reason': f"{student.user.name} {student.user.surname} ning {class_time_table.flow.name} patokidagi dars jadvali sinif dars jadvaliga togri kelmadi"
                        }
                    else:
                        student_data['extra_info'] = {
                            'status': True,
                            'reason': ''
                        }
            else:
                student_data['extra_info'] = {
                    'status': True,
                    'reason': ''
                }
            if should_add_student:
                students_list.append(student_data)
        return Response({'students': students_list})


class CheckedStudentsMoveToGroup(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        today = datetime.now()
        errors = []
        branch_id = self.request.query_params.get('branch')
        group_id = self.request.query_params.get('group')
        data = json.loads(request.body)
        students = Student.objects.filter(pk__in=data['students']).distinct()
        group = Group.objects.get(id=group_id)
        to_group_id = data.get('to_group_id')
        to_group = Group.objects.get(pk=to_group_id)
        reason = data.get('reason')
        for student in students:
            student_status = True
            class_time_tables = student.class_time_table.filter(flow__isnull=False).all()
            if class_time_tables:
                for class_time_table in class_time_tables:
                    group_time_table = group.classtimetable_set.filter(hours_id=class_time_table.hours_id,
                                                                       week_id=class_time_table.week_id,
                                                                       branch_id=branch_id, flow__isnull=False).first()

                    if group_time_table:
                        student_status = False
                        errors.append(
                            f"{student.user.name} {student.user.surname} ning {class_time_table.flow.name} patokidagi dars jadvali {group.class_number.number}-{group.color.name} sinif dars jadvaliga togri kelmadi")

            if student_status:
                student_history_group = StudentHistoryGroups.objects.get(group=group, student=student)
                student_history_group.left_day = today
                student_history_group.reason = reason
                student_history_group.save()
                group.students.remove(student)
                to_group.students.add(student)
                StudentHistoryGroups.objects.create(group=to_group, student=student,
                                                    teacher=to_group.teacher.all()[0],
                                                    joined_day=today)
        serializer = GroupClassSerializer(group)
        return Response({'data': serializer.data, 'errors': errors})



