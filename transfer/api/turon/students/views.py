from transfer.api.turon.students.flask_data_base import get_students
import time
from .serializers import StudentSerializerTransfer


def students_turon(self):
    start = time.time()
    list = get_students()
    for info in list:
        serializer = StudentSerializerTransfer(data=info)
        if serializer.is_valid():
            # serializer.save()
            print(True)
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))
    end = time.time()
    print(f"Run time students: {(end - start) * 10 ** 3:.03f}ms")
    return True
