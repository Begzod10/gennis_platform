from rest_framework import serializers

from group.models import Group
from students.models import Student
from .models import (
    Party, PartyMember, PartyTask, PartyTaskGrade,
    Competition, CompetitionResult,
)


class StudentSelectSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['id', 'label', 'born_date']

    def get_label(self, obj):
        return f"{obj.user.name} {obj.user.surname}"


class GroupSelectSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'label']

    def get_label(self, obj):
        if obj.name:
            return obj.name
        parts = []
        if obj.class_number:
            parts.append(str(obj.class_number.number))
        if obj.color.name:
            parts.append(obj.color.name)
        return " ".join(parts) if parts else f"Guruh #{obj.id}"


class PartyMemberSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_class = serializers.SerializerMethodField()

    class Meta:
        model = PartyMember
        fields = [
            'id', 'party', 'student',
            'student_name', 'student_class',
            'role', 'ball', 'level', 'status', 'is_active', 'joined_at',
        ]

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"

    def get_student_class(self, obj):
        return getattr(obj.student, 'class_number', None) or "—"


class PartyMemberWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartyMember
        fields = ['party', 'student', 'role', 'ball', 'level', 'status', 'is_active']


class PartyInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = ['id', 'name', 'color']


class PartyListSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    members_count = serializers.SerializerMethodField()
    wins_count = serializers.SerializerMethodField()
    tasks_count = serializers.SerializerMethodField()
    groups_count = serializers.SerializerMethodField()

    class Meta:
        model = Party
        fields = [
            'id', 'name', 'display_name', 'image', 'color', 'rating', 'ball',
            'members_count', 'wins_count', 'tasks_count', 'groups_count', 'desc',
        ]

    def get_display_name(self, obj):
        return obj.display_name()

    def get_members_count(self, obj):
        return obj.students.count()

    def get_wins_count(self, obj):
        return obj.competition_results.filter(is_winner=True).count()

    def get_tasks_count(self, obj):
        return obj.tasks.count()

    def get_groups_count(self, obj):
        return obj.groups.count()


class PartyDetailSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    memberships = PartyMemberSerializer(many=True, read_only=True)
    groups_info = GroupSelectSerializer(source='groups', many=True, read_only=True)

    students = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        many=True, write_only=True, required=False,
    )
    groups = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        many=True, write_only=True, required=False,
    )

    class Meta:
        model = Party
        fields = [
            'id', 'name', 'display_name', 'image', 'desc', 'color', 'rating', 'ball',
            'students', 'groups',
            'memberships', 'groups_info',
        ]

    def get_display_name(self, obj):
        return obj.display_name()

    def create(self, validated_data):
        students = validated_data.pop('students', [])
        groups = validated_data.pop('groups', [])
        party = Party.objects.create(**validated_data)
        party.students.set(students)
        party.groups.set(groups)
        return party

    def update(self, instance, validated_data):
        students = validated_data.pop('students', None)
        groups = validated_data.pop('groups', None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if students is not None:
            instance.students.set(students)
        if groups is not None:
            instance.groups.set(groups)
        return instance


class PartyTaskGradeSerializer(serializers.ModelSerializer):
    party_name = serializers.CharField(source='party.name', read_only=True)
    party_color = serializers.CharField(source='party.color', read_only=True)

    class Meta:
        model = PartyTaskGrade
        fields = ['id', 'task', 'party', 'party_name', 'party_color', 'ball', 'graded_at']


class PartyTaskSerializer(serializers.ModelSerializer):
    # parties_info = PartyInfoSerializer(source='parties', many=True, read_only=True)
    # grades = PartyTaskGradeSerializer(many=True, read_only=True)
    parties_info = serializers.SerializerMethodField()


    class Meta:
        model = PartyTask
        fields = [
            'id', 'name', 'desc', 'ball', 'deadline',
            'is_completed', 'created_at',
            'parties',
            'parties_info',
        ]
        extra_kwargs = {
            'parties': {'write_only': True, 'required': False},
        }

    def get_parties_info(self, obj):
        result = []

        grades = {g.party_id: g for g in obj.grades.all()}

        for party in obj.parties.all():
            grade = grades.get(party.id)

            result.append({
                "id": party.id,
                "name": party.name,
                "color": party.color,
                "ball": grade.ball if grade else 0,
                "graded_at": grade.graded_at if grade else 0,
            })

        return result

class CompetitionResultSerializer(serializers.ModelSerializer):
    party_name = serializers.CharField(source='party.name', read_only=True)
    party_color = serializers.CharField(source='party.color', read_only=True)

    class Meta:
        model = CompetitionResult
        fields = [
            'id', 'competition', 'party', 'party_name', 'party_color',
            'quarter', 'ball', 'note', 'is_winner', 'created_at',
        ]


class CompetitionSerializer(serializers.ModelSerializer):
    results = CompetitionResultSerializer(many=True, read_only=True)

    class Meta:
        model = Competition
        fields = ['id', 'name', 'emoji', 'color', 'results', 'created_at']
