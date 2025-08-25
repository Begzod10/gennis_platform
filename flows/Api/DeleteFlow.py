from rest_framework.response import Response
from rest_framework.views import APIView

from flows.models import Flow


class DeleteFlow(APIView):
    def delete(self, request, pk):
        try:
            flow = Flow.objects.get(pk=pk)
        except Flow.DoesNotExist:
            return Response({'error': 'Flow not found'}, status=404)

        # copy related objects to avoid issues while deleting in loop
        students = list(flow.students.all())
        class_time_tables = list(flow.classtimetable_set.all())

        for student in students:
            for class_time_table in class_time_tables:
                if class_time_table in student.class_time_table.all():
                    student.class_time_table.remove(class_time_table)

                if flow.teacher and class_time_table in flow.teacher.classtimetable_set.all():
                    flow.teacher.classtimetable_set.remove(class_time_table)

                class_time_table.delete()

            flow.students.remove(student)

        name = flow.name
        flow.delete()

        return Response({'msg': f'{name} patoki ochirildi'}, status=200)
