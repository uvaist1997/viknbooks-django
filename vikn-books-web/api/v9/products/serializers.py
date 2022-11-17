from api.v9.stockPostings.functions import query_get_product_stock
from rest_framework import serializers
from brands.models import Product, ProductBarcode, PriceList, Brand, ProductGroup, TaxCategory, Unit, StockPosting, Batch, GeneralSettings, Warehouse
from api.v9.priceLists.serializers import PriceListRestSerializer, SinglePriceListRestSerializer
from api.v9.workOrder.serializers import Batch_ListSerializer, UnitListSerializer
from main.functions import converted_float, get_BranchList, get_BranchSettings,get_GeneralSettings
from django.db.models import Max, Q, Prefetch, Sum
from api.v9.priceLists.functions import get_LastSalesPrice_PurchasePrice

class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ('id', 'BranchID', 'ProductCode', 'ProductName', 'DisplayName', 'Description', 'ProductGroupID', 'is_Service',
                  'BrandID', 'InventoryType', 'VatID', 'StockMinimum', 'MinimumSalesPrice', 'StockReOrder', 'StockMaximum', 'is_inclusive',
                  'MarginPercent', 'Active', 'IsRawMaterial', 'IsWeighingScale', 'WeighingCalcType', 'PLUNo', 'WarrantyType', 'Warranty',
                  'IsFavourite', 'CreatedDate', 'CreatedUserID', 'IsFinishedProduct', 'IsSales', 'IsPurchase', "GST", "Tax1", "Tax2", "Tax3", "IsKFC", "HSNCode")


class ProductBarcodeListRestSerializer(serializers.ModelSerializer):

    detailID = serializers.SerializerMethodField()

    class Meta:
        model = ProductBarcode
        fields = ('id', 'BranchID', 'CompanyID', 'Barcode', 'detailID')

    def get_detailID(self, instances):
        return 0


class ProductSearchSerializer(serializers.ModelSerializer):

    Stock = serializers.SerializerMethodField()
    PurchasePrice = serializers.SerializerMethodField()
    SalesPrice = serializers.SerializerMethodField()
    Barcode = serializers.SerializerMethodField()
    BatchCode = serializers.SerializerMethodField()
    # Check_positive_Stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'Description', 'ProductID', 'ProductCode', 'Barcode', 'ProductName',
                  'Stock', 'HSNCode', 'PurchasePrice', 'SalesPrice', 'is_inclusive', 'BatchCode', 'BranchID')

    def get_BatchCode(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        BatchCode = 0
        if Batch.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).exists():
            BatchCode = Batch.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).first().BatchCode

        return BatchCode

    def get_Barcode(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            Barcode = priceList.Barcode
            # Barcode = round(Barcode, int(PriceRounding))
        else:
            Barcode = 0
        return Barcode

    def get_PurchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            PurchasePrice = priceList.PurchasePrice
            # PurchasePrice = round(PurchasePrice, int(PriceRounding))
        else:
            PurchasePrice = 0
        return PurchasePrice

    def get_SalesPrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            SalesPrice = priceList.SalesPrice
            # SalesPrice = round(SalesPrice, int(PriceRounding))
        else:
            SalesPrice = 0
        return SalesPrice

    def get_Stock(self, instances):
        CompanyID = self.context.get("CompanyID")
        WarehouseID = self.context.get("WarehouseID")

        try:
            type = self.context.get("type")
        except:
            type = "any"

        try:
            Date = self.context.get("Date")
        except:
            Date = ""

        ProductID = instances.ProductID
        BranchID = instances.BranchID
        Stock = 0
        check_EnableProductBatchWise = False
        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
            check_EnableProductBatchWise = GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
        if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
            if WarehouseID:
                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID).exists():
                    Batch_ins = Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID).order_by('BatchCode').last()
                    batch_pricelistID = Batch_ins.PriceListID
                    batch_MultiFactor = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=batch_pricelistID).MultiFactor
                    total_stockIN = converted_float(Batch_ins.StockIn)
                    total_stockOUT = converted_float(Batch_ins.StockOut)
                    # total_stockIN = converted_float(Batch_ins.StockIn) / converted_float(batch_MultiFactor)
                    # total_stockOUT = converted_float(Batch_ins.StockOut) / converted_float(batch_MultiFactor)
                    # total_stockIN = 0
                    # total_stockOUT = 0
                    # for b in Batch_ins:
                    #     batch_pricelistID = b.PriceListID
                    #     batch_MultiFactor = PriceList.objects.get(
                    #         CompanyID=CompanyID, PriceListID=batch_pricelistID).MultiFactor
                    #     total_stockIN += (converted_float(b.StockIn) /
                    #                       converted_float(batch_MultiFactor))
                    #     total_stockOUT += (converted_float(b.StockOut) /
                    #                        converted_float(batch_MultiFactor))

                    Stock = converted_float(total_stockIN) - converted_float(total_stockOUT)
            else:
                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
                    Batch_ins = Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                    total_stockIN = Batch_ins.aggregate(Sum('StockIn'))
                    total_stockIN = total_stockIN['StockIn__sum']
                    total_stockOUT = Batch_ins.aggregate(Sum('StockOut'))
                    total_stockOUT = total_stockOUT['StockOut__sum']
                    # for b in Batch_ins:
                    #     batch_pricelistID = b.PriceListID
                    #     batch_MultiFactor = PriceList.objects.get(
                    #         CompanyID=CompanyID, PriceListID=batch_pricelistID).MultiFactor
                    #     total_stockIN += (converted_float(b.StockIn))
                    #     total_stockOUT += (converted_float(b.StockOut))

                    Stock = converted_float(total_stockIN) - converted_float(total_stockOUT)
        else:
            if type == "CommonStockCalculation" and Date:
                if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID, Date__lte=Date):
                    stock_ins = StockPosting.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID, Date__lte=Date)
                    total_stockIN = stock_ins.aggregate(Sum('QtyIn'))
                    total_stockIN = total_stockIN['QtyIn__sum']
                    total_stockOUT = stock_ins.aggregate(Sum('QtyOut'))
                    total_stockOUT = total_stockOUT['QtyOut__sum']
                    # for s in stock_ins:
                    #     total_stockIN += converted_float(s.QtyIn)
                    #     total_stockOUT += converted_float(s.QtyOut)
                    Stock = converted_float(total_stockIN) - converted_float(total_stockOUT)

            elif WarehouseID:
                if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID):
                    stock_ins = StockPosting.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID)
                    total_stockIN = stock_ins.aggregate(Sum('QtyIn'))
                    total_stockIN = total_stockIN['QtyIn__sum']
                    total_stockOUT = stock_ins.aggregate(Sum('QtyOut'))
                    total_stockOUT = total_stockOUT['QtyOut__sum']
                    # for s in stock_ins:
                    #     total_stockIN += converted_float(s.QtyIn)
                    #     total_stockOUT += converted_float(s.QtyOut)

                    Stock = converted_float(total_stockIN) - converted_float(total_stockOUT)
            else:
                if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID):
                    stock_ins = StockPosting.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                    total_stockIN = stock_ins.aggregate(Sum('QtyIn'))
                    total_stockIN = total_stockIN['QtyIn__sum']
                    total_stockOUT = stock_ins.aggregate(Sum('QtyOut'))
                    total_stockOUT = total_stockOUT['QtyOut__sum']
                    # for s in stock_ins:
                    #     total_stockIN += converted_float(s.QtyIn)
                    #     total_stockOUT += converted_float(s.QtyOut)

                    Stock = converted_float(total_stockIN) - converted_float(total_stockOUT)
        return Stock


class ProductSearchInvoiceSerializer(serializers.ModelSerializer):

    Stock = serializers.SerializerMethodField()
    PurchaseTax = serializers.SerializerMethodField()
    SalesTax = serializers.SerializerMethodField()
    GST_PurchaseTax = serializers.SerializerMethodField()
    GST_SalesTax = serializers.SerializerMethodField()
    Tax1_PurchaseTax = serializers.SerializerMethodField()
    Tax1_SalesTax = serializers.SerializerMethodField()
    Tax2_PurchaseTax = serializers.SerializerMethodField()
    Tax2_SalesTax = serializers.SerializerMethodField()
    Tax3_PurchaseTax = serializers.SerializerMethodField()
    Tax3_SalesTax = serializers.SerializerMethodField()
    DefaultUnitID = serializers.SerializerMethodField()
    DefaultUnitName = serializers.SerializerMethodField()
    DefaultSalesPrice = serializers.SerializerMethodField()
    DefaultPurchasePrice = serializers.SerializerMethodField()
    is_GST_inclusive = serializers.SerializerMethodField()
    is_VAT_inclusive = serializers.SerializerMethodField()
    is_TAX1_inclusive = serializers.SerializerMethodField()
    is_TAX2_inclusive = serializers.SerializerMethodField()
    is_TAX3_inclusive = serializers.SerializerMethodField()
    GST_TaxName = serializers.SerializerMethodField()
    VAT_TaxName = serializers.SerializerMethodField()
    GST_ID = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'ProductID', 'ProductName', 'PurchaseTax', 'SalesTax', 'GST_PurchaseTax', 'GST_SalesTax', 'Tax1_PurchaseTax',
                  'Tax1_SalesTax', 'Tax2_PurchaseTax', 'Tax2_SalesTax', 'Tax3_PurchaseTax', 'Tax3_SalesTax', 'DefaultUnitID', 'is_inclusive',
                  'DefaultUnitName', 'DefaultSalesPrice', 'DefaultPurchasePrice', 'Stock', 'is_GST_inclusive', 'is_VAT_inclusive',
                  'is_TAX1_inclusive', 'is_TAX2_inclusive', 'is_TAX3_inclusive', 'GST_TaxName', 'VAT_TaxName', 'GST_ID', 'VatID')

    def get_GST_ID(self, instances):
        CompanyID = self.context.get("CompanyID")
        GST_ID = instances.GST
        return GST_ID

    def get_GST_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.GST
        BranchID = instances.BranchID
        GST_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            GST_TaxName = tax.TaxName

        return GST_TaxName

    def get_VAT_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        VAT_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            VAT_TaxName = tax.TaxName

        return VAT_TaxName

    def get_PurchaseTax(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        PurchaseTax = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            PurchaseTax = tax.PurchaseTax
        return str(PurchaseTax)

    def get_SalesTax(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        SalesTax = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
        return str(SalesTax)

    def get_GST_PurchaseTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.GST
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            PurchaseTax = tax.PurchaseTax
            return str(PurchaseTax)
        else:
            return "0"

    def get_GST_SalesTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.GST
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            return str(SalesTax)
        else:
            return "0"

    def get_Tax1_PurchaseTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax1
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            PurchaseTax = tax.PurchaseTax
            return str(PurchaseTax)
        else:
            return "0"

    def get_Tax1_SalesTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax1
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            return str(SalesTax)
        else:
            return "0"

    def get_Tax2_PurchaseTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax2
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            PurchaseTax = tax.PurchaseTax
            return str(PurchaseTax)
        else:
            return "0"

    def get_Tax2_SalesTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax2
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            return str(SalesTax)
        else:
            return "0"

    def get_Tax3_PurchaseTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax3
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            PurchaseTax = tax.PurchaseTax
            return str(PurchaseTax)
        else:
            return "0"

    def get_Tax3_SalesTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax3
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            return str(SalesTax)
        else:
            return "0"

    def get_DefaultUnitID(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        DefaultUnitID = 0
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            DefaultUnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).PriceListID
        return DefaultUnitID

    def get_DefaultUnitName(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        UnitID = 0
        DefaultUnitName = ""
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).UnitID
            DefaultUnitName = Unit.objects.get(
                UnitID=UnitID, CompanyID=CompanyID).UnitName

        return DefaultUnitName

    def get_DefaultSalesPrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            get_DefaultSalesPrice = unitInstance.SalesPrice
        else:
            get_DefaultSalesPrice = 0

        return get_DefaultSalesPrice

    def get_DefaultPurchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            DefaultPurchasePrice = unitInstance.PurchasePrice
        else:
            DefaultPurchasePrice = 0

        return DefaultPurchasePrice

    def get_Stock(self, instances):
        CompanyID = self.context.get("CompanyID")
        WarehouseID = self.context.get("WarehouseID")

        try:
            type = self.context.get("type")
        except:
            type = "any"

        try:
            Date = self.context.get("Date")
        except:
            Date = ""

        ProductID = instances.ProductID
        BranchID = instances.BranchID
        Stock = 0
        check_EnableProductBatchWise = False
        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
            check_EnableProductBatchWise = GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
        if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
            if WarehouseID:
                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID).exists():
                    Batch_ins = Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID)
                    total_stockIN = 0
                    total_stockOUT = 0
                    for b in Batch_ins:
                        batch_pricelistID = b.PriceListID
                        batch_MultiFactor = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=batch_pricelistID).MultiFactor
                        total_stockIN += (converted_float(b.StockIn) /
                                          converted_float(batch_MultiFactor))
                        total_stockOUT += (converted_float(b.StockOut) /
                                           converted_float(batch_MultiFactor))

                    Stock = converted_float(total_stockIN) - converted_float(total_stockOUT)
            else:
                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
                    Batch_ins = Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                    total_stockIN = 0
                    total_stockOUT = 0
                    for b in Batch_ins:
                        batch_pricelistID = b.PriceListID
                        batch_MultiFactor = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=batch_pricelistID).MultiFactor
                        total_stockIN += (converted_float(b.StockIn) /
                                          converted_float(batch_MultiFactor))
                        total_stockOUT += (converted_float(b.StockOut) /
                                           converted_float(batch_MultiFactor))

                    Stock = converted_float(total_stockIN) - converted_float(total_stockOUT)
        else:
            if type == "CommonStockCalculation" and Date:
                if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID, Date__lte=Date):
                    stock_ins = StockPosting.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID, Date__lte=Date)
                    total_stockIN = 0
                    total_stockOUT = 0
                    for s in stock_ins:
                        total_stockIN += converted_float(s.QtyIn)
                        total_stockOUT += converted_float(s.QtyOut)
                    Stock = converted_float(total_stockIN) - converted_float(total_stockOUT)

            elif WarehouseID:
                if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID):
                    stock_ins = StockPosting.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID)
                    total_stockIN = 0
                    total_stockOUT = 0
                    for s in stock_ins:
                        total_stockIN += converted_float(s.QtyIn)
                        total_stockOUT += converted_float(s.QtyOut)

                    Stock = converted_float(total_stockIN) - converted_float(total_stockOUT)
            else:
                if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID):
                    stock_ins = StockPosting.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                    total_stockIN = 0
                    total_stockOUT = 0
                    for s in stock_ins:
                        total_stockIN += converted_float(s.QtyIn)
                        total_stockOUT += converted_float(s.QtyOut)

                    Stock = converted_float(total_stockIN) - converted_float(total_stockOUT)

        return Stock

    def get_is_GST_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        GST = instances.GST
        BranchID = instances.BranchID
        Inclusive = False
        if GST:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=GST).Inclusive
        return Inclusive

    def get_is_VAT_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        VatID = instances.VatID
        BranchID = instances.BranchID
        Inclusive = False
        if VatID:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=VatID).Inclusive
        return Inclusive

    def get_is_TAX1_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax1 = instances.Tax1
        BranchID = instances.BranchID
        Inclusive = False
        if Tax1:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax1).Inclusive
        return Inclusive

    def get_is_TAX2_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax2 = instances.Tax2
        BranchID = instances.BranchID
        Inclusive = False
        if Tax2:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax2).Inclusive
        return Inclusive

    def get_is_TAX3_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax3 = instances.Tax3
        BranchID = instances.BranchID
        Inclusive = False
        if Tax3:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax3).Inclusive
        return Inclusive


