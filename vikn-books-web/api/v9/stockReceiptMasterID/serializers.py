from rest_framework import serializers
from brands.models import StockReceiptMaster_ID


class StockReceiptMaster_IDSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockReceiptMaster_ID
        fields = ('id','BranchID','VoucherNo','InvoiceNo','Date','Notes','WarehouseFromID',
        	'WarehouseToID','IsActive','CreatedDate','CreatedUserID')


class StockReceiptMaster_IDRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockReceiptMaster_ID
        fields = ('id','StockReceiptMasterID','BranchID','Action','VoucherNo','InvoiceNo','Date','Notes',
        	'WarehouseFromID','WarehouseToID','IsActive','CreatedDate','CreatedUserID')
