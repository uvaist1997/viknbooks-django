from rest_framework import serializers
from brands.models import PurchaseOrderMaster, PurchaseOrderDetails


class PurchaseOrderMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseOrderMaster
        fields = ('id','BranchID','Action','VoucherNo','OrderNo','Date',
            'CreditPeriod','LedgerID',
            'PriceCategoryID','EmployeeID','PurchaseAccount','DeliveryMasterID','OrderMasterID','CustomerName','Address1',
            'Address2','Address3','Notes','FinacialYearID','TotalTax','NetTotal','AdditionalCost',
            'BillDiscount','GrandTotal','RoundOff','IsActive',)


class PurchaseOrderMasterRestSerializer(serializers.ModelSerializer):

    PurchaseOrderDetails = serializers.SerializerMethodField()
    DetailID = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderMaster
        fields = ('id','PurchaseOrderMasterID','BranchID','Action','VoucherNo','OrderNo','Date',
        	'CreditPeriod','LedgerID','LedgerName',
        	'PriceCategoryID','EmployeeID','PurchaseAccount','DeliveryMasterID','OrderMasterID','CustomerName','Address1',
            'Address2','Address3','Notes','FinacialYearID','TotalTax','NetTotal','AdditionalCost',
            'BillDiscount','GrandTotal','RoundOff','IsActive','CreatedDate','UpdatedDate','CreatedUserID','PurchaseOrderDetails')


    def get_PurchaseOrderDetails(self, instances):
        DataBase = self.context.get("DataBase")

        purchaseOrder_details = PurchaseOrderDetails.objects.filter(PurchaseOrderMasterID=instances.PurchaseOrderMasterID,BranchID=instances.BranchID)
        serialized = PurchaseOrderDetailsRestSerializer(purchaseOrder_details,many=True,)

        return serialized.data


    def get_DetailID(self, instances):

        return ""


    def get_LedgerName(self, instances):
        DataBase = self.context.get("DataBase")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(LedgerID=LedgerID,BranchID=BranchID)

        LedgerName = ledger.LedgerName

        return LedgerName


class PurchaseOrderDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseOrderDetails
        fields = ('id','BranchID','DeliveryDetailsID','OrederDetailsID','ProductID',
            'Qty','FreeQty','UnitPrice',
            'RateWithTax','CostPerPrice','PriceListID','TaxID','TaxType','DiscountPerc',
            'DiscountAmount','GrossAmount','TaxableAmount','VATPerc','VATAmount',
            'SGSTPerc','SGSTAmount','CGSTPerc','CGSTAmount','IGSTPerc','IGSTAmount',
            'NetAmount')


class PurchaseOrderDetailsRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseOrderDetails
        fields = ('id','PurchaseOrderDetailsID','BranchID','Action','BatchID','PurchaseOrderMasterID','DeliveryDetailsID','OrederDetailsID',
            'ProductID','Qty','FreeQty',
            'UnitPrice','RateWithTax','CostPerPrice','PriceListID','TaxID','TaxType','DiscountPerc',
            'DiscountAmount','GrossAmount','TaxableAmount','VATPerc','VATAmount','SGSTPerc','SGSTAmount',
            'CGSTPerc','CGSTAmount','IGSTPerc','IGSTAmount','NetAmount')
