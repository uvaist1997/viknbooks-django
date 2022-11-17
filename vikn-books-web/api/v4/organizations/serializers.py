from rest_framework import serializers
from django.contrib.auth.models import User
from brands.models import CompanySettings
import datetime


class OrganizationSettingsSerializer(serializers.Serializer):
    # ExpiryDate = serializers.DateField(format="%d-%m-%Y", input_formats=['%d-%m-%Y', 'iso-8601'])
    ExpiryDate = serializers.DateField(format="%Y-%m-%d", required=False)
    NoOfUsers = serializers.IntegerField()
    Customer = serializers.CharField()
    Organization = serializers.CharField()


# class OrganizationUserListSerializer(serializers.Serializer):
#     # ExpiryDate = serializers.DateField(format="%d-%m-%Y", input_formats=['%d-%m-%Y', 'iso-8601'])
#     ExpiryDate = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", required=False, read_only=True)
#     NoOfUsers = serializers.IntegerField()
#     Customer = serializers.CharField()
#     Organization = serializers.CharField()

class OrganizationSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    RegisteredDate = serializers.SerializerMethodField()
    Customerid = serializers.SerializerMethodField()


    class Meta:
        model = CompanySettings
        fields = ('id','Action','Customerid','CompanyName','State','Country','Phone','Mobile','Email','Website','ExpiryDate','NoOfUsers','username','status','CreatedDate','RegisteredDate')

    def get_RegisteredDate(self, instance):
        RegisteredDate = instance.CreatedDate.date()
        return RegisteredDate


    def get_Customerid(self, instance):
        Customerid = (instance.owner.id)
        return Customerid


    def get_username(self, instance):
        username = instance.owner.username
        return username


    def get_status(self, instance):
        status = ''
        if instance.is_deleted == True:
            status = 'InActive'
        else:
            status = 'Active'
        return status

class OrganizationUserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id','username',)

class OrganizationListSerializer(serializers.ModelSerializer):

    class Meta:
        model = CompanySettings
        fields = ('id','CompanyName',)