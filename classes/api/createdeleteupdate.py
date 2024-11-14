import json
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from classes.models import ClassNumber, ClassCoin, CoinInfo, StudentCoin, ClassNumberSubjects
from classes.serializers import (ClassNumberSerializers,
                                 ClassCoinSerializers,
                                 StudentCoinSerializers, CoinInfoSerializers, ClassNumberSubjectsSerializers)
from permissions.response import CustomResponseMixin


class ClassNumberCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ClassNumberSubjects.objects.all()
    serializer_class = ClassNumberSubjectsSerializers


class CoinInfoCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = CoinInfo.objects.all()
    serializer_class = CoinInfoSerializers


class CoinInfoUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = CoinInfo.objects.all()
    serializer_class = CoinInfoSerializers


class CoinInfoDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = CoinInfo.objects.all()
    serializer_class = CoinInfoSerializers


class StudentCoinCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = StudentCoin.objects.all()
    serializer_class = StudentCoinSerializers


class StudentCoinUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = StudentCoin.objects.all()
    serializer_class = StudentCoinSerializers


class StudentCoinDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = StudentCoin.objects.all()
    serializer_class = StudentCoinSerializers


class ClassCoinCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ClassCoin.objects.all()
    serializer_class = ClassCoinSerializers


class ClassCoinUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ClassCoin.objects.all()
    serializer_class = ClassCoinSerializers


class ClassCoinDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ClassCoin.objects.all()
    serializer_class = ClassCoinSerializers


class ClassNumberCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ClassNumber.objects.all()
    serializer_class = ClassNumberSerializers


class ClassNumberUpdateStatusView(CustomResponseMixin, generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ClassNumber.objects.all()
    serializer_class = ClassNumberSerializers

    def update(self, request, *args, **kwargs):
        from rest_framework.response import Response
        from ..serializers import ClassNumberListSerializers
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        class_types_data = validated_data.get('class_types', None)
        print(class_types_data)
        # subjects_data = validated_data.get('subjects', None)
        instance = serializer.update(instance, validated_data)

        if class_types_data is not None:
            instance.class_types = class_types_data
        # elif class_types_data is None and subjects_data is None:
        #     instance.class_types = None

        # if subjects_data is not None:
        #     instance.subjects.set(subjects_data)
        instance.save()
        instance.refresh_from_db()
        data = ClassNumberListSerializers(instance).data

        return Response(data)


class ClassNumberUpdateView(generics.UpdateAPIView):
    def update(self, request, *args, **kwargs):
        data = json.loads(request.body)
        subjects = data.get('subjects')
        class_number = ClassNumber.objects.get(pk=kwargs.get('pk'))
        class_number.price = data.get('price')
        class_number.save()
        for subject in subjects:
            subject_added = ClassNumberSubjects.objects.filter(subject_id=subject['value'],
                                                               class_number_id=kwargs.get('pk')).first()
            if subject_added:
                subject_added.hours = subject['hours']
                subject_added.save()
            else:
                ClassNumberSubjects.objects.create(subject_id=subject['value'], class_number_id=kwargs.get('pk'),
                                                   hours=subject['hours'])

        subjects_query = ClassNumberSubjects.objects.filter(class_number_id=class_number.id).all()
        info = {
            'id': class_number.id,
            'price': class_number.price,
            'number': class_number.number,
            'subjects': [{'id': subject_qr.subject.id, 'name': subject_qr.subject.name, 'hours': subject_qr.hours} for
                         subject_qr in subjects_query]
        }

        return Response(info)


class ClassNumberSubjectList(APIView):
    def get(self, request):
        id = self.request.query_params.get('id')
        class_subjects = ClassNumberSubjects.objects.filter(class_number_id=id).all()
        if class_subjects:
            return Response({
                'hours': [{'id': subject.subject_id, 'name': subject.subject.name, 'hours': subject.hours} for subject
                          in
                          class_subjects]
            })
        return Response({
            'hours': []
        })


class ClassNumberDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = ClassNumber.objects.all()
    serializer_class = ClassNumberSerializers


class ClassNumberStatusView(APIView):
    def post(self, request):
        data = json.loads(request.body)
        class_type_id = data.get('class_type_id')
        class_number_id = data.get('class_number_id')
        class_number = ClassNumber.objects.get(pk=class_number_id)
        status = data.get('status')
        if status == True:
            class_number.class_types_id = class_type_id
        else:
            class_number.class_types_id = None
        class_number.save()
        return Response({
            'id': class_number.id
        })
