from rest_framework import serializers

from system.serializers import SystemSerializers, System
from .models import Location


class LocationSerializers(serializers.ModelSerializer):
    system = serializers.PrimaryKeyRelatedField(queryset=System.objects.all())

    class Meta:
        model = Location
        fields = '__all__'


class LocationListSerializers(serializers.ModelSerializer):
    system = SystemSerializers(read_only=True)

    class Meta:
        model = Location
        fields = ['id', 'name', 'number', 'system']


class LocationListSerializersWithBranch(serializers.ModelSerializer):
    system = SystemSerializers(read_only=True)
    branches = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = ['id', 'name', 'number', 'system','branches']

    def get_branches(self, obj):
        from branch.serializers import BranchSerializer, Branch
        from students.models import Student
        branches = Branch.objects.filter(location_id=obj.pk).all()
        datas =[]
        for branch in branches:
            students = Student.objects.filter(user__branch_id=branch.pk).count()
            datas.append({
                'id': branch.pk,
                'name': branch.name,
                'number': branch.number,
                'count': students
            })

        return datas
