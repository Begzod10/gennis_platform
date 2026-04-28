from transfer.api.turon.students.flask_data_base import get_students
import time
from .serializers import StudentSerializerTransfer


def students_turon(self):
    list = get_students()
    for info in list:
        serializer = StudentSerializerTransfer(data=info)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))
    return True
