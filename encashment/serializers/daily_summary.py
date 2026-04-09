from rest_framework import serializers

from encashment.models import DailySummary


class DailySummarySerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = DailySummary
        fields = [
            'id',
            'date',
            'branch',
            'branch_name',
            'total_students',
            'new_students',
            'deleted_students',
            'present_students',
            'new_deleted_students',
            'total_payments',
            'total_payments_sum',
        ]
