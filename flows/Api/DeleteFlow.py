from rest_framework.response import Response
from rest_framework.views import APIView

from flows.models import Flow


class DeleteFlow(APIView):
    def delete(self, request, pk):
        try:
            flow = Flow.objects.get(pk=pk)
        except Flow.DoesNotExist:
            return Response({'error': 'Flow not found'}, status=404)

        for class_time_table in flow.classtimetable_set.all():
            # Avval timetable o‘chirilsin
            class_time_table.delete()

        # Keyin studentlarni detach qilamiz
        flow.students.clear()

        # Agar teacher bog‘langan bo‘lsa, timetable aloqalarini olib tashlash
        if flow.teacher:
            flow.teacher.classtimetable_set.clear()

        # Oxirida flow o‘chirilsin
        flow.delete()

        return Response({'msg': f'{flow.name} patoki o‘chirildi'}, status=200)
