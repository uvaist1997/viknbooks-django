from rest_framework import serializers

from brands.models import Warehouse


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ("id", "BranchID", "WarehouseName", "Notes", "CreatedUserID")


class WarehouseRestSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Warehouse
        fields = (
            "id",
            "name",
            "WarehouseID",
            "BranchID",
            "WarehouseName",
            "Notes",
            "CreatedUserID",
            "CreatedDate",
            "UpdatedDate",
            "Action",
        )

    def get_name(self, instance):
        name = instance.WarehouseName
        return name
