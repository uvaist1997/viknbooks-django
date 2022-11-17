from rest_framework import serializers
from brands.models import OpeningStockMaster


class OpeningStockMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = OpeningStockMaster
        fields = ('id','BranchID','VoucherNo','Date','WarehouseID',
        	'Notes','TotalQty','GrandTotal','IsActive','CreatedDate','CreatedUserID')


class OpeningStockMasterRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = OpeningStockMaster
        fields = ('id','OpeningStockMasterID','BranchID','Action','VoucherNo','Date','WarehouseID',
        	'Notes','TotalQty','GrandTotal','IsActive','CreatedDate','CreatedUserID')
