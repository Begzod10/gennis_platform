from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from permissions.response import CustomResponseMixin
from .models import ClassTypes, ClassColors, ClassNumber
from .serializers import (ClassTypesSerializers, ClassColorsSerializers)


class CreateClassColorsList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ClassColors.objects.all()
    serializer_class = ClassColorsSerializers

    def get(self, request, *args, **kwargs):
        from group.models import Group
        queryset = ClassColors.objects.all()
        datas = []
        for data in queryset:
            info = ClassColorsSerializers(data).data
            info['status'] = False if Group.objects.filter(color_id=data.id).exists() else True
            datas.append(info)

        return Response(datas)


class ClassColorsRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ClassColors.objects.all()
    serializer_class = ClassColorsSerializers

    def retrieve(self, request, *args, **kwargs):
        class_colors = self.get_object()
        class_colors_data = self.get_serializer(class_colors).data
        return Response(class_colors_data)


from permissions.response import QueryParamFilterMixin


class CreateClassTypesList(QueryParamFilterMixin, generics.ListCreateAPIView):
    filter_mappings = {
        'branch': 'branch_id',
    }
    queryset = ClassTypes.objects.all()
    serializer_class = ClassTypesSerializers

    def get(self, request, *args, **kwargs):
        queryset = ClassTypes.objects.all()
        serializer = ClassTypesSerializers(queryset, many=True)
        datas = []

        class_numbers = ClassNumber.objects.all()
        class_numbers = self.filter_queryset(class_numbers)

        for data in serializer.data:
            class_type_id = data.get('id')
            assigned_class_numbers = class_numbers.filter(class_types_id=class_type_id)

            class_number_list = []
            for class_number in assigned_class_numbers:
                class_number_list.append({
                    'id': class_number.id,
                    'status': True,
                    'number': class_number.number
                })

            datas.append({
                'id': data['id'],
                'name': data['name'],
                'class_numbers': class_number_list
            })

        return Response(datas)


class ClassTypesRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView, CustomResponseMixin):
    permission_classes = [IsAuthenticated]

    queryset = ClassTypes.objects.all()
    serializer_class = ClassTypesSerializers

    def retrieve(self, request, *args, **kwargs):
        class_types = self.get_object()
        class_types_data = self.get_serializer(class_types).data
        return Response(class_types_data)

    def destroy(self, request, *args, **kwargs):
        super().destroy(self, request, *args, **kwargs)
        return Response({'msg': "Maʼlumotlar muvaffaqiyatli o'chirildi."}, status=status.HTTP_200_OK)
