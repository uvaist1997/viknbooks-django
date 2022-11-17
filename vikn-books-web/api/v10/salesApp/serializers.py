from sre_parse import State
from rest_framework import serializers
from api.v10.workOrder.serializers import Batch_ListSalesSerializer, Batch_ListSerializer
from brands import models as table
from api.v10.priceLists.serializers import PriceListRestSerializer
from api.v10.companySettings.serializers import CompanySettingsRestSerializer
from api.v10.sales.serializers import GST_finalList_fun, QRCodeSerializer, SalesDetailsRestSerializer, SerialNumberSerializer, ShippingAddressListSerializer, get_treatment_name
from main.functions import converted_float, get_BalanceFromLedgerPost, get_GeneralSettings, get_LedgerBalance, get_ProductStock
from django.db.models import F, Q, Sum

class PriceListSerializer(serializers.ModelSerializer):
   
    UnitName = serializers.SerializerMethodField()

    class Meta:
        model = table.PriceList
        fields = ('id','PriceListID','BranchID','MRP','ProductID','UnitID','UnitName','SalesPrice','PurchasePrice','MultiFactor','Barcode','AutoBarcode')


    def get_UnitName(self, instances):
        CompanyID = self.context.get("CompanyID")

        UnitID = instances.UnitID
        BranchID = instances.BranchID
        UnitName = ""
        if table.Unit.objects.filter(CompanyID=CompanyID,UnitID=UnitID,BranchID=BranchID).exists():
            UnitName = table.Unit.objects.get(CompanyID=CompanyID,UnitID=UnitID,BranchID=BranchID).UnitName

        return UnitName



class POS_ProductList_Serializer(serializers.ModelSerializer):
    UnitList = serializers.SerializerMethodField()
    GST_Tax = serializers.SerializerMethodField()
    VAT_Tax = serializers.SerializerMethodField()

    class Meta:
        model = table.Product
        fields = ('id','ProductID','ProductName','ProductCode','UnitList','GST_Tax','VAT_Tax')

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


class SalesListSerializer(serializers.ModelSerializer):
    LedgerName = serializers.SerializerMethodField()

    class Meta:
        model = table.SalesMaster
        fields = ('id','VoucherNo','GrandTotal','Date','LedgerName')

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        LedgerName = ""
        if table.AccountLedger.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID).exists():
            LedgerName = table.AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID).LedgerName
        return LedgerName
    
    
class SalesReturnListSerializer(serializers.ModelSerializer):
    LedgerName = serializers.SerializerMethodField()

    class Meta:
        model = table.SalesReturnMaster
        fields = ('id', 'VoucherNo', 'GrandTotal', 'VoucherDate', 'LedgerName')

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        LedgerName = ""
        if table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():
            LedgerName = table.AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID).LedgerName
        return LedgerName
    

class SalesOrderListSerializer(serializers.ModelSerializer):
    LedgerName = serializers.SerializerMethodField()

    class Meta:
        model = table.SalesOrderMaster
        fields = ('id', 'VoucherNo', 'GrandTotal', 'Date', 'LedgerName')

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        LedgerName = ""
        if table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():
            LedgerName = table.AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID).LedgerName
        return LedgerName
    
    
class PaymentListSerializer(serializers.ModelSerializer):
    VoucherNo = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    MasterLedgerName = serializers.SerializerMethodField()
    VoucherType = serializers.SerializerMethodField()
    TotalAmount = serializers.SerializerMethodField()
    Date = serializers.SerializerMethodField()
    MasterLedgerID = serializers.SerializerMethodField()
    Notes = serializers.SerializerMethodField()
    MasterUid = serializers.SerializerMethodField()

    class Meta:
        model = table.PaymentDetails
        fields = ('id', 'VoucherNo', 'TotalAmount',
                  'VoucherType', 'LedgerName', 'Date', 'MasterLedgerID', 'LedgerID', 'Balance',
                  'Amount', 'Discount', 'NetAmount', 'Notes', 'MasterLedgerName', 'MasterUid')
        
    def get_MasterUid(self, instances):
        CompanyID = self.context.get("CompanyID")
        PaymentMasterID = instances.PaymentMasterID
        BranchID = instances.BranchID
        MasterUid = ""
        if table.PaymentMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID).exists():
            master_ins = table.PaymentMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID).first()
            MasterUid = master_ins.id
        return MasterUid
    
    def get_Notes(self, instances):
        CompanyID = self.context.get("CompanyID")
        PaymentMasterID = instances.PaymentMasterID
        BranchID = instances.BranchID
        Notes = ""
        if table.PaymentMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID).exists():
            master_ins = table.PaymentMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID).first()
            Notes = master_ins.Notes
        return Notes
    
    def get_MasterLedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        PaymentMasterID = instances.PaymentMasterID
        BranchID = instances.BranchID
        MasterLedgerName = ""
        if table.PaymentMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID).exists():
            master_ins = table.PaymentMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID).first()
            MasterLedgerID = master_ins.LedgerID
            if table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=MasterLedgerID).exists():
                MasterLedgerName = table.AccountLedger.objects.get(
                    CompanyID=CompanyID, LedgerID=MasterLedgerID).LedgerName
        return MasterLedgerName
    
    
    def get_MasterLedgerID(self, instances):
        CompanyID = self.context.get("CompanyID")
        PaymentMasterID = instances.PaymentMasterID
        BranchID = instances.BranchID
        MasterLedgerID = ""
        if table.PaymentMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID).exists():
            master_ins = table.PaymentMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID).first()
            MasterLedgerID = master_ins.LedgerID
        return MasterLedgerID

    
    def get_Date(self, instances):
        CompanyID = self.context.get("CompanyID")
        PaymentMasterID = instances.PaymentMasterID
        BranchID = instances.BranchID
        Date = ""
        if table.PaymentMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID).exists():
            master_ins = table.PaymentMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID).first()
            Date = master_ins.Date
        return Date
    
    def get_VoucherNo(self, instances):
        CompanyID = self.context.get("CompanyID")
        PaymentMasterID = instances.PaymentMasterID
        BranchID = instances.BranchID
        VoucherNo = ""
        if table.PaymentMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID).exists():
            master_ins = table.PaymentMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID).first()
            VoucherNo = master_ins.VoucherNo
        return VoucherNo
    
    def get_TotalAmount(self, instances):
        CompanyID = self.context.get("CompanyID")
        PaymentMasterID = instances.PaymentMasterID
        BranchID = instances.BranchID
        TotalAmount = ""
        if table.PaymentMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID).exists():
            master_ins = table.PaymentMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID).first()
            TotalAmount = master_ins.TotalAmount
        return TotalAmount
    
    def get_VoucherType(self, instances):
        CompanyID = self.context.get("CompanyID")
        PaymentMasterID = instances.PaymentMasterID
        BranchID = instances.BranchID
        VoucherType = ""
        if table.PaymentMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID).exists():
            master_ins = table.PaymentMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID).first()
            VoucherType = master_ins.VoucherType
        return VoucherType

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        LedgerName = ""
        if table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():
            LedgerName = table.AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID).LedgerName
        return LedgerName


