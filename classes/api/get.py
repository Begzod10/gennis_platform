from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from classes.models import ClassNumber, ClassCoin, CoinInfo, StudentCoin, ClassColors
from classes.serializers import (ClassCoinListSerializers, CoinInfoListSerializers, StudentCoinListSerializers,
                                 ClassNumberListSerializers, ClassColorsSerializers)
from group.models import Group
from subjects.serializers import SubjectSerializer
from permissions.response import QueryParamFilterMixin


class ClassNumberRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ClassNumber.objects.all()
    serializer_class = ClassNumberListSerializers

    def retrieve(self, request, *args, **kwargs):

        pk = int(self.kwargs.get('pk'))
        class_number = ClassNumber.objects.all()
        datas = []

        for class_num in class_number:
            if class_num.class_types is not None:
                class_type_id = class_num.class_types.id
                status = class_num.class_types.id == pk

            else:
                status = False
                class_type_id = None
            if pk == class_type_id or class_type_id is None:
                data = {
                    'id': class_num.id,
                    'number': class_num.number,
                    'price': class_num.price,
                    'curriculum_hours': class_num.curriculum_hours,
                    'class_types': class_type_id,
                    'status': status,
                    'subjects': [
                        {
                            'id': i.id,
                            'name': i.name
                        }
                        for i in class_num.subjects.all()
                    ]
                }
                datas.append(data)

        datas.sort(key=lambda x: not x['status'])

        return Response(datas)


class StudentCoinRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = StudentCoin.objects.all()
    serializer_class = StudentCoinListSerializers

    def retrieve(self, request, *args, **kwargs):
        student_coin = self.get_object()
        student_coin_data = self.get_serializer(student_coin).data
        return Response(student_coin_data)


class CoinInfoRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = CoinInfo.objects.all()
    serializer_class = CoinInfoListSerializers

    def retrieve(self, request, *args, **kwargs):
        coininfo = self.get_object()
        coininfo_data = self.get_serializer(coininfo).data
        return Response(coininfo_data)


class ClassCoinRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ClassCoin.objects.all()
    serializer_class = ClassCoinListSerializers

    def retrieve(self, request, *args, **kwargs):
        class_coin = self.get_object()
        class_coin_data = self.get_serializer(class_coin).data
        return Response(class_coin_data)


class ClassCoinListView(generics.ListAPIView):
    queryset = ClassCoin.objects.all()
    serializer_class = ClassCoinListSerializers

    def get(self, request, *args, **kwargs):

        queryset = ClassCoin.objects.all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        serializer = ClassCoinListSerializers(queryset, many=True)
        return Response(serializer.data)


class CoinInfoListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = CoinInfo.objects.all()
    serializer_class = CoinInfoListSerializers

    def get(self, request, *args, **kwargs):

        queryset = CoinInfo.objects.all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        serializer = CoinInfoListSerializers(queryset, many=True)
        return Response(serializer.data)


class StudentCoinListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = StudentCoin.objects.all()
    serializer_class = StudentCoinListSerializers

    def get(self, request, *args, **kwargs):

        queryset = StudentCoin.objects.all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)

        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        serializer = StudentCoinListSerializers(queryset, many=True)
        return Response(serializer.data)




class ClassNumberListView( QueryParamFilterMixin,generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    filter_mappings = {
        'branch': 'branch_id',
    }

    queryset = ClassNumber.objects.all()
    serializer_class = ClassNumberListSerializers

    def get(self, request, *args, **kwargs):
        queryset = ClassNumber.objects.all()
        queryset_branch = self.filter_queryset(queryset)
        serializer = ClassNumberListSerializers(queryset_branch, many=True)
        return Response(serializer.data)


class ClassColorsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ClassColors.objects.all()
    serializer_class = ClassColorsSerializers

    def get_queryset(self):
        queryset = ClassColors.objects.all()
        location_id = self.request.query_params.get('location_id', None)
        branch_id = self.request.query_params.get('branch_id', None)
        if branch_id is not None:
            queryset = queryset.filter(branch_id=branch_id)
        if location_id is not None:
            queryset = queryset.filter(location_id=location_id)
        return queryset


class ClassColorsDeleteView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = ClassColors.objects.all()
    serializer_class = ClassColorsSerializers

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"msg": "Rang o'chirildi"}, status=status.HTTP_200_OK)


class ClassSubjects(APIView):
    def get(self, request):
        group = Group.objects.filter(pk=request.query_params.get('group')).first()

        subjects = group.class_number.subjects.all()
        print(subjects)
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)
