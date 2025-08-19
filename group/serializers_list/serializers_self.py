from rest_framework import serializers

from group.models import Group
from teachers.models import Teacher


class AddClassesSerializers(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Group
        fields = ['id', 'name', 'branch']

    def get_name(self, obj):
        return f"{obj.class_number.number}-{obj.color.name}"


class TeacherCreateGroupSerializerRead(serializers.ModelSerializer):
    # user = UserSerializer(read_only=True)
    name = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Teacher
        fields = ["id", "name", ]

    def get_name(self, obj):
        return f"{obj.user.name} {obj.user.surname}"


class GroupListSerializer(serializers.ModelSerializer):
    teacher = serializers.SerializerMethodField(required=False)
    count = serializers.SerializerMethodField(required=False)
    name = serializers.SerializerMethodField(required=False)
    class_number = serializers.CharField(required=False, source='class_number.number')
    color = serializers.CharField(required=False, source='color.name')

    class Meta:
        model = Group
        fields = ['id', 'teacher', "status", "name", "count", "class_number", "color", 'price']

    def get_teacher(self, obj):
        name = ""
        for i in obj.teacher.all():
            name = f"{i.user.name} {i.user.surname}"

        return name

    def get_count(self, obj):
        return obj.students.count()

    def get_name(self, obj):
        if obj.name:
            return obj.name
        else:
            return f"{obj.class_number.number}-{obj.color.name}"

    # def get_students(self, obj):
    #     students = obj.students.all()
    #     list_id = []
    #     for i in students:
    #         list_id.append(i.user)
    #     return UserSerializer(list_id, many=True).data


class GroupListSerialize2r(serializers.ModelSerializer):
    teacher = serializers.SerializerMethodField(required=False)
    count = serializers.SerializerMethodField(required=False)
    name = serializers.SerializerMethodField(required=False)
    class_number = serializers.CharField(required=False, source='class_number.number')
    color = serializers.CharField(required=False, source='color.name')
    students = serializers.SerializerMethodField(required=False)
    language = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Group
        fields = ['id', 'teacher', "status", "name", "count", "class_number", "color", 'price', "students", "language"]

    def get_teacher(self, obj):
        name = ""
        for i in obj.teacher.all():
            name = f"{i.user.name} {i.user.surname}"

        return name

    def get_count(self, obj):
        return obj.students.count()

    def get_name(self, obj):
        if obj.name:
            return obj.name
        else:
            return f"{obj.class_number.number}-{obj.color.name}"

    def get_language(self, obj):
        return {"id": obj.language.id, "name": obj.language.name}

    def get_students(self, obj):
        students = obj.students.all()
        from students.serializer.lists import ActiveListSerializer

        return ActiveListSerializer(students, many=True).data
