from rest_framework import serializers
from brands.models import Batch,PriceList,Product,StockManagementMaster, StockManagementDetails
from main.functions import converted_float, get_ProductStock
from api.v10.priceLists.serializers import PriceListRestSerializer
from api.v10.workOrder.serializers import Batch_ListSerializer


class StockManagementSerializer(serializers.ModelSerializer):
    StockManagement_Details = serializers.SerializerMethodField()
    StockManageType = serializers.SerializerMethodField()
    ProductList = serializers.SerializerMethodField()

    class Meta:
        model = StockManagementMaster
        fields = ('id','StockMasterID','VoucherNo','Date','WarehouseID','Notes','TotalQty','GrandTotal',
                  'StockManageType', 'StockManagement_Details', 'ProductList', 'TotalExcessOrShortage','TotalExcessAmount','TotalShortageAmount')


    def get_ProductList(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        StockMasterID = instances.StockMasterID
        sales_details = StockManagementDetails.objects.filter(
            CompanyID=CompanyID, StockMasterID=StockMasterID, BranchID=BranchID)

        product_ids = sales_details.values_list('ProductID', flat=True)
        produc_instances = Product.objects.filter(
            CompanyID=CompanyID, ProductID__in=product_ids)
        ProductList = []
        for p in produc_instances:
            BatchCode = ""
            if Batch.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ProductID=p.ProductID).exists():
                BatchCode = Batch.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ProductID=p.ProductID).order_by('BatchCode').first().BatchCode
            ProductList.append({
                "id": p.id,
                "product_id": p.id,
                "ProductCode": p.ProductCode,
                "ProductName": p.ProductName,
                "ProductID": p.ProductID,
                "BatchCode": BatchCode,
            })

        return ProductList
    
    
    def get_StockManagement_Details(self, instance):
        CompanyID = self.context.get("CompanyID")
        StockManagement_Details = StockManagementDetails.objects.filter(CompanyID=CompanyID,StockMasterID=instance.StockMasterID,BranchID=instance.BranchID).order_by('StockMasterID')
        serialized = StockManagementDetailsSerializer(StockManagement_Details,many=True,context={"CompanyID": CompanyID })
        return serialized.data
    
    def get_StockManageType(self,instance):
        StockManageType = ""
        # StockType = instance.StockType
        # if StockType == "0":
        #     StockManageType = "Excess Stock"
        # elif StockType == "1":
        #     StockManageType = "Shortage Stock"
        # elif StockType == "2":
        #     StockManageType = "Stock Adjustments"
        return StockManageType
        



