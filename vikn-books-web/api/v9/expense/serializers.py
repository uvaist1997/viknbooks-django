from main.functions import converted_float
from rest_framework import serializers
from brands import models as model
from rest_framework.fields import CurrentUserDefault
from api.v9.accountLedgers import serializers as serializer


class ExpenseMasterSerializer(serializers.ModelSerializer):
    SupplierName = serializers.SerializerMethodField()
    GSTNumber = serializers.SerializerMethodField()
    VATNumber = serializers.SerializerMethodField()
    PlaceOfSupplyName = serializers.SerializerMethodField()
    ExpenseDetails = serializers.SerializerMethodField()
    Supplier = serializers.SerializerMethodField()
    LedgerDatas = serializers.SerializerMethodField()
    Amount = serializers.SerializerMethodField()
    class Meta:
        model = model.ExpenseMaster
        fields = ('id','GSTNumber','VATNumber','BranchID','VoucherNo','SupplierName','Supplier','Date','GST_Treatment','PlaceOfSupply','PlaceOfSupplyName','InvoiceNo','TaxType','TaxTypeID','Notes',
            'PaymentMode','PaymentID','Amount','BillDiscPercent','BillDiscAmount','TotalGrossAmt','TotalTaxableAmount','TotalDiscount',
            'TotalTaxAmount','TotalNetAmount','RoundOff','GrandTotal','TaxInclusive','TotalVATAmount','TotalIGSTAmount',
            'TotalSGSTAmount','TotalCGSTAmount','ExpenseDetails','LedgerDatas','TaxNo')


    def get_Supplier(self, instance):
        CompanyID = self.context.get("CompanyID")
        Supplier = instance.Supplier
        return Supplier.id

    def get_GSTNumber(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.Supplier.LedgerID
        BranchID = instances.BranchID
        GSTNumber = ""
        if model.Parties.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        ).exists():
            pary_ins = model.Parties.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).first()
            GSTNumber = pary_ins.GSTNumber
        return str(GSTNumber)


    def get_VATNumber(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        LedgerID = instances.Supplier.LedgerID
        BranchID = instances.BranchID
        VATNumber = ""
        if model.Parties.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        ).exists():
            pary_ins = model.Parties.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).first()
            VATNumber = pary_ins.VATNumber
        return str(VATNumber)
    
    def get_Amount(self, instance):
        CompanyID = self.context.get("CompanyID")
        Amount = instance.Amount
        return converted_float(Amount)

    def get_SupplierName(self, instance):
        CompanyID = self.context.get("CompanyID")
        Supplier = instance.Supplier
        return Supplier.LedgerName

    def get_PlaceOfSupplyName(self, instance):
        CompanyID = self.context.get("CompanyID")
        PlaceOfSupply = ""
        if instance.PlaceOfSupply:
            PlaceOfSupply = instance.PlaceOfSupply.Name
        return PlaceOfSupply

    def get_LedgerDatas(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        expense_details = model.ExpenseDetails.objects.filter(CompanyID=CompanyID,ExpenseMasterID=instances.ExpenseMasterID,BranchID=instances.BranchID)
        ledger_ids = expense_details.values_list('Ledger', flat=True)
        lendger_instances = model.AccountLedger.objects.filter(id__in=ledger_ids)
        serialized = serializer.AccountLedgerListSerializer(lendger_instances, many=True, context={"CompanyID": CompanyID,
                                                                                    "PriceRounding": PriceRounding})
        return serialized.data


    def get_ExpenseDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        expense_details = model.ExpenseDetails.objects.filter(CompanyID=CompanyID,ExpenseMasterID=instances.ExpenseMasterID,BranchID=instances.BranchID).order_by('ExpenseDetailsID')
        serialized = ExpenseDetailsSerializer(expense_details,many=True,context = {"CompanyID": CompanyID,"PriceRounding":PriceRounding })

        return serialized.data 



class ExpenseDetailsSerializer(serializers.ModelSerializer):
    LedgerID = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    Total = serializers.SerializerMethodField()
    unq_id = serializers.SerializerMethodField()
    detailID = serializers.SerializerMethodField()
    class Meta:
        model = model.ExpenseDetails
        fields = ('id','unq_id','detailID','ExpenseDetailsID','ExpenseMasterID','LedgerID','Amount','TaxID','TaxableAmount','DiscountAmount',
            'TaxPerc','TaxAmount','NetTotal','Total','CreatedDate','UpdatedDate','CreatedUserID','VATPerc','VATAmount','IGSTPerc',
            'IGSTAmount','SGSTPerc','SGSTAmount','CGSTPerc','CGSTAmount','LedgerName',)


    def get_LedgerName(self, instance):
        CompanyID = self.context.get("CompanyID")
        Ledger = instance.Ledger
        return Ledger.LedgerName

    def get_LedgerID(self, instance):
        CompanyID = self.context.get("CompanyID")
        Ledger = instance.Ledger
        return Ledger.id

    def get_Total(self, instance):
        CompanyID = self.context.get("CompanyID")
        Total = instance.NetTotal
        return Total

    def get_unq_id(self, instance):
        CompanyID = self.context.get("CompanyID")
        unq_id = instance.id
        return unq_id

    def get_detailID(self, instance):
        detailID = 0
        return detailID

