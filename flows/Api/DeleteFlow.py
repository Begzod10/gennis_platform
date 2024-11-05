from rest_framework.response import Response
from rest_framework.views import APIView


from flows.models import Flow



class DeleteFlow(APIView):
    def delete(self, request, pk):
        try:
            flow = Flow.objects.get(pk=pk)
        except Flow.DoesNotExist:
            return Response({'error': 'Flow not found'}, status=404)

        students = flow.students.all()
        for student in students:
            if flow.classtimetable_set.all():
                for class_time_table in flow.classtimetable_set.all():
                    student.class_time_table.remove(class_time_table)
                    if flow.teacher is not None:
                        flow.teacher.classtimetable_set.remove(class_time_table)
                    class_time_table.delete()
            flow.students.remove(student)
        flow.delete()

        return Response({'msg': f'{flow.name} patoki ochirildi'}, status=200)
