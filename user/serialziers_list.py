from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import Group
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from werkzeug.security import check_password_hash

from branch.serializers import BranchSerializer
from language.serializers import LanguageSerializers, Language
from payments.serializers import PaymentTypesSerializers, PaymentTypes
from permissions.models import ManySystem, ManyBranch, ManyLocation
from user.models import CustomUser, UserSalaryList, UserSalary, Branch, CustomAutoGroup


class UsersWithJobSerializers(serializers.ModelSerializer):
    job = serializers.SerializerMethodField(required=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'surname',
                  'profile_img', 'job', 'file']

    def get_job(self, obj):
        return [group.name for group in obj.groups.all()]
