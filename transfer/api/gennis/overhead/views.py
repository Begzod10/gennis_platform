from .serializers import TransferOverheadSerializerCreate
from transfer.api.gennis.overhead.flask_data_base import get_overheads
import time


def overhead(self):
    # start = time.time()
    # list = get_overheads()
    # for info in list:
    #     serializer = TransferOverheadSerializerCreate(data=info)
    #     if serializer.is_valid():
    #         serializer.save()
    #     else:
    #         self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))
    # end = time.time()
    # print(f"Run time attendance: {(end - start) * 10 ** 3:.03f}ms")
    return True
