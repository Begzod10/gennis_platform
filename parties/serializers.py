from rest_framework import serializers
from .models import Party, PartyTask


class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = "__all__"

class PartySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = ["id", "name"]


class PartyTaskSerializer(serializers.ModelSerializer):
    parties = serializers.PrimaryKeyRelatedField(
        queryset=Party.objects.all(),
        many=True
    )
    parties_info = PartySimpleSerializer(
        source="parties",
        many=True,
        read_only=True
    )

    class Meta:
        model = PartyTask
        fields = "__all__"