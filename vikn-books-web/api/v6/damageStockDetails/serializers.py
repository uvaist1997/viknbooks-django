from rest_framework import serializers
from brands.models import DamageStockDetails, DamageStockDetailsDummy


class DamageStockDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = DamageStockDetails
        fields = ('id','BranchID','ProductID','Qty','PriceListID','Rate','Amount')


class DamageStockDetailsRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = DamageStockDetails
        fields = ('id','DamageStockDetailsID','BranchID','DamageStockMasterID','ProductID','Qty','PriceListID','Action','Rate','Amount')



class DamageStockDetailsDummySerializer(serializers.ModelSerializer):

    Qty = serializers.SerializerMethodField()

    class Meta:
        model = DamageStockDetailsDummy
        fields = ('id','BranchID','DamageStockMasterID','ProductID','Qty','PriceListID','Rate','Amount','detailID')


    def get_Qty(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))


        Qty = instances.Qty

        Qty = round(Qty,PriceRounding)

        return str(Qty)

