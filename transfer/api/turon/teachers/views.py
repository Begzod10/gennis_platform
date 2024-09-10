from transfer.api.turon.teachers.flask_data_base import get_teachers, get_teachers_salary_type
import time
from .serializers import TeacherSerializerTransfer, TeacherSalaryTypeSerializerTransfer


def teachers_turon(self):

    list = get_teachers_salary_type()
    for info in list:
        serializer = TeacherSalaryTypeSerializerTransfer(data=info)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))


    list = get_teachers()
    for info in list:
        serializer = TeacherSerializerTransfer(data=info)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))

    return True
