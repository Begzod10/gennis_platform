from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from branch.serializers import BranchSerializer
from language.serializers import LanguageSerializers, Language
from payments.serializers import PaymentTypesSerializers
from user.models import CustomUser, UserSalaryList, UserSalary, Branch


class UserSerializerWrite(serializers.ModelSerializer):
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    language = serializers.PrimaryKeyRelatedField(queryset=Language.objects.all())

    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'surname', 'username', 'father_name', 'password',
                  'phone', 'profile_img', 'observer', 'comment', 'registered_date', 'birth_date', 'language',
                  'branch', 'is_superuser', 'is_staff']
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'birth_date': {'required': False},
            'language': {'required': True},
            'branch': {'required': True},
            'is_superuser': {'required': False},
            'is_staff': {'required': False}
        }


class UserSerializerRead(serializers.ModelSerializer):
    branch = BranchSerializer(read_only=True)
    language = LanguageSerializers(read_only=True)
    age = serializers.SerializerMethodField(required=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'surname', 'username', 'father_name', 'password',
                  'phone', 'profile_img', 'observer', 'comment', 'registered_date', 'birth_date', 'language',
                  'branch', 'is_superuser', 'is_staff', 'age']

    def get_age(self, obj):
        return obj.calculate_age()


class UserSalaryListSerializers(serializers.ModelSerializer):
    # user = UserSerializer(read_only=True)
    # branch = BranchSerializer(read_only=True    )

    class Meta:
        model = UserSalaryList
        fields = '__all__'

    def create(self, validated_data):
        branch = Branch.objects.get(pk=validated_data.get('branch_id'))
        user = User.objects.get(pk=validated_data.get('user_id'))
        user_salary = UserSalary.objects.get(pk=validated_data.get('user_salary_id'))
        user_salary.taken_salary += validated_data.get('salary')
        user_salary.remaining_salary -= validated_data.get('salary')
        user_salary.save()
        user = UserSalaryList.objects.create_user(
            user_salary=user_salary,
            payment_types=validated_data['payment_types'],
            user=user,
            branch=branch,
            salary=validated_data.get('salary'),
            date=validated_data.get('date'),
            comment=validated_data.get('comment', ''),
        )
        return user

    def update(self, instance, validated_data):
        instance.payment_types = validated_data['payment_types'],
        instance.save()
        return instance

    def delete(self, instance):
        instance.deleted = True
        instance.save()
        instance.user_salary.taken_salary -= instance.salary
        instance.user_salary.remaining_salary += instance.salary
        instance.user_salary.save()
        return instance


class UserSalarySerializers(serializers.ModelSerializer):
    class Meta:
        model = UserSalaryList
        fields = '__all__'


class UserSalaryListSerializersRead(serializers.ModelSerializer):
    user = UserSerializerWrite(read_only=True)
    branch = BranchSerializer(read_only=True)
    user_salary = UserSalarySerializers(read_only=True)
    payment_types = PaymentTypesSerializers

    class Meta:
        model = UserSalaryList
        fields = '__all__'


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        user_data = UserSerializerWrite(self.user).data
        data['admin'] = user_data.get('is_staff', False)

        return data
