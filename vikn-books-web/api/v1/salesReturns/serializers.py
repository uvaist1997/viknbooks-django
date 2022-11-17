from rest_framework import serializers
from brands.models import SalesReturnMaster, SalesReturnDetails, AccountLedger, Product, PriceList, Warehouse, Unit, TaxCategory, LedgerPosting


class SalesReturnMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalesReturnMaster
        fields = ('id','BranchID','Action','VoucherNo','VoucherDate','RefferenceBillNo',
            'RefferenceBillDate','CreditPeriod','LedgerID',
            'PriceCategoryID','EmployeeID','SalesAccount','DeliveryMasterID','OrderMasterID','CustomerName','Address1',
            'Address2','Address3','Notes','FinacialYearID','TotalGrossAmt','TotalTax','NetTotal',
            'AdditionalCost','GrandTotal','RoundOff','CashReceived','CashAmount','BankAmount','WarehouseID','TableID'
            ,'SeatNumber','NoOfGuests','INOUT','TokenNumber','IsActive','IsPosted','SalesType'
            ,'CreatedUserID','CreatedDate','TaxID','TaxType','VATAmount','SGSTAmount','CGSTAmount','IGSTAmount','TAX1Amount',
            'TAX2Amount','TAX3Amount','AddlDiscPercent','AddlDiscAmt','TotalDiscount','BillDiscPercent','BillDiscAmt')


