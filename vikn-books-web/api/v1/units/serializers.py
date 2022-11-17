from rest_framework import serializers
from brands.models import Unit
from rest_framework.fields import CurrentUserDefault


class UnitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Unit
        fields = ('id','BranchID','UnitName','Notes')


class UnitRestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ('id','UnitID','BranchID','UnitName','Notes','CreatedUserID','CreatedDate','UpdatedDate','Action')


class ListSerializer(serializers.Serializer):

    BranchID = serializers.IntegerField()

