from user.models import CustomUser
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



class TransferUserSerializer(serializers.ModelSerializer):
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    language = OldIdRelatedField(queryset=Language.objects.all(), required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = '__all__'


class TransferUserJobs(serializers.Serializer):
    user_id = serializers.SlugRelatedField(
        queryset=CustomUser.objects.all(), slug_field='turon_old_id'
    )
    group_id = serializers.SlugRelatedField(
        queryset=Group.objects.all(), slug_field='name'
    )

    def create(self, validated_data):
        user = validated_data['user_id']
        group = validated_data['group_id']
        user.groups.add(group)
        return user
