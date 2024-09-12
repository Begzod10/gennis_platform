from transfer.api.turon.classes.serializers import (
    TransferClassNumberSerializer, TransferClassColorsSerializer, TransferGroupSerializer, TransferRoomSerializer
)
import time
from transfer.api.turon.classes.flask_data_base import get_class_number, get_class_color, get_class, get_room


def class_turon(self):
    list = get_class_number()
    for info in list:
        serializer = TransferClassNumberSerializer(data=info)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))
    list = get_room()
    for info in list:
        serializer = TransferRoomSerializer(data=info)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))
    list = get_class_color()
    for info in list:
        serializer = TransferClassColorsSerializer(data=info)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))
    list = get_class()
    for info in list:
        serializer = TransferGroupSerializer(data=info)
        if not serializer.is_valid():
            print(serializer)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid data: {serializer.errors}"))
    return True
