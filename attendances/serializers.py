from datetime import datetime, timedelta

from rest_framework import serializers

from group.serializers import GroupSerializer
from lesson_plan.functions.utils import update_lesson_plan
from students.models import Student
from students.serializers import StudentSerializer
from tasks.models import TaskStatistics, TaskStudent
from teachers.models import Teacher
from teachers.models import TeacherBlackSalary
from teachers.models import TeacherSalary
from teachers.serializers import TeacherSerializer
from .Api.functions.CalculateGroupOverallAttendance import calculate_group_attendances
from .models import AttendancePerDay, AttendancePerMonth
from .models import Group


class AttendancePerMonthSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    group = GroupSerializer()

    class Meta:
        model = AttendancePerMonth
        fields = ['id', 'status', 'total_debt', 'total_salary', 'ball_percentage', 'month_date',
                  'total_charity', 'remaining_debt', 'payment', 'remaining_salary', 'student',
                  'taken_salary', 'group']


class AttendancePerDaySerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    teacher = TeacherSerializer()
    group = GroupSerializer()
    attendance_per_month = AttendancePerMonthSerializer()

    class Meta:
        model = AttendancePerDay
        fields = ['id', 'status', 'debt_per_day', 'salary_per_day', 'charity_per_day', 'day',
                  'homework_ball', 'dictionary_ball', 'activeness_ball', 'average', 'teacher', 'student',
                  'status', 'group', 'attendance_per_month']


class StudentDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    homework = serializers.IntegerField()
    dictionary = serializers.IntegerField()
    active = serializers.IntegerField()
    type = serializers.CharField()


class AttendancePerDayCreateUpdateSerializer(serializers.ModelSerializer):
    students = serializers.ListField(
        child=StudentDetailSerializer(),
        write_only=True  # Ensure this field is used only during write operations
    )
    date = serializers.CharField(default=None, allow_blank=True)
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    class Meta:
        model = AttendancePerDay
        fields = ['id', 'status', 'debt_per_day', 'salary_per_day', 'charity_per_day', 'day',
                  'homework_ball', 'dictionary_ball', 'activeness_ball', 'average', 'teacher', 'students',
                  'status', 'group', 'attendance_per_month', 'date']

    def create(self, validated_data):
        teacher = validated_data.get('teacher')
        group = validated_data.get('group')
        students = validated_data.pop('students', [])
        date = validated_data.get('date')
        today = datetime.today()
        tomorrow = today + timedelta(days=1)
        month_date = f"{today.year}-{date}"
        year = today.year

        day = datetime.strptime(f"{today.year}-{date}", "%Y-%m-%d")
        month = day.month

        errors = []
        status = False
        attendance_per_day = None

        def update_attendance_per_month(current_month_attendance):
            overall_salary = overall_debt = overall_charity = monthly_average = 0
            for attendance in current_month_attendance.attendanceperday_set.all():
                overall_salary += attendance.salary_per_day
                overall_debt += attendance.debt_per_day
                overall_charity += attendance.charity_per_day
                monthly_average += attendance.average
            count = current_month_attendance.attendanceperday_set.count()
            current_month_attendance.total_debt = overall_debt
            current_month_attendance.total_salary = overall_salary
            current_month_attendance.total_charity = overall_charity
            current_month_attendance.ball_percentage = monthly_average / count if count else 0
            current_month_attendance.save()

        def calculate_and_create_attendance(student, current_month_attendance, charity_data=None):
            student_dt = Student.objects.get(pk=student['id'])

            average = (student['homework'] + student['dictionary'] + student['active']) / 3
            salary_per_day = group.teacher_salary / 13
            if student_dt.debt_status == 2:
                black_salary, created = TeacherBlackSalary.objects.get_or_create(
                    teacher_id=teacher.id,
                    student_id=student['id'],
                    group_id=group.id,
                    month_date=month_date,
                    status=False
                )
                black_salary.black_salary += salary_per_day
                black_salary.save()
            charity_per_day = charity_data.charity_sum / 13 if charity_data else 0
            if charity_per_day == 0:
                debt_per_day = group.price / 13
            else:
                debt_per_day = (group.price / 13) - charity_per_day
            update_lesson_plan(group.id)
            nonlocal attendance_per_day
            attendance_per_day = AttendancePerDay.objects.create(
                group_id=group.id,
                student_id=student['id'],
                teacher=teacher,
                status=bool(student['type']),
                attendance_per_month_id=current_month_attendance.id,
                debt_per_day=debt_per_day,
                salary_per_day=salary_per_day,
                charity_per_day=charity_per_day,
                day=day,
                homework_ball=student['homework'],
                dictionary_ball=student['dictionary'],
                activeness_ball=student['active'],
                average=average
            )

        for student in students:
            current_month_attendance, created = AttendancePerMonth.objects.get_or_create(
                month_date__year=year,
                month_date__month=month,
                defaults={'month_date': month_date},
                group_id=group.id,
                student_id=student['id'],
                teacher=teacher
            )
            student_data = Student.objects.get(pk=student['id'])
            if current_month_attendance:
                if current_month_attendance.remaining_debt == 0:
                    student_data.debt_status = 0
                elif student_data.total_payment_month > current_month_attendance.total_debt:
                    student_data.debt_status = 1
                    TeacherBlackSalary.objects.filter(student=student_data, status=False).update(status=True)
                elif student_data.total_payment_month < current_month_attendance.total_debt:
                    student_data.debt_status = 2
                    static, _ = TaskStatistics.objects.get_or_create(
                        task__name="Qarzdor uquvchilar",
                        day=tomorrow,
                        defaults={'progress_num': 100, 'percentage': 0, 'completed_num': 0, 'user': 11}
                    )
                    TaskStudent.objects.get_or_create(
                        task__name="Qarzdor uquvchilar",
                        task_static=static,
                        status=False,
                        students=student
                    )

                student_data.save()
            try:
                AttendancePerDay.objects.get(group_id=group.id, teacher=teacher, day=day, student_id=student['id'])
                errors.append(
                    {'msg': f'bu kunda {student_data.user.name} {student_data.user.surname} davomat qilingan'})
            except AttendancePerDay.DoesNotExist:
                status = True
                charity_data = student_data.charity_student_id.filter(student_id=student['id'],
                                                                      group_id=group.id).first()
                calculate_and_create_attendance(student, current_month_attendance, charity_data)
                update_attendance_per_month(current_month_attendance)
        teacher_attendances_per_month = teacher.attendance_per_month.filter(month_date=month_date)
        salary = sum(attendance.total_salary for attendance in teacher_attendances_per_month)
        current_salary, created = TeacherSalary.objects.get_or_create(month_date=month_date,
                                                                      branch_id=group.branch_id, teacher_id=teacher.id)
        current_salary.total_salary = salary
        teacher_black_salaries = teacher.teacher_black_salary.filter(month_date=month_date)
        overall_black_salary = 0
        for teacher_black_salary in teacher_black_salaries:
            overall_black_salary += teacher_black_salary.black_salary
        current_salary.overall_black_salary = overall_black_salary
        current_salary.total_salary = salary - current_salary.overall_black_salary
        current_salary.save()

        calculate_group_attendances(group.id, month_date)
        if not status:
            raise serializers.ValidationError({"detail": errors})
        else:
            return attendance_per_day


class StudentDetailSchoolSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    status = serializers.BooleanField()
    reason = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class AttendancePerDayCreateUpdateSerializerSchool(serializers.ModelSerializer):
    students = serializers.ListField(
        child=StudentDetailSchoolSerializer(),
        write_only=True
    )
    date = serializers.CharField(default=None, allow_blank=True)
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    class Meta:
        model = AttendancePerDay
        fields = ['id', 'teacher', 'students', 'group', 'date']

    def create(self, validated_data):
        teacher = validated_data.get('teacher')
        group = validated_data.get('group')
        students = validated_data.pop('students', [])
        date = validated_data.get('date')
        today = datetime.today()
        day = datetime.strptime(f"{today.year}-{date}", "%Y-%m-%d")

        errors = []
        created_instances = []
        update_lesson_plan(group.id)

        for student in students:
            student_data = Student.objects.get(pk=student['id'])
            try:
                AttendancePerDay.objects.get(group_id=group.id, teacher=teacher, day=day, student_id=student['id'])
                errors.append(
                    {
                        'msg': f'Attendance already exists for {student_data.user.name} {student_data.user.surname} on this day.'}
                )
            except AttendancePerDay.DoesNotExist:
                attendance = AttendancePerDay.objects.create(
                    teacher=teacher,
                    group=group,
                    student=student_data,
                    day=day,
                    status=student['status'],
                    reason=student.get('reason', None)
                )
                created_instances.append(attendance)

        if errors:
            raise serializers.ValidationError({"detail": errors})

        return created_instances[0] if created_instances else None


from .models import StudentDailyAttendance, StudentMonthlySummary


class StudentDailyAttendanceSerializer(serializers.ModelSerializer):

    student_id = serializers.IntegerField(write_only=True)
    group_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = StudentDailyAttendance
        fields = ["id", "student_id", "group_id", "day", "status", "reason"]

    def create(self, validated_data):
        student_id = validated_data.pop("student_id")
        group_id = validated_data.pop("group_id")
        day = validated_data["day"]

        year = day.year
        month = day.month

        summary, created = StudentMonthlySummary.objects.get_or_create(
            student_id=student_id,
            group_id=group_id,
            year=year,
            month=month,
            defaults={"stats": {}}
        )

        daily = StudentDailyAttendance.objects.create(
            monthly_summary=summary,
            day=day,
            status=validated_data.get("status", False),
            reason=validated_data.get("reason", None),
        )

        return daily


class StudentMonthlySummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentMonthlySummary
        fields = "__all__"
