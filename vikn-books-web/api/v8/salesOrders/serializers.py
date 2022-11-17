from rest_framework import serializers
from brands.models import SalesOrderMaster, SerialNumbers, SalesOrderDetails, AccountLedger, Product, PriceList, Unit, TaxCategory
from api.v8.priceLists.serializers import PriceListRestSerializer
from api.v8.sales.serializers import SerialNumberSerializer


class SalesOrderMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalesOrderMaster
        fields = ('id', 'BranchID', 'Action', 'VoucherNo', 'Date',
                  'LedgerID',
                  'PriceCategoryID', 'CustomerName', 'Address1',
                  'Address2', 'Notes', 'FinacialYearID', 'TotalTax', 'NetTotal',
                  'BillDiscount', 'GrandTotal', 'RoundOff',
                  'IsActive', 'IsInvoiced', 'CreatedUserID')


class SalesOrderMasterRestSerializer(serializers.ModelSerializer):

    SalesOrderDetails = serializers.SerializerMethodField()
    # DetailID = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    TotalGrossAmt = serializers.SerializerMethodField()
    NetTotal = serializers.SerializerMethodField()
    is_customer = serializers.SerializerMethodField()

    class Meta:
        model = SalesOrderMaster
        fields = ('id', 'SalesOrderMasterID', 'ShippingCharge', 'shipping_tax_amount', 'TaxTypeID', 'SAC', 'SalesTax', 'BranchID', 'Action', 'VoucherNo', 'Date', 'LedgerID', 'LedgerName',
                  'PriceCategoryID', 'CustomerName', 'Address1', 'TotalGrossAmt', 'TaxID', 'TaxType', 'Country_of_Supply', 'State_of_Supply', 'GST_Treatment', 'TokenNumber', 'Phone',
                  'Address2', 'Notes', 'FinacialYearID', 'TotalTax', 'NetTotal', 'is_customer', 'VATAmount', 'SGSTAmount', 'CGSTAmount', 'IGSTAmount', 'TAX1Amount', 'TAX2Amount', 'TAX3Amount',
                  'BillDiscAmt', 'BillDiscPercent', 'GrandTotal', 'RoundOff', 'DeliveryDate', 'IsActive', 'IsInvoiced', 'CreatedDate', 'UpdatedDate', 'CreatedUserID', 'SalesOrderDetails')

    def get_SalesOrderDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        salesOrder_details = SalesOrderDetails.objects.filter(
            CompanyID=CompanyID, SalesOrderMasterID=instances.SalesOrderMasterID, BranchID=instances.BranchID).order_by('SalesOrderDetailsID')
        serialized = SalesOrderDetailsRestSerializer(salesOrder_details, many=True, context={
                                                     "CompanyID": CompanyID, "PriceRounding": PriceRounding})

        return serialized.data

    def get_is_customer(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        is_customer = False
        groups = [10, 29]
        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=groups).exists():
            is_customer = True

        return is_customer

    def get_TotalTax(self, instances):
        TotalTax = float(instances.TotalTax)
        # TotalTax = round(TotalTax, 2)
        return TotalTax

    def get_GrandTotal(self, instances):
        GrandTotal = float(instances.GrandTotal)
        # GrandTotal = round(GrandTotal, 2)
        return GrandTotal

    def get_TotalGrossAmt(self, instances):
        GrandTotal = float(instances.GrandTotal)
        # GrandTotal = round(GrandTotal, 2)
        return GrandTotal

    def get_NetTotal(self, instances):
        NetTotal = float(instances.NetTotal)
        # NetTotal = round(NetTotal, 2)
        return NetTotal

    def get_DetailID(self, instances):

        return ""

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(
            CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)

        LedgerName = ledger.LedgerName

        return LedgerName


