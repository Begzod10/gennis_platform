from rest_framework import generics
from rest_framework.response import Response
from ...models import ClassTimeTable

from ...serializers import ClassTimeTableCreateUpdateSerializers
from teachers.functions.school.CalculateTeacherSalary import teacher_salary_school


class DeleteItemClassTimeTable(generics.RetrieveDestroyAPIView):
    queryset = ClassTimeTable.objects.all()
    serializer_class = ClassTimeTableCreateUpdateSerializers

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        print(instance.id)
        teacher_salary_school(request=None, update=True, salary_id=instance.id, worked_hours=0, deleted=True)
        self.perform_destroy(instance)
        print(instance)

        return Response({"msg": "Dars muvvaffaqqiyatli o'chirildi"})