class StockManagementDetailsSerializer(serializers.ModelSerializer):
    Rate = serializers.SerializerMethodField()
    Stock = serializers.SerializerMethodField()
    UnitList = serializers.SerializerMethodField()
    Qty = serializers.SerializerMethodField()
    Amount = serializers.SerializerMethodField()
    PurchasePrice = serializers.SerializerMethodField()
    unq_id = serializers.SerializerMethodField()
    detailID = serializers.SerializerMethodField()
    ProductCodeVal = serializers.SerializerMethodField()
    BatchList = serializers.SerializerMethodField()
    NetAmount = serializers.SerializerMethodField()
    ExcessAmount = serializers.SerializerMethodField()
    ShortageAmount = serializers.SerializerMethodField()
    Barcode = serializers.SerializerMethodField()
    
    class Meta:
        model = StockManagementDetails
        fields = ('id','StockDetailsID','StockMasterID','ProductID','PriceListID','Qty','Excess_or_Shortage','CostPerItem','Rate'
                  , 'Stock', 'UnitList', 'Amount', 'PurchasePrice', 'BatchCode', 'unq_id', 'detailID', 'ProductCodeVal', 'BatchList', 'NetAmount',
                  'ExcessAmount', 'ShortageAmount', 'Barcode', 'is_damage')
        
    def get_Barcode(self, instance):
        Barcode = ""
        CompanyID = self.context.get("CompanyID")
        PriceListID = instance.PriceListID
        if PriceList.objects.filter(CompanyID=CompanyID,PriceListID=PriceListID).exists():
            Barcode = PriceList.objects.filter(
                CompanyID=CompanyID, PriceListID=PriceListID).first().Barcode
        return str(Barcode)
    
    def get_unq_id(self, instance):
        unq_id = instance.id
        return str(unq_id)
    
    def get_ProductCodeVal(self, instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = instance.ProductID
        product = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID)
        ProductCode = product.ProductCode
        return ProductCode
    
    def get_detailID(self, instance):
        return 0
    
    def get_PurchasePrice(self, instance):
        # CompanyID = self.context.get("CompanyID")
        # PriceListID = instance.PriceListID
        # BranchID = instance.BranchID
        # PurchasePrice = 0
        # if PriceList.objects.filter(CompanyID=CompanyID,PriceListID=PriceListID).exists():
        #     PurchasePrice = PriceList.objects.filter(CompanyID=CompanyID,PriceListID=PriceListID).first().PurchasePrice
        PurchasePrice = instance.CostPerItem
        return converted_float(PurchasePrice)
    
    def get_Amount(self, instance):
        Rate = instance.CostPerItem
        Qty = instance.Qty
        Amount = converted_float(Rate) * converted_float(Qty)
        return converted_float(Amount)
    
    def get_Rate(self, instance):
        Rate = instance.CostPerItem
        return converted_float(Rate)
    
    def get_Qty(self, instance):
        Qty = instance.Qty
        return converted_float(Qty)
    
    def get_Stock(self, instance):
        CompanyID = self.context.get("CompanyID")
        Stock = instance.Stock
        # BranchID = instance.BranchID
        # StockMasterID = instance.StockMasterID
        # BatchCode = instance.BatchCode
        # WarehouseID = StockManagementMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,StockMasterID=StockMasterID).first().WarehouseID
        # Stock = get_ProductStock(CompanyID,BranchID,ProductID,WarehouseID,BatchCode)
        return converted_float(Stock)
    
    def get_UnitList(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = sales_details.ProductID
        UnitList = PriceList.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID)
        serialized = PriceListRestSerializer(UnitList, many=True, context={
                                             "CompanyID": CompanyID, "PriceRounding": PriceRounding})
        return serialized.data
    
    def get_BatchList(self, sales_details):
        BatchList = []
        CompanyID = self.context.get("CompanyID")
        # PriceRounding = int(self.context.get("PriceRounding"))
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
            batch_details = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
            batchList = Batch_ListSerializer(batch_details, many=True, context={
                "CompanyID": CompanyID})
            BatchList = batchList.data
        return BatchList
    
    def get_NetAmount(self, instance):
        Rate = instance.CostPerItem
        # Qty = instance.Qty
        Excess_or_Shortage = instance.Excess_or_Shortage
        NetAmount = converted_float(Excess_or_Shortage) * converted_float(Rate)
        return converted_float(NetAmount)
    
    def get_ExcessAmount(self, instance):
        Rate = instance.CostPerItem
        # Qty = instance.Qty
        Excess_or_Shortage = instance.Excess_or_Shortage
        ExcessAmount = 0
        if converted_float(Excess_or_Shortage) > 0:
            ExcessAmount = converted_float(
                Excess_or_Shortage) * converted_float(Rate)
        return converted_float(ExcessAmount)

    def get_ShortageAmount(self, instance):
        Rate = instance.CostPerItem
        # Qty = instance.Qty
        Excess_or_Shortage = instance.Excess_or_Shortage
        ShortageAmount = 0
        if converted_float(Excess_or_Shortage) < 0:
            ShortageAmount = converted_float(
                Excess_or_Shortage) * converted_float(Rate)
        return converted_float(ShortageAmount)
    
    
