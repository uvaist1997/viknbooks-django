from rest_framework import serializers
from brands import models as table
# from api.v8.priceLists.serializers import PriceListRestSerializer
from api.v8.companySettings.serializers import CompanySettingsRestSerializer



class PriceListSerializer(serializers.ModelSerializer):
   
    UnitName = serializers.SerializerMethodField()

    class Meta:
        model = table.PriceList
        fields = ('id','PriceListID','BranchID','MRP','ProductID','UnitID','UnitName','SalesPrice','PurchasePrice','MultiFactor','Barcode','AutoBarcode')


    def get_UnitName(self, instances):
        CompanyID = self.context.get("CompanyID")

        UnitID = instances.UnitID
        BranchID = instances.BranchID
        UnitName = ""
        if table.Unit.objects.filter(CompanyID=CompanyID,UnitID=UnitID,BranchID=BranchID).exists():
            UnitName = table.Unit.objects.get(CompanyID=CompanyID,UnitID=UnitID,BranchID=BranchID).UnitName

        return UnitName



class POS_ProductList_Serializer(serializers.ModelSerializer):
    UnitList = serializers.SerializerMethodField()
    GST_Tax = serializers.SerializerMethodField()
    VAT_Tax = serializers.SerializerMethodField()

    class Meta:
        model = table.Product
        fields = ('id','ProductID','ProductName','ProductCode','UnitList','GST_Tax','VAT_Tax')

    def get_UnitList(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID
        UnitList = table.PriceList.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)
        serialized = PriceListSerializer(UnitList, many=True, context={
                                             "CompanyID": CompanyID, "PriceRounding": PriceRounding})
        return serialized.data


    def get_GST_Tax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.GST
        BranchID = instance.BranchID
        if table.TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = table.TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
            SalesTax = tax.SalesTax
            return str(SalesTax)
        else:
            return "0"

    def get_VAT_Tax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.VatID
        BranchID = instance.BranchID
        if table.TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = table.TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
            SalesTax = tax.SalesTax
            return str(SalesTax)
        else:
            return "0"


    


