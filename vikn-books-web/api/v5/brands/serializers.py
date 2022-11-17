from rest_framework import serializers
from brands.models import Brand
from rest_framework.fields import CurrentUserDefault


class BrandSerializer(serializers.ModelSerializer):

    class Meta:
        model = Brand
        fields = ('id', 'BranchID', 'BrandName', 'Notes')


class BrandRestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'BrandID', 'BranchID', 'BrandName', 'Notes',
                  'CreatedUserID', 'CreatedDate', 'UpdatedDate', 'Action')


class ListSerializer(serializers.Serializer):

    BranchID = serializers.IntegerField()
