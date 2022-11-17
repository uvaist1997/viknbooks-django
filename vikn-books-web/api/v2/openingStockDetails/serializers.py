from rest_framework import serializers
from brands.models import OpeningStockDetails, OpeningStockDetailsDummy, Product


class OpeningStockDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = OpeningStockDetails
        fields = ('id','BranchID','OpeningStockMasterID','ProductID','Qty','PriceListID',
        	'Rate','Amount')


class OpeningStockDetailsRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = OpeningStockDetails
        fields = ('id','OpeningStockDetailsID','Action','BranchID','OpeningStockMasterID','ProductID','Qty','PriceListID',
        	'Rate','Amount',)



class OpeningStockDetailsDummySerializer(serializers.ModelSerializer):

    Qty = serializers.SerializerMethodField()
    ProductName = serializers.SerializerMethodField()
    Rate = serializers.SerializerMethodField()
    Amount = serializers.SerializerMethodField()

    class Meta:
        model = OpeningStockDetailsDummy
        fields = ('id','unq_id','BranchID','OpeningStockMasterID','ProductID','ProductName','Qty','PriceListID','Rate','Amount','detailID')


    def get_Qty(self, instances):

        Qty = instances.Qty
        Qty = round(Qty,2)
        return str(Qty)

    def get_Rate(self, instances):

        Rate = instances.Rate
        Rate = round(Rate,2)
        return str(Rate)

    def get_Amount(self, instances):

        Amount = instances.Amount
        Amount = round(Amount,2)
        return str(Amount)

    def get_ProductName(self, instance):

        DataBase = self.context.get("DataBase")
        BranchID = instance.BranchID
        ProductID = instance.ProductID
        product_instance = Product.objects.get(BranchID=BranchID,ProductID=ProductID)

        ProductName = product_instance.ProductName

        return str(ProductName)


class OpeningStockDetailsDeletedDummySerializer(serializers.ModelSerializer):

    class Meta:
        model = OpeningStockDetailsDummy
        fields = ('id','OpeningStockDetailsID','unq_id')