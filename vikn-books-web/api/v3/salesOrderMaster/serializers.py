from rest_framework import serializers
from brands.models import SalesOrderMaster


class SalesOrderMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalesOrderMaster
        fields = ('id','BranchID','VoucherNo','InvoiceNo','OrderNo','Date',
        	'CreditPeriod','LedgerID',
        	'PriceCategoryID','EmployeeID','SalesAccount','CustomerName',
            'Address1','Address2','Address3','Notes','OldTransactionID',
            'FinacialYearID','TotalTax','NetTotal','AdditionalCost','BillDiscount','GrandTotal',
            'RoundOff','CashReceived','CashAmount','BankAmount','WarehouseID','TableID','SeatNumber'
            ,'NoOfGuests','INOUT','TokenNumber','IsActive','IsInvoiced','CreatedDate','CreatedUserID')


class SalesOrderMasterRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalesOrderMaster
        fields = ('id','SalesOrderMasterID','BranchID','Action','VoucherNo','InvoiceNo','OrderNo','Date',
        	'CreditPeriod','LedgerID',
        	'PriceCategoryID','EmployeeID','SalesAccount','CustomerName','Address1',
            'Address2','Address3','Notes','OldTransactionID','FinacialYearID','TotalTax','NetTotal',
            'AdditionalCost','BillDiscount','GrandTotal','RoundOff','CashReceived','CashAmount','BankAmount','WarehouseID','TableID','SeatNumber',
            'NoOfGuests','INOUT','TokenNumber','IsActive','IsInvoiced','CreatedDate','CreatedUserID')
