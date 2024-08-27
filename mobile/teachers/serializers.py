from django.db.models import Sum
from rest_framework import serializers

from teachers.models import TeacherSalary, Teacher
from user.models import CustomUser
from ..get_user import get_user


class TeachersSalariesSerializer(serializers.ModelSerializer):
    salaries = serializers.SerializerMethodField()

    class Meta:
        model = TeacherSalary
        fields = ['salaries']

    def get_salaries(self, obj):
        user = get_user(self.context['request'])
        datas = []
        for i in user.teacher.teacher_salary.all():
            data = {
                "id": i.id,
                "date": i.date.strftime('%Y-%m-%d'),
                "total_salary": i.total_salary,
                "reaming_salary": i.remaining_salary,
                "taken_salary": i.taken_salary,
                "black_salary": i.black_salary

            }
            datas.append(data)
        return datas


class TeachersDebtedStudents(serializers.ModelSerializer):
    students = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = ['students']

    def get_students(self, obj):
        user = get_user(self.context['request'])
        datas = []
        for i in user.teacher.groups.all():
            teachers = i.black_salary.all()
            for teacher in teachers:
                color = ''
                if teacher.student.debt_status == 1:
                    color = 'yellow'
                elif teacher.student.debt_status == 2:
                    color = 'red'
                elif teacher.student.debt_status == 0:
                    color = 'green'
                data = {
                    "id": i.id,
                    "name": teacher.student.user.first_name + ' ' + teachers.student.user.last_name,
                    "group": i.name,
                    "debt": teacher.black_salary,
                    "color": color
                }

                datas.append(data)
        return datas


class TeacherProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = ['user']

    def get_user(self, obj):
        user = get_user(self.context['request'])
        user = CustomUser.objects.get(pk=user)
        salary_aggregate = TeacherSalary.objects.filter(
            teacher=obj
        ).aggregate(
            total_salary=Sum('remaining_salary') + Sum('total_black_salary')
        )
        total_salary = salary_aggregate.get('total_salary', 0)

        data = {
            "user_id": user.id,
            "teacher_id": obj.id,
            "name": user.name,
            "surname": user.surname,
            "father_name": user.father_name,
            "age": user.calculate_age(),
            "birth_date": user.birth_date.strftime('%Y-%m-%d'),
            "phone": user.phone,
            "profile_img": user.profile_img.url if user.profile_img else None,
            "balance": total_salary
        }

        return data

    def update(self, instance, validated_data):
        user = get_user(self.context['request'])
        user = CustomUser.objects.get(pk=user)
        user.name = validated_data['name']
        user.surname = validated_data['surname']
        user.father_name = validated_data['father_name']
        user.phone = validated_data['phone']
        user.birth_date = validated_data['birth_date']
        user.save()
        return user
