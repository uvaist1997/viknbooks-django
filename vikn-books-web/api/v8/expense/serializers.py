from rest_framework import serializers
from brands import models as model
from rest_framework.fields import CurrentUserDefault
from api.v8.accountLedgers import serializers as serializer


class ExpenseMasterSerializer(serializers.ModelSerializer):
    SupplierName = serializers.SerializerMethodField()
    PlaceOfSupplyName = serializers.SerializerMethodField()
    ExpenseDetails = serializers.SerializerMethodField()
    Supplier = serializers.SerializerMethodField()
    LedgerDatas = serializers.SerializerMethodField()
    class Meta:
        model = model.ExpenseMaster
        fields = ('id','BranchID','VoucherNo','SupplierName','Supplier','Date','GST_Treatment','PlaceOfSupply','PlaceOfSupplyName','InvoiceNo','TaxType','TaxTypeID','Notes',
            'PaymentMode','PaymentID','Amount','BillDiscPercent','BillDiscAmount','TotalGrossAmt','TotalTaxableAmount','TotalDiscount',
            'TotalTaxAmount','TotalNetAmount','RoundOff','GrandTotal','TaxInclusive','TotalVATAmount','TotalIGSTAmount',
            'TotalSGSTAmount','TotalCGSTAmount','ExpenseDetails','LedgerDatas','TaxNo')


    def get_Supplier(self, instance):
        CompanyID = self.context.get("CompanyID")
        Supplier = instance.Supplier
        return Supplier.id

    def get_SupplierName(self, instance):
        CompanyID = self.context.get("CompanyID")
        Supplier = instance.Supplier
        return Supplier.LedgerName

    def get_PlaceOfSupplyName(self, instance):
        CompanyID = self.context.get("CompanyID")
        PlaceOfSupply = instance.PlaceOfSupply
        return PlaceOfSupply.Name

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
    Total = serializers.SerializerMethodField()
    unq_id = serializers.SerializerMethodField()
    detailID = serializers.SerializerMethodField()
    class Meta:
        model = model.ExpenseDetails
        fields = ('id','unq_id','detailID','ExpenseDetailsID','ExpenseMasterID','LedgerID','Amount','TaxID','TaxableAmount','DiscountAmount',
            'TaxPerc','TaxAmount','NetTotal','Total','CreatedDate','UpdatedDate','CreatedUserID','VATPerc','VATAmount','IGSTPerc',
            'IGSTAmount','SGSTPerc','SGSTAmount','CGSTPerc','CGSTAmount',)


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