class ProductRestSerializer(serializers.ModelSerializer):

    BrandName = serializers.SerializerMethodField()
    ProductGroupName = serializers.SerializerMethodField()
    PriceListDetails = serializers.SerializerMethodField()
    TaxName = serializers.SerializerMethodField()
    StockMinimum = serializers.SerializerMethodField()
    StockReOrder = serializers.SerializerMethodField()
    StockMaximum = serializers.SerializerMethodField()
    PurchaseTax = serializers.SerializerMethodField()
    SalesTax = serializers.SerializerMethodField()
    GST_PurchaseTax = serializers.SerializerMethodField()
    GST_SalesTax = serializers.SerializerMethodField()
    Tax1_PurchaseTax = serializers.SerializerMethodField()
    Tax1_SalesTax = serializers.SerializerMethodField()
    Tax2_PurchaseTax = serializers.SerializerMethodField()
    Tax2_SalesTax = serializers.SerializerMethodField()
    Tax3_PurchaseTax = serializers.SerializerMethodField()
    Tax3_SalesTax = serializers.SerializerMethodField()
    GST_TaxName = serializers.SerializerMethodField()
    VAT_TaxName = serializers.SerializerMethodField()
    Tax1_TaxName = serializers.SerializerMethodField()
    Tax2_TaxName = serializers.SerializerMethodField()
    Tax3_TaxName = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()
    PurchasePrice = serializers.SerializerMethodField()
    SalesPrice = serializers.SerializerMethodField()
    MRP = serializers.SerializerMethodField()
    DefaultUnitID = serializers.SerializerMethodField()
    DefaultUnitName = serializers.SerializerMethodField()
    DefaultSalesPrice = serializers.SerializerMethodField()
    DefaultSalesPrice1 = serializers.SerializerMethodField()
    DefaultSalesPrice2 = serializers.SerializerMethodField()
    DefaultSalesPrice3 = serializers.SerializerMethodField()
    DefaultPurchasePrice = serializers.SerializerMethodField()
    DefaultMRP = serializers.SerializerMethodField()
    is_VAT_inclusive = serializers.SerializerMethodField()
    is_GST_inclusive = serializers.SerializerMethodField()
    is_TAX1_inclusive = serializers.SerializerMethodField()
    is_TAX2_inclusive = serializers.SerializerMethodField()
    is_TAX3_inclusive = serializers.SerializerMethodField()
    Tax1 = serializers.SerializerMethodField()
    Tax2 = serializers.SerializerMethodField()
    Tax3 = serializers.SerializerMethodField()
    GST = serializers.SerializerMethodField()
    VatID = serializers.SerializerMethodField()
    PLUNo = serializers.SerializerMethodField()
    DefUntID = serializers.SerializerMethodField()
    DefBarcode = serializers.SerializerMethodField()
    Stock = serializers.SerializerMethodField()
    Check_positive_Stock = serializers.SerializerMethodField()
    ProductBarcodeList = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'ProductID',  'is_Service', 'BranchID', 'ProductCode', 'ProductBarcodeList', 'ProductName', 'DisplayName', 'Description', 'ProductGroupID', 'is_Service',
                  'BrandID', 'InventoryType', 'VatID', 'StockMinimum', 'MinimumSalesPrice', 'StockReOrder', 'StockMaximum', 'DefUntID', 'DefBarcode', 'is_inclusive',
                  'MarginPercent', 'ProductImage', 'Active', 'IsRawMaterial', 'IsWeighingScale', 'WeighingCalcType', 'PLUNo', 'WarrantyType', 'Warranty',
                  'IsFavourite', 'CreatedDate', 'CreatedUserID', 'Action', 'GST', 'GST_PurchaseTax', 'GST_SalesTax', 'SalesTax', 'Tax1', 'Tax1_PurchaseTax', 'Tax1_SalesTax',
                  'Tax2', 'Tax2_PurchaseTax', 'Tax2_SalesTax', 'Tax3', 'Tax3_PurchaseTax', 'Tax3_SalesTax', 'BrandName', 'TaxName', 'ProductGroupName', 'PurchaseTax', 'SalesTax',
                  'IsFinishedProduct', 'IsSales', 'IsPurchase', 'PurchasePrice', 'SalesPrice', 'MRP', 'GST_TaxName', 'VAT_TaxName', 'UnitName', 'Tax1_TaxName', 'Tax2_TaxName', 'Tax3_TaxName',
                  'DefaultUnitID', 'DefaultUnitName', 'DefaultSalesPrice', 'DefaultSalesPrice1', 'DefaultSalesPrice2', 'DefaultSalesPrice3', 'DefaultPurchasePrice',
                  'is_VAT_inclusive', 'is_GST_inclusive', 'is_TAX1_inclusive', 'is_TAX2_inclusive', 'is_TAX3_inclusive', 'PriceListDetails', 'DefaultMRP', "IsKFC", "HSNCode", 'Stock', 'Check_positive_Stock')

    def get_ProductBarcodeList(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        product_barcode_list = ProductBarcode.objects.filter(
            CompanyID=CompanyID, ProductID=instances, BranchID=BranchID)
        serialized = ProductBarcodeListRestSerializer(product_barcode_list, many=True, context={
            "CompanyID": CompanyID, "PriceRounding": PriceRounding})
        data = serialized.data
        if not data:
            data = []

        return data

    def get_BrandName(self, instances):
        CompanyID = self.context.get("CompanyID")

        BrandID = instances.BrandID
        BranchID = instances.BranchID
        productsForAllBranches = get_BranchSettings(
            CompanyID, "productsForAllBranches")
        print(productsForAllBranches)
        if productsForAllBranches:
            brand = Brand.objects.filter(
                CompanyID=CompanyID, BrandID=BrandID).first()
        else:
            brand = Brand.objects.filter(
                CompanyID=CompanyID, BrandID=BrandID).first()
        BrandName = ""
        if brand:
            BrandName = brand.BrandName

        return BrandName

    def get_Check_positive_Stock(self, instances):
        CompanyID = self.context.get("CompanyID")
        WarehouseID = self.context.get("WarehouseID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        Check_positive_Stock = 0

        if WarehouseID:
            if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID):
                stock_ins = StockPosting.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID)
                total_stockIN = 0
                total_stockOUT = 0
                for s in stock_ins:
                    total_stockIN += converted_float(s.QtyIn)
                    total_stockOUT += converted_float(s.QtyOut)

                Check_positive_Stock = converted_float(
                    total_stockIN) - converted_float(total_stockOUT)
        else:
            if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID):
                stock_ins = StockPosting.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                total_stockIN = 0
                total_stockOUT = 0
                for s in stock_ins:
                    total_stockIN += converted_float(s.QtyIn)
                    total_stockOUT += converted_float(s.QtyOut)

                Check_positive_Stock = converted_float(
                    total_stockIN) - converted_float(total_stockOUT)

        return Check_positive_Stock

    def get_Stock(self, instances):
        CompanyID = self.context.get("CompanyID")
        WarehouseID = self.context.get("WarehouseID")

        try:
            type = self.context.get("type")
        except:
            type = "any"

        try:
            Date = self.context.get("Date")
        except:
            Date = ""

        ProductID = instances.ProductID
        BranchID = instances.BranchID
        Stock = 0
        check_EnableProductBatchWise = False
        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
            check_EnableProductBatchWise = GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
        if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
            if WarehouseID:
                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID).exists():
                    Batch_ins = Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID)
                    total_stockIN = 0
                    total_stockOUT = 0
                    for b in Batch_ins:
                        batch_pricelistID = b.PriceListID
                        batch_MultiFactor = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=batch_pricelistID).MultiFactor
                        total_stockIN += (converted_float(b.StockIn) /
                                          converted_float(batch_MultiFactor))
                        total_stockOUT += (converted_float(b.StockOut) /
                                           converted_float(batch_MultiFactor))

                    Stock = converted_float(total_stockIN) - converted_float(total_stockOUT)
            else:
                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
                    Batch_ins = Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                    total_stockIN = 0
                    total_stockOUT = 0
                    for b in Batch_ins:
                        batch_pricelistID = b.PriceListID
                        batch_MultiFactor = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=batch_pricelistID).MultiFactor
                        total_stockIN += (converted_float(b.StockIn) /
                                          converted_float(batch_MultiFactor))
                        total_stockOUT += (converted_float(b.StockOut) /
                                           converted_float(batch_MultiFactor))

                    Stock = converted_float(total_stockIN) - converted_float(total_stockOUT)
        else:
            if type == "CommonStockCalculation" and Date:
                if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID, Date__lte=Date):
                    stock_ins = StockPosting.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID, Date__lte=Date)
                    total_stockIN = 0
                    total_stockOUT = 0
                    for s in stock_ins:
                        total_stockIN += converted_float(s.QtyIn)
                        total_stockOUT += converted_float(s.QtyOut)
                    Stock = converted_float(total_stockIN) - converted_float(total_stockOUT)

            elif WarehouseID:
                if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID):
                    stock_ins = StockPosting.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID)
                    total_stockIN = 0
                    total_stockOUT = 0
                    for s in stock_ins:
                        total_stockIN += converted_float(s.QtyIn)
                        total_stockOUT += converted_float(s.QtyOut)

                    Stock = converted_float(total_stockIN) - converted_float(total_stockOUT)
            else:
                if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID):
                    stock_ins = StockPosting.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                    total_stockIN = 0
                    total_stockOUT = 0
                    for s in stock_ins:
                        total_stockIN += converted_float(s.QtyIn)
                        total_stockOUT += converted_float(s.QtyOut)

                    Stock = converted_float(total_stockIN) - converted_float(total_stockOUT)

        return Stock

    def get_Tax1(self, instances):
        Tax1 = instances.Tax1
        if not Tax1:
            Tax1 = 1
        return Tax1

    def get_Tax2(self, instances):
        Tax2 = instances.Tax2
        if not Tax2:
            Tax2 = 1
        return Tax2

    def get_Tax3(self, instances):
        Tax3 = instances.Tax3
        if not Tax3:
            Tax3 = 1
        return Tax3

    def get_GST(self, instances):
        GST = instances.GST
        if not GST:
            GST = 1
        return GST

    def get_VatID(self, instances):
        VatID = instances.VatID

        if not VatID:
            VatID = 1
        return VatID

    def get_PLUNo(self, instances):
        PLUNo = instances.PLUNo
        if not PLUNo:
            PLUNo = 1
        return PLUNo

    def get_is_VAT_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        VatID = instances.VatID
        BranchID = instances.BranchID
        Inclusive = False
        check_productsForAllBranches = get_BranchSettings(
            CompanyID, "productsForAllBranches")
        if VatID:
            if check_productsForAllBranches:
                Inclusive = TaxCategory.objects.filter(
                    CompanyID=CompanyID, TaxID=VatID).first().Inclusive
            else:
                Inclusive = TaxCategory.objects.get(
                    CompanyID=CompanyID, TaxID=VatID).Inclusive
        return Inclusive

    def get_is_GST_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        GST = instances.GST
        BranchID = instances.BranchID
        Inclusive = False
        check_productsForAllBranches = get_BranchSettings(
            CompanyID, "productsForAllBranches")
        if GST:
            if check_productsForAllBranches:
                Inclusive = TaxCategory.objects.filter(
                    CompanyID=CompanyID, TaxID=GST).first().Inclusive
            else:
                Inclusive = TaxCategory.objects.get(
                    CompanyID=CompanyID, TaxID=GST).Inclusive
        return Inclusive

    def get_is_TAX1_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax1 = instances.Tax1
        BranchID = instances.BranchID
        Inclusive = False
        if Tax1:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax1).Inclusive
        return Inclusive

    def get_is_TAX2_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax2 = instances.Tax2
        BranchID = instances.BranchID
        Inclusive = False
        if Tax2:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax2).Inclusive
        return Inclusive

    def get_is_TAX3_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax3 = instances.Tax3
        BranchID = instances.BranchID
        Inclusive = False
        if Tax3:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax3).Inclusive
        return Inclusive

    def get_DefaultUnitID(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        DefaultUnitID = 0
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            DefaultUnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).PriceListID
            # DefaultUnitID = unitInstance.PriceListID
        return DefaultUnitID

    def get_DefUntID(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        DefUntID = 0
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            DefUntID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).UnitID
        # DefUntID = unitInstance.PriceListID
        return DefUntID

    def get_DefBarcode(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        DefBarcode = 0
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            DefBarcode = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).Barcode
        # DefBarcode = unitInstance.PriceListID
        return DefBarcode

    def get_DefaultUnitName(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        UnitID = 0
        DefaultUnitName = ""
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).UnitID
            DefaultUnitName = Unit.objects.get(
                UnitID=UnitID, CompanyID=CompanyID).UnitName

        return DefaultUnitName

    def get_DefaultSalesPrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            get_DefaultSalesPrice = unitInstance.SalesPrice
        else:
            get_DefaultSalesPrice = 0

        return get_DefaultSalesPrice

    def get_DefaultSalesPrice1(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            get_DefaultSalesPrice1 = unitInstance.SalesPrice1
        else:
            get_DefaultSalesPrice1 = 0

        return get_DefaultSalesPrice1

    def get_DefaultSalesPrice2(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            get_DefaultSalesPrice2 = unitInstance.SalesPrice2
        else:
            get_DefaultSalesPrice2 = 0

        return get_DefaultSalesPrice2

    def get_DefaultSalesPrice3(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            get_DefaultSalesPrice3 = unitInstance.SalesPrice3
        else:
            get_DefaultSalesPrice3 = 0

        return get_DefaultSalesPrice3

    def get_DefaultMRP(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            get_DefaultMRP = unitInstance.MRP
        else:
            get_DefaultMRP = 0

        return get_DefaultMRP

    def get_DefaultPurchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            DefaultPurchasePrice = unitInstance.PurchasePrice
        else:
            DefaultPurchasePrice = 0

        return DefaultPurchasePrice

    def get_UnitName(self, instances):
        CompanyID = self.context.get("CompanyID")

        ProductID = instances.ProductID
        BranchID = instances.BranchID
        UnitName = ""
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            UnitID = priceList.UnitID
            UnitName = Unit.objects.get(
                CompanyID=CompanyID, UnitID=UnitID).UnitName

        return UnitName

    def get_PurchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            PurchasePrice = priceList.PurchasePrice
            # PurchasePrice = round(PurchasePrice, int(PriceRounding))
        else:
            PurchasePrice = 0
        return PurchasePrice

    def get_SalesPrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            SalesPrice = priceList.SalesPrice
            # SalesPrice = round(SalesPrice, int(PriceRounding))
        else:
            SalesPrice = 0
        return SalesPrice

    def get_MRP(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            MRP = priceList.MRP
            # MRP = round(MRP, int(PriceRounding))
        else:
            MRP = 0
        return MRP

    def get_ProductGroupName(self, instances):
        CompanyID = self.context.get("CompanyID")

        ProductGroupID = instances.ProductGroupID
        BranchID = instances.BranchID
        product_group = ProductGroup.objects.filter(
            CompanyID=CompanyID, ProductGroupID=ProductGroupID).first()
        ProductGroupName = product_group.GroupName

        return ProductGroupName

    def get_PriceListDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        price_list = PriceList.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID)
        serialized = PriceListRestSerializer(price_list, many=True, context={
                                             "CompanyID": CompanyID, "PriceRounding": PriceRounding})

        return serialized.data

    def get_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")
        TaxName = ""
        TaxID = 1
        if instances.VatID != 1:
            TaxID = instances.VatID
        elif instances.GST != 1:
            TaxID = instances.GST
        elif instances.Tax1 != 1:
            TaxID = instances.Tax1
        elif instances.Tax2 != 1:
            TaxID = instances.Tax2
        elif instances.Tax3 != 1:
            TaxID = instances.Tax3
        BranchID = instances.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            TaxName = tax.TaxName

        return TaxName

    def get_GST_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.GST
        BranchID = instances.BranchID
        GST_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            GST_TaxName = tax.TaxName

        return GST_TaxName

    def get_VAT_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        VAT_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            VAT_TaxName = tax.TaxName

        return VAT_TaxName

    def get_Tax1_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.Tax1
        BranchID = instances.BranchID
        Tax1_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            Tax1_TaxName = tax.TaxName

        return Tax1_TaxName

    def get_Tax2_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.Tax2
        BranchID = instances.BranchID
        Tax2_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            Tax2_TaxName = tax.TaxName

        return Tax2_TaxName

    def get_Tax3_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.Tax3
        BranchID = instances.BranchID
        Tax3_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            Tax3_TaxName = tax.TaxName

        return Tax3_TaxName

    def get_PurchaseTax(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        PurchaseTax = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            PurchaseTax = tax.PurchaseTax
            # if PurchaseTax:
            #     PurchaseTax = round(PurchaseTax, int(PriceRounding))
            # else:
            #     PurchaseTax = 0
        return str(PurchaseTax)

    def get_SalesTax(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        SalesTax = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            # if SalesTax:
            #     SalesTax = round(SalesTax, int(PriceRounding))
            # else:
            #     SalesTax = 0
        return str(SalesTax)

    def get_StockMinimum(self, instances):
        PriceRounding = self.context.get("PriceRounding")

        StockMinimum = instances.StockMinimum
        # if StockMinimum:
        #     StockMinimum = round(StockMinimum, int(PriceRounding))
        # else:
        #     StockMinimum = 0

        return str(StockMinimum)

    def get_StockMaximum(self, instances):

        PriceRounding = self.context.get("PriceRounding")
        StockMaximum = instances.StockMaximum

        # if StockMaximum:
        #     StockMaximum = round(StockMaximum, int(PriceRounding))
        # else:
        #     StockMaximum = 0

        return str(StockMaximum)

    def get_StockReOrder(self, instances):

        PriceRounding = self.context.get("PriceRounding")
        StockReOrder = instances.StockReOrder
        # if StockReOrder:
        #     StockReOrder = round(StockReOrder, int(PriceRounding))
        # else:
        #     StockReOrder = 0
        return str(StockReOrder)

    def get_GST_PurchaseTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.GST
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
            PurchaseTax = tax.PurchaseTax
            # if PurchaseTax:
            #     GST_PurchaseTax = round(PurchaseTax, int(PriceRounding))
            # else:
            #     GST_PurchaseTax = 0
            return str(PurchaseTax)
        else:
            return "0"

    def get_GST_SalesTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.GST
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            # if SalesTax:
            #     GST_SalesTax = round(SalesTax, int(PriceRounding))
            # else:
            #     GST_SalesTax = 0
            return str(SalesTax)
        else:
            return "0"

    def get_Tax1_PurchaseTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax1
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            PurchaseTax = tax.PurchaseTax
            # if PurchaseTax:
            #     Tax1_PurchaseTax = round(PurchaseTax, int(PriceRounding))
            # else:
            #     Tax1_PurchaseTax = 0
            return str(PurchaseTax)
        else:
            return "0"

    def get_Tax1_SalesTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax1
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            # if SalesTax:
            #     Tax1_SalesTax = round(SalesTax, int(PriceRounding))
            # else:
            #     Tax1_SalesTax = 0
            return str(SalesTax)
        else:
            return "0"

    def get_Tax2_PurchaseTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax2
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            PurchaseTax = tax.PurchaseTax
            # if PurchaseTax:
            #     Tax2_PurchaseTax = round(PurchaseTax, int(PriceRounding))
            # else:
            #     Tax2_PurchaseTax = 0
            return str(PurchaseTax)
        else:
            return "0"

    def get_Tax2_SalesTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax2
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            # if SalesTax:
            #     Tax2_SalesTax = round(SalesTax, int(PriceRounding))
            # else:
            #     Tax2_SalesTax = 0
            return str(SalesTax)
        else:
            return "0"

    def get_Tax3_PurchaseTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax3
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            PurchaseTax = tax.PurchaseTax
            # if PurchaseTax:
            #     Tax3_PurchaseTax = round(PurchaseTax, int(PriceRounding))
            # else:
            #     Tax3_PurchaseTax = 0
            return str(PurchaseTax)
        else:
            return "0"

    def get_Tax3_SalesTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax3
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            # if SalesTax:
            #     Tax3_SalesTax = round(SalesTax, int(PriceRounding))
            # else:
            #     Tax3_SalesTax = 0
            return str(SalesTax)
        else:
            return "0"


class SingleProductRestSerializer(serializers.ModelSerializer):
    BrandName = serializers.SerializerMethodField()
    ProductGroupName = serializers.SerializerMethodField()
    PriceListDetails = serializers.SerializerMethodField()
    TaxName = serializers.SerializerMethodField()
    StockMinimum = serializers.SerializerMethodField()
    StockReOrder = serializers.SerializerMethodField()
    StockMaximum = serializers.SerializerMethodField()
    PurchaseTax = serializers.SerializerMethodField()
    SalesTax = serializers.SerializerMethodField()
    GST_PurchaseTax = serializers.SerializerMethodField()
    GST_SalesTax = serializers.SerializerMethodField()
    Tax1_PurchaseTax = serializers.SerializerMethodField()
    Tax1_SalesTax = serializers.SerializerMethodField()
    Tax2_PurchaseTax = serializers.SerializerMethodField()
    Tax2_SalesTax = serializers.SerializerMethodField()
    Tax3_PurchaseTax = serializers.SerializerMethodField()
    Tax3_SalesTax = serializers.SerializerMethodField()
    GST_TaxName = serializers.SerializerMethodField()
    VAT_TaxName = serializers.SerializerMethodField()
    Tax1_TaxName = serializers.SerializerMethodField()
    Tax2_TaxName = serializers.SerializerMethodField()
    Tax3_TaxName = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()
    PurchasePrice = serializers.SerializerMethodField()
    SalesPrice = serializers.SerializerMethodField()
    MRP = serializers.SerializerMethodField()
    DefaultUnitID = serializers.SerializerMethodField()
    DefaultUnitName = serializers.SerializerMethodField()
    DefaultSalesPrice = serializers.SerializerMethodField()
    DefaultSalesPrice1 = serializers.SerializerMethodField()
    DefaultSalesPrice2 = serializers.SerializerMethodField()
    DefaultSalesPrice3 = serializers.SerializerMethodField()
    DefaultPurchasePrice = serializers.SerializerMethodField()
    DefaultMRP = serializers.SerializerMethodField()
    is_VAT_inclusive = serializers.SerializerMethodField()
    is_GST_inclusive = serializers.SerializerMethodField()
    is_TAX1_inclusive = serializers.SerializerMethodField()
    is_TAX2_inclusive = serializers.SerializerMethodField()
    is_TAX3_inclusive = serializers.SerializerMethodField()
    Tax1 = serializers.SerializerMethodField()
    Tax2 = serializers.SerializerMethodField()
    Tax3 = serializers.SerializerMethodField()
    GST = serializers.SerializerMethodField()
    VatID = serializers.SerializerMethodField()
    PLUNo = serializers.SerializerMethodField()
    DefUntID = serializers.SerializerMethodField()
    DefBarcode = serializers.SerializerMethodField()
    Stock = serializers.SerializerMethodField()
    Check_positive_Stock = serializers.SerializerMethodField()
    DefaultBarcode = serializers.SerializerMethodField()
    ProductBarcodeList = serializers.SerializerMethodField()
    

    class Meta:
        model = Product
        fields = ('id', 'ProductID', 'is_Service', 'BranchID', 'ProductCode', 'ProductBarcodeList', 'ProductName', 'DisplayName', 'Description', 'ProductGroupID',
                  'BrandID', 'InventoryType', 'VatID', 'StockMinimum', 'MinimumSalesPrice', 'StockReOrder', 'StockMaximum', 'DefUntID', 'DefBarcode', 'is_inclusive',
                  'MarginPercent', 'ProductImage', 'Active', 'IsRawMaterial', 'IsWeighingScale', 'WeighingCalcType', 'PLUNo', 'WarrantyType', 'Warranty',
                  'IsFavourite', 'CreatedDate', 'CreatedUserID', 'Action', 'GST', 'GST_PurchaseTax', 'GST_SalesTax', 'SalesTax', 'Tax1', 'Tax1_PurchaseTax', 'Tax1_SalesTax',
                  'Tax2', 'Tax2_PurchaseTax', 'Tax2_SalesTax', 'Tax3', 'Tax3_PurchaseTax', 'Tax3_SalesTax', 'BrandName', 'TaxName', 'ProductGroupName', 'PurchaseTax', 'SalesTax',
                  'IsFinishedProduct', 'IsSales', 'IsPurchase', 'PurchasePrice', 'SalesPrice', 'MRP', 'GST_TaxName', 'VAT_TaxName', 'UnitName', 'Tax1_TaxName', 'Tax2_TaxName', 'Tax3_TaxName',
                  'DefaultUnitID', 'DefaultUnitName', 'DefaultSalesPrice', 'DefaultSalesPrice1', 'DefaultSalesPrice2', 'DefaultSalesPrice3', 'DefaultPurchasePrice',
                  'is_VAT_inclusive', 'is_GST_inclusive', 'is_TAX1_inclusive', 'is_TAX2_inclusive', 'is_TAX3_inclusive', 'PriceListDetails', 'DefaultMRP', "IsKFC", 'DefaultBarcode', "HSNCode", 'Stock', 'Check_positive_Stock')

    def get_ReverseFactor(self, instances):
        return ""
    
    def get_ProductBarcodeList(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        product_barcode_list = ProductBarcode.objects.filter(
            CompanyID=CompanyID, ProductID=instances, BranchID=BranchID)
        serialized = ProductBarcodeListRestSerializer(product_barcode_list, many=True, context={
            "CompanyID": CompanyID, "PriceRounding": PriceRounding})

        return serialized.data

    def get_BrandName(self, instances):
        CompanyID = self.context.get("CompanyID")

        BrandID = instances.BrandID
        BranchID = instances.BranchID
        brand = Brand.objects.filter(
            CompanyID=CompanyID, BrandID=BrandID).first()
        BrandName = ""
        if brand:
            BrandName = brand.BrandName

        return BrandName

    def get_DefaultBarcode(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        DefaultBarcode = ""
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            DefaultBarcode = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).Barcode

        return DefaultBarcode

    def get_Check_positive_Stock(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        Check_positive_Stock = 0

        if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID):
            stock_ins = StockPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
            total_stockIN = 0
            total_stockOUT = 0
            for s in stock_ins:
                total_stockIN += converted_float(s.QtyIn)
                total_stockOUT += converted_float(s.QtyOut)

            Check_positive_Stock = converted_float(total_stockIN) - converted_float(total_stockOUT)

        return Check_positive_Stock

    def get_Stock(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        Stock = 0
        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
            Batch_ins = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
            total_stockIN = 0
            total_stockOUT = 0
            for b in Batch_ins:
                batch_pricelistID = b.PriceListID
                batch_MultiFactor = PriceList.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, PriceListID=batch_pricelistID).MultiFactor
                total_stockIN += (converted_float(b.StockIn) / converted_float(batch_MultiFactor))
                total_stockOUT += (converted_float(b.StockOut) /
                                   converted_float(batch_MultiFactor))

            Stock = converted_float(total_stockIN) - converted_float(total_stockOUT)
        else:
            if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID):
                stock_ins = StockPosting.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                total_stockIN = 0
                total_stockOUT = 0
                for s in stock_ins:
                    total_stockIN += converted_float(s.QtyIn)
                    total_stockOUT += converted_float(s.QtyOut)

                Stock = converted_float(total_stockIN) - converted_float(total_stockOUT)

        return Stock

    def get_Tax1(self, instances):
        Tax1 = instances.Tax1
        if not Tax1:
            Tax1 = 1
        return Tax1

    def get_Tax2(self, instances):
        Tax2 = instances.Tax2
        if not Tax2:
            Tax2 = 1
        return Tax2

    def get_Tax3(self, instances):
        Tax3 = instances.Tax3
        if not Tax3:
            Tax3 = 1
        return Tax3

    def get_GST(self, instances):
        GST = instances.GST
        if not GST:
            GST = 1
        return GST

    def get_VatID(self, instances):
        VatID = instances.VatID

        if not VatID:
            VatID = 1
        return VatID

    def get_PLUNo(self, instances):
        PLUNo = instances.PLUNo
        if not PLUNo:
            PLUNo = 1
        return PLUNo

    def get_is_VAT_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        VatID = instances.VatID
        BranchID = instances.BranchID
        Inclusive = False
        if VatID:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=VatID).Inclusive
        return Inclusive

    def get_is_GST_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        GST = instances.GST
        BranchID = instances.BranchID
        Inclusive = False
        if GST:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=GST).Inclusive
        return Inclusive

    def get_is_TAX1_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax1 = instances.Tax1
        BranchID = instances.BranchID
        Inclusive = False
        if Tax1:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax1).Inclusive
        return Inclusive

    def get_is_TAX2_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax2 = instances.Tax2
        BranchID = instances.BranchID
        Inclusive = False
        if Tax2:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax2).Inclusive
        return Inclusive

    def get_is_TAX3_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax3 = instances.Tax3
        BranchID = instances.BranchID
        Inclusive = False
        if Tax3:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax3).Inclusive
        return Inclusive

    def get_DefaultUnitID(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        DefaultUnitID = 0
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            DefaultUnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).PriceListID
            # DefaultUnitID = unitInstance.PriceListID
        return DefaultUnitID

    def get_DefUntID(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        DefUntID = 0
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            DefUntID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).UnitID
        # DefUntID = unitInstance.PriceListID
        return DefUntID

    def get_DefBarcode(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        DefBarcode = 0
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            DefBarcode = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).Barcode
        # DefBarcode = unitInstance.PriceListID
        return DefBarcode

    def get_DefaultUnitName(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        UnitID = 0
        DefaultUnitName = ""
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).UnitID
            DefaultUnitName = Unit.objects.get(
                UnitID=UnitID, CompanyID=CompanyID).UnitName

        return DefaultUnitName

    def get_DefaultSalesPrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            get_DefaultSalesPrice = unitInstance.SalesPrice
        else:
            get_DefaultSalesPrice = 0

        return get_DefaultSalesPrice

    def get_DefaultSalesPrice1(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            get_DefaultSalesPrice1 = unitInstance.SalesPrice1
        else:
            get_DefaultSalesPrice1 = 0

        return get_DefaultSalesPrice1

    def get_DefaultSalesPrice2(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            get_DefaultSalesPrice2 = unitInstance.SalesPrice2
        else:
            get_DefaultSalesPrice2 = 0

        return get_DefaultSalesPrice2

    def get_DefaultSalesPrice3(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            get_DefaultSalesPrice3 = unitInstance.SalesPrice3
        else:
            get_DefaultSalesPrice3 = 0

        return get_DefaultSalesPrice3

    def get_DefaultMRP(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            get_DefaultMRP = unitInstance.MRP
        else:
            get_DefaultMRP = 0

        return get_DefaultMRP

    def get_DefaultPurchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            DefaultPurchasePrice = unitInstance.PurchasePrice
        else:
            DefaultPurchasePrice = 0

        return DefaultPurchasePrice

    def get_UnitName(self, instances):
        CompanyID = self.context.get("CompanyID")

        ProductID = instances.ProductID
        BranchID = instances.BranchID
        UnitName = ""
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            UnitID = priceList.UnitID
            UnitName = Unit.objects.get(
                CompanyID=CompanyID, UnitID=UnitID).UnitName

        return UnitName

    def get_PurchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            PurchasePrice = priceList.PurchasePrice
            PurchasePrice = round(PurchasePrice, int(PriceRounding))
        else:
            PurchasePrice = 0
        return PurchasePrice

    def get_SalesPrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            SalesPrice = priceList.SalesPrice
            SalesPrice = round(SalesPrice, int(PriceRounding))
        else:
            SalesPrice = 0
        return SalesPrice

    def get_MRP(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            MRP = priceList.MRP
            MRP = round(MRP, int(PriceRounding))
        else:
            MRP = 0
        return MRP

    def get_ProductGroupName(self, instances):
        CompanyID = self.context.get("CompanyID")

        ProductGroupID = instances.ProductGroupID
        BranchID = instances.BranchID
        product_group = ProductGroup.objects.filter(
            CompanyID=CompanyID, ProductGroupID=ProductGroupID).first()
        ProductGroupName = product_group.GroupName

        return ProductGroupName

    def get_PriceListDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        price_list = PriceList.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID)
        serialized = SinglePriceListRestSerializer(price_list, many=True, context={
            "CompanyID": CompanyID, "PriceRounding": PriceRounding})

        return serialized.data

    def get_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            TaxName = tax.TaxName

        return TaxName

    def get_GST_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.GST
        BranchID = instances.BranchID
        GST_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            GST_TaxName = tax.TaxName

        return GST_TaxName

    def get_VAT_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        VAT_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            VAT_TaxName = tax.TaxName

        return VAT_TaxName

    def get_Tax1_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.Tax1
        BranchID = instances.BranchID
        Tax1_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            Tax1_TaxName = tax.TaxName

        return Tax1_TaxName

    def get_Tax2_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.Tax2
        BranchID = instances.BranchID
        Tax2_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            Tax2_TaxName = tax.TaxName

        return Tax2_TaxName

    def get_Tax3_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.Tax3
        BranchID = instances.BranchID
        Tax3_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            Tax3_TaxName = tax.TaxName

        return Tax3_TaxName

    def get_PurchaseTax(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        PurchaseTax = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            PurchaseTax = tax.PurchaseTax
            if PurchaseTax:
                PurchaseTax = round(PurchaseTax, int(PriceRounding))
            else:
                PurchaseTax = 0
        return str(PurchaseTax)

    def get_SalesTax(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        SalesTax = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            if SalesTax:
                SalesTax = round(SalesTax, int(PriceRounding))
            else:
                SalesTax = 0
        return str(SalesTax)

    def get_StockMinimum(self, instances):
        PriceRounding = self.context.get("PriceRounding")

        StockMinimum = instances.StockMinimum
        if StockMinimum:
            StockMinimum = round(StockMinimum, int(PriceRounding))
        else:
            StockMinimum = 0

        return str(StockMinimum)

    def get_StockMaximum(self, instances):

        PriceRounding = self.context.get("PriceRounding")
        StockMaximum = instances.StockMaximum

        if StockMaximum:
            StockMaximum = round(StockMaximum, int(PriceRounding))
        else:
            StockMaximum = 0

        return str(StockMaximum)

    def get_StockReOrder(self, instances):

        PriceRounding = self.context.get("PriceRounding")
        StockReOrder = instances.StockReOrder
        if StockReOrder:
            StockReOrder = round(StockReOrder, int(PriceRounding))
        else:
            StockReOrder = 0
        return str(StockReOrder)

    def get_GST_PurchaseTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.GST
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            PurchaseTax = tax.PurchaseTax
            if PurchaseTax:
                GST_PurchaseTax = round(PurchaseTax, int(PriceRounding))
            else:
                GST_PurchaseTax = 0
            return str(GST_PurchaseTax)
        else:
            return "0"

    def get_GST_SalesTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.GST
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            if SalesTax:
                GST_SalesTax = round(SalesTax, int(PriceRounding))
            else:
                GST_SalesTax = 0
            return str(GST_SalesTax)
        else:
            return "0"

    def get_Tax1_PurchaseTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax1
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            PurchaseTax = tax.PurchaseTax
            if PurchaseTax:
                Tax1_PurchaseTax = round(PurchaseTax, int(PriceRounding))
            else:
                Tax1_PurchaseTax = 0
            return str(Tax1_PurchaseTax)
        else:
            return "0"

    def get_Tax1_SalesTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax1
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            if SalesTax:
                Tax1_SalesTax = round(SalesTax, int(PriceRounding))
            else:
                Tax1_SalesTax = 0
            return str(Tax1_SalesTax)
        else:
            return "0"

    def get_Tax2_PurchaseTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax2
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            PurchaseTax = tax.PurchaseTax
            if PurchaseTax:
                Tax2_PurchaseTax = round(PurchaseTax, int(PriceRounding))
            else:
                Tax2_PurchaseTax = 0
            return str(Tax2_PurchaseTax)
        else:
            return "0"

    def get_Tax2_SalesTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax2
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            if SalesTax:
                Tax2_SalesTax = round(SalesTax, int(PriceRounding))
            else:
                Tax2_SalesTax = 0
            return str(Tax2_SalesTax)
        else:
            return "0"

    def get_Tax3_PurchaseTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax3
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            PurchaseTax = tax.PurchaseTax
            if PurchaseTax:
                Tax3_PurchaseTax = round(PurchaseTax, int(PriceRounding))
            else:
                Tax3_PurchaseTax = 0
            return str(Tax3_PurchaseTax)
        else:
            return "0"

    def get_Tax3_SalesTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax3
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            if SalesTax:
                Tax3_SalesTax = round(SalesTax, int(PriceRounding))
            else:
                Tax3_SalesTax = 0
            return str(Tax3_SalesTax)
        else:
            return "0"


class ProductbyGrouptSerializer(serializers.ModelSerializer):

    Barcode = serializers.SerializerMethodField()
    Stock = serializers.SerializerMethodField()
    CostPerItem = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()
    ExcessOrShortage = serializers.SerializerMethodField()
    StockAdjustment = serializers.SerializerMethodField()
    PriceListID = serializers.SerializerMethodField()
    BatchCode = serializers.SerializerMethodField()
    BatchCode_list = serializers.SerializerMethodField()
    UnitList = serializers.SerializerMethodField()
    Batch_purchasePrice = serializers.SerializerMethodField()
    Batch_salesPrice = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'ProductID', 'PriceListID', 'Barcode', 'ProductName', 'BatchCode', 'BatchCode_list', 'UnitList',
                  'Stock', 'CostPerItem', 'UnitName', 'ExcessOrShortage', 'StockAdjustment', 'Batch_purchasePrice', 'Batch_salesPrice')

    def get_Barcode(self, instances):
        CompanyID = self.context.get("CompanyID")

        ProductID = instances.ProductID
        BranchID = instances.BranchID
        Barcode = ""
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            Barcode = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).AutoBarcode

        return Barcode

    def get_BatchCode(self, instances):
        CompanyID = self.context.get("CompanyID")
        BatchCode = "0"
        BranchID = instances.BranchID
        ProductID = instances.ProductID
        # PriceListID = instances.PriceListID
        check_EnableProductBatchWise = False
        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
            check_EnableProductBatchWise = GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
            if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
                    batch_ins = Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).last()
                    BatchCode = batch_ins.BatchCode

        return str(BatchCode)

    def get_BatchCode_list(self, instance):
        BatchCode_list = []
        CompanyID = self.context.get("CompanyID")
        # PriceRounding = int(self.context.get("PriceRounding"))
        BranchID = instance.BranchID
        ProductID = instance.ProductID
        BatchCode_list = []
        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
            batch_details = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
            BatchCode_list = Batch_ListSerializer(
                batch_details, many=True, context={"CompanyID": CompanyID})
            BatchCode_list = BatchCode_list.data
        return BatchCode_list

    def get_UnitList(self, instance):
        UnitList = []
        CompanyID = self.context.get("CompanyID")
        # PriceRounding = int(self.context.get("PriceRounding"))
        BranchID = instance.BranchID
        ProductID = instance.ProductID
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID).exists():
            unit_details = PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID)
            UnitList = UnitListSerializer(unit_details, many=True, context={
                                          "CompanyID": CompanyID})
            UnitList = UnitList.data
        return UnitList

    def get_PriceListID(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        PriceListID = ""
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            PriceListID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).PriceListID
        return PriceListID

    def get_Stock(self, instances):
        CompanyID = self.context.get("CompanyID")
        WarehouseID = self.context.get("WarehouseID")
        TotalQtyIn = 0
        TotalQtyOut = 0
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        PriceListID = PriceList.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).PriceListID

        if WarehouseID:
            if StockPosting.objects.filter(CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID, WareHouseID=WarehouseID).exists():
                stockpostIns = StockPosting.objects.filter(
                    CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID, WareHouseID=WarehouseID)
                for i in stockpostIns:
                    TotalQtyIn += i.QtyIn
                    TotalQtyOut += i.QtyOut

            Stock = converted_float(TotalQtyIn) - converted_float(TotalQtyOut)
        else:
            if StockPosting.objects.filter(CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).exists():
                stockpostIns = StockPosting.objects.filter(
                    CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID)
                for i in stockpostIns:
                    TotalQtyIn += i.QtyIn
                    TotalQtyOut += i.QtyOut

            Stock = converted_float(TotalQtyIn) - converted_float(TotalQtyOut)
        return converted_float(Stock)

    def get_CostPerItem(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        PurchasePrice = 0
        check_EnableProductBatchWise = False
        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
            check_EnableProductBatchWise = GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
            if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
                    batch_ins = Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).last()
                    PurchasePrice = batch_ins.PurchasePrice
                else:
                    PurchasePrice = PriceList.objects.get(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, DefaultUnit=True).PurchasePrice
            else:
                PurchasePrice = PriceList.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, DefaultUnit=True).PurchasePrice
        else:
            PurchasePrice = PriceList.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, DefaultUnit=True).PurchasePrice
        return converted_float(PurchasePrice)

    def get_Batch_purchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        Batch_purchasePrice = 0
        check_EnableProductBatchWise = False
        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
            check_EnableProductBatchWise = GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
            if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
                    batch_ins = Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).last()
                    Batch_purchasePrice = batch_ins.PurchasePrice
                else:
                    Batch_purchasePrice = PriceList.objects.get(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, DefaultUnit=True).PurchasePrice
            else:
                Batch_purchasePrice = PriceList.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, DefaultUnit=True).PurchasePrice
        else:
            Batch_purchasePrice = PriceList.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, DefaultUnit=True).PurchasePrice
        return converted_float(Batch_purchasePrice)

    def get_Batch_salesPrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        Batch_salesPrice = 0
        check_EnableProductBatchWise = False
        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
            check_EnableProductBatchWise = GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
            if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
                    batch_ins = Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).last()
                    Batch_salesPrice = batch_ins.SalesPrice
                else:
                    Batch_salesPrice = PriceList.objects.get(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, DefaultUnit=True).SalesPrice
            else:
                Batch_salesPrice = PriceList.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, DefaultUnit=True).SalesPrice
        else:
            Batch_salesPrice = PriceList.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, DefaultUnit=True).SalesPrice
        return converted_float(Batch_salesPrice)

    def get_UnitName(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        UnitID = PriceList.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).UnitID
        UnitName = Unit.objects.get(
            CompanyID=CompanyID, UnitID=UnitID).UnitName
        return UnitName

    def get_ExcessOrShortage(self, instances):
        ExcessOrShortage = 0
        return ExcessOrShortage

    def get_StockAdjustment(self, instances):
        StockAdjustment = 0
        return StockAdjustment


