from rest_framework import serializers
from brands.models import StockAdjustmentDetails, StockAdjustmentDetailsDummy


class StockAdjustmentDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockAdjustmentDetails
        fields = ('id','BranchID','StockAdjustmentMasterID','ProductID','PriceListID','ActualStock','PhysicalStock','Difference')


class StockAdjustmentDetailsRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockAdjustmentDetails
        fields = ('id','StockAdjustmentDetailsID','BranchID','Action','StockAdjustmentMasterID','ProductID','PriceListID','ActualStock',
        	'PhysicalStock','Difference')



class StockAdjustmentDetailsDummySerializer(serializers.ModelSerializer):

    class Meta:
        model = StockAdjustmentDetailsDummy
        fields = ('id','BranchID','StockAdjustmentMasterID','ProductID','PriceListID','ActualStock','PhysicalStock','Difference','detailID',)

