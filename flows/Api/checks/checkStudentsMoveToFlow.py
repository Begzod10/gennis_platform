import json

from rest_framework.response import Response
from rest_framework.views import APIView

from group.models import Group
from flows.models import Flow
from students.models import Student

from students.serializers import StudentListSerializer


class CheckStudentsMoveToFlow(APIView):
    def post(self, request, *args, **kwargs):
        flow_id = self.request.query_params.get('flow_id')
        to_flow_id = self.request.query_params.get('to_flow_id')
        flow = Flow.objects.get(id=flow_id)
        to_flow = Flow.objects.get(id=to_flow_id)
        data = json.loads(request.body)
        errors = []
        students = Student.objects.filter(id__in=data['students'])
        for student in students:
            student_status = True
            for flow_time_table in flow.classtimetable_set.all():
                student_time_table = student.class_time_table.filter(hours_id=flow_time_table.hours_id,
                                                                     week_id=flow_time_table.week_id).first()
                if student_time_table:
                    student_status = False
                    if student_time_table.flow_id is None:
                        text = f"Bu vaqtda '{student.user.name} {student.user.surname}' o'quvchisining  '{student_time_table.room.name}' xonasida  '{student_time_table.group.class_number.number}-{student_time_table.group.color.name}' sinifida darsi bor"
                    else:
                        text = f"Bu vaqtda '{student.user.name} {student.user.surname}' o'quvchisining  '{student_time_table.room.name}' xonasida  '{student_time_table.flow.name}' patokida darsi bor"
                    errors.append(text)
            if student_status:
                flow.students.remove(student)
                to_flow.students.add(student)
        return Response({'errors': errors})
