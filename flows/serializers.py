from rest_framework import serializers

from teachers.models import Teacher
from .models import Flow
from subjects.models import Subject, SubjectLevel
from students.models import Student
from branch.models import Branch

from subjects.serializers import SubjectSerializer, SubjectLevelSerializer
from teachers.serializers import TeacherSerializer
from students.serializers import StudentSerializer
from branch.serializers import BranchSerializer

from .functions.flowClasses import flow_classes


class FlowCreateUpdateSerializer(serializers.ModelSerializer):
    update_type = serializers.CharField(default=None, allow_blank=True)
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    students = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), many=True)
    level = serializers.PrimaryKeyRelatedField(queryset=SubjectLevel.objects.all(), allow_null=True, required=False)
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())

    class Meta:
        model = Flow
        fields = ['id', 'name', 'level', 'activity', 'subject', 'teacher', 'students', 'update_type', 'branch',
                  'classes']

    def create(self, validated_data):
        students = validated_data.pop('students')
        flow = Flow.objects.create(**validated_data)
        flow.students.set(students)
        flow.save()
        flow_classes(flow)
        return flow

    def update(self, instance, validated_data):
        update_type = validated_data.get('update_type', None)
        instance.name = validated_data.get('name', instance.name)
        instance.level = validated_data.get('level', instance.level) if validated_data.get('level') else None
        instance.activity = validated_data.get('activity', instance.activity)
        instance.subject = validated_data.get('subject', instance.subject)
        instance.teacher = validated_data.get('teacher', instance.teacher)

        if update_type:
            print(instance.classtimetable_set.all())
            if update_type == 'add_students':
                students = validated_data.get('students')
                for student in students:
                    instance.students.add(student)
                    student.class_time_table.set(instance.classtimetable_set.all())


            elif update_type == 'remove_students':
                students = validated_data.get('students')
                for student in students:
                    instance.students.remove(student)
                    for time_table in instance.classtimetable_set.all():
                        student.class_time_table.remove(time_table)
        instance.save()
        flow_classes(instance)
        return instance


class FlowsSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    teacher = TeacherSerializer(read_only=True)
    students = StudentSerializer(read_only=True, many=True)
    level = SubjectLevelSerializer(read_only=True)
    branch = BranchSerializer(read_only=True)
    type = serializers.CharField(default='flow', read_only=True)

    class Meta:
        model = Flow
        fields = ['id', 'name', 'level', 'activity', 'subject', 'teacher', 'students', 'branch', 'type', 'classes']
