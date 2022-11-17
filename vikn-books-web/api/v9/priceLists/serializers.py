from sqlalchemy import false
from main.functions import converted_float, get_GeneralSettings
from rest_framework import serializers
from brands.models import OpeningStockDetails, PriceList, Product, PurchaseDetails, PurchaseOrderDetails, PurchaseReturnDetails, SalesDetails, SalesEstimateDetails, SalesOrderDetails, SalesReturnDetails, StockManagementDetails, StockPosting, StockTransferDetails, Unit, GeneralSettings, Batch
from api.v9.priceLists.functions import get_LastSalesPrice_PurchasePrice

class PriceListSerializer(serializers.ModelSerializer):

    class Meta:
        model = PriceList
        fields = ('id', 'BranchID', 'ProductID', 'UnitName', 'SalesPrice', 'PurchasePrice', 'MultiFactor', 'Barcode', 'AutoBarcode', 'SalesPrice1',
                  'SalesPrice2', 'SalesPrice3', 'CreatedDate', 'CreatedUserID', 'DefaultUnit', 'UnitInSales', 'UnitInPurchase', 'UnitInReports',)


class PriceListRestSerializer(serializers.ModelSerializer):
    SalesPrice = serializers.SerializerMethodField()
    SalesPrice1 = serializers.SerializerMethodField()
    SalesPrice2 = serializers.SerializerMethodField()
    SalesPrice3 = serializers.SerializerMethodField()
    PurchasePrice = serializers.SerializerMethodField()
    MRP = serializers.SerializerMethodField()
    MultiFactor = serializers.SerializerMethodField()
    detailID = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()
    BatchCode = serializers.SerializerMethodField()
    Rate = serializers.SerializerMethodField()

    class Meta:
        model = PriceList
        fields = ('id', 'PriceListID', 'BranchID', 'MRP', 'ProductID', 'UnitID', 'UnitName', 'SalesPrice', 'PurchasePrice', 'MultiFactor', 'Barcode', 'AutoBarcode', 'SalesPrice1', 'SalesPrice2', 'SalesPrice3', 'Action', 'CreatedDate', 'CreatedUserID', 'DefaultUnit', 'UnitInSales',
                  'UnitInPurchase', 'UnitInReports', 'detailID', 'BatchCode', 'Rate')

    def get_Rate(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        PurchasePrice = instances.PurchasePrice
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        PriceListID = instances.PriceListID
        try:
            LedgerID = self.context.get("LedgerID")
        except:
            LedgerID = 0
        check_EnableProductBatchWise = get_GeneralSettings(
            CompanyID, BranchID, "EnableProductBatchWise")
        if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
            if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PriceListID=PriceListID).exists():
                batch_ins = Batch.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PriceListID=PriceListID).first()
                PurchasePrice = batch_ins.PurchasePrice

        PurchasePrice = get_LastSalesPrice_PurchasePrice(
            "Purchase", PurchasePrice, CompanyID, BranchID, LedgerID, ProductID)
        return converted_float(PurchasePrice)
    
    
    def get_SalesPrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        try:
            LedgerID = self.context.get("LedgerID")
        except:
            LedgerID = 0

        PriceRounding = self.context.get("PriceRounding")
        SalesPrice = instances.SalesPrice
        BranchID = instances.BranchID
        ProductID = instances.ProductID
        PriceListID = instances.PriceListID
        check_EnableProductBatchWise = get_GeneralSettings(CompanyID,BranchID,"EnableProductBatchWise")

        # if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
        #     check_EnableProductBatchWise = GeneralSettings.objects.get(
        #         BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
        if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
            if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PriceListID=PriceListID).exists():
                batch_ins = Batch.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PriceListID=PriceListID).last()
                SalesPrice = batch_ins.SalesPrice
        
        SalesPrice = get_LastSalesPrice_PurchasePrice("Sales",SalesPrice,CompanyID,BranchID,LedgerID,ProductID)
        
        return converted_float(SalesPrice)

    def get_BatchCode(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        BatchCode = 0
        BranchID = instances.BranchID
        ProductID = instances.ProductID
        PriceListID = instances.PriceListID
        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
            check_EnableProductBatchWise = GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
            if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PriceListID=PriceListID).exists():
                    batch_ins = Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PriceListID=PriceListID).last()
                    BatchCode = batch_ins.BatchCode

        return str(BatchCode)

    def get_detailID(self, instances):

        detailID = 0

        return detailID

    def get_UnitName(self, instances):
        CompanyID = self.context.get("CompanyID")

        UnitID = instances.UnitID
        BranchID = instances.BranchID
        UnitName = ""
        if Unit.objects.filter(CompanyID=CompanyID, UnitID=UnitID).exists():
            UnitName = Unit.objects.get(
                CompanyID=CompanyID, UnitID=UnitID).UnitName

        return UnitName

    def get_SalesPrice1(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        SalesPrice1 = instances.SalesPrice1

        # SalesPrice1 = round(SalesPrice1,PriceRounding)

        return str(SalesPrice1)

    def get_SalesPrice2(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        SalesPrice2 = instances.SalesPrice2

        # SalesPrice2 = round(SalesPrice2,PriceRounding)

        return str(SalesPrice2)

    def get_SalesPrice3(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        SalesPrice3 = instances.SalesPrice3

        # SalesPrice3 = round(SalesPrice3,PriceRounding)

        return str(SalesPrice3)

    def get_MRP(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        MRP = instances.MRP

        # MRP = round(MRP,PriceRounding)

        return str(MRP)

    def get_PurchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        PurchasePrice = instances.PurchasePrice
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        PriceListID = instances.PriceListID
        try:
            LedgerID = self.context.get("LedgerID")
        except:
            LedgerID = 0
        check_EnableProductBatchWise = get_GeneralSettings(CompanyID,BranchID,"EnableProductBatchWise")
        if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
            if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PriceListID=PriceListID).exists():
                batch_ins = Batch.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PriceListID=PriceListID).first()
                PurchasePrice = batch_ins.PurchasePrice
        
        PurchasePrice = get_LastSalesPrice_PurchasePrice("Purchase",PurchasePrice,CompanyID,BranchID,LedgerID,ProductID)
        return converted_float(PurchasePrice)

    def get_MultiFactor(self, instances):

        PriceRounding = self.context.get("PriceRounding")
        MultiFactor = instances.MultiFactor

        # MultiFactor = round(MultiFactor,PriceRounding)

        return str(MultiFactor)


class SinglePriceListRestSerializer(serializers.ModelSerializer):
    SalesPrice = serializers.SerializerMethodField()
    SalesPrice1 = serializers.SerializerMethodField()
    SalesPrice2 = serializers.SerializerMethodField()
    SalesPrice3 = serializers.SerializerMethodField()
    PurchasePrice = serializers.SerializerMethodField()
    MRP = serializers.SerializerMethodField()
    MultiFactor = serializers.SerializerMethodField()
    detailID = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()
    BatchCode = serializers.SerializerMethodField()
    is_used_unit = serializers.SerializerMethodField()
    ReverseFactor = serializers.SerializerMethodField()

    class Meta:
        model = PriceList
        fields = ('id', 'PriceListID', 'BranchID', 'MRP', 'ProductID', 'UnitID', 'UnitName', 'SalesPrice', 'PurchasePrice', 'MultiFactor', 'Barcode', 'AutoBarcode', 'SalesPrice1', 'SalesPrice2', 'SalesPrice3', 'Action', 'CreatedDate', 'CreatedUserID', 'DefaultUnit', 'UnitInSales',
                  'UnitInPurchase', 'UnitInReports', 'detailID', 'BatchCode', 'is_used_unit', "ReverseFactor",)

    def get_ReverseFactor(self, instances):
        return ""
    
    def get_is_used_unit(self, instance):
        CompanyID = self.context.get("CompanyID")
        is_used_unit = False
        PriceListID = instance.PriceListID
        sales_details = SalesDetails.objects.filter(
            CompanyID=CompanyID, PriceListID=PriceListID)
        salesReturn_details = SalesReturnDetails.objects.filter(
            CompanyID=CompanyID, PriceListID=PriceListID)
        salesOrder_details = SalesOrderDetails.objects.filter(
            CompanyID=CompanyID, PriceListID=PriceListID)
        salesEstimate_details = SalesEstimateDetails.objects.filter(
            CompanyID=CompanyID, PriceListID=PriceListID)
        purchase_details = PurchaseDetails.objects.filter(
            CompanyID=CompanyID, PriceListID=PriceListID)
        purchaseReturn_details = PurchaseReturnDetails.objects.filter(
            CompanyID=CompanyID, PriceListID=PriceListID)
        purchaseOrder_details = PurchaseOrderDetails.objects.filter(
            CompanyID=CompanyID, PriceListID=PriceListID)
        openingStock_details = OpeningStockDetails.objects.filter(
            CompanyID=CompanyID, PriceListID=PriceListID)
        stockTransfer_details = StockTransferDetails.objects.filter(
            CompanyID=CompanyID, PriceListID=PriceListID)
        stockManagement_details = StockManagementDetails.objects.filter(
            CompanyID=CompanyID, PriceListID=PriceListID)
        if sales_details or salesReturn_details or salesOrder_details or salesEstimate_details or purchase_details or purchaseReturn_details or purchaseOrder_details or openingStock_details or stockTransfer_details or stockManagement_details:
            is_used_unit = True
        return is_used_unit
        
    
    
    def get_SalesPrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        SalesPrice = instances.SalesPrice

        SalesPrice = round(SalesPrice, PriceRounding)

        return converted_float(SalesPrice)

    def get_BatchCode(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        BatchCode = 0
        BranchID = instances.BranchID
        ProductID = instances.ProductID
        PriceListID = instances.PriceListID
        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
            check_EnableProductBatchWise = GeneralSettings.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
            if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PriceListID=PriceListID).exists():
                    batch_ins = Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PriceListID=PriceListID).last()
                    BatchCode = batch_ins.BatchCode

        return str(BatchCode)

    def get_detailID(self, instances):

        detailID = 0

        return detailID

    def get_UnitName(self, instances):
        CompanyID = self.context.get("CompanyID")

        UnitID = instances.UnitID
        BranchID = instances.BranchID
        UnitName = ""
        if Unit.objects.filter(CompanyID=CompanyID, UnitID=UnitID).exists():
            UnitName = Unit.objects.get(
                CompanyID=CompanyID, UnitID=UnitID).UnitName

        return UnitName

    def get_SalesPrice1(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        SalesPrice1 = instances.SalesPrice1

        SalesPrice1 = round(SalesPrice1, PriceRounding)

        return str(SalesPrice1)

    def get_SalesPrice2(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        SalesPrice2 = instances.SalesPrice2

        SalesPrice2 = round(SalesPrice2, PriceRounding)

        return str(SalesPrice2)

    def get_SalesPrice3(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        SalesPrice3 = instances.SalesPrice3

        SalesPrice3 = round(SalesPrice3, PriceRounding)

        return str(SalesPrice3)

    def get_MRP(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        MRP = instances.MRP

        MRP = round(MRP, PriceRounding)

        return str(MRP)

    def get_PurchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        PurchasePrice = instances.PurchasePrice

        PurchasePrice = round(PurchasePrice, PriceRounding)

        return converted_float(PurchasePrice)

    def get_MultiFactor(self, instances):

        PriceRounding = self.context.get("PriceRounding")
        MultiFactor = instances.MultiFactor

        MultiFactor = round(MultiFactor, PriceRounding)

        return str(MultiFactor)


class ListSerializer(serializers.Serializer):

    BranchID = serializers.IntegerField()
    ProductID = serializers.IntegerField()
