import json
from datetime import datetime

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from group.models import Group
from group.serializers import GroupClassSerializer
from students.models import Student, StudentHistoryGroups, DeletedStudent
from students.serializers import StudentListSerializer


class GetCheckedStudentsForClassTimeTable(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        students_list = []
        branch_id = self.request.query_params.get('branch')
        group_id = self.request.query_params.get('group')
        group = Group.objects.get(id=group_id)

        data = json.loads(request.body)
        ignore_students = data['ignore_students']
        deleted = DeletedStudent.objects.filter(deleted=False).values_list('student_id', flat=True)
        student_deleted_groups = Group.objects.filter(
            deleted=True, branch_id=branch_id
        ).values_list('id', flat=True)

        students = Student.objects.filter(
            groups_student__isnull=True,
            user__branch_id=branch_id,
            class_number=group.class_number
        ).exclude(id__in=ignore_students).distinct()
        for student in students:

            student_data = StudentListSerializer(student).data
            class_time_tables = student.class_time_table.filter(flow__isnull=False).all()

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
                student_history_group = StudentHistoryGroups.objects.filter(group=group, student=student).update(
                    left_day=today, reason=reason)

                group.students.remove(student)
                to_group.students.add(student)
                StudentHistoryGroups.objects.create(group=to_group, student=student,
                                                    teacher=to_group.teacher.all()[0],
                                                    joined_day=today)
        serializer = GroupClassSerializer(group)
        return Response({'data': serializer.data, 'errors': errors})
