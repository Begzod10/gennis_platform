from .serializers import TransferGroupCreateUpdateSerializer
from transfer.api.gennis.group.flask_data_base import get_groups
import time


def groups(self):
    start = time.time()
    list = get_groups()
    for info in list:
        serializer = TransferGroupCreateUpdateSerializer(data=info)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))
    end = time.time()
    print(f"Run time attendance: {(end - start) * 10 ** 3:.03f}ms")
    return True
