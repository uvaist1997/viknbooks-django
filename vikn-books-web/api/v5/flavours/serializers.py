from rest_framework import serializers
from brands.models import Flavours


class FlavoursSerializer(serializers.ModelSerializer):

    class Meta:
        model = Flavours
        fields = ('id','BranchID','FlavourName','BgColor','IsActive')


class FlavoursRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Flavours
        fields = ('id','FlavourID','BranchID','FlavourName','BgColor','IsActive','Action')
