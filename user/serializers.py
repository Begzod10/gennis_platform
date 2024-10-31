import requests
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


class UserSerializerRead(serializers.ModelSerializer):
    branch = BranchSerializer(read_only=True)
    language = LanguageSerializers(read_only=True)
    age = serializers.SerializerMethodField(required=False)
    job = serializers.SerializerMethodField(required=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'surname', 'username', 'father_name', 'password',
                  'phone', 'profile_img', 'observer', 'comment', 'registered_date', 'birth_date', 'language',
                  'branch', 'is_superuser', 'is_staff', 'age', 'job', 'file']

    def get_age(self, obj):
        return obj.calculate_age()

    def get_job(self, obj):
        return [group.name for group in obj.groups.all()]


class UserSerializerWrite(serializers.ModelSerializer):
    old_id = serializers.IntegerField(required=False)
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    language = serializers.PrimaryKeyRelatedField(queryset=Language.objects.all())
    profession = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), required=False, allow_null=True)
    money = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'surname', 'username', 'father_name', 'password',
                  'phone', 'profile_img', 'observer', 'comment', 'registered_date', 'birth_date', 'language',
                  'branch', 'is_superuser', 'is_staff', 'old_id', 'profession', 'money']
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'birth_date': {'required': False},
            'language': {'required': True},
            'branch': {'required': True},
            'is_superuser': {'required': False},
            'is_staff': {'required': False}
        }

    def create(self, validated_data):
        # test
        profession = validated_data.pop('profession', None)

        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        branch = validated_data.get('branch')
        if branch and branch.location:
            system = branch.location.system
            ManySystem.objects.get_or_create(user=user, system=system)
            ManyLocation.objects.get_or_create(user=user, location=branch.location)
            ManyBranch.objects.get_or_create(user=user, branch=branch)
        if profession is not None:
            CustomAutoGroup.objects.create(user=user, group=profession, salary='0')
            user.groups.add(profession)
            if profession.name == 'admin':
                user.is_superuser = True
                user.is_staff = True
                user.save()
            elif profession.name == 'director':
                user.is_staff = True
                user.is_superuser = True
                user.save()
        return user

    def update(self, instance, validated_data):
        profession = validated_data.pop('profession', None)
        if profession is not None:
            instance.groups.clear()
            instance.groups.add(profession)
            CustomAutoGroup.objects.filter(user=instance).update(group=profession)

        salary = validated_data.pop('money', None)
        if salary is not None:
            CustomAutoGroup.objects.filter(user=instance).update(salary=salary)
        user = super().update(instance, validated_data)
        if 'password' in validated_data:
            user.set_password(validated_data['password'])
            user.save()

        # user_data = UserSerializerRead(user).data
        # self.send_data(user_data)
        return user


class UserSalaryListSerializers(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), required=False)
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), required=False)
    user_salary = serializers.PrimaryKeyRelatedField(queryset=UserSalary.objects.all(), required=False)
    payment_types = serializers.PrimaryKeyRelatedField(queryset=PaymentTypes.objects.all(), required=False)
    name = serializers.SerializerMethodField(required=False, read_only=True)
    surname = serializers.SerializerMethodField(required=False, read_only=True)
    payment_type_name = serializers.SerializerMethodField(required=False, read_only=True)

    class Meta:
        model = UserSalaryList
        fields = '__all__'

    def get_name(self, obj):
        return obj.user.name

    def get_surname(self, obj):
        return obj.user.surname

    def get_payment_type_name(self, obj):
        return obj.payment_types.name

    def create(self, validated_data):
        branch = validated_data.get('branch')
        user = validated_data.get('user')
        user_salary = validated_data.get('user_salary')
        payment_types = validated_data.get('payment_types')
        user_salary.taken_salary += validated_data.get('salary')
        user_salary.remaining_salary -= validated_data.get('salary')
        user_salary.save()
        user = UserSalaryList.objects.create(
            user_salary=user_salary,
            payment_types=payment_types,
            user=user,
            date=validated_data.get('date'),
            branch=branch,
            salary=validated_data.get('salary'),
            comment=validated_data.get('comment', ''),
        )
        return user

    def update(self, instance, validated_data):
        payment_types = validated_data.get('payment_types')
        if payment_types:
            instance.payment_types_id = payment_types.id
        instance.save()
        return instance


