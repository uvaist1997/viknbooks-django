from rest_framework import serializers
from brands.models import SalesReturnMaster


class SalesReturnMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalesReturnMaster
        fields = ('id','BranchID','VoucherNo','InvoiceNo','RefferenceBillNo','RefferenceBillDate','VoucherDate',
        	'CreditPeriod','LedgerID',
        	'PriceCategoryID','EmployeeID','SalesAccount','DeliveryMasterID','OrderMasterID','CustomerName',
            'Address1','Address2','Address3','Notes','OldTransactionID',
            'FinacialYearID','TotalTax','NetTotal','AdditionalCost','BillDiscount','GrandTotal',
            'RoundOff','CashReceived','CashAmount','BankAmount','WarehouseID','TableID'
            ,'SeatNumber','NoOfGuests','INOUT','TokenNumber','CardTypeID','IsActive','IsPosted'
            ,'SalesType','CreatedDate','CreatedUserID')


class SalesReturnMasterRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalesReturnMaster
        fields = ('id','SalesReturnMasterID','BranchID','Action','VoucherNo','InvoiceNo','RefferenceBillNo','RefferenceBillDate',
        	'VoucherDate','CreditPeriod','LedgerID',
        	'PriceCategoryID','EmployeeID','SalesAccount','DeliveryMasterID','OrderMasterID','CustomerName','Address1',
            'Address2','Address3','Notes','OldTransactionID','FinacialYearID','TotalTax','NetTotal',
            'AdditionalCost','BillDiscount','GrandTotal','RoundOff','CashReceived','CashAmount','BankAmount','WarehouseID','TableID'
            ,'SeatNumber','NoOfGuests','INOUT','TokenNumber','CardTypeID','IsActive','IsPosted'
            ,'SalesType','CreatedDate','CreatedUserID')
