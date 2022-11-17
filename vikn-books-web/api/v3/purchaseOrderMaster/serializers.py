from rest_framework import serializers
from brands.models import PurchaseOrderMaster


class PurchaseOrderMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseOrderMaster
        fields = ('id','BranchID','VoucherNo','InvoiceNo','OrderNo','Date',
        	'CreditPeriod','LedgerID',
        	'PriceCategoryID','EmployeeID','PurchaseAccount','DeliveryMasterID','OrderMasterID','CustomerName',
            'Address1','Address2','Address3','Notes','OldTransactionID',
            'FinacialYearID','TotalTax','NetTotal','AdditionalCost','BillDiscount','GrandTotal',
            'RoundOff','CashAmount','BankAmount','WarehouseID','IsActive','CreatedDate','CreatedUserID')


class PurchaseOrderMasterRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseOrderMaster
        fields = ('id','PurchaseOrderMasterID','BranchID','Action','VoucherNo','InvoiceNo','OrderNo','Date',
        	'CreditPeriod','LedgerID',
        	'PriceCategoryID','EmployeeID','PurchaseAccount','DeliveryMasterID','OrderMasterID','CustomerName','Address1',
            'Address2','Address3','Notes','OldTransactionID','FinacialYearID','TotalTax','NetTotal',
            'AdditionalCost','BillDiscount','GrandTotal','RoundOff','CashAmount','BankAmount','WarehouseID','IsActive','CreatedDate','CreatedUserID')
