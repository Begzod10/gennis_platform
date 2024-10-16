from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from students.models import Student, DeletedStudent, DeletedNewStudent
from tasks.models import Task, StudentCallInfo, TaskStatistics, TaskStudent, TaskDailyStatistics
from tasks.serializers import TaskGetSerializer, StudentCallInfoGetSerializers
from user.functions.functions import check_auth


class TaskListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all()
    serializer_class = TaskGetSerializer

    def get(self, request, *args, **kwargs):
        queryset = Task.objects.all()

        serializer = TaskGetSerializer(queryset, many=True)
        return Response(serializer.data)


class TaskRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all()
    serializer_class = TaskGetSerializer

    def retrieve(self, request, *args, **kwargs):
        task = self.get_object()
        task_data = self.get_serializer(task).data
        return Response(task_data)


class CallListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = StudentCallInfo.objects.all()
    serializer_class = StudentCallInfoGetSerializers

    def get(self, request, *args, **kwargs):
        queryset = Task.objects.all()

        serializer = TaskGetSerializer(queryset, many=True)
        return Response(serializer.data)


class CallRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = StudentCallInfo.objects.all()
    serializer_class = StudentCallInfoGetSerializers

    def retrieve(self, request, *args, **kwargs):
        task = self.get_object()
        task_data = self.get_serializer(task).data
        return Response(task_data)


class CreateTask(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error, status=403)

        qarzdor_data_list = []
        yangi_uquvchilar_data_list = []

        tasks = Task.objects.all()
        today = timezone.now()

        for task in tasks:
            if task.name == 'Qarzdor uquvchilar':
                static, _ = TaskStatistics.objects.get_or_create(
                    task=task,
                    day=today,
                    defaults={'progress_num': 100, 'percentage': 0, 'completed_num': 0, 'user': user}
                )

                students = Student.objects.filter(debt_status=2)[:100]
                for student in students:
                    TaskStudent.objects.get_or_create(
                        task=task,
                        task_static=static,
                        status=False,
                        students=student
                    )

                    qarzdor_data_list.append({
                        'student_id': student.id,
                        'task_id': task.id,
                        'task_name': task.name,
                        'task_static_id': static.id,
                        'task_static_progress_num': static.progress_num,
                        'task_static_percentage': static.percentage,
                        'task_static_completed_num': static.completed_num,
                        'task_static_day': static.day,
                    })

            elif task.name == 'Yangi uquvchilar':
                deleted_student_ids = DeletedStudent.objects.filter(deleted=True).values_list('student_id', flat=True)
                deleted_new_student_ids = DeletedNewStudent.objects.values_list('student_id', flat=True)
                active_students = Student.objects.exclude(id__in=deleted_student_ids).exclude(
                    id__in=deleted_new_student_ids)

                static, _ = TaskStatistics.objects.get_or_create(
                    task=task,
                    day=today,
                    defaults={'progress_num': active_students.count(), 'percentage': 0, 'completed_num': 0,
                              'user': user}
                )

                for student in active_students:
                    TaskStudent.objects.get_or_create(
                        task=task,
                        task_static=static,
                        status=False,
                        students=student
                    )

                    yangi_uquvchilar_data_list.append({
                        'student_id': student.id,
                        'task_id': task.id,
                        'task_name': task.name,
                        'task_static_id': static.id,
                        'task_static_progress_num': static.progress_num,
                        'task_static_percentage': static.percentage,
                        'task_static_completed_num': static.completed_num,
                        'task_static_day': static.day,
                    })

            TaskDailyStatistics.objects.get_or_create(
                day=today,
                defaults={'completed_num': 0, 'progress_num': len(qarzdor_data_list) + len(yangi_uquvchilar_data_list),
                          'percentage': 0, 'user': user}
            )

        response_data = {
            'qarzdor_uquvchilar': qarzdor_data_list,
            'yangi_uquvchilar': yangi_uquvchilar_data_list
        }

        return Response(response_data, status=200)
