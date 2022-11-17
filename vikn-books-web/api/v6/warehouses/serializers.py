from rest_framework import serializers
from brands.models import Warehouse


class WarehouseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Warehouse
        fields = ('id','BranchID','WarehouseName','Notes','CreatedUserID')


class WarehouseRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Warehouse
        fields = ('id','WarehouseID','BranchID','WarehouseName','Notes','CreatedUserID','CreatedDate','UpdatedDate','Action')
