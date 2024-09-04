from students.models import DeletedNewStudent
from teachers.models import Teacher, TeacherSalaryType
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


class TeacherSalaryTypeSerializerTransfer(serializers.ModelSerializer):
    class Meta:
        model = TeacherSalaryType
        fields = '__all__'


class   TeacherSerializerTransfer(serializers.ModelSerializer):
    user = OldIdRelatedField(queryset=CustomUser.objects.all(), many=False)
    teacher_salary_type = OldIdRelatedField(queryset=TeacherSalaryType.objects.all(), many=False)

    class Meta:
        model = Teacher
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = CustomUser.objects.get(turon_old_id=user_data['turon_old_id']) if isinstance(user_data,
                                                                                            dict) else user_data
        teacher = Teacher.objects.create(user=user, **validated_data)
        return teacher
