from rest_framework import serializers
from brands.models import StockAdjustmentMaster


class StockAdjustmentMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockAdjustmentMaster
        fields = ('id','BranchID','VoucherNo','InvoiceNo','Date','WarehouseID','Notes',
        	'GroupWise','ProductGroupID','IsActive','CreatedDate','CreatedUserID')


class StockAdjustmentMasterRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockAdjustmentMaster
        fields = ('id','StockAdjustmentMasterID','BranchID','Action','VoucherNo','InvoiceNo',
            'Date','WarehouseID','Notes','GroupWise','ProductGroupID','IsActive','CreatedDate','CreatedUserID')
