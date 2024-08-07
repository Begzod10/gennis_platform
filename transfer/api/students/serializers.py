from rest_framework import serializers
from subjects.serializers import Subject
from user.serializers import CustomUser
from students.models import Student


class StudentSerializerTransfer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'parents_number', 'shift', 'representative_name',
                  'representative_surname',
                  'old_id', 'extra_payment', 'old_money']

    def create(self, validated_data):
        user_data = validated_data.get('old_user_id')
        subject_data = validated_data.get('id_subjects')
        user = CustomUser.objects.filter(old_id=user_data).first()
        student = Student.objects.create(user=user, **validated_data)
        subjects = []
        for subject in subject_data:
            subject = Subject.objects.get(Subject.old_id == subject)
            subjects.append(subject.id)
        student.subject.set(subjects)
        return student