class SalesReturnMasterRestSerializer(serializers.ModelSerializer):

    SalesReturnDetails = serializers.SerializerMethodField()
    DetailID = serializers.SerializerMethodField()
    TotalGrossAmt = serializers.SerializerMethodField()
    AddlDiscPercent = serializers.SerializerMethodField()
    AddlDiscAmt = serializers.SerializerMethodField()
    TotalDiscount = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    NetTotal = serializers.SerializerMethodField()
    AdditionalCost = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    RoundOff = serializers.SerializerMethodField()
    CashReceived = serializers.SerializerMethodField()
    CashAmount = serializers.SerializerMethodField()
    BankAmount = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    AccountName = serializers.SerializerMethodField()
    WareHouseName = serializers.SerializerMethodField()
    Types = serializers.SerializerMethodField()
    VATAmount = serializers.SerializerMethodField()
    SGSTAmount = serializers.SerializerMethodField()
    CGSTAmount = serializers.SerializerMethodField()
    IGSTAmount = serializers.SerializerMethodField()
    TAX1Amount = serializers.SerializerMethodField()
    TAX2Amount = serializers.SerializerMethodField()
    TAX3Amount = serializers.SerializerMethodField()
    BillDiscPercent = serializers.SerializerMethodField()
    BillDiscAmt = serializers.SerializerMethodField()
    is_customer = serializers.SerializerMethodField()
    

    class Meta:
        model = SalesReturnMaster
        fields = ('id','SalesReturnMasterID','BranchID','Action','VoucherNo','VoucherDate','RefferenceBillNo',
            'RefferenceBillDate','CreditPeriod','LedgerID','LedgerName','WareHouseName','AddlDiscPercent','AddlDiscAmt',
            'PriceCategoryID','EmployeeID','SalesAccount','AccountName','DeliveryMasterID','OrderMasterID','CustomerName','Address1',
            'Address2','Address3','is_customer','Notes','FinacialYearID','TotalGrossAmt','TotalTax','NetTotal',
            'AdditionalCost','GrandTotal','RoundOff','CashReceived','CashAmount','BankAmount','WarehouseID','TableID'
            ,'SeatNumber','NoOfGuests','INOUT','TokenNumber','IsActive','IsPosted','SalesType','Types'
            ,'CreatedUserID','CreatedDate','TaxID','TaxType','VATAmount','SGSTAmount','CGSTAmount','IGSTAmount','TAX1Amount',
            'TAX2Amount','TAX3Amount','TotalDiscount','BillDiscPercent','BillDiscAmt',
            'SalesReturnDetails','DetailID')



    def get_SalesReturnDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        salesReturn_details = SalesReturnDetails.objects.filter(CompanyID=CompanyID,SalesReturnMasterID=instances.SalesReturnMasterID,BranchID=instances.BranchID)
        serialized = SalesReturnDetailsRestSerializer(salesReturn_details,many=True,context = {"CompanyID": CompanyID,
        "PriceRounding" : PriceRounding })

        return serialized.data


    def get_DetailID(self, instances):

        return 0


    def get_is_customer(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        is_customer = False
        groups = [10,29]
        if AccountLedger.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID,AccountGroupUnder__in=groups).exists():
            is_customer = True

        return is_customer


    def get_WareHouseName(self, instances):
        CompanyID = self.context.get("CompanyID")

        WarehouseID = instances.WarehouseID
        BranchID = instances.BranchID

        wareHouse = Warehouse.objects.get(CompanyID=CompanyID,WarehouseID=WarehouseID,BranchID=BranchID)

        WareHouseName = wareHouse.WarehouseName

        return WareHouseName


    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        LedgerName = ""
        if AccountLedger.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID,BranchID=BranchID).exists():
            ledger = AccountLedger.objects.get(CompanyID=CompanyID,LedgerID=LedgerID,BranchID=BranchID)
            LedgerName = ledger.LedgerName

        return LedgerName



    def get_AccountName(self, instances):
        CompanyID = self.context.get("CompanyID")
        SalesAccount = instances.SalesAccount
        BranchID = instances.BranchID
        AccountName = ""
        if AccountLedger.objects.filter(CompanyID=CompanyID,LedgerID=SalesAccount,BranchID=BranchID).exists():
            AccountName = AccountLedger.objects.get(CompanyID=CompanyID,LedgerID=SalesAccount,BranchID=BranchID).LedgerName

        return AccountName


    def get_Types(self, instances):
        
        Types = instances.SalesType
        
        return Types


    def get_TotalGrossAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalGrossAmt = instances.TotalGrossAmt

        TotalGrossAmt = round(TotalGrossAmt,PriceRounding)

        return float(TotalGrossAmt)

    def get_AddlDiscPercent(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        AddlDiscPercent = instances.AddlDiscPercent

        AddlDiscPercent = round(AddlDiscPercent,PriceRounding)

        return float(AddlDiscPercent)


    def get_AddlDiscAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        AddlDiscAmt = instances.AddlDiscAmt

        AddlDiscAmt = round(AddlDiscAmt,PriceRounding)

        return float(AddlDiscAmt)


    def get_TotalDiscount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalDiscount = instances.TotalDiscount
        if not TotalDiscount == None:
            TotalDiscount = round(TotalDiscount,PriceRounding)
        else:
            TotalDiscount = 0

        return float(TotalDiscount)


    def get_TotalTax(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalTax = instances.TotalTax

        TotalTax = round(TotalTax,PriceRounding)

        return float(TotalTax)


    def get_NetTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        NetTotal = instances.NetTotal

        NetTotal = round(NetTotal,PriceRounding)

        return float(NetTotal)


    def get_AdditionalCost(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        AdditionalCost = instances.AdditionalCost

        AdditionalCost = round(AdditionalCost,PriceRounding)

        return float(AdditionalCost)


    def get_GrandTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        GrandTotal = instances.GrandTotal

        GrandTotal = round(GrandTotal,PriceRounding)

        return float(GrandTotal)


    def get_RoundOff(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        RoundOff = instances.RoundOff

        RoundOff = round(RoundOff,PriceRounding)

        return float(RoundOff)


    def get_CashReceived(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CashReceived = instances.CashReceived

        CashReceived = round(CashReceived,PriceRounding)

        return float(CashReceived)


    def get_CashAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CashAmount = instances.CashAmount

        CashAmount = round(CashAmount,PriceRounding)

        return float(CashAmount)


    def get_BankAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BankAmount = instances.BankAmount

        BankAmount = round(BankAmount,PriceRounding)

        return float(BankAmount)


    def get_VATAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        VATAmount = instances.VATAmount

        VATAmount = round(VATAmount,PriceRounding)

        return float(VATAmount)


    def get_SGSTAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        SGSTAmount = instances.SGSTAmount

        SGSTAmount = round(SGSTAmount,PriceRounding)

        return float(SGSTAmount)


    def get_CGSTAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CGSTAmount = instances.CGSTAmount

        CGSTAmount = round(CGSTAmount,PriceRounding)

        return float(CGSTAmount)


    def get_IGSTAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        IGSTAmount = instances.IGSTAmount

        IGSTAmount = round(IGSTAmount,PriceRounding)

        return float(IGSTAmount)


    def get_TAX1Amount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TAX1Amount = instances.TAX1Amount

        TAX1Amount = round(TAX1Amount,PriceRounding)

        return float(TAX1Amount)


    def get_TAX2Amount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TAX2Amount = instances.TAX2Amount

        TAX2Amount = round(TAX2Amount,PriceRounding)

        return float(TAX2Amount)


    def get_TAX3Amount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TAX3Amount = instances.TAX3Amount

        TAX3Amount = round(TAX3Amount,PriceRounding)

        return float(TAX3Amount)


    def get_BillDiscPercent(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscPercent = instances.BillDiscPercent

        BillDiscPercent = round(BillDiscPercent,PriceRounding)

        return float(BillDiscPercent)


    def get_BillDiscAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscAmt = instances.BillDiscAmt

        BillDiscAmt = round(BillDiscAmt,PriceRounding)

        return float(BillDiscAmt)



class SalesReturnDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalesReturnDetails
        fields = ('id','BranchID','Action','SalesReturnMasterID','DeliveryDetailsID','OrderDetailsID','ProductID',
            'Qty','FreeQty','UnitPrice',
            'RateWithTax','CostPerPrice','PriceListID','DiscountPerc','DiscountAmount',
            'GrossAmount','TaxableAmount','VATPerc','VATAmount','SGSTPerc','SGSTAmount','CGSTPerc',
            'CGSTAmount','IGSTPerc','IGSTAmount','NetAmount','Flavour','CreatedUserID',
            'AddlDiscPercent','AddlDiscAmt','TAX1Perc','TAX1Amount','TAX2Perc','TAX2Amount','TAX3Perc','TAX3Amount')


class SalesReturnDetailsRestSerializer(serializers.ModelSerializer):

    ProductName = serializers.SerializerMethodField()
    unq_id = serializers.SerializerMethodField()
    detailID = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()
    AddlDiscPerc = serializers.SerializerMethodField()
    AddlDiscAmt = serializers.SerializerMethodField()
    Qty = serializers.SerializerMethodField()
    FreeQty = serializers.SerializerMethodField()
    UnitPrice = serializers.SerializerMethodField()
    InclusivePrice = serializers.SerializerMethodField()
    RateWithTax = serializers.SerializerMethodField()
    CostPerPrice = serializers.SerializerMethodField()
    DiscountPerc = serializers.SerializerMethodField()
    DiscountAmount = serializers.SerializerMethodField()
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
    actualSalesPrice = serializers.SerializerMethodField()
    netAmountRounded = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    class Meta:
        model = SalesReturnDetails
        fields = ('id','unq_id','SalesReturnDetailsID','BranchID','Action','SalesReturnMasterID','DeliveryDetailsID','OrderDetailsID','ProductID',
            'ProductName','Qty','FreeQty','UnitPrice','InclusivePrice','detailID','TotalTax','UnitName',
            'RateWithTax','CostPerPrice','PriceListID','DiscountPerc','DiscountAmount',
            'GrossAmount','TaxableAmount','VATPerc','VATAmount','SGSTPerc','SGSTAmount','CGSTPerc',
            'CGSTAmount','IGSTPerc','IGSTAmount','NetAmount','Flavour','CreatedUserID','CreatedDate','UpdatedDate',
            'AddlDiscPerc','AddlDiscAmt','TAX1Perc','TAX1Amount','TAX2Perc','TAX2Amount','TAX3Perc','TAX3Amount',
            'is_VAT_inclusive','is_GST_inclusive','is_TAX1_inclusive','is_TAX2_inclusive','is_TAX3_inclusive',
            'unitPriceRounded','quantityRounded','actualSalesPrice','netAmountRounded')



    def get_ProductName(self, salesReturn_details):

        CompanyID = self.context.get("CompanyID")

        ProductID = salesReturn_details.ProductID
        BranchID = salesReturn_details.BranchID

        if Product.objects.filter(CompanyID=CompanyID,ProductID=ProductID,BranchID=BranchID).exists():

            product = Product.objects.get(CompanyID=CompanyID,ProductID=ProductID,BranchID=BranchID)

            ProductName = product.ProductName
        else:
            ProductName = ""

        return ProductName


    def get_id(self, instances):
        id = instances.id
        
        return str(id)


    def get_InclusivePrice(self, salesReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        # PriceRounding = 2
        InclusivePrice = salesReturn_details.InclusivePrice
        if InclusivePrice:
            InclusivePrice = round(InclusivePrice,PriceRounding)
        else:
            InclusivePrice = 0

        return float(InclusivePrice)


    def get_unitPriceRounded(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        UnitPrice = salesReturn_details.UnitPrice
        UnitPrice = round(UnitPrice,PriceRounding)
        return float(UnitPrice)


    def get_quantityRounded(self, salesReturn_details):
        Qty = salesReturn_details.Qty
        return float(Qty)


    def get_actualSalesPrice(self, salesReturn_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = salesReturn_details.PriceListID
        BranchID = salesReturn_details.BranchID
        ProductID = salesReturn_details.ProductID
        SalesPrice = ''
        if PriceList.objects.filter(ProductID=ProductID,CompanyID=CompanyID,PriceListID=PriceListID,BranchID=BranchID).exists():
            SalesPrice = PriceList.objects.get(ProductID=ProductID,CompanyID=CompanyID,PriceListID=PriceListID,BranchID=BranchID).SalesPrice
        return float(SalesPrice)


    def get_netAmountRounded(self, salesReturn_details):
        NetAmount = salesReturn_details.NetAmount
        return float(NetAmount)


    def get_is_VAT_inclusive(self, salesReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = salesReturn_details.BranchID
        ProductID = salesReturn_details.ProductID
        Inclusive = False
        VatID = Product.objects.get(CompanyID=CompanyID,ProductID=ProductID,BranchID=BranchID).VatID
        if VatID:
            Inclusive = TaxCategory.objects.get(CompanyID=CompanyID,TaxID=VatID,BranchID=BranchID).Inclusive
        return Inclusive


    def get_is_GST_inclusive(self, salesReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = salesReturn_details.BranchID
        ProductID = salesReturn_details.ProductID
        Inclusive = False
        GST = Product.objects.get(CompanyID=CompanyID,ProductID=ProductID,BranchID=BranchID).GST
        if GST:
            Inclusive = TaxCategory.objects.get(CompanyID=CompanyID,TaxID=GST,BranchID=BranchID).Inclusive
        return Inclusive


    def get_is_TAX1_inclusive(self, salesReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = salesReturn_details.BranchID
        ProductID = salesReturn_details.ProductID
        Inclusive = False
        Tax1 = Product.objects.get(CompanyID=CompanyID,ProductID=ProductID,BranchID=BranchID).Tax1
        if Tax1:
            Inclusive = TaxCategory.objects.get(CompanyID=CompanyID,TaxID=Tax1,BranchID=BranchID).Inclusive
        return Inclusive


    def get_is_TAX2_inclusive(self, salesReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = salesReturn_details.BranchID
        ProductID = salesReturn_details.ProductID
        Inclusive = False
        Tax2 = Product.objects.get(CompanyID=CompanyID,ProductID=ProductID,BranchID=BranchID).Tax2
        if Tax2:
            Inclusive = TaxCategory.objects.get(CompanyID=CompanyID,TaxID=Tax2,BranchID=BranchID).Inclusive
        return Inclusive


    def get_is_TAX3_inclusive(self, salesReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = salesReturn_details.BranchID
        ProductID = salesReturn_details.ProductID
        Inclusive = False
        Tax3 = Product.objects.get(CompanyID=CompanyID,ProductID=ProductID,BranchID=BranchID).Tax3
        if Tax3:
            Inclusive = TaxCategory.objects.get(CompanyID=CompanyID,TaxID=Tax3,BranchID=BranchID).Inclusive
        return Inclusive


    def get_AddlDiscPerc(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        AddlDiscPerc = salesReturn_details.AddlDiscPercent

        if AddlDiscPerc:
            AddlDiscPerc = round(AddlDiscPerc,PriceRounding)
        else:
            AddlDiscPerc = 0

        return float(AddlDiscPerc)


    def get_AddlDiscAmt(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        AddlDiscAmt = salesReturn_details.AddlDiscAmt

        if AddlDiscAmt:
            AddlDiscAmt = round(AddlDiscAmt,PriceRounding)
        else:
            AddlDiscAmt = 0

        return float(AddlDiscAmt)



    def get_UnitName(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        PriceListID = purchase_details.PriceListID
        BranchID = purchase_details.BranchID

        if PriceList.objects.filter(CompanyID=CompanyID,PriceListID=PriceListID,BranchID=BranchID).exists():
            UnitID = PriceList.objects.get(CompanyID=CompanyID,PriceListID=PriceListID,BranchID=BranchID).UnitID
            UnitName = Unit.objects.get(CompanyID=CompanyID,BranchID=BranchID,UnitID=UnitID).UnitName
        else:
            UnitName = ""

        return UnitName


    def get_TotalTax(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        TAX1Amount = purchase_details.TAX1Amount
        TAX2Amount = purchase_details.TAX2Amount
        TAX3Amount = purchase_details.TAX3Amount
        VATAmount = purchase_details.VATAmount
        IGSTAmount = purchase_details.IGSTAmount
        SGSTAmount = purchase_details.SGSTAmount
        IGSTAmount = purchase_details.IGSTAmount

        TotalTax = (TAX1Amount + TAX2Amount + TAX3Amount + VATAmount + IGSTAmount + SGSTAmount + IGSTAmount)

        return float(TotalTax)


    def get_unq_id(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        unq_id = purchase_details.id

        return str(unq_id)


    def get_detailID(self, purchase_details):

        detailID = 0
        return detailID


    def get_Qty(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        Qty = salesReturn_details.Qty

        if Qty:
            Qty = round(Qty,PriceRounding)
        else:
            Qty = 0

        return float(Qty)


    def get_FreeQty(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        FreeQty = salesReturn_details.FreeQty

        if FreeQty:
            FreeQty = round(FreeQty,PriceRounding)
        else:
            FreeQty = 0

        return float(FreeQty)


    def get_UnitPrice(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        UnitPrice = salesReturn_details.UnitPrice

        if UnitPrice:
            UnitPrice = round(UnitPrice,PriceRounding)
        else:
            UnitPrice = 0

        return float(UnitPrice)


    def get_RateWithTax(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        RateWithTax = salesReturn_details.RateWithTax

        if RateWithTax:
            RateWithTax = round(RateWithTax,PriceRounding)
        else:
            RateWithTax = 0

        return float(RateWithTax)


    def get_CostPerPrice(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        CostPerPrice = salesReturn_details.CostPerPrice

        if CostPerPrice:
            CostPerPrice = round(CostPerPrice,PriceRounding)
        else:
            CostPerPrice = 0

        return float(CostPerPrice)


    def get_DiscountPerc(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        DiscountPerc = salesReturn_details.DiscountPerc

        if DiscountPerc:
            DiscountPerc = round(DiscountPerc,PriceRounding)
        else:
            DiscountPerc = 0

        return float(DiscountPerc)


    def get_DiscountAmount(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        DiscountAmount = salesReturn_details.DiscountAmount

        if DiscountAmount:
            DiscountAmount = round(DiscountAmount,PriceRounding)
        else:
            DiscountAmount = 0

        return float(DiscountAmount)


    def get_GrossAmount(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        GrossAmount = salesReturn_details.GrossAmount

        if GrossAmount:
            GrossAmount = round(GrossAmount,PriceRounding)
        else:
            GrossAmount = 0

        return float(GrossAmount)


    def get_TaxableAmount(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        TaxableAmount = salesReturn_details.TaxableAmount

        if TaxableAmount:
            TaxableAmount = round(TaxableAmount,PriceRounding)
        else:
            TaxableAmount = 0

        return float(TaxableAmount)


    def get_VATAmount(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        VATAmount = salesReturn_details.VATAmount

        if VATAmount:
            VATAmount = round(VATAmount,PriceRounding)
        else:
            VATAmount = 0

        return float(VATAmount)


    def get_SGSTAmount(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        SGSTAmount = salesReturn_details.SGSTAmount

        if SGSTAmount:
            SGSTAmount = round(SGSTAmount,PriceRounding)
        else:
            SGSTAmount = 0

        return float(SGSTAmount)


    def get_CGSTAmount(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        CGSTAmount = salesReturn_details.CGSTAmount

        if CGSTAmount:
            CGSTAmount = round(CGSTAmount,PriceRounding)
        else:
            CGSTAmount = 0

        return float(CGSTAmount)


    def get_IGSTAmount(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        IGSTAmount = salesReturn_details.IGSTAmount

        if IGSTAmount:
            IGSTAmount = round(IGSTAmount,PriceRounding)
        else:
            IGSTAmount = 0

        return float(IGSTAmount)


    def get_TAX1Amount(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX1Amount = salesReturn_details.TAX1Amount

        if TAX1Amount:
            TAX1Amount = round(TAX1Amount,PriceRounding)
        else:
            TAX1Amount = 0

        return float(TAX1Amount)


    def get_TAX2Amount(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX2Amount = salesReturn_details.TAX2Amount

        if TAX2Amount:
            TAX2Amount = round(TAX2Amount,PriceRounding)
        else:
            TAX2Amount = 0

        return float(TAX2Amount)


    def get_TAX3Amount(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX3Amount = salesReturn_details.TAX3Amount

        if TAX3Amount:
            TAX3Amount = round(TAX3Amount,PriceRounding)
        else:
            TAX3Amount = 0

        return float(TAX3Amount)


    def get_NetAmount(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        NetAmount = salesReturn_details.NetAmount

        if NetAmount:
            NetAmount = round(NetAmount,PriceRounding)
        else:
            NetAmount = 0

        return float(NetAmount)



class SalesReturnMasterReportSerializer(serializers.ModelSerializer):

    SalesReturnDetails = serializers.SerializerMethodField()
    DetailID = serializers.SerializerMethodField()
    TotalGrossAmt = serializers.SerializerMethodField()
    AddlDiscPercent = serializers.SerializerMethodField()
    AddlDiscAmt = serializers.SerializerMethodField()
    TotalDiscount = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    NetTotal = serializers.SerializerMethodField()
    AdditionalCost = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    RoundOff = serializers.SerializerMethodField()
    CashReceived = serializers.SerializerMethodField()
    CashAmount = serializers.SerializerMethodField()
    BankAmount = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    AccountName = serializers.SerializerMethodField()
    WareHouseName = serializers.SerializerMethodField()
    Types = serializers.SerializerMethodField()
    VATAmount = serializers.SerializerMethodField()
    SGSTAmount = serializers.SerializerMethodField()
    CGSTAmount = serializers.SerializerMethodField()
    IGSTAmount = serializers.SerializerMethodField()
    TAX1Amount = serializers.SerializerMethodField()
    TAX2Amount = serializers.SerializerMethodField()
    TAX3Amount = serializers.SerializerMethodField()
    BillDiscPercent = serializers.SerializerMethodField()
    BillDiscAmt = serializers.SerializerMethodField()
    CashSalesReturn = serializers.SerializerMethodField()
    BankSalesReturn = serializers.SerializerMethodField()
    CreditSalesReturn = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    

    class Meta:
        model = SalesReturnMaster
        fields = ('id','SalesReturnMasterID','BranchID','Action','VoucherNo','VoucherDate','RefferenceBillNo',
            'RefferenceBillDate','CreditPeriod','LedgerID','LedgerName','WareHouseName','AddlDiscPercent','AddlDiscAmt',
            'PriceCategoryID','EmployeeID','SalesAccount','AccountName','DeliveryMasterID','OrderMasterID','CustomerName','Address1',
            'Address2','Address3','Notes','FinacialYearID','TotalGrossAmt','TotalTax','NetTotal',
            'AdditionalCost','GrandTotal','RoundOff','CashReceived','CashAmount','BankAmount','WarehouseID','TableID'
            ,'SeatNumber','NoOfGuests','INOUT','TokenNumber','IsActive','IsPosted','SalesType','Types'
            ,'CreatedUserID','CreatedDate','TaxID','TaxType','VATAmount','SGSTAmount','CGSTAmount','IGSTAmount','TAX1Amount',
            'TAX2Amount','TAX3Amount','TotalDiscount','BillDiscPercent','BillDiscAmt','CashSalesReturn','BankSalesReturn','CreditSalesReturn',
            'SalesReturnDetails','DetailID')



    def get_SalesReturnDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        salesReturn_details = SalesReturnDetails.objects.filter(CompanyID=CompanyID,SalesReturnMasterID=instances.SalesReturnMasterID,BranchID=instances.BranchID)
        serialized = SalesReturnDetailsRestSerializer(salesReturn_details,many=True,context = {"CompanyID": CompanyID,
        "PriceRounding" : PriceRounding })

        return serialized.data

    def get_id(self, instances):
        id = instances.id
        
        return str(id)


    def get_CashSalesReturn(self, instances):
        CompanyID = self.context.get("CompanyID")
        FromDate = self.context.get("FromDate")
        ToDate = self.context.get("ToDate")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        TotalDebit = 0
        TotalCredit = 0
        if AccountLedger.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID,BranchID=BranchID,AccountGroupUnder=9).exists():
            if LedgerPosting.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID,Date__gte=FromDate,Date__lte=ToDate,VoucherType="SR").exists():
                ledger_ins = LedgerPosting.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID,Date__gte=FromDate,Date__lte=ToDate,VoucherType="SR")
                for i in ledger_ins:
                    TotalDebit += float(i.Debit)
                    TotalCredit += float(i.Credit)

        CashSales = float(TotalDebit) - float(TotalCredit)
        return CashSales


    def get_BankSalesReturn(self, instances):
        CompanyID = self.context.get("CompanyID")
        FromDate = self.context.get("FromDate")
        ToDate = self.context.get("ToDate")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        TotalDebit = 0
        TotalCredit = 0
        if AccountLedger.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID,BranchID=BranchID,AccountGroupUnder=8).exists():
            if LedgerPosting.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID,Date__gte=FromDate,Date__lte=ToDate,VoucherType="SR").exists():
                ledger_ins = LedgerPosting.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID,Date__gte=FromDate,Date__lte=ToDate,VoucherType="SR")
                for i in ledger_ins:
                    TotalDebit += float(i.Debit)
                    TotalCredit += float(i.Credit)

        BankSales = float(TotalDebit) - float(TotalCredit)
        return BankSales


    def get_CreditSalesReturn(self, instances):
        CompanyID = self.context.get("CompanyID")
        FromDate = self.context.get("FromDate")
        ToDate = self.context.get("ToDate")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        TotalDebit = 0
        TotalCredit = 0
        if AccountLedger.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID,BranchID=BranchID,AccountGroupUnder__in=[10,29]).exists():
            if LedgerPosting.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID,Date__gte=FromDate,Date__lte=ToDate,VoucherType="SR").exists():
                ledger_ins = LedgerPosting.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID,Date__gte=FromDate,Date__lte=ToDate,VoucherType="SR")
                for i in ledger_ins:
                    TotalDebit += float(i.Debit)
                    TotalCredit += float(i.Credit)

        CreditSales = float(TotalDebit) - float(TotalCredit)
        return CreditSales


    def get_DetailID(self, instances):

        return 0


    def get_WareHouseName(self, instances):
        CompanyID = self.context.get("CompanyID")

        WarehouseID = instances.WarehouseID
        BranchID = instances.BranchID

        wareHouse = Warehouse.objects.get(CompanyID=CompanyID,WarehouseID=WarehouseID,BranchID=BranchID)

        WareHouseName = wareHouse.WarehouseName

        return WareHouseName


    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        LedgerName = ""
        if AccountLedger.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID,BranchID=BranchID).exists():
            ledger = AccountLedger.objects.get(CompanyID=CompanyID,LedgerID=LedgerID,BranchID=BranchID)
            LedgerName = ledger.LedgerName

        return LedgerName



    def get_AccountName(self, instances):
        CompanyID = self.context.get("CompanyID")
        SalesAccount = instances.SalesAccount
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(CompanyID=CompanyID,LedgerID=SalesAccount,BranchID=BranchID)

        AccountName = ledger.LedgerName

        return AccountName


    def get_Types(self, instances):
        
        Types = instances.SalesType
        
        return Types


    def get_TotalGrossAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalGrossAmt = instances.TotalGrossAmt

        TotalGrossAmt = round(TotalGrossAmt,PriceRounding)

        return float(TotalGrossAmt)

    def get_AddlDiscPercent(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        AddlDiscPercent = instances.AddlDiscPercent

        AddlDiscPercent = round(AddlDiscPercent,PriceRounding)

        return float(AddlDiscPercent)


    def get_AddlDiscAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        AddlDiscAmt = instances.AddlDiscAmt

        AddlDiscAmt = round(AddlDiscAmt,PriceRounding)

        return float(AddlDiscAmt)


    def get_TotalDiscount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalDiscount = instances.TotalDiscount
        if not TotalDiscount == None:
            TotalDiscount = round(TotalDiscount,PriceRounding)
        else:
            TotalDiscount = 0

        return float(TotalDiscount)


    def get_TotalTax(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalTax = instances.TotalTax

        TotalTax = round(TotalTax,PriceRounding)

        return float(TotalTax)


    def get_NetTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        NetTotal = instances.NetTotal

        NetTotal = round(NetTotal,PriceRounding)

        return float(NetTotal)


    def get_AdditionalCost(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        AdditionalCost = instances.AdditionalCost

        AdditionalCost = round(AdditionalCost,PriceRounding)

        return float(AdditionalCost)


    def get_GrandTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        GrandTotal = instances.GrandTotal

        GrandTotal = round(GrandTotal,PriceRounding)

        return float(GrandTotal)


    def get_RoundOff(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        RoundOff = instances.RoundOff

        RoundOff = round(RoundOff,PriceRounding)

        return float(RoundOff)


    def get_CashReceived(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CashReceived = instances.CashReceived

        CashReceived = round(CashReceived,PriceRounding)

        return float(CashReceived)


    def get_CashAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CashAmount = instances.CashAmount

        CashAmount = round(CashAmount,PriceRounding)

        return float(CashAmount)


    def get_BankAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BankAmount = instances.BankAmount

        BankAmount = round(BankAmount,PriceRounding)

        return float(BankAmount)


    def get_VATAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        VATAmount = instances.VATAmount

        VATAmount = round(VATAmount,PriceRounding)

        return float(VATAmount)


    def get_SGSTAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        SGSTAmount = instances.SGSTAmount

        SGSTAmount = round(SGSTAmount,PriceRounding)

        return float(SGSTAmount)


    def get_CGSTAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CGSTAmount = instances.CGSTAmount

        CGSTAmount = round(CGSTAmount,PriceRounding)

        return float(CGSTAmount)


    def get_IGSTAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        IGSTAmount = instances.IGSTAmount

        IGSTAmount = round(IGSTAmount,PriceRounding)

        return float(IGSTAmount)


    def get_TAX1Amount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TAX1Amount = instances.TAX1Amount

        TAX1Amount = round(TAX1Amount,PriceRounding)

        return float(TAX1Amount)


    def get_TAX2Amount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TAX2Amount = instances.TAX2Amount

        TAX2Amount = round(TAX2Amount,PriceRounding)

        return float(TAX2Amount)


    def get_TAX3Amount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TAX3Amount = instances.TAX3Amount

        TAX3Amount = round(TAX3Amount,PriceRounding)

        return float(TAX3Amount)


    def get_BillDiscPercent(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscPercent = instances.BillDiscPercent

        BillDiscPercent = round(BillDiscPercent,PriceRounding)

        return float(BillDiscPercent)


    def get_BillDiscAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscAmt = instances.BillDiscAmt

        BillDiscAmt = round(BillDiscAmt,PriceRounding)

        return float(BillDiscAmt)



class SalesRetrnDetailsReportSerializer(serializers.ModelSerializer):

    MasterID = serializers.SerializerMethodField()
    DetailsID = serializers.SerializerMethodField()
    ProductName = serializers.SerializerMethodField()
    

    class Meta:
        model = SalesReturnDetails
        fields = ('id','DetailsID','BranchID','Action','MasterID','DeliveryDetailsID','OrderDetailsID','ProductID',
            'ProductName','Qty','FreeQty','UnitPrice',
            'RateWithTax','CostPerPrice','PriceListID','DiscountPerc','DiscountAmount',
            'GrossAmount','TaxableAmount','VATPerc','VATAmount','SGSTPerc','SGSTAmount','CGSTPerc',
            'CGSTAmount','IGSTPerc','IGSTAmount','NetAmount','Flavour','CreatedUserID','CreatedDate','UpdatedDate',
            'AddlDiscPercent','AddlDiscAmt','TAX1Perc','TAX1Amount','TAX2Perc','TAX2Amount','TAX3Perc','TAX3Amount')



    def get_MasterID(self, salesReturn_details):
        
        MasterID = salesReturn_details.SalesReturnMasterID
        
        return MasterID

    def get_ProductName(self, salesReturn_details):

        CompanyID = self.context.get("CompanyID")

        ProductID = salesReturn_details.ProductID
        BranchID = salesReturn_details.BranchID

        product = Product.objects.get(CompanyID=CompanyID,ProductID=ProductID,BranchID=BranchID)

        if product:
            ProductName = product.ProductName
        else:
            ProductName = ""

        return ProductName


    def get_DetailsID(self, salesReturn_details):
        
        DetailsID = salesReturn_details.SalesReturnDetailsID
        
        return Detail


class SalesReturnMasterPrintSerializer(serializers.ModelSerializer):

    Details = serializers.SerializerMethodField()
    DetailID = serializers.SerializerMethodField()
    TotalGrossAmt = serializers.SerializerMethodField()
    AddlDiscPercent = serializers.SerializerMethodField()
    AddlDiscAmt = serializers.SerializerMethodField()
    TotalDiscount = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    NetTotal = serializers.SerializerMethodField()
    AdditionalCost = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    RoundOff = serializers.SerializerMethodField()
    CashReceived = serializers.SerializerMethodField()
    CashAmount = serializers.SerializerMethodField()
    BankAmount = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    AccountName = serializers.SerializerMethodField()
    WareHouseName = serializers.SerializerMethodField()
    Types = serializers.SerializerMethodField()
    VATAmount = serializers.SerializerMethodField()
    SGSTAmount = serializers.SerializerMethodField()
    CGSTAmount = serializers.SerializerMethodField()
    IGSTAmount = serializers.SerializerMethodField()
    TAX1Amount = serializers.SerializerMethodField()
    TAX2Amount = serializers.SerializerMethodField()
    TAX3Amount = serializers.SerializerMethodField()
    BillDiscPercent = serializers.SerializerMethodField()
    BillDiscAmt = serializers.SerializerMethodField()
    

    class Meta:
        model = SalesReturnMaster
        fields = ('SalesReturnMasterID','BranchID','Action','VoucherNo','VoucherDate','RefferenceBillNo',
            'RefferenceBillDate','CreditPeriod','LedgerID','LedgerName','WareHouseName','AddlDiscPercent','AddlDiscAmt',
            'PriceCategoryID','EmployeeID','SalesAccount','AccountName','DeliveryMasterID','OrderMasterID','CustomerName','Address1',
            'Address2','Address3','Notes','FinacialYearID','TotalGrossAmt','TotalTax','NetTotal',
            'AdditionalCost','GrandTotal','RoundOff','CashReceived','CashAmount','BankAmount','WarehouseID','TableID'
            ,'SeatNumber','NoOfGuests','INOUT','TokenNumber','IsActive','IsPosted','SalesType','Types'
            ,'CreatedUserID','CreatedDate','TaxID','TaxType','VATAmount','SGSTAmount','CGSTAmount','IGSTAmount','TAX1Amount',
            'TAX2Amount','TAX3Amount','TotalDiscount','BillDiscPercent','BillDiscAmt'
            ,'DetailID','Details')



    def get_Details(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        salesReturn_details = SalesReturnDetails.objects.filter(CompanyID=CompanyID,SalesReturnMasterID=instances.SalesReturnMasterID,BranchID=instances.BranchID)
        serialized = SalesReturnPrintSerializer(salesReturn_details,many=True,context = {"CompanyID": CompanyID,
        "PriceRounding" : PriceRounding })

        return serialized.data


    def get_DetailID(self, instances):

        return 0


    def get_WareHouseName(self, instances):
        CompanyID = self.context.get("CompanyID")

        WarehouseID = instances.WarehouseID
        BranchID = instances.BranchID

        wareHouse = Warehouse.objects.get(CompanyID=CompanyID,WarehouseID=WarehouseID,BranchID=BranchID)

        WareHouseName = wareHouse.WarehouseName

        return WareHouseName


    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        LedgerName = ""
        if AccountLedger.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID,BranchID=BranchID).exists():
            ledger = AccountLedger.objects.get(CompanyID=CompanyID,LedgerID=LedgerID,BranchID=BranchID)
            LedgerName = ledger.LedgerName

        return LedgerName



    def get_AccountName(self, instances):
        CompanyID = self.context.get("CompanyID")
        SalesAccount = instances.SalesAccount
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(CompanyID=CompanyID,LedgerID=SalesAccount,BranchID=BranchID)

        AccountName = ledger.LedgerName

        return AccountName


    def get_Types(self, instances):
        
        Types = instances.SalesType
        
        return Types


    def get_TotalGrossAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalGrossAmt = instances.TotalGrossAmt

        TotalGrossAmt = round(TotalGrossAmt,PriceRounding)

        return float(TotalGrossAmt)

    def get_AddlDiscPercent(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        AddlDiscPercent = instances.AddlDiscPercent

        AddlDiscPercent = round(AddlDiscPercent,PriceRounding)

        return float(AddlDiscPercent)


    def get_AddlDiscAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        AddlDiscAmt = instances.AddlDiscAmt

        AddlDiscAmt = round(AddlDiscAmt,PriceRounding)

        return float(AddlDiscAmt)


    def get_TotalDiscount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalDiscount = instances.TotalDiscount
        if not TotalDiscount == None:
            TotalDiscount = round(TotalDiscount,PriceRounding)
        else:
            TotalDiscount = 0

        return float(TotalDiscount)


    def get_TotalTax(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalTax = instances.TotalTax

        TotalTax = round(TotalTax,PriceRounding)

        return float(TotalTax)


    def get_NetTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        NetTotal = instances.NetTotal

        NetTotal = round(NetTotal,PriceRounding)

        return float(NetTotal)


    def get_AdditionalCost(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        AdditionalCost = instances.AdditionalCost

        AdditionalCost = round(AdditionalCost,PriceRounding)

        return float(AdditionalCost)


    def get_GrandTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        GrandTotal = instances.GrandTotal

        GrandTotal = round(GrandTotal,PriceRounding)

        return float(GrandTotal)


    def get_RoundOff(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        RoundOff = instances.RoundOff

        RoundOff = round(RoundOff,PriceRounding)

        return float(RoundOff)


    def get_CashReceived(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CashReceived = instances.CashReceived

        CashReceived = round(CashReceived,PriceRounding)

        return float(CashReceived)


    def get_CashAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CashAmount = instances.CashAmount

        CashAmount = round(CashAmount,PriceRounding)

        return float(CashAmount)


    def get_BankAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BankAmount = instances.BankAmount

        BankAmount = round(BankAmount,PriceRounding)

        return float(BankAmount)


    def get_VATAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        VATAmount = instances.VATAmount

        VATAmount = round(VATAmount,PriceRounding)

        return float(VATAmount)


    def get_SGSTAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        SGSTAmount = instances.SGSTAmount

        SGSTAmount = round(SGSTAmount,PriceRounding)

        return float(SGSTAmount)


    def get_CGSTAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CGSTAmount = instances.CGSTAmount

        CGSTAmount = round(CGSTAmount,PriceRounding)

        return float(CGSTAmount)


    def get_IGSTAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        IGSTAmount = instances.IGSTAmount

        IGSTAmount = round(IGSTAmount,PriceRounding)

        return float(IGSTAmount)


    def get_TAX1Amount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TAX1Amount = instances.TAX1Amount

        TAX1Amount = round(TAX1Amount,PriceRounding)

        return float(TAX1Amount)


    def get_TAX2Amount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TAX2Amount = instances.TAX2Amount

        TAX2Amount = round(TAX2Amount,PriceRounding)

        return float(TAX2Amount)


    def get_TAX3Amount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TAX3Amount = instances.TAX3Amount

        TAX3Amount = round(TAX3Amount,PriceRounding)

        return float(TAX3Amount)


    def get_BillDiscPercent(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscPercent = instances.BillDiscPercent

        BillDiscPercent = round(BillDiscPercent,PriceRounding)

        return float(BillDiscPercent)


    def get_BillDiscAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscAmt = instances.BillDiscAmt

        BillDiscAmt = round(BillDiscAmt,PriceRounding)

        return float(BillDiscAmt)

class SalesReturnPrintSerializer(serializers.ModelSerializer):

    ProductName = serializers.SerializerMethodField()
    Qty = serializers.SerializerMethodField()
    UnitPrice = serializers.SerializerMethodField()
    NetAmount = serializers.SerializerMethodField()

    class Meta:
        model = SalesReturnDetails
        fields = ('ProductName','Qty','UnitPrice','NetAmount')



    def get_ProductName(self, salesReturn_details):

        CompanyID = self.context.get("CompanyID")

        ProductID = salesReturn_details.ProductID
        BranchID = salesReturn_details.BranchID

        if Product.objects.filter(CompanyID=CompanyID,ProductID=ProductID,BranchID=BranchID).exists():

            product = Product.objects.get(CompanyID=CompanyID,ProductID=ProductID,BranchID=BranchID)

            ProductName = product.ProductName
        else:
            ProductName = ""

        return ProductName




    def get_Qty(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        Qty = salesReturn_details.Qty

        if Qty:
            Qty = round(Qty,PriceRounding)
        else:
            Qty = 0

        return float(Qty)


    def get_UnitPrice(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        UnitPrice = salesReturn_details.UnitPrice

        if UnitPrice:
            UnitPrice = round(UnitPrice,PriceRounding)
        else:
            UnitPrice = 0

        return float(UnitPrice)


    def get_NetAmount(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        NetAmount = salesReturn_details.NetAmount

        if NetAmount:
            NetAmount = round(NetAmount,PriceRounding)
        else:
            NetAmount = 0

        return float(NetAmount)
