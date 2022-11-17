from rest_framework import serializers
from brands.models import StockReceiptDetails, StockReceiptDetailsDummy


class StockReceiptDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockReceiptDetails
        fields = ('id','BranchID','StockReceiptMasterID','ProductID','Qty','PriceListID',
        	'Rate','Amount')


class StockReceiptDetailsRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockReceiptDetails
        fields = ('id','StockReceiptDetailsID','BranchID','Action','StockReceiptMasterID','ProductID','Qty','PriceListID',
        	'Rate','Amount')



class StockReceiptDetailsDummySerializer(serializers.ModelSerializer):

    class Meta:
        model = StockReceiptDetailsDummy
        fields = ('id','BranchID','StockReceiptMasterID','ProductID','Qty','PriceListID','Rate','Amount','detailID',)