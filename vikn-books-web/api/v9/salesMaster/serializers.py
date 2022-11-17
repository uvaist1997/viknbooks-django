from rest_framework import serializers
from brands.models import SalesMaster


class SalesMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalesMaster
        fields = ('id','BranchID','Action','VoucherNo','InvoiceNo','Date',
            'CreditPeriod','LedgerID',
            'PriceCategoryID','EmployeeID','SalesAccount','CustomerName','Address1','Address2','Address3',
            'Notes','FinacialYearID','TotalGrossAmt','AddlDiscPercent','AddlDiscAmt','TotalDiscount','TotalTax',
            'NetTotal','AdditionalCost','GrandTotal','RoundOff','CashReceived','CashAmount','BankAmount','WarehouseID','TableID','SeatNumber','NoOfGuests'
            ,'INOUT','TokenNumber','CardTypeID','CardNumber','IsActive','IsPosted','SalesType','CreatedDate','CreatedUserID')


class SalesMasterRestSerializer(serializers.ModelSerializer):


    class Meta:
        model = SalesMaster
        fields = ('id','SalesMasterID','BranchID','Action','VoucherNo','InvoiceNo','Date',
            'CreditPeriod','LedgerID',
            'PriceCategoryID','EmployeeID','SalesAccount','CustomerName','Address1','Address2','Address3',
            'Notes','FinacialYearID','TotalGrossAmt','AddlDiscPercent','AddlDiscAmt','TotalDiscount','TotalTax',
            'NetTotal','AdditionalCost','GrandTotal','RoundOff','CashReceived','CashAmount','BankAmount','WarehouseID','TableID','SeatNumber','NoOfGuests'
            ,'INOUT','TokenNumber','CardTypeID','CardNumber','IsActive','IsPosted','SalesType','CreatedDate','CreatedUserID')

