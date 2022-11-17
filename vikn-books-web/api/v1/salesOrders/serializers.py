from rest_framework import serializers
from brands.models import SalesOrderMaster, SalesOrderDetails


class SalesOrderMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalesOrderMaster
        fields = ('id','BranchID','Action','VoucherNo','OrderNo','Date',
            'CreditPeriod','LedgerID',
            'PriceCategoryID','EmployeeID','SalesAccount','CustomerName','Address1',
            'Address2','Address3','Notes','FinacialYearID','TotalTax','NetTotal','AdditionalCost',
            'BillDiscount','GrandTotal','RoundOff','CashReceived','CashAmount','BankAmount','WarehouseID','TableID','SeatNumber','NoOfGuests',
            'INOUT','TokenNumber','IsActive','IsInvoiced','CreatedUserID')


class SalesOrderMasterRestSerializer(serializers.ModelSerializer):

    SalesOrderDetails = serializers.SerializerMethodField()
    DetailID = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()

    class Meta:
        model = SalesOrderMaster
        fields = ('id','SalesOrderMasterID','BranchID','Action','VoucherNo','OrderNo','Date',
        	'CreditPeriod','LedgerID','LedgerName',
        	'PriceCategoryID','EmployeeID','SalesAccount','CustomerName','Address1',
            'Address2','Address3','Notes','FinacialYearID','TotalTax','NetTotal','AdditionalCost',
            'BillDiscount','GrandTotal','RoundOff','CashReceived','CashAmount','BankAmount','WarehouseID','TableID','SeatNumber','NoOfGuests',
            'INOUT','TokenNumber','IsActive','IsInvoiced','CreatedDate','UpdatedDate','CreatedUserID','SalesOrderDetails')


    def get_SalesOrderDetails(self, instances):
        DataBase = self.context.get("DataBase")

        salesOrder_details = SalesOrderDetails.objects.filter(SalesOrderMasterID=instances.SalesOrderMasterID,BranchID=instances.BranchID)
        serialized = SalesOrderDetailsRestSerializer(salesOrder_details,many=True,)

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



class SalesOrderDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalesOrderDetails
        fields = ('id','BranchID','Action','SalesOrderMasterID','DeliveryDetailsID','OrderDetailsID','ProductID',
            'Qty','FreeQty','UnitPrice',
            'RateWithTax','CostPerPrice','PriceListID','TaxID','TaxType','DiscountPerc','DiscountAmount',
            'GrossAmount','TaxableAmount','VATPerc','VATAmount','SGSTPerc','SGSTAmount','CGSTPerc',
            'CGSTAmount','IGSTPerc','IGSTAmount','NetAmount','Flavour','CreatedUserID')


class SalesOrderDetailsRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalesOrderDetails
        fields = ('id','SalesOrderDetailsID','BranchID','Action','SalesOrderMasterID','DeliveryDetailsID','OrderDetailsID','ProductID',
            'Qty','FreeQty','UnitPrice',
            'RateWithTax','CostPerPrice','PriceListID','TaxID','TaxType','DiscountPerc','DiscountAmount',
            'GrossAmount','TaxableAmount','VATPerc','VATAmount','SGSTPerc','SGSTAmount','CGSTPerc',
            'CGSTAmount','IGSTPerc','IGSTAmount','NetAmount','Flavour','CreatedDate','UpdatedDate','CreatedUserID')