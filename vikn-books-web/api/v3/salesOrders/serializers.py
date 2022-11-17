from rest_framework import serializers
from brands.models import SalesOrderMaster, SalesOrderDetails, AccountLedger, Product


class SalesOrderMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalesOrderMaster
        fields = ('id','BranchID','Action','VoucherNo','Date',
            'LedgerID',
            'PriceCategoryID','CustomerName','Address1',
            'Address2','Notes','FinacialYearID','TotalTax','NetTotal',
            'BillDiscount','GrandTotal','RoundOff',
            'IsActive','IsInvoiced','CreatedUserID')


class SalesOrderMasterRestSerializer(serializers.ModelSerializer):

    SalesOrderDetails = serializers.SerializerMethodField()
    # DetailID = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    TotalGrossAmt = serializers.SerializerMethodField()
    NetTotal = serializers.SerializerMethodField()

    class Meta:
        model = SalesOrderMaster
        fields = ('id','SalesOrderMasterID','BranchID','Action','VoucherNo','Date','LedgerID','LedgerName',
        	'PriceCategoryID','CustomerName','Address1','TotalGrossAmt','TaxID','TaxType',
            'Address2','Notes','FinacialYearID','TotalTax','NetTotal',
            'BillDiscAmt','BillDiscPercent','GrandTotal','RoundOff','DeliveryDate'
            ,'IsActive','IsInvoiced','CreatedDate','UpdatedDate','CreatedUserID','SalesOrderDetails')


    def get_SalesOrderDetails(self, instances):
        CompanyID = self.context.get("CompanyID")

        salesOrder_details = SalesOrderDetails.objects.filter(CompanyID=CompanyID,SalesOrderMasterID=instances.SalesOrderMasterID,BranchID=instances.BranchID)
        serialized = SalesOrderDetailsRestSerializer(salesOrder_details,many=True,context={"CompanyID" : CompanyID})

        return serialized.data


    def get_TotalTax(self, instances):
        TotalTax = float(instances.TotalTax)
        TotalTax = round(TotalTax,2)
        return TotalTax


    def get_GrandTotal(self, instances):
        GrandTotal = float(instances.GrandTotal)
        GrandTotal = round(GrandTotal,2)
        return GrandTotal

    def get_TotalGrossAmt(self, instances):
        GrandTotal = float(instances.GrandTotal)
        GrandTotal = round(GrandTotal,2)
        return GrandTotal

    def get_NetTotal(self, instances):
        NetTotal = float(instances.NetTotal)
        NetTotal = round(NetTotal,2)
        return NetTotal


    def get_DetailID(self, instances):

        return ""


    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(CompanyID=CompanyID,LedgerID=LedgerID,BranchID=BranchID)

        LedgerName = ledger.LedgerName

        return LedgerName



class SalesOrderDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalesOrderDetails
        fields = ('id','BranchID','Action','SalesOrderMasterID','ProductID',
            'Qty','FreeQty','UnitPrice',
            'RateWithTax','PriceListID','DiscountPerc','DiscountAmount',
            'GrossAmount','TaxableAmount','VATPerc','VATAmount','SGSTPerc','SGSTAmount','CGSTPerc',
            'CGSTAmount','IGSTPerc','IGSTAmount','NetAmount','CreatedUserID')


class SalesOrderDetailsRestSerializer(serializers.ModelSerializer):

    Qty = serializers.SerializerMethodField()
    FreeQty = serializers.SerializerMethodField()
    UnitPrice = serializers.SerializerMethodField()
    InclusivePrice = serializers.SerializerMethodField()
    TaxableAmount = serializers.SerializerMethodField()
    DiscountPerc = serializers.SerializerMethodField()
    DiscountAmount = serializers.SerializerMethodField()
    GrossAmount = serializers.SerializerMethodField()
    VATAmount = serializers.SerializerMethodField()
    SGSTAmount = serializers.SerializerMethodField()
    CGSTAmount = serializers.SerializerMethodField()
    IGSTAmount = serializers.SerializerMethodField()
    NetAmount = serializers.SerializerMethodField()
    ProductName = serializers.SerializerMethodField()
    unq_id = serializers.SerializerMethodField()
    detailID = serializers.SerializerMethodField()



    class Meta:
        model = SalesOrderDetails
        fields = ('id','unq_id','SalesOrderDetailsID','BranchID','Action','SalesOrderMasterID','ProductID',
            'Qty','FreeQty','UnitPrice','BatchCode','InclusivePrice','ProductName','TAX1Perc','TAX1Amount','TAX2Perc','TAX2Amount',
            'RateWithTax','PriceListID','DiscountPerc','DiscountAmount','detailID','TAX3Perc','TAX3Amount','KFCAmount',
            'GrossAmount','TaxableAmount','VATPerc','VATAmount','SGSTPerc','SGSTAmount','CGSTPerc',
            'CGSTAmount','IGSTPerc','IGSTAmount','NetAmount','CreatedDate','UpdatedDate','CreatedUserID')

    def get_Qty(self, instances):
        Qty = float(instances.Qty)
        Qty = round(Qty,2)
        return Qty


    def get_ProductName(self, instances):

        CompanyID = self.context.get("CompanyID")

        ProductID = instances.ProductID
        BranchID = instances.BranchID

        product = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)

        ProductName = product.ProductName

        return ProductName


    def get_detailID(self, instances):

        detailID = 0

        return detailID


    def get_unq_id(self, instances):
        CompanyID = self.context.get("CompanyID")
        unq_id = instances.id
        return str(unq_id)


    def get_FreeQty(self, instances):
        FreeQty = float(instances.FreeQty)
        FreeQty = round(FreeQty,2)
        return FreeQty

    def get_UnitPrice(self, instances):
        UnitPrice = float(instances.UnitPrice)
        UnitPrice = round(UnitPrice,2)
        return UnitPrice


    def get_InclusivePrice(self, instances):
        InclusivePrice = float(instances.InclusivePrice)
        InclusivePrice = round(InclusivePrice,2)
        return InclusivePrice

    def get_TaxableAmount(self, instances):
        TaxableAmount = float(instances.TaxableAmount)
        TaxableAmount = round(TaxableAmount,2)
        return TaxableAmount


    def get_DiscountPerc(self, instances):
        DiscountPerc = float(instances.DiscountPerc)
        DiscountPerc = round(DiscountPerc,2)
        return DiscountPerc


    def get_DiscountAmount(self, instances):
        DiscountAmount = float(instances.DiscountAmount)
        DiscountAmount = round(DiscountAmount,2)
        return DiscountAmount


    def get_GrossAmount(self, instances):
        GrossAmount = float(instances.GrossAmount)
        GrossAmount = round(GrossAmount,2)
        return GrossAmount


    def get_VATAmount(self, instances):
        VATAmount = float(instances.VATAmount)
        VATAmount = round(VATAmount,2)
        return VATAmount


    def get_SGSTAmount(self, instances):
        SGSTAmount = float(instances.SGSTAmount)
        SGSTAmount = round(SGSTAmount,2)
        return SGSTAmount


    def get_CGSTAmount(self, instances):
        CGSTAmount = float(instances.CGSTAmount)
        CGSTAmount = round(CGSTAmount,2)
        return CGSTAmount


    def get_IGSTAmount(self, instances):
        IGSTAmount = float(instances.IGSTAmount)
        IGSTAmount = round(IGSTAmount,2)
        return IGSTAmount


    def get_NetAmount(self, instances):
        NetAmount = float(instances.NetAmount)
        NetAmount = round(NetAmount,2)
        return NetAmount