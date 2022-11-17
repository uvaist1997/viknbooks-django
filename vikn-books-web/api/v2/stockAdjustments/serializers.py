from rest_framework import serializers
from brands.models import StockAdjustmentMaster, StockAdjustmentDetails



class StockAdjustmentMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockAdjustmentMaster
        fields = ('id','BranchID','VoucherNo','InvoiceNo','Date','WarehouseID','Notes',
            'GroupWise','ProductGroupID','IsActive','CreatedDate','CreatedUserID')


class StockAdjustmentMasterRestSerializer(serializers.ModelSerializer):

    StockAdjustmentDetails = serializers.SerializerMethodField()

    class Meta:
        model = StockAdjustmentMaster
        fields = ('id','StockAdjustmentMasterID','BranchID','Action','VoucherNo','InvoiceNo',
            'Date','WarehouseID','Notes','GroupWise','ProductGroupID','IsActive','CreatedDate','CreatedUserID','StockAdjustmentDetails')



    def get_StockAdjustmentDetails(self, instances):
        stockAdjustment_details = StockAdjustmentDetails.objects.filter(StockAdjustmentMasterID=instances.StockAdjustmentMasterID,BranchID=instances.BranchID)
        serialized = StockAdjustmentDetailsRestSerializer(stockAdjustment_details,many=True,)

        return serialized.data 



class StockAdjustmentDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockAdjustmentDetails
        fields = ('id','BranchID','ProductID','PriceListID','ActualStock','PhysicalStock','Difference')


class StockAdjustmentDetailsRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockAdjustmentDetails
        fields = ('id','StockAdjustmentDetailsID','BranchID','Action','StockAdjustmentMasterID','ProductID','PriceListID','ActualStock',
            'PhysicalStock','Difference')
