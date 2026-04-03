from rest_framework import serializers

class DebtorSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    phone = serializers.CharField()
    parent_phone = serializers.CharField()
    debt = serializers.IntegerField()
    months_count = serializers.IntegerField()
    color = serializers.CharField()