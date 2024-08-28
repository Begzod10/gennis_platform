from user.models import CustomUser, CustomAutoGroup, UserSalary, UserSalaryList, Branch, PaymentTypes
from rest_framework import serializers
from branch.models import Branch
from language.models import Language
from django.contrib.auth.models import Group


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


class NameRelatedField(serializers.SlugRelatedField):
    def __init__(self, *args, **kwargs):
        kwargs['slug_field'] = 'name'
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        model = self.queryset.model
        try:
            return model.objects.get(name=data)
        except model.DoesNotExist:
            raise serializers.ValidationError(f"{model.__name__} with old_id {data} does not exist.")


class TransferUserSerializer(serializers.ModelSerializer):
    branch = OldIdRelatedField(queryset=Branch.objects.all())
    language = OldIdRelatedField(queryset=Language.objects.all(), required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = '__all__'


class TransferStaffs(serializers.ModelSerializer):
    group = NameRelatedField(queryset=Group.objects.all())
    user = serializers.SlugRelatedField(queryset=CustomUser.objects.all(), slug_field='old_id')

    class Meta:
        model = CustomAutoGroup
        fields = '__all__'


class TransferStaffsSalary(serializers.ModelSerializer):
    user = OldIdRelatedField(queryset=CustomUser.objects.all(), required=False, allow_null=True)
    permission = OldIdRelatedField(queryset=CustomAutoGroup.objects.all(), required=False, allow_null=True)

    class Meta:
        model = UserSalary
        fields = '__all__'


class TransferStaffsSalaryList(serializers.ModelSerializer):
    user = OldIdRelatedField(queryset=CustomUser.objects.all(), required=False, allow_null=True)
    permission = OldIdRelatedField(queryset=CustomAutoGroup.objects.all(), allow_null=True)
    user_salary = OldIdRelatedField(queryset=UserSalary.objects.all(), allow_null=True)
    payment_types = OldIdRelatedField(queryset=PaymentTypes.objects.all())
    branch = OldIdRelatedField(queryset=Branch.objects.all())

    class Meta:
        model = UserSalaryList
        fields = '__all__'


class TransferUserJobs(serializers.Serializer):
    user_id = serializers.SlugRelatedField(
        queryset=CustomUser.objects.all(), slug_field='old_id'
    )
    group_id = serializers.SlugRelatedField(
        queryset=Group.objects.all(), slug_field='name'
    )

    def create(self, validated_data):
        user = validated_data['user_id']
        group = validated_data['group_id']
        user.groups.add(group)
        return user
