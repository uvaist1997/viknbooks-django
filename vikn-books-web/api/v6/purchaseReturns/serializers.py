from rest_framework import serializers
from brands.models import State,Country,PurchaseReturnMaster, PurchaseReturnDetails, AccountLedger, Product, PriceList, Warehouse, Unit, TaxCategory
from api.v6.priceLists.serializers import PriceListRestSerializer


class PurchaseReturnMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseReturnMaster
        fields = ('id', 'BranchID', 'Action', 'VoucherNo', 'VoucherDate', 'RefferenceBillNo',
                  'RefferenceBillDate', 'VenderInvoiceDate', 'CreditPeriod','Country_of_Supply','State_of_Supply','GST_Treatment',
                  'LedgerID', 'PriceCategoryID', 'EmployeeID', 'PurchaseAccount', 'DeliveryMasterID', 'OrderMasterID', 'CustomerName',
                  'Address1', 'Address2', 'Address3', 'Notes', 'FinacialYearID', 'TotalGrossAmt', 'TotalTax',
                  'NetTotal', 'AdditionalCost', 'GrandTotal', 'RoundOff', 'WarehouseID', 'IsActive','VAT_Treatment',
                  'TaxID', 'TaxType', 'VATAmount', 'SGSTAmount', 'CGSTAmount', 'IGSTAmount', 'TAX1Amount', 'TAX2Amount', 'TAX3Amount',
                  'AddlDiscPercent', 'AddlDiscAmt', 'TotalDiscount', 'BillDiscPercent', 'BillDiscAmt')


class PurchaseReturn1MasterRestSerializer(serializers.ModelSerializer):

    LedgerName = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    TotalTax_rounded = serializers.SerializerMethodField()
    GrandTotal_Rounded = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseReturnMaster
        fields = ('id', 'PurchaseReturnMasterID', 'VoucherNo', 'VoucherDate', 'RefferenceBillNo',
                  'RefferenceBillDate', 'VenderInvoiceDate', 'CustomerName', 'TotalTax_rounded', 'GrandTotal_Rounded',
                  'LedgerID', 'LedgerName', 'TotalTax', 'GrandTotal')

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(
            CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)

        LedgerName = ledger.LedgerName

        return LedgerName

    def get_TotalTax(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalTax = instances.TotalTax

        if TotalTax:
            TotalTax = round(TotalTax, PriceRounding)
        else:
            TotalTax = 0

        return float(TotalTax)

    def get_GrandTotal(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))

        GrandTotal = instances.GrandTotal

        if GrandTotal:
            GrandTotal = round(GrandTotal, PriceRounding)
        else:
            GrandTotal = 0

        return float(GrandTotal)

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


class PurchaseReturnMasterRestSerializer(serializers.ModelSerializer):

    PurchaseReturnDetails = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    DetailID = serializers.SerializerMethodField()
    PurchaseAccountName = serializers.SerializerMethodField()
    WareHouseName = serializers.SerializerMethodField()
    AddlDiscPercent = serializers.SerializerMethodField()
    BillDiscPercent = serializers.SerializerMethodField()
    RoundOff = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    TotalGrossAmt = serializers.SerializerMethodField()
    AddlDiscAmt = serializers.SerializerMethodField()
    NetTotal = serializers.SerializerMethodField()
    TotalDiscount = serializers.SerializerMethodField()
    VATAmount = serializers.SerializerMethodField()
    SGSTAmount = serializers.SerializerMethodField()
    CGSTAmount = serializers.SerializerMethodField()
    IGSTAmount = serializers.SerializerMethodField()
    TAX1Amount = serializers.SerializerMethodField()
    TAX2Amount = serializers.SerializerMethodField()
    TAX3Amount = serializers.SerializerMethodField()
    BillDiscAmt = serializers.SerializerMethodField()
    is_customer = serializers.SerializerMethodField()
    Country_of_Supply_name = serializers.SerializerMethodField()
    State_of_Supply_name = serializers.SerializerMethodField()
    TotalGrossAmt_print = serializers.SerializerMethodField()
    TotalDiscount_print = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseReturnMaster
        fields = ('id','TotalDiscount_print', 'TotalGrossAmt_print','PurchaseReturnMasterID', 'BranchID', 'Action', 'VoucherNo', 'VoucherDate', 'RefferenceBillNo',
                  'RefferenceBillDate', 'VenderInvoiceDate', 'CreditPeriod', 'DetailID', 'WareHouseName','Country_of_Supply','State_of_Supply','GST_Treatment',
                  'LedgerID', 'LedgerName', 'PriceCategoryID', 'EmployeeID', 'PurchaseAccount', 'PurchaseAccountName', 'DeliveryMasterID', 'OrderMasterID', 'CustomerName',
                  'Address1', 'Address2', 'Address3', 'is_customer', 'Notes', 'FinacialYearID', 'TotalGrossAmt', 'TotalTax','Country_of_Supply_name','State_of_Supply_name',
                  'NetTotal', 'AdditionalCost', 'GrandTotal', 'RoundOff', 'WarehouseID', 'IsActive', 'CreatedDate', 'UpdatedDate', 'CreatedUserID',
                  'TaxID', 'TaxType', 'VATAmount', 'SGSTAmount', 'CGSTAmount', 'IGSTAmount', 'TAX1Amount', 'TAX2Amount', 'TAX3Amount','VAT_Treatment',
                  'AddlDiscPercent', 'AddlDiscAmt', 'TotalDiscount', 'BillDiscPercent', 'BillDiscAmt', 'PurchaseReturnDetails')

    def get_TotalDiscount_print(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalDiscount = instances.TotalDiscount
        if TotalDiscount:
            TotalDiscount = round(TotalDiscount,PriceRounding)
        else:
            TotalDiscount = 0

        return str(TotalDiscount)

    def get_TotalGrossAmt_print(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))

        TotalGrossAmt = instances.TotalGrossAmt

        if TotalGrossAmt:
            TotalGrossAmt = round(TotalGrossAmt,PriceRounding)
        else:
            TotalGrossAmt = 0

        return str(TotalGrossAmt)

    def get_PurchaseReturnDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = int(self.context.get("PriceRounding"))
        BranchID = instances.BranchID
        purchaseReturn_details = PurchaseReturnDetails.objects.filter(
            CompanyID=CompanyID, PurchaseReturnMasterID=instances.PurchaseReturnMasterID, BranchID=BranchID).order_by('PurchaseReturnDetailsID')
        serialized = PurchaseReturnDetailsRestSerializer(purchaseReturn_details, many=True, context={
                                                         "CompanyID": CompanyID, "PriceRounding": PriceRounding})

        return serialized.data


    def get_Country_of_Supply_name(self, instances):
        CompanyID = self.context.get("CompanyID")
        Country_of_Supply = instances.Country_of_Supply
        Country_of_Supply_name = ""
        if Country_of_Supply:
            if Country.objects.filter(id=Country_of_Supply).exists():
                Country_of_Supply_name = Country.objects.get(id=Country_of_Supply).Country_Name
        return Country_of_Supply_name

    def get_State_of_Supply_name(self, instances):
        CompanyID = self.context.get("CompanyID")
        State_of_Supply = instances.State_of_Supply
        State_of_Supply_name = ""
        if State_of_Supply:
            if State.objects.filter(id=State_of_Supply).exists():
                State_of_Supply_name = State.objects.get(id=State_of_Supply).Name
        return State_of_Supply_name


    def get_DetailID(self, instances):

        return ""

    def get_is_customer(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        is_customer = False
        groups = [10, 29]
        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=groups).exists():
            is_customer = True

        return is_customer

    def get_WareHouseName(self, instances):
        CompanyID = self.context.get("CompanyID")

        WarehouseID = instances.WarehouseID
        BranchID = instances.BranchID

        wareHouse = Warehouse.objects.get(
            CompanyID=CompanyID, WarehouseID=WarehouseID, BranchID=BranchID)

        WareHouseName = wareHouse.WarehouseName

        return WareHouseName

    def get_PurchaseAccountName(self, instances):
        CompanyID = self.context.get("CompanyID")

        PurchaseAccount = instances.PurchaseAccount
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(
            CompanyID=CompanyID, LedgerID=PurchaseAccount, BranchID=BranchID)

        PurchaseAccountName = ledger.LedgerName

        return PurchaseAccountName

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(
            CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)

        LedgerName = ledger.LedgerName

        return LedgerName

    def get_AddlDiscPercent(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        AddlDiscPercent = instances.AddlDiscPercent

        # if AddlDiscPercent:
        #     AddlDiscPercent = round(AddlDiscPercent,PriceRounding)
        # else:
        #     AddlDiscPercent = 0

        return float(AddlDiscPercent)

    def get_BillDiscPercent(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        BillDiscPercent = instances.BillDiscPercent

        # if BillDiscPercent:
        #     BillDiscPercent = round(BillDiscPercent,PriceRounding)
        # else:
        #     BillDiscPercent = 0

        return float(BillDiscPercent)

    def get_RoundOff(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        RoundOff = instances.RoundOff

        # if RoundOff:
        #     RoundOff = round(RoundOff,PriceRounding)
        # else:
        #     RoundOff = 0

        return float(RoundOff)

    def get_TotalTax(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalTax = instances.TotalTax

        # if TotalTax:
        #     TotalTax = round(TotalTax,PriceRounding)
        # else:
        #     TotalTax = 0

        return float(TotalTax)

    def get_GrandTotal(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))

        GrandTotal = instances.GrandTotal

        # if GrandTotal:
        #     GrandTotal = round(GrandTotal,PriceRounding)
        # else:
        #     GrandTotal = 0

        return float(GrandTotal)

    def get_TotalGrossAmt(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))

        TotalGrossAmt = instances.TotalGrossAmt

        # if TotalGrossAmt:
        #     TotalGrossAmt = round(TotalGrossAmt,PriceRounding)
        # else:
        #     TotalGrossAmt = 0

        return float(TotalGrossAmt)

    def get_AddlDiscAmt(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        AddlDiscAmt = instances.AddlDiscAmt
        # if AddlDiscAmt:
        #     AddlDiscAmt = round(AddlDiscAmt,PriceRounding)
        # else:
        #     AddlDiscAmt = 0

        return float(AddlDiscAmt)

    def get_NetTotal(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        NetTotal = instances.NetTotal
        # if NetTotal:
        #     NetTotal = round(NetTotal,PriceRounding)
        # else:
        #     NetTotal = 0

        return float(NetTotal)

    def get_TotalDiscount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalDiscount = instances.TotalDiscount
        # if TotalDiscount:
        #     TotalDiscount = round(TotalDiscount,PriceRounding)
        # else:
        #     TotalDiscount = 0

        return float(TotalDiscount)

    def get_VATAmount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        VATAmount = instances.VATAmount
        # if VATAmount:
        #     VATAmount = round(VATAmount,PriceRounding)
        # else:
        #     VATAmount = 0

        return float(VATAmount)

    def get_SGSTAmount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        SGSTAmount = instances.SGSTAmount
        # if SGSTAmount:
        #     SGSTAmount = round(SGSTAmount,PriceRounding)
        # else:
        #     SGSTAmount = 0

        return float(SGSTAmount)

    def get_CGSTAmount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        CGSTAmount = instances.CGSTAmount
        # if CGSTAmount:
        #     CGSTAmount = round(CGSTAmount,PriceRounding)
        # else:
        #     CGSTAmount = 0

        return float(CGSTAmount)

    def get_IGSTAmount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        IGSTAmount = instances.IGSTAmount
        # if IGSTAmount:
        #     IGSTAmount = round(IGSTAmount,PriceRounding)
        # else:
        #     IGSTAmount = 0

        return float(IGSTAmount)

    def get_TAX1Amount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX1Amount = instances.TAX1Amount
        # if TAX1Amount:
        #     TAX1Amount = round(TAX1Amount,PriceRounding)
        # else:
        #     TAX1Amount = 0

        return float(TAX1Amount)

    def get_TAX2Amount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX2Amount = instances.TAX2Amount
        # if TAX2Amount:
        #     TAX2Amount = round(TAX2Amount,PriceRounding)
        # else:
        #     TAX2Amount = 0

        return float(TAX2Amount)

    def get_TAX3Amount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX3Amount = instances.TAX3Amount
        # if TAX3Amount:
        #     TAX3Amount = round(TAX3Amount,PriceRounding)
        # else:
        #     TAX3Amount = 0

        return float(TAX3Amount)

    def get_BillDiscAmt(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        BillDiscAmt = instances.BillDiscAmt
        # if BillDiscAmt:
        #     BillDiscAmt = round(BillDiscAmt,PriceRounding)
        # else:
        #     BillDiscAmt = 0

        return float(BillDiscAmt)


class PurchaseReturnDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseReturnDetails
        fields = ('id', 'BranchID', 'Action', 'PurchaseReturnMasterID', 'DeliveryDetailsID', 'OrderDetailsID', 'ProductID',
                  'Qty', 'FreeQty', 'UnitPrice',
                  'RateWithTax', 'CostPerPrice', 'PriceListID', 'DiscountPerc', 'DiscountAmount',
                  'GrossAmount', 'TaxableAmount', 'VATPerc', 'VATAmount', 'SGSTPerc', 'SGSTAmount', 'CGSTPerc',
                  'CGSTAmount', 'IGSTPerc', 'IGSTAmount', 'NetAmount', 'AddlDiscPerc', 'AddlDiscAmt', 'TAX1Perc', 'TAX1Amount', 'TAX2Perc',
                  'TAX2Amount', 'TAX3Perc', 'TAX3Amount')


class PurchaseReturnDetailsRestSerializer(serializers.ModelSerializer):

    ProductName = serializers.SerializerMethodField()
    unq_id = serializers.SerializerMethodField()
    detailID = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()
    AddlDiscPerc = serializers.SerializerMethodField()
    AddlDiscAmt = serializers.SerializerMethodField()
    UnitPrice = serializers.SerializerMethodField()
    InclusivePrice = serializers.SerializerMethodField()
    DiscountPerc = serializers.SerializerMethodField()
    DiscountAmount = serializers.SerializerMethodField()
    Qty = serializers.SerializerMethodField()
    FreeQty = serializers.SerializerMethodField()
    RateWithTax = serializers.SerializerMethodField()
    CostPerPrice = serializers.SerializerMethodField()
    GrossAmount = serializers.SerializerMethodField()
    TaxableAmount = serializers.SerializerMethodField()
    VATAmount = serializers.SerializerMethodField()
    SGSTAmount = serializers.SerializerMethodField()
    CGSTAmount = serializers.SerializerMethodField()
    IGSTAmount = serializers.SerializerMethodField()
    TAX1Amount = serializers.SerializerMethodField()
    TAX2Amount = serializers.SerializerMethodField()
    TAX3Amount = serializers.SerializerMethodField()
    NetAmount = serializers.SerializerMethodField()
    is_VAT_inclusive = serializers.SerializerMethodField()
    is_GST_inclusive = serializers.SerializerMethodField()
    is_TAX1_inclusive = serializers.SerializerMethodField()
    is_TAX2_inclusive = serializers.SerializerMethodField()
    is_TAX3_inclusive = serializers.SerializerMethodField()
    unitPriceRounded = serializers.SerializerMethodField()
    quantityRounded = serializers.SerializerMethodField()
    actualPurchasePrice = serializers.SerializerMethodField()
    netAmountRounded = serializers.SerializerMethodField()
    BatchCode = serializers.SerializerMethodField()
    VATPerc = serializers.SerializerMethodField()
    SGSTPerc = serializers.SerializerMethodField()
    CGSTPerc = serializers.SerializerMethodField()
    IGSTPerc = serializers.SerializerMethodField()
    UnitList = serializers.SerializerMethodField()
    is_inclusive = serializers.SerializerMethodField()
    ActualUnitPrice = serializers.SerializerMethodField()
    ProductCode = serializers.SerializerMethodField()
    HSNCode = serializers.SerializerMethodField()
    GST_Inclusive = serializers.SerializerMethodField()
    Vat_Inclusive = serializers.SerializerMethodField()
    PurchasePrice = serializers.SerializerMethodField()
    ProductTaxName = serializers.SerializerMethodField()
    ActualProductTaxName = serializers.SerializerMethodField()
    ActualProductTaxID = serializers.SerializerMethodField()
    unitPrice_print = serializers.SerializerMethodField()
    NetAmount_print = serializers.SerializerMethodField()


    class Meta:
        model = PurchaseReturnDetails
        fields = ('id', 'NetAmount_print','unitPrice_print','PurchaseReturnDetailsID', 'BranchID', 'Action', 'PurchaseReturnMasterID', 'DeliveryDetailsID', 'OrderDetailsID', 'ProductID',
                  'Qty', 'FreeQty', 'UnitPrice', 'InclusivePrice', 'ProductName', 'unq_id', 'detailID', 'TotalTax', 'UnitName', 'AddlDiscPerc','ProductTaxID',
                  'RateWithTax', 'CostPerPrice', 'PriceListID', 'DiscountPerc', 'DiscountAmount', 'AddlDiscAmt', 'is_inclusive', 'UnitList',
                  'GrossAmount', 'TaxableAmount', 'VATPerc', 'VATAmount', 'SGSTPerc', 'SGSTAmount', 'CGSTPerc', 'BatchCode', 'ActualUnitPrice',
                  'CGSTAmount', 'IGSTPerc', 'IGSTAmount', 'NetAmount', 'CreatedDate', 'UpdatedDate', 'CreatedUserID', 'AddlDiscPerc', 'AddlDiscAmt', 'TAX1Perc', 'TAX1Amount', 'TAX2Perc',
                  'TAX2Amount', 'TAX3Perc', 'TAX3Amount', 'is_VAT_inclusive', 'is_GST_inclusive', 'is_TAX1_inclusive', 'is_TAX2_inclusive', 'is_TAX3_inclusive',
                  'unitPriceRounded', 'quantityRounded', 'actualPurchasePrice', 'netAmountRounded', "ProductCode", "HSNCode",
                  'PurchasePrice','GST_Inclusive','Vat_Inclusive','ProductTaxName','ActualProductTaxName','ActualProductTaxID')

    
    def get_NetAmount_print(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        NetAmount = purchaseReturn_details.NetAmount
        NetAmount = round(NetAmount,PriceRounding)
        return str(NetAmount)

    def get_unitPrice_print(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        UnitPrice = purchaseReturn_details.UnitPrice
        UnitPrice = round(UnitPrice,PriceRounding)
        return str(UnitPrice)

    def get_ActualProductTaxName(self, purchaseReturn_details):
        CompanyID = self.context.get("CompanyID")
        ProductTaxID = purchaseReturn_details.ProductTaxID
        BranchID = purchaseReturn_details.BranchID
        ActualProductTaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID,BranchID=BranchID,TaxID=ProductTaxID).exists():
            ActualProductTaxName = TaxCategory.objects.get(CompanyID=CompanyID,BranchID=BranchID,TaxID=ProductTaxID).TaxName
        return ActualProductTaxName

    def get_ActualProductTaxID(self, purchaseReturn_details):
        CompanyID = self.context.get("CompanyID")
        ActualProductTaxID = purchaseReturn_details.ProductTaxID
        return ActualProductTaxID
        

    def get_PurchasePrice(self, purchaseReturn_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = purchaseReturn_details.PriceListID
        BranchID = purchaseReturn_details.BranchID
        PurchasePrice = 0
        if PriceList.objects.filter(CompanyID=CompanyID,BranchID=BranchID,PriceListID=PriceListID).exists():
            PurchasePrice = PriceList.objects.get(CompanyID=CompanyID,BranchID=BranchID,PriceListID=PriceListID).PurchasePrice
        return float(PurchasePrice)

    def get_ProductTaxName(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        ProductTaxID = purchase_details.ProductTaxID
        BranchID = purchase_details.BranchID
        ProductTaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID,BranchID=BranchID,TaxID=ProductTaxID).exists():
            ProductTaxName = TaxCategory.objects.get(CompanyID=CompanyID,BranchID=BranchID,TaxID=ProductTaxID).TaxName
        return ProductTaxName


    def get_Vat_Inclusive(self, purchaseReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchaseReturn_details.BranchID
        ProductID = purchaseReturn_details.ProductID
        ProductTaxID = purchaseReturn_details.ProductTaxID
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

    def get_GST_Inclusive(self, purchaseReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchaseReturn_details.BranchID
        ProductID = purchaseReturn_details.ProductID
        ProductTaxID = purchaseReturn_details.ProductTaxID
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


    def get_ProductName(self, purchaseReturn_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = purchaseReturn_details.ProductID
        BranchID = purchaseReturn_details.BranchID

        if Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).exists():

            product = Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)
            ProductName = product.ProductName
        else:
            ProductName = ""

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

    def get_ActualUnitPrice(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        ActualUnitPrice = sales_details.UnitPrice

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

    def get_is_inclusive(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchase_details.BranchID
        ProductID = purchase_details.ProductID
        pro_ins = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)
        GST = pro_ins.GST
        VatID = pro_ins.VatID
        Tax1 = pro_ins.Tax1
        Tax2 = pro_ins.Tax2
        Tax3 = pro_ins.Tax3
        is_inclusive = False
        GST_inclusive = False
        VAT_inclusive = False
        Tax1_inclusive = False
        Tax2_inclusive = False
        Tax3_inclusive = False
        if GST:
            GST_inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=GST, BranchID=BranchID).Inclusive
        if VatID:
            VAT_inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=VatID, BranchID=BranchID).Inclusive
        if Tax1:
            Tax1_inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax1, BranchID=BranchID).Inclusive
        if Tax2:
            Tax2_inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax2, BranchID=BranchID).Inclusive
        if Tax3:
            Tax3_inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax3, BranchID=BranchID).Inclusive

        if GST_inclusive == True or VAT_inclusive == True or Tax1_inclusive == True or Tax2_inclusive == True or Tax3_inclusive == True:
            is_inclusive = True

        return is_inclusive

    def get_BatchCode(self, purchaseReturn_details):
        CompanyID = self.context.get("CompanyID")
        BatchCode = purchaseReturn_details.BatchCode
        BranchID = purchaseReturn_details.BranchID
        if not BatchCode:
            BatchCode = 0

        return BatchCode

    def get_VATPerc(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        VATPerc = purchaseReturn_details.VATPerc

        # if VATPerc:
        #     VATPerc = round(VATPerc, PriceRounding)
        # else:
        #     VATPerc = 0

        return str(VATPerc)

    def get_SGSTPerc(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        SGSTPerc = purchaseReturn_details.SGSTPerc

        # if SGSTPerc:
        #     SGSTPerc = round(SGSTPerc, PriceRounding)
        # else:
        #     SGSTPerc = 0

        return str(SGSTPerc)

    def get_CGSTPerc(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        CGSTPerc = purchaseReturn_details.CGSTPerc

        # if CGSTPerc:
        #     CGSTPerc = round(CGSTPerc, PriceRounding)
        # else:
        #     CGSTPerc = 0

        return str(CGSTPerc)

    def get_IGSTPerc(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        IGSTPerc = purchaseReturn_details.IGSTPerc

        # if IGSTPerc:
        #     IGSTPerc = round(IGSTPerc, PriceRounding)
        # else:
        #     IGSTPerc = 0

        return str(IGSTPerc)

    def get_InclusivePrice(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        # PriceRounding = 2
        InclusivePrice = purchaseReturn_details.InclusivePrice
        # if InclusivePrice:
        #     InclusivePrice = round(InclusivePrice,PriceRounding)
        # else:
        #     InclusivePrice = 0

        return str(InclusivePrice)

    def get_unitPriceRounded(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        UnitPrice = purchaseReturn_details.UnitPrice
        # UnitPrice = round(UnitPrice,PriceRounding)
        return UnitPrice

    def get_quantityRounded(self, purchaseReturn_details):
        Qty = purchaseReturn_details.Qty
        return Qty

    def get_actualPurchasePrice(self, purchaseReturn_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = purchaseReturn_details.PriceListID
        BranchID = purchaseReturn_details.BranchID
        ProductID = purchaseReturn_details.ProductID
        PurchasePrice = ''
        if PriceList.objects.filter(ProductID=ProductID, CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).exists():
            PurchasePrice = PriceList.objects.get(
                ProductID=ProductID, CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).PurchasePrice
        return PurchasePrice

    def get_netAmountRounded(self, purchaseReturn_details):
        NetAmount = purchaseReturn_details.NetAmount
        return NetAmount

    def get_is_VAT_inclusive(self, purchaseReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchaseReturn_details.BranchID
        ProductID = purchaseReturn_details.ProductID
        Inclusive = False
        VatID = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).VatID
        if VatID:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=VatID, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_GST_inclusive(self, purchaseReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchaseReturn_details.BranchID
        ProductID = purchaseReturn_details.ProductID
        Inclusive = False
        GST = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).GST
        if GST:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=GST, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_TAX1_inclusive(self, purchaseReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchaseReturn_details.BranchID
        ProductID = purchaseReturn_details.ProductID
        Inclusive = False
        Tax1 = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).Tax1
        if Tax1:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax1, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_TAX2_inclusive(self, purchaseReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchaseReturn_details.BranchID
        ProductID = purchaseReturn_details.ProductID
        Inclusive = False
        Tax2 = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).Tax2
        if Tax2:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax2, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_TAX3_inclusive(self, purchaseReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchaseReturn_details.BranchID
        ProductID = purchaseReturn_details.ProductID
        Inclusive = False
        Tax3 = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).Tax3
        if Tax3:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax3, BranchID=BranchID).Inclusive
        return Inclusive

    def get_UnitPrice(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        UnitPrice = purchaseReturn_details.UnitPrice

        # if UnitPrice:
        #     UnitPrice = round(UnitPrice,PriceRounding)
        # else:
        #     UnitPrice = 0

        return str(UnitPrice)

    def get_Qty(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        Qty = purchaseReturn_details.Qty

        # if Qty:
        #     Qty = round(Qty,PriceRounding)
        # else:
        #     Qty = 0

        return str(Qty)

    def get_FreeQty(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        FreeQty = purchaseReturn_details.FreeQty

        # if FreeQty:
        #     FreeQty = round(FreeQty,PriceRounding)
        # else:
        #     FreeQty = 0

        return str(FreeQty)

    def get_RateWithTax(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        RateWithTax = purchaseReturn_details.RateWithTax

        # if RateWithTax:
        #     RateWithTax = round(RateWithTax,PriceRounding)
        # else:
        #     RateWithTax = 0

        return str(RateWithTax)

    def get_CostPerPrice(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        CostPerPrice = purchaseReturn_details.CostPerPrice

        # if CostPerPrice:
        #     CostPerPrice = round(CostPerPrice,PriceRounding)
        # else:
        #     CostPerPrice = 0

        return str(CostPerPrice)

    def get_GrossAmount(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        GrossAmount = purchaseReturn_details.GrossAmount

        # if GrossAmount:
        #     GrossAmount = round(GrossAmount,PriceRounding)
        # else:
        #     GrossAmount = 0

        return str(GrossAmount)

    def get_TaxableAmount(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        TaxableAmount = purchaseReturn_details.TaxableAmount

        # if TaxableAmount:
        #     TaxableAmount = round(TaxableAmount,PriceRounding)
        # else:
        #     TaxableAmount = 0

        return str(TaxableAmount)

    def get_VATAmount(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        VATAmount = purchaseReturn_details.VATAmount

        # if VATAmount:
        #     VATAmount = round(VATAmount,PriceRounding)
        # else:
        #     VATAmount = 0

        return str(VATAmount)

    def get_SGSTAmount(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        SGSTAmount = purchaseReturn_details.SGSTAmount

        # if SGSTAmount:
        #     SGSTAmount = round(SGSTAmount,PriceRounding)
        # else:
        #     SGSTAmount = 0

        return str(SGSTAmount)

    def get_CGSTAmount(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        CGSTAmount = purchaseReturn_details.CGSTAmount

        # if CGSTAmount:
        #     CGSTAmount = round(CGSTAmount,PriceRounding)
        # else:
        #     CGSTAmount = 0

        return str(CGSTAmount)

    def get_IGSTAmount(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        IGSTAmount = purchaseReturn_details.IGSTAmount

        # if IGSTAmount:
        #     IGSTAmount = round(IGSTAmount,PriceRounding)
        # else:
        #     IGSTAmount = 0

        return str(IGSTAmount)

    def get_TAX1Amount(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX1Amount = purchaseReturn_details.TAX1Amount

        # if TAX1Amount:
        #     TAX1Amount = round(TAX1Amount,PriceRounding)
        # else:
        #     TAX1Amount = 0

        return str(TAX1Amount)

    def get_TAX2Amount(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX2Amount = purchaseReturn_details.TAX2Amount

        # if TAX2Amount:
        #     TAX2Amount = round(TAX2Amount,PriceRounding)
        # else:
        #     TAX2Amount = 0

        return str(TAX2Amount)

    def get_TAX3Amount(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX3Amount = purchaseReturn_details.TAX3Amount

        # if TAX3Amount:
        #     TAX3Amount = round(TAX3Amount,PriceRounding)
        # else:
        #     TAX3Amount = 0

        return str(TAX3Amount)

    def get_NetAmount(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        NetAmount = purchaseReturn_details.NetAmount

        # if NetAmount:
        #     NetAmount = round(NetAmount,PriceRounding)
        # else:
        #     NetAmount = 0

        return str(NetAmount)

    def get_DiscountPerc(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        DiscountPerc = purchaseReturn_details.DiscountPerc

        # if DiscountPerc:
        #     DiscountPerc = round(DiscountPerc,PriceRounding)
        # else:
        #     DiscountPerc = 0

        return str(DiscountPerc)

    def get_DiscountAmount(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        DiscountAmount = purchaseReturn_details.DiscountAmount

        # if DiscountAmount:
        #     DiscountAmount = round(DiscountAmount,PriceRounding)
        # else:
        #     DiscountAmount = 0

        return str(DiscountAmount)

    def get_AddlDiscPerc(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        AddlDiscPerc = purchaseReturn_details.AddlDiscPerc

        # if AddlDiscPerc:
        #     AddlDiscPerc = round(AddlDiscPerc,PriceRounding)
        # else:
        #     AddlDiscPerc = 0

        return str(AddlDiscPerc)

    def get_AddlDiscAmt(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        AddlDiscAmt = purchaseReturn_details.AddlDiscAmt

        # if AddlDiscAmt:
        #     AddlDiscAmt = round(AddlDiscAmt,PriceRounding)
        # else:
        #     AddlDiscAmt = 0

        return str(AddlDiscAmt)

    def get_UnitName(self, purchaseReturn_details):

        CompanyID = self.context.get("CompanyID")

        PriceListID = purchaseReturn_details.PriceListID
        BranchID = purchaseReturn_details.BranchID

        if PriceList.objects.filter(CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).UnitID
            UnitName = Unit.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, UnitID=UnitID).UnitName
        else:
            UnitName = ""

        return UnitName

    def get_TotalTax(self, purchaseReturn_details):

        CompanyID = self.context.get("CompanyID")

        TAX1Amount = purchaseReturn_details.TAX1Amount
        TAX2Amount = purchaseReturn_details.TAX2Amount
        TAX3Amount = purchaseReturn_details.TAX3Amount
        VATAmount = purchaseReturn_details.VATAmount
        IGSTAmount = purchaseReturn_details.IGSTAmount
        SGSTAmount = purchaseReturn_details.SGSTAmount
        CGSTAmount = purchaseReturn_details.CGSTAmount

        TotalTax = (TAX1Amount + TAX2Amount + TAX3Amount +
                    VATAmount + IGSTAmount + SGSTAmount + CGSTAmount)

        return TotalTax

    def get_unq_id(self, purchaseReturn_details):

        CompanyID = self.context.get("CompanyID")

        unq_id = purchaseReturn_details.id

        return unq_id

    def get_detailID(self, purchaseReturn_details):

        detailID = 0
        return detailID


class PurchaseReturnPrintSerializer(serializers.ModelSerializer):

    Details = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    DetailID = serializers.SerializerMethodField()
    PurchaseAccountName = serializers.SerializerMethodField()
    WareHouseName = serializers.SerializerMethodField()
    AddlDiscPercent = serializers.SerializerMethodField()
    BillDiscPercent = serializers.SerializerMethodField()
    RoundOff = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    TotalGrossAmt = serializers.SerializerMethodField()
    AddlDiscAmt = serializers.SerializerMethodField()
    NetTotal = serializers.SerializerMethodField()
    TotalDiscount = serializers.SerializerMethodField()
    VATAmount = serializers.SerializerMethodField()
    SGSTAmount = serializers.SerializerMethodField()
    CGSTAmount = serializers.SerializerMethodField()
    IGSTAmount = serializers.SerializerMethodField()
    TAX1Amount = serializers.SerializerMethodField()
    TAX2Amount = serializers.SerializerMethodField()
    TAX3Amount = serializers.SerializerMethodField()
    BillDiscAmt = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseReturnMaster
        fields = ('PurchaseReturnMasterID', 'BranchID', 'Action', 'VoucherNo', 'VoucherDate', 'RefferenceBillNo',
                  'RefferenceBillDate', 'VenderInvoiceDate', 'CreditPeriod', 'DetailID', 'WareHouseName',
                  'LedgerID', 'LedgerName', 'PriceCategoryID', 'EmployeeID', 'PurchaseAccount', 'PurchaseAccountName', 'DeliveryMasterID', 'OrderMasterID', 'CustomerName',
                  'Address1', 'Address2', 'Address3', 'Notes', 'FinacialYearID', 'TotalGrossAmt', 'TotalTax',
                  'NetTotal', 'AdditionalCost', 'GrandTotal', 'RoundOff', 'WarehouseID', 'IsActive', 'CreatedDate', 'UpdatedDate', 'CreatedUserID',
                  'TaxID', 'TaxType', 'VATAmount', 'SGSTAmount', 'CGSTAmount', 'IGSTAmount', 'TAX1Amount', 'TAX2Amount', 'TAX3Amount',
                  'AddlDiscPercent', 'AddlDiscAmt', 'TotalDiscount', 'BillDiscPercent', 'BillDiscAmt', 'Details')

    def get_Details(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = int(self.context.get("PriceRounding"))
        BranchID = instances.BranchID
        purchaseReturn_details = PurchaseReturnDetails.objects.filter(
            CompanyID=CompanyID, PurchaseReturnMasterID=instances.PurchaseReturnMasterID, BranchID=BranchID)
        serialized = PurchaseReturnDetailsPrintSerializer(purchaseReturn_details, many=True, context={
                                                          "CompanyID": CompanyID, "PriceRounding": PriceRounding})

        return serialized.data

    def get_DetailID(self, instances):

        return ""

    def get_WareHouseName(self, instances):
        CompanyID = self.context.get("CompanyID")

        WarehouseID = instances.WarehouseID
        BranchID = instances.BranchID

        wareHouse = Warehouse.objects.get(
            CompanyID=CompanyID, WarehouseID=WarehouseID, BranchID=BranchID)

        WareHouseName = wareHouse.WarehouseName

        return WareHouseName

    def get_PurchaseAccountName(self, instances):
        CompanyID = self.context.get("CompanyID")

        PurchaseAccount = instances.PurchaseAccount
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(
            CompanyID=CompanyID, LedgerID=PurchaseAccount, BranchID=BranchID)

        PurchaseAccountName = ledger.LedgerName

        return PurchaseAccountName

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(
            CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)

        LedgerName = ledger.LedgerName

        return LedgerName

    def get_AddlDiscPercent(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        AddlDiscPercent = instances.AddlDiscPercent

        if AddlDiscPercent:
            AddlDiscPercent = round(AddlDiscPercent, PriceRounding)
        else:
            AddlDiscPercent = 0

        return float(AddlDiscPercent)

    def get_BillDiscPercent(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        BillDiscPercent = instances.BillDiscPercent

        if BillDiscPercent:
            BillDiscPercent = round(BillDiscPercent, PriceRounding)
        else:
            BillDiscPercent = 0

        return float(BillDiscPercent)

    def get_RoundOff(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        RoundOff = instances.RoundOff

        if RoundOff:
            RoundOff = round(RoundOff, PriceRounding)
        else:
            RoundOff = 0

        return float(RoundOff)

    def get_TotalTax(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalTax = instances.TotalTax

        if TotalTax:
            TotalTax = round(TotalTax, PriceRounding)
        else:
            TotalTax = 0

        return float(TotalTax)

    def get_GrandTotal(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))

        GrandTotal = instances.GrandTotal

        if GrandTotal:
            GrandTotal = round(GrandTotal, PriceRounding)
        else:
            GrandTotal = 0

        return float(GrandTotal)

    def get_TotalGrossAmt(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))

        TotalGrossAmt = instances.TotalGrossAmt

        if TotalGrossAmt:
            TotalGrossAmt = round(TotalGrossAmt, PriceRounding)
        else:
            TotalGrossAmt = 0

        return float(TotalGrossAmt)

    def get_AddlDiscAmt(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        AddlDiscAmt = instances.AddlDiscAmt
        if AddlDiscAmt:
            AddlDiscAmt = round(AddlDiscAmt, PriceRounding)
        else:
            AddlDiscAmt = 0

        return float(AddlDiscAmt)

    def get_NetTotal(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        NetTotal = instances.NetTotal
        if NetTotal:
            NetTotal = round(NetTotal, PriceRounding)
        else:
            NetTotal = 0

        return float(NetTotal)

    def get_TotalDiscount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalDiscount = instances.TotalDiscount
        if TotalDiscount:
            TotalDiscount = round(TotalDiscount, PriceRounding)
        else:
            TotalDiscount = 0

        return float(TotalDiscount)

    def get_VATAmount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        VATAmount = instances.VATAmount
        if VATAmount:
            VATAmount = round(VATAmount, PriceRounding)
        else:
            VATAmount = 0

        return float(VATAmount)

    def get_SGSTAmount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        SGSTAmount = instances.SGSTAmount
        if SGSTAmount:
            SGSTAmount = round(SGSTAmount, PriceRounding)
        else:
            SGSTAmount = 0

        return float(SGSTAmount)

    def get_CGSTAmount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        CGSTAmount = instances.CGSTAmount
        if CGSTAmount:
            CGSTAmount = round(CGSTAmount, PriceRounding)
        else:
            CGSTAmount = 0

        return float(CGSTAmount)

    def get_IGSTAmount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        IGSTAmount = instances.IGSTAmount
        if IGSTAmount:
            IGSTAmount = round(IGSTAmount, PriceRounding)
        else:
            IGSTAmount = 0

        return float(IGSTAmount)

    def get_TAX1Amount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX1Amount = instances.TAX1Amount
        if TAX1Amount:
            TAX1Amount = round(TAX1Amount, PriceRounding)
        else:
            TAX1Amount = 0

        return float(TAX1Amount)

    def get_TAX2Amount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX2Amount = instances.TAX2Amount
        if TAX2Amount:
            TAX2Amount = round(TAX2Amount, PriceRounding)
        else:
            TAX2Amount = 0

        return float(TAX2Amount)

    def get_TAX3Amount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX3Amount = instances.TAX3Amount
        if TAX3Amount:
            TAX3Amount = round(TAX3Amount, PriceRounding)
        else:
            TAX3Amount = 0

        return float(TAX3Amount)

    def get_BillDiscAmt(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        BillDiscAmt = instances.BillDiscAmt
        if BillDiscAmt:
            BillDiscAmt = round(BillDiscAmt, PriceRounding)
        else:
            BillDiscAmt = 0

        return float(BillDiscAmt)


class PurchaseReturnDetailsPrintSerializer(serializers.ModelSerializer):

    ProductName = serializers.SerializerMethodField()
    UnitPrice = serializers.SerializerMethodField()
    Qty = serializers.SerializerMethodField()
    NetAmount = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseReturnDetails
        fields = ('Qty', 'UnitPrice', 'ProductName', 'NetAmount', 'UnitName')

    def get_ProductName(self, purchaseReturn_details):

        CompanyID = self.context.get("CompanyID")
        ProductID = purchaseReturn_details.ProductID
        BranchID = purchaseReturn_details.BranchID

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

    def get_UnitPrice(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        UnitPrice = purchaseReturn_details.UnitPrice

        if UnitPrice:
            UnitPrice = round(UnitPrice, PriceRounding)
        else:
            UnitPrice = 0

        return str(UnitPrice)

    def get_Qty(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        Qty = purchaseReturn_details.Qty

        if Qty:
            Qty = round(Qty, PriceRounding)
        else:
            Qty = 0

        return str(Qty)

    def get_NetAmount(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        NetAmount = purchaseReturn_details.NetAmount

        if NetAmount:
            NetAmount = round(NetAmount, PriceRounding)
        else:
            NetAmount = 0

        return str(NetAmount)
