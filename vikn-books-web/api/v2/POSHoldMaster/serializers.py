from rest_framework import serializers
from brands.models import POSHoldMaster


class POSHoldMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = POSHoldMaster
        fields = ('id','BranchID','VoucherNo','InvoiceNo','Date','LedgerID',
        	'PriceCategoryID','EmployeeID','SalesAccount',
        	'HoldStatus','CustomerName','Address1','Address2','Address3','Notes',
            'FinacialYearID','TotalTax','NetTotal','BillDiscount','GrandTotal',
            'RoundOff','CashReceived','CashAmount','BankAmount','WarehouseID','TableID',
            'SeatNumber','NoOfGuests','INOUT','TokenNumber','IsActive','CreatedDate','CreatedUserID')


class POSHoldMasterRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = POSHoldMaster
        fields = ('id','POSHoldMasterID','BranchID','Action','VoucherNo','InvoiceNo','Date','LedgerID',
        	'PriceCategoryID','EmployeeID','SalesAccount',
        	'HoldStatus','CustomerName','Address1','Address2','Address3','Notes','FinacialYearID',
            'TotalTax','NetTotal','BillDiscount','GrandTotal','RoundOff','CashReceived','CashAmount',
            'BankAmount','WarehouseID','TableID','SeatNumber','NoOfGuests','INOUT','TokenNumber','IsActive','CreatedDate','CreatedUserID')
