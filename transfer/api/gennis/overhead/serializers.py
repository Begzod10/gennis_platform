from rest_framework import serializers
from branch.models import Branch
from payments.serializers import PaymentTypes
from overhead.models import Overhead


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


class TransferOverheadSerializerCreate(serializers.ModelSerializer):
    payment = OldIdRelatedField(queryset=PaymentTypes.objects.all(), required=False, allow_null=True)
    branch = OldIdRelatedField(queryset=Branch.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Overhead
        fields = '__all__'
