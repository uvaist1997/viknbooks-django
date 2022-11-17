from rest_framework import serializers
from brands.models import Brand
from rest_framework.fields import CurrentUserDefault


class BrandSerializer(serializers.ModelSerializer):

    class Meta:
        model = Brand
        fields = ('id', 'BranchID', 'BrandName', 'Notes')


class BrandRestSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ('id', 'name', 'BrandID', 'BranchID', 'BrandName', 'Notes',
                  'CreatedUserID', 'CreatedDate', 'UpdatedDate', 'Action')

    def get_name(self, instances):
        name = instances.BrandName
        return name


class ListSerializer(serializers.Serializer):

    BranchID = serializers.IntegerField()
