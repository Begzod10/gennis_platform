from rest_framework import serializers

from students.serializers import get_remaining_debt_for_student
from .models import Flow


class FlowsSerializerTest(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.name', read_only=True)
    teacher_surname = serializers.CharField(source='teacher.user.surname', read_only=True)
    student_count = serializers.IntegerField(source='students.count', read_only=True)
    level_name = serializers.CharField(source='level.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    type = serializers.CharField(default='flow', read_only=True)

    class Meta:
        model = Flow
        fields = ['id', 'name', 'level_name', 'activity', 'subject_name', 'teacher_name', 'student_count',
                  'branch_name', 'type', 'classes', 'teacher_surname']

    def get_teacher(self, obj):
        return {
            'name': obj.teacher.user.name,
            'surname': obj.teacher.user.surname,
            'subject': obj.teacher.subject.name,
            'photo': obj.teacher.user.profile_img,
        }


class FlowsSerializerProfile(serializers.ModelSerializer):
    teacher = serializers.SerializerMethodField()
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_id = serializers.CharField(source='subject.id', read_only=True)
    students = serializers.SerializerMethodField()
    level_name = serializers.CharField(source='level.name', read_only=True)
    type = serializers.CharField(default='flow', read_only=True)

    class Meta:
        model = Flow
        fields = ['id', 'name', 'level_name', 'activity', 'subject_name', 'teacher', 'students', 'type',
                  'classes', 'subject_id']

    def get_teacher(self, obj):
        return {
            "id": obj.teacher.id if obj.teacher else None,
            'name': obj.teacher.user.name if obj.teacher.user and obj.teacher else None,
            'surname': obj.teacher.user.surname if obj.teacher.user and obj.teacher else None,
            'subject': [
                {
                    "id": subject.id,
                    "name": subject.name
                }
                for subject in obj.teacher.subject.all()
            ],

            'photo': obj.teacher.user.profile_img.url if obj.teacher.user.profile_img else None
        }

    def get_students(self, obj):
        return [
            {
                'id': student.id,
                'name': student.user.name,
                'surname': student.user.surname,
                'phone': student.user.phone,
                'parents_phone': student.parents_number,
                'balance': self.get_debt(student),
                'img': student.user.profile_img.url if student.user.profile_img else None
            }
            for student in obj.students.all()
        ]

    def get_debt(self, student):
        debt = 0
        if student.user.branch.location.system.name == 'school':
            debt = get_remaining_debt_for_student(student.id)
        else:
            groups = student.groups_student.all()
            for group in groups:
                for teacher in group.teacher.all():
                    for salary in teacher.teacher_black_salary.filter(student_id=student.id).all():
                        debt += salary.black_salary if salary.black_salary else 0
        return debt
