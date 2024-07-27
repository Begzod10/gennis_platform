from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from branch.serializers import BranchSerializer
from language.serializers import Language
from language.serializers import LanguageSerializers
from user.models import CustomUser, UserSalaryList, UserSalary, Branch


class UserSerializer(serializers.ModelSerializer):
    branch = BranchSerializer()
    language = LanguageSerializers()
    age = serializers.SerializerMethodField(required=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'surname', 'username', 'father_name', 'password',
                  'phone', 'age', 'profile_img', 'observer', 'comment', 'registered_date', 'birth_date', 'language',
                  'branch', 'is_superuser', 'is_staff', 'age']
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'birth_date': {'required': False},
            'language': {'required': True},
            'branch': {'required': True},
            'is_superuser': {'required': False},
            'is_staff': {'required': False}
        }

    def get_age(self, obj):
        return obj.calculate_age()

    def create(self, validated_data):
        branch_data = validated_data.pop('branch', None)
        language_data = validated_data.pop('language', None)

        branch = Branch.objects.get(name=branch_data['name']) if isinstance(branch_data, dict) else None
        language = Language.objects.get(name=language_data['name']) if isinstance(language_data, dict) else None

        user = CustomUser.objects.create_user(
            name=validated_data.get('name'),
            surname=validated_data.get('surname'),
            username=validated_data.get('username'),
            father_name=validated_data.get('father_name'),
            password=validated_data.get('password'),
            phone=validated_data.get('phone'),
            profile_img=validated_data.get('profile_img'),
            observer=validated_data.get('observer'),
            comment=validated_data.get('comment'),
            registered_date=validated_data.get('registered_date'),
            birth_date=validated_data.get('birth_date'),
            language=language,
            branch=branch
        )
        return user

    def update(self, instance, validated_data):
        branch_data = validated_data.pop('branch', None)
        language_data = validated_data.pop('language', None)

        instance.username = validated_data.get('username', instance.username)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.name = validated_data.get('name', instance.name)
        instance.surname = validated_data.get('surname', instance.surname)
        instance.father_name = validated_data.get('father_name', instance.father_name)
        instance.birth_date = validated_data.get('birth_date', instance.birth_date)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.age = validated_data.get('age', instance.age)
        instance.profile_img = validated_data.get('profile_img', instance.profile_img)
        instance.observer = validated_data.get('observer', instance.observer)
        instance.comment = validated_data.get('comment', instance.comment)

        if branch_data and isinstance(branch_data, dict):
            branch = Branch.objects.get(name=branch_data['name'])
            instance.branch = branch

        if language_data and isinstance(language_data, dict):
            language = Language.objects.get(name=language_data['name'])
            instance.language = language

        instance.save()
        return instance


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


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        user_data = UserSerializer(self.user).data
        data['admin'] = user_data.get('is_staff', False)

        return data
