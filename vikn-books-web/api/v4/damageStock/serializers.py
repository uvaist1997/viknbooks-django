from rest_framework import serializers
from brands.models import DamageStockMaster, DamageStockDetails




class DamageStockMasterRestSerializer(serializers.ModelSerializer):

    DamageStockDetails = serializers.SerializerMethodField()

    class Meta:
        model = DamageStockMaster
        fields = ('id','DamageStockMasterID','BranchID','VoucherNo','Date','WarehouseID','Action','Notes','TotalQty','GrandTotal','IsActive','CreatedDate','UpdatedDate','CreatedUserID','DamageStockDetails')


    def get_DamageStockDetails(self, instances):
        CompanyID = self.context.get("CompanyID")

        stock_details = DamageStockDetails.objects.filter(DamageStockMasterID=instances.DamageStockMasterID,BranchID=instances.BranchID,CompanyID=CompanyID)
        serialized = DamageStockDetailsRestSerializer(stock_details,many=True,)

        return serialized.data 


class DamageStockDetailsRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = DamageStockDetails
        fields = ('id','DamageStockDetailsID','BranchID','DamageStockMasterID','ProductID','Qty','PriceListID','Action','Rate','Amount')