class BarCodeSearchSerializer(serializers.ModelSerializer):

    PriceListID = serializers.SerializerMethodField()
    UnitPrice = serializers.SerializerMethodField()
    BatchCode = serializers.SerializerMethodField()
    DefaultUnitName = serializers.SerializerMethodField()
    DefaultUnitID = serializers.SerializerMethodField()
    DefaultSalesPrice = serializers.SerializerMethodField()
    DefaultPurchasePrice = serializers.SerializerMethodField()
    GST_SalesTax = serializers.SerializerMethodField()
    Tax3_SalesTax = serializers.SerializerMethodField()
    Tax2_SalesTax = serializers.SerializerMethodField()
    Tax1_SalesTax = serializers.SerializerMethodField()
    SalesTax = serializers.SerializerMethodField()
    Stock = serializers.SerializerMethodField()
    is_GST_inclusive = serializers.SerializerMethodField()
    is_VAT_inclusive = serializers.SerializerMethodField()
    is_TAX1_inclusive = serializers.SerializerMethodField()
    is_TAX2_inclusive = serializers.SerializerMethodField()
    is_TAX3_inclusive = serializers.SerializerMethodField()
    GST_TaxName = serializers.SerializerMethodField()
    VAT_TaxName = serializers.SerializerMethodField()
    GST_ID = serializers.SerializerMethodField()
    BatchList = serializers.SerializerMethodField()
    MultiFactor = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'ProductID', 'BranchID', 'DefaultUnitName', 'DefaultUnitID', 'DefaultSalesPrice', 'ProductCode', 'HSNCode',
                  'ProductName', 'PriceListID', 'UnitPrice', 'Stock', 'BatchCode', 'DefaultPurchasePrice', 'is_inclusive',
                  'GST_SalesTax', 'Tax3_SalesTax', 'Tax2_SalesTax', 'Tax1_SalesTax', 'SalesTax',  'VatID','BatchList',
                  'is_GST_inclusive', 'is_VAT_inclusive', 'is_TAX1_inclusive', 'is_TAX2_inclusive', 'is_TAX3_inclusive', 'GST_TaxName', 'VAT_TaxName', 'GST_ID',
                  'MultiFactor')

    def get_GST_ID(self, instances):
        CompanyID = self.context.get("CompanyID")
        GST_ID = instances.GST
        return GST_ID

    def get_BatchList(self, instance):
        # check_EnableProductBatchWise = False
        CompanyID = self.context.get("CompanyID")
        # PriceRounding = int(self.context.get("PriceRounding"))
        BranchID = instance.BranchID
        ProductID = instance.ProductID
        # if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
        #     check_EnableProductBatchWise = GeneralSettings.objects.get(
        #         BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
        BatchList = []
        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
            batch_details = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
            batchList = Batch_ListSerializer(batch_details, many=True, context={
                "CompanyID": CompanyID})
            BatchList = batchList.data
        return BatchList
        

    def get_GST_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.GST
        BranchID = instances.BranchID
        GST_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            GST_TaxName = tax.TaxName

        return GST_TaxName

    def get_VAT_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        VAT_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            VAT_TaxName = tax.TaxName

        return VAT_TaxName

    def get_PriceListID(self, instances):
        CompanyID = self.context.get("CompanyID")
        BarCode = self.context.get("BarCode")
        BranchID = instances.BranchID
        ProductID = instances.ProductID
        check_EnableProductBatchWise = get_GeneralSettings(CompanyID,BranchID,"EnableProductBatchWise")
        if get_BranchSettings(CompanyID, "productsForAllBranches"):
            pricelist_list = PriceList.objects.filter(
                CompanyID=CompanyID)
        else:
            pricelist_list = PriceList.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
        PriceListID = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).PriceListID
        if check_EnableProductBatchWise:
            if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BarCode).exists():
                batch_ins = Batch.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, BatchCode=BarCode)
                PriceListID = batch_ins.PriceListID
        else:
            if pricelist_list.filter(Barcode=BarCode).exists():
                PriceListID = pricelist_list.filter(
                    Barcode=BarCode).first().PriceListID
                
        return PriceListID
    

    def get_MultiFactor(self, instances):
        CompanyID = self.context.get("CompanyID")
        BarCode = self.context.get("BarCode")
        BranchID = instances.BranchID
        ProductID = instances.ProductID
        check_EnableProductBatchWise = get_GeneralSettings(CompanyID,BranchID,"EnableProductBatchWise")
        if get_BranchSettings(CompanyID, "productsForAllBranches"):
            pricelist_list = PriceList.objects.filter(
                CompanyID=CompanyID)
        else:
            pricelist_list = PriceList.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
        MultiFactor = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).MultiFactor
        if check_EnableProductBatchWise:
            if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BarCode).exists():
                batch_ins = Batch.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, BatchCode=BarCode)
                batch_pricelistID = batch_ins.PriceListID
                MultiFactor = PriceList.objects.get(
                    CompanyID=CompanyID, PriceListID=batch_pricelistID).MultiFactor
        else:
            if pricelist_list.filter(Barcode=BarCode).exists():
                MultiFactor = pricelist_list.filter(
                    Barcode=BarCode).first().MultiFactor
                
        return MultiFactor

    def get_UnitPrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        Barcode = self.context.get("Barcode")
        BranchID = instances.BranchID
        ProductID = instances.ProductID
        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=Barcode).exists():
            UnitPrice = Batch.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, BatchCode=Barcode).SalesPrice

        else:
            UnitPrice = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).PurchasePrice
        return UnitPrice

    def get_DefaultUnitID(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        DefaultUnitID = 0
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            DefaultUnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).PriceListID
            # DefaultUnitID = unitInstance.PriceListID
        return DefaultUnitID

    def get_is_TAX1_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax1 = instances.Tax1
        BranchID = instances.BranchID
        Inclusive = False
        if Tax1:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax1).Inclusive
        return Inclusive

    def get_is_TAX2_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax2 = instances.Tax2
        BranchID = instances.BranchID
        Inclusive = False
        if Tax2:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax2).Inclusive
        return Inclusive

    def get_is_TAX3_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax3 = instances.Tax3
        BranchID = instances.BranchID
        Inclusive = False
        if Tax3:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax3).Inclusive
        return Inclusive

    def get_is_GST_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        GST = instances.GST
        BranchID = instances.BranchID
        Inclusive = False
        if GST:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=GST).Inclusive
        return Inclusive

    def get_is_VAT_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        VatID = instances.VatID
        BranchID = instances.BranchID
        Inclusive = False
        if VatID:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=VatID).Inclusive
        return Inclusive

    def get_Stock(self, instances):
        CompanyID = self.context.get("CompanyID")
        BarCode = self.context.get("BarCode")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        Stock = 0
        # check_EnableProductBatchWise = False
        # if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
        #     check_EnableProductBatchWise = GeneralSettings.objects.get(
        #         BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
        check_EnableProductBatchWise = get_GeneralSettings(CompanyID,BranchID,"EnableProductBatchWise")
        if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
            if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BarCode).exists():
                batch_ins = Batch.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, BatchCode=BarCode)

                batch_pricelistID = batch_ins.PriceListID
                batch_MultiFactor = PriceList.objects.get(
                    CompanyID=CompanyID, PriceListID=batch_pricelistID).MultiFactor
                StockIn = batch_ins.StockIn
                StockOut = batch_ins.StockOut
                # StockIn = converted_float(btach_StockIn) / converted_float(batch_MultiFactor)
                # StockOut = converted_float(btach_StockOut) / converted_float(batch_MultiFactor)
                Stock = converted_float(StockIn) - \
                    converted_float(StockOut)
            else:
                if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductCode=BarCode).exists():
                    product_instance = Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductCode=BarCode).order_by('ProductID').first()
                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=product_instance.ProductID).exists():
                        batch_ins = Batch.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, ProductID=product_instance.ProductID).order_by('BatchCode').first()
                        batch_pricelistID = batch_ins.PriceListID
                        batch_MultiFactor = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=batch_pricelistID).MultiFactor
                        StockIn = batch_ins.StockIn
                        StockOut = batch_ins.StockOut
                        # StockIn = converted_float(btach_StockIn) / converted_float(batch_MultiFactor)
                        # StockOut = converted_float(btach_StockOut) / converted_float(batch_MultiFactor)
                        Stock = converted_float(StockIn) - \
                            converted_float(StockOut)
                    
        else:
            if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID):
                stock_ins = StockPosting.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                total_stockIN = 0
                total_stockOUT = 0
                for s in stock_ins:
                    total_stockIN += converted_float(s.QtyIn)
                    total_stockOUT += converted_float(s.QtyOut)

                Stock = converted_float(total_stockIN) - converted_float(total_stockOUT)

        return Stock

    def get_SalesTax(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        SalesTax = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            if SalesTax:
                SalesTax = round(SalesTax, int(PriceRounding))
            else:
                SalesTax = 0
        return str(SalesTax)

    def get_GST_SalesTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.GST
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            if SalesTax:
                GST_SalesTax = round(SalesTax, int(PriceRounding))
            else:
                GST_SalesTax = 0
            return str(GST_SalesTax)
        else:
            return "0"

    def get_Tax3_SalesTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax3
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            if SalesTax:
                Tax3_SalesTax = round(SalesTax, int(PriceRounding))
            else:
                Tax3_SalesTax = 0
            return str(Tax3_SalesTax)
        else:
            return "0"

    def get_Tax2_SalesTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax2
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            if SalesTax:
                Tax2_SalesTax = round(SalesTax, int(PriceRounding))
            else:
                Tax2_SalesTax = 0
            return str(Tax2_SalesTax)
        else:
            return "0"

    def get_Tax1_SalesTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax1
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            if SalesTax:
                Tax1_SalesTax = round(SalesTax, int(PriceRounding))
            else:
                Tax1_SalesTax = 0
            return str(Tax1_SalesTax)
        else:
            return "0"

    def get_DefaultUnitName(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        UnitID = 0
        DefaultUnitName = ""
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).UnitID
            DefaultUnitName = Unit.objects.get(
                UnitID=UnitID, CompanyID=CompanyID).UnitName

        return DefaultUnitName

    def get_DefaultPurchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            DefaultPurchasePrice = unitInstance.PurchasePrice
        else:
            DefaultPurchasePrice = 0

        return DefaultPurchasePrice

    def get_DefaultSalesPrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            get_DefaultSalesPrice = unitInstance.SalesPrice
        else:
            get_DefaultSalesPrice = 0

        return get_DefaultSalesPrice


    def get_BatchCode(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        BatchCode = 0
        check_EnableProductBatchWise = False
        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
            check_EnableProductBatchWise = GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
            if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
                    Batch_ins = Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).first()
                    BatchCode = Batch_ins.BatchCode

        return BatchCode


class UploadSerializer(serializers.Serializer):
    CompanyID = serializers.CharField(max_length=200)
    CreatedUserID = serializers.CharField(max_length=200)
    file = serializers.FileField()


class ProductSearchShortcutSerializer(serializers.ModelSerializer):
    BrandName = serializers.SerializerMethodField()
    ProductGroupName = serializers.SerializerMethodField()
    PriceListDetails = serializers.SerializerMethodField()
    TaxName = serializers.SerializerMethodField()
    StockMinimum = serializers.SerializerMethodField()
    StockReOrder = serializers.SerializerMethodField()
    StockMaximum = serializers.SerializerMethodField()
    PurchaseTax = serializers.SerializerMethodField()
    SalesTax = serializers.SerializerMethodField()
    GST_PurchaseTax = serializers.SerializerMethodField()
    GST_SalesTax = serializers.SerializerMethodField()
    Tax1_PurchaseTax = serializers.SerializerMethodField()
    Tax1_SalesTax = serializers.SerializerMethodField()
    Tax2_PurchaseTax = serializers.SerializerMethodField()
    Tax2_SalesTax = serializers.SerializerMethodField()
    Tax3_PurchaseTax = serializers.SerializerMethodField()
    Tax3_SalesTax = serializers.SerializerMethodField()
    GST_TaxName = serializers.SerializerMethodField()
    VAT_TaxName = serializers.SerializerMethodField()
    Tax1_TaxName = serializers.SerializerMethodField()
    Tax2_TaxName = serializers.SerializerMethodField()
    Tax3_TaxName = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()
    PurchasePrice = serializers.SerializerMethodField()
    SalesPrice = serializers.SerializerMethodField()
    MRP = serializers.SerializerMethodField()
    DefaultUnitID = serializers.SerializerMethodField()
    DefaultUnitName = serializers.SerializerMethodField()
    DefaultSalesPrice = serializers.SerializerMethodField()
    DefaultPurchasePrice = serializers.SerializerMethodField()
    DefaultMRP = serializers.SerializerMethodField()
    is_VAT_inclusive = serializers.SerializerMethodField()
    is_GST_inclusive = serializers.SerializerMethodField()
    is_TAX1_inclusive = serializers.SerializerMethodField()
    is_TAX2_inclusive = serializers.SerializerMethodField()
    is_TAX3_inclusive = serializers.SerializerMethodField()
    Tax1 = serializers.SerializerMethodField()
    Tax2 = serializers.SerializerMethodField()
    Tax3 = serializers.SerializerMethodField()
    GST = serializers.SerializerMethodField()
    VatID = serializers.SerializerMethodField()
    PLUNo = serializers.SerializerMethodField()
    DefUntID = serializers.SerializerMethodField()
    DefBarcode = serializers.SerializerMethodField()
    Quantity = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'ProductID', 'BranchID', 'ProductCode', 'ProductName', 'DisplayName', 'Description', 'ProductGroupID',
                  'BrandID', 'InventoryType', 'VatID', 'StockMinimum', 'MinimumSalesPrice', 'StockReOrder', 'StockMaximum', 'DefUntID', 'DefBarcode',
                  'MarginPercent', 'ProductImage', 'Active', 'IsRawMaterial', 'IsWeighingScale', 'WeighingCalcType', 'PLUNo',
                  'IsFavourite', 'CreatedDate', 'CreatedUserID', 'Action', 'GST', 'GST_PurchaseTax', 'GST_SalesTax', 'SalesTax', 'Tax1', 'Tax1_PurchaseTax', 'Tax1_SalesTax',
                  'Tax2', 'Tax2_PurchaseTax', 'Tax2_SalesTax', 'Tax3', 'Tax3_PurchaseTax', 'Tax3_SalesTax', 'BrandName', 'TaxName', 'ProductGroupName', 'PurchaseTax', 'SalesTax',
                  'IsFinishedProduct', 'IsSales', 'IsPurchase', 'PurchasePrice', 'SalesPrice', 'MRP', 'GST_TaxName', 'VAT_TaxName', 'UnitName', 'Tax1_TaxName', 'Tax2_TaxName', 'Tax3_TaxName',
                  'DefaultUnitID', 'DefaultUnitName', 'DefaultSalesPrice', 'DefaultPurchasePrice',
                  'is_VAT_inclusive', 'is_GST_inclusive', 'is_TAX1_inclusive', 'is_TAX2_inclusive', 'is_TAX3_inclusive', 'PriceListDetails', 'DefaultMRP', "IsKFC", "HSNCode", "Quantity")

    def get_Quantity(self, instances):
        CompanyID = self.context.get("CompanyID")
        WarehouseID = self.context.get("WarehouseID")
        TotalQtyIn = 0
        TotalQtyOut = 0
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if StockPosting.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, WareHouseID=WarehouseID).exists():
            stockpostIns = StockPosting.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, WareHouseID=WarehouseID)
            for i in stockpostIns:
                TotalQtyIn += i.QtyIn
                TotalQtyOut += i.QtyOut

        Quantity = converted_float(TotalQtyIn) - converted_float(TotalQtyOut)
        return converted_float(Quantity)

    def get_BrandName(self, instances):
        CompanyID = self.context.get("CompanyID")

        BrandID = instances.BrandID
        BranchID = instances.BranchID
        brand = Brand.objects.filter(
            CompanyID=CompanyID, BrandID=BrandID).first()
        BrandName = brand.BrandName

        return BrandName

    def get_Tax1(self, instances):
        Tax1 = instances.Tax1
        if not Tax1:
            Tax1 = 1
        return Tax1

    def get_Tax2(self, instances):
        Tax2 = instances.Tax2
        if not Tax2:
            Tax2 = 1
        return Tax2

    def get_Tax3(self, instances):
        Tax3 = instances.Tax3
        if not Tax3:
            Tax3 = 1
        return Tax3

    def get_GST(self, instances):
        GST = instances.GST
        if not GST:
            GST = 1
        return GST

    def get_VatID(self, instances):
        VatID = instances.VatID

        if not VatID:
            VatID = 1
        return VatID

    def get_PLUNo(self, instances):
        PLUNo = instances.PLUNo
        if not PLUNo:
            PLUNo = 1
        return PLUNo

    def get_is_VAT_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        VatID = instances.VatID
        BranchID = instances.BranchID
        Inclusive = False
        if VatID:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=VatID).Inclusive
        return Inclusive

    def get_is_GST_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        GST = instances.GST
        BranchID = instances.BranchID
        Inclusive = False
        if GST:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=GST).Inclusive
        return Inclusive

    def get_is_TAX1_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax1 = instances.Tax1
        BranchID = instances.BranchID
        Inclusive = False
        if Tax1:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax1).Inclusive
        return Inclusive

    def get_is_TAX2_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax2 = instances.Tax2
        BranchID = instances.BranchID
        Inclusive = False
        if Tax2:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax2).Inclusive
        return Inclusive

    def get_is_TAX3_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax3 = instances.Tax3
        BranchID = instances.BranchID
        Inclusive = False
        if Tax3:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax3).Inclusive
        return Inclusive

    def get_DefaultUnitID(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        DefaultUnitID = ""
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            DefaultUnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).PriceListID
        # DefaultUnitID = unitInstance.PriceListID
        return DefaultUnitID

    def get_DefUntID(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        DefUntID = ""
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            DefUntID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).UnitID
        # DefUntID = unitInstance.PriceListID
        return DefUntID

    def get_DefBarcode(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        DefBarcode = ""
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            DefBarcode = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).Barcode
        # DefBarcode = unitInstance.PriceListID
        return DefBarcode

    def get_DefaultUnitName(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        DefaultUnitName = ""
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).UnitID
            DefaultUnitName = Unit.objects.get(
                UnitID=UnitID, CompanyID=CompanyID).UnitName

        return DefaultUnitName

    def get_DefaultSalesPrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            get_DefaultSalesPrice = unitInstance.SalesPrice
        else:
            get_DefaultSalesPrice = 0

        return get_DefaultSalesPrice

    def get_DefaultMRP(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            get_DefaultMRP = unitInstance.MRP
        else:
            get_DefaultMRP = 0

        return get_DefaultMRP

    def get_DefaultPurchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            DefaultPurchasePrice = unitInstance.PurchasePrice
        else:
            DefaultPurchasePrice = 0

        return DefaultPurchasePrice

    def get_UnitName(self, instances):
        CompanyID = self.context.get("CompanyID")

        ProductID = instances.ProductID
        BranchID = instances.BranchID
        UnitName = ""
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            UnitID = priceList.UnitID
            UnitName = Unit.objects.get(
                CompanyID=CompanyID, UnitID=UnitID).UnitName

        return UnitName

    def get_PurchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            PurchasePrice = priceList.PurchasePrice
            PurchasePrice = round(PurchasePrice, int(PriceRounding))
        else:
            PurchasePrice = 0
        return PurchasePrice

    def get_SalesPrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            SalesPrice = priceList.SalesPrice
            # SalesPrice = round(SalesPrice, int(PriceRounding))
        else:
            SalesPrice = 0
        return SalesPrice

    def get_MRP(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            MRP = priceList.MRP
            # MRP = round(MRP, int(PriceRounding))
        else:
            MRP = 0
        return MRP

    def get_ProductGroupName(self, instances):
        CompanyID = self.context.get("CompanyID")

        ProductGroupID = instances.ProductGroupID
        BranchID = instances.BranchID
        product_group = ProductGroup.objects.filter(
            CompanyID=CompanyID, ProductGroupID=ProductGroupID).first()
        ProductGroupName = product_group.GroupName

        return ProductGroupName

    def get_PriceListDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        price_list = PriceList.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID)
        serialized = PriceListRestSerializer(price_list, many=True, context={
                                             "CompanyID": CompanyID, "PriceRounding": PriceRounding})

        return serialized.data

    def get_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")
        TaxName = ""
        TaxID = 1
        if instances.VatID != 1:
            TaxID = instances.VatID
        elif instances.GST != 1:
            TaxID = instances.GST
        elif instances.Tax1 != 1:
            TaxID = instances.Tax1
        elif instances.Tax2 != 1:
            TaxID = instances.Tax2
        elif instances.Tax3 != 1:
            TaxID = instances.Tax3
        BranchID = instances.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            TaxName = tax.TaxName

        return TaxName

    def get_GST_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.GST
        BranchID = instances.BranchID
        GST_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            GST_TaxName = tax.TaxName

        return GST_TaxName

    def get_VAT_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        VAT_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            VAT_TaxName = tax.TaxName

        return VAT_TaxName

    def get_Tax1_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.Tax1
        BranchID = instances.BranchID
        Tax1_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            Tax1_TaxName = tax.TaxName

        return Tax1_TaxName

    def get_Tax2_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.Tax2
        BranchID = instances.BranchID
        Tax2_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            Tax2_TaxName = tax.TaxName

        return Tax2_TaxName

    def get_Tax3_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.Tax3
        BranchID = instances.BranchID
        Tax3_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            Tax3_TaxName = tax.TaxName

        return Tax3_TaxName

    def get_PurchaseTax(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        PurchaseTax = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            PurchaseTax = tax.PurchaseTax
            # if PurchaseTax:
            #     PurchaseTax = round(PurchaseTax, int(PriceRounding))
            # else:
            #     PurchaseTax = 0
        return str(PurchaseTax)

    def get_SalesTax(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        SalesTax = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            # if SalesTax:
            #     SalesTax = round(SalesTax, int(PriceRounding))
            # else:
            #     SalesTax = 0
        return str(SalesTax)

    def get_StockMinimum(self, instances):
        PriceRounding = self.context.get("PriceRounding")

        StockMinimum = instances.StockMinimum
        # if StockMinimum:
        #     StockMinimum = round(StockMinimum, int(PriceRounding))
        # else:
        #     StockMinimum = 0

        return str(StockMinimum)

    def get_StockMaximum(self, instances):

        PriceRounding = self.context.get("PriceRounding")
        StockMaximum = instances.StockMaximum

        # if StockMaximum:
        #     StockMaximum = round(StockMaximum, int(PriceRounding))
        # else:
        #     StockMaximum = 0

        return str(StockMaximum)

    def get_StockReOrder(self, instances):

        PriceRounding = self.context.get("PriceRounding")
        StockReOrder = instances.StockReOrder
        # if StockReOrder:
        #     StockReOrder = round(StockReOrder, int(PriceRounding))
        # else:
        #     StockReOrder = 0
        return str(StockReOrder)

    def get_GST_PurchaseTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.GST
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            PurchaseTax = tax.PurchaseTax
            # if PurchaseTax:
            #     GST_PurchaseTax = round(PurchaseTax, int(PriceRounding))
            # else:
            #     GST_PurchaseTax = 0
            return str(PurchaseTax)
        else:
            return "0"

    def get_GST_SalesTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.GST
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            # if SalesTax:
            #     GST_SalesTax = round(SalesTax, int(PriceRounding))
            # else:
            #     GST_SalesTax = 0
            return str(SalesTax)
        else:
            return "0"

    def get_Tax1_PurchaseTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax1
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            PurchaseTax = tax.PurchaseTax
            # if PurchaseTax:
            #     Tax1_PurchaseTax = round(PurchaseTax, int(PriceRounding))
            # else:
            #     Tax1_PurchaseTax = 0
            return str(PurchaseTax)
        else:
            return "0"

    def get_Tax1_SalesTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax1
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            # if SalesTax:
            #     Tax1_SalesTax = round(SalesTax, int(PriceRounding))
            # else:
            #     Tax1_SalesTax = 0
            return str(SalesTax)
        else:
            return "0"

    def get_Tax2_PurchaseTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax2
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            PurchaseTax = tax.PurchaseTax
            # if PurchaseTax:
            #     Tax2_PurchaseTax = round(PurchaseTax, int(PriceRounding))
            # else:
            #     Tax2_PurchaseTax = 0
            return str(PurchaseTax)
        else:
            return "0"

    def get_Tax2_SalesTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax2
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            # if SalesTax:
            #     Tax2_SalesTax = round(SalesTax, int(PriceRounding))
            # else:
            #     Tax2_SalesTax = 0
            return str(SalesTax)
        else:
            return "0"

    def get_Tax3_PurchaseTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax3
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            PurchaseTax = tax.PurchaseTax
            # if PurchaseTax:
            #     Tax3_PurchaseTax = round(PurchaseTax, int(PriceRounding))
            # else:
            #     Tax3_PurchaseTax = 0
            return str(PurchaseTax)
        else:
            return "0"

    def get_Tax3_SalesTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax3
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            # if SalesTax:
            #     Tax3_SalesTax = round(SalesTax, int(PriceRounding))
            # else:
            #     Tax3_SalesTax = 0
            return str(SalesTax)
        else:
            return "0"


# reportssssssssssss
class ListSerializerforReport(serializers.Serializer):

    BranchID = serializers.IntegerField()
    FromDate = serializers.DateField()
    ToDate = serializers.DateField()


class StockSerializer(serializers.ModelSerializer):

    AutoBarcode = serializers.SerializerMethodField()
    PurchasePrice = serializers.SerializerMethodField()
    SalesPrice = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()
    BaseUnitName = serializers.SerializerMethodField()
    is_BasicUnit = serializers.SerializerMethodField()
    MultiFactor = serializers.SerializerMethodField()
    WareHouseName = serializers.SerializerMethodField()
    Qty = serializers.SerializerMethodField()
    Cost = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'AutoBarcode', 'ProductID', 'ProductName', 'WareHouseName', 'PurchasePrice',
                  'SalesPrice', 'UnitName', 'BaseUnitName', 'is_BasicUnit', 'MultiFactor', 'Qty', 'Cost', 'ProductCode')

    # def get_OpeningStock(self, instance):
    #     CompanyID = self.context.get("CompanyID")
    #     WareHouseID = self.context.get("WareHouseID")
    #     ToDate = self.context.get("ToDate")
    #     FromDate = self.context.get("FromDate")
    #     ProductID = instance.ProductID
    #     BranchID = instance.BranchID
    #     if Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, InventoryType="StockItem").exists():
    #         if StockPosting.objects.filter(ProductID=ProductID, Date__lt=FromDate, CompanyID=CompanyID).exists():
    #             stock_instance = StockPosting.objects.filter(
    #                 ProductID=ProductID, Date__lt=FromDate, CompanyID=CompanyID)

    #     return Cost

    def get_Cost(self, instance):

        CompanyID = self.context.get("CompanyID")
        WareHouseID = self.context.get("WareHouseID")
        ToDate = self.context.get("ToDate")

        ProductID = instance.ProductID
        BranchID = instance.BranchID

        Cost = 0

        if StockPosting.objects.filter(ProductID=ProductID, CompanyID=CompanyID, WareHouseID=WareHouseID, QtyIn__gt=0, Date__lte=ToDate).exists():
            stock_ins = StockPosting.objects.filter(
                ProductID=ProductID, CompanyID=CompanyID, WareHouseID=WareHouseID, QtyIn__gt=0, Date__lte=ToDate)
            TotalQtyInRate = 0
            TotalQtyIn = 0
            for s in stock_ins:
                QtyInRate = converted_float(s.QtyIn) * converted_float(s.Rate)
                TotalQtyIn += s.QtyIn
                TotalQtyInRate += QtyInRate

            Cost = converted_float(TotalQtyInRate) / converted_float(TotalQtyIn)

        return Cost

    def get_Qty(self, instance):

        CompanyID = self.context.get("CompanyID")
        WareHouseID = self.context.get("WareHouseID")
        ToDate = self.context.get("ToDate")

        ProductID = instance.ProductID
        BranchID = instance.BranchID

        Qty = 0

        if StockPosting.objects.filter(ProductID=ProductID, CompanyID=CompanyID, WareHouseID=WareHouseID, Date__lte=ToDate).exists():
            stock_ins = StockPosting.objects.filter(
                ProductID=ProductID, CompanyID=CompanyID, WareHouseID=WareHouseID, Date__lte=ToDate)
            TotalQtyIn = 0
            TotalQtyOut = 0
            for s in stock_ins:
                TotalQtyIn += s.QtyIn
                TotalQtyOut += s.QtyOut

            Qty = converted_float(TotalQtyIn) - converted_float(TotalQtyOut)

        return Qty

    def get_WareHouseName(self, instance):

        CompanyID = self.context.get("CompanyID")
        WareHouseID = self.context.get("WareHouseID")

        BranchID = instance.BranchID
        WareHouseName = ""
        if Warehouse.objects.filter(CompanyID=CompanyID, WarehouseID=WareHouseID, BranchID=BranchID).exists():
            WareHouseName = Warehouse.objects.get(
                CompanyID=CompanyID, WarehouseID=WareHouseID, BranchID=BranchID).WarehouseName

        return WareHouseName

    def get_AutoBarcode(self, final_instance):

        CompanyID = self.context.get("CompanyID")
        ProductID = final_instance.ProductID
        BranchID = final_instance.BranchID
        AutoBarcode = PriceList.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).AutoBarcode

        return AutoBarcode

    def get_PurchasePrice(self, final_instance):

        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = final_instance.ProductID
        BranchID = final_instance.BranchID
        PurchasePrice = PriceList.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).PurchasePrice

        return converted_float(round(PurchasePrice, PriceRounding))

    def get_SalesPrice(self, final_instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = final_instance.ProductID
        BranchID = final_instance.BranchID
        SalesPrice = PriceList.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).SalesPrice

        return converted_float(round(SalesPrice, PriceRounding))

    def get_UnitName(self, final_instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = final_instance.ProductID
        BranchID = final_instance.BranchID
        UnitName = ""
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, UnitInReports=True).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, UnitInReports=True).UnitID
            UnitName = Unit.objects.get(
                CompanyID=CompanyID, UnitID=UnitID).UnitName
        else:
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).UnitID
            UnitName = Unit.objects.get(
                CompanyID=CompanyID, UnitID=UnitID).UnitName

        return UnitName

    def get_BaseUnitName(self, final_instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = final_instance.ProductID
        BranchID = final_instance.BranchID
        BaseUnitName = ""
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).UnitID
            BaseUnitName = Unit.objects.get(
                CompanyID=CompanyID, UnitID=UnitID).UnitName

        return BaseUnitName

    def get_is_BasicUnit(self, final_instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = final_instance.ProductID
        BranchID = final_instance.BranchID

        is_BasicUnit = False
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, UnitInReports=True, DefaultUnit=True).exists():

            is_BasicUnit = True

        return is_BasicUnit

    def get_MultiFactor(self, final_instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = final_instance.ProductID
        BranchID = final_instance.BranchID
        MultiFactor = 1
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, UnitInReports=True, DefaultUnit=False).exists():
            MultiFactor = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, UnitInReports=True, DefaultUnit=False).MultiFactor
        return converted_float(MultiFactor)


