from rest_framework import serializers
from brands.models import OpeningStockMaster, OpeningStockDetails, Warehouse, Product, PriceList, Unit


class OpeningStockMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = OpeningStockMaster
        fields = ('id','BranchID','VoucherNo','Date','WarehouseID',
            'Notes','TotalQty','GrandTotal','IsActive','CreatedDate','CreatedUserID')


class OpeningStockMasterRestSerializer(serializers.ModelSerializer):

    OpeningStockDetails = serializers.SerializerMethodField()
    WareHouseName = serializers.SerializerMethodField()
    TotalQty = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()

    class Meta:
        model = OpeningStockMaster
        fields = ('id','OpeningStockMasterID','BranchID','Action','VoucherNo','Date','WarehouseID','WareHouseName',
            'Notes','TotalQty','GrandTotal','IsActive','CreatedDate','UpdatedDate','CreatedUserID','OpeningStockDetails')


    def get_OpeningStockDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        opening_stock_details = OpeningStockDetails.objects.filter(CompanyID=CompanyID,OpeningStockMasterID=instances.OpeningStockMasterID,BranchID=instances.BranchID)
        serialized = OpeningStockDetailsRestSerializer(opening_stock_details,many=True,context = {"PriceRounding" : PriceRounding,
            "CompanyID" : CompanyID})

        return serialized.data


    def get_TotalQty(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalQty = instances.TotalQty
        TotalQty = round(TotalQty,PriceRounding)
        return float(TotalQty)


    def get_GrandTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        GrandTotal = instances.GrandTotal
        GrandTotal = round(GrandTotal,PriceRounding)
        return float(GrandTotal)


    def get_WareHouseName(self, instance):

        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        WarehouseID = instance.WarehouseID
        WarehouseInstance = Warehouse.objects.get(CompanyID=CompanyID,BranchID=BranchID,WarehouseID=WarehouseID)

        WareHouseName = WarehouseInstance.WarehouseName

        return str(WareHouseName)


class OpeningStockDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = OpeningStockDetails
        fields = ('id','BranchID','ProductID','Qty','PriceListID',
            'Rate','Amount')


class OpeningStockDetailsRestSerializer(serializers.ModelSerializer):

    Qty = serializers.SerializerMethodField()
    Rate = serializers.SerializerMethodField()
    Amount = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()
    ProductName = serializers.SerializerMethodField()
    unq_id = serializers.SerializerMethodField()
    detailID = serializers.SerializerMethodField()

    class Meta:
        model = OpeningStockDetails
        fields = ('id','OpeningStockDetailsID','Action','BranchID','OpeningStockMasterID','ProductID','Qty','PriceListID',
            'UnitName','ProductName','Rate','Amount','unq_id','detailID')


    def get_Qty(self, opening_stock_details):
        PriceRounding = self.context.get("PriceRounding")
        Qty = opening_stock_details.Qty
        Qty = round(Qty,PriceRounding)
        return float(Qty)


    def get_Rate(self, opening_stock_details):
        PriceRounding = self.context.get("PriceRounding")
        Rate = opening_stock_details.Rate
        Rate = round(Rate,PriceRounding)
        return float(Rate)


    def get_Amount(self, opening_stock_details):
        PriceRounding = self.context.get("PriceRounding")
        Amount = opening_stock_details.Amount
        Amount = round(Amount,PriceRounding)
        return float(Amount)


    def get_ProductName(self, opening_stock_details):

        CompanyID = self.context.get("CompanyID")

        ProductID = opening_stock_details.ProductID
        BranchID = opening_stock_details.BranchID

        if Product.objects.filter(CompanyID=CompanyID,ProductID=ProductID,BranchID=BranchID).exists():
            product = Product.objects.get(CompanyID=CompanyID,ProductID=ProductID,BranchID=BranchID)
            ProductName = product.ProductName
        else:
            ProductName = ""

        return ProductName


    def get_UnitName(self, opening_stock_details):

        CompanyID = self.context.get("CompanyID")

        PriceListID = opening_stock_details.PriceListID
        BranchID = opening_stock_details.BranchID

        if PriceList.objects.filter(CompanyID=CompanyID,PriceListID=PriceListID,BranchID=BranchID).exists():
            UnitID = PriceList.objects.get(CompanyID=CompanyID,PriceListID=PriceListID,BranchID=BranchID).UnitID
            UnitName = Unit.objects.get(CompanyID=CompanyID,BranchID=BranchID,UnitID=UnitID).UnitName
        else:
            UnitName = ""

        return UnitName


    def get_unq_id(self, opening_stock_details):

        CompanyID = self.context.get("CompanyID")

        unq_id = opening_stock_details.id

        return unq_id


    def get_detailID(self, opening_stock_details):


        detailID = 0

        return detailID