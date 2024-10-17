from rest_framework import serializers
from students.models import Student
from group.models import Group
from user.models import CustomUser
from students.serializers import get_remaining_debt_for_student


class UserSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField(required=False)

    class Meta:
        model = CustomUser
        fields = ('name', 'surname', 'phone', 'age')

    def get_age(self, obj):
        return obj.calculate_age()


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('name',)


class ActiveListSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    group = serializers.SerializerMethodField(required=False)
    color = serializers.SerializerMethodField(required=False)
    debt = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Student
        fields = ('id', 'user', "group", "color", "debt")

    def get_color(self, obj):
        color = ''
        if obj.debt_status == 1:
            color = '#FACC15'
        elif obj.debt_status == 2:
            color = '#FF3130'
        elif obj.debt_status == 0:
            color = '24FF00'
        return color

    def get_debt(self, obj):
        debt = 0
        if obj.user.branch.location.system.name == 'school':
            debt = get_remaining_debt_for_student(obj.id)
        else:
            groups = obj.groups_student.all()
            for group in groups:
                for i in group.teacher.all():
                    for salary in i.teacher_black_salary.filter(student_id=obj.id).all():
                        debt += salary.black_salary if salary.black_salary else 0

        return debt

    def get_group(self, obj):
        groups = obj.groups_student.first()
        group = {
            "id": groups.id if groups else None,
            "name": groups.name if groups else None
        }
        return group
