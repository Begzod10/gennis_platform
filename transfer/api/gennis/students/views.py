from transfer.api.gennis.students.flask_data_base import get_students, get_deleted_students, get_studenthistorygroups, \
    get_studentcharity, get_studentpayments
import time
from transfer.api.gennis.students.serializers import StudentSerializerTransfer, TransferDeletedNewStudentSerializer, \
    StudentHistoryGroupCreateSerializerTransfer, StudentCharitySerializerTransfer
from transfer.api.gennis.students.payments.serializers import StudentPaymentSerializerTransfer


def students(self):
    start = time.time()
    # list = get_students()
    # for info in list:
    #     serializer = StudentSerializerTransfer(data=info)
    #     if serializer.is_valid():
    #         serializer.save()
    #     else:
    #         self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))
    # list = get_deleted_students()
    # for info in list:
    #     serializer = TransferDeletedNewStudentSerializer(data=info)
    #     if serializer.is_valid():
    #         serializer.save()
    #     else:
    #         self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))
    # list = get_studenthistorygroups()
    # for info in list:
    #     serializer = StudentHistoryGroupCreateSerializerTransfer(data=info)
    #     if serializer.is_valid():
    #         serializer.save()
    #     else:
    #         self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))
    # list = get_studentcharity()
    # for info in list:
    #     serializer = StudentCharitySerializerTransfer(data=info)
    #     if serializer.is_valid():
    #         serializer.save()
    #     else:
    #         self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))
    # list = get_studentpayments()
    # for info in list:
    #     serializer = StudentPaymentSerializerTransfer(data=info)
    #     if serializer.is_valid():
    #         serializer.save()
    #     else:
    #         self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))
    # end = time.time()
    # print(f"Run time students: {(end - start) * 10 ** 3:.03f}ms")
    return True
