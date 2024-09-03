from rest_framework import serializers

from subjects.models import Subject, SubjectLevel


class SubjectSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=250)
    desc = serializers.CharField(null=True, blank=True)
    disabled = serializers.BooleanField(default=False)
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Subject
        fields = '__all__'

    def create(self, validated_data):
        subject = Subject(**validated_data)
        subject.save()
        return subject




class SubjectLevelSerializer(serializers.ModelSerializer):
    old_id = serializers.IntegerField(required=False)
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())

    class Meta:
        model = SubjectLevel
        fields = '__all__'


class SubjectLevelListSerializer(serializers.ModelSerializer):
    old_id = serializers.IntegerField(required=False)
    subject = SubjectSerializer(read_only=True)

    class Meta:
        model = SubjectLevel
        fields = '__all__'


