from rest_framework import serializers
from subjects.serializers import Subject
from user.serializers import CustomUser
from students.models import Student


class StudentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), many=True)
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), many=True)

    class Meta:
        model = Student
        fields = ['id', 'user', 'subject', 'parents_number', 'shift', 'representative_name', 'representative_surname',
                  'old_id', 'extra_payment', 'old_money']
