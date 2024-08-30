from rest_framework import serializers

from branch.models import Branch
from payments.models import PaymentTypes
from user.serializers import CustomUser
from capital.models import OldCapital
from django.db import transaction


class OldIdRelatedField(serializers.SlugRelatedField):
    def __init__(self, *args, **kwargs):
        kwargs['slug_field'] = 'old_id'
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        model = self.queryset.model
        try:
            return model.objects.get(old_id=data)
        except model.DoesNotExist:
            raise serializers.ValidationError(f"{model.__name__} with old_id {data} does not exist.")


class OldCapitalSerializerTransfer(serializers.ModelSerializer):
    by_who = OldIdRelatedField(queryset=CustomUser.objects.all(), required=False)
    payment_type = OldIdRelatedField(queryset=PaymentTypes.objects.all(), )
    branch = OldIdRelatedField(queryset=Branch.objects.all())

    class Meta:
        model = OldCapital
        fields = '__all__'

    # @transaction.atomic
    # def create(self, validated_data):
    #     user_data = validated_data.pop('by_who')
    #     user = CustomUser.objects.get(old_id=user_data.old_id)
    #     branch_data = validated_data.pop('branch')
    #     branch = Branch.objects.get(old_id=branch_data.old_id)
    #     student = OldCapital.objects.create(by_who=user, payment_type=validated_data.pop('payment_type'), branch=branch,
    #                                         **validated_data)
    #     return student
