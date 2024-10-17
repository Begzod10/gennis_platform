from rest_framework import serializers
from students.models import Student, DeletedStudent
from group.models import Group, GroupReason
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
        fields = ('name')


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


class ActiveListDeletedSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(required=False)
    surname = serializers.SerializerMethodField(required=False)
    age = serializers.SerializerMethodField(required=False)
    phone = serializers.SerializerMethodField(required=False)
    registered_date = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Student
        fields = ('id', 'name', 'surname', 'age', 'phone', 'registered_date')

    def get_name(self, obj):
        return obj.user.name

    def get_phone(self, obj):
        return obj.user.phone

    def get_age(self, obj):
        return obj.user.calculate_age()

    def get_surname(self, obj):
        return obj.user.surname

    def get_registered_date(self, obj):
        return f'{obj.user.registered_date}'


class ActiveGroupSerializerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')


class ActiveGroupReasonSerializerSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupReason
        fields = ('id', 'name')


class ActiveListDeletedStudentSerializer(serializers.ModelSerializer):
    student = ActiveListDeletedSerializer(required=True)
    group = ActiveGroupSerializerSerializer(required=True)
    group_reason = ActiveGroupReasonSerializerSerializer(required=True)

    class Meta:
        model = DeletedStudent
        fields = ['id', 'student', 'group', 'group_reason', 'deleted_date', 'comment']

