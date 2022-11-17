from rest_framework import serializers
from brands.models import State, Country
from rest_framework.fields import CurrentUserDefault


class StateSerializer(serializers.ModelSerializer):

    class Meta:
        model = State
        fields = ('id','Name','State_Type','Country')


class StateRestSerializer(serializers.ModelSerializer):
    Country_Name = serializers.SerializerMethodField()

    class Meta:
        model = State
        fields = ('id','Name','State_Type','Country','Country_Name')

    def get_Country_Name(self, instance):
        Country_Name = instance.Country.Country_Name
        return Country_Name


class ListSerializer(serializers.Serializer):

    BranchID = serializers.IntegerField()

