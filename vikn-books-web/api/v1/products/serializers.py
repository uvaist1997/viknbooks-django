from rest_framework import serializers
from brands.models import Product, PriceList, Brand, ProductGroup, TaxCategory, Unit, StockPosting, ProductUpload
from api.v1.priceLists.serializers import PriceListRestSerializer


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ('id', 'BranchID', 'ProductCode', 'ProductName', 'DisplayName', 'Description', 'ProductGroupID',
                  'BrandID', 'InventoryType', 'VatID', 'StockMinimum', 'StockReOrder', 'StockMaximum',
                  'MarginPercent', 'Active', 'IsRawMaterial', 'IsWeighingScale', 'WeighingCalcType', 'PLUNo',
                  'IsFavourite', 'CreatedDate', 'CreatedUserID', 'IsFinishedProduct', 'IsSales', 'IsPurchase',"GST","Tax1","Tax2","Tax3")




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

    class Meta:
        model = Product
        fields = ('id', 'ProductID', 'BranchID', 'ProductCode', 'ProductName', 'DisplayName', 'Description', 'ProductGroupID',
                  'BrandID', 'InventoryType', 'VatID', 'StockMinimum', 'StockReOrder', 'StockMaximum','DefUntID',
                  'MarginPercent', 'ProductImage', 'Active', 'IsRawMaterial', 'IsWeighingScale', 'WeighingCalcType', 'PLUNo',
                  'IsFavourite', 'CreatedDate', 'CreatedUserID', 'Action', 'GST', 'GST_PurchaseTax', 'GST_SalesTax', 'SalesTax', 'Tax1', 'Tax1_PurchaseTax', 'Tax1_SalesTax',
                  'Tax2', 'Tax2_PurchaseTax', 'Tax2_SalesTax', 'Tax3', 'Tax3_PurchaseTax', 'Tax3_SalesTax', 'BrandName', 'TaxName', 'ProductGroupName', 'PurchaseTax', 'SalesTax',
                  'IsFinishedProduct', 'IsSales', 'IsPurchase', 'PurchasePrice', 'SalesPrice', 'MRP', 'GST_TaxName', 'VAT_TaxName', 'UnitName', 'Tax1_TaxName', 'Tax2_TaxName', 'Tax3_TaxName',
                  'DefaultUnitID', 'DefaultUnitName', 'DefaultSalesPrice', 'DefaultPurchasePrice',
                  'is_VAT_inclusive', 'is_GST_inclusive', 'is_TAX1_inclusive', 'is_TAX2_inclusive', 'is_TAX3_inclusive', 'PriceListDetails','DefaultMRP')

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
        
        DefaultUnitID = PriceList.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).PriceListID
        # DefaultUnitID = unitInstance.PriceListID
        return DefaultUnitID


    def get_DefUntID(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        
        DefUntID = PriceList.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).UnitID
        # DefUntID = unitInstance.PriceListID
        return DefUntID


    def get_DefaultUnitName(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
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

    class Meta:
        model = Product
        fields = ('id', 'ProductID', 'PriceListID', 'Barcode', 'ProductName',
                  'Stock', 'CostPerItem', 'UnitName', 'ExcessOrShortage', 'StockAdjustment')

    def get_Barcode(self, instances):
        CompanyID = self.context.get("CompanyID")

        ProductID = instances.ProductID
        BranchID = instances.BranchID
        Barcode = ""
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            Barcode = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).AutoBarcode

        return Barcode

    def get_PriceListID(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        PriceListID = PriceList.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).PriceListID
        return PriceListID

    def get_Stock(self, instances):
        CompanyID = self.context.get("CompanyID")
        TotalQtyIn = 0
        TotalQtyOut = 0
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        PriceListID = PriceList.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).PriceListID

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
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            PurchasePrice = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).PurchasePrice
        return float(PurchasePrice)

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

    class Meta:
        model = Product
        fields = ('id', 'ProductID', 'BranchID',
                  'ProductName', 'PriceListID', 'UnitPrice')

    def get_PriceListID(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        ProductID = instances.ProductID

        PriceListID = PriceList.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).PriceListID
        return PriceListID

    def get_UnitPrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        ProductID = instances.ProductID

        UnitPrice = PriceList.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).PurchasePrice
        return UnitPrice


# class UploadSerializer(serializers.Serializer):
#     CompanyID = serializers.CharField(max_length=200)
#     CreatedUserID = serializers.CharField(max_length=200)
#     file = serializers.FileField()


class UploadSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductUpload
        fields = (
            'CompanyID', 
            'CreatedUserID', 
            'file')
