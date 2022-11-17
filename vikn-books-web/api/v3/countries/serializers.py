from rest_framework import serializers
from brands.models import Country, State
from rest_framework.fields import CurrentUserDefault


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = ('id','CountryCode','Country_Name','Currency_Name','Change','Symbol','FractionalUnits','CurrencySymbolUnicode','ISD_Code','Tax_Type',)


class CountryRestSerializer(serializers.ModelSerializer):
    # state = serializers.SerializerMethodField()
    class Meta:
        model = Country
        fields = ('id','CountryCode','Country_Name','Currency_Name','Change','Symbol','FractionalUnits','CurrencySymbolUnicode','CurrencySymbolUnicode','ISD_Code','Tax_Type','Flag')

    # def get_state(self, instance):
    #     state = State.objects.filter(Country=instance)
    #     print(state)
    #     print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    #     return 'state'

class ListSerializer(serializers.Serializer):

    BranchID = serializers.IntegerField()

