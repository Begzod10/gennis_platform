from rest_framework import serializers

from group.models import Group, GroupReason
from students.models import Student, DeletedStudent
from students.serializers import get_remaining_debt_for_student
from user.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField(required=False)
    language = serializers.SerializerMethodField(required=False)
    id = serializers.SerializerMethodField(required=False)

    class Meta:
        model = CustomUser
        fields = ('id', 'name', 'surname', 'phone', 'age', 'registered_date', 'language')

    def get_age(self, obj):
        return obj.calculate_age()

    def get_language(self, obj):
        # select_related('user__language') tufayli endi extra query yo'q
        if obj.language:
            return obj.language.name
        return None

    def get_id(self, obj):
        students = obj.student_user.all()
        if students:
            return students[0].id
        return "No student ID"


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('name')


class ActiveListSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    group = serializers.SerializerMethodField(required=False)
    color = serializers.SerializerMethodField(required=False)
    debt = serializers.SerializerMethodField(required=False)
    class_number = serializers.CharField(required=False, source='class_number.number')
    comment = serializers.CharField(required=False, source="user.comment")

    class Meta:
        model = Student
        fields = ('id', 'user', "group", "color", "debt", 'class_number', 'comment')

    def get_color(self, obj):
        if obj.debt_status == 1:
            return '#FACC15'
        elif obj.debt_status == 2:
            return '#FF3130'
        elif obj.debt_status == 0:
            return '#24FF00'
        return ''

    def get_debt(self, obj):
        # debt = get_remaining_debt_for_student(obj.id)
        return 0

    def get_group(self, obj):
        # prefetch_related ishlagani uchun endi extra query yo'q
        groups = obj.groups_student.first()
        if groups:
            return {
                "id": groups.id,
                "name": groups.name,
                "class_number": groups.class_number.number,
                "color": groups.color.name
            }
        return {
            "id": None,
            "name": None,
            "class_number": None,
            "color": None
        }
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
