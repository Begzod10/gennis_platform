from rest_framework import serializers

from parents.models import Parent
from students.models import Student
from user.models import CustomUser


class ParentUserSerializer(serializers.ModelSerializer):
    branch = serializers.CharField(source="branch.name")

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'name', 'surname', 'father_name',
            'birth_date', 'phone', 'branch'
        ]


class StudentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="user.name")
    surname = serializers.CharField(source="user.surname")
    username = serializers.CharField(source="user.username")
    father_name = serializers.CharField(source="user.father_name")
    location = serializers.CharField(source="user.branch.name")
    phone = serializers.CharField(source="user.phone")
    born_date = serializers.CharField(source="user.birth_date")
    age = serializers.CharField(source="user.calculate_age")

    class Meta:
        model = Student
        fields = ["id", "shift", "class_number", 'username', 'name', 'surname', 'father_name',
                  'born_date', 'phone', 'location', 'age']


class StudentSerializerMobile(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    balance = serializers.IntegerField(source="user.balance")

    def get_group(self, obj):
        # Get the first group safely
        first_group = obj.groups_student.first()

        if first_group:
            return {
                "id": first_group.id,
                "name": first_group.name if first_group.name else f"{first_group.class_number.number}-{first_group.color.name}"
            }
        return None

    def get_user(self, obj):
        return {
            "id": obj.user.id,
            "name": obj.user.name,
            "surname": obj.user.surname,
            "shift": obj.shift,
            "class_number": obj.class_number.number
        }

    class Meta:
        model = Student
        fields = ["id", "user", "group", "balance"]


class ParentSerializer(serializers.ModelSerializer):
    user = ParentUserSerializer()
    children = StudentSerializer(many=True)

    class Meta:
        model = Parent
        fields = ["id", "user", "children"]


class ParentSerializerForList(serializers.ModelSerializer):
    name = serializers.CharField(source="user.name")
    surname = serializers.CharField(source="user.surname")
    username = serializers.CharField(source="user.username")
    father_name = serializers.CharField(source="user.father_name")
    location = serializers.CharField(source="user.branch.name")
    phone = serializers.CharField(source="user.phone")
    born_date = serializers.CharField(source="user.birth_date")

    class Meta:
        model = Parent
        fields = ["id", 'username', 'name', 'surname', 'father_name',
                  'born_date', 'phone', 'location']
