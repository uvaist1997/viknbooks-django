from rest_framework import serializers
from brands import models as table
# from api.v8.priceLists.serializers import PriceListRestSerializer
from api.v8.companySettings.serializers import CompanySettingsRestSerializer


class PriceListSerializer(serializers.ModelSerializer):

    UnitName = serializers.SerializerMethodField()

    class Meta:
        model = table.PriceList
        fields = ('id', 'PriceListID', 'BranchID', 'MRP', 'ProductID', 'UnitID', 'UnitName',
                  'SalesPrice', 'PurchasePrice', 'MultiFactor', 'Barcode', 'AutoBarcode')

    def get_UnitName(self, instances):
        CompanyID = self.context.get("CompanyID")

        UnitID = instances.UnitID
        BranchID = instances.BranchID
        UnitName = ""
        if table.Unit.objects.filter(CompanyID=CompanyID, UnitID=UnitID, BranchID=BranchID).exists():
            UnitName = table.Unit.objects.get(
                CompanyID=CompanyID, UnitID=UnitID, BranchID=BranchID).UnitName

        return UnitName


class POS_ProductList_Serializer(serializers.ModelSerializer):
    UnitList = serializers.SerializerMethodField()
    GST_Tax = serializers.SerializerMethodField()
    VAT_Tax = serializers.SerializerMethodField()

    class Meta:
        model = table.Product
        fields = ('id', 'ProductID', 'ProductName', 'ProductCode',
                  'UnitList', 'GST_Tax', 'VAT_Tax', 'VatID', 'GST', 'is_inclusive')

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


class POS_Sales_Serializer(serializers.ModelSerializer):
    LedgerName = serializers.SerializerMethodField()
    SubTotal = serializers.SerializerMethodField()
    TenderCash = serializers.SerializerMethodField()
    ItemDetails = serializers.SerializerMethodField()

    class Meta:
        model = table.SalesMaster
        fields = ('id', 'LedgerID', 'LedgerName', 'CustomerName', 'SubTotal', 'TotalDiscount', 'TotalTax', 'GrandTotal', 'Balance',
                  'TenderCash', 'BillDiscPercent', 'TaxType', 'CashReceived', 'BankAmount', 'CardTypeID', 'CardNumber', 'ItemDetails',
                  'SGSTAmount', 'CGSTAmount', 'IGSTAmount')

    def get_LedgerName(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        LedgerID = instance.LedgerID
        BranchID = instance.BranchID
        LedgerName = ""
        if table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID).exists():
            LedgerName = table.AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID).LedgerName
        return LedgerName

    def get_SubTotal(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        SubTotal = instance.TotalGrossAmt
        return SubTotal

    def get_TenderCash(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TenderCash = instance.CashReceived
        return TenderCash

    def get_ItemDetails(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        BranchID = instance.BranchID
        SalesMasterID = instance.SalesMasterID
        ItemDetails = []
        if table.SalesDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SalesMasterID=SalesMasterID).exists():
            details = table.SalesDetails.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, SalesMasterID=SalesMasterID)
            serialized = Pos_SalesDetailSerializer(details, many=True, context={
                "CompanyID": CompanyID, "PriceRounding": PriceRounding})
            ItemDetails = serialized.data
        return ItemDetails


class Pos_SalesDetailSerializer(serializers.ModelSerializer):
    ProductName = serializers.SerializerMethodField()
    ProductCode = serializers.SerializerMethodField()
    UnitList = serializers.SerializerMethodField()

    class Meta:
        model = table.SalesDetails
        fields = ('id', 'SalesDetailsID', 'Qty', 'ProductID', 'ProductName', 'UnitPrice', 'InclusivePrice', 'ProductCode', 'UnitList',
                  'PriceListID', 'DiscountPerc', 'DiscountAmount', 'GrossAmount', 'TaxableAmount', 'VATPerc', 'VATAmount', 'SGSTPerc', 'SGSTAmount', 'CGSTPerc',
                  'CGSTAmount', 'IGSTPerc', 'IGSTAmount', 'NetAmount')

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

    def get_ProductName(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID
        ProductName = ""
        if table.Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
            ProductName = table.Product.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).ProductName
        return ProductName

    def get_ProductCode(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID
        ProductCode = ""
        if table.Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
            ProductCode = table.Product.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).ProductCode
        return ProductCode


class POS_BranchList_Serializer(serializers.ModelSerializer):
    TaxNo = serializers.SerializerMethodField()

    class Meta:
        model = table.Branch
        fields = ('id', 'BranchID', 'BranchName',
                  'Building', 'City', 'Phone', 'TaxNo', 'DisplayName')

    def get_TaxNo(self, instances):
        VATNumber = instances.VATNumber
        GSTNumber = instances.GSTNumber
        is_gst = instances.is_gst
        is_vat = instances.is_vat
        TaxNo = ""
        if is_gst == True and GSTNumber:
            TaxNo = GSTNumber
        if is_vat == True and VATNumber:
            TaxNo = VATNumber
        return TaxNo
