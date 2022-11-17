from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from six import text_type
from api.v7.general import functions


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(UserTokenObtainPairSerializer, cls).get_token(user)
        return token

    def validate(cls, attrs):
        data = super(UserTokenObtainPairSerializer, cls).validate(attrs)

        refresh = cls.get_token(cls.user)

        data['refresh'] = text_type(refresh)
        data['access'] = text_type(refresh.access_token)
        data['user_id'] = cls.user.id

        current_role = functions.get_current_role(cls)
        data['role'] = current_role

        return data
