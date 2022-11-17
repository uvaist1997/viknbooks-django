from rest_framework import serializers
from brands.models import PurchaseMaster


class PurchaseMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseMaster
        fields = ('id','BranchID','VoucherNo','InvoiceNo','RefferenceBillNo','Date',
        	'VenderInvoiceDate','CreditPeriod','LedgerID',
        	'PriceCategoryID','EmployeeID','PurchaseAccount','DeliveryMasterID','OrderMasterID','CustomerName',
            'Address1','Address2','Address3','Notes','OldTransactionID',
            'FinacialYearID','TotalTax','NetTotal','AdditionalCost','BillDiscount','GrandTotal',
            'RoundOff','CashAmount','BankAmount','WarehouseID','IsActive','CreatedDate','CreatedUserID')


class PurchaseMasterRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseMaster
        fields = ('id','PurchaseMasterID','BranchID','Action','VoucherNo','InvoiceNo','RefferenceBillNo','Date',
        	'VenderInvoiceDate','CreditPeriod','LedgerID',
        	'PriceCategoryID','EmployeeID','PurchaseAccount','DeliveryMasterID','OrderMasterID','CustomerName','Address1',
            'Address2','Address3','Notes','OldTransactionID','FinacialYearID','TotalTax','NetTotal',
            'AdditionalCost','BillDiscount','GrandTotal','RoundOff','CashAmount','BankAmount','WarehouseID','IsActive','CreatedDate','CreatedUserID')
