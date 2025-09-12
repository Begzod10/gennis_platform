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
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.date = validated_data.get('date', instance.date)
        instance.weight = validated_data.get('weight', instance.weight)
        instance.subject = validated_data.get('subject', instance.subject)
        instance.term = validated_data.get('term', instance.term)
        instance.deleted = validated_data.get('deleted', instance.deleted)
        instance.group = validated_data.get('group', instance.group)
        instance.save()
        instance.class_number = instance.group.class_number
        instance.save()

        return instance


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = '__all__'
