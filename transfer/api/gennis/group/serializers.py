from rest_framework import serializers
from branch.models import Branch
from language.models import Language
from students.models import Student
from subjects.models import Subject, SubjectLevel
from teachers.models import Teacher
from group.models import Group, CourseTypes


class OldIdRelatedField(serializers.SlugRelatedField):
    def __init__(self, *args, **kwargs):
        kwargs['slug_field'] = 'old_id'
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        model = self.queryset.model
        if isinstance(data, list):
            try:
                return [model.objects.get(old_id=item) for item in data]
            except model.DoesNotExist:
                raise serializers.ValidationError(f"{model.__name__} with old_id(s) {data} does not exist.")
        else:
            try:
                return model.objects.get(old_id=data)
            except model.DoesNotExist:
                raise serializers.ValidationError(f"{model.__name__} with old_id {data} does not exist.")



class TransferGroupCreateUpdateSerializer(serializers.ModelSerializer):

    students = OldIdRelatedField(queryset=Student.objects.all(), many=True, required=False)
    teacher = OldIdRelatedField(queryset=Teacher.objects.all(), required=False, allow_null=True)
    branch = OldIdRelatedField(queryset=Branch.objects.all(), required=False, allow_null=True)
    language = OldIdRelatedField(queryset=Language.objects.all(), required=False, allow_null=True)
    level = OldIdRelatedField(queryset=SubjectLevel.objects.all(), required=False, allow_null=True)
    subject = OldIdRelatedField(queryset=Subject.objects.all(), required=False, allow_null=True)
    course_types = OldIdRelatedField(queryset=CourseTypes.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'price', 'status', 'created_date', 'teacher_salary', 'attendance_days',
                  'deleted', 'branch', 'language', 'level', 'subject', 'students', 'teacher', 'system', 'class_number',
                  'color', 'course_types', 'class_number', 'old_id']
