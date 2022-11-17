from rest_framework import serializers
from brands.models import StockTransferMaster_ID


class StockTransferMaster_IDSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockTransferMaster_ID
        fields = ('id','BranchID','VoucherNo','InvoiceNo','Date','Notes','TransferredByID','WarehouseFromID',
        	'WarehouseToID','TotalQty','GrandTotal','IsActive','CreatedDate','CreatedUserID')


class StockTransferMaster_IDRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockTransferMaster_ID
        fields = ('id','StockTransferMasterID','BranchID','Action','VoucherNo','InvoiceNo','Date','Notes','TransferredByID',
        	'WarehouseFromID','WarehouseToID','TotalQty','GrandTotal','IsActive','CreatedDate','CreatedUserID')
