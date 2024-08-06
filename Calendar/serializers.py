from rest_framework import serializers

from .models import Years, Month, Day, TypeDay


class TypeDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeDay
        fields = '__all__'


class YearsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Years
        fields = '__all__'


class MonthSerializer(serializers.ModelSerializer):
    years = YearsSerializer()

    class Meta:
        model = Month
        fields = '__all__'


class DaySerializer(serializers.ModelSerializer):
    type_id = TypeDaySerializer()
    month = MonthSerializer()

    class Meta:
        model = Day
        fields = '__all__'