class ReceiptListSerializer(serializers.ModelSerializer):
    VoucherNo = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    VoucherType = serializers.SerializerMethodField()
    TotalAmount = serializers.SerializerMethodField()
    Date = serializers.SerializerMethodField()
    MasterLedgerID = serializers.SerializerMethodField()
    Notes = serializers.SerializerMethodField()
    MasterLedgerName = serializers.SerializerMethodField()
    MasterUid = serializers.SerializerMethodField()

    class Meta:
        model = table.ReceiptDetails
        fields = ('id', 'VoucherNo', 'TotalAmount',
                'VoucherType', 'LedgerName', 'Date', 'MasterLedgerID', 'LedgerID', 'Balance',
                  'Amount', 'Discount', 'NetAmount', 'Notes', 'MasterLedgerName', 'MasterUid')

    def get_MasterUid(self, instances):
        CompanyID = self.context.get("CompanyID")
        ReceiptMasterID = instances.ReceiptMasterID
        BranchID = instances.BranchID
        MasterUid = ""
        if table.ReceiptMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ReceiptMasterID=ReceiptMasterID).exists():
            master_ins = table.ReceiptMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ReceiptMasterID=ReceiptMasterID).first()
            MasterUid = master_ins.id
        return MasterUid
    
    def get_Notes(self, instances):
        CompanyID = self.context.get("CompanyID")
        ReceiptMasterID = instances.ReceiptMasterID
        BranchID = instances.BranchID
        Notes = ""
        if table.ReceiptMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ReceiptMasterID=ReceiptMasterID).exists():
            master_ins = table.ReceiptMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ReceiptMasterID=ReceiptMasterID).first()
            Notes = master_ins.Notes
        return Notes

    def get_MasterLedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        ReceiptMasterID = instances.ReceiptMasterID
        BranchID = instances.BranchID
        MasterLedgerName = ""
        if table.ReceiptMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ReceiptMasterID=ReceiptMasterID).exists():
            master_ins = table.ReceiptMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ReceiptMasterID=ReceiptMasterID).first()
            MasterLedgerID = master_ins.LedgerID
            if table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=MasterLedgerID).exists():
                MasterLedgerName = table.AccountLedger.objects.get(
                    CompanyID=CompanyID, LedgerID=MasterLedgerID).LedgerName
        return MasterLedgerName

    def get_MasterLedgerID(self, instances):
        CompanyID = self.context.get("CompanyID")
        ReceiptMasterID = instances.ReceiptMasterID
        BranchID = instances.BranchID
        MasterLedgerID = ""
        if table.ReceiptMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ReceiptMasterID=ReceiptMasterID).exists():
            master_ins = table.ReceiptMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ReceiptMasterID=ReceiptMasterID).first()
            MasterLedgerID = master_ins.LedgerID
        return MasterLedgerID
    
    
    def get_Date(self, instances):
        CompanyID = self.context.get("CompanyID")
        ReceiptMasterID = instances.ReceiptMasterID
        BranchID = instances.BranchID
        Date = ""
        if table.ReceiptMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ReceiptMasterID=ReceiptMasterID).exists():
            master_ins = table.ReceiptMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ReceiptMasterID=ReceiptMasterID).first()
            Date = master_ins.Date
        return Date

    def get_VoucherNo(self, instances):
        CompanyID = self.context.get("CompanyID")
        ReceiptMasterID = instances.ReceiptMasterID
        BranchID = instances.BranchID
        VoucherNo = ""
        if table.ReceiptMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ReceiptMasterID=ReceiptMasterID).exists():
            master_ins = table.ReceiptMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ReceiptMasterID=ReceiptMasterID).first()
            VoucherNo = master_ins.VoucherNo
        return VoucherNo

    def get_TotalAmount(self, instances):
        CompanyID = self.context.get("CompanyID")
        ReceiptMasterID = instances.ReceiptMasterID
        BranchID = instances.BranchID
        TotalAmount = ""
        if table.ReceiptMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ReceiptMasterID=ReceiptMasterID).exists():
            master_ins = table.ReceiptMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ReceiptMasterID=ReceiptMasterID).first()
            TotalAmount = master_ins.TotalAmount
        return TotalAmount

    def get_VoucherType(self, instances):
        CompanyID = self.context.get("CompanyID")
        ReceiptMasterID = instances.ReceiptMasterID
        BranchID = instances.BranchID
        VoucherType = ""
        if table.ReceiptMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ReceiptMasterID=ReceiptMasterID).exists():
            master_ins = table.ReceiptMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ReceiptMasterID=ReceiptMasterID).first()
            VoucherType = master_ins.VoucherType
        return VoucherType

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        LedgerName = ""
        if table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():
            LedgerName = table.AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID).LedgerName
        return LedgerName


