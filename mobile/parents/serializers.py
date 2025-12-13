# time_table/serializers.py
from rest_framework import serializers
from school_time_table.models import ClassTimeTable
from attendances.models import StudentDailyAttendance, AttendancePerMonth


class ClassTimeTableSerializer(serializers.ModelSerializer):
    # Add nested data for better readability
    room_name = serializers.CharField(source='room.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    start_time = serializers.TimeField(source='hours.start_time', read_only=True)
    end_time = serializers.TimeField(source='hours.end_time', read_only=True)

    class Meta:
        model = ClassTimeTable
        fields = [
            'id',
            'name',
            'date',
            'start_time',
            'end_time',
            'room',
            'room_name',
            'teacher',
            'teacher_name',
            'subject',
            'subject_name',
            'group',
            'group_name',
        ]


class StudentDailyAttendanceMobileSerializer(serializers.ModelSerializer):
    student_id = serializers.IntegerField(write_only=True)
    group_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = StudentDailyAttendance
        fields = ["id", "student_id", "group_id", "day", "status", "reason", "entry_time", "leave_time"]


class AttendancePerMonthParentSerializer(serializers.ModelSerializer):


    class Meta:
        model = AttendancePerMonth
        fields = ['id', 'status', 'total_debt', 'ball_percentage', 'month_date',
                  'total_charity', 'remaining_debt', 'payment', 'remaining_salary',
                  ]