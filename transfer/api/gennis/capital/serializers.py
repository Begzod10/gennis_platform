from rest_framework import serializers

from branch.models import Branch
from payments.models import PaymentTypes
from user.serializers import CustomUser
from capital.models import OldCapital
from django.db import transaction


class OldCapitalSerializerTransfer(serializers.ModelSerializer):
    by_who = serializers.SlugRelatedField(queryset=CustomUser.objects.all(), slug_field='old_id', required=False)
    payment_types = serializers.SlugRelatedField(queryset=PaymentTypes.objects.all(), slug_field='old_id')
    branch = serializers.SlugRelatedField(queryset=Branch.objects.all(), slug_field='old_id')

    class Meta:
        model = OldCapital
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop('by_who')
        user = CustomUser.objects.get(old_id=user_data.old_id)
        payment_types_data = validated_data.pop('payment_types')
        payment_types = PaymentTypes.objects.get(old_id=payment_types_data.old_id)
        branch_data = validated_data.pop('branch')
        branch = Branch.objects.get(old_id=branch_data.old_id)
        student = OldCapital.objects.create(by_who=user, payment_types=payment_types, branch=branch, **validated_data)
        return student
