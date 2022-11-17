from rest_framework import serializers
from brands.models import Kitchen


class KitchenSerializer(serializers.ModelSerializer):

    class Meta:
        model = Kitchen
        fields = ('id','BranchID','KitchenName','PrinterName','IsActive','Notes')


class KitchenRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Kitchen
        fields = ('id','KitchenID','BranchID','KitchenName','PrinterName','IsActive','Notes','Action','CreatedUserID','CreatedDate','UpdatedDate')
