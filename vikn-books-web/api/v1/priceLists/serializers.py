from rest_framework import serializers
from brands.models import PriceList, Product, Unit


class PriceListSerializer(serializers.ModelSerializer):

    class Meta:
        model = PriceList
        fields = ('id', 'BranchID', 'ProductID', 'UnitName', 'SalesPrice', 'PurchasePrice', 'MultiFactor', 'Barcode', 'AutoBarcode', 'SalesPrice1',
                  'SalesPrice2', 'SalesPrice3', 'CreatedDate', 'CreatedUserID', 'DefaultUnit', 'UnitInSales', 'UnitInPurchase', 'UnitInReports',)


class PriceListRestSerializer(serializers.ModelSerializer):
    SalesPrice = serializers.SerializerMethodField()
    SalesPrice1 = serializers.SerializerMethodField()
    SalesPrice2 = serializers.SerializerMethodField()
    SalesPrice3 = serializers.SerializerMethodField()
    PurchasePrice = serializers.SerializerMethodField()
    MRP = serializers.SerializerMethodField()
    MultiFactor = serializers.SerializerMethodField()
    detailID = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()

    class Meta:
        model = PriceList
        fields = ('id', 'PriceListID', 'BranchID', 'MRP', 'ProductID', 'UnitID', 'UnitName', 'SalesPrice', 'PurchasePrice', 'MultiFactor', 'Barcode', 'AutoBarcode', 'SalesPrice1', 'SalesPrice2', 'SalesPrice3', 'Action', 'CreatedDate', 'CreatedUserID', 'DefaultUnit', 'UnitInSales',
                  'UnitInPurchase', 'UnitInReports', 'detailID')

    def get_SalesPrice(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        SalesPrice = instances.SalesPrice

        SalesPrice = round(SalesPrice, PriceRounding)

        return str(SalesPrice)

    def get_detailID(self, instances):

        detailID = 0

        return detailID

    def get_UnitName(self, instances):
        CompanyID = self.context.get("CompanyID")

        UnitID = instances.UnitID
        BranchID = instances.BranchID
        UnitName = ""
        if Unit.objects.filter(CompanyID=CompanyID, UnitID=UnitID, BranchID=BranchID).exists():
            UnitName = Unit.objects.get(
                CompanyID=CompanyID, UnitID=UnitID, BranchID=BranchID).UnitName

        return UnitName

    def get_SalesPrice1(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        SalesPrice1 = instances.SalesPrice1

        SalesPrice1 = round(SalesPrice1, PriceRounding)

        return str(SalesPrice1)

    def get_SalesPrice2(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        SalesPrice2 = instances.SalesPrice2

        SalesPrice2 = round(SalesPrice2, PriceRounding)

        return str(SalesPrice2)

    def get_SalesPrice3(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        SalesPrice3 = instances.SalesPrice3

        SalesPrice3 = round(SalesPrice3, PriceRounding)

        return str(SalesPrice3)

    def get_MRP(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        MRP = instances.MRP

        MRP = round(MRP, PriceRounding)

        return str(MRP)

    def get_PurchasePrice(self, instances):

        PriceRounding = self.context.get("PriceRounding")
        PurchasePrice = instances.PurchasePrice

        PurchasePrice = round(PurchasePrice, PriceRounding)

        return str(PurchasePrice)

    def get_MultiFactor(self, instances):

        PriceRounding = self.context.get("PriceRounding")
        MultiFactor = instances.MultiFactor

        MultiFactor = round(MultiFactor, PriceRounding)

        return str(MultiFactor)


class ListSerializer(serializers.Serializer):

    BranchID = serializers.IntegerField()
    ProductID = serializers.IntegerField()
