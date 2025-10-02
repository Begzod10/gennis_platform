from rest_framework import viewsets, permissions
from rest_framework.response import Response
from teachers.models import TeacherRequest, Teacher
from teachers.serializer.lists import TeacherRequestSerializer


class TeacherRequestViewSet(viewsets.ModelViewSet):
    queryset = TeacherRequest.objects.all().order_by('-created_at')
    serializer_class = TeacherRequestSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        branch_id = self.request.query_params.get('branch')
        teacher_id = self.request.query_params.get('turon_id')
        # turon_old_id = self.request.query_params.get('turon_old_id')
        status = self.request.query_params.get('status')
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)

        if teacher_id:
            queryset = queryset.filter(teacher_id=teacher_id)

        # if turon_old_id:
        #     try:
        #         teacher = Teacher.objects.get(user__id=turon_old_id)
        #         queryset = queryset.filter(teacher=teacher)
        #     except Teacher.DoesNotExist:
        #         return TeacherRequest.objects.none()
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def perform_create(self, serializer):
        turon_id = self.request.query_params.get('turon_id')
        if not turon_id:
            raise ValueError("turon_old_id kerak")

        try:
            teacher = Teacher.objects.get(id=turon_id)
        except Teacher.DoesNotExist:
            raise ValueError("Teacher topilmadi")

        serializer.save(teacher=teacher)