class CustomAutoGroupSerializers(serializers.ModelSerializer):
    class Meta:
        model = CustomAutoGroup
        fields = '__all__'


class UserSalarySerializers(serializers.ModelSerializer):
    permission = CustomAutoGroupSerializers(read_only=True)

    class Meta:
        model = UserSalary
        fields = '__all__'


class UserSalaryListSerializersRead(serializers.ModelSerializer):
    user = UserSerializerRead(read_only=True)
    branch = BranchSerializer(read_only=True)
    user_salary = UserSalarySerializers(read_only=True)
    payment_types = PaymentTypesSerializers(read_only=True)

    class Meta:
        model = UserSalaryList
        fields = '__all__'


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def send_data(self, user_data, url):
        try:
            response = requests.post(url, json={"user": user_data})
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise serializers.ValidationError({"error": str(e)})

    def user_send(self, user, password):
        user = CustomUser.objects.get(id=user)
        from students.models import Student,Teacher
        student = Student.objects.filter(user=user).first()
        teacher = Teacher.objects.filter(user=user).first()


        if student:
            object = {
                'id': user.id,
                'name': user.name,
                'surname': user.surname,
                'username': user.username,
                'father_name': user.father_name,
                'password': password,
                'balance': student.id,
                'role': 'student',
                'birth_date': user.birth_date.isoformat() if user.birth_date else None,
                'phone_number': user.phone,
                'groups': [{
                    'name': group.name,
                    'id': group.id,
                    'subject': group.subject,
                    'teacher_salary': group.teacher_salary,
                    'price': group.price
                } for group in student.groups_student.all()]
            }
            self.send_data(object, 'http://192.168.1.17:5001/api/turon_user')
            return object
        if teacher:
            object = {
                'id': user.id,
                'name': user.name,
                'surname': user.surname,
                'username': user.username,
                'father_name': user.father_name,
                'password': password,
                'balance': teacher.id,
                'role': 'teacher',
                'birth_date': user.birth_date.isoformat() if user.birth_date else None,
                'phone_number': user.phone,
                'groups': [{
                    'name': group.name,
                    'id': group.id,
                    'subject': group.subject,
                    'teacher_salary': group.teacher_salary,
                    'price': group.price
                } for group in teacher.group_set.all()]
            }
            self.send_data(object, 'http://192.168.1.17:5001/api/turon_user')
            return object

    def validate(self, attrs):

        username = attrs.get('username')
        password = attrs.get('password')
        user = CustomUser.objects.get(username=username)
        self.user_send(user.id, password)
        if user.password.startswith('sha256$'):
            if check_password_hash(user.password, password):
                new_password = make_password(password)
                user.password = new_password
                user.save()
                data = super().validate(attrs)
                refresh = self.get_token(self.user)
                data['refresh'] = str(refresh)
                data['access'] = str(refresh.access_token)

                return data
            else:
                raise AuthenticationFailed("No active account found with the given credentials")
        elif user.password.startswith('pbkdf2:sha256'):
            if check_password(password, user.password):
                new_password = make_password(password)
                user.password = new_password
                user.save()
                data = super().validate(attrs)
                refresh = self.get_token(self.user)
                data['refresh'] = str(refresh)
                data['access'] = str(refresh.access_token)

                return data
            else:
                raise AuthenticationFailed("No active account found with the given credentials")
        else:
            data = super().validate(attrs)
            refresh = self.get_token(self.user)
            data['refresh'] = str(refresh)
            data['access'] = str(refresh.access_token)

            return data


class GroupSeriliazers(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class Employeers(serializers.ModelSerializer):
    user = UserSerializerRead(read_only=True)
    group = GroupSeriliazers(read_only=True)

    class Meta:
        model = CustomAutoGroup
        fields = '__all__'


class UserSalarySerializersRead(serializers.ModelSerializer):
    user = UserSerializerRead(read_only=True)
    branch = BranchSerializer(read_only=True)
    # user_salary = UserSalarySerializers(read_only=True)
    payment_types = PaymentTypesSerializers(read_only=True)

    class Meta:
        model = UserSalary
        fields = '__all__'


class CustomUserSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )
    profile_photo = serializers.ImageField(use_url=True, required=False, allow_null=True)
    location_id = serializers.CharField(source='branch_id')

    class Meta:
        model = CustomUser
        fields = ('username', 'surname', 'name', 'id', 'groups', 'profile_photo', 'location_id')
