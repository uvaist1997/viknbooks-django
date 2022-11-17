from rest_framework import serializers
from brands.models import ProductBarcode,Product, PriceList, Brand, ProductGroup, TaxCategory, Unit, StockPosting, Batch, GeneralSettings, Warehouse
from api.v5.priceLists.serializers import PriceListRestSerializer, SinglePriceListRestSerializer
from api.v5.workOrder.serializers import Batch_ListSerializer, UnitListSerializer


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ('id', 'BranchID', 'ProductCode', 'ProductName', 'DisplayName', 'Description', 'ProductGroupID', 'is_Service',
                  'BrandID', 'InventoryType', 'VatID', 'StockMinimum', 'MinimumSalesPrice', 'StockReOrder', 'StockMaximum',
                  'MarginPercent', 'Active', 'IsRawMaterial', 'IsWeighingScale', 'WeighingCalcType', 'PLUNo', 'WarrantyType', 'Warranty',
                  'IsFavourite', 'CreatedDate', 'CreatedUserID', 'IsFinishedProduct', 'IsSales', 'IsPurchase', "GST", "Tax1", "Tax2", "Tax3", "IsKFC", "HSNCode")


class ProductBarcodeListRestSerializer(serializers.ModelSerializer):

    detailID = serializers.SerializerMethodField()

    class Meta:
        model = ProductBarcode
        fields = ('id', 'BranchID','CompanyID','Barcode','detailID' )

    def get_detailID(self, instances):
        return 0




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
        fields = ('id', 'ProductID', 'ProductBarcodeList','BranchID', 'ProductCode', 'ProductName', 'DisplayName', 'Description', 'ProductGroupID', 'is_Service',
                  'BrandID', 'InventoryType', 'VatID', 'StockMinimum', 'MinimumSalesPrice', 'StockReOrder', 'StockMaximum', 'DefUntID', 'DefBarcode',
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

        return serialized.data


    def get_BrandName(self, instances):
        CompanyID = self.context.get("CompanyID")

        BrandID = instances.BrandID
        BranchID = instances.BranchID
        brand = Brand.objects.get(
            CompanyID=CompanyID, BrandID=BrandID, BranchID=BranchID)
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
                    total_stockIN += float(s.QtyIn)
                    total_stockOUT += float(s.QtyOut)

                Check_positive_Stock = float(
                    total_stockIN) - float(total_stockOUT)
        else:
            if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID):
                stock_ins = StockPosting.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                total_stockIN = 0
                total_stockOUT = 0
                for s in stock_ins:
                    total_stockIN += float(s.QtyIn)
                    total_stockOUT += float(s.QtyOut)

                Check_positive_Stock = float(
                    total_stockIN) - float(total_stockOUT)

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
                CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
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
                            CompanyID=CompanyID, BranchID=BranchID, PriceListID=batch_pricelistID).MultiFactor
                        total_stockIN += (float(b.StockIn) /
                                          float(batch_MultiFactor))
                        total_stockOUT += (float(b.StockOut) /
                                           float(batch_MultiFactor))

                    Stock = float(total_stockIN) - float(total_stockOUT)
            else:
                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
                    Batch_ins = Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                    total_stockIN = 0
                    total_stockOUT = 0
                    for b in Batch_ins:
                        batch_pricelistID = b.PriceListID
                        batch_MultiFactor = PriceList.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, PriceListID=batch_pricelistID).MultiFactor
                        total_stockIN += (float(b.StockIn) /
                                          float(batch_MultiFactor))
                        total_stockOUT += (float(b.StockOut) /
                                           float(batch_MultiFactor))

                    Stock = float(total_stockIN) - float(total_stockOUT)
        else:
            if type == "CommonStockCalculation" and Date:
                print(type,"&&&&&&&&&&&&&&&&&&&&&&123&&&&&&&&&&&&&&&&&&&&&&&&",Date)
                if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID,Date__lte=Date):
                    stock_ins = StockPosting.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID,Date__lte=Date)
                    total_stockIN = 0
                    total_stockOUT = 0
                    for s in stock_ins:
                        print(s.Date)
                        total_stockIN += float(s.QtyIn)
                        total_stockOUT += float(s.QtyOut)
                        print(total_stockIN)
                        print(total_stockOUT)
                        print(s.ProductID)
                    Stock = float(total_stockIN) - float(total_stockOUT)
                    print(Stock)

            elif WarehouseID:
                if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID):
                    stock_ins = StockPosting.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID)
                    total_stockIN = 0
                    total_stockOUT = 0
                    for s in stock_ins:
                        total_stockIN += float(s.QtyIn)
                        total_stockOUT += float(s.QtyOut)

                    Stock = float(total_stockIN) - float(total_stockOUT)
            else:
                if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID):
                    stock_ins = StockPosting.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                    total_stockIN = 0
                    total_stockOUT = 0
                    for s in stock_ins:
                        total_stockIN += float(s.QtyIn)
                        total_stockOUT += float(s.QtyOut)

                    Stock = float(total_stockIN) - float(total_stockOUT)

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
                CompanyID=CompanyID, TaxID=VatID, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_GST_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        GST = instances.GST
        BranchID = instances.BranchID
        Inclusive = False
        if GST:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=GST, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_TAX1_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax1 = instances.Tax1
        BranchID = instances.BranchID
        Inclusive = False
        if Tax1:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax1, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_TAX2_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax2 = instances.Tax2
        BranchID = instances.BranchID
        Inclusive = False
        if Tax2:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax2, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_TAX3_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax3 = instances.Tax3
        BranchID = instances.BranchID
        Inclusive = False
        if Tax3:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax3, BranchID=BranchID).Inclusive
        return Inclusive

    def get_DefaultUnitID(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        DefaultUnitID = 0
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            DefaultUnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).PriceListID
            # DefaultUnitID = unitInstance.PriceListID
        return DefaultUnitID

    def get_DefUntID(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        DefUntID = 0
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            DefUntID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).UnitID
        # DefUntID = unitInstance.PriceListID
        return DefUntID

    def get_DefBarcode(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        DefBarcode = 0
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            DefBarcode = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).Barcode
        # DefBarcode = unitInstance.PriceListID
        return DefBarcode

    def get_DefaultUnitName(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        UnitID = 0
        DefaultUnitName = ""
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).UnitID
            DefaultUnitName = Unit.objects.get(
                BranchID=BranchID, UnitID=UnitID, CompanyID=CompanyID).UnitName

        return DefaultUnitName

    def get_DefaultSalesPrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
            get_DefaultSalesPrice = unitInstance.SalesPrice
        else:
            get_DefaultSalesPrice = 0

        return get_DefaultSalesPrice

    def get_DefaultSalesPrice1(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
            get_DefaultSalesPrice1 = unitInstance.SalesPrice1
        else:
            get_DefaultSalesPrice1 = 0

        return get_DefaultSalesPrice1

    def get_DefaultSalesPrice2(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
            get_DefaultSalesPrice2 = unitInstance.SalesPrice2
        else:
            get_DefaultSalesPrice2 = 0

        return get_DefaultSalesPrice2

    def get_DefaultSalesPrice3(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
            get_DefaultSalesPrice3 = unitInstance.SalesPrice3
        else:
            get_DefaultSalesPrice3 = 0

        return get_DefaultSalesPrice3

    def get_DefaultMRP(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
            get_DefaultMRP = unitInstance.MRP
        else:
            get_DefaultMRP = 0

        return get_DefaultMRP

    def get_DefaultPurchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
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
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
            UnitID = priceList.UnitID
            UnitName = Unit.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, UnitID=UnitID).UnitName

        return UnitName

    def get_PurchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
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
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
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
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
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
            CompanyID=CompanyID, ProductGroupID=ProductGroupID, BranchID=BranchID)
        ProductGroupName = product_group.GroupName

        return ProductGroupName

    def get_PriceListDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        price_list = PriceList.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
            TaxName = tax.TaxName

        return TaxName

    def get_GST_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.GST
        BranchID = instances.BranchID
        GST_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
            GST_TaxName = tax.TaxName

        return GST_TaxName

    def get_VAT_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        VAT_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
            VAT_TaxName = tax.TaxName

        return VAT_TaxName

    def get_Tax1_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.Tax1
        BranchID = instances.BranchID
        Tax1_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
            Tax1_TaxName = tax.TaxName

        return Tax1_TaxName

    def get_Tax2_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.Tax2
        BranchID = instances.BranchID
        Tax2_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
            Tax2_TaxName = tax.TaxName

        return Tax2_TaxName

    def get_Tax3_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.Tax3
        BranchID = instances.BranchID
        Tax3_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
            Tax3_TaxName = tax.TaxName

        return Tax3_TaxName

    def get_PurchaseTax(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        PurchaseTax = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        fields = ('id', 'ProductID', 'ProductBarcodeList','BranchID', 'ProductCode', 'ProductName', 'DisplayName', 'Description', 'ProductGroupID',
                  'BrandID', 'InventoryType', 'VatID', 'StockMinimum', 'MinimumSalesPrice', 'StockReOrder', 'StockMaximum', 'DefUntID', 'DefBarcode',
                  'MarginPercent', 'ProductImage', 'Active', 'IsRawMaterial', 'IsWeighingScale', 'WeighingCalcType', 'PLUNo', 'WarrantyType', 'Warranty',
                  'IsFavourite', 'CreatedDate', 'CreatedUserID', 'Action', 'GST', 'GST_PurchaseTax', 'GST_SalesTax', 'SalesTax', 'Tax1', 'Tax1_PurchaseTax', 'Tax1_SalesTax',
                  'Tax2', 'Tax2_PurchaseTax', 'Tax2_SalesTax', 'Tax3', 'Tax3_PurchaseTax', 'Tax3_SalesTax', 'BrandName', 'TaxName', 'ProductGroupName', 'PurchaseTax', 'SalesTax',
                  'IsFinishedProduct', 'IsSales', 'IsPurchase', 'PurchasePrice', 'SalesPrice', 'MRP', 'GST_TaxName', 'VAT_TaxName', 'UnitName', 'Tax1_TaxName', 'Tax2_TaxName', 'Tax3_TaxName',
                  'DefaultUnitID', 'DefaultUnitName', 'DefaultSalesPrice', 'DefaultSalesPrice1', 'DefaultSalesPrice2', 'DefaultSalesPrice3', 'DefaultPurchasePrice',
                  'is_VAT_inclusive', 'is_GST_inclusive', 'is_TAX1_inclusive', 'is_TAX2_inclusive', 'is_TAX3_inclusive', 'PriceListDetails', 'DefaultMRP', "IsKFC", 'DefaultBarcode', "HSNCode", 'Stock', 'Check_positive_Stock')


    def get_ProductBarcodeList(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        product_barcode_list = ProductBarcode.objects.filter(
            CompanyID=CompanyID, ProductID=instances, BranchID=BranchID)
        serialized = ProductBarcodeListRestSerializer(product_barcode_list, many=True, context={
                                             "CompanyID": CompanyID, "PriceRounding": PriceRounding})
        print(serialized,'product_barcode_listproduct_barcode_list')
        return serialized.data


    def get_BrandName(self, instances):
        CompanyID = self.context.get("CompanyID")

        BrandID = instances.BrandID
        BranchID = instances.BranchID
        brand = Brand.objects.get(
            CompanyID=CompanyID, BrandID=BrandID, BranchID=BranchID)
        BrandName = brand.BrandName

        return BrandName

    def get_DefaultBarcode(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID

        DefaultBarcode = PriceList.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).Barcode

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
                total_stockIN += float(s.QtyIn)
                total_stockOUT += float(s.QtyOut)

            Check_positive_Stock = float(total_stockIN) - float(total_stockOUT)

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
                total_stockIN += (float(b.StockIn) / float(batch_MultiFactor))
                total_stockOUT += (float(b.StockOut) /
                                   float(batch_MultiFactor))

            Stock = float(total_stockIN) - float(total_stockOUT)
        else:
            if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID):
                stock_ins = StockPosting.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                total_stockIN = 0
                total_stockOUT = 0
                for s in stock_ins:
                    total_stockIN += float(s.QtyIn)
                    total_stockOUT += float(s.QtyOut)

                Stock = float(total_stockIN) - float(total_stockOUT)

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
                CompanyID=CompanyID, TaxID=VatID, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_GST_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        GST = instances.GST
        BranchID = instances.BranchID
        Inclusive = False
        if GST:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=GST, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_TAX1_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax1 = instances.Tax1
        BranchID = instances.BranchID
        Inclusive = False
        if Tax1:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax1, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_TAX2_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax2 = instances.Tax2
        BranchID = instances.BranchID
        Inclusive = False
        if Tax2:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax2, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_TAX3_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax3 = instances.Tax3
        BranchID = instances.BranchID
        Inclusive = False
        if Tax3:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax3, BranchID=BranchID).Inclusive
        return Inclusive

    def get_DefaultUnitID(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        DefaultUnitID = 0
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            DefaultUnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).PriceListID
            # DefaultUnitID = unitInstance.PriceListID
        return DefaultUnitID

    def get_DefUntID(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        DefUntID = 0
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            DefUntID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).UnitID
        # DefUntID = unitInstance.PriceListID
        return DefUntID

    def get_DefBarcode(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        DefBarcode = 0
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            DefBarcode = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).Barcode
        # DefBarcode = unitInstance.PriceListID
        return DefBarcode

    def get_DefaultUnitName(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        UnitID = 0
        DefaultUnitName = ""
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).UnitID
            DefaultUnitName = Unit.objects.get(
                BranchID=BranchID, UnitID=UnitID, CompanyID=CompanyID).UnitName

        return DefaultUnitName

    def get_DefaultSalesPrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
            get_DefaultSalesPrice = unitInstance.SalesPrice
        else:
            get_DefaultSalesPrice = 0

        return get_DefaultSalesPrice

    def get_DefaultSalesPrice1(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
            get_DefaultSalesPrice1 = unitInstance.SalesPrice1
        else:
            get_DefaultSalesPrice1 = 0

        return get_DefaultSalesPrice1

    def get_DefaultSalesPrice2(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
            get_DefaultSalesPrice2 = unitInstance.SalesPrice2
        else:
            get_DefaultSalesPrice2 = 0

        return get_DefaultSalesPrice2

    def get_DefaultSalesPrice3(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
            get_DefaultSalesPrice3 = unitInstance.SalesPrice3
        else:
            get_DefaultSalesPrice3 = 0

        return get_DefaultSalesPrice3

    def get_DefaultMRP(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
            get_DefaultMRP = unitInstance.MRP
        else:
            get_DefaultMRP = 0

        return get_DefaultMRP

    def get_DefaultPurchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
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
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
            UnitID = priceList.UnitID
            UnitName = Unit.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, UnitID=UnitID).UnitName

        return UnitName

    def get_PurchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
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
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
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
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
            MRP = priceList.MRP
            MRP = round(MRP, int(PriceRounding))
        else:
            MRP = 0
        return MRP

    def get_ProductGroupName(self, instances):
        CompanyID = self.context.get("CompanyID")

        ProductGroupID = instances.ProductGroupID
        BranchID = instances.BranchID
        product_group = ProductGroup.objects.get(
            CompanyID=CompanyID, ProductGroupID=ProductGroupID, BranchID=BranchID)
        ProductGroupName = product_group.GroupName

        return ProductGroupName

    def get_PriceListDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        price_list = PriceList.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)
        serialized = SinglePriceListRestSerializer(price_list, many=True, context={
            "CompanyID": CompanyID, "PriceRounding": PriceRounding})

        return serialized.data

    def get_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
            TaxName = tax.TaxName

        return TaxName

    def get_GST_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.GST
        BranchID = instances.BranchID
        GST_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
            GST_TaxName = tax.TaxName

        return GST_TaxName

    def get_VAT_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        VAT_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
            VAT_TaxName = tax.TaxName

        return VAT_TaxName

    def get_Tax1_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.Tax1
        BranchID = instances.BranchID
        Tax1_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
            Tax1_TaxName = tax.TaxName

        return Tax1_TaxName

    def get_Tax2_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.Tax2
        BranchID = instances.BranchID
        Tax2_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
            Tax2_TaxName = tax.TaxName

        return Tax2_TaxName

    def get_Tax3_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.Tax3
        BranchID = instances.BranchID
        Tax3_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
            Tax3_TaxName = tax.TaxName

        return Tax3_TaxName

    def get_PurchaseTax(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        PurchaseTax = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            Barcode = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).AutoBarcode

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
                CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
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
        if PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
            unit_details = PriceList.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
            UnitList = UnitListSerializer(unit_details, many=True, context={
                                          "CompanyID": CompanyID})
            UnitList = UnitList.data
        return UnitList

    def get_PriceListID(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        PriceListID = ""
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            PriceListID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).PriceListID
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

            Stock = float(TotalQtyIn) - float(TotalQtyOut)
        else:
            if StockPosting.objects.filter(CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).exists():
                stockpostIns = StockPosting.objects.filter(
                    CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID)
                for i in stockpostIns:
                    TotalQtyIn += i.QtyIn
                    TotalQtyOut += i.QtyOut

            Stock = float(TotalQtyIn) - float(TotalQtyOut)
        return float(Stock)

    def get_CostPerItem(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        PurchasePrice = 0
        check_EnableProductBatchWise = False
        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
            check_EnableProductBatchWise = GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
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
        return float(PurchasePrice)

    def get_Batch_purchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        Batch_purchasePrice = 0
        check_EnableProductBatchWise = False
        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
            check_EnableProductBatchWise = GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
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
        return float(Batch_purchasePrice)

    def get_Batch_salesPrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        Batch_salesPrice = 0
        check_EnableProductBatchWise = False
        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
            check_EnableProductBatchWise = GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
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
        return float(Batch_salesPrice)

    def get_UnitName(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        UnitID = PriceList.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).UnitID
        UnitName = Unit.objects.get(
            CompanyID=CompanyID, BranchID=BranchID, UnitID=UnitID).UnitName
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
    Stock = serializers.SerializerMethodField()
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

    class Meta:
        model = Product
        fields = ('id', 'ProductID', 'BranchID', 'DefaultUnitName', 'DefaultUnitID', 'DefaultSalesPrice',
                  'ProductName', 'PriceListID', 'UnitPrice', 'Stock', 'BatchCode', 'DefaultPurchasePrice',
                  'GST_SalesTax', 'Tax3_SalesTax', 'Tax2_SalesTax', 'Tax1_SalesTax', 'SalesTax', 'Stock',
                  'is_GST_inclusive', 'is_VAT_inclusive', 'is_TAX1_inclusive', 'is_TAX2_inclusive', 'is_TAX3_inclusive')

    def get_PriceListID(self, instances):
        CompanyID = self.context.get("CompanyID")
        BarCode = self.context.get("BarCode")
        BranchID = instances.BranchID
        ProductID = instances.ProductID
        if PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Barcode=BarCode).exists():
            PriceListID = PriceList.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Barcode=BarCode).first().PriceListID
        else:
            PriceListID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).PriceListID
        return PriceListID

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
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).PurchasePrice
        return UnitPrice

    def get_DefaultUnitID(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        DefaultUnitID = 0
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            DefaultUnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).PriceListID
            # DefaultUnitID = unitInstance.PriceListID
        return DefaultUnitID

    def get_is_TAX1_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax1 = instances.Tax1
        BranchID = instances.BranchID
        Inclusive = False
        if Tax1:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax1, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_TAX2_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax2 = instances.Tax2
        BranchID = instances.BranchID
        Inclusive = False
        if Tax2:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax2, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_TAX3_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax3 = instances.Tax3
        BranchID = instances.BranchID
        Inclusive = False
        if Tax3:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax3, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_GST_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        GST = instances.GST
        BranchID = instances.BranchID
        Inclusive = False
        if GST:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=GST, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_VAT_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        VatID = instances.VatID
        BranchID = instances.BranchID
        Inclusive = False
        if VatID:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=VatID, BranchID=BranchID).Inclusive
        return Inclusive

    def get_Stock(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        Stock = 0
        check_EnableProductBatchWise = False
        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
            check_EnableProductBatchWise = GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
        if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
            if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
                Batch_ins = Batch.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                total_stockIN = 0
                total_stockOUT = 0
                for b in Batch_ins:
                    batch_pricelistID = b.PriceListID
                    batch_MultiFactor = PriceList.objects.get(
                        CompanyID=CompanyID, BranchID=BranchID, PriceListID=batch_pricelistID).MultiFactor
                    total_stockIN += (float(b.StockIn) /
                                      float(batch_MultiFactor))
                    total_stockOUT += (float(b.StockOut) /
                                       float(batch_MultiFactor))

                Stock = float(total_stockIN) - float(total_stockOUT)
        else:
            if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID):
                stock_ins = StockPosting.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                total_stockIN = 0
                total_stockOUT = 0
                for s in stock_ins:
                    total_stockIN += float(s.QtyIn)
                    total_stockOUT += float(s.QtyOut)

                Stock = float(total_stockIN) - float(total_stockOUT)

        return Stock

    def get_SalesTax(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        SalesTax = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).UnitID
            DefaultUnitName = Unit.objects.get(
                BranchID=BranchID, UnitID=UnitID, CompanyID=CompanyID).UnitName

        return DefaultUnitName

    def get_DefaultPurchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
            DefaultPurchasePrice = unitInstance.PurchasePrice
        else:
            DefaultPurchasePrice = 0

        return DefaultPurchasePrice

    def get_DefaultSalesPrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
            get_DefaultSalesPrice = unitInstance.SalesPrice
        else:
            get_DefaultSalesPrice = 0

        return get_DefaultSalesPrice

    def get_Stock(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        Stock = 0

        check_EnableProductBatchWise = False
        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
            check_EnableProductBatchWise = GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
        if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
            if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
                Batch_ins = Batch.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                total_stockIN = 0
                total_stockOUT = 0
                for b in Batch_ins:
                    batch_pricelistID = b.PriceListID
                    batch_MultiFactor = PriceList.objects.get(
                        CompanyID=CompanyID, BranchID=BranchID, PriceListID=batch_pricelistID).MultiFactor
                    total_stockIN += (float(b.StockIn) /
                                      float(batch_MultiFactor))
                    total_stockOUT += (float(b.StockOut) /
                                       float(batch_MultiFactor))

                Stock = float(total_stockIN) - float(total_stockOUT)
            elif StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID):
                stock_ins = StockPosting.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                total_stockIN = 0
                total_stockOUT = 0
                for s in stock_ins:
                    total_stockIN += float(s.QtyIn)
                    total_stockOUT += float(s.QtyOut)

                Stock = float(total_stockIN) - float(total_stockOUT)
        else:
            if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID):
                stock_ins = StockPosting.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                total_stockIN = 0
                total_stockOUT = 0
                for s in stock_ins:
                    total_stockIN += float(s.QtyIn)
                    total_stockOUT += float(s.QtyOut)

                Stock = float(total_stockIN) - float(total_stockOUT)

        return Stock

    def get_BatchCode(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        BatchCode = 0
        check_EnableProductBatchWise = False
        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
            check_EnableProductBatchWise = GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
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

        Quantity = float(TotalQtyIn) - float(TotalQtyOut)
        return float(Quantity)

    def get_BrandName(self, instances):
        CompanyID = self.context.get("CompanyID")

        BrandID = instances.BrandID
        BranchID = instances.BranchID
        brand = Brand.objects.get(
            CompanyID=CompanyID, BrandID=BrandID, BranchID=BranchID)
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
                CompanyID=CompanyID, TaxID=VatID, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_GST_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        GST = instances.GST
        BranchID = instances.BranchID
        Inclusive = False
        if GST:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=GST, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_TAX1_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax1 = instances.Tax1
        BranchID = instances.BranchID
        Inclusive = False
        if Tax1:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax1, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_TAX2_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax2 = instances.Tax2
        BranchID = instances.BranchID
        Inclusive = False
        if Tax2:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax2, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_TAX3_inclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        Tax3 = instances.Tax3
        BranchID = instances.BranchID
        Inclusive = False
        if Tax3:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax3, BranchID=BranchID).Inclusive
        return Inclusive

    def get_DefaultUnitID(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        DefaultUnitID = ""
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            DefaultUnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).PriceListID
        # DefaultUnitID = unitInstance.PriceListID
        return DefaultUnitID

    def get_DefUntID(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        DefUntID = ""
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            DefUntID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).UnitID
        # DefUntID = unitInstance.PriceListID
        return DefUntID

    def get_DefBarcode(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        DefBarcode = ""
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            DefBarcode = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).Barcode
        # DefBarcode = unitInstance.PriceListID
        return DefBarcode

    def get_DefaultUnitName(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        DefaultUnitName = ""
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).UnitID
            DefaultUnitName = Unit.objects.get(
                BranchID=BranchID, UnitID=UnitID, CompanyID=CompanyID).UnitName

        return DefaultUnitName

    def get_DefaultSalesPrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
            get_DefaultSalesPrice = unitInstance.SalesPrice
        else:
            get_DefaultSalesPrice = 0

        return get_DefaultSalesPrice

    def get_DefaultMRP(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
            get_DefaultMRP = unitInstance.MRP
        else:
            get_DefaultMRP = 0

        return get_DefaultMRP

    def get_DefaultPurchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            unitInstance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
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
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
            UnitID = priceList.UnitID
            UnitName = Unit.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, UnitID=UnitID).UnitName

        return UnitName

    def get_PurchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
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
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
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
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            priceList = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
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
            CompanyID=CompanyID, ProductGroupID=ProductGroupID, BranchID=BranchID)
        ProductGroupName = product_group.GroupName

        return ProductGroupName

    def get_PriceListDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        price_list = PriceList.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)
        serialized = PriceListRestSerializer(price_list, many=True, context={
                                             "CompanyID": CompanyID, "PriceRounding": PriceRounding})

        return serialized.data

    def get_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
            TaxName = tax.TaxName

        return TaxName

    def get_GST_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.GST
        BranchID = instances.BranchID
        GST_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
            GST_TaxName = tax.TaxName

        return GST_TaxName

    def get_VAT_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        VAT_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
            VAT_TaxName = tax.TaxName

        return VAT_TaxName

    def get_Tax1_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.Tax1
        BranchID = instances.BranchID
        Tax1_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
            Tax1_TaxName = tax.TaxName

        return Tax1_TaxName

    def get_Tax2_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.Tax2
        BranchID = instances.BranchID
        Tax2_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
            Tax2_TaxName = tax.TaxName

        return Tax2_TaxName

    def get_Tax3_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.Tax3
        BranchID = instances.BranchID
        Tax3_TaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
            Tax3_TaxName = tax.TaxName

        return Tax3_TaxName

    def get_PurchaseTax(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        PurchaseTax = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
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
                QtyInRate = float(s.QtyIn) * float(s.Rate)
                TotalQtyIn += s.QtyIn
                TotalQtyInRate += QtyInRate

            Cost = float(TotalQtyInRate) / float(TotalQtyIn)

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

            Qty = float(TotalQtyIn) - float(TotalQtyOut)

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

        return float(round(PurchasePrice, PriceRounding))

    def get_SalesPrice(self, final_instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = final_instance.ProductID
        BranchID = final_instance.BranchID
        SalesPrice = PriceList.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).SalesPrice

        return float(round(SalesPrice, PriceRounding))

    def get_UnitName(self, final_instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = final_instance.ProductID
        BranchID = final_instance.BranchID
        UnitName = ""
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, UnitInReports=True).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, UnitInReports=True).UnitID
            UnitName = Unit.objects.get(
                CompanyID=CompanyID, UnitID=UnitID).UnitName
        else:
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).UnitID
            UnitName = Unit.objects.get(
                CompanyID=CompanyID, UnitID=UnitID).UnitName

        return UnitName

    def get_BaseUnitName(self, final_instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = final_instance.ProductID
        BranchID = final_instance.BranchID
        BaseUnitName = ""
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).UnitID
            BaseUnitName = Unit.objects.get(
                CompanyID=CompanyID, UnitID=UnitID).UnitName

        return BaseUnitName

    def get_is_BasicUnit(self, final_instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = final_instance.ProductID
        BranchID = final_instance.BranchID

        is_BasicUnit = False
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, UnitInReports=True, DefaultUnit=True).exists():

            is_BasicUnit = True

        return is_BasicUnit

    def get_MultiFactor(self, final_instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = final_instance.ProductID
        BranchID = final_instance.BranchID
        MultiFactor = 1
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, UnitInReports=True, DefaultUnit=False).exists():
            MultiFactor = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, UnitInReports=True, DefaultUnit=False).MultiFactor
        return float(MultiFactor)
