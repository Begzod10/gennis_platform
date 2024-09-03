import json

from rest_framework.response import Response
from rest_framework.views import APIView

from group.models import Group
from flows.models import Flow

from students.serializers import StudentListSerializer


class GetFlowCheckedStudentsForClassTimeTable(APIView):
    def post(self, request):
        flow_id = self.request.query_params.get('flow')
        branch_id = self.request.query_params.get('branch')
        flow = Flow.objects.get(pk=flow_id)
        ignore_students = json.loads(request.body)['ignore_students']

        groups = Group.objects.filter(deleted=False, class_number__isnull=False, branch_id=branch_id).all()
        classes = [self.get_group_info(group, flow, ignore_students) for group in groups]

        classes = [cls for cls in classes if cls]

        return Response({'classes': classes})

    def get_group_info(self, group, flow, ignore_students):
        students = group.students.exclude(id__in=ignore_students).all()

        if not students.exists():
            return None

        info = {
            'id': group.id,
            'class_number': {'number': group.class_number.number},
            'color': {'name': group.color.name},
            'students': [self.get_student_info(student, flow) for student in students]
        }
        return info

    def get_student_info(self, student, flow):
        student_data = StudentListSerializer(student).data
        if flow.classtimetable_set.all():
            for flow_time_table in flow.classtimetable_set.all():
                student_time_table = student.class_time_table.filter(
                    hours_id=flow_time_table.hours_id,
                    week_id=flow_time_table.week_id
                ).first()

                if student_time_table:
                    text = self.get_student_conflict_text(student, student_time_table)
                    student_data['extra_info'] = {'status': False, 'reason': text}
                else:
                    student_data['extra_info'] = {'status': True, 'reason': ''}
        else:
            student_data['extra_info'] = {'status': True, 'reason': ''}
        return student_data

    def get_student_conflict_text(self, student, student_time_table):
        if student_time_table.flow_id is None:
            return (
                f"Bu vaqtda '{student.user.name} {student.user.surname}' o'quvchisining  "
                f"'{student_time_table.room.name}' xonasida  "
                f"'{student_time_table.group.class_number.number}-{student_time_table.group.color.name}' sinifida darsi bor"
            )
        return (
            f"Bu vaqtda '{student.user.name} {student.user.surname}' o'quvchisining  "
            f"'{student_time_table.room.name}' xonasida  '{student_time_table.flow.name}' patokida darsi bor"
        )
