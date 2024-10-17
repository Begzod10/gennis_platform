from django.db.models import Sum
from django.db.models.functions import ExtractMonth, ExtractYear
from django.utils.timezone import localtime
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from attendances.models import AttendancePerDay
from group.serializers import GroupCreateUpdateSerializer
from teachers.models import TeacherSalary, Teacher
from user.models import CustomUser
from ..get_user import get_user

BASE_URL = 'http://192.168.0.101:8000'


class YearMonthSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    months = serializers.ListField(child=serializers.IntegerField())

    def to_representation(self, instance):
        return {
            'year': instance['year'],
            'months': sorted(instance['months'])
        }


class TeachersSalariesSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    month_date = serializers.DateField()
    total_salary = serializers.IntegerField()
    remaining_salary = serializers.IntegerField()
    taken_salary = serializers.IntegerField()
    total_black_salary = serializers.IntegerField()

    class Meta:
        model = TeacherSalary
        fields = ['id', 'month_date', 'total_salary', 'remaining_salary', 'taken_salary', 'total_black_salary']





class TeachersDebtedStudents(serializers.ModelSerializer):
    students = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Teacher
        fields = ['students']

    def get_students(self, obj):
        datas = []
        today = localtime()
        teachers = obj.teacherblacksalary_set.filter(month_date__year=today.year, month_date__month=today.month).all()
        for teacher in teachers:
            color = ''
            if teacher.student.debt_status == 1:
                color = 'yellow'
            elif teacher.student.debt_status == 2:
                color = 'red'
            elif teacher.student.debt_status == 0:
                color = 'green'
            data = {
                "id": obj.id,
                "name": teacher.student.user.name,
                'surname': teacher.student.user.surname,
                "group": obj.name,
                "debt": teacher.black_salary if teacher.black_salary else 0,
                "color": color
            }

            datas.append(data)
        if datas:
            return datas
        else:
            raise NotFound(detail="Joriy oy uchun qarzdor talabalar topilmadi.")


class TeacherProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(required=False, read_only=True)
    name = serializers.CharField(write_only=True, required=False)
    surname = serializers.CharField(write_only=True, required=False)
    father_name = serializers.CharField(write_only=True, required=False)
    birth_date = serializers.CharField(write_only=True, required=False)
    phone = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Teacher
        fields = ['user', 'phone', 'birth_date', 'father_name', 'surname', 'name']

    def get_user(self, obj):
        user = get_user(self.context['request'])
        user = CustomUser.objects.get(pk=user)
        teacher = Teacher.objects.get(user_id=user.id)
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
            "profile_img": BASE_URL + user.profile_img.url if user.profile_img else None,
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


class AttendancesTodayStudentsSerializer(serializers.ModelSerializer):
    attendances = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Teacher
        fields = ['attendances']

    def get_attendances(self, obj):

        datas = []
        today = localtime()
        students = obj.students.all()
        for student in students:
            attendances = AttendancePerDay.objects.filter(day__year=today.year, day__month=today.month,
                                                          day__day=today.day, teacher__in=obj.teacher.all(),
                                                          student_id=student.id).first()
            if not attendances:
                datas.append({
                    'name': student.user.name + ' ' + ' ' + student.user.surname,
                    'group': obj.name,
                    'balance': student.total_payment_month,
                    'date': today.strftime('%Y-%m-%d')
                })

        return datas


# class GetLessonPlanSerializer(serializer.ModelSerializer):
#
#     class Meta:
#         model = Teacher
#         fields = ['id', 'name', 'description']
class GroupListSeriliazersMobile(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Teacher
        fields = ['groups']

    def get_groups(self, obj):
        return GroupCreateUpdateSerializer(obj).data
