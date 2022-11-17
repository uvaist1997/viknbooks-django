from rest_framework import serializers
from brands.models import POSHoldMaster, POSHoldDetails


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

    POSHoldDetails = serializers.SerializerMethodField()

    class Meta:
        model = POSHoldMaster
        fields = ('id','POSHoldMasterID','BranchID','Action','VoucherNo','InvoiceNo','Date','LedgerID',
            'PriceCategoryID','EmployeeID','SalesAccount',
            'HoldStatus','CustomerName','Address1','Address2','Address3','Notes','FinacialYearID',
            'TotalTax','NetTotal','BillDiscount','GrandTotal','RoundOff','CashReceived','CashAmount',
            'BankAmount','WarehouseID','TableID','SeatNumber','NoOfGuests','INOUT','TokenNumber','IsActive','CreatedDate','CreatedUserID','POSHoldDetails')


    def get_POSHoldDetails(self, instances):
        poshold_details = POSHoldDetails.objects.filter(POSHoldMasterID=instances.POSHoldMasterID,BranchID=instances.BranchID)
        serialized = POSHoldDetailsRestSerializer(poshold_details,many=True,)

        return serialized.data 




class POSHoldDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = POSHoldDetails
        fields = ('id','BranchID','ProductID','Qty','FreeQty',
            'UnitPrice','RateWithTax','CostPerPrice',
            'PriceListID','TaxID','TaxType','DiscountPerc','DiscountAmount','GrossAmount',
            'TaxableAmount','VATPerc','VATAmount','SGSTPerc','SGSTAmount',
            'CGSTPerc','CGSTAmount','IGSTPerc','IGSTAmount','NetAmount','Flavour')


class POSHoldDetailsRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = POSHoldDetails
        fields = ('id','POSHoldDetailsID','BranchID','Action','POSHoldMasterID','ProductID','Qty','FreeQty',
            'UnitPrice','RateWithTax','CostPerPrice',
            'PriceListID','TaxID','TaxType','DiscountPerc','DiscountAmount','GrossAmount','TaxableAmount',
            'VATPerc','VATAmount','SGSTPerc','SGSTAmount','CGSTPerc','CGSTAmount','IGSTPerc',
            'IGSTAmount','NetAmount','Flavour')