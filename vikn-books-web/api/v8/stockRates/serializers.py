from rest_framework import serializers
from brands.models import StockPosting


class StockPostingSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockPosting
        fields = ('id','BranchID','Action','Date','VoucherMasterID','ProductID',
        	'BatchID','WareHouseID','QtyIn','QtyOut','Rate','PriceListID','IsActive','CreatedUserID')


class StockPostingRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockPosting
        fields = ('id','StockPostingID','BranchID','Action','Date','VoucherMasterID','ProductID',
        	'BatchID','WareHouseID','QtyIn','QtyOut','Rate','PriceListID','IsActive','CreatedDate','UpdatedDate','CreatedUserID')
