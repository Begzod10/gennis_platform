from rest_framework import serializers

from .models import FrontedPageType, FrontedPage, FrontedPageImage


class FrontedPageTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrontedPageType
        fields = '__all__'


class FrontedPageImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrontedPageImage
        fields = ['id', 'image']


class FrontedPageSerializer(serializers.ModelSerializer):
    type = serializers.PrimaryKeyRelatedField(queryset=FrontedPageType.objects.all())
    image = serializers.ImageField(write_only=True, required=False)
    images = FrontedPageImageSerializer(many=True, read_only=True,
                                        source='frontedpageimage_set')

    class Meta:
        model = FrontedPage
        fields = ['id', 'name', 'type', 'description', 'date', 'image', 'images']

    def create(self, validated_data):
        image_data = validated_data.pop('image', None)
        fronted_page = FrontedPage.objects.create(**validated_data)
        print(image_data)
        if image_data:
            FrontedPageImage.objects.create(page=fronted_page, image=image_data)
            print(True)

        return fronted_page

    def update(self, instance, validated_data):
        image_data = validated_data.pop('image', None)
        instance = super().update(instance, validated_data)

        if image_data:
            image_instance, created = FrontedPageImage.objects.get_or_create(page=instance)
            image_instance.image = image_data
            image_instance.save()

        return instance