class BatchCodeSearchSerializer(serializers.ModelSerializer):
    PriceListID = serializers.SerializerMethodField()
    UnitPrice = serializers.SerializerMethodField()
    GST_SalesTax = serializers.SerializerMethodField()
    SalesTax = serializers.SerializerMethodField()
    Stock = serializers.SerializerMethodField()
    is_GST_inclusive = serializers.SerializerMethodField()
    is_VAT_inclusive = serializers.SerializerMethodField()
    SalesPrice = serializers.SerializerMethodField()
    PurchasePrice = serializers.SerializerMethodField()
    BarCode = serializers.SerializerMethodField()
    MRP = serializers.SerializerMethodField()
    SalesPrice1 = serializers.SerializerMethodField()
    SalesPrice2 = serializers.SerializerMethodField()
    SalesPrice3 = serializers.SerializerMethodField()
    UnitList = serializers.SerializerMethodField()
    BatchList = serializers.SerializerMethodField()
    MultiFactor = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'ProductID', 'BranchID', 'ProductCode', 'HSNCode', 'ProductName', 'PriceListID', 'UnitPrice',
                  'Stock', 'is_inclusive', 'GST_SalesTax', 'SalesTax', 'VatID', 'is_GST_inclusive', 'is_VAT_inclusive', 'GST',
                  'SalesPrice', 'PurchasePrice', 'BarCode', 'MRP', 'MinimumSalesPrice', 'SalesPrice1', 'SalesPrice2', 'SalesPrice3',
                  'UnitList', 'BatchList','MultiFactor')

    def get_PriceListID(self, instances):
        CompanyID = self.context.get("CompanyID")
        BatchCode = self.context.get("BatchCode")
        BranchID = instances.BranchID
        ProductID = instances.ProductID
        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
            PriceListID = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).first().PriceListID
        else:
            PriceListID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).PriceListID
        return PriceListID
    
    
    def get_MultiFactor(self, instances):
        CompanyID = self.context.get("CompanyID")
        BatchCode = self.context.get("BatchCode")
        BranchID = instances.BranchID
        ProductID = instances.ProductID
        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
            PriceListID = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).first().PriceListID
            MultiFactor = PriceList.objects.filter(CompanyID=CompanyID,PriceListID=PriceListID).first().MultiFactor
        else:
            MultiFactor = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).MultiFactor
        return MultiFactor

    def get_Stock(self, instances):
        CompanyID = self.context.get("CompanyID")
        BatchCode = self.context.get("BatchCode")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        Stock = 0
        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
            Batch_ins = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).first()
            batch_pricelistID = Batch_ins.PriceListID
            batch_MultiFactor = PriceList.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, PriceListID=batch_pricelistID).MultiFactor
            batch_StockIn = Batch_ins.StockIn
            batch_StockOut = Batch_ins.StockOut
            StockIn = converted_float(batch_StockIn)
            StockOut = converted_float(batch_StockOut)
            # StockIn = converted_float(batch_StockIn) / converted_float(batch_MultiFactor)
            # StockOut = converted_float(batch_StockOut) / converted_float(batch_MultiFactor)
            Stock = converted_float(StockIn) - \
                converted_float(StockOut)

        return Stock

    def get_UnitPrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        BatchCode = self.context.get("BatchCode")
        BranchID = instances.BranchID
        ProductID = instances.ProductID
        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
            UnitPrice = Batch.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).SalesPrice

        else:
            UnitPrice = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).SalesPrice
        return UnitPrice

    def get_is_GST_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        GST = instances.GST
        BranchID = instances.BranchID
        Inclusive = False
        if GST:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=GST).Inclusive
        return Inclusive

    def get_is_VAT_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        VatID = instances.VatID
        BranchID = instances.BranchID
        Inclusive = False
        if VatID:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=VatID).Inclusive
        return Inclusive

    def get_SalesTax(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        SalesTax = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            if SalesTax:
                SalesTax = round(SalesTax, int(PriceRounding))
            else:
                SalesTax = 0
        return str(SalesTax)

    def get_GST_SalesTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.GST
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            if SalesTax:
                GST_SalesTax = round(SalesTax, int(PriceRounding))
            else:
                GST_SalesTax = 0
            return str(GST_SalesTax)
        else:
            return "0"

    def get_SalesPrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        BatchCode = self.context.get("BatchCode")
        try:
            LedgerID = self.context.get("LedgerID")
        except:
            LedgerID = 0

        BranchID = instances.BranchID
        ProductID = instances.ProductID
        SalesPrice = 0
        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
            SalesPrice = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).first().SalesPrice

        SalesPrice = get_LastSalesPrice_PurchasePrice("Sales",SalesPrice,CompanyID,BranchID,LedgerID,ProductID)

        return converted_float(SalesPrice)

    def get_PurchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        BatchCode = self.context.get("BatchCode")
        BranchID = instances.BranchID
        ProductID = instances.ProductID
        try:
            LedgerID = self.context.get("LedgerID")
        except:
            LedgerID = 0
        PurchasePrice = 0
        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
            PurchasePrice = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).first().PurchasePrice
        PurchasePrice = get_LastSalesPrice_PurchasePrice("Purchase",PurchasePrice,CompanyID,BranchID,LedgerID,ProductID)

        return converted_float(PurchasePrice)

    def get_BarCode(self, instances):
        CompanyID = self.context.get("CompanyID")
        BatchCode = self.context.get("BatchCode")
        BranchID = instances.BranchID
        BarCode = ""
        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
            PriceListID = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).first().PriceListID
            BarCode = PriceList.objects.filter(
                CompanyID=CompanyID, PriceListID=PriceListID).first().Barcode

        return BarCode

    def get_MRP(self, instances):
        CompanyID = self.context.get("CompanyID")
        BatchCode = self.context.get("BatchCode")
        BranchID = instances.BranchID
        MRP = ""
        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
            PriceListID = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).first().PriceListID
            MRP = PriceList.objects.filter(
                CompanyID=CompanyID, PriceListID=PriceListID).first().MRP

        return MRP

    def get_SalesPrice1(self, instances):
        CompanyID = self.context.get("CompanyID")
        BatchCode = self.context.get("BatchCode")
        BranchID = instances.BranchID
        SalesPrice1 = ""
        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
            PriceListID = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).first().PriceListID
            SalesPrice1 = PriceList.objects.filter(
                CompanyID=CompanyID, PriceListID=PriceListID).first().SalesPrice1

        return SalesPrice1

    def get_SalesPrice2(self, instances):
        CompanyID = self.context.get("CompanyID")
        BatchCode = self.context.get("BatchCode")
        BranchID = instances.BranchID
        SalesPrice2 = ""
        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
            PriceListID = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).first().PriceListID
            SalesPrice2 = PriceList.objects.filter(
                CompanyID=CompanyID, PriceListID=PriceListID).first().SalesPrice2

        return SalesPrice2

    def get_SalesPrice3(self, instances):
        CompanyID = self.context.get("CompanyID")
        BatchCode = self.context.get("BatchCode")
        BranchID = instances.BranchID
        SalesPrice3 = ""
        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
            PriceListID = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).first().PriceListID
            SalesPrice3 = PriceList.objects.filter(
                CompanyID=CompanyID, PriceListID=PriceListID).first().SalesPrice3

        return SalesPrice3

    def get_UnitList(self, instance):
        UnitList = []
        CompanyID = self.context.get("CompanyID")
        # PriceRounding = int(self.context.get("PriceRounding"))
        BranchID = instance.BranchID
        ProductID = instance.ProductID
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID).exists():
            unit_details = PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID)
            UnitList = UnitListSerializer(unit_details, many=True, context={
                                          "CompanyID": CompanyID})
            UnitList = UnitList.data
        return UnitList

    def get_BatchList(self, instance):
        BatchList = []
        CompanyID = self.context.get("CompanyID")
        # PriceRounding = int(self.context.get("PriceRounding"))
        BranchID = instance.BranchID
        ProductID = instance.ProductID
        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
            batch_details = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).order_by('-CreatedDate')
            batchList = Batch_ListSerializer(batch_details, many=True, context={
                "CompanyID": CompanyID})
            BatchList = batchList.data
        return BatchList


