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
                    "debt": teacher.teacher_black_salary.black_salary if teacher.teacher_black_salary else 0,
                    "color": color
                }

                datas.append(data)
        return datas


class TeacherProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(required=False,read_only=True)
    name = serializers.CharField(write_only=True, required=False)
    surname = serializers.CharField(write_only=True, required=False)
    father_name = serializers.CharField(write_only=True, required=False)
    birth_date = serializers.CharField(write_only=True, required=False)
    phone = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Teacher
        fields = ['user','phone','birth_date','father_name','surname','name']

    def get_user(self, obj):
        user = get_user(self.context['request'])
        user = CustomUser.objects.get(pk=user)
        teacher =Teacher.objects.get(user_id=user.id)
        salary_aggregate = TeacherSalary.objects.filter(
            teacher=teacher
        ).aggregate(
            total_salary=Sum('remaining_salary') + Sum('total_black_salary')
        )
        total_salary = salary_aggregate.get('total_salary', 0)

        data = {
            "user_id": user.id,
            "teacher_id": teacher.id,
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
        try:
            user = CustomUser.objects.get(pk=user)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")

        user.name = validated_data.get('name', user.name)
        user.surname = validated_data.get('surname', user.surname)
        user.father_name = validated_data.get('father_name', user.father_name)
        user.phone = validated_data.get('phone', user.phone)
        user.birth_date = validated_data.get('birth_date', user.birth_date)

        user.save()

        return user
