from rest_framework import serializers

from parents.models import Parent
from students.models import Student
from user.models import CustomUser


class ParentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'name', 'surname', 'father_name',
            'birth_date', 'phone', 'address', 'branch'
        ]


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ["id", "user", "shift", "class_number"]


class ParentSerializer(serializers.ModelSerializer):
    user = ParentUserSerializer()
    children = StudentSerializer(many=True)

    class Meta:
        model = Parent
        fields = ["id", "user", "children"]
