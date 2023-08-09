from rest_framework import serializers

from user_auth.models import UserProfile


class UserPhoneSerializer(serializers.Serializer):
    phone_number = serializers.CharField()


class UserAuthCodeSerializer(serializers.Serializer):
    auth_code = serializers.CharField()


class UserProfileViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class ActivateInviteCodeSerializer(serializers.Serializer):
    invite_code = serializers.CharField()
