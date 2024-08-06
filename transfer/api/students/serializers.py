from rest_framework import serializers
from subjects.serializers import Subject
from user.serializers import CustomUser
from students.models import Student


class StudentSerializerTransfer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), many=True)
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), many=True)

    class Meta:
        model = Student
        fields = ['id', 'user', 'subject', 'parents_number', 'shift', 'representative_name', 'representative_surname',
                  'old_id', 'extra_payment', 'old_money']

    def create(self, validated_data):
        user_data = validated_data.get('user')
        subject_data = validated_data.get('subject')
        user = CustomUser.objects.get(CustomUser.old_id == user_data)
        student = Student.objects.create(user=user, **validated_data)
        for subject in subject_data:
            subject = Subject.objects.get(Subject.old_id == subject)
            student.subject.set(subject)
        return student
