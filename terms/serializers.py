from rest_framework import serializers

from .models import Test, Term


class TestCreateUpdateSerializer(serializers.ModelSerializer):
    class_number = serializers.CharField(required=False)
    class Meta:
        model = Test
        fields = '__all__'

    def create(self, validated_data):
        group = validated_data.get('group')

        if group and hasattr(group, 'class_number'):
            validated_data['class_number'] = group.class_number

        test = Test.objects.create(**validated_data)

        return test


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = '__all__'