class ExpenseListSerializer(serializers.ModelSerializer):
    VoucherNo = serializers.SerializerMethodField()
    LedgerID = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    TotalAmount = serializers.SerializerMethodField()
    Date = serializers.SerializerMethodField()
    Supplier = serializers.SerializerMethodField()
    SupplierName = serializers.SerializerMethodField()
    GST_Treatment = serializers.SerializerMethodField()
    Notes = serializers.SerializerMethodField()
    TotalGrossAmt = serializers.SerializerMethodField()
    TotalTaxableAmount = serializers.SerializerMethodField()
    TotalDiscount = serializers.SerializerMethodField()
    TotalTaxAmount = serializers.SerializerMethodField()
    TotalNetAmount = serializers.SerializerMethodField()
    RoundOff = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    TaxInclusive = serializers.SerializerMethodField()
    TaxType = serializers.SerializerMethodField()
    TaxTypeID = serializers.SerializerMethodField()
    TotalVATAmount = serializers.SerializerMethodField()
    TotalIGSTAmount = serializers.SerializerMethodField()
    TotalSGSTAmount = serializers.SerializerMethodField()
    TotalCGSTAmount = serializers.SerializerMethodField()
    TaxNo = serializers.SerializerMethodField()
    TaxName = serializers.SerializerMethodField()
    MasterUid = serializers.SerializerMethodField()
    SupplierBalance = serializers.SerializerMethodField()
    PaymentMode = serializers.SerializerMethodField()
    PaymentID = serializers.SerializerMethodField()
    PaymentName = serializers.SerializerMethodField()
    MasterAmount = serializers.SerializerMethodField()

    class Meta:
        model = table.ExpenseDetails
        fields = ('id', 'VoucherNo', 'TotalAmount', 'TaxPerc','TaxAmount', 'NetTotal',
                  'VATPerc', 'VATAmount', 'IGSTPerc', 'IGSTAmount', 'SGSTPerc', 'SGSTAmount',
                  'CGSTPerc', 'CGSTAmount',
                  'LedgerName','LedgerID', 'Date', 'Supplier','SupplierName', 'GST_Treatment', 'Notes',
                  'TotalGrossAmt', 'TotalTaxableAmount', 'TotalDiscount', 'TotalTaxAmount',
                  'TotalNetAmount', 'RoundOff', 'GrandTotal', 'TaxInclusive', 'TaxType',
                  'TaxTypeID', 'TotalVATAmount', 'TotalIGSTAmount', 'TotalSGSTAmount',
                  'TotalCGSTAmount', 'TaxNo', 'TaxID', 'TaxName', 'MasterUid', 'SupplierBalance',
                  'PaymentMode', 'PaymentID', 'MasterAmount', 'PaymentName')

    def get_PaymentMode(self, instances):
        CompanyID = self.context.get("CompanyID")
        ExpenseMasterID = instances.ExpenseMasterID
        BranchID = instances.BranchID
        PaymentMode = ""
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            master_ins = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            PaymentMode = master_ins.PaymentMode
        return PaymentMode
    
    def get_PaymentID(self, instances):
        CompanyID = self.context.get("CompanyID")
        ExpenseMasterID = instances.ExpenseMasterID
        BranchID = instances.BranchID
        PaymentID = ""
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            master_ins = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            if master_ins.PaymentID:
                PaymentID = master_ins.PaymentID.id
        return PaymentID
    
    def get_PaymentName(self, instances):
        CompanyID = self.context.get("CompanyID")
        ExpenseMasterID = instances.ExpenseMasterID
        BranchID = instances.BranchID
        PaymentName = ""
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            master_ins = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            if master_ins.PaymentID:
                PaymentName = master_ins.PaymentID.LedgerName
        return PaymentName
    
    def get_MasterAmount(self, instances):
        CompanyID = self.context.get("CompanyID")
        ExpenseMasterID = instances.ExpenseMasterID
        BranchID = instances.BranchID
        Amount = 0
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            master_ins = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            Amount = master_ins.Amount
        return Amount

    def get_MasterUid(self, instances):
        CompanyID = self.context.get("CompanyID")
        ExpenseMasterID = instances.ExpenseMasterID
        BranchID = instances.BranchID
        MasterUid = ""
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            master_ins = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            MasterUid = master_ins.id
        return MasterUid
    
    def get_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")
        TaxID = instances.TaxID
        BranchID = instances.BranchID
        TaxName = ""
        if table.TaxCategory.objects.filter(CompanyID=CompanyID, BranchID=BranchID, TaxID=TaxID).exists():
            master_ins = table.TaxCategory.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, TaxID=TaxID).first()
            TaxName = master_ins.TaxName
        return TaxName
    
    def get_TaxNo(self, instances):
        CompanyID = self.context.get("CompanyID")
        ExpenseMasterID = instances.ExpenseMasterID
        BranchID = instances.BranchID
        TaxNo = ""
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            master_ins = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            TaxNo = master_ins.TaxNo
        return TaxNo

    def get_TotalSGSTAmount(self, instances):
        CompanyID = self.context.get("CompanyID")
        ExpenseMasterID = instances.ExpenseMasterID
        BranchID = instances.BranchID
        TotalSGSTAmount = ""
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            master_ins = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            TotalSGSTAmount = master_ins.TotalSGSTAmount
        return TotalSGSTAmount
    
    def get_TotalCGSTAmount(self, instances):
        CompanyID = self.context.get("CompanyID")
        ExpenseMasterID = instances.ExpenseMasterID
        BranchID = instances.BranchID
        TotalCGSTAmount = ""
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            master_ins = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            TotalCGSTAmount = master_ins.TotalCGSTAmount
        return TotalCGSTAmount
    
    def get_TotalIGSTAmount(self, instances):
        CompanyID = self.context.get("CompanyID")
        ExpenseMasterID = instances.ExpenseMasterID
        BranchID = instances.BranchID
        TotalIGSTAmount = ""
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            master_ins = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            TotalIGSTAmount = master_ins.TotalIGSTAmount
        return TotalIGSTAmount
    
    def get_TotalVATAmount(self, instances):
        CompanyID = self.context.get("CompanyID")
        ExpenseMasterID = instances.ExpenseMasterID
        BranchID = instances.BranchID
        TotalVATAmount = ""
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            master_ins = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            TotalVATAmount = master_ins.TotalVATAmount
        return TotalVATAmount
    
    def get_TaxTypeID(self, instances):
        CompanyID = self.context.get("CompanyID")
        ExpenseMasterID = instances.ExpenseMasterID
        BranchID = instances.BranchID
        TaxTypeID = ""
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            master_ins = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            TaxTypeID = master_ins.TaxTypeID
        return TaxTypeID
    
    def get_TaxType(self, instances):
        CompanyID = self.context.get("CompanyID")
        ExpenseMasterID = instances.ExpenseMasterID
        BranchID = instances.BranchID
        TaxType = ""
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            master_ins = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            TaxType = master_ins.TaxType
        return TaxType

    def get_TaxInclusive(self, instances):
        CompanyID = self.context.get("CompanyID")
        ExpenseMasterID = instances.ExpenseMasterID
        BranchID = instances.BranchID
        TaxInclusive = ""
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            master_ins = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            TaxInclusive = master_ins.TaxInclusive
        return TaxInclusive
    
    def get_GrandTotal(self, instances):
        CompanyID = self.context.get("CompanyID")
        ExpenseMasterID = instances.ExpenseMasterID
        BranchID = instances.BranchID
        GrandTotal = ""
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            master_ins = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            GrandTotal = master_ins.GrandTotal
        return GrandTotal
    
    def get_RoundOff(self, instances):
        CompanyID = self.context.get("CompanyID")
        ExpenseMasterID = instances.ExpenseMasterID
        BranchID = instances.BranchID
        RoundOff = ""
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            master_ins = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            RoundOff = master_ins.RoundOff
        return RoundOff
    
    def get_TotalNetAmount(self, instances):
        CompanyID = self.context.get("CompanyID")
        ExpenseMasterID = instances.ExpenseMasterID
        BranchID = instances.BranchID
        TotalNetAmount = ""
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            master_ins = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            TotalNetAmount = master_ins.TotalNetAmount
        return TotalNetAmount
    
    def get_TotalTaxAmount(self, instances):
        CompanyID = self.context.get("CompanyID")
        ExpenseMasterID = instances.ExpenseMasterID
        BranchID = instances.BranchID
        TotalTaxAmount = ""
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            master_ins = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            TotalTaxAmount = master_ins.TotalTaxAmount
        return TotalTaxAmount

    def get_TotalDiscount(self, instances):
        CompanyID = self.context.get("CompanyID")
        ExpenseMasterID = instances.ExpenseMasterID
        BranchID = instances.BranchID
        TotalDiscount = ""
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            master_ins = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            TotalDiscount = master_ins.TotalDiscount
        return TotalDiscount
    
    def get_TotalTaxableAmount(self, instances):
        CompanyID = self.context.get("CompanyID")
        ExpenseMasterID = instances.ExpenseMasterID
        BranchID = instances.BranchID
        TotalTaxableAmount = ""
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            master_ins = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            TotalTaxableAmount = master_ins.TotalTaxableAmount
        return TotalTaxableAmount

    def get_TotalGrossAmt(self, instances):
        CompanyID = self.context.get("CompanyID")
        ExpenseMasterID = instances.ExpenseMasterID
        BranchID = instances.BranchID
        TotalGrossAmt = ""
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            master_ins = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            TotalGrossAmt = master_ins.TotalGrossAmt
        return TotalGrossAmt
    
    def get_Notes(self, instances):
        CompanyID = self.context.get("CompanyID")
        ExpenseMasterID = instances.ExpenseMasterID
        BranchID = instances.BranchID
        Notes = ""
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            master_ins = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            Notes = master_ins.Notes
        return Notes
    
    def get_GST_Treatment(self, instances):
        CompanyID = self.context.get("CompanyID")
        ExpenseMasterID = instances.ExpenseMasterID
        BranchID = instances.BranchID
        GST_Treatment = ""
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            master_ins = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            GST_Treatment = master_ins.GST_Treatment
        return GST_Treatment
    
    def get_Supplier(self, instances):
        CompanyID = self.context.get("CompanyID")
        ExpenseMasterID = instances.ExpenseMasterID
        BranchID = instances.BranchID
        Supplier = ""
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            master_ins = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            Supplier = master_ins.Supplier.id
        return Supplier
    
    def get_SupplierBalance(self, instances):
        CompanyID = self.context.get("CompanyID")
        ExpenseMasterID = instances.ExpenseMasterID
        BranchID = instances.BranchID
        SupplierBalance = 0
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            master_ins = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            Supplier = master_ins.Supplier.LedgerID
            SupplierBalance = get_BalanceFromLedgerPost(
                CompanyID, Supplier, BranchID)
        return SupplierBalance
    
    def get_SupplierName(self, instances):
        CompanyID = self.context.get("CompanyID")
        ExpenseMasterID = instances.ExpenseMasterID
        BranchID = instances.BranchID
        SupplierName = ""
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            master_ins = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            SupplierName = master_ins.Supplier.LedgerName
        return SupplierName
    
    def get_Date(self, instances):
        CompanyID = self.context.get("CompanyID")
        ExpenseMasterID = instances.ExpenseMasterID
        BranchID = instances.BranchID
        Date = ""
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            master_ins = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            Date = master_ins.Date
        return Date

    def get_VoucherNo(self, instances):
        CompanyID = self.context.get("CompanyID")
        ExpenseMasterID = instances.ExpenseMasterID
        BranchID = instances.BranchID
        VoucherNo = ""
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            master_ins = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            VoucherNo = master_ins.VoucherNo
        return VoucherNo

    def get_TotalAmount(self, instances):
        CompanyID = self.context.get("CompanyID")
        ExpenseMasterID = instances.ExpenseMasterID
        BranchID = instances.BranchID
        TotalAmount = ""
        if table.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
            master_ins = table.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).first()
            TotalAmount = master_ins.GrandTotal
        return TotalAmount


    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerName = instances.Ledger.LedgerName
        return LedgerName
    
    def get_LedgerID(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.Ledger.id
        return LedgerID


class StockOrderListSerializer(serializers.ModelSerializer):
    WarehouseFrom = serializers.SerializerMethodField()
    WarehouseTo = serializers.SerializerMethodField()

    class Meta:
        model = table.StockTransferMaster_ID
        fields = ('id', 'VoucherNo', 'GrandTotal',
                  'Date', 'WarehouseFrom', 'WarehouseTo', 'StockTransferMasterID', 'IsTaken')

    def get_WarehouseFrom(self, instances):
        CompanyID = self.context.get("CompanyID")
        WarehouseFromID = instances.WarehouseFromID
        WarehouseName = ""
        if table.Warehouse.objects.filter(CompanyID=CompanyID, WarehouseID=WarehouseFromID).exists():
            WarehouseName = table.Warehouse.objects.get(
                CompanyID=CompanyID, WarehouseID=WarehouseFromID).WarehouseName
        return WarehouseName
    
    def get_WarehouseTo(self, instances):
        CompanyID = self.context.get("CompanyID")
        WarehouseToID = instances.WarehouseToID
        WarehouseName = ""
        if table.Warehouse.objects.filter(CompanyID=CompanyID, WarehouseID=WarehouseToID).exists():
            WarehouseName = table.Warehouse.objects.get(
                CompanyID=CompanyID, WarehouseID=WarehouseToID).WarehouseName
        return WarehouseName


class SalesReturnMasterSerializer(serializers.ModelSerializer):
    SalesReturnDetails = serializers.SerializerMethodField()
    DetailID = serializers.SerializerMethodField()
    CashReceived = serializers.SerializerMethodField()
    BankAmount = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    BillDiscPercent = serializers.SerializerMethodField()
    BillDiscAmt = serializers.SerializerMethodField()
    # =====
    Date = serializers.SerializerMethodField()

    class Meta:
        model = table.SalesReturnMaster
        fields = (
            "id",
            "Date",
            "SalesReturnMasterID",
            "VoucherNo",
            "LedgerID",
            "LedgerName",
            "SalesAccount",
            "CashReceived",
            "BankAmount",
            "WarehouseID",
            "TaxID",
            "TaxType",
            "BillDiscPercent",
            "BillDiscAmt",
            "SalesReturnDetails",
            "Country_of_Supply",
            "State_of_Supply",
            "GST_Treatment",
            "VAT_Treatment",
            "CashID",
            "BankID",
            "DetailID"

        )
        
    def get_DetailID(self,instance):
        DetailID = 0
        return DetailID

    def get_Date(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        VoucherDate = instances.VoucherDate
        return str(VoucherDate)

    def get_SalesReturnDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        salesReturn_details = table.SalesReturnDetails.objects.filter(
            CompanyID=CompanyID,
            SalesReturnMasterID=instances.SalesReturnMasterID,
            BranchID=instances.BranchID,
        ).order_by("SalesReturnDetailsID")
        serialized = SalesReturnDetailsRestSerializer(
            salesReturn_details,
            many=True,
            context={"CompanyID": CompanyID, "PriceRounding": PriceRounding},
        )

        return serialized.data

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        LedgerName = ""
        if table.AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID
        ).exists():
            ledger = table.AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID)
            LedgerName = ledger.LedgerName
        return LedgerName

    def get_CashReceived(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CashReceived = instances.CashReceived
        # CashReceived = round(CashReceived,PriceRounding)

        return converted_float(CashReceived)

    def get_BankAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BankAmount = instances.BankAmount
        # BankAmount = round(BankAmount,PriceRounding)
        return converted_float(BankAmount)

    def get_BillDiscPercent(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscPercent = instances.BillDiscPercent
        # BillDiscPercent = round(BillDiscPercent,PriceRounding)
        return converted_float(BillDiscPercent)

    def get_BillDiscAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscAmt = instances.BillDiscAmt
        # BillDiscAmt = round(BillDiscAmt,PriceRounding)
        return converted_float(BillDiscAmt)
    
    
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
    BatchCode = serializers.SerializerMethodField()
    is_inclusive = serializers.SerializerMethodField()
    ActualUnitPrice = serializers.SerializerMethodField()
    is_show_details = serializers.SerializerMethodField()
    SerialNos = serializers.SerializerMethodField()
    ProductCode = serializers.SerializerMethodField()
    HSNCode = serializers.SerializerMethodField()
    ProductTaxName = serializers.SerializerMethodField()
    GST_Inclusive = serializers.SerializerMethodField()
    Vat_Inclusive = serializers.SerializerMethodField()
    SalesPrice = serializers.SerializerMethodField()
    ActualProductTaxName = serializers.SerializerMethodField()
    ActualProductTaxID = serializers.SerializerMethodField()
    unitPrice_print = serializers.SerializerMethodField()
    NetAmount_print = serializers.SerializerMethodField()
    VATPerc_print = serializers.SerializerMethodField()
    VATAmount_print = serializers.SerializerMethodField()
    NetAmount_print = serializers.SerializerMethodField()
    DiscountAmount_print = serializers.SerializerMethodField()
    TaxableAmount_print = serializers.SerializerMethodField()
    product_description = serializers.SerializerMethodField()
    ManufactureDatePrint = serializers.SerializerMethodField()
    ExpiryDatePrint = serializers.SerializerMethodField()
    ProductCodeVal = serializers.SerializerMethodField()
    SalesDetailsID = serializers.SerializerMethodField()
    TotalTaxRounded = serializers.SerializerMethodField()
    gstPer = serializers.SerializerMethodField()
    Description = serializers.SerializerMethodField()
    current_stock = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()

    class Meta:
        model = table.SalesReturnDetails
        fields = (
            "id",
            "TaxableAmount_print",
            "DiscountAmount_print",
            "NetAmount_print",
            "VATPerc_print",
            "VATAmount_print",
            "unq_id",
            "NetAmount_print",
            "unitPrice_print",
            "SalesReturnDetailsID",
            "Description",
            "BranchID",
            "Action",
            "SalesReturnMasterID",
            "DeliveryDetailsID",
            "OrderDetailsID",
            "ProductID",
            "ProductName",
            "Qty",
            "FreeQty",
            "UnitPrice",
            "InclusivePrice",
            "detailID",
            "TotalTax",
            "UnitName",
            "ProductTaxID",
            "RateWithTax",
            "CostPerPrice",
            "PriceListID",
            "DiscountPerc",
            "DiscountAmount",
            "KFCAmount",
            "KFCPerc",
            "GST_Inclusive",
            "Vat_Inclusive",
            "SalesPrice",
            "GrossAmount",
            "TaxableAmount",
            "VATPerc",
            "VATAmount",
            "SGSTPerc",
            "SGSTAmount",
            "CGSTPerc",
            "is_inclusive",
            "CGSTAmount",
            "IGSTPerc",
            "IGSTAmount",
            "NetAmount",
            "Flavour",
            "CreatedUserID",
            "CreatedDate",
            "UpdatedDate",
            "AddlDiscPerc",
            "AddlDiscAmt",
            "TAX1Perc",
            "TAX1Amount",
            "TAX2Perc",
            "TAX2Amount",
            "TAX3Perc",
            "TAX3Amount",
            "ActualProductTaxName",
            "ActualProductTaxID",
            "is_VAT_inclusive",
            "is_GST_inclusive",
            "is_TAX1_inclusive",
            "is_TAX2_inclusive",
            "is_TAX3_inclusive",
            "ProductTaxName",
            "unitPriceRounded",
            "quantityRounded",
            "actualSalesPrice",
            "netAmountRounded",
            "BatchCode",
            "ActualUnitPrice",
            "is_show_details",
            "SerialNos",
            "ProductCode",
            "HSNCode",
            "product_description",
            "ManufactureDatePrint",
            "ExpiryDatePrint",
            "ProductCodeVal",
            "SalesDetailsID",
            "TotalTaxRounded",
            "gstPer",
            "current_stock",
            "stock_status",
        )
        
    def get_current_stock(self, purchaseReturn_details):
        current_stock = ""
        return current_stock

    def get_stock_status(self, purchaseReturn_details):
        stock_status = ""
        return stock_status
        
    def get_Description(self, sales_details):
        Description = sales_details.Description
        if not Description:
            Description = ""
        return Description
    
    def get_gstPer(self, sales_details):
        gstPer = sales_details.IGSTPerc
        return gstPer
        
    def get_TotalTaxRounded(self, sales_details):
        CompanyID = self.context.get("CompanyID")

        TAX1Amount = sales_details.TAX1Amount
        TAX2Amount = sales_details.TAX2Amount
        TAX3Amount = sales_details.TAX3Amount
        VATAmount = sales_details.VATAmount
        IGSTAmount = sales_details.IGSTAmount
        SGSTAmount = sales_details.SGSTAmount
        CGSTAmount = sales_details.CGSTAmount

        TotalTax = (
            TAX1Amount
            + TAX2Amount
            + TAX3Amount
            + VATAmount
            + CGSTAmount
            + SGSTAmount
            + IGSTAmount
        )

        return converted_float(TotalTax)

    def get_ManufactureDatePrint(self, sales_details):
        ManufactureDate = ""
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        BatchCode = sales_details.BatchCode
        if table.Batch.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode
        ).exists():
            batch_details = table.Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode
            ).first()
            ManufactureDate = batch_details.ManufactureDate
            if ManufactureDate:
                Date = ManufactureDate.strftime("%Y/%d")
                ManufactureDate = Date
        return ManufactureDate

    def get_ExpiryDatePrint(self, sales_details):
        ExpiryDate = ""
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        BatchCode = sales_details.BatchCode
        if table.Batch.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode
        ).exists():
            batch_details = table.Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode
            ).first()
            ExpiryDate = batch_details.ExpiryDate
            if ExpiryDate:
                Date = ExpiryDate.strftime("%Y/%d")
                ExpiryDate = Date
        return ExpiryDate

    # def get_BatchList(self, sales_details):
    #     BatchCode_list = []
    #     CompanyID = self.context.get("CompanyID")
    #     PriceRounding = int(self.context.get("PriceRounding"))
    #     BranchID = sales_details.BranchID
    #     ProductID = sales_details.ProductID
    #     BatchCode_list = []
    #     if table.Batch.objects.filter(
    #         CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
    #     ).exists():
    #         batch_details = table.Batch.objects.filter(
    #             CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
    #         )
    #         BatchCode_list = Batch_ListSerializer(
    #             batch_details,
    #             many=True,
    #             context={"CompanyID": CompanyID, "PriceRounding": PriceRounding},
    #         )
    #         BatchCode_list = BatchCode_list.data
    #     return BatchCode_list

    def get_product_description(self, purchaseReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchaseReturn_details.BranchID
        ProductID = purchaseReturn_details.ProductID
        Description = ""
        if table.Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID).exists():
            Description = table.Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID
            ).Description
        return str(Description)
    
    def get_SalesDetailsID(self, salesReturn_details):
        SalesDetailsID = salesReturn_details.SalesReturnDetailsID
        return SalesDetailsID

    def get_TaxableAmount_print(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")

        TaxableAmount = salesReturn_details.TaxableAmount
        TaxableAmount = round(TaxableAmount, PriceRounding)

        return str(TaxableAmount)

    def get_DiscountAmount_print(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        DiscountAmount = salesReturn_details.DiscountAmount
        DiscountAmount = round(DiscountAmount, PriceRounding)

        return str(DiscountAmount)

    def get_VATPerc_print(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        VATPerc = salesReturn_details.VATPerc
        print(VATPerc, "((((((((**VATPerc****))))))))")

        VATPerc = round(VATPerc, PriceRounding)

        return str(VATPerc)

    def get_VATAmount_print(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        VATAmount = salesReturn_details.VATAmount
        print(VATAmount, "((((((((***VATAmount***))))))))")

        VATAmount = round(VATAmount, PriceRounding)

        return str(VATAmount)

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

    def get_ActualProductTaxName(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductTaxID = sales_details.ProductTaxID
        BranchID = sales_details.BranchID
        ActualProductTaxName = ""
        if table.TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=ProductTaxID).exists():
            ActualProductTaxName = table.TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=ProductTaxID
            ).TaxName
        return ActualProductTaxName

    def get_ActualProductTaxID(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ActualProductTaxID = sales_details.ProductTaxID
        return ActualProductTaxID

    def get_Vat_Inclusive(self, salesReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = salesReturn_details.BranchID
        ProductID = salesReturn_details.ProductID
        ProductTaxID = salesReturn_details.ProductTaxID
        if ProductTaxID:
            VatID = ProductTaxID
        else:
            VatID = table.Product.objects.get(CompanyID=CompanyID, ProductID=ProductID).VatID
        Inclusive = False
        if VatID:
            Inclusive = table.TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=VatID
            ).Inclusive
        return Inclusive

    def get_GST_Inclusive(self, salesReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = salesReturn_details.BranchID
        ProductID = salesReturn_details.ProductID
        ProductTaxID = salesReturn_details.ProductTaxID
        Inclusive = False
        if ProductTaxID:
            GST = ProductTaxID
        else:
            GST = table.Product.objects.get(CompanyID=CompanyID, ProductID=ProductID).GST
        if GST:
            Inclusive = table.TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=GST
            ).Inclusive
        return Inclusive

    def get_SalesPrice(self, salesReturn_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = salesReturn_details.PriceListID
        BranchID = salesReturn_details.BranchID
        SalesPrice = 0
        if table.PriceList.objects.filter(
            CompanyID=CompanyID, PriceListID=PriceListID
        ).exists():
            SalesPrice = table.PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListID
            ).SalesPrice
        return converted_float(SalesPrice)

    def get_ProductTaxName(self, salesReturn_details):
        CompanyID = self.context.get("CompanyID")
        ProductTaxID = salesReturn_details.ProductTaxID
        BranchID = salesReturn_details.BranchID
        ProductTaxName = ""
        if table.TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=ProductTaxID).exists():
            ProductTaxName = table.TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=ProductTaxID
            ).TaxName
        return ProductTaxName

    def get_is_show_details(self, instances):
        return False

    def get_ProductName(self, salesReturn_details):

        CompanyID = self.context.get("CompanyID")

        ProductID = salesReturn_details.ProductID
        BranchID = salesReturn_details.BranchID

        if table.Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID).exists():

            product = table.Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)

            ProductName = product.ProductName
        else:
            ProductName = ""

        return ProductName

    def get_ProductCode(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = sales_details.ProductID
        product = table.Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)
        ProductCode = product.ProductCode
        return ProductCode

    def get_ProductCodeVal(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = sales_details.ProductID
        product = table.Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)
        ProductCode = product.ProductCode
        return ProductCode

    def get_HSNCode(self, sales_details):

        CompanyID = self.context.get("CompanyID")

        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID

        product = table.Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)

        HSNCode = product.HSNCode
        return HSNCode

    # def get_UnitList(self, salesReturn_details):

    #     CompanyID = self.context.get("CompanyID")
    #     PriceRounding = self.context.get("PriceRounding")

    #     ProductID = salesReturn_details.ProductID
    #     BranchID = salesReturn_details.BranchID

    #     UnitList = table.PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID)

    #     serialized = PriceListRestSerializer(
    #         UnitList,
    #         many=True,
    #         context={"CompanyID": CompanyID, "PriceRounding": PriceRounding},
    #     )

    #     return serialized.data

    def get_is_inclusive(self, salesReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = salesReturn_details.BranchID
        ProductID = salesReturn_details.ProductID
        is_inclusive = table.Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID
        ).is_inclusive

        return is_inclusive

    def get_BatchCode(self, salesReturn_details):
        CompanyID = self.context.get("CompanyID")
        BatchCode = salesReturn_details.BatchCode
        BranchID = salesReturn_details.BranchID
        if not BatchCode:
            BatchCode = 0

        return BatchCode

    def get_id(self, instances):
        id = instances.id

        return str(id)

    def get_InclusivePrice(self, salesReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        # PriceRounding = 2
        InclusivePrice = salesReturn_details.InclusivePrice
        if not InclusivePrice:
            InclusivePrice = 0

        return converted_float(InclusivePrice)

    def get_unitPriceRounded(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        UnitPrice = salesReturn_details.UnitPrice
        # UnitPrice = round(UnitPrice,PriceRounding)
        return converted_float(UnitPrice)

    def get_quantityRounded(self, salesReturn_details):
        Qty = salesReturn_details.Qty
        return converted_float(Qty)

    def get_ActualUnitPrice(self, salesReturn_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = salesReturn_details.PriceListID
        BranchID = salesReturn_details.BranchID
        ProductID = salesReturn_details.ProductID
        SalesPrice = 0
        if table.PriceList.objects.filter(
            ProductID=ProductID, CompanyID=CompanyID, PriceListID=PriceListID
        ).exists():
            SalesPrice = table.PriceList.objects.get(
                ProductID=ProductID, CompanyID=CompanyID, PriceListID=PriceListID
            ).SalesPrice
        return converted_float(SalesPrice)

    def get_actualSalesPrice(self, salesReturn_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = salesReturn_details.PriceListID
        BranchID = salesReturn_details.BranchID
        ProductID = salesReturn_details.ProductID
        SalesPrice = 0
        if table.PriceList.objects.filter(
            ProductID=ProductID, CompanyID=CompanyID, PriceListID=PriceListID
        ).exists():
            SalesPrice = table.PriceList.objects.get(
                ProductID=ProductID, CompanyID=CompanyID, PriceListID=PriceListID
            ).SalesPrice
        return converted_float(SalesPrice)

    def get_netAmountRounded(self, salesReturn_details):
        NetAmount = salesReturn_details.NetAmount
        return converted_float(NetAmount)

    def get_is_VAT_inclusive(self, salesReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = salesReturn_details.BranchID
        ProductID = salesReturn_details.ProductID
        Inclusive = False
        VatID = table.Product.objects.get(CompanyID=CompanyID, ProductID=ProductID).VatID
        if VatID:
            Inclusive = table.TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=VatID
            ).Inclusive
        return Inclusive

    def get_is_GST_inclusive(self, salesReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = salesReturn_details.BranchID
        ProductID = salesReturn_details.ProductID
        Inclusive = False
        GST = table.Product.objects.get(CompanyID=CompanyID, ProductID=ProductID).GST
        if GST:
            Inclusive = table.TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=GST
            ).Inclusive
        return Inclusive

    def get_is_TAX1_inclusive(self, salesReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = salesReturn_details.BranchID
        ProductID = salesReturn_details.ProductID
        Inclusive = False
        Tax1 = table.Product.objects.get(CompanyID=CompanyID, ProductID=ProductID).Tax1
        if Tax1:
            Inclusive = table.TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax1
            ).Inclusive
        return Inclusive

    def get_is_TAX2_inclusive(self, salesReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = salesReturn_details.BranchID
        ProductID = salesReturn_details.ProductID
        Inclusive = False
        Tax2 = table.Product.objects.get(CompanyID=CompanyID, ProductID=ProductID).Tax2
        if Tax2:
            Inclusive = table.TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax2
            ).Inclusive
        return Inclusive

    def get_is_TAX3_inclusive(self, salesReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = salesReturn_details.BranchID
        ProductID = salesReturn_details.ProductID
        Inclusive = False
        Tax3 = table.Product.objects.get(CompanyID=CompanyID, ProductID=ProductID).Tax3
        if Tax3:
            Inclusive = table.TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax3
            ).Inclusive
        return Inclusive

    def get_AddlDiscPerc(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        AddlDiscPerc = salesReturn_details.AddlDiscPercent

        if not AddlDiscPerc:
            AddlDiscPerc = 0

        return converted_float(AddlDiscPerc)

    def get_AddlDiscAmt(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        AddlDiscAmt = salesReturn_details.AddlDiscAmt

        if not AddlDiscAmt:
            AddlDiscAmt = 0

        return converted_float(AddlDiscAmt)

    def get_UnitName(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        PriceListID = purchase_details.PriceListID
        BranchID = purchase_details.BranchID

        if table.PriceList.objects.filter(
            CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID
        ).exists():
            UnitID = table.PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListID
            ).UnitID
            UnitName = table.Unit.objects.get(CompanyID=CompanyID, UnitID=UnitID).UnitName
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
        CGSTAmount = purchase_details.CGSTAmount

        TotalTax = (
            TAX1Amount
            + TAX2Amount
            + TAX3Amount
            + VATAmount
            + CGSTAmount
            + SGSTAmount
            + IGSTAmount
        )

        return converted_float(TotalTax)

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

        if not Qty:
            Qty = 0

        return converted_float(Qty)

    def get_FreeQty(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        FreeQty = salesReturn_details.FreeQty

        if not FreeQty:
            FreeQty = 0

        return converted_float(FreeQty)

    def get_UnitPrice(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        UnitPrice = salesReturn_details.UnitPrice

        if not UnitPrice:
            UnitPrice = 0

        return converted_float(UnitPrice)

    def get_RateWithTax(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        RateWithTax = salesReturn_details.RateWithTax

        if not RateWithTax:
            RateWithTax = 0

        return converted_float(RateWithTax)

    def get_CostPerPrice(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        CostPerPrice = salesReturn_details.CostPerPrice

        if not CostPerPrice:
            CostPerPrice = 0

        return converted_float(CostPerPrice)

    def get_DiscountPerc(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        DiscountPerc = salesReturn_details.DiscountPerc

        if not DiscountPerc:
            DiscountPerc = 0

        return converted_float(DiscountPerc)

    def get_DiscountAmount(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        DiscountAmount = salesReturn_details.DiscountAmount

        if not DiscountAmount:
            DiscountAmount = 0

        return converted_float(DiscountAmount)

    def get_GrossAmount(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        GrossAmount = salesReturn_details.GrossAmount

        if not GrossAmount:
            GrossAmount = 0

        return converted_float(GrossAmount)

    def get_TaxableAmount(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        TaxableAmount = salesReturn_details.TaxableAmount

        if not TaxableAmount:
            TaxableAmount = 0

        return converted_float(TaxableAmount)

    def get_VATAmount(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        VATAmount = salesReturn_details.VATAmount

        if not VATAmount:
            VATAmount = 0

        return converted_float(VATAmount)

    def get_SGSTAmount(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        SGSTAmount = salesReturn_details.SGSTAmount

        if not SGSTAmount:
            SGSTAmount = 0

        return converted_float(SGSTAmount)

    def get_CGSTAmount(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        CGSTAmount = salesReturn_details.CGSTAmount

        if not CGSTAmount:
            CGSTAmount = 0

        return converted_float(CGSTAmount)

    def get_IGSTAmount(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        IGSTAmount = salesReturn_details.IGSTAmount

        if not IGSTAmount:
            IGSTAmount = 0

        return converted_float(IGSTAmount)

    def get_TAX1Amount(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX1Amount = salesReturn_details.TAX1Amount

        if not TAX1Amount:
            TAX1Amount = 0

        return converted_float(TAX1Amount)

    def get_TAX2Amount(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX2Amount = salesReturn_details.TAX2Amount

        if not TAX2Amount:
            TAX2Amount = 0

        return converted_float(TAX2Amount)

    def get_TAX3Amount(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX3Amount = salesReturn_details.TAX3Amount

        if not TAX3Amount:
            TAX3Amount = 0

        return converted_float(TAX3Amount)

    def get_NetAmount(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        NetAmount = salesReturn_details.NetAmount

        if not NetAmount:
            NetAmount = 0

        return converted_float(NetAmount)

    def get_SerialNos(self, sales_details):
        SerialNos = []
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        SalesMasterID = sales_details.SalesReturnMasterID
        SalesDetailsID = sales_details.SalesReturnDetailsID
        if table.SerialNumbers.objects.filter(
            CompanyID=CompanyID,
            BranchID=BranchID,
            SalesMasterID=SalesMasterID,
            SalesDetailsID=SalesDetailsID,
            VoucherType="SR",
        ).exists():
            Serial_details = table.SerialNumbers.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                SalesMasterID=SalesMasterID,
                SalesDetailsID=SalesDetailsID,
                VoucherType="SR",
            )
            SerialNos = SerialNumberSerializer(
                Serial_details, many=True, context={"CompanyID": CompanyID}
            )
            SerialNos = SerialNos.data
        return SerialNos
    
    
class SalesFaeraSerializer(serializers.ModelSerializer):
    SalesDetails = serializers.SerializerMethodField()
    CashReceived = serializers.SerializerMethodField()
    BankAmount = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    BillDiscPercent = serializers.SerializerMethodField()
    BillDiscAmt = serializers.SerializerMethodField()
    GST_Treatment = serializers.SerializerMethodField()
    VAT_Treatment = serializers.SerializerMethodField()
    

    class Meta:
        model = table.SalesMaster

        fields = (
            "id",
            "SalesMasterID",
            "VoucherNo",
            "Date",
            "LedgerID",
            "LedgerName",
            "CashID",
            "BankID",
            "Country_of_Supply",
            "State_of_Supply",
            "VAT_Treatment",
            "SalesAccount",
            "GST_Treatment",
            "CashReceived",
            "BankAmount",
            "WarehouseID",
            "CardTypeID",
            "CardNumber",
            "TaxID",
            "TaxType",
            "BillDiscPercent",
            "BillDiscAmt",
            "SalesDetails",
        )

    def get_GST_Treatment(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        GST_Treatment = instances.GST_Treatment
        if not GST_Treatment:
            GST_Treatment = ""
            if table.Parties.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).exists():
                pary_ins = table.Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
                ).first()
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
            if table.Parties.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).exists():
                pary_ins = table.Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
                ).first()
                VAT_Treatment = pary_ins.VAT_Treatment
        return str(VAT_Treatment)


    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        if table.AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID
        ).exists():
            ledger = table.AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID)

            LedgerName = ledger.LedgerName
        else:
            LedgerName = ""

        return LedgerName

    def get_SalesDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        print(PriceRounding)

        SalesMasterID = instances.SalesMasterID
        WarehouseID = instances.WarehouseID
        BranchID = instances.BranchID
        print(SalesMasterID, "SalesMasterID")
        sales_details = table.SalesDetails.objects.filter(
            CompanyID=CompanyID, SalesMasterID=SalesMasterID, BranchID=BranchID
        ).order_by("SalesDetailsID")
        serialized = SalesDetailsFaeraSerializer(
            sales_details,
            many=True,
            context={
                "CompanyID": CompanyID,
                "PriceRounding": PriceRounding,
                "WarehouseID": WarehouseID,
                "BranchID": BranchID,
            },
        )

        return serialized.data

    def get_BillDiscPercent(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscPercent = instances.BillDiscPercent

        # BillDiscPercent = round(BillDiscPercent, PriceRounding)

        return converted_float(BillDiscPercent)

    def get_BillDiscAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscAmt = instances.BillDiscAmt

        # BillDiscAmt = round(BillDiscAmt, PriceRounding)

        return converted_float(BillDiscAmt)

    def get_CashReceived(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CashReceived = instances.CashReceived

        # CashReceived = round(CashReceived, PriceRounding)

        return converted_float(CashReceived)

    def get_BankAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BankAmount = instances.BankAmount

        # BankAmount = round(BankAmount, PriceRounding)

        return converted_float(BankAmount)


class SalesDetailsFaeraSerializer(serializers.ModelSerializer):
    Qty = serializers.SerializerMethodField()
    UnitPrice = serializers.SerializerMethodField()
    InclusivePrice = serializers.SerializerMethodField()
    RateWithTax = serializers.SerializerMethodField()
    CostPerPrice = serializers.SerializerMethodField()
    DiscountPerc = serializers.SerializerMethodField()
    DiscountAmount = serializers.SerializerMethodField()
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
    detailID = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    is_inclusive = serializers.SerializerMethodField()
    ProductTaxName = serializers.SerializerMethodField()
    SalesPrice = serializers.SerializerMethodField()
    ActualProductTaxName = serializers.SerializerMethodField()
    ActualProductTaxID = serializers.SerializerMethodField()
    Stock = serializers.SerializerMethodField()
    gstPer = serializers.SerializerMethodField()
    TotalTaxRounded = serializers.SerializerMethodField()
    Barcode = serializers.SerializerMethodField()
    current_stock = serializers.SerializerMethodField()
    multi_factor = serializers.SerializerMethodField()

    class Meta:
        model = table.SalesDetails
        fields = (
            "id",
            "SalesDetailsID",
            "ProductID",
            "ProductName",
            "ProductTaxID",
            "Qty",
            "UnitPrice",
            "InclusivePrice",
            "RateWithTax",
            "CostPerPrice",
            "PriceListID",
            "UnitName",
            "DiscountPerc",
            "DiscountAmount",
            "AddlDiscAmt",
            "GrossAmount",
            "TaxableAmount",
            "VATPerc",
            "VATAmount",
            "SGSTPerc",
            "SGSTAmount",
            "CGSTPerc",
            "Description",
            "ProductTaxName",
            "CGSTAmount",
            "IGSTPerc",
            "IGSTAmount",
            "NetAmount",
            "CreatedUserID",
            "TotalTax",
            "detailID",
            "is_inclusive",
            "SalesPrice",
            "ActualProductTaxName",
            "ActualProductTaxID",
            "Stock",
            "Barcode",
            "gstPer",
            "TotalTaxRounded",
            "current_stock",
            "multi_factor"
        )
        
    def get_Barcode(self, salesdetails):
        CompanyID = self.context.get("CompanyID")
        PriceListID = salesdetails.PriceListID
        Barcode = ""
        if table.PriceList.objects.filter(CompanyID=CompanyID, PriceListID=PriceListID).exists():
            Barcode = table.PriceList.objects.filter(
                CompanyID=CompanyID, PriceListID=PriceListID).first().Barcode
        return Barcode
    
    def get_multi_factor(self, salesdetails):
        CompanyID = self.context.get("CompanyID")
        PriceListID = salesdetails.PriceListID
        MultiFactor = ""
        if table.PriceList.objects.filter(CompanyID=CompanyID, PriceListID=PriceListID).exists():
            MultiFactor = table.PriceList.objects.filter(
                CompanyID=CompanyID, PriceListID=PriceListID).first().MultiFactor
        return MultiFactor

    def get_current_stock(self, salesdetails):
        CompanyID = self.context.get("CompanyID")
        ProductID = salesdetails.ProductID
        BranchID = salesdetails.BranchID
        WarehouseID = 1
        BatchCode = ""
        current_stock = get_ProductStock(
            CompanyID, BranchID, ProductID, WarehouseID, BatchCode)
        return current_stock

    def get_TotalTaxRounded(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        TAX1Amount = purchase_details.TAX1Amount
        TAX2Amount = purchase_details.TAX2Amount
        TAX3Amount = purchase_details.TAX3Amount
        VATAmount = purchase_details.VATAmount
        IGSTAmount = purchase_details.IGSTAmount
        SGSTAmount = purchase_details.SGSTAmount
        CGSTAmount = purchase_details.CGSTAmount
        KFCAmount = purchase_details.KFCAmount

        TotalTax = (
            converted_float(TAX1Amount)
            + converted_float(TAX2Amount)
            + converted_float(TAX3Amount)
            + converted_float(VATAmount)
            + converted_float(IGSTAmount)
            + converted_float(SGSTAmount)
            + converted_float(CGSTAmount)
            + converted_float(KFCAmount)
        )
        return converted_float(TotalTax)

    def get_gstPer(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        IGSTPerc = sales_details.IGSTPerc
        return converted_float(IGSTPerc)

    def get_Stock(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        WarehouseID = self.context.get("WarehouseID")
        BranchID = self.context.get("BranchID")
        ProductID = sales_details.ProductID
        BatchCode = sales_details.BatchCode
        Stock = 0
        EnableProductBatchWise = get_GeneralSettings(
            CompanyID, BranchID, "EnableProductBatchWise"
        )
        if EnableProductBatchWise == True:
            if table.Batch.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                BatchCode=BatchCode,
                WareHouseID=WarehouseID,
            ).exists():
                Batch_ins = (
                    table.Batch.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        BatchCode=BatchCode,
                        WareHouseID=WarehouseID,
                    )
                    .order_by("BatchCode")
                    .last()
                )
                batch_pricelistID = Batch_ins.PriceListID
                batch_MultiFactor = table.PriceList.objects.get(
                    CompanyID=CompanyID, PriceListID=batch_pricelistID
                ).MultiFactor
                total_stockIN = converted_float(Batch_ins.StockIn) / converted_float(
                    batch_MultiFactor
                )
                total_stockOUT = converted_float(Batch_ins.StockOut) / converted_float(
                    batch_MultiFactor
                )

                Stock = converted_float(total_stockIN) - \
                    converted_float(total_stockOUT)
        else:
            if table.StockPosting.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                ProductID=ProductID,
                WareHouseID=WarehouseID,
            ):
                stock_ins = table.StockPosting.objects.filter(
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    ProductID=ProductID,
                    WareHouseID=WarehouseID,
                )
                qtyIn_sum = stock_ins.aggregate(Sum("QtyIn"))
                qtyIn_sum = qtyIn_sum["QtyIn__sum"]
                qtyOut_sum = stock_ins.aggregate(Sum("QtyOut"))
                qtyOut_sum = qtyOut_sum["QtyOut__sum"]
                Stock = converted_float(qtyIn_sum) - \
                    converted_float(qtyOut_sum)
        return Stock

    def get_ActualProductTaxName(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductTaxID = sales_details.ProductTaxID
        BranchID = sales_details.BranchID
        ActualProductTaxName = ""
        if table.TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=ProductTaxID).exists():
            ActualProductTaxName = table.TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=ProductTaxID
            ).TaxName
        return ActualProductTaxName

    def get_ActualProductTaxID(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ActualProductTaxID = sales_details.ProductTaxID
        return ActualProductTaxID

    def get_SalesPrice(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = sales_details.PriceListID
        SalesPrice = 0
        if table.PriceList.objects.filter(
            CompanyID=CompanyID, PriceListID=PriceListID
        ).exists():
            SalesPrice = table.PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListID
            ).SalesPrice
        return converted_float(SalesPrice)

    def get_ProductTaxName(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductTaxID = sales_details.ProductTaxID
        ProductTaxName = ""
        if table.TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=ProductTaxID).exists():
            ProductTaxName = table.TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=ProductTaxID
            ).TaxName
        return ProductTaxName

    def get_ProductName(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = sales_details.ProductID
        product = table.Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID)
        ProductName = product.ProductName
        return ProductName

    def get_id(self, instances):
        id = instances.id

        return str(id)

    def get_InclusivePrice(self, sales_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        # PriceRounding = 2
        InclusivePrice = sales_details.InclusivePrice
        if not InclusivePrice:
            InclusivePrice = 0
        #     InclusivePrice = round(InclusivePrice, PriceRounding)
        # else:
        #     InclusivePrice = 0

        return converted_float(InclusivePrice)

    def get_is_inclusive(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        is_inclusive = table.Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID
        ).is_inclusive

        return is_inclusive

    def get_TotalTax(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        TAX1Amount = purchase_details.TAX1Amount
        TAX2Amount = purchase_details.TAX2Amount
        TAX3Amount = purchase_details.TAX3Amount
        VATAmount = purchase_details.VATAmount
        IGSTAmount = purchase_details.IGSTAmount
        SGSTAmount = purchase_details.SGSTAmount
        CGSTAmount = purchase_details.CGSTAmount
        KFCAmount = purchase_details.KFCAmount

        TotalTax = (
            converted_float(TAX1Amount)
            + converted_float(TAX2Amount)
            + converted_float(TAX3Amount)
            + converted_float(VATAmount)
            + converted_float(IGSTAmount)
            + converted_float(SGSTAmount)
            + converted_float(CGSTAmount)
            + converted_float(KFCAmount)
        )

        return converted_float(TotalTax)

    def get_detailID(self, purchase_details):

        detailID = 0

        return detailID

    def get_UnitName(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        PriceListID = purchase_details.PriceListID
        BranchID = purchase_details.BranchID

        if table.PriceList.objects.filter(
            CompanyID=CompanyID, PriceListID=PriceListID
        ).exists():
            UnitID = table.PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListID
            ).UnitID
            UnitName = table.Unit.objects.get(
                UnitID=UnitID, CompanyID=CompanyID).UnitName
        else:
            UnitName = ""

        return UnitName

    def get_Qty(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        Qty = sales_details.Qty

        # Qty = round(Qty, PriceRounding)

        return converted_float(Qty)

    def get_UnitPrice(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        UnitPrice = sales_details.UnitPrice

        # UnitPrice = round(UnitPrice, PriceRounding)

        return converted_float(UnitPrice)

    def get_RateWithTax(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        RateWithTax = sales_details.RateWithTax

        # RateWithTax = round(RateWithTax, PriceRounding)

        return converted_float(RateWithTax)

    def get_CostPerPrice(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        CostPerPrice = sales_details.CostPerPrice

        # CostPerPrice = round(CostPerPrice, PriceRounding)

        return converted_float(CostPerPrice)

    def get_DiscountPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        DiscountPerc = sales_details.DiscountPerc

        # DiscountPerc = round(DiscountPerc, PriceRounding)

        return converted_float(DiscountPerc)

    def get_DiscountAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        DiscountAmount = sales_details.DiscountAmount

        # DiscountAmount = round(DiscountAmount, PriceRounding)

        return converted_float(DiscountAmount)

    def get_GrossAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        GrossAmount = sales_details.GrossAmount

        # GrossAmount = round(GrossAmount, PriceRounding)

        return converted_float(GrossAmount)

    def get_TaxableAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TaxableAmount = sales_details.TaxableAmount

        # TaxableAmount = round(TaxableAmount, PriceRounding)

        return converted_float(TaxableAmount)

    def get_VATPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        VATPerc = sales_details.VATPerc

        # VATPerc = round(VATPerc, PriceRounding)

        return converted_float(VATPerc)

    def get_VATAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        VATAmount = sales_details.VATAmount

        # VATAmount = round(VATAmount, PriceRounding)

        return converted_float(VATAmount)

    def get_SGSTPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        SGSTPerc = sales_details.SGSTPerc

        # SGSTPerc = round(SGSTPerc, PriceRounding)

        return converted_float(SGSTPerc)

    def get_SGSTAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        SGSTAmount = sales_details.SGSTAmount

        # SGSTAmount = round(SGSTAmount, PriceRounding)

        return converted_float(SGSTAmount)

    def get_CGSTPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        CGSTPerc = sales_details.CGSTPerc

        # CGSTPerc = round(CGSTPerc, PriceRounding)

        return converted_float(CGSTPerc)

    def get_CGSTAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        CGSTAmount = sales_details.CGSTAmount

        # CGSTAmount = round(CGSTAmount, PriceRounding)

        return converted_float(CGSTAmount)

    def get_IGSTPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        IGSTPerc = sales_details.IGSTPerc

        # IGSTPerc = round(IGSTPerc, PriceRounding)

        return converted_float(IGSTPerc)

    def get_IGSTAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        IGSTAmount = sales_details.IGSTAmount

        # IGSTAmount = round(IGSTAmount, PriceRounding)

        return converted_float(IGSTAmount)

    def get_NetAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        NetAmount = sales_details.NetAmount

        # NetAmount = round(NetAmount, PriceRounding)

        return converted_float(NetAmount)

    def get_AddlDiscAmt(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        AddlDiscAmt = sales_details.AddlDiscAmt

        if not AddlDiscAmt:
            AddlDiscAmt = 0
        #     AddlDiscAmt = round(AddlDiscAmt, PriceRounding)
        # else:

        return converted_float(AddlDiscAmt)


class LedgerSerializer(serializers.ModelSerializer):

    class Meta:
        model = table.AccountLedger
        fields = ('id', 'LedgerID', 'LedgerName', 'OpeningBalance')

