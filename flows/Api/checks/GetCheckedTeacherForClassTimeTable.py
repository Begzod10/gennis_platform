import json
from rest_framework.response import Response
from rest_framework.views import APIView

from flows.models import Flow
from teachers.models import Teacher

from teachers.serializers import TeacherSerializerRead


class GetCheckedTeacherForClassTimeTable(APIView):
    def post(self, request):
        flow_id = self.request.query_params.get('flow')
        branch_id = self.request.query_params.get('branch')
        data = json.loads(request.body)
        ignore_teacher = data['ignore_teacher']
        teachers = Teacher.objects.filter(user__branch_id=branch_id).exclude(pk=ignore_teacher)

        flow = Flow.objects.get(pk=flow_id)
        teachers_list = []
        for teacher in teachers:
            teacher_data = TeacherSerializerRead(teacher).data
            if flow.classtimetable_set.all():
                for time_table in flow.classtimetable_set.all():

                    teacher_class_time_table = teacher.classtimetable_set.filter(hours_id=time_table.hours_id,
                                                                                 week_id=time_table.week_id).first()
                    if teacher_class_time_table:


                        if teacher_class_time_table.flow_id == None:
                            teacher_data['extra_info'] = {'status': False,
                                                          'reason': f"Bu vaqtda '{teacher.user.name} {teacher.user.surname}' o'quvchisining '{teacher_class_time_table.room.name}' xonasida  '{teacher_class_time_table.group.class_number.number}-{teacher_class_time_table.group.color.name}' sinifiga darsi bor"
                                                          }
                        else:
                            teacher_data['extra_info'] = {'status': False,
                                                          'reason': f"Bu vaqtda '{teacher.user.name} {teacher.user.surname}' o'quvchisining  '{teacher_class_time_table.room.name}' xonasida  '{teacher_class_time_table.flow.name}' patokida darsi bor"}
                    else:
                        teacher_data['extra_info'] = {'status': True,
                                                      'reason': ''}
            else:
                teacher_data['extra_info'] = {'status': True,
                                              'reason': ''}
            teachers_list.append(teacher_data)
        return Response({'teachers_list': teachers_list})
