from rest_framework import serializers
from brands import models
from rest_framework.fields import CurrentUserDefault


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Category
        fields = ('Name','Code',)


class CategoryRestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ('id','BranchID','Name','Code','CreatedUserID','CreatedDate','UpdatedDate','Action')



class ListSerializer(serializers.Serializer):

    BranchID = serializers.IntegerField()


class DatabaseSyncTestRestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DatabaseSyncTest
        fields = ('id','CompanyID','BranchID','Name','CreatedUserID','CreatedDate','UpdatedDate','Action','DataSyncID','IsDeleted',)


class DatabaseSyncTestSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.DatabaseSyncTest
        fields = ('Name',)