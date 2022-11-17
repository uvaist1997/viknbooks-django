from rest_framework import serializers
from brands.models import UserType
from rest_framework.fields import CurrentUserDefault


class UserTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserType
        fields = ('id', 'BranchID', 'UserTypeName', 'Notes',
                  "UserTypeName", "BranchID", "Notes", "Action", "CreatedUserID", "CreatedDate", "UpdatedDate")


class UserTypeRestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserType
        fields = ('id', 'BranchID', 'UserTypeName', 'Notes','ID',
                  "UserTypeName", "BranchID", "Notes", "Action", "CreatedUserID", "CreatedDate", "UpdatedDate")


class ListSerializer(serializers.Serializer):
    BranchID = serializers.IntegerField()
