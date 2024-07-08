# from django.contrib.auth.models import User

from rest_framework import serializers

from user.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'surname', 'username', 'father_name', 'password', 'birth_date',
                  'email',
                  'phone', 'age', 'profile_img', 'observer', 'comment', 'registered_date', 'branch','language']

        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            name=validated_data.get('name', ''),
            surname=validated_data.get('surname', ''),
            father_name=validated_data.get('father_name', ''),
            birth_date=validated_data.get('birth_date'),
            phone=validated_data.get('phone', ''),
            age=validated_data.get('age', ''),
            profile_img=validated_data.get('profile_img', ''),
            observer=validated_data.get('observer', False),
            comment=validated_data.get('comment', ''),
            branch_id=validated_data.get('branch'),
            language_id=validated_data.get('language'),

        )
        return user

    def update(self, instance, validated_data):
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
        instance.save()
        return instance
