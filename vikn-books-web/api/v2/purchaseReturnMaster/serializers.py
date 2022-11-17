from rest_framework import serializers
from brands.models import PurchaseReturnMaster


class PurchaseReturnMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseReturnMaster
        fields = ('id','BranchID','VoucherNo','InvoiceNo','RefferenceBillNo','RefferenceBillDate','VenderInvoiceDate',
        	'CreditPeriod','LedgerID',
        	'PriceCategoryID','EmployeeID','PurchaseAccount','DeliveryMasterID','OrderMasterID','CustomerName',
            'Address1','Address2','Address3','Notes','OldTransactionID',
            'FinacialYearID','TotalTax','NetTotal','AdditionalCost','BillDiscount','GrandTotal',
            'RoundOff','CashAmount','BankAmount','WarehouseID','IsActive','CreatedDate','CreatedUserID')


class PurchaseReturnMasterRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseReturnMaster
        fields = ('id','PurchaseReturnMasterID','BranchID','Action','VoucherNo','InvoiceNo','RefferenceBillNo','RefferenceBillDate',
        	'VenderInvoiceDate','CreditPeriod','LedgerID',
        	'PriceCategoryID','EmployeeID','PurchaseAccount','DeliveryMasterID','OrderMasterID','CustomerName','Address1',
            'Address2','Address3','Notes','OldTransactionID','FinacialYearID','TotalTax','NetTotal',
            'AdditionalCost','BillDiscount','GrandTotal','RoundOff','CashAmount','BankAmount','WarehouseID','IsActive','CreatedDate','CreatedUserID')
