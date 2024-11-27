from rest_framework import serializers
from .models import FrontedPageType, FrontedPage, FrontedPageImage


class FrontedPageTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrontedPageType
        fields = '__all__'


class FrontedPageSerializer(serializers.ModelSerializer):
    type = serializers.PrimaryKeyRelatedField(queryset=FrontedPageType.objects.all())

    class Meta:
        model = FrontedPage
        fields = '__all__'


class FrontedPageImageSerializer(serializers.ModelSerializer):
    page = serializers.PrimaryKeyRelatedField(queryset=FrontedPage.objects.all())

    class Meta:
        model = FrontedPageImage
        fields = '__all__'
