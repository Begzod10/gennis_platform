from datetime import date

from rest_framework import serializers
from datetime import datetime, timedelta
from .models import Lead, LeadCall


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'


class LeadListSerializer(serializers.ModelSerializer):
    color = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = "__all__"

    def get_color(self, obj):
        today = date.today()
        leadcalls = obj.lead_id_leadCall.all().order_by('-delay')

        target_date = leadcalls.first().delay if leadcalls.exists() else obj.created
        days_diff = (target_date - today).days

        if days_diff <= 1:
            return 'green'
        elif days_diff == 2:
            return 'yellow'
        elif days_diff == 3:
            return 'pink'
        else:
            return 'red'


class LeadCallSerializer(serializers.ModelSerializer):
    lead = serializers.PrimaryKeyRelatedField(queryset=Lead.objects.all())
    name = serializers.ReadOnlyField(source='lead.name')
    surname = serializers.ReadOnlyField(source='lead.surname')
    phone = serializers.ReadOnlyField(source='lead.phone')

    class Meta:
        model = LeadCall
        fields = ['id', 'lead', 'delay', 'comment', 'status', 'created', 'audio_file', 'other_infos', 'name', 'surname',
                  'phone', 'is_agreed']

    def create(self, validated_data):
        if 'delay' not in validated_data or validated_data['delay'] is None:
            validated_data['delay'] = (datetime.now() + timedelta(days=1)).date()

        return LeadCall.objects.create(**validated_data)


class LeadCallListSerializer(serializers.ModelSerializer):
    lead = LeadSerializer()

    class Meta:
        model = LeadCall
        fields = ['id', 'lead', 'delay', 'comment', 'status']
