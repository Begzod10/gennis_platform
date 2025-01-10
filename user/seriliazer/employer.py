from rest_framework import serializers
from rest_framework_simplejwt.authentication import JWTAuthentication

from payments.serializers import PaymentTypesSerializers
from user.models import CustomAutoGroup, UserSalary, UserSalaryList


class EmployerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(required=False)
    phone = serializers.SerializerMethodField(required=False)
    age = serializers.SerializerMethodField(required=False)
    job = serializers.SerializerMethodField(required=False)
    status = serializers.SerializerMethodField(required=False)

    class Meta:
        model = CustomAutoGroup
        fields = ('id', 'name', 'phone', 'age', 'job', 'status')

    def get_name(self, obj):
        return f"{obj.user.name} {obj.user.surname} {obj.user.father_name}"

    def get_phone(self, obj):
        return obj.user.phone

    def get_age(self, obj):
        return obj.user.calculate_age()

    def get_job(self, obj):
        return obj.group.name

    def get_status(self, obj):

        jwt_auth = JWTAuthentication()
        request = self.context['request']
        header = request.META.get('HTTP_AUTHORIZATION')
        if header is not None:
            raw_token = header.split(' ')[1]
            validated_token = jwt_auth.get_validated_token(raw_token)
            user_id = validated_token['user_id']
            if user_id == obj.user.id:
                return False
            else:
                return True


class EmployerSalaryMonths(serializers.ModelSerializer):
    class Meta:
        model = UserSalary
        fields = ['id', 'total_salary', 'taken_salary', 'remaining_salary', 'date', 'permission']


class UserForOneMonthListSerializer(serializers.ModelSerializer):
    payment_types = PaymentTypesSerializers()

    class Meta:
        model = UserSalaryList
        fields = ['id', 'payment_types', 'comment', 'deleted', 'salary', 'date']