class ProductsExcelSerializer(serializers.ModelSerializer):

    BrandName = serializers.SerializerMethodField()
    ProductGroupName = serializers.SerializerMethodField()
    PriceListDetails = serializers.SerializerMethodField()
    TaxName = serializers.SerializerMethodField()
    StockMinimum = serializers.SerializerMethodField()
    StockReOrder = serializers.SerializerMethodField()
    StockMaximum = serializers.SerializerMethodField()
    PurchaseTax = serializers.SerializerMethodField()
    SalesTax = serializers.SerializerMethodField()
    GST_PurchaseTax = serializers.SerializerMethodField()
    GST_SalesTax = serializers.SerializerMethodField()
    Tax1_PurchaseTax = serializers.SerializerMethodField()
    Tax1_SalesTax = serializers.SerializerMethodField()
    Tax2_PurchaseTax = serializers.SerializerMethodField()
    Tax2_SalesTax = serializers.SerializerMethodField()
    Tax3_PurchaseTax = serializers.SerializerMethodField()
    Tax3_SalesTax = serializers.SerializerMethodField()
    GST_TaxName = serializers.SerializerMethodField()
    VAT_TaxName = serializers.SerializerMethodField()
    Tax1_TaxName = serializers.SerializerMethodField()
    Tax2_TaxName = serializers.SerializerMethodField()
    Tax3_TaxName = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()
    PurchasePrice = serializers.SerializerMethodField()
    SalesPrice = serializers.SerializerMethodField()
    MRP = serializers.SerializerMethodField()
    DefaultUnitID = serializers.SerializerMethodField()
    DefaultUnitName = serializers.SerializerMethodField()
    DefaultSalesPrice = serializers.SerializerMethodField()
    DefaultSalesPrice1 = serializers.SerializerMethodField()
    DefaultSalesPrice2 = serializers.SerializerMethodField()
    DefaultSalesPrice3 = serializers.SerializerMethodField()
    DefaultPurchasePrice = serializers.SerializerMethodField()
    DefaultMRP = serializers.SerializerMethodField()
    is_VAT_inclusive = serializers.SerializerMethodField()
    is_GST_inclusive = serializers.SerializerMethodField()
    is_TAX1_inclusive = serializers.SerializerMethodField()
    is_TAX2_inclusive = serializers.SerializerMethodField()
    is_TAX3_inclusive = serializers.SerializerMethodField()
    Tax1 = serializers.SerializerMethodField()
    Tax2 = serializers.SerializerMethodField()
    Tax3 = serializers.SerializerMethodField()
    GST = serializers.SerializerMethodField()
    VatID = serializers.SerializerMethodField()
    PLUNo = serializers.SerializerMethodField()
    DefUntID = serializers.SerializerMethodField()
    DefBarcode = serializers.SerializerMethodField()
    Stock = serializers.SerializerMethodField()
    Check_positive_Stock = serializers.SerializerMethodField()
    ProductBarcodeList = serializers.SerializerMethodField()
    AutoBarcode = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'AutoBarcode', 'ProductID',  'is_Service', 'BranchID', 'ProductCode', 'ProductBarcodeList', 'ProductName', 'DisplayName', 'Description', 'ProductGroupID', 'is_Service',
                  'BrandID', 'InventoryType', 'VatID', 'StockMinimum', 'MinimumSalesPrice', 'StockReOrder', 'StockMaximum', 'DefUntID', 'DefBarcode', 'is_inclusive',
                  'MarginPercent', 'ProductImage', 'Active', 'IsRawMaterial', 'IsWeighingScale', 'WeighingCalcType', 'PLUNo', 'WarrantyType', 'Warranty',
                  'IsFavourite', 'CreatedDate', 'CreatedUserID', 'Action', 'GST', 'GST_PurchaseTax', 'GST_SalesTax', 'SalesTax', 'Tax1', 'Tax1_PurchaseTax', 'Tax1_SalesTax',
                  'Tax2', 'Tax2_PurchaseTax', 'Tax2_SalesTax', 'Tax3', 'Tax3_PurchaseTax', 'Tax3_SalesTax', 'BrandName', 'TaxName', 'ProductGroupName', 'PurchaseTax', 'SalesTax',
                  'IsFinishedProduct', 'IsSales', 'IsPurchase', 'PurchasePrice', 'SalesPrice', 'MRP', 'GST_TaxName', 'VAT_TaxName', 'UnitName', 'Tax1_TaxName', 'Tax2_TaxName', 'Tax3_TaxName',
                  'DefaultUnitID', 'DefaultUnitName', 'DefaultSalesPrice', 'DefaultSalesPrice1', 'DefaultSalesPrice2', 'DefaultSalesPrice3', 'DefaultPurchasePrice',
                  'is_VAT_inclusive', 'is_GST_inclusive', 'is_TAX1_inclusive', 'is_TAX2_inclusive', 'is_TAX3_inclusive', 'PriceListDetails', 'DefaultMRP', "IsKFC", "HSNCode", 'Stock', 'Check_positive_Stock')

    def get_AutoBarcode(self, instances):
        CompanyID = self.context.get("CompanyID")
        AutoBarcode = 0
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=instances.ProductID, DefaultUnit=True):
            AutoBarcode = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=instances.ProductID, DefaultUnit=True).AutoBarcode
        return AutoBarcode

    def get_ProductBarcodeList(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        product_barcode_list = ProductBarcode.objects.filter(
            CompanyID=CompanyID, ProductID=instances, BranchID=BranchID)
        serialized = ProductBarcodeListRestSerializer(product_barcode_list, many=True, context={
            "CompanyID": CompanyID, "PriceRounding": PriceRounding})
        data = serialized.data
        if not data:
            data = []

        return data

    def get_BrandName(self, instances):
        CompanyID = self.context.get("CompanyID")

        BrandID = instances.BrandID
        BranchID = instances.BranchID
        productsForAllBranches = get_BranchSettings(
            CompanyID, "productsForAllBranches")
        if productsForAllBranches:
            brand = Brand.objects.filter(
                CompanyID=CompanyID, BrandID=BrandID).first()
        else:
            brand = Brand.objects.get(
                CompanyID=CompanyID, BrandID=BrandID)
        BrandName = brand.BrandName

        return BrandName

    def get_Check_positive_Stock(self, instances):
        CompanyID = self.context.get("CompanyID")
        WarehouseID = self.context.get("WarehouseID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        Check_positive_Stock = 0

        if WarehouseID:
            if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID):
                stock_ins = StockPosting.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID)
                total_stockIN = 0
                total_stockOUT = 0
                for s in stock_ins:
                    total_stockIN += converted_float(s.QtyIn)
                    total_stockOUT += converted_float(s.QtyOut)

                Check_positive_Stock = converted_float(
                    total_stockIN) - converted_float(total_stockOUT)
        else:
            if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID):
                stock_ins = StockPosting.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                total_stockIN = 0
                total_stockOUT = 0
                for s in stock_ins:
                    total_stockIN += converted_float(s.QtyIn)
                    total_stockOUT += converted_float(s.QtyOut)

                Check_positive_Stock = converted_float(
                    total_stockIN) - converted_float(total_stockOUT)

        return Check_positive_Stock

    def get_Stock(self, instances):
        CompanyID = self.context.get("CompanyID")
        WarehouseID = self.context.get("WarehouseID")

        try:
            type = self.context.get("type")
        except:
            type = "any"

        try:
            Date = self.context.get("Date")
        except:
            Date = ""

        ProductID = instances.ProductID
        BranchID = instances.BranchID
        Stock = 0
        check_EnableProductBatchWise = False
        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
            check_EnableProductBatchWise = GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
        if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
            if WarehouseID:
                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID).exists():
                    Batch_ins = Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID)
                    total_stockIN = 0
                    total_stockOUT = 0
                    for b in Batch_ins:
                        batch_pricelistID = b.PriceListID
                        batch_MultiFactor = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=batch_pricelistID).MultiFactor
                        total_stockIN += (converted_float(b.StockIn) /
                                          converted_float(batch_MultiFactor))
                        total_stockOUT += (converted_float(b.StockOut) /
                                           converted_float(batch_MultiFactor))

                    Stock = converted_float(total_stockIN) - converted_float(total_stockOUT)
            else:
                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
                    Batch_ins = Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                    total_stockIN = 0
                    total_stockOUT = 0
                    for b in Batch_ins:
                        batch_pricelistID = b.PriceListID
                        batch_MultiFactor = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=batch_pricelistID).MultiFactor
                        total_stockIN += (converted_float(b.StockIn) /
                                          converted_float(batch_MultiFactor))
                        total_stockOUT += (converted_float(b.StockOut) /
                                           converted_float(batch_MultiFactor))

                    Stock = converted_float(total_stockIN) - converted_float(total_stockOUT)
        else:
            if type == "CommonStockCalculation" and Date:
                if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID, Date__lte=Date):
                    stock_ins = StockPosting.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID, Date__lte=Date)
                    total_stockIN = 0
                    total_stockOUT = 0
                    for s in stock_ins:
                        total_stockIN += converted_float(s.QtyIn)
                        total_stockOUT += converted_float(s.QtyOut)
                    Stock = converted_float(total_stockIN) - converted_float(total_stockOUT)

            elif WarehouseID:
                if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID):
                    stock_ins = StockPosting.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID)
                    total_stockIN = 0
                    total_stockOUT = 0
                    for s in stock_ins:
                        total_stockIN += converted_float(s.QtyIn)
                        total_stockOUT += converted_float(s.QtyOut)

                    Stock = converted_float(total_stockIN) - converted_float(total_stockOUT)
            else:
                if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID):
                    stock_ins = StockPosting.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                    total_stockIN = 0
                    total_stockOUT = 0
                    for s in stock_ins:
                        total_stockIN += converted_float(s.QtyIn)
                        total_stockOUT += converted_float(s.QtyOut)

                    Stock = converted_float(total_stockIN) - converted_float(total_stockOUT)

        return Stock

    def get_Tax1(self, instances):
        Tax1 = instances.Tax1
        if not Tax1:
            Tax1 = 1
        return Tax1

    def get_Tax2(self, instances):
        Tax2 = instances.Tax2
        if not Tax2:
            Tax2 = 1
        return Tax2

    def get_Tax3(self, instances):
        Tax3 = instances.Tax3
        if not Tax3:
            Tax3 = 1
        return Tax3

    def get_GST(self, instances):
        GST = instances.GST
        if not GST:
            GST = 1
        return GST

    def get_VatID(self, instances):
        VatID = instances.VatID

        if not VatID:
            VatID = 1
        return VatID

    def get_PLUNo(self, instances):
        PLUNo = instances.PLUNo
        if not PLUNo:
            PLUNo = 1
        return PLUNo

    def get_is_VAT_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        VatID = instances.VatID
        BranchID = instances.BranchID
        Inclusive = False
        check_productsForAllBranches = get_BranchSettings(
            CompanyID, "productsForAllBranches")
        if VatID:
            if check_productsForAllBranches:
                Inclusive = TaxCategory.objects.filter(
                    CompanyID=CompanyID, TaxID=VatID).first().Inclusive
            else:
                Inclusive = TaxCategory.objects.get(
                    CompanyID=CompanyID, TaxID=VatID).Inclusive
        return Inclusive

    def get_is_GST_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        GST = instances.GST
        BranchID = instances.BranchID
        Inclusive = False
        check_productsForAllBranches = get_BranchSettings(
            CompanyID, "productsForAllBranches")
        if GST:
            if check_productsForAllBranches:
                Inclusive = TaxCategory.objects.filter(
                    CompanyID=CompanyID, TaxID=GST).first().Inclusive
            else:
                Inclusive = TaxCategory.objects.get(
                    CompanyID=CompanyID, TaxID=GST).Inclusive
        return Inclusive

    def get_is_TAX1_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax1 = instances.Tax1
        BranchID = instances.BranchID
        Inclusive = False
        if Tax1:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax1).Inclusive
        return Inclusive

    def get_is_TAX2_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax2 = instances.Tax2
        BranchID = instances.BranchID
        Inclusive = False
        if Tax2:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax2).Inclusive
        return Inclusive

    def get_is_TAX3_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax3 = instances.Tax3
        BranchID = instances.BranchID
        Inclusive = False
        if Tax3:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax3).Inclusive
        return Inclusive

    def get_DefaultUnitID(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        DefaultUnitID = 0
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            DefaultUnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).PriceListID
            # DefaultUnitID = unitInstance.PriceListID
        return DefaultUnitID

    def get_DefUntID(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        DefUntID = 0
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            DefUntID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).UnitID
        # DefUntID = unitInstance.PriceListID
        return DefUntID

    def get_DefBarcode(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        DefBarcode = 0
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            DefBarcode = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).Barcode
        # DefBarcode = unitInstance.PriceListID
        return DefBarcode

    def get_DefaultUnitName(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        UnitID = 0
        DefaultUnitName = ""
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).UnitID
            DefaultUnitName = Unit.objects.get(
                UnitID=UnitID, CompanyID=CompanyID).UnitName

        return DefaultUnitName

    def get_DefaultSalesPrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            get_DefaultSalesPrice = unitInstance.SalesPrice
        else:
            get_DefaultSalesPrice = 0

        return get_DefaultSalesPrice

    def get_DefaultSalesPrice1(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            get_DefaultSalesPrice1 = unitInstance.SalesPrice1
        else:
            get_DefaultSalesPrice1 = 0

        return get_DefaultSalesPrice1

    def get_DefaultSalesPrice2(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            get_DefaultSalesPrice2 = unitInstance.SalesPrice2
        else:
            get_DefaultSalesPrice2 = 0

        return get_DefaultSalesPrice2

    def get_DefaultSalesPrice3(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            get_DefaultSalesPrice3 = unitInstance.SalesPrice3
        else:
            get_DefaultSalesPrice3 = 0

        return get_DefaultSalesPrice3

    def get_DefaultMRP(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            get_DefaultMRP = unitInstance.MRP
        else:
            get_DefaultMRP = 0

        return get_DefaultMRP

    def get_DefaultPurchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            DefaultPurchasePrice = unitInstance.PurchasePrice
        else:
            DefaultPurchasePrice = 0

        return DefaultPurchasePrice

    def get_UnitName(self, instances):
        CompanyID = self.context.get("CompanyID")

        ProductID = instances.ProductID
        BranchID = instances.BranchID
        UnitName = ""
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            UnitID = priceList.UnitID
            UnitName = Unit.objects.get(
                CompanyID=CompanyID, UnitID=UnitID).UnitName

        return UnitName

    def get_PurchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            PurchasePrice = priceList.PurchasePrice
            # PurchasePrice = round(PurchasePrice, int(PriceRounding))
        else:
            PurchasePrice = 0
        return PurchasePrice

    def get_SalesPrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            SalesPrice = priceList.SalesPrice
            # SalesPrice = round(SalesPrice, int(PriceRounding))
        else:
            SalesPrice = 0
        return SalesPrice

    def get_MRP(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            MRP = priceList.MRP
            # MRP = round(MRP, int(PriceRounding))
        else:
            MRP = 0
        return MRP

    def get_ProductGroupName(self, instances):
        CompanyID = self.context.get("CompanyID")

        ProductGroupID = instances.ProductGroupID
        BranchID = instances.BranchID
        product_group = ProductGroup.objects.get(
            CompanyID=CompanyID, ProductGroupID=ProductGroupID)
        ProductGroupName = product_group.GroupName

        return ProductGroupName

    def get_PriceListDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        price_list = PriceList.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID)
        serialized = PriceListRestSerializer(price_list, many=True, context={
                                             "CompanyID": CompanyID, "PriceRounding": PriceRounding})

        return serialized.data

    def get_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")
        TaxName = ""
        TaxID = 1
        if instances.VatID != 1:
            TaxID = instances.VatID
        elif instances.GST != 1:
            TaxID = instances.GST
        elif instances.Tax1 != 1:
            TaxID = instances.Tax1
        elif instances.Tax2 != 1:
            TaxID = instances.Tax2
        elif instances.Tax3 != 1:
            TaxID = instances.Tax3
        BranchID = instances.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            TaxName = tax.TaxName

        return TaxName

    def get_GST_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.GST
        BranchID = instances.BranchID
        GST_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            GST_TaxName = tax.TaxName

        return GST_TaxName

    def get_VAT_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        VAT_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            VAT_TaxName = tax.TaxName

        return VAT_TaxName

    def get_Tax1_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.Tax1
        BranchID = instances.BranchID
        Tax1_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            Tax1_TaxName = tax.TaxName

        return Tax1_TaxName

    def get_Tax2_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.Tax2
        BranchID = instances.BranchID
        Tax2_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            Tax2_TaxName = tax.TaxName

        return Tax2_TaxName

    def get_Tax3_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.Tax3
        BranchID = instances.BranchID
        Tax3_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            Tax3_TaxName = tax.TaxName

        return Tax3_TaxName

    def get_PurchaseTax(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        PurchaseTax = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            PurchaseTax = tax.PurchaseTax
            # if PurchaseTax:
            #     PurchaseTax = round(PurchaseTax, int(PriceRounding))
            # else:
            #     PurchaseTax = 0
        return str(PurchaseTax)

    def get_SalesTax(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        SalesTax = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            # if SalesTax:
            #     SalesTax = round(SalesTax, int(PriceRounding))
            # else:
            #     SalesTax = 0
        return str(SalesTax)

    def get_StockMinimum(self, instances):
        PriceRounding = self.context.get("PriceRounding")

        StockMinimum = instances.StockMinimum
        # if StockMinimum:
        #     StockMinimum = round(StockMinimum, int(PriceRounding))
        # else:
        #     StockMinimum = 0

        return str(StockMinimum)

    def get_StockMaximum(self, instances):

        PriceRounding = self.context.get("PriceRounding")
        StockMaximum = instances.StockMaximum

        # if StockMaximum:
        #     StockMaximum = round(StockMaximum, int(PriceRounding))
        # else:
        #     StockMaximum = 0

        return str(StockMaximum)

    def get_StockReOrder(self, instances):

        PriceRounding = self.context.get("PriceRounding")
        StockReOrder = instances.StockReOrder
        # if StockReOrder:
        #     StockReOrder = round(StockReOrder, int(PriceRounding))
        # else:
        #     StockReOrder = 0
        return str(StockReOrder)

    def get_GST_PurchaseTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.GST
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
            PurchaseTax = tax.PurchaseTax
            # if PurchaseTax:
            #     GST_PurchaseTax = round(PurchaseTax, int(PriceRounding))
            # else:
            #     GST_PurchaseTax = 0
            return str(PurchaseTax)
        else:
            return "0"

    def get_GST_SalesTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.GST
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            # if SalesTax:
            #     GST_SalesTax = round(SalesTax, int(PriceRounding))
            # else:
            #     GST_SalesTax = 0
            return str(SalesTax)
        else:
            return "0"

    def get_Tax1_PurchaseTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax1
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            PurchaseTax = tax.PurchaseTax
            # if PurchaseTax:
            #     Tax1_PurchaseTax = round(PurchaseTax, int(PriceRounding))
            # else:
            #     Tax1_PurchaseTax = 0
            return str(PurchaseTax)
        else:
            return "0"

    def get_Tax1_SalesTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax1
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            # if SalesTax:
            #     Tax1_SalesTax = round(SalesTax, int(PriceRounding))
            # else:
            #     Tax1_SalesTax = 0
            return str(SalesTax)
        else:
            return "0"

    def get_Tax2_PurchaseTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax2
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            PurchaseTax = tax.PurchaseTax
            # if PurchaseTax:
            #     Tax2_PurchaseTax = round(PurchaseTax, int(PriceRounding))
            # else:
            #     Tax2_PurchaseTax = 0
            return str(PurchaseTax)
        else:
            return "0"

    def get_Tax2_SalesTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax2
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            # if SalesTax:
            #     Tax2_SalesTax = round(SalesTax, int(PriceRounding))
            # else:
            #     Tax2_SalesTax = 0
            return str(SalesTax)
        else:
            return "0"

    def get_Tax3_PurchaseTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax3
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            PurchaseTax = tax.PurchaseTax
            # if PurchaseTax:
            #     Tax3_PurchaseTax = round(PurchaseTax, int(PriceRounding))
            # else:
            #     Tax3_PurchaseTax = 0
            return str(PurchaseTax)
        else:
            return "0"

    def get_Tax3_SalesTax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.Tax3
        BranchID = instance.BranchID
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID)
            SalesTax = tax.SalesTax
            # if SalesTax:
            #     Tax3_SalesTax = round(SalesTax, int(PriceRounding))
            # else:
            #     Tax3_SalesTax = 0
            return str(SalesTax)
        else:
            return "0"


class MultyUnitExcelSerializer(serializers.ModelSerializer):
    SalesPrice = serializers.SerializerMethodField()
    SalesPrice1 = serializers.SerializerMethodField()
    SalesPrice2 = serializers.SerializerMethodField()
    SalesPrice3 = serializers.SerializerMethodField()
    PurchasePrice = serializers.SerializerMethodField()
    MRP = serializers.SerializerMethodField()
    MultiFactor = serializers.SerializerMethodField()
    detailID = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()
    BatchCode = serializers.SerializerMethodField()
    ProductCode = serializers.SerializerMethodField()

    class Meta:
        model = PriceList
        fields = ('id', 'ProductCode', 'PriceListID', 'BranchID', 'MRP', 'ProductID', 'UnitID', 'UnitName', 'SalesPrice', 'PurchasePrice', 'MultiFactor', 'Barcode', 'AutoBarcode', 'SalesPrice1', 'SalesPrice2', 'SalesPrice3', 'Action', 'CreatedDate', 'CreatedUserID', 'DefaultUnit', 'UnitInSales',
                  'UnitInPurchase', 'UnitInReports', 'detailID', 'BatchCode')

    def get_ProductCode(self, instances):
        ProductCode = instances.product.ProductCode
        return ProductCode

    def get_SalesPrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        SalesPrice = instances.SalesPrice
        BranchID = instances.BranchID
        ProductID = instances.ProductID
        PriceListID = instances.PriceListID
        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
            check_EnableProductBatchWise = GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
            if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PriceListID=PriceListID).exists():
                    batch_ins = Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PriceListID=PriceListID).last()
                    SalesPrice = batch_ins.SalesPrice
        # SalesPrice = round(SalesPrice,PriceRounding)

        return converted_float(SalesPrice)

    def get_BatchCode(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        BatchCode = 0
        BranchID = instances.BranchID
        ProductID = instances.ProductID
        PriceListID = instances.PriceListID
        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
            check_EnableProductBatchWise = GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
            if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PriceListID=PriceListID).exists():
                    batch_ins = Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PriceListID=PriceListID).last()
                    BatchCode = batch_ins.BatchCode

        return str(BatchCode)

    def get_detailID(self, instances):

        detailID = 0

        return detailID

    def get_UnitName(self, instances):
        CompanyID = self.context.get("CompanyID")

        UnitID = instances.UnitID
        BranchID = instances.BranchID
        UnitName = ""
        if Unit.objects.filter(CompanyID=CompanyID, UnitID=UnitID).exists():
            UnitName = Unit.objects.get(
                CompanyID=CompanyID, UnitID=UnitID).UnitName

        return UnitName

    def get_SalesPrice1(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        SalesPrice1 = instances.SalesPrice1

        # SalesPrice1 = round(SalesPrice1,PriceRounding)

        return str(SalesPrice1)

    def get_SalesPrice2(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        SalesPrice2 = instances.SalesPrice2

        # SalesPrice2 = round(SalesPrice2,PriceRounding)

        return str(SalesPrice2)

    def get_SalesPrice3(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        SalesPrice3 = instances.SalesPrice3

        # SalesPrice3 = round(SalesPrice3,PriceRounding)

        return str(SalesPrice3)

    def get_MRP(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        MRP = instances.MRP

        # MRP = round(MRP,PriceRounding)

        return str(MRP)

    def get_PurchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        PurchasePrice = instances.PurchasePrice
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        PriceListID = instances.PriceListID
        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
            check_EnableProductBatchWise = GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
            if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PriceListID=PriceListID).exists():
                    batch_ins = Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PriceListID=PriceListID).first()
                    PurchasePrice = batch_ins.PurchasePrice

        # PurchasePrice = round(PurchasePrice,PriceRounding)

        return converted_float(PurchasePrice)

    def get_MultiFactor(self, instances):

        PriceRounding = self.context.get("PriceRounding")
        MultiFactor = instances.MultiFactor

        # MultiFactor = round(MultiFactor,PriceRounding)

        return str(MultiFactor)



class ProductCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'ProductCode')
        
        
class AddItemBarcodeSerializer(serializers.ModelSerializer):
    PriceListID = serializers.SerializerMethodField()
    Stock = serializers.SerializerMethodField()
    BatchList = serializers.SerializerMethodField()
    PurchasePrice = serializers.SerializerMethodField()
    SalesPrice = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'ProductID', 'BranchID', 'ProductCode','ProductName', 'PriceListID', 'Stock', 'is_inclusive',
                  'BatchList', 'PurchasePrice', 'SalesPrice', 'StockMaximum', 'StockMinimum')

    def get_PurchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            PurchasePrice = priceList.PurchasePrice
            # PurchasePrice = round(PurchasePrice, int(PriceRounding))
        else:
            PurchasePrice = 0
        return PurchasePrice

    def get_SalesPrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            SalesPrice = priceList.SalesPrice
            # SalesPrice = round(SalesPrice, int(PriceRounding))
        else:
            SalesPrice = 0
        return SalesPrice

    
    def get_BatchList(self, instance):
        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        ProductID = instance.ProductID
        BatchList = []
        check_EnableProductBatchWise = get_GeneralSettings(CompanyID,BranchID,"EnableProductBatchWise")
        if check_EnableProductBatchWise:
            if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
                batch_details = Batch.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                batchList = Batch_ListSerializer(batch_details, many=True, context={
                    "CompanyID": CompanyID})
                BatchList = batchList.data
        return BatchList
        
    def get_PriceListID(self, instances):
        CompanyID = self.context.get("CompanyID")
        BarCode = self.context.get("BarCode")
        BranchID = instances.BranchID
        ProductID = instances.ProductID
        check_EnableProductBatchWise = get_GeneralSettings(CompanyID,BranchID,"EnableProductBatchWise")
        if get_BranchSettings(CompanyID, "productsForAllBranches"):
            pricelist_list = PriceList.objects.filter(
                CompanyID=CompanyID)
        else:
            pricelist_list = PriceList.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
        PriceListID = PriceList.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).PriceListID
        if check_EnableProductBatchWise:
            if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BarCode).exists():
                batch_ins = Batch.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, BatchCode=BarCode)
                PriceListID = batch_ins.PriceListID
        else:
            if pricelist_list.filter(Barcode=BarCode).exists():
                PriceListID = pricelist_list.filter(
                    Barcode=BarCode).first().PriceListID
                
        return PriceListID
    
    
    def get_Stock(self, instances):
        CompanyID = self.context.get("CompanyID")
        WarehouseID = self.context.get("WarehouseID")

        try:
            type = self.context.get("type")
        except:
            type = "any"

        try:
            Date = self.context.get("Date")
        except:
            Date = ""

        ProductID = instances.ProductID
        BranchID = instances.BranchID
        Stock = 0
        check_EnableProductBatchWise = False
        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
            check_EnableProductBatchWise = GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
        if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
            if WarehouseID:
                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID).exists():
                    Batch_ins = Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID).order_by('BatchCode').last()
                    batch_pricelistID = Batch_ins.PriceListID
                    batch_MultiFactor = PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=batch_pricelistID).MultiFactor
                    total_stockIN = converted_float(Batch_ins.StockIn)
                    total_stockOUT = converted_float(Batch_ins.StockOut)
                    Stock = converted_float(
                        total_stockIN) - converted_float(total_stockOUT)
            else:
                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
                    Batch_ins = Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                    total_stockIN = Batch_ins.aggregate(Sum('StockIn'))
                    total_stockIN = total_stockIN['StockIn__sum']
                    total_stockOUT = Batch_ins.aggregate(Sum('StockOut'))
                    total_stockOUT = total_stockOUT['StockOut__sum']

                    Stock = converted_float(
                        total_stockIN) - converted_float(total_stockOUT)
        else:
            if type == "CommonStockCalculation" and Date:
                if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID, Date__lte=Date):
                    stock_ins = StockPosting.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID, Date__lte=Date)
                    total_stockIN = stock_ins.aggregate(Sum('QtyIn'))
                    total_stockIN = total_stockIN['QtyIn__sum']
                    total_stockOUT = stock_ins.aggregate(Sum('QtyOut'))
                    total_stockOUT = total_stockOUT['QtyOut__sum']
                    Stock = converted_float(
                        total_stockIN) - converted_float(total_stockOUT)

            elif WarehouseID:
                if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID):
                    stock_ins = StockPosting.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID)
                    total_stockIN = stock_ins.aggregate(Sum('QtyIn'))
                    total_stockIN = total_stockIN['QtyIn__sum']
                    total_stockOUT = stock_ins.aggregate(Sum('QtyOut'))
                    total_stockOUT = total_stockOUT['QtyOut__sum']
                    Stock = converted_float(
                        total_stockIN) - converted_float(total_stockOUT)
            else:
                if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID):
                    stock_ins = StockPosting.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                    total_stockIN = stock_ins.aggregate(Sum('QtyIn'))
                    total_stockIN = total_stockIN['QtyIn__sum']
                    total_stockOUT = stock_ins.aggregate(Sum('QtyOut'))
                    total_stockOUT = total_stockOUT['QtyOut__sum']
                    Stock = converted_float(
                        total_stockIN) - converted_float(total_stockOUT)
        return Stock
    

    # def get_Stock(self, instances):
    #     CompanyID = self.context.get("CompanyID")
    #     BarCode = self.context.get("BarCode")
    #     WarehouseID = self.context.get("WarehouseID")
    #     ProductID = instances.ProductID
    #     BranchID = instances.BranchID
    #     Stock = 0
    #     check_EnableProductBatchWise = get_GeneralSettings(CompanyID,BranchID,"EnableProductBatchWise")
    #     if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
    #         if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BarCode,WareHouseID=WarehouseID).exists():
    #             batch_ins = Batch.objects.get(
    #                 CompanyID=CompanyID, BranchID=BranchID, BatchCode=BarCode, WareHouseID=WarehouseID)

    #             batch_pricelistID = batch_ins.PriceListID
    #             batch_MultiFactor = PriceList.objects.get(
    #                 CompanyID=CompanyID, PriceListID=batch_pricelistID).MultiFactor
    #             StockIn = batch_ins.StockIn
    #             StockOut = batch_ins.StockOut
    #             Stock = converted_float(StockIn) - \
    #                 converted_float(StockOut)
    #         else:
    #             if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductCode=BarCode).exists():
    #                 product_instance = Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductCode=BarCode).order_by('ProductID').first()
    #                 if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=product_instance.ProductID, WareHouseID=WarehouseID).exists():
    #                     batch_ins = Batch.objects.filter(
    #                         CompanyID=CompanyID, BranchID=BranchID, ProductID=product_instance.ProductID, WareHouseID=WarehouseID).order_by('BatchCode').first()
    #                     batch_pricelistID = batch_ins.PriceListID
    #                     batch_MultiFactor = PriceList.objects.get(
    #                         CompanyID=CompanyID, PriceListID=batch_pricelistID).MultiFactor
    #                     StockIn = batch_ins.StockIn
    #                     StockOut = batch_ins.StockOut
    #                     Stock = converted_float(StockIn) - \
    #                         converted_float(StockOut)
                    
    #     else:
    #         if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID):
    #             stock_ins = StockPosting.objects.filter(
    #                 CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID)
    #             total_stockIN = 0
    #             total_stockOUT = 0
    #             for s in stock_ins:
    #                 total_stockIN += converted_float(s.QtyIn)
    #                 total_stockOUT += converted_float(s.QtyOut)
    #             Stock = converted_float(total_stockIN) - converted_float(total_stockOUT)

    #     return Stock

    

    

