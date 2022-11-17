from rest_framework import serializers
from brands.models import StockTransferDetails, StockTransferDetailsDummy


class StockTransferDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockTransferDetails
        fields = ('id','BranchID','StockTransferMasterID','ProductID','Qty','PriceListID',
        	'Rate','Amount')


class StockTransferDetailsRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockTransferDetails
        fields = ('id','StockTransferDetailsID','BranchID','Action','StockTransferMasterID','ProductID','Qty','PriceListID',
        	'Rate','Amount')


class StockTransferDetailsDummySerializer(serializers.ModelSerializer):

    class Meta:
        model = StockTransferDetailsDummy
        fields = ('id','unq_id','StockTransferDetailsID','BranchID','StockTransferMasterID','ProductID','Qty','PriceListID','Rate','Amount','detailID',)
