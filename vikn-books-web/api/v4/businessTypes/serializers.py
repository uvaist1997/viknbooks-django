from rest_framework import serializers
from brands.models import BusinessType


class BusinessTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessType
        fields = ('id','Name')