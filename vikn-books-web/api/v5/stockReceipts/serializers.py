from rest_framework import serializers
from brands.models import StockReceiptMaster_ID, StockReceiptDetails


class StockReceiptMaster_IDSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockReceiptMaster_ID
        fields = ('id','BranchID','VoucherNo','InvoiceNo','Date','Notes','WarehouseFromID',
            'WarehouseToID','IsActive','CreatedDate','CreatedUserID')


class StockReceiptMaster_IDRestSerializer(serializers.ModelSerializer):

    StockReceiptDetails = serializers.SerializerMethodField()

    class Meta:
        model = StockReceiptMaster_ID
        fields = ('id','StockReceiptMasterID','BranchID','Action','VoucherNo','InvoiceNo','Date','Notes',
            'WarehouseFromID','WarehouseToID','IsActive','CreatedDate','CreatedUserID','StockReceiptDetails')



    def get_StockReceiptDetails(self, instances):
        stockReceipt_details = StockReceiptDetails.objects.filter(StockReceiptMasterID=instances.StockReceiptMasterID,BranchID=instances.BranchID)
        serialized = StockReceiptDetailsRestSerializer(stockReceipt_details,many=True,)

        return serialized.data




class StockReceiptDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockReceiptDetails
        fields = ('id','BranchID','ProductID','Qty','PriceListID',
            'Rate','Amount')


class StockReceiptDetailsRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockReceiptDetails
        fields = ('id','StockReceiptDetailsID','BranchID','Action','StockReceiptMasterID','ProductID','Qty','PriceListID',
            'Rate','Amount')
