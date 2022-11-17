from rest_framework import serializers
from brands.models import PurchaseOrderMaster, PurchaseOrderDetails, AccountLedger, Product, PriceList, Unit, TaxCategory
from api.v5.priceLists.serializers import PriceListRestSerializer
import datetime as dt
import calendar


class PurchaseOrderMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseOrderMaster
        fields = ('id', 'BranchID', 'Action', 'VoucherNo', 'Date',
                  'LedgerID',
                  'PriceCategoryID', 'CustomerName', 'Address1',
                  'Address2', 'Notes', 'FinacialYearID', 'TotalTax', 'NetTotal',
                  'BillDiscount', 'GrandTotal', 'RoundOff', 'IsActive',)


class PurchaseOrderMaster1RestSerializer(serializers.ModelSerializer):

    LedgerName = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    TotalTax_rounded = serializers.SerializerMethodField()
    GrandTotal_Rounded = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderMaster
        fields = ('id', 'PurchaseOrderMasterID', 'VoucherNo', 'Date', 'TotalTax_rounded',
                  'GrandTotal_Rounded', 'LedgerName', 'CustomerName', 'DeliveryDate', 'TotalTax', 'IsInvoiced',  'GrandTotal')

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
            LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID)

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


class PurchaseOrderMasterRestSerializer(serializers.ModelSerializer):

    PurchaseOrderDetails = serializers.SerializerMethodField()
    DetailID = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    TotalGrossAmt = serializers.SerializerMethodField()
    TotalDiscount = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderMaster
        fields = ('id', 'PurchaseOrderMasterID','ShippingCharge','shipping_tax_amount','TaxTypeID','SAC','PurchaseTax', 'BranchID', 'Action', 'VoucherNo', 'Date', 'DetailID',
                  'LedgerID', 'LedgerName', 'VATAmount', 'SGSTAmount', 'CGSTAmount', 'IGSTAmount', 'TAX1Amount', 'TAX2Amount', 'TAX3Amount',
                  'PriceCategoryID', 'CustomerName', 'Address1', 'DeliveryDate', 'IsInvoiced',
                  'Address2', 'Notes', 'FinacialYearID', 'TotalTax', 'NetTotal', 'TaxID', 'TaxType', 'TotalGrossAmt', 'TotalDiscount',
                  'BillDiscount', 'GrandTotal', 'RoundOff', 'IsActive', 'CreatedDate', 'UpdatedDate', 'CreatedUserID', 'PurchaseOrderDetails', 'BillDiscPercent', 'BillDiscAmt')

    def get_PurchaseOrderDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        print("CompanyID============")
        print(CompanyID)
        PriceRounding = self.context.get("PriceRounding")

        purchaseOrder_details = PurchaseOrderDetails.objects.filter(
            PurchaseOrderMasterID=instances.PurchaseOrderMasterID, BranchID=instances.BranchID).order_by('PurchaseOrderDetailsID')
        serialized = PurchaseOrderDetailsRestSerializer(purchaseOrder_details, many=True, context={
                                                        "PriceRounding": PriceRounding, "CompanyID": CompanyID})

        return serialized.data

    def get_DetailID(self, instances):

        return ""

    def get_TotalTax(self, instances):
        TotalTax = float(instances.TotalTax)
        # TotalTax = round(TotalTax, 2)
        return TotalTax

    def get_GrandTotal(self, instances):
        GrandTotal = float(instances.GrandTotal)
        # GrandTotal = round(GrandTotal, 2)
        return GrandTotal

    def get_TotalDiscount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalDiscount = instances.TotalDiscount
        # if not TotalDiscount == None:
        #     TotalDiscount = round(TotalDiscount, PriceRounding)
        # else:
        #     TotalDiscount = 0

        return str(TotalDiscount)

    def get_TotalGrossAmt(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalGrossAmt = instances.TotalGrossAmt

        # TotalGrossAmt = round(TotalGrossAmt, PriceRounding)

        return str(TotalGrossAmt)

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(
            LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID)

        LedgerName = ledger.LedgerName

        return LedgerName


class PurchaseOrderDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseOrderDetails
        fields = ('id', 'BranchID', 'ProductID',
                  'Qty', 'FreeQty', 'UnitPrice',
                  'RateWithTax', 'CostPerItem', 'PriceListID', 'DiscountPerc',
                  'DiscountAmount', 'GrossAmount', 'TaxableAmount', 'VATPerc', 'VATAmount',
                  'SGSTPerc', 'SGSTAmount', 'CGSTPerc', 'CGSTAmount', 'IGSTPerc', 'IGSTAmount',
                  'NetAmount')


class PurchaseOrderDetailsRestSerializer(serializers.ModelSerializer):
    Qty = serializers.SerializerMethodField()
    FreeQty = serializers.SerializerMethodField()
    ReturnQty = serializers.SerializerMethodField()
    UnitPrice = serializers.SerializerMethodField()
    InclusivePrice = serializers.SerializerMethodField()
    RateWithTax = serializers.SerializerMethodField()
    CostPerItem = serializers.SerializerMethodField()
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
    ExistingQty = serializers.SerializerMethodField()
    is_VAT_inclusive = serializers.SerializerMethodField()
    is_GST_inclusive = serializers.SerializerMethodField()
    is_TAX1_inclusive = serializers.SerializerMethodField()
    is_TAX2_inclusive = serializers.SerializerMethodField()
    is_TAX3_inclusive = serializers.SerializerMethodField()
    unitPriceRounded = serializers.SerializerMethodField()
    quantityRounded = serializers.SerializerMethodField()
    actualSalesPrice = serializers.SerializerMethodField()
    actualPurchasePrice = serializers.SerializerMethodField()
    netAmountRounded = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    BatchCode = serializers.SerializerMethodField()
    UnitList = serializers.SerializerMethodField()
    Flavour = serializers.SerializerMethodField()
    ManufactureDate = serializers.SerializerMethodField()
    ExpiryDate = serializers.SerializerMethodField()
    ActualUnitPrice = serializers.SerializerMethodField()
    ProductCode = serializers.SerializerMethodField()
    HSNCode = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderDetails
        fields = ('id', 'PurchaseOrderDetailsID', 'BranchID', 'Action', 'BatchID', 'PurchaseOrderMasterID',
                  'ProductID', 'Qty', 'FreeQty', 'InclusivePrice', 'ProductName', 'ReturnQty', 'AddlDiscPerc', 'AddlDiscAmt',
                  'UnitPrice', 'RateWithTax', 'CostPerItem', 'PriceListID', 'DiscountPerc', 'UnitName', 'unq_id', 'detailID',
                  'DiscountAmount', 'GrossAmount', 'TaxableAmount', 'VATPerc', 'VATAmount', 'SGSTPerc', 'SGSTAmount', 'ManufactureDate', 'ExpiryDate',
                  'CGSTPerc', 'CGSTAmount', 'IGSTPerc', 'IGSTAmount', 'NetAmount', 'TotalTax', 'TAX1Amount', 'TAX1Perc', 'ActualUnitPrice',
                  'TAX2Amount', 'TAX2Perc', 'TAX3Perc', 'TAX3Amount', 'ExistingQty', 'is_VAT_inclusive', 'is_GST_inclusive', 'is_TAX1_inclusive', 'is_TAX2_inclusive', 'is_TAX3_inclusive',
                  'unitPriceRounded', 'quantityRounded', 'actualSalesPrice', 'actualPurchasePrice', 'netAmountRounded', 'BatchCode', 'UnitList', 'Flavour', "ProductCode", "HSNCode")

    def get_ProductName(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        ProductID = purchase_details.ProductID
        BranchID = purchase_details.BranchID

        print("=====---------------------->")
        print(CompanyID)
        print(ProductID)
        print(BranchID)

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

    def get_ActualUnitPrice(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        ActualUnitPrice = purchase_details.UnitPrice

        # ActualUnitPrice = round(ActualUnitPrice, PriceRounding)
        return str(ActualUnitPrice)

    def get_UnitList(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = purchase_details.ProductID
        BranchID = purchase_details.BranchID

        UnitList = PriceList.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)

        serialized = PriceListRestSerializer(UnitList, many=True, context={
                                             "CompanyID": CompanyID, "PriceRounding": PriceRounding})
        return serialized.data

    def get_BatchCode(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        BatchCode = purchase_details.BatchCode
        BranchID = purchase_details.BranchID
        if not BatchCode:
            BatchCode = 0

        return BatchCode

    def get_ManufactureDate(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        ManufactureDate = dt.datetime.now().date()

        return ManufactureDate

    def get_ExpiryDate(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        day = dt.datetime.now().date()
        one_year_delta = dt.timedelta(days=366 if ((day.month >= 3 and calendar.isleap(day.year+1)) or
                                                   (day.month < 3 and calendar.isleap(day.year))) else 365)

        ExpiryDate = day + one_year_delta
        return ExpiryDate

    def get_id(self, instances):
        id = instances.id

        return str(id)

    def get_Flavour(self, instances):
        Flavour = ""

        return Flavour

    def get_InclusivePrice(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        # PriceRounding = 2
        InclusivePrice = purchase_details.InclusivePrice
        if not InclusivePrice:
            InclusivePrice = 0

        return float(InclusivePrice)

    def get_unitPriceRounded(self, purchase_details):
        UnitPrice = purchase_details.UnitPrice
        return float(UnitPrice)

    def get_quantityRounded(self, purchase_details):
        Qty = purchase_details.Qty
        return float(Qty)

    def get_actualSalesPrice(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = purchase_details.PriceListID
        BranchID = purchase_details.BranchID
        ProductID = purchase_details.ProductID
        SalesPrice = 0
        if PriceList.objects.filter(ProductID=ProductID, CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).exists():
            SalesPrice = PriceList.objects.get(
                ProductID=ProductID, CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).SalesPrice
        return float(SalesPrice)

    def get_actualPurchasePrice(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = purchase_details.PriceListID
        BranchID = purchase_details.BranchID
        ProductID = purchase_details.ProductID
        PurchasePrice = ''
        if PriceList.objects.filter(ProductID=ProductID, CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).exists():
            PurchasePrice = PriceList.objects.get(
                ProductID=ProductID, CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).PurchasePrice
        return PurchasePrice

    def get_netAmountRounded(self, purchase_details):
        NetAmount = purchase_details.NetAmount
        return float(NetAmount)

    def get_is_VAT_inclusive(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchase_details.BranchID
        ProductID = purchase_details.ProductID
        VatID = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).VatID
        Inclusive = TaxCategory.objects.get(
            CompanyID=CompanyID, TaxID=VatID, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_GST_inclusive(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchase_details.BranchID
        ProductID = purchase_details.ProductID
        GST = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).GST
        Inclusive = False
        if GST:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=GST, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_TAX1_inclusive(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchase_details.BranchID
        ProductID = purchase_details.ProductID
        Tax1 = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).Tax1
        Inclusive = False
        if Tax1:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax1, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_TAX2_inclusive(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchase_details.BranchID
        ProductID = purchase_details.ProductID
        Tax2 = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).Tax2
        Inclusive = False
        if Tax2:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax2, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_TAX3_inclusive(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchase_details.BranchID
        ProductID = purchase_details.ProductID
        Tax3 = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).Tax3
        Inclusive = False
        if Tax3:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax3, BranchID=BranchID).Inclusive
        return Inclusive

    def get_ExistingQty(self, purchase_details):
        Qty = purchase_details.Qty
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
        IGSTAmount = purchase_details.IGSTAmount

        TotalTax = (TAX1Amount + TAX2Amount + TAX3Amount +
                    VATAmount + IGSTAmount + SGSTAmount + IGSTAmount)

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

    def get_Qty(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        Qty = purchase_details.Qty

        # Qty = round(Qty, PriceRounding)

        return float(Qty)

    def get_FreeQty(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        FreeQty = purchase_details.FreeQty

        # FreeQty = round(FreeQty, PriceRounding)

        return float(FreeQty)

    def get_ReturnQty(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        Qty = purchase_details.Qty

        ReturnQty = Qty

        return float(ReturnQty)

    def get_UnitPrice(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        UnitPrice = purchase_details.UnitPrice

        # UnitPrice = round(UnitPrice, PriceRounding)

        return float(UnitPrice)

    def get_RateWithTax(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        RateWithTax = purchase_details.RateWithTax

        # RateWithTax = round(RateWithTax, PriceRounding)

        return float(RateWithTax)

    def get_CostPerItem(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        # CostPerPrice = purchase_details.CostPerPrice

        CostPerPrice = 0

        return float(CostPerPrice)

    def get_DiscountPerc(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        DiscountPerc = purchase_details.DiscountPerc

        # DiscountPerc = round(DiscountPerc, PriceRounding)

        return float(DiscountPerc)

    def get_DiscountAmount(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        DiscountAmount = purchase_details.DiscountAmount

        # DiscountAmount = round(DiscountAmount, PriceRounding)

        return float(DiscountAmount)

    def get_GrossAmount(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        GrossAmount = purchase_details.GrossAmount

        # GrossAmount = round(GrossAmount, PriceRounding)

        return float(GrossAmount)

    def get_TaxableAmount(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        TaxableAmount = purchase_details.TaxableAmount

        # TaxableAmount = round(TaxableAmount, PriceRounding)

        return float(TaxableAmount)

    def get_VATPerc(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        VATPerc = purchase_details.VATPerc

        # VATPerc = round(VATPerc, PriceRounding)

        return float(VATPerc)

    def get_VATAmount(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        VATAmount = purchase_details.VATAmount

        # VATAmount = round(VATAmount, PriceRounding)

        return float(VATAmount)

    def get_SGSTPerc(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        SGSTPerc = purchase_details.SGSTPerc

        # SGSTPerc = round(SGSTPerc, PriceRounding)

        return float(SGSTPerc)

    def get_SGSTAmount(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        SGSTAmount = purchase_details.SGSTAmount

        # SGSTAmount = round(SGSTAmount, PriceRounding)

        return float(SGSTAmount)

    def get_CGSTPerc(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        CGSTPerc = purchase_details.CGSTPerc

        # CGSTPerc = round(CGSTPerc, PriceRounding)

        return float(CGSTPerc)

    def get_CGSTAmount(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        CGSTAmount = purchase_details.CGSTAmount

        # CGSTAmount = round(CGSTAmount, PriceRounding)

        return float(CGSTAmount)

    def get_IGSTPerc(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        IGSTPerc = purchase_details.IGSTPerc

        # IGSTPerc = round(IGSTPerc, PriceRounding)

        return float(IGSTPerc)

    def get_IGSTAmount(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        IGSTAmount = purchase_details.IGSTAmount

        # IGSTAmount = round(IGSTAmount, PriceRounding)

        return float(IGSTAmount)

    def get_NetAmount(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        NetAmount = purchase_details.NetAmount

        # NetAmount = round(NetAmount, PriceRounding)

        return float(NetAmount)

    def get_AddlDiscPerc(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")

        AddlDiscPerc = 0

        return float(AddlDiscPerc)

    def get_AddlDiscAmt(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")

        AddlDiscAmt = 0

        return float(AddlDiscAmt)

    def get_TAX1Perc(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX1Perc = purchase_details.TAX1Perc

        if not TAX1Perc:
            TAX1Perc = 0

        return float(TAX1Perc)

    def get_TAX2Perc(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX2Perc = purchase_details.TAX2Perc

        if not TAX2Perc:
            TAX2Perc = 0

        return float(TAX2Perc)

    def get_TAX3Perc(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX3Perc = purchase_details.TAX3Perc

        if not TAX3Perc:
            TAX3Perc = 0

        return float(TAX3Perc)

    def get_TAX1Amount(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX1Amount = purchase_details.TAX1Amount

        if not TAX1Amount:
            TAX1Amount = 0

        return float(TAX1Amount)

    def get_TAX2Amount(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX2Amount = purchase_details.TAX2Amount

        if not TAX2Amount:
            TAX2Amount = 0

        return float(TAX2Amount)

    def get_TAX3Amount(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX3Amount = purchase_details.TAX3Amount

        if not TAX3Amount:
            TAX3Amount = 0

        return float(TAX3Amount)


class PurchaseOrderReportSerializer(serializers.ModelSerializer):

    LedgerName = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    NetTotal = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderMaster
        fields = ('id', 'PurchaseOrderMasterID', 'BranchID', 'Action', 'VoucherNo', 'Date',
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


class PurchaseOrderPrintSerializer(serializers.ModelSerializer):

    PurchaseOrderDetails = serializers.SerializerMethodField()
    DetailID = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderMaster
        fields = ('id', 'PurchaseOrderMasterID', 'BranchID', 'Action', 'VoucherNo', 'Date', 'DetailID',
                  'LedgerID', 'LedgerName', 'VATAmount', 'SGSTAmount', 'CGSTAmount', 'IGSTAmount', 'TAX1Amount', 'TAX2Amount', 'TAX3Amount',
                  'PriceCategoryID', 'CustomerName', 'Address1', 'DeliveryDate', 'IsInvoiced',
                  'Address2', 'Notes', 'FinacialYearID', 'TotalTax', 'NetTotal', 'TaxID', 'TaxType',
                  'BillDiscount', 'GrandTotal', 'RoundOff', 'IsActive', 'CreatedDate', 'UpdatedDate', 'CreatedUserID', 'PurchaseOrderDetails')

    def get_PurchaseOrderDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        purchaseOrder_details = PurchaseOrderDetails.objects.filter(
            PurchaseOrderMasterID=instances.PurchaseOrderMasterID, BranchID=instances.BranchID)
        serialized = PurchaseDetailsPrintSerializer(purchaseOrder_details, many=True, context={
            "PriceRounding": PriceRounding, "CompanyID": CompanyID})

        return serialized.data

    def get_DetailID(self, instances):

        return ""

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
            LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID)

        LedgerName = ledger.LedgerName

        return LedgerName


class PurchaseDetailsPrintSerializer(serializers.ModelSerializer):

    Qty = serializers.SerializerMethodField()
    UnitPrice = serializers.SerializerMethodField()
    NetAmount = serializers.SerializerMethodField()
    ProductName = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderDetails
        fields = ('ProductName', 'Qty', 'UnitPrice', 'UnitName', 'NetAmount')

    def get_ProductName(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        ProductID = purchase_details.ProductID
        BranchID = purchase_details.BranchID

        if Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).exists():
            product = Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)
            ProductName = product.ProductName
        else:
            ProductName = ""

        return ProductName

    def get_UnitName(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = purchase_details.PriceListID
        BranchID = purchase_details.BranchID

        UnitName = ""
        if PriceList.objects.filter(CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).UnitID
            UnitName = Unit.objects.get(
                BranchID=BranchID, UnitID=UnitID, CompanyID=CompanyID).UnitName

        return UnitName

    def get_Qty(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        Qty = purchase_details.Qty

        if Qty:
            Qty = round(Qty, PriceRounding)
        else:
            Qty = 0

        return str(Qty)

    def get_UnitPrice(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        UnitPrice = purchase_details.UnitPrice
        if UnitPrice:
            UnitPrice = round(UnitPrice, PriceRounding)
        else:
            UnitPrice = 0

        return str(UnitPrice)

    def get_NetAmount(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        NetAmount = purchase_details.NetAmount

        if NetAmount:
            NetAmount = round(NetAmount, PriceRounding)
        else:
            NetAmount = 0

        return str(NetAmount)
