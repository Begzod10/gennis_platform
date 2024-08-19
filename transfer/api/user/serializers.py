from user.models import CustomUser, CustomAutoGroup, UserSalary, UserSalaryList, Branch, PaymentTypes
from rest_framework import serializers
from branch.models import Branch
from language.models import Language
from group.models import Group


class OldIdRelatedField(serializers.SlugRelatedField):
    def __init__(self, *args, **kwargs):
        # `slug_field` ni `old_id` ga sozlash
        kwargs['slug_field'] = 'old_id'
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        # `old_id` orqali obyektni olish
        model = self.queryset.model
        try:
            return model.objects.get(old_id=data)
        except model.DoesNotExist:
            raise serializers.ValidationError(f"{model.__name__} with old_id {data} does not exist.")


class TransferUserSerializer(serializers.ModelSerializer):
    branch = OldIdRelatedField(queryset=Branch.objects.all())
    language = OldIdRelatedField(queryset=Language.objects.all(), required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = '__all__'


class TransferStaffs(serializers.ModelSerializer):
    group = serializers.SlugRelatedField(queryset=Group.objects.all(), slug_field='name')
    user = serializers.SlugRelatedField(queryset=CustomUser.objects.all(), slug_field='old_id')

    class Meta:
        model = CustomAutoGroup
        fields = '__all__'


class TransferStaffsSalary(serializers.ModelSerializer):
    permission = serializers.SlugRelatedField(queryset=CustomAutoGroup.objects.all(), slug_field='old_id')
    user = serializers.SlugRelatedField(queryset=CustomUser.objects.all(), slug_field='old_id')

    class Meta:
        model = UserSalary
        fields = '__all__'


class TransferStaffsSalaryList(serializers.ModelSerializer):
    permission = serializers.SlugRelatedField(queryset=CustomAutoGroup.objects.all(), slug_field='old_id')
    user = serializers.SlugRelatedField(queryset=CustomUser.objects.all(), slug_field='old_id')
    user_salary = serializers.SlugRelatedField(queryset=UserSalary.objects.all(), slug_field='old_id')
    payment_types = serializers.SlugRelatedField(queryset=PaymentTypes.objects.all(), slug_field='old_id')
    branch = serializers.SlugRelatedField(queryset=Branch.objects.all(), slug_field='old_id')

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