class SalesOrderMaster1RestSerializer(serializers.ModelSerializer):

    LedgerName = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    TotalTax_rounded = serializers.SerializerMethodField()
    GrandTotal_Rounded = serializers.SerializerMethodField()

    class Meta:
        model = SalesOrderMaster
        fields = ('id', 'SalesOrderMasterID', 'TotalTax_rounded', 'GrandTotal_Rounded', 'VoucherNo', 'Date', 'LedgerID', 'LedgerName',
                  'CustomerName', 'TotalTax', 'GrandTotal', 'DeliveryDate', 'IsInvoiced')

    def get_TotalTax(self, instances):
        TotalTax = float(instances.TotalTax)
        TotalTax = round(TotalTax, 2)
        return TotalTax

    def get_GrandTotal(self, instances):
        GrandTotal = float(instances.GrandTotal)
        GrandTotal = round(GrandTotal, 2)
        return GrandTotal

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(
            CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)

        LedgerName = ledger.LedgerName

        return LedgerName

    def get_TotalTax_rounded(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalTax = instances.TotalTax

        TotalTax_rounded = round(TotalTax, PriceRounding)

        return str(TotalTax_rounded)

    def get_GrandTotal_Rounded(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        GrandTotal = instances.GrandTotal

        GrandTotal_Rounded = round(GrandTotal, PriceRounding)

        return str(GrandTotal_Rounded)


class SalesOrderDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalesOrderDetails
        fields = ('id', 'BranchID', 'Action', 'SalesOrderMasterID', 'ProductID',
                  'Qty', 'FreeQty', 'UnitPrice',
                  'RateWithTax', 'PriceListID', 'DiscountPerc', 'DiscountAmount',
                  'GrossAmount', 'TaxableAmount', 'VATPerc', 'VATAmount', 'SGSTPerc', 'SGSTAmount', 'CGSTPerc',
                  'CGSTAmount', 'IGSTPerc', 'IGSTAmount', 'NetAmount', 'CreatedUserID')


class SalesOrderDetailsRestSerializer(serializers.ModelSerializer):

    Qty = serializers.SerializerMethodField()
    FreeQty = serializers.SerializerMethodField()
    ReturnQty = serializers.SerializerMethodField()
    UnitPrice = serializers.SerializerMethodField()
    InclusivePrice = serializers.SerializerMethodField()
    RateWithTax = serializers.SerializerMethodField()
    CostPerPrice = serializers.SerializerMethodField()
    DiscountPerc = serializers.SerializerMethodField()
    DiscountAmount = serializers.SerializerMethodField()
    AddlDiscPerc = serializers.SerializerMethodField()
    AddlDiscAmt = serializers.SerializerMethodField()
    GrossAmount = serializers.SerializerMethodField()
    TaxableAmount = serializers.SerializerMethodField()
    VATPerc = serializers.SerializerMethodField()
    VATAmount = serializers.SerializerMethodField()
    SGSTPerc = serializers.SerializerMethodField()
    SGSTAmount = serializers.SerializerMethodField()
    CGSTPerc = serializers.SerializerMethodField()
    CGSTAmount = serializers.SerializerMethodField()
    IGSTPerc = serializers.SerializerMethodField()
    IGSTAmount = serializers.SerializerMethodField()
    NetAmount = serializers.SerializerMethodField()
    ProductName = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()
    unq_id = serializers.SerializerMethodField()
    detailID = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    TAX1Amount = serializers.SerializerMethodField()
    TAX1Perc = serializers.SerializerMethodField()
    TAX2Amount = serializers.SerializerMethodField()
    TAX2Perc = serializers.SerializerMethodField()
    TAX3Perc = serializers.SerializerMethodField()
    TAX3Amount = serializers.SerializerMethodField()
    DeliveryDetailsID = serializers.SerializerMethodField()
    OrderDetailsID = serializers.SerializerMethodField()
    ExistingQty = serializers.SerializerMethodField()
    is_VAT_inclusive = serializers.SerializerMethodField()
    is_GST_inclusive = serializers.SerializerMethodField()
    is_TAX1_inclusive = serializers.SerializerMethodField()
    is_TAX2_inclusive = serializers.SerializerMethodField()
    is_TAX3_inclusive = serializers.SerializerMethodField()
    unitPriceRounded = serializers.SerializerMethodField()
    quantityRounded = serializers.SerializerMethodField()
    actualSalesPrice = serializers.SerializerMethodField()
    netAmountRounded = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    BatchCode = serializers.SerializerMethodField()
    UnitList = serializers.SerializerMethodField()
    SerialNos = serializers.SerializerMethodField()
    Flavour = serializers.SerializerMethodField()
    is_inclusive = serializers.SerializerMethodField()
    ActualUnitPrice = serializers.SerializerMethodField()
    ProductCode = serializers.SerializerMethodField()
    HSNCode = serializers.SerializerMethodField()
    ProductTaxName = serializers.SerializerMethodField()
    GST_Inclusive = serializers.SerializerMethodField()
    Vat_Inclusive = serializers.SerializerMethodField()
    SalesPrice = serializers.SerializerMethodField()
    ActualProductTaxID = serializers.SerializerMethodField()
    ActualProductTaxName = serializers.SerializerMethodField()
    SalesDetailsID = serializers.SerializerMethodField()
    gstPer = serializers.SerializerMethodField()
    TotalTaxRounded = serializers.SerializerMethodField()
    Description = serializers.SerializerMethodField()

    class Meta:
        model = SalesOrderDetails
        fields = ('id', 'unq_id', 'SalesOrderDetailsID', 'BranchID', 'Action', 'SalesOrderMasterID', 'ProductID', 'ProductName',
                  'Qty', 'FreeQty', 'UnitPrice', 'ReturnQty', 'InclusivePrice', 'AddlDiscPerc', 'AddlDiscAmt', 'UnitList', 'ProductTaxID',
                  'RateWithTax', 'CostPerPrice', 'PriceListID', 'UnitName', 'DiscountPerc', 'DiscountAmount', 'Flavour', 'ActualProductTaxID',
                  'GrossAmount', 'TaxableAmount', 'VATPerc', 'VATAmount', 'SGSTPerc', 'SGSTAmount', 'CGSTPerc', 'SerialNos', 'ActualProductTaxName',
                  'CGSTAmount', 'IGSTPerc', 'IGSTAmount', 'KFCAmount', 'NetAmount', 'CreatedDate', 'CreatedUserID', 'ActualUnitPrice',
                  'TAX1Perc', 'TAX1Amount', 'TAX2Perc', 'TAX2Amount', 'TAX3Perc', 'TAX3Amount', 'TotalTax', 'DeliveryDetailsID', 'OrderDetailsID', 'detailID', 'ExistingQty',
                  'is_VAT_inclusive', 'is_GST_inclusive', 'is_TAX1_inclusive', 'is_TAX2_inclusive', 'is_TAX3_inclusive',
                  'unitPriceRounded', 'quantityRounded', 'actualSalesPrice', 'netAmountRounded', 'BatchCode', 'is_inclusive', "ProductCode", "HSNCode",
                  'ProductTaxName', 'GST_Inclusive', 'Vat_Inclusive', 'SalesPrice', 'SalesDetailsID', 'gstPer', 'TotalTaxRounded', 'Description')

    def get_ActualProductTaxID(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductTaxID = sales_details.ProductTaxID
        return ProductTaxID

    def get_Description(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID
        Description = ""
        if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
            instance = Product.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
            Description = instance.Description
        return Description

    def get_TotalTaxRounded(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        TAX1Amount = sales_details.TAX1Amount
        TAX2Amount = sales_details.TAX2Amount
        TAX3Amount = sales_details.TAX3Amount
        VATAmount = sales_details.VATAmount
        IGSTAmount = sales_details.IGSTAmount
        SGSTAmount = sales_details.SGSTAmount
        CGSTAmount = sales_details.CGSTAmount

        TotalTax = (TAX1Amount + TAX2Amount + TAX3Amount +
                    VATAmount + CGSTAmount + SGSTAmount + IGSTAmount)
        return TotalTax

    def get_gstPer(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        IGSTPerc = sales_details.IGSTPerc
        return IGSTPerc

    def get_SalesDetailsID(self, sales_details):
        SalesDetailsID = 1
        return SalesDetailsID

    def get_ActualProductTaxName(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductTaxID = sales_details.ProductTaxID
        BranchID = sales_details.BranchID
        ProductTaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, BranchID=BranchID, TaxID=ProductTaxID).exists():
            ProductTaxName = TaxCategory.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, TaxID=ProductTaxID).TaxName
        return ProductTaxName

    def get_Vat_Inclusive(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        ProductTaxID = sales_details.ProductTaxID
        if ProductTaxID:
            VatID = ProductTaxID
        else:
            VatID = Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).VatID
        Inclusive = False
        if VatID:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=VatID, BranchID=BranchID).Inclusive
        return Inclusive

    def get_GST_Inclusive(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        ProductTaxID = sales_details.ProductTaxID
        Inclusive = False
        if ProductTaxID:
            GST = ProductTaxID
        else:
            GST = Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).GST
        if GST:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=GST, BranchID=BranchID).Inclusive
        return Inclusive

    def get_SalesPrice(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = sales_details.PriceListID
        BranchID = sales_details.BranchID
        SalesPrice = 0
        if PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID).exists():
            SalesPrice = PriceList.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID).SalesPrice
        return float(SalesPrice)

    def get_ProductTaxName(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductTaxID = sales_details.ProductTaxID
        BranchID = sales_details.BranchID
        ProductTaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, BranchID=BranchID, TaxID=ProductTaxID).exists():
            ProductTaxName = TaxCategory.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, TaxID=ProductTaxID).TaxName
        return ProductTaxName

    def get_ProductName(self, sales_details):

        CompanyID = self.context.get("CompanyID")

        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID

        product = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)

        ProductName = product.ProductName
        return ProductName

    def get_ProductCode(self, sales_details):

        CompanyID = self.context.get("CompanyID")

        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID

        product = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)

        ProductCode = product.ProductCode
        return ProductCode

    def get_HSNCode(self, sales_details):

        CompanyID = self.context.get("CompanyID")

        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID

        product = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)

        HSNCode = product.HSNCode
        return HSNCode

    def get_UnitList(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID

        UnitList = PriceList.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)

        serialized = PriceListRestSerializer(UnitList, many=True, context={
                                             "CompanyID": CompanyID, "PriceRounding": PriceRounding})

        return serialized.data

    def get_ActualUnitPrice(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        ActualUnitPrice = purchase_details.UnitPrice

        # ActualUnitPrice = round(ActualUnitPrice, PriceRounding)
        return str(ActualUnitPrice)

    def get_SerialNos(self, sales_details):
        SerialNos = []
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        SalesMasterID = sales_details.SalesOrderMasterID
        SalesDetailsID = sales_details.SalesOrderDetailsID
        if SerialNumbers.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SalesMasterID=SalesMasterID, SalesDetailsID=SalesDetailsID, VoucherType="SO").exists():
            Serial_details = SerialNumbers.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, SalesMasterID=SalesMasterID, SalesDetailsID=SalesDetailsID, VoucherType="SO")
            SerialNos = SerialNumberSerializer(
                Serial_details, many=True, context={"CompanyID": CompanyID})
            SerialNos = SerialNos.data
        return SerialNos

    def get_BatchCode(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        BatchCode = sales_details.BatchCode
        BranchID = sales_details.BranchID
        if not BatchCode:
            BatchCode = 0

        return BatchCode

    def get_id(self, instances):
        id = instances.id

        return str(id)

    def get_Flavour(self, instances):
        Flavour = ""

        return Flavour

    def get_InclusivePrice(self, sales_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        # PriceRounding = 2
        InclusivePrice = sales_details.InclusivePrice
        if InclusivePrice:
            # InclusivePrice = round(InclusivePrice, PriceRounding)
            InclusivePrice = InclusivePrice
        else:
            InclusivePrice = 0

        return float(InclusivePrice)

    def get_unitPriceRounded(self, sales_details):
        UnitPrice = sales_details.UnitPrice
        return float(UnitPrice)

    def get_quantityRounded(self, sales_details):
        Qty = sales_details.Qty
        return float(Qty)

    def get_actualSalesPrice(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = sales_details.PriceListID
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        SalesPrice = 0
        if PriceList.objects.filter(ProductID=ProductID, CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).exists():
            SalesPrice = PriceList.objects.get(
                ProductID=ProductID, CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).SalesPrice
        return float(SalesPrice)

    def get_netAmountRounded(self, sales_details):
        NetAmount = sales_details.NetAmount
        return float(NetAmount)

    def get_is_inclusive(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        is_inclusive = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).is_inclusive

        return is_inclusive

    # def get_is_inclusive(self, sales_details):
    #     CompanyID = self.context.get("CompanyID")
    #     BranchID = sales_details.BranchID
    #     ProductID = sales_details.ProductID
    #     GST = Product.objects.get(
    #         CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).GST
    #     GstInclusive = False
    #     if GST:
    #         GstInclusive = TaxCategory.objects.get(
    #             CompanyID=CompanyID, TaxID=GST, BranchID=BranchID).Inclusive

    #     VatID = Product.objects.get(
    #         CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).VatID
    #     VatInclusive = TaxCategory.objects.get(
    #         CompanyID=CompanyID, TaxID=VatID, BranchID=BranchID).Inclusive
    #     Inclusive = False
    #     if GstInclusive == True or VatInclusive == True:
    #         Inclusive == True

    #     return Inclusive

    def get_is_VAT_inclusive(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        VatID = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).VatID
        Inclusive = TaxCategory.objects.get(
            CompanyID=CompanyID, TaxID=VatID, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_GST_inclusive(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        GST = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).GST
        Inclusive = False
        if GST:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=GST, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_TAX1_inclusive(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        Tax1 = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).Tax1
        Inclusive = False
        if Tax1:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax1, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_TAX2_inclusive(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        Tax2 = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).Tax2
        Inclusive = False
        if Tax2:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax2, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_TAX3_inclusive(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        Tax3 = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).Tax3
        Inclusive = False
        if Tax3:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax3, BranchID=BranchID).Inclusive
        return Inclusive

    def get_ExistingQty(self, sales_details):
        Qty = sales_details.Qty
        ExistingQty = Qty
        return float(ExistingQty)

    def get_DeliveryDetailsID(self, instances):

        return 1

    def get_OrderDetailsID(self, instances):

        return 1

    def get_TotalTax(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        TAX1Amount = purchase_details.TAX1Amount
        TAX2Amount = purchase_details.TAX2Amount
        TAX3Amount = purchase_details.TAX3Amount
        VATAmount = purchase_details.VATAmount
        IGSTAmount = purchase_details.IGSTAmount
        SGSTAmount = purchase_details.SGSTAmount
        CGSTAmount = purchase_details.CGSTAmount

        TotalTax = (TAX1Amount + TAX2Amount + TAX3Amount +
                    VATAmount + CGSTAmount + SGSTAmount + IGSTAmount)

        return float(TotalTax)

    def get_unq_id(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        unq_id = purchase_details.id

        return str(unq_id)

    def get_detailID(self, purchase_details):

        detailID = 0

        return detailID

    def get_UnitName(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        PriceListID = purchase_details.PriceListID
        BranchID = purchase_details.BranchID

        if PriceList.objects.filter(CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).UnitID
            UnitName = Unit.objects.get(
                BranchID=BranchID, UnitID=UnitID, CompanyID=CompanyID).UnitName
        else:
            UnitName = ""

        return UnitName

    def get_Qty(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        Qty = sales_details.Qty

        # Qty = round(Qty, PriceRounding)

        return float(Qty)

    def get_FreeQty(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        FreeQty = sales_details.FreeQty

        # FreeQty = round(FreeQty, PriceRounding)

        return float(FreeQty)

    def get_ReturnQty(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        ReturnQty = sales_details.Qty

        # ReturnQty = round(Qty, PriceRounding)

        return float(ReturnQty)

    def get_UnitPrice(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        UnitPrice = sales_details.UnitPrice

        # UnitPrice = round(UnitPrice, PriceRounding)

        return float(UnitPrice)

    def get_RateWithTax(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        RateWithTax = sales_details.RateWithTax

        # RateWithTax = round(RateWithTax, PriceRounding)

        return float(RateWithTax)

    def get_CostPerPrice(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        # CostPerPrice = sales_details.CostPerPrice

        CostPerPrice = 0

        return float(CostPerPrice)

    def get_DiscountPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        DiscountPerc = sales_details.DiscountPerc

        # DiscountPerc = round(DiscountPerc, PriceRounding)

        return float(DiscountPerc)

    def get_DiscountAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        DiscountAmount = sales_details.DiscountAmount

        # DiscountAmount = round(DiscountAmount, PriceRounding)

        return float(DiscountAmount)

    def get_GrossAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        GrossAmount = sales_details.GrossAmount

        # GrossAmount = round(GrossAmount, PriceRounding)

        return float(GrossAmount)

    def get_TaxableAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TaxableAmount = sales_details.TaxableAmount

        # TaxableAmount = round(TaxableAmount, PriceRounding)

        return float(TaxableAmount)

    def get_VATPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        VATPerc = sales_details.VATPerc

        # VATPerc = round(VATPerc, PriceRounding)

        return float(VATPerc)

    def get_VATAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        VATAmount = sales_details.VATAmount

        # VATAmount = round(VATAmount, PriceRounding)

        return float(VATAmount)

    def get_SGSTPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        SGSTPerc = sales_details.SGSTPerc

        # SGSTPerc = round(SGSTPerc, PriceRounding)

        return float(SGSTPerc)

    def get_SGSTAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        SGSTAmount = sales_details.SGSTAmount

        # SGSTAmount = round(SGSTAmount, PriceRounding)

        return float(SGSTAmount)

    def get_CGSTPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        CGSTPerc = sales_details.CGSTPerc

        # CGSTPerc = round(CGSTPerc, PriceRounding)

        return float(CGSTPerc)

    def get_CGSTAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        CGSTAmount = sales_details.CGSTAmount

        # CGSTAmount = round(CGSTAmount, PriceRounding)

        return float(CGSTAmount)

    def get_IGSTPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        IGSTPerc = sales_details.IGSTPerc

        # IGSTPerc = round(IGSTPerc, PriceRounding)

        return float(IGSTPerc)

    def get_IGSTAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        IGSTAmount = sales_details.IGSTAmount

        # IGSTAmount = round(IGSTAmount, PriceRounding)

        return float(IGSTAmount)

    def get_NetAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        NetAmount = sales_details.NetAmount

        # NetAmount = round(NetAmount, PriceRounding)

        return float(NetAmount)

    def get_AddlDiscPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")

        AddlDiscPerc = 0

        return float(AddlDiscPerc)

    def get_AddlDiscAmt(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")

        AddlDiscAmt = 0

        return float(AddlDiscAmt)

    def get_TAX1Perc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX1Perc = sales_details.TAX1Perc

        if not TAX1Perc:
            TAX1Perc = 0

        return float(TAX1Perc)

    def get_TAX2Perc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX2Perc = sales_details.TAX2Perc

        if not TAX2Perc:
            TAX2Perc = 0

        return float(TAX2Perc)

    def get_TAX3Perc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX3Perc = sales_details.TAX3Perc

        if not TAX3Perc:
            TAX3Perc = 0

        return float(TAX3Perc)

    def get_TAX1Amount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX1Amount = sales_details.TAX1Amount

        if not TAX1Amount:
            TAX1Amount = 0

        return float(TAX1Amount)

    def get_TAX2Amount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX2Amount = sales_details.TAX2Amount

        if not TAX2Amount:
            TAX2Amount = 0

        return float(TAX2Amount)

    def get_TAX3Amount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX3Amount = sales_details.TAX3Amount

        if not TAX3Amount:
            TAX3Amount = 0

        return float(TAX3Amount)


class SalesOrderReportSerializer(serializers.ModelSerializer):

    LedgerName = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    NetTotal = serializers.SerializerMethodField()

    class Meta:
        model = SalesOrderMaster
        fields = ('id', 'SalesOrderMasterID', 'BranchID', 'Action', 'VoucherNo', 'Date',
                  'LedgerID', 'LedgerName', 'CustomerName', 'IsInvoiced', 'TotalTax', 'NetTotal', 'GrandTotal')

    def get_TotalTax(self, instances):
        TotalTax = float(instances.TotalTax)
        TotalTax = round(TotalTax, 2)
        return TotalTax

    def get_NetTotal(self, instances):
        NetTotal = float(instances.NetTotal)
        NetTotal = round(NetTotal, 2)
        return NetTotal

    def get_GrandTotal(self, instances):
        GrandTotal = float(instances.GrandTotal)
        GrandTotal = round(GrandTotal, 2)
        return GrandTotal

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(
            LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID)

        LedgerName = ledger.LedgerName

        return LedgerName
