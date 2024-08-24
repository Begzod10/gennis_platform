from students.models import DeletedNewStudent
from students.models import Student, StudentHistoryGroups, StudentCharity
from subjects.serializers import Subject
from teachers.models import Teacher
from user.models import CustomUser
from branch.models import Branch
from group.models import Group
from rest_framework import serializers
from django.db import transaction


class OldIdRelatedField(serializers.RelatedField):
    def to_internal_value(self, data):
        if isinstance(data, dict):
            turon_old_id = data.get('turon_old_id')
            if turon_old_id is None:
                raise serializers.ValidationError("turon_old_id is required.")
            try:
                return self.get_queryset().get(turon_old_id=turon_old_id)
            except self.get_queryset().model.DoesNotExist:
                raise serializers.ValidationError(f"Object with turon_old_id {turon_old_id} does not exist.")
        raise serializers.ValidationError("Expected a dictionary with an 'turon_old_id'.")

    def to_representation(self, value):
        return {
            'turon_old_id': value.turon_old_id,
        }


class StudentSerializerTransfer(serializers.ModelSerializer):
    user = OldIdRelatedField(queryset=CustomUser.objects.all(), many=False)
    language_type = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Student
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        language_type = validated_data.pop('language_type')
        print(language_type)
        user = CustomUser.objects.get(old_id=user_data['turon_old_id']) if isinstance(user_data, dict) else user_data
        student = Student.objects.create(user=user, **validated_data)
        return student
