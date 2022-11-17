from rest_framework import serializers
from brands.models import DamageStockMaster
from brands.models import DamageStockDetails
from api.v5.damageStockDetails.serializers import DamageStockDetailsRestSerializer


class DamageStockMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = DamageStockMaster
        fields = ('id', 'BranchID', 'VoucherNo', 'Date', 'WarehouseID',
                  'Notes', 'TotalQty', 'GrandTotal', 'IsActive')


class DamageStockMasterRestSerializer(serializers.ModelSerializer):

    DamageStockDetails = serializers.SerializerMethodField()

    class Meta:
        model = DamageStockMaster
        fields = ('id', 'DamageStockMasterID', 'BranchID', 'VoucherNo', 'Date', 'WarehouseID', 'Action',
                  'Notes', 'TotalQty', 'GrandTotal', 'IsActive', 'CreatedDate', 'CreatedUserID', 'DamageStockDetails')

    def get_DamageStockDetails(self, instances):
        DataBase = self.context.get("DataBase")

        stock_details = DamageStockDetails.objects.filter(
            DamageStockMasterID=instances.DamageStockMasterID)
        serialized = DamageStockDetailsRestSerializer(
            stock_details, many=True, context={"DataBase": DataBase})

        return serialized.data