class ProductSearchStockQrySerializer(serializers.ModelSerializer):
    
    Stock = serializers.SerializerMethodField()
    PurchasePrice = serializers.SerializerMethodField()
    SalesPrice = serializers.SerializerMethodField()
    Barcode = serializers.SerializerMethodField()
    BatchCode = serializers.SerializerMethodField()
    # Check_positive_Stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'Description', 'ProductID', 'ProductCode', 'Barcode', 'ProductName',
                  'Stock', 'HSNCode', 'PurchasePrice', 'SalesPrice', 'is_inclusive', 'BatchCode', 'BranchID')

    def get_BatchCode(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        BatchCode = 0
        if Batch.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).exists():
            BatchCode = Batch.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).first().BatchCode

        return BatchCode

    def get_Barcode(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            Barcode = priceList.Barcode
            # Barcode = round(Barcode, int(PriceRounding))
        else:
            Barcode = 0
        return Barcode

    def get_PurchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            PurchasePrice = priceList.PurchasePrice
            # PurchasePrice = round(PurchasePrice, int(PriceRounding))
        else:
            PurchasePrice = 0
        return PurchasePrice

    def get_SalesPrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True)
            SalesPrice = priceList.SalesPrice
            # SalesPrice = round(SalesPrice, int(PriceRounding))
        else:
            SalesPrice = 0
        return SalesPrice

    def get_Stock(self, instances):
        CompanyID = self.context.get("CompanyID")
        WarehouseID = self.context.get("WarehouseID")
        PriceRounding = self.context.get("PriceRounding")

        try:
            type = self.context.get("type")
        except:
            type = "any"

        try:
            Date = self.context.get("Date")
        except:
            Date = ""
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        BranchList = get_BranchList(CompanyID, BranchID)
        WarehouseList = []
        if WarehouseID > 0:
            WarehouseList.append(WarehouseID)
        else:
            WarehouseList = Warehouse.objects.filter(CompanyID=CompanyID,BranchID__in=BranchList).values_list('WarehousID',flat=True)
        Stock = query_get_product_stock(CompanyID.id,ProductID,PriceRounding,type,Date,WarehouseList,BranchList)
        print("-==================================end")
        print(Stock)
        return Stock