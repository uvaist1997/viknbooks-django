from rest_framework import serializers
from brands.models import Parties, Country, State, PurchaseMaster, PurchaseDetails, AccountLedger, Product, Warehouse, PriceList, Unit, TaxCategory, PriceCategory, TransactionTypes, Batch
from api.v8.priceLists.serializers import PriceListRestSerializer
from api.v8.workOrder.serializers import Batch_ListSerializer
from api.v8.sales import functions as func
from datetime import datetime as dt


class PurchaseMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseMaster
        fields = ('id', 'BranchID', 'Action', 'VoucherNo', 'RefferenceBillNo', 'Date',
                  'VenderInvoiceDate', 'CreditPeriod', 'LedgerID', 'GST_Treatment', 'VAT_Treatment',
                  'PriceCategoryID', 'EmployeeID', 'PurchaseAccount', 'CustomerName', 'Address1', 'Address2', 'Address3',
                  'Notes', 'FinacialYearID', 'TotalGrossAmt', 'TotalTax', 'NetTotal', 'AddlDiscPercent', 'AddlDiscAmt',
                  'AdditionalCost', 'TotalDiscount', 'GrandTotal', 'RoundOff', 'TransactionTypeID', 'WarehouseID', 'IsActive', 'CreatedDate', 'CreatedUserID',
                  'TaxID', 'TaxType', 'VATAmount', 'SGSTAmount', 'CGSTAmount', 'IGSTAmount', 'TAX1Amount', 'TAX2Amount', 'TAX3Amount', 'BillDiscPercent', 'BillDiscAmt', 'CashReceived', 'CashAmount', 'BankAmount', 'Balance')


class PurchaseMasterRest1Serializer(serializers.ModelSerializer):
    TotalTax = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    TotalTax_rounded = serializers.SerializerMethodField()
    TotalGrossAmt_rounded = serializers.SerializerMethodField()
    GrandTotal_Rounded = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseMaster
        fields = ('id', 'PurchaseMasterID', 'VoucherNo', 'Date', 'TotalTax_rounded',
                  'VenderInvoiceDate', 'LedgerName', 'GrandTotal_Rounded', 'TotalGrossAmt_rounded',
                  'CustomerName', 'TotalTax', 'GrandTotal', 'TotalGrossAmt', 'BillDiscAmt',
                  'TaxID',)

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        LedgerName = ""
        if AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID).exists():
            ledger = AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)

            LedgerName = ledger.LedgerName

        return LedgerName

    def get_TotalGrossAmt_rounded(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalGrossAmt = instances.TotalGrossAmt

        TotalGrossAmt_rounded = round(TotalGrossAmt, PriceRounding)

        return str(TotalGrossAmt_rounded)

    def get_TotalTax(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalTax = instances.TotalTax

        # TotalTax = round(TotalTax, PriceRounding)

        return str(TotalTax)

    def get_GrandTotal(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        GrandTotal = instances.GrandTotal

        # GrandTotal = round(GrandTotal, PriceRounding)

        return str(GrandTotal)

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


class PurchaseMasterRestSerializer(serializers.ModelSerializer):

    PurchaseDetails = serializers.SerializerMethodField()
    TotalGrossAmt = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    NetTotal = serializers.SerializerMethodField()
    AddlDiscPercent = serializers.SerializerMethodField()
    AddlDiscAmt = serializers.SerializerMethodField()
    AdditionalCost = serializers.SerializerMethodField()
    TotalDiscount = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    RoundOff = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    PurchaseAccountName = serializers.SerializerMethodField()
    WareHouseName = serializers.SerializerMethodField()
    DetailID = serializers.SerializerMethodField()
    VATAmount = serializers.SerializerMethodField()
    SGSTAmount = serializers.SerializerMethodField()
    CGSTAmount = serializers.SerializerMethodField()
    IGSTAmount = serializers.SerializerMethodField()
    TAX1Amount = serializers.SerializerMethodField()
    TAX2Amount = serializers.SerializerMethodField()
    TAX3Amount = serializers.SerializerMethodField()
    BillDiscPercent = serializers.SerializerMethodField()
    BillDiscAmt = serializers.SerializerMethodField()
    Balance = serializers.SerializerMethodField()
    is_customer = serializers.SerializerMethodField()
    PriceCategoryName = serializers.SerializerMethodField()
    CashReceived = serializers.SerializerMethodField()
    CashAmount = serializers.SerializerMethodField()
    BankAmount = serializers.SerializerMethodField()
    CardTypeName = serializers.SerializerMethodField()
    TotalTax_rounded = serializers.SerializerMethodField()
    GrandTotal_Rounded = serializers.SerializerMethodField()
    CashName = serializers.SerializerMethodField()
    BankName = serializers.SerializerMethodField()
    Country_of_Supply_name = serializers.SerializerMethodField()
    State_of_Supply_name = serializers.SerializerMethodField()
    TotalGrossAmt_print = serializers.SerializerMethodField()
    TotalDiscount_print = serializers.SerializerMethodField()
    GST_Treatment = serializers.SerializerMethodField()
    VAT_Treatment = serializers.SerializerMethodField()
    VATAmount_print = serializers.SerializerMethodField()
    GrandTotal_print = serializers.SerializerMethodField()
    ProductList = serializers.SerializerMethodField()
    Mobile = serializers.SerializerMethodField()
    SGST_final_list = serializers.SerializerMethodField()
    IGST_final_list = serializers.SerializerMethodField()
    Place_of_Supply = serializers.SerializerMethodField()
    PrintCustomerName = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseMaster
        fields = ('id', 'VATAmount_print', 'GrandTotal_print', 'TotalDiscount_print', 'TotalGrossAmt_print', 'PurchaseMasterID', 'ShippingCharge', 'shipping_tax_amount', 'TaxTypeID', 'SAC', 'PurchaseTax', 'CashName', 'BankName', "CashID", "BankID", 'BranchID', 'TotalTaxableAmount', 'Action', 'VoucherNo', 'RefferenceBillNo', 'Date',
                  'VenderInvoiceDate', 'CreditPeriod', 'LedgerID', 'LedgerName', 'TotalTax_rounded', 'GrandTotal_Rounded', 'Country_of_Supply', 'State_of_Supply', 'GST_Treatment', 'VAT_Treatment', 'ProductList',
                  'PriceCategoryID', 'PriceCategoryName', 'EmployeeID', 'PurchaseAccount', 'PurchaseAccountName', 'CustomerName', 'Address1', 'Address2', 'Address3', 'is_customer', 'Country_of_Supply', 'State_of_Supply',
                  'Notes', 'FinacialYearID', 'TotalGrossAmt', 'TotalTax', 'NetTotal', 'AddlDiscPercent', 'AddlDiscAmt', 'CardTypeID', 'CardTypeName', 'CardNumber', 'Country_of_Supply_name', 'State_of_Supply_name',
                  'AdditionalCost', 'TotalDiscount', 'GrandTotal', 'RoundOff', 'TransactionTypeID', 'WarehouseID', 'WareHouseName', 'IsActive', 'CreatedDate', 'CreatedUserID', 'CashReceived', 'CashAmount', 'BankAmount',
                  'TaxID', 'TaxType', 'VATAmount', 'SGSTAmount', 'CGSTAmount', 'IGSTAmount', 'TAX1Amount', 'TAX2Amount', 'TAX3Amount', 'BillDiscPercent', 'BillDiscAmt', 'Balance', 'DetailID', 'PurchaseDetails',
                  'Mobile', 'SGST_final_list', 'IGST_final_list', 'Place_of_Supply', 'PrintCustomerName')

    def get_PrintCustomerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        DisplayName = ""
        LedgerID = instances.LedgerID
        if Parties.objects.filter(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID).exists():
            party = Parties.objects.get(
                LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID)
            DisplayName = party.DisplayName
        return DisplayName

    def get_SGST_final_list(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        BranchID = instances.BranchID
        PurchaseMasterID = instances.PurchaseMasterID
        purchase_details = PurchaseDetails.objects.filter(
            CompanyID=CompanyID, PurchaseMasterID=PurchaseMasterID, BranchID=BranchID)
        SGST_final_list = func.GST_finalList_fun(
            instances, purchase_details, "SGST", PriceRounding, "Purchase")
        return SGST_final_list

    def get_IGST_final_list(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        BranchID = instances.BranchID
        PurchaseMasterID = instances.PurchaseMasterID
        purchase_details = PurchaseDetails.objects.filter(
            CompanyID=CompanyID, PurchaseMasterID=PurchaseMasterID, BranchID=BranchID)
        IGST_final_list = func.GST_finalList_fun(
            instances, purchase_details, "IGST", PriceRounding, "Purchase")
        return IGST_final_list

    def get_ProductList(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        PurchaseMasterID = instances.PurchaseMasterID
        purchase_details = PurchaseDetails.objects.filter(
            CompanyID=CompanyID, PurchaseMasterID=PurchaseMasterID, BranchID=BranchID)

        product_ids = purchase_details.values_list('ProductID', flat=True)
        produc_instances = Product.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_ids)
        ProductList = []
        for p in produc_instances:
            ProductList.append({
                "ProductName": p.ProductName,
                "ProductID": p.ProductID,
            })

        return ProductList

    def get_Mobile(self, instances):
        CompanyID = self.context.get("CompanyID")
        Mobile = ""
        if Parties.objects.filter(LedgerID=instances.LedgerID, CompanyID=CompanyID).exists():
            Mobile = Parties.objects.get(
                LedgerID=instances.LedgerID, CompanyID=CompanyID).Mobile

        return str(Mobile)

    def get_VATAmount_print(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        VATAmount = instances.VATAmount
        VATAmount = str(round(VATAmount, PriceRounding))
        return str(VATAmount)

    def get_GrandTotal_print(self, instances):
        CompanyID = self.context.get("CompanyID")

        PriceRounding = self.context.get("PriceRounding")

        GrandTotal = instances.GrandTotal
        GrandTotal_print = str(round(GrandTotal, PriceRounding))
        return str(GrandTotal_print)

    def get_GST_Treatment(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        GST_Treatment = instances.GST_Treatment
        if not GST_Treatment:
            GST_Treatment = ""
            if Parties.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).exists():
                pary_ins = Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).first()
                GST_Treatment = pary_ins.GST_Treatment
        return str(GST_Treatment)

    def get_VAT_Treatment(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        VAT_Treatment = instances.VAT_Treatment
        if not VAT_Treatment:
            VAT_Treatment = ""
            if Parties.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).exists():
                pary_ins = Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).first()
                VAT_Treatment = pary_ins.VAT_Treatment
        return str(VAT_Treatment)

    def get_TotalDiscount_print(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalDiscount = instances.TotalDiscount
        if TotalDiscount:
            TotalDiscount = round(TotalDiscount, PriceRounding)
        else:
            TotalDiscount = 0

        return str(TotalDiscount)

    def get_TotalGrossAmt_print(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))

        TotalGrossAmt = instances.TotalGrossAmt

        if TotalGrossAmt:
            TotalGrossAmt = round(TotalGrossAmt, PriceRounding)
        else:
            TotalGrossAmt = 0

        return str(TotalGrossAmt)

    def get_Country_of_Supply_name(self, instances):
        CompanyID = self.context.get("CompanyID")
        Country_of_Supply = instances.Country_of_Supply
        Country_of_Supply_name = ""
        if Country_of_Supply:
            if Country.objects.filter(id=Country_of_Supply).exists():
                Country_of_Supply_name = Country.objects.get(
                    id=Country_of_Supply).Country_Name
        return Country_of_Supply_name

    def get_State_of_Supply_name(self, instances):
        CompanyID = self.context.get("CompanyID")
        State_of_Supply = instances.State_of_Supply
        State_of_Supply_name = ""
        if State_of_Supply:
            if State.objects.filter(id=State_of_Supply).exists():
                State_of_Supply_name = State.objects.get(
                    id=State_of_Supply).Name
        return State_of_Supply_name

    def get_Place_of_Supply(self, instances):
        CompanyID = self.context.get("CompanyID")
        State_Name = ""
        try:
            if State.objects.filter(pk=instances.State_of_Supply).exists():
                State_Name = State.objects.get(
                    pk=instances.State_of_Supply).Name
        except:
            pass

        return State_Name

    def get_CashName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.CashID
        BranchID = instances.BranchID

        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID).exists():
            ledger = AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)
            CashName = ledger.LedgerName
        else:
            CashName = ""
        return CashName

    def get_BankName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.BankID
        BranchID = instances.BranchID

        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID).exists():
            ledger = AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)
            BankName = ledger.LedgerName
        else:
            BankName = ""
        return BankName

    def get_PurchaseDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = int(self.context.get("PriceRounding"))
        QtyRounding = self.context.get("QtyRounding")
        purchase_details = PurchaseDetails.objects.filter(
            CompanyID=CompanyID, PurchaseMasterID=instances.PurchaseMasterID, BranchID=instances.BranchID).order_by('PurchaseDetailsID')
        serialized = PurchaseDetailsRestSerializer(purchase_details, many=True, context={"CompanyID": CompanyID,
                                                                                         "PriceRounding": PriceRounding, "QtyRounding": QtyRounding})

        return serialized.data

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

    def get_CashReceived(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CashReceived = instances.CashReceived

        # CashReceived = round(CashReceived, PriceRounding)

        return str(CashReceived)

    def get_CardTypeName(self, instances):
        CompanyID = self.context.get("CompanyID")
        TransactionTypesID = instances.CardTypeID
        BranchID = instances.BranchID

        if TransactionTypes.objects.filter(CompanyID=CompanyID, TransactionTypesID=TransactionTypesID, BranchID=BranchID).exists():

            transactionType = TransactionTypes.objects.get(
                CompanyID=CompanyID, TransactionTypesID=TransactionTypesID, BranchID=BranchID)
            Name = transactionType.Name

        else:
            Name = ""

        CardTypeName = Name

        return CardTypeName

    def get_CashAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CashAmount = instances.CashAmount

        # CashAmount = round(CashAmount, PriceRounding)

        return str(CashAmount)

    def get_BankAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BankAmount = instances.BankAmount

        # BankAmount = round(BankAmount, PriceRounding)

        return str(BankAmount)

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        LedgerName = ""
        if AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID).exists():
            ledger = AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)

            LedgerName = ledger.LedgerName

        return LedgerName

    def get_PriceCategoryName(self, instances):
        CompanyID = self.context.get("CompanyID")

        PriceCategoryID = instances.PriceCategoryID
        BranchID = instances.BranchID

        PriceCategoryName = ""
        if PriceCategory.objects.filter(CompanyID=CompanyID, PriceCategoryID=PriceCategoryID, BranchID=BranchID).exists():

            PriceCategoryName = PriceCategory.objects.get(
                CompanyID=CompanyID, PriceCategoryID=PriceCategoryID, BranchID=BranchID).PriceCategoryName

        return PriceCategoryName

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
        PurchaseAccountName = ""
        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=PurchaseAccount, BranchID=BranchID).exists():
            PurchaseAccountName = AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=PurchaseAccount, BranchID=BranchID).LedgerName

        return PurchaseAccountName

    def get_TotalGrossAmt(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalGrossAmt = instances.TotalGrossAmt

        # TotalGrossAmt = round(TotalGrossAmt, PriceRounding)

        return str(TotalGrossAmt)

    def get_AddlDiscPercent(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        AddlDiscPercent = instances.AddlDiscPercent
        if not AddlDiscPercent == None:
            AddlDiscPercent = round(AddlDiscPercent, PriceRounding)
        else:
            AddlDiscPercent = 0

        return str(AddlDiscPercent)

    def get_AddlDiscAmt(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        AddlDiscAmt = instances.AddlDiscAmt
        # if not AddlDiscAmt == None:
        #     AddlDiscAmt = round(AddlDiscAmt, PriceRounding)
        # else:
        #     AddlDiscAmt = 0

        return str(AddlDiscAmt)

    def get_TotalDiscount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalDiscount = instances.TotalDiscount
        # if not TotalDiscount == None:
        #     TotalDiscount = round(TotalDiscount, PriceRounding)
        # else:
        #     TotalDiscount = 0

        return str(TotalDiscount)

    def get_TotalTax_rounded(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalTax = instances.TotalTax

        TotalTax_rounded = round(TotalTax, PriceRounding)

        return str(TotalTax_rounded)

    def get_TotalTax(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalTax = instances.TotalTax

        # TotalTax = round(TotalTax, PriceRounding)

        return str(TotalTax)

    def get_NetTotal(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        NetTotal = instances.NetTotal

        # NetTotal = round(NetTotal, PriceRounding)

        return str(NetTotal)

    def get_AdditionalCost(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        AdditionalCost = instances.AdditionalCost
        # if not AdditionalCost == None:
        #     AdditionalCost = round(AdditionalCost, PriceRounding)
        # else:
        #     AdditionalCost = 0

        return str(AdditionalCost)

    def get_GrandTotal(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        GrandTotal = instances.GrandTotal

        # GrandTotal = round(GrandTotal, PriceRounding)

        return str(GrandTotal)

    def get_GrandTotal_Rounded(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        GrandTotal = instances.GrandTotal

        GrandTotal_Rounded = round(GrandTotal, PriceRounding)

        return str(GrandTotal_Rounded)

    def get_RoundOff(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        RoundOff = instances.RoundOff
        # if not RoundOff == None:
        #     RoundOff = round(RoundOff, PriceRounding)
        # else:
        #     RoundOff = 0

        return str(RoundOff)

    def get_VATAmount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        VATAmount = instances.VATAmount

        # VATAmount = round(VATAmount, PriceRounding)

        return str(VATAmount)

    def get_SGSTAmount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        SGSTAmount = instances.SGSTAmount

        # SGSTAmount = round(SGSTAmount, PriceRounding)

        return str(SGSTAmount)

    def get_CGSTAmount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        CGSTAmount = instances.CGSTAmount

        # CGSTAmount = round(CGSTAmount, PriceRounding)

        return str(CGSTAmount)

    def get_IGSTAmount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        IGSTAmount = instances.IGSTAmount

        # IGSTAmount = round(IGSTAmount, PriceRounding)

        return str(IGSTAmount)

    def get_TAX1Amount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX1Amount = instances.TAX1Amount

        # TAX1Amount = round(TAX1Amount, PriceRounding)

        return str(TAX1Amount)

    def get_TAX2Amount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX2Amount = instances.TAX2Amount

        # TAX2Amount = round(TAX2Amount, PriceRounding)

        return str(TAX2Amount)

    def get_TAX3Amount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX3Amount = instances.TAX3Amount

        # TAX3Amount = round(TAX3Amount, PriceRounding)

        return str(TAX3Amount)

    def get_BillDiscPercent(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        BillDiscPercent = instances.BillDiscPercent

        # BillDiscPercent = round(BillDiscPercent, PriceRounding)

        return str(BillDiscPercent)

    def get_BillDiscAmt(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        BillDiscAmt = instances.BillDiscAmt

        # BillDiscAmt = round(BillDiscAmt, PriceRounding)

        return str(BillDiscAmt)

    def get_Balance(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        Balance = instances.Balance

        # Balance = round(Balance, PriceRounding)

        return str(Balance)


class PurchaseDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseDetails
        fields = ('id', 'BranchID', 'Action', 'PurchaseMasterID', 'ProductID', 'Qty', 'FreeQty',
                  'UnitPrice', 'RateWithTax', 'CostPerItem',
                  'PriceListID', 'DiscountPerc', 'DiscountAmount', 'AddlDiscPerc', 'AddlDiscAmt',
                  'GrossAmount', 'TaxableAmount', 'VATPerc', 'VATAmount', 'SGSTPerc', 'SGSTAmount', 'CGSTPerc',
                  'CGSTAmount', 'IGSTPerc', 'IGSTAmount', 'NetAmount', 'CreatedDate', 'CreatedUserID',
                  'TAX1Perc', 'TAX1Amount', 'TAX2Perc', 'TAX2Amount', 'TAX3Perc', 'TAX3Amount')


class PurchaseDetailsRestSerializer(serializers.ModelSerializer):

    Qty = serializers.SerializerMethodField()
    FreeQty = serializers.SerializerMethodField()
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
    ManufactureDate = serializers.SerializerMethodField()
    ExpiryDate = serializers.SerializerMethodField()
    ActualUnitPrice = serializers.SerializerMethodField()
    SalesPrice = serializers.SerializerMethodField()
    ProductCode = serializers.SerializerMethodField()
    HSNCode = serializers.SerializerMethodField()
    UnitList = serializers.SerializerMethodField()
    is_inclusive = serializers.SerializerMethodField()
    ProductTaxName = serializers.SerializerMethodField()
    GST_Inclusive = serializers.SerializerMethodField()
    Vat_Inclusive = serializers.SerializerMethodField()
    PurchasePrice = serializers.SerializerMethodField()
    ActualProductTaxName = serializers.SerializerMethodField()
    ActualProductTaxID = serializers.SerializerMethodField()
    unitPrice_print = serializers.SerializerMethodField()
    NetAmount_print = serializers.SerializerMethodField()
    ManufactureDatePrint = serializers.SerializerMethodField()
    ExpiryDatePrint = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseDetails
        fields = ('id', 'unq_id', 'NetAmount_print', 'unitPrice_print', 'PurchaseDetailsID', 'BranchID', 'Action', 'PurchaseMasterID', 'ProductID', 'ProductName', 'Qty', 'FreeQty',
                  'UnitPrice', 'InclusivePrice', 'RateWithTax', 'CostPerItem', 'ManufactureDate', 'ExpiryDate', 'ActualUnitPrice',
                  'PriceListID', 'UnitName', 'DiscountPerc', 'DiscountAmount', 'AddlDiscPerc', 'AddlDiscAmt', 'ProductTaxID', 'PurchasePrice',
                  'GrossAmount', 'TaxableAmount', 'VATPerc', 'VATAmount', 'SGSTPerc', 'SGSTAmount', 'CGSTPerc', 'ProductTaxName',
                  'CGSTAmount', 'IGSTPerc', 'IGSTAmount', 'NetAmount', 'CreatedDate', 'CreatedUserID', 'SalesPrice', 'GST_Inclusive', 'Vat_Inclusive',
                  'TAX1Perc', 'TAX1Amount', 'TAX2Perc', 'TAX2Amount', 'TAX3Perc', 'TAX3Amount', 'TotalTax', 'detailID', 'is_inclusive',
                  'is_VAT_inclusive', 'is_GST_inclusive', 'is_TAX1_inclusive', 'is_TAX2_inclusive', 'is_TAX3_inclusive', 'UnitList', 'ActualProductTaxName', 'ActualProductTaxID',
                  'unitPriceRounded', 'quantityRounded', 'actualPurchasePrice', 'netAmountRounded', 'BatchCode', 'ManufactureDate', 'ExpiryDate', "ProductCode", "HSNCode",
                  'ManufactureDatePrint', 'ExpiryDatePrint')

    def get_ManufactureDatePrint(self, purchase_details):
        ManufactureDate = ""
        CompanyID = self.context.get("CompanyID")
        BranchID = purchase_details.BranchID
        BatchCode = purchase_details.BatchCode
        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
            batch_details = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).first()
            ManufactureDate = batch_details.ManufactureDate
            if ManufactureDate:
                Date = ManufactureDate.strftime("%Y/%m")
                ManufactureDate = Date
        return ManufactureDate

    def get_ExpiryDatePrint(self, purchase_details):
        ExpiryDate = ""
        CompanyID = self.context.get("CompanyID")
        BranchID = purchase_details.BranchID
        BatchCode = purchase_details.BatchCode
        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
            batch_details = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).first()
            ExpiryDate = batch_details.ExpiryDate
            if ExpiryDate:
                Date = ExpiryDate.strftime("%Y/%m")
                ExpiryDate = Date
        return ExpiryDate

    def get_NetAmount_print(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        NetAmount = purchaseReturn_details.NetAmount
        NetAmount = round(NetAmount, PriceRounding)
        return str(NetAmount)

    def get_unitPrice_print(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        UnitPrice = purchaseReturn_details.UnitPrice
        UnitPrice = round(UnitPrice, PriceRounding)
        return str(UnitPrice)

    def get_InclusivePrice(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        InclusivePrice = purchase_details.InclusivePrice
        if InclusivePrice:
            InclusivePrice = round(InclusivePrice, PriceRounding)
        else:
            InclusivePrice = 0

        return str(InclusivePrice)

    def get_ActualProductTaxName(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        ProductTaxID = purchase_details.ProductTaxID
        BranchID = purchase_details.BranchID
        ActualProductTaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, BranchID=BranchID, TaxID=ProductTaxID).exists():
            ActualProductTaxName = TaxCategory.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, TaxID=ProductTaxID).TaxName
        return ActualProductTaxName

    def get_ActualProductTaxID(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        ActualProductTaxID = purchase_details.ProductTaxID
        return ActualProductTaxID

    def get_PurchasePrice(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = purchase_details.PriceListID
        BranchID = purchase_details.BranchID
        PurchasePrice = 0
        if PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID).exists():
            PurchasePrice = PriceList.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID).PurchasePrice
        return float(PurchasePrice)

    def get_ProductTaxName(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        ProductTaxID = purchase_details.ProductTaxID
        BranchID = purchase_details.BranchID
        ProductTaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, BranchID=BranchID, TaxID=ProductTaxID).exists():
            ProductTaxName = TaxCategory.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, TaxID=ProductTaxID).TaxName
        return ProductTaxName

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

    def get_Vat_Inclusive(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchase_details.BranchID
        ProductID = purchase_details.ProductID
        ProductTaxID = purchase_details.ProductTaxID
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

    def get_GST_Inclusive(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchase_details.BranchID
        ProductID = purchase_details.ProductID
        ProductTaxID = purchase_details.ProductTaxID
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

    def get_is_inclusive(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchase_details.BranchID
        ProductID = purchase_details.ProductID
        is_inclusive = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).is_inclusive

        return is_inclusive

    # def get_is_inclusive(self, purchase_details):
    #     CompanyID = self.context.get("CompanyID")
    #     BranchID = purchase_details.BranchID
    #     ProductID = purchase_details.ProductID
    #     pro_ins = Product.objects.get(
    #         CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)
    #     GST = pro_ins.GST
    #     VatID = pro_ins.VatID
    #     Tax1 = pro_ins.Tax1
    #     Tax2 = pro_ins.Tax2
    #     Tax3 = pro_ins.Tax3
    #     is_inclusive = False
    #     GST_inclusive = False
    #     VAT_inclusive = False
    #     Tax1_inclusive = False
    #     Tax2_inclusive = False
    #     Tax3_inclusive = False
    #     if GST:
    #         GST_inclusive = TaxCategory.objects.get(
    #             CompanyID=CompanyID, TaxID=GST, BranchID=BranchID).Inclusive
    #     if VatID:
    #         VAT_inclusive = TaxCategory.objects.get(
    #             CompanyID=CompanyID, TaxID=VatID, BranchID=BranchID).Inclusive
    #     if Tax1:
    #         Tax1_inclusive = TaxCategory.objects.get(
    #             CompanyID=CompanyID, TaxID=Tax1, BranchID=BranchID).Inclusive
    #     if Tax2:
    #         Tax2_inclusive = TaxCategory.objects.get(
    #             CompanyID=CompanyID, TaxID=Tax2, BranchID=BranchID).Inclusive
    #     if Tax3:
    #         Tax3_inclusive = TaxCategory.objects.get(
    #             CompanyID=CompanyID, TaxID=Tax3, BranchID=BranchID).Inclusive

    #     if GST_inclusive == True or VAT_inclusive == True or Tax1_inclusive == True or Tax2_inclusive == True or Tax3_inclusive == True:
    #         is_inclusive = True

    #     return is_inclusive

    def get_ProductCode(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        ProductID = purchase_details.ProductID
        BranchID = purchase_details.BranchID

        product = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)

        ProductCode = product.ProductCode
        return ProductCode

    def get_HSNCode(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        ProductID = purchase_details.ProductID
        BranchID = purchase_details.BranchID

        product = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)

        HSNCode = product.HSNCode
        return HSNCode

    def get_ManufactureDate(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        ManufactureDate = purchase_details.ManufactureDate
        if ManufactureDate:
            ManufactureDate = '{:%Y-%m}'.format(
                dt.strptime(str(ManufactureDate), '%Y-%m-%d'))

        return ManufactureDate

    def get_ExpiryDate(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        ExpiryDate = purchase_details.ExpiryDate
        if ExpiryDate:
            ExpiryDate = '{:%Y-%m}'.format(
                dt.strptime(str(ExpiryDate), '%Y-%m-%d'))

        return ExpiryDate

    def get_BatchCode(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        BatchCode = purchase_details.BatchCode
        BranchID = purchase_details.BranchID
        if not BatchCode:
            BatchCode = 0

        return BatchCode

    def get_unitPriceRounded(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        UnitPrice = purchase_details.UnitPrice
        # UnitPrice = round(UnitPrice, PriceRounding)
        return str(UnitPrice)

    def get_quantityRounded(self, purchase_details):
        Qty = purchase_details.Qty
        return Qty

    def get_SalesPrice(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = purchase_details.PriceListID
        BranchID = purchase_details.BranchID
        ProductID = purchase_details.ProductID
        SalesPrice = ''
        if PriceList.objects.filter(ProductID=ProductID, CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).exists():
            SalesPrice = PriceList.objects.get(
                ProductID=ProductID, CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).SalesPrice
        return str(SalesPrice)

    def get_actualPurchasePrice(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = purchase_details.PriceListID
        BranchID = purchase_details.BranchID
        ProductID = purchase_details.ProductID
        PurchasePrice = ''
        if PriceList.objects.filter(ProductID=ProductID, CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).exists():
            PurchasePrice = PriceList.objects.get(
                ProductID=ProductID, CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).PurchasePrice
        return str(PurchasePrice)

    def get_netAmountRounded(self, purchase_details):
        NetAmount = purchase_details.NetAmount
        return str(NetAmount)

    def get_is_VAT_inclusive(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchase_details.BranchID
        ProductID = purchase_details.ProductID
        VatID = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).VatID
        Inclusive = False
        if VatID:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=VatID, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_GST_inclusive(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchase_details.BranchID
        ProductID = purchase_details.ProductID
        Inclusive = False
        GST = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).GST
        if GST:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=GST, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_TAX1_inclusive(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchase_details.BranchID
        ProductID = purchase_details.ProductID
        Inclusive = False
        Tax1 = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).Tax1
        if Tax1:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax1, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_TAX2_inclusive(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchase_details.BranchID
        ProductID = purchase_details.ProductID
        Inclusive = False
        Tax2 = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).Tax2
        if Tax2:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax2, BranchID=BranchID).Inclusive
        return Inclusive

    def get_is_TAX3_inclusive(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchase_details.BranchID
        ProductID = purchase_details.ProductID
        Inclusive = False
        Tax3 = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).Tax3
        if Tax3:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax3, BranchID=BranchID).Inclusive
        return Inclusive

    def get_TotalTax(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        TAX1Amount = purchase_details.TAX1Amount
        TAX2Amount = purchase_details.TAX2Amount
        TAX3Amount = purchase_details.TAX3Amount
        VATAmount = purchase_details.VATAmount
        CGSTAmount = purchase_details.CGSTAmount
        SGSTAmount = purchase_details.SGSTAmount
        IGSTAmount = purchase_details.IGSTAmount
        TotalTax = (TAX1Amount + TAX2Amount + TAX3Amount +
                    VATAmount + CGSTAmount + SGSTAmount + IGSTAmount)

        return str(TotalTax)

    def get_unq_id(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        unq_id = purchase_details.id

        return unq_id

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
        PriceRounding = int(self.context.get("PriceRounding"))
        Qty = purchase_details.Qty

        # if Qty:
        #     Qty = round(Qty, PriceRounding)
        # else:
        #     Qty = 0

        return float(Qty)

    def get_FreeQty(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        FreeQty = purchase_details.FreeQty
        # if FreeQty:
        #     FreeQty = round(FreeQty, PriceRounding)
        # else:
        #     FreeQty = 0

        return float(FreeQty)

    def get_UnitPrice(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        UnitPrice = purchase_details.UnitPrice
        # if UnitPrice:
        #     UnitPrice = round(UnitPrice, PriceRounding)
        # else:
        #     UnitPrice = 0

        return float(UnitPrice)

    def get_ActualUnitPrice(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        ActualUnitPrice = purchase_details.UnitPrice

        # ActualUnitPrice = round(ActualUnitPrice, PriceRounding)
        return float(ActualUnitPrice)

    def get_RateWithTax(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        RateWithTax = purchase_details.RateWithTax
        # if RateWithTax:
        #     RateWithTax = round(RateWithTax, PriceRounding)
        # else:
        #     RateWithTax = 0

        return float(RateWithTax)

    def get_CostPerItem(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        CostPerItem = purchase_details.CostPerItem

        # if CostPerItem:
        #     CostPerItem = round(CostPerItem, PriceRounding)
        # else:
        #     CostPerItem = 0

        return float(CostPerItem)

    def get_DiscountPerc(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        DiscountPerc = purchase_details.DiscountPerc

        # if DiscountPerc:
        #     DiscountPerc = round(DiscountPerc, PriceRounding)
        # else:
        #     DiscountPerc = 0

        return float(DiscountPerc)

    def get_DiscountAmount(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        DiscountAmount = purchase_details.DiscountAmount

        # if DiscountAmount:
        #     DiscountAmount = round(DiscountAmount, PriceRounding)
        # else:
        #     DiscountAmount = 0

        return float(DiscountAmount)

    def get_AddlDiscPerc(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        AddlDiscPerc = purchase_details.AddlDiscPerc

        # if AddlDiscPerc:
        #     AddlDiscPerc = round(AddlDiscPerc, PriceRounding)
        # else:
        #     AddlDiscPerc = 0

        return str(AddlDiscPerc)

    def get_AddlDiscAmt(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        AddlDiscAmt = purchase_details.AddlDiscAmt

        # if AddlDiscAmt:
        #     AddlDiscAmt = round(AddlDiscAmt, PriceRounding)
        # else:
        #     AddlDiscAmt = 0

        return str(AddlDiscAmt)

    def get_GrossAmount(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        GrossAmount = purchase_details.GrossAmount

        # GrossAmount = round(GrossAmount, PriceRounding)

        return str(GrossAmount)

    def get_TaxableAmount(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        TaxableAmount = purchase_details.TaxableAmount

        # if TaxableAmount:
        #     TaxableAmount = round(TaxableAmount, PriceRounding)
        # else:
        #     TaxableAmount = 0

        return str(TaxableAmount)

    def get_VATPerc(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        VATPerc = purchase_details.VATPerc

        # if VATPerc:

        #     VATPerc = round(VATPerc, PriceRounding)
        # else:
        #     VATPerc = 0

        return str(VATPerc)

    def get_VATAmount(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        VATAmount = purchase_details.VATAmount

        # if VATAmount:
        #     VATAmount = round(VATAmount, PriceRounding)
        # else:
        #     VATAmount = 0

        return str(VATAmount)

    def get_SGSTPerc(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        SGSTPerc = purchase_details.SGSTPerc

        # if SGSTPerc:
        #     SGSTPerc = round(SGSTPerc, PriceRounding)
        # else:
        #     SGSTPerc = 0

        return str(SGSTPerc)

    def get_SGSTAmount(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        SGSTAmount = purchase_details.SGSTAmount

        # if SGSTAmount:
        #     SGSTAmount = round(SGSTAmount, PriceRounding)
        # else:
        #     SGSTAmount = 0

        return str(SGSTAmount)

    def get_CGSTPerc(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        CGSTPerc = purchase_details.CGSTPerc

        # if CGSTPerc:
        #     CGSTPerc = round(CGSTPerc, PriceRounding)
        # else:
        #     CGSTPerc = 0

        return str(CGSTPerc)

    def get_CGSTAmount(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        CGSTAmount = purchase_details.CGSTAmount

        # if CGSTAmount:
        #     CGSTAmount = round(CGSTAmount, PriceRounding)
        # else:
        #     CGSTAmount = 0

        return str(CGSTAmount)

    def get_IGSTPerc(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        IGSTPerc = purchase_details.IGSTPerc

        # if IGSTPerc:
        #     IGSTPerc = round(IGSTPerc, PriceRounding)
        # else:
        #     IGSTPerc = 0

        return str(IGSTPerc)

    def get_IGSTAmount(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        IGSTAmount = purchase_details.IGSTAmount

        # if IGSTAmount:
        #     IGSTAmount = round(IGSTAmount, PriceRounding)
        # else:
        #     IGSTAmount = 0

        return str(IGSTAmount)

    def get_TAX1Perc(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX1Perc = purchase_details.TAX1Perc

        # if TAX1Perc:
        #     TAX1Perc = round(TAX1Perc, PriceRounding)
        # else:
        #     TAX1Perc = 0

        return str(TAX1Perc)

    def get_TAX2Perc(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX2Perc = purchase_details.TAX2Perc

        # if TAX2Perc:
        #     TAX2Perc = round(TAX2Perc, PriceRounding)
        # else:
        #     TAX2Perc = 0

        return str(TAX2Perc)

    def get_TAX3Perc(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX3Perc = purchase_details.TAX3Perc

        # if TAX3Perc:
        #     TAX3Perc = round(TAX3Perc, PriceRounding)
        # else:
        #     TAX3Perc = 0

        return str(TAX3Perc)

    def get_TAX1Amount(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX1Amount = purchase_details.TAX1Amount

        # if TAX1Amount:
        #     TAX1Amount = round(TAX1Amount, PriceRounding)
        # else:
        #     TAX1Amount = 0

        return str(TAX1Amount)

    def get_TAX2Amount(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX2Amount = purchase_details.TAX2Amount

        # if TAX2Amount:
        #     TAX2Amount = round(TAX2Amount, PriceRounding)
        # else:
        #     TAX2Amount = 0

        return str(TAX2Amount)

    def get_TAX3Amount(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX3Amount = purchase_details.TAX3Amount

        # if TAX3Amount:
        #     TAX3Amount = round(TAX3Amount, PriceRounding)
        # else:
        #     TAX3Amount = 0

        return str(TAX3Amount)

    def get_NetAmount(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        NetAmount = purchase_details.NetAmount

        # if NetAmount:
        #     NetAmount = round(NetAmount, PriceRounding)
        # else:
        #     NetAmount = 0

        return str(NetAmount)


class PurchaseMasterReportSerializer(serializers.ModelSerializer):

    Details = serializers.SerializerMethodField()
    TotalGrossAmt = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    NetTotal = serializers.SerializerMethodField()
    AddlDiscPercent = serializers.SerializerMethodField()
    AddlDiscAmt = serializers.SerializerMethodField()
    AdditionalCost = serializers.SerializerMethodField()
    TotalDiscount = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    RoundOff = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    AccountName = serializers.SerializerMethodField()
    MasterID = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseMaster
        fields = ('id', 'MasterID', 'BranchID', 'Action', 'VoucherNo', 'RefferenceBillNo', 'Date',
                  'VenderInvoiceDate', 'CreditPeriod', 'LedgerID', 'LedgerName',
                  'PriceCategoryID', 'EmployeeID', 'PurchaseAccount', 'AccountName', 'CustomerName', 'Address1', 'Address2', 'Address3',
                  'Notes', 'FinacialYearID', 'TotalGrossAmt', 'TotalTax', 'NetTotal', 'AddlDiscPercent', 'AddlDiscAmt',
                  'AdditionalCost', 'TotalDiscount', 'GrandTotal', 'RoundOff', 'TransactionTypeID', 'WarehouseID', 'IsActive', 'CreatedDate', 'CreatedUserID',
                  'TaxID', 'TaxType', 'VATAmount', 'SGSTAmount', 'CGSTAmount', 'IGSTAmount', 'TAX1Amount', 'TAX2Amount', 'TAX3Amount', 'BillDiscPercent', 'BillDiscAmt', 'Balance', 'Details')

    def get_Details(self, instances):
        CompanyID = self.context.get("CompanyID")
        purchase_details = PurchaseDetails.objects.filter(
            CompanyID=CompanyID, PurchaseMasterID=instances.PurchaseMasterID, BranchID=instances.BranchID)
        serialized = PurchaseDetailsReportSerializer(
            purchase_details, many=True, context={"CompanyID": CompanyID})

        return serialized.data

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(
            CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)

        if ledger:
            LedgerName = ledger.LedgerName
        else:
            LedgerName = ""

        return LedgerName

    def get_AccountName(self, instances):
        CompanyID = self.context.get("CompanyID")

        PurchaseAccount = instances.PurchaseAccount
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(
            CompanyID=CompanyID, LedgerID=PurchaseAccount, BranchID=BranchID)

        AccountName = ledger.LedgerName

        return AccountName

    def get_MasterID(self, instances):

        MasterID = instances.PurchaseMasterID

        return MasterID

    def get_TotalGrossAmt(self, instances):

        TotalGrossAmt = instances.TotalGrossAmt

        TotalGrossAmt = round(TotalGrossAmt, 2)

        return str(TotalGrossAmt)

    def get_AddlDiscPercent(self, instances):

        AddlDiscPercent = instances.AddlDiscPercent

        AddlDiscPercent = round(AddlDiscPercent, 2)

        return str(AddlDiscPercent)

    def get_AddlDiscAmt(self, instances):

        AddlDiscAmt = instances.AddlDiscAmt

        AddlDiscAmt = round(AddlDiscAmt, 2)

        return str(AddlDiscAmt)

    def get_TotalDiscount(self, instances):

        TotalDiscount = instances.TotalDiscount

        TotalDiscount = round(TotalDiscount, 2)

        return str(TotalDiscount)

    def get_TotalTax(self, instances):

        TotalTax = instances.TotalTax

        TotalTax = round(TotalTax, 2)

        return str(TotalTax)

    def get_NetTotal(self, instances):

        NetTotal = instances.NetTotal

        NetTotal = round(NetTotal, 2)

        return str(NetTotal)

    def get_AdditionalCost(self, instances):

        AdditionalCost = instances.AdditionalCost

        AdditionalCost = round(AdditionalCost, 2)

        return str(AdditionalCost)

    def get_GrandTotal(self, instances):

        GrandTotal = instances.GrandTotal

        GrandTotal = round(GrandTotal, 2)

        return str(GrandTotal)

    def get_RoundOff(self, instances):

        RoundOff = instances.RoundOff

        RoundOff = round(RoundOff, 2)

        return str(RoundOff)


class PurchaseDetailsReportSerializer(serializers.ModelSerializer):

    Qty = serializers.SerializerMethodField()
    FreeQty = serializers.SerializerMethodField()
    UnitPrice = serializers.SerializerMethodField()
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

    class Meta:
        model = PurchaseDetails
        fields = ('id', 'PurchaseDetailsID', 'BranchID', 'Action', 'PurchaseMasterID', 'ProductID', 'ProductName', 'Qty', 'FreeQty',
                  'UnitPrice', 'RateWithTax', 'CostPerItem',
                  'PriceListID', 'DiscountPerc', 'DiscountAmount', 'AddlDiscPerc', 'AddlDiscAmt',
                  'GrossAmount', 'TaxableAmount', 'VATPerc', 'VATAmount', 'SGSTPerc', 'SGSTAmount', 'CGSTPerc',
                  'CGSTAmount', 'IGSTPerc', 'IGSTAmount', 'NetAmount', 'CreatedDate', 'CreatedUserID',
                  'TAX1Perc', 'TAX1Amount', 'TAX2Perc', 'TAX2Amount', 'TAX3Perc', 'TAX3Amount')

    def get_ProductName(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        ProductID = purchase_details.ProductID
        BranchID = purchase_details.BranchID

        product = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)

        if product:
            ProductName = product.ProductName
        else:
            ProductName = ""

        return ProductName

    def get_Qty(self, purchase_details):

        Qty = purchase_details.Qty

        Qty = round(Qty, 2)

        return str(Qty)

    def get_FreeQty(self, purchase_details):

        FreeQty = purchase_details.FreeQty

        FreeQty = round(FreeQty, 2)

        return str(FreeQty)

    def get_UnitPrice(self, purchase_details):

        UnitPrice = purchase_details.UnitPrice

        UnitPrice = round(UnitPrice, 2)

        return str(UnitPrice)

    def get_RateWithTax(self, purchase_details):

        RateWithTax = purchase_details.RateWithTax

        RateWithTax = round(RateWithTax, 2)

        return str(RateWithTax)

    def get_CostPerItem(self, purchase_details):

        CostPerItem = purchase_details.CostPerItem

        CostPerItem = round(CostPerItem, 2)

        return str(CostPerItem)

    def get_DiscountPerc(self, purchase_details):

        DiscountPerc = purchase_details.DiscountPerc

        DiscountPerc = round(DiscountPerc, 2)

        return str(DiscountPerc)

    def get_DiscountAmount(self, purchase_details):

        DiscountAmount = purchase_details.DiscountAmount

        DiscountAmount = round(DiscountAmount, 2)

        return str(DiscountAmount)

    def get_AddlDiscPerc(self, purchase_details):

        AddlDiscPerc = purchase_details.AddlDiscPerc

        AddlDiscPerc = round(AddlDiscPerc, 2)

        return str(AddlDiscPerc)

    def get_AddlDiscAmt(self, purchase_details):

        AddlDiscAmt = purchase_details.AddlDiscAmt

        AddlDiscAmt = round(AddlDiscAmt, 2)

        return str(AddlDiscAmt)

    def get_GrossAmount(self, purchase_details):

        GrossAmount = purchase_details.GrossAmount

        GrossAmount = round(GrossAmount, 2)

        return str(GrossAmount)

    def get_TaxableAmount(self, purchase_details):

        TaxableAmount = purchase_details.TaxableAmount

        TaxableAmount = round(TaxableAmount, 2)

        return str(TaxableAmount)

    def get_VATPerc(self, purchase_details):

        VATPerc = purchase_details.VATPerc

        VATPerc = round(VATPerc, 2)

        return str(VATPerc)

    def get_VATAmount(self, purchase_details):

        VATAmount = purchase_details.VATAmount

        VATAmount = round(VATAmount, 2)

        return str(VATAmount)

    def get_SGSTPerc(self, purchase_details):

        SGSTPerc = purchase_details.SGSTPerc

        SGSTPerc = round(SGSTPerc, 2)

        return str(SGSTPerc)

    def get_SGSTAmount(self, purchase_details):

        SGSTAmount = purchase_details.SGSTAmount

        SGSTAmount = round(SGSTAmount, 2)

        return str(SGSTAmount)

    def get_CGSTPerc(self, purchase_details):

        CGSTPerc = purchase_details.CGSTPerc

        CGSTPerc = round(CGSTPerc, 2)

        return str(CGSTPerc)

    def get_CGSTAmount(self, purchase_details):

        CGSTAmount = purchase_details.CGSTAmount

        CGSTAmount = round(CGSTAmount, 2)

        return str(CGSTAmount)

    def get_IGSTPerc(self, purchase_details):

        IGSTPerc = purchase_details.IGSTPerc

        IGSTPerc = round(IGSTPerc, 2)

        return str(IGSTPerc)

    def get_IGSTAmount(self, purchase_details):

        IGSTAmount = purchase_details.IGSTAmount

        IGSTAmount = round(IGSTAmount, 2)

        return str(IGSTAmount)

    def get_NetAmount(self, purchase_details):

        NetAmount = purchase_details.NetAmount

        NetAmount = round(NetAmount, 2)

        return str(NetAmount)


class PurchaseMasterForReturnSerializer(serializers.ModelSerializer):

    PurchaseDetails = serializers.SerializerMethodField()
    TotalGrossAmt = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    NetTotal = serializers.SerializerMethodField()
    AddlDiscPercent = serializers.SerializerMethodField()
    AddlDiscAmt = serializers.SerializerMethodField()
    AdditionalCost = serializers.SerializerMethodField()
    TotalDiscount = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    RoundOff = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    PurchaseAccountName = serializers.SerializerMethodField()
    WareHouseName = serializers.SerializerMethodField()
    DetailID = serializers.SerializerMethodField()
    BillDiscPercent = serializers.SerializerMethodField()
    BillDiscAmt = serializers.SerializerMethodField()
    ProductList = serializers.SerializerMethodField()
    LedgerList = serializers.SerializerMethodField()
    is_customer = serializers.SerializerMethodField()
    Mobile = serializers.SerializerMethodField()
    GSTNumber = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseMaster
        fields = ('id', 'PurchaseMasterID', 'BranchID', 'Action', 'VoucherNo', 'RefferenceBillNo', 'Date',
                  'VenderInvoiceDate', 'CreditPeriod', 'LedgerID', 'LedgerName', 'GST_Treatment',
                  'CreditPeriod', 'LedgerID', 'LedgerName', 'ProductList', 'Mobile', 'LedgerList', 'GSTNumber', 'Country_of_Supply', 'State_of_Supply', 'VAT_Treatment',
                  'PriceCategoryID', 'EmployeeID', 'PurchaseAccount', 'PurchaseAccountName', 'CustomerName', 'Address1', 'Address2', 'Address3',
                  'Notes', 'FinacialYearID', 'TotalGrossAmt', 'TotalTax', 'NetTotal', 'AddlDiscPercent', 'AddlDiscAmt',
                  'AdditionalCost', 'TotalDiscount', 'GrandTotal', 'RoundOff', 'TransactionTypeID', 'WarehouseID', 'WareHouseName', 'IsActive', 'CreatedDate', 'CreatedUserID',
                  'TaxID', 'TaxType', 'VATAmount', 'SGSTAmount', 'CGSTAmount', 'IGSTAmount', 'TAX1Amount', 'TAX2Amount', 'TAX3Amount', 'BillDiscPercent', 'BillDiscAmt', 'Balance', 'DetailID', 'PurchaseDetails',
                  'ProductList', 'LedgerList', 'is_customer', 'Mobile', 'GSTNumber')

    def get_PurchaseDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = int(self.context.get("PriceRounding"))
        purchase_details = PurchaseDetails.objects.filter(
            CompanyID=CompanyID, PurchaseMasterID=instances.PurchaseMasterID, BranchID=instances.BranchID)
        serialized = PurchaseDetailsForReturnsSerializer(purchase_details, many=True, context={
                                                         "CompanyID": CompanyID, "PriceRounding": PriceRounding})

        return serialized.data

    def get_GSTNumber(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        GSTNumber = ""
        if Parties.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).exists():
            pary_ins = Parties.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).first()
            GSTNumber = pary_ins.GSTNumber
        return str(GSTNumber)

    def get_LedgerList(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        LedgerID = instances.LedgerID
        LedgerName = AccountLedger.objects.get(
            CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID).LedgerName
        LedgerList = [{
            "name": LedgerName,
            "LedgerID": LedgerID,
        }]

        return LedgerList

    def get_Mobile(self, instances):

        CompanyID = self.context.get("CompanyID")
        Mobile = ""
        if Parties.objects.filter(LedgerID=instances.LedgerID, CompanyID=CompanyID).exists():
            Mobile = Parties.objects.get(
                LedgerID=instances.LedgerID, CompanyID=CompanyID).Mobile

        return str(Mobile)

    def get_is_customer(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        is_customer = False
        groups = [10, 29]
        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=groups).exists():
            is_customer = True

        return is_customer

    def get_ProductList(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        PurchaseMasterID = instances.PurchaseMasterID
        purchase_details = PurchaseDetails.objects.filter(
            CompanyID=CompanyID, PurchaseMasterID=PurchaseMasterID, BranchID=BranchID)

        product_ids = purchase_details.values_list('ProductID', flat=True)
        produc_instances = Product.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_ids)
        ProductList = []
        for p in produc_instances:
            ProductList.append({
                "ProductName": p.ProductName,
                "ProductID": p.ProductID,
            })

        return ProductList

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

    def get_TotalGrossAmt(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalGrossAmt = instances.TotalGrossAmt

        TotalGrossAmt = round(TotalGrossAmt, PriceRounding)

        return str(TotalGrossAmt)

    def get_AddlDiscPercent(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        AddlDiscPercent = instances.AddlDiscPercent
        if not AddlDiscPercent == None:
            AddlDiscPercent = round(AddlDiscPercent, PriceRounding)
        else:
            AddlDiscPercent = 0

        return str(AddlDiscPercent)

    def get_AddlDiscAmt(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        AddlDiscAmt = instances.AddlDiscAmt
        if not AddlDiscAmt == None:
            AddlDiscAmt = round(AddlDiscAmt, PriceRounding)
        else:
            AddlDiscAmt = 0

        return str(AddlDiscAmt)

    def get_TotalDiscount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalDiscount = instances.TotalDiscount
        if not TotalDiscount == None:
            TotalDiscount = round(TotalDiscount, PriceRounding)
        else:
            TotalDiscount = 0

        return str(TotalDiscount)

    def get_TotalTax(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalTax = instances.TotalTax

        TotalTax = round(TotalTax, PriceRounding)

        return str(TotalTax)

    def get_NetTotal(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        NetTotal = instances.NetTotal

        NetTotal = round(NetTotal, PriceRounding)

        return str(NetTotal)

    def get_AdditionalCost(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        AdditionalCost = instances.AdditionalCost
        if not AdditionalCost == None:
            AdditionalCost = round(AdditionalCost, PriceRounding)
        else:
            AdditionalCost = 0

        return str(AdditionalCost)

    def get_GrandTotal(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        GrandTotal = instances.GrandTotal

        GrandTotal = round(GrandTotal, PriceRounding)

        return str(GrandTotal)

    def get_RoundOff(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        RoundOff = instances.RoundOff
        if not RoundOff == None:
            RoundOff = round(RoundOff, PriceRounding)
        else:
            RoundOff = 0

        return str(RoundOff)

    def get_BillDiscPercent(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        BillDiscPercent = instances.BillDiscPercent
        if not BillDiscPercent == None:
            BillDiscPercent = round(BillDiscPercent, PriceRounding)
        else:
            BillDiscPercent = 0

        return str(BillDiscPercent)

    def get_BillDiscAmt(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        BillDiscAmt = instances.BillDiscAmt
        if not BillDiscAmt == None:
            BillDiscAmt = round(BillDiscAmt, PriceRounding)
        else:
            BillDiscAmt = 0

        return str(BillDiscAmt)


class PurchaseDetailsForReturnsSerializer(serializers.ModelSerializer):

    Qty = serializers.SerializerMethodField()
    FreeQty = serializers.SerializerMethodField()
    UnitPrice = serializers.SerializerMethodField()
    InclusivePrice = serializers.SerializerMethodField()
    RateWithTax = serializers.SerializerMethodField()
    CostPerItem = serializers.SerializerMethodField()
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
    UnitList = serializers.SerializerMethodField()
    BatchCode_list = serializers.SerializerMethodField()
    BatchCode = serializers.SerializerMethodField()
    BatchList = serializers.SerializerMethodField()
    ActualUnitPrice = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseDetails
        fields = ('id', 'unq_id', 'PurchaseDetailsID', 'BranchID', 'Action', 'PurchaseMasterID', 'ProductID', 'UnitList', 'ProductName', 'Qty', 'FreeQty',
                  'UnitPrice', 'InclusivePrice', 'RateWithTax', 'CostPerItem', 'DeliveryDetailsID', 'OrderDetailsID', 'CostPerPrice',
                  'PriceListID', 'UnitName', 'DiscountPerc', 'DiscountAmount', 'AddlDiscPerc', 'AddlDiscAmt', 'ActualUnitPrice',
                  'GrossAmount', 'TaxableAmount', 'VATPerc', 'VATAmount', 'SGSTPerc', 'SGSTAmount', 'CGSTPerc', 'BatchCode_list', 'BatchCode',
                  'CGSTAmount', 'IGSTPerc', 'IGSTAmount', 'NetAmount', 'CreatedDate', 'CreatedUserID', 'ExistingQty', 'ProductTaxID',
                  'TAX1Perc', 'TAX1Amount', 'TAX2Perc', 'TAX2Amount', 'TAX3Perc', 'TAX3Amount', 'TotalTax', 'detailID', 'BatchList')

    def get_ActualUnitPrice(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        ActualUnitPrice = purchase_details.UnitPrice
        return ActualUnitPrice

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

    def get_BatchCode(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        BatchCode = purchase_details.BatchCode
        BranchID = purchase_details.BranchID
        if not BatchCode:
            BatchCode = 0

        return str(BatchCode)

    def get_BatchCode_list(self, purchase_details):
        BatchCode_list = []
        CompanyID = self.context.get("CompanyID")
        PriceRounding = int(self.context.get("PriceRounding"))
        BranchID = purchase_details.BranchID
        ProductID = purchase_details.ProductID
        BatchCode_list = []
        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
            batch_details = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
            BatchCode_list = Batch_ListSerializer(batch_details, many=True, context={"CompanyID": CompanyID,
                                                                                     "PriceRounding": PriceRounding})
            BatchCode_list = BatchCode_list.data
        return BatchCode_list

    def get_BatchList(self, purchase_details):
        BatchCode_list = []
        CompanyID = self.context.get("CompanyID")
        PriceRounding = int(self.context.get("PriceRounding"))
        BranchID = purchase_details.BranchID
        ProductID = purchase_details.ProductID
        BatchCode_list = []
        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
            batch_details = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
            BatchCode_list = Batch_ListSerializer(batch_details, many=True, context={"CompanyID": CompanyID,
                                                                                     "PriceRounding": PriceRounding})
            BatchCode_list = BatchCode_list.data
        return BatchCode_list

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

    def get_ExistingQty(self, purchase_details):
        ReturnQty = purchase_details.ReturnQty
        ExistingQty = ReturnQty
        return ExistingQty

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
        CGSTAmount = purchase_details.CGSTAmount
        SGSTAmount = purchase_details.SGSTAmount
        IGSTAmount = purchase_details.IGSTAmount

        TotalTax = (TAX1Amount + TAX2Amount + TAX3Amount +
                    VATAmount + CGSTAmount + SGSTAmount + IGSTAmount)

        return TotalTax

    def get_unq_id(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        unq_id = purchase_details.id

        return unq_id

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
                BranchID=BranchID, CompanyID=CompanyID, UnitID=UnitID).UnitName
        else:
            UnitName = ""

        return UnitName

    def get_Qty(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        Qty = purchase_details.ReturnQty
        if Qty:
            Qty = round(Qty, PriceRounding)
        else:
            Qty = 0

        return str(Qty)

    def get_FreeQty(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        FreeQty = purchase_details.FreeQty
        if FreeQty:
            FreeQty = round(FreeQty, PriceRounding)
        else:
            FreeQty = 0

        return str(FreeQty)

    def get_UnitPrice(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        UnitPrice = purchase_details.UnitPrice
        if UnitPrice:
            UnitPrice = round(UnitPrice, PriceRounding)
        else:
            UnitPrice = 0

        return str(UnitPrice)

    def get_InclusivePrice(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        InclusivePrice = purchase_details.InclusivePrice
        if InclusivePrice:
            InclusivePrice = round(InclusivePrice, PriceRounding)
        else:
            InclusivePrice = 0

        return str(InclusivePrice)

    def get_RateWithTax(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        RateWithTax = purchase_details.RateWithTax
        if RateWithTax:
            RateWithTax = round(RateWithTax, PriceRounding)
        else:
            RateWithTax = 0

        return str(RateWithTax)

    def get_CostPerPrice(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        CostPerPrice = purchase_details.CostPerItem

        if CostPerPrice:
            CostPerPrice = round(CostPerPrice, PriceRounding)
        else:
            CostPerPrice = 0

        return str(CostPerPrice)

    def get_CostPerItem(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        CostPerItem = purchase_details.CostPerItem

        if CostPerItem:
            CostPerItem = round(CostPerItem, PriceRounding)
        else:
            CostPerItem = 0

        return str(CostPerItem)

    def get_DiscountPerc(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        DiscountPerc = purchase_details.DiscountPerc

        if DiscountPerc:
            DiscountPerc = round(DiscountPerc, PriceRounding)
        else:
            DiscountPerc = 0

        return str(DiscountPerc)

    def get_DiscountAmount(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        DiscountAmount = purchase_details.DiscountAmount

        if DiscountAmount:
            DiscountAmount = round(DiscountAmount, PriceRounding)
        else:
            DiscountAmount = 0

        return str(DiscountAmount)

    def get_AddlDiscPerc(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        AddlDiscPerc = purchase_details.AddlDiscPerc

        if AddlDiscPerc:
            AddlDiscPerc = round(AddlDiscPerc, PriceRounding)
        else:
            AddlDiscPerc = 0

        return str(AddlDiscPerc)

    def get_AddlDiscAmt(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        AddlDiscAmt = purchase_details.AddlDiscAmt

        if AddlDiscAmt:
            AddlDiscAmt = round(AddlDiscAmt, PriceRounding)
        else:
            AddlDiscAmt = 0

        return str(AddlDiscAmt)

    def get_GrossAmount(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        GrossAmount = purchase_details.GrossAmount

        GrossAmount = round(GrossAmount, PriceRounding)

        return str(GrossAmount)

    def get_TaxableAmount(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        TaxableAmount = purchase_details.TaxableAmount

        if TaxableAmount:
            TaxableAmount = round(TaxableAmount, PriceRounding)
        else:
            TaxableAmount = 0

        return str(TaxableAmount)

    def get_VATPerc(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        VATPerc = purchase_details.VATPerc

        if VATPerc:

            VATPerc = round(VATPerc, PriceRounding)
        else:
            VATPerc = 0

        return str(VATPerc)

    def get_VATAmount(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        VATAmount = purchase_details.VATAmount

        if VATAmount:
            VATAmount = round(VATAmount, PriceRounding)
        else:
            VATAmount = 0

        return str(VATAmount)

    def get_SGSTPerc(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        SGSTPerc = purchase_details.SGSTPerc

        if SGSTPerc:
            SGSTPerc = round(SGSTPerc, PriceRounding)
        else:
            SGSTPerc = 0

        return str(SGSTPerc)

    def get_SGSTAmount(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        SGSTAmount = purchase_details.SGSTAmount

        if SGSTAmount:
            SGSTAmount = round(SGSTAmount, PriceRounding)
        else:
            SGSTAmount = 0

        return str(SGSTAmount)

    def get_CGSTPerc(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        CGSTPerc = purchase_details.CGSTPerc

        if CGSTPerc:
            CGSTPerc = round(CGSTPerc, PriceRounding)
        else:
            CGSTPerc = 0

        return str(CGSTPerc)

    def get_CGSTAmount(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        CGSTAmount = purchase_details.CGSTAmount

        if CGSTAmount:
            CGSTAmount = round(CGSTAmount, PriceRounding)
        else:
            CGSTAmount = 0

        return str(CGSTAmount)

    def get_IGSTPerc(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        IGSTPerc = purchase_details.IGSTPerc

        if IGSTPerc:
            IGSTPerc = round(IGSTPerc, PriceRounding)
        else:
            IGSTPerc = 0

        return str(IGSTPerc)

    def get_IGSTAmount(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        IGSTAmount = purchase_details.IGSTAmount

        if IGSTAmount:
            IGSTAmount = round(IGSTAmount, PriceRounding)
        else:
            IGSTAmount = 0

        return str(IGSTAmount)

    def get_TAX1Perc(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX1Perc = purchase_details.TAX1Perc

        if TAX1Perc:
            TAX1Perc = round(TAX1Perc, PriceRounding)
        else:
            TAX1Perc = 0

        return str(TAX1Perc)

    def get_TAX2Perc(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX2Perc = purchase_details.TAX2Perc

        if TAX2Perc:
            TAX2Perc = round(TAX2Perc, PriceRounding)
        else:
            TAX2Perc = 0

        return str(TAX2Perc)

    def get_TAX3Perc(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX3Perc = purchase_details.TAX3Perc

        if TAX3Perc:
            TAX3Perc = round(TAX3Perc, PriceRounding)
        else:
            TAX3Perc = 0

        return str(TAX3Perc)

    def get_TAX1Amount(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX1Amount = purchase_details.TAX1Amount

        if TAX1Amount:
            TAX1Amount = round(TAX1Amount, PriceRounding)
        else:
            TAX1Amount = 0

        return str(TAX1Amount)

    def get_TAX2Amount(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX2Amount = purchase_details.TAX2Amount

        if TAX2Amount:
            TAX2Amount = round(TAX2Amount, PriceRounding)
        else:
            TAX2Amount = 0

        return str(TAX2Amount)

    def get_TAX3Amount(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX3Amount = purchase_details.TAX3Amount

        if TAX3Amount:
            TAX3Amount = round(TAX3Amount, PriceRounding)
        else:
            TAX3Amount = 0

        return str(TAX3Amount)

    def get_NetAmount(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        NetAmount = purchase_details.NetAmount

        if NetAmount:
            NetAmount = round(NetAmount, PriceRounding)
        else:
            NetAmount = 0

        return str(NetAmount)


class PurchasePrintSerializer(serializers.ModelSerializer):

    Details = serializers.SerializerMethodField()
    TotalGrossAmt = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    NetTotal = serializers.SerializerMethodField()
    AddlDiscPercent = serializers.SerializerMethodField()
    AddlDiscAmt = serializers.SerializerMethodField()
    AdditionalCost = serializers.SerializerMethodField()
    TotalDiscount = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    RoundOff = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    PurchaseAccountName = serializers.SerializerMethodField()
    WareHouseName = serializers.SerializerMethodField()
    DetailID = serializers.SerializerMethodField()
    VATAmount = serializers.SerializerMethodField()
    SGSTAmount = serializers.SerializerMethodField()
    CGSTAmount = serializers.SerializerMethodField()
    IGSTAmount = serializers.SerializerMethodField()
    TAX1Amount = serializers.SerializerMethodField()
    TAX2Amount = serializers.SerializerMethodField()
    TAX3Amount = serializers.SerializerMethodField()
    BillDiscPercent = serializers.SerializerMethodField()
    BillDiscAmt = serializers.SerializerMethodField()
    Balance = serializers.SerializerMethodField()
    TaxNo = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseMaster
        fields = ('PurchaseMasterID', 'BranchID', 'Action', 'VoucherNo', 'RefferenceBillNo', 'Date',
                  'VenderInvoiceDate', 'CreditPeriod', 'LedgerID', 'LedgerName', 'TaxNo',
                  'PriceCategoryID', 'EmployeeID', 'PurchaseAccount', 'PurchaseAccountName', 'CustomerName', 'Address1', 'Address2', 'Address3',
                  'Notes', 'FinacialYearID', 'TotalGrossAmt', 'TotalTax', 'NetTotal', 'AddlDiscPercent', 'AddlDiscAmt',
                  'AdditionalCost', 'TotalDiscount', 'GrandTotal', 'RoundOff', 'TransactionTypeID', 'WarehouseID', 'WareHouseName', 'IsActive', 'CreatedDate', 'CreatedUserID',
                  'TaxID', 'TaxType', 'VATAmount', 'SGSTAmount', 'CGSTAmount', 'IGSTAmount', 'TAX1Amount', 'TAX2Amount', 'TAX3Amount', 'BillDiscPercent', 'BillDiscAmt', 'Balance', 'DetailID', 'Details')

    def get_TaxNo(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        TaxNo = ""
        if Parties.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():
            party_instance = Parties.objects.filter(
                CompanyID=CompanyID, LedgerID=LedgerID).first()
            if party_instance.VATNumber:
                TaxNo = party_instance.VATNumber
            elif party_instance.GSTNumber:
                TaxNo = party_instance.GSTNumber
        return TaxNo

    def get_Details(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = int(self.context.get("PriceRounding"))
        QtyRounding = self.context.get("QtyRounding")
        purchase_details = PurchaseDetails.objects.filter(
            CompanyID=CompanyID, PurchaseMasterID=instances.PurchaseMasterID, BranchID=instances.BranchID)
        serialized = PurchaseDetailsPrintSerializer(purchase_details, many=True, context={"CompanyID": CompanyID,
                                                                                          "PriceRounding": PriceRounding, "QtyRounding": QtyRounding})

        return serialized.data

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

    def get_TotalGrossAmt(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalGrossAmt = instances.TotalGrossAmt

        TotalGrossAmt = round(TotalGrossAmt, PriceRounding)

        return str(TotalGrossAmt)

    def get_AddlDiscPercent(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        AddlDiscPercent = instances.AddlDiscPercent
        if not AddlDiscPercent == None:
            AddlDiscPercent = round(AddlDiscPercent, PriceRounding)
        else:
            AddlDiscPercent = 0

        return str(AddlDiscPercent)

    def get_AddlDiscAmt(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        AddlDiscAmt = instances.AddlDiscAmt
        if not AddlDiscAmt == None:
            AddlDiscAmt = round(AddlDiscAmt, PriceRounding)
        else:
            AddlDiscAmt = 0

        return str(AddlDiscAmt)

    def get_TotalDiscount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalDiscount = instances.TotalDiscount
        if not TotalDiscount == None:
            TotalDiscount = round(TotalDiscount, PriceRounding)
        else:
            TotalDiscount = 0

        return str(TotalDiscount)

    def get_TotalTax(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalTax = instances.TotalTax

        TotalTax = round(TotalTax, PriceRounding)

        return str(TotalTax)

    def get_NetTotal(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        NetTotal = instances.NetTotal

        NetTotal = round(NetTotal, PriceRounding)

        return str(NetTotal)

    def get_AdditionalCost(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        AdditionalCost = instances.AdditionalCost
        if not AdditionalCost == None:
            AdditionalCost = round(AdditionalCost, PriceRounding)
        else:
            AdditionalCost = 0

        return str(AdditionalCost)

    def get_GrandTotal(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        GrandTotal = instances.GrandTotal

        GrandTotal = round(GrandTotal, PriceRounding)

        return str(GrandTotal)

    def get_RoundOff(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        RoundOff = instances.RoundOff
        if not RoundOff == None:
            RoundOff = round(RoundOff, PriceRounding)
        else:
            RoundOff = 0

        return str(RoundOff)

    def get_VATAmount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        VATAmount = instances.VATAmount

        VATAmount = round(VATAmount, PriceRounding)

        return str(VATAmount)

    def get_SGSTAmount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        SGSTAmount = instances.SGSTAmount

        SGSTAmount = round(SGSTAmount, PriceRounding)

        return str(SGSTAmount)

    def get_CGSTAmount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        CGSTAmount = instances.CGSTAmount

        CGSTAmount = round(CGSTAmount, PriceRounding)

        return str(CGSTAmount)

    def get_IGSTAmount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        IGSTAmount = instances.IGSTAmount

        IGSTAmount = round(IGSTAmount, PriceRounding)

        return str(IGSTAmount)

    def get_TAX1Amount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX1Amount = instances.TAX1Amount

        TAX1Amount = round(TAX1Amount, PriceRounding)

        return str(TAX1Amount)

    def get_TAX2Amount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX2Amount = instances.TAX2Amount

        TAX2Amount = round(TAX2Amount, PriceRounding)

        return str(TAX2Amount)

    def get_TAX3Amount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX3Amount = instances.TAX3Amount

        TAX3Amount = round(TAX3Amount, PriceRounding)

        return str(TAX3Amount)

    def get_BillDiscPercent(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        BillDiscPercent = instances.BillDiscPercent

        BillDiscPercent = round(BillDiscPercent, PriceRounding)

        return str(BillDiscPercent)

    def get_BillDiscAmt(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        BillDiscAmt = instances.BillDiscAmt

        BillDiscAmt = round(BillDiscAmt, PriceRounding)

        return str(BillDiscAmt)

    def get_Balance(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        Balance = instances.Balance

        Balance = round(Balance, PriceRounding)

        return str(Balance)


class PurchaseDetailsPrintSerializer(serializers.ModelSerializer):

    Qty = serializers.SerializerMethodField()
    UnitPrice = serializers.SerializerMethodField()
    NetAmount = serializers.SerializerMethodField()
    ProductName = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseDetails
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
