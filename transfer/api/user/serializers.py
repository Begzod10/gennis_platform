from django.contrib.auth.models import Group
from rest_framework import serializers

from user.models import CustomUser, CustomAutoGroup, UserSalary, UserSalaryList, Branch, PaymentTypes


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
