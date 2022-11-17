from rest_framework import serializers
from brands.models import PurchaseMaster, PurchaseDetails, AccountLedger, Product, Warehouse, PriceList, Unit, TaxCategory,PriceCategory
from api.v2.priceLists.serializers import PriceListRestSerializer



class PurchaseMasterRestSerializer(serializers.ModelSerializer):

    PurchaseDetails = serializers.SerializerMethodField()
    TotalGrossAmt = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseMaster
        fields = ('id','PurchaseMasterID','BranchID','Action','VoucherNo','RefferenceBillNo','Date',
            'VenderInvoiceDate','CreditPeriod','LedgerID','LedgerName',
            'PriceCategoryID','PriceCategoryName','EmployeeID','PurchaseAccount','PurchaseAccountName','CustomerName','Address1','Address2','Address3','is_customer',
            'Notes','FinacialYearID','TotalGrossAmt','TotalTax','NetTotal','AddlDiscPercent','AddlDiscAmt',
            'AdditionalCost','TotalDiscount','GrandTotal','RoundOff','TransactionTypeID','WarehouseID','WareHouseName','IsActive','CreatedDate','CreatedUserID',
            'TaxID','TaxType','VATAmount','SGSTAmount','CGSTAmount','IGSTAmount','TAX1Amount','TAX2Amount','TAX3Amount','BillDiscPercent','BillDiscAmt','Balance','DetailID','PurchaseDetails')


    def get_PurchaseDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = int(self.context.get("PriceRounding"))
        QtyRounding = self.context.get("QtyRounding")
        purchase_details = PurchaseDetails.objects.filter(CompanyID=CompanyID,PurchaseMasterID=instances.PurchaseMasterID,BranchID=instances.BranchID)
        serialized = PurchaseDetailsRestSerializer(purchase_details,many=True,context = {"CompanyID": CompanyID,
        "PriceRounding": PriceRounding, "QtyRounding" : QtyRounding })

        return serialized.data 


