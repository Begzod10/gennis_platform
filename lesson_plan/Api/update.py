from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from lesson_plan.models import LessonPlan, LessonPlanStudents
from lesson_plan.serializers import LessonPlanSerializer


class ChangeLessonPlanView(generics.UpdateAPIView):
    queryset = LessonPlan.objects.all()
    serializer_class = LessonPlanSerializer
    # permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        plan_id = kwargs.get('pk')
        lesson_plan = self.get_object()

        data = request.data
        lesson_plan.objective = data.get('objective')
        lesson_plan.main_lesson = data.get('main_lesson')
        lesson_plan.homework = data.get('homework')
        lesson_plan.assessment = data.get('assessment')
        lesson_plan.activities = data.get('activities')
        lesson_plan.resources = data.get('resources')
        lesson_plan.save()

        students = data.get('students', [])
        for student in students:
            info = {
                "comment": student.get('comment'),
                "student_id": student['student']['id'],
                "lesson_plan_id": plan_id
            }
            lesson_plan_student, created = LessonPlanStudents.objects.get_or_create(
                lesson_plan_id=plan_id,
                student_id=student['student']['id'],
                defaults=info
            )
            if not created:
                lesson_plan_student.comment = student.get('comment')
                lesson_plan_student.save()

        return Response({
            "success": True,
            "msg": "Lesson plan updated",
            "lesson_plan": LessonPlanSerializer(lesson_plan).data
        })
