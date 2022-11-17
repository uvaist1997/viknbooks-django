from rest_framework import serializers
from brands.models import State, Country, UQCTable
from rest_framework.fields import CurrentUserDefault


class StateSerializer(serializers.ModelSerializer):

    class Meta:
        model = State
        fields = ('id','Name','State_Code','State_Type','Country')


class StateRestSerializer(serializers.ModelSerializer):
    Country_Name = serializers.SerializerMethodField()
    CountryCode = serializers.SerializerMethodField()

    class Meta:
        model = State
        fields = ('id','Name','State_Code','State_Type','Country','Country_Name','CountryCode')

    def get_Country_Name(self, instance):
        Country_Name = instance.Country.Country_Name
        return Country_Name

    def get_CountryCode(self, instance):
        CountryCode = instance.Country.CountryCode
        return CountryCode


class ListSerializer(serializers.Serializer):

    BranchID = serializers.IntegerField()


class UQCSerializer(serializers.ModelSerializer):

    class Meta:
        model = UQCTable
        fields = ('id','UQC_Name')

