from rest_framework import serializers
from brands.models import ProductGroup, PurchaseMaster, PurchaseDetails, AccountLedger, Product, Warehouse, PriceList, Unit, TaxCategory, PriceCategory, WorkOrderMaster, Batch, WorkOrderDetails
from api.v10.priceLists.serializers import PriceListRestSerializer
from main.functions import converted_float, get_GeneralSettings
from django.db.models import Q, Sum, F

class WorkOrderSerializer(serializers.ModelSerializer):
    BatchCode = serializers.SerializerMethodField()
    WorkOrderDetails = serializers.SerializerMethodField()
    ExpiryDate = serializers.SerializerMethodField()
    ManufactureDate = serializers.SerializerMethodField()
    WareHouseName = serializers.SerializerMethodField()
    ProductName = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()
    Barcode = serializers.SerializerMethodField()
    ProductCode = serializers.SerializerMethodField()
    AutoBarcode = serializers.SerializerMethodField()
    ProductQty = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    is_inclusive = serializers.SerializerMethodField()
    BatchPurchasePrice = serializers.SerializerMethodField()
    UnitList = serializers.SerializerMethodField()
    ProductList = serializers.SerializerMethodField()
    ProductListMaster = serializers.SerializerMethodField()
    BatchList = serializers.SerializerMethodField()
    sum_salesPrice = serializers.SerializerMethodField()
    sum_cost = serializers.SerializerMethodField()
    detailID = serializers.SerializerMethodField()
    VATPercMaster = serializers.SerializerMethodField()
    IGSTPercMaster = serializers.SerializerMethodField()
    InclusiveMaster = serializers.SerializerMethodField()
    StandardSalesPrice = serializers.SerializerMethodField()
    SalesPrice1 = serializers.SerializerMethodField()
    SalesPrice2 = serializers.SerializerMethodField()
    SalesPrice3 = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkOrderMaster
        fields = ('id', 'WorkOrderMasterID', 'BatchPurchasePrice', 'BranchID', 'UnitList', 'Action',
                    'VoucherNo', 'Date', 'WareHouseID', 'WareHouseName', 'Notes', 'ProductID', 'ProductName',
                     'ManufactureDate', 'ExpiryDate','ProductQty', 'CostPerPrice', 'UnitPrice', 'PriceListID',
                      'Barcode', 'AutoBarcode', 'UnitName', 'Amount', 'Weight', 'TotalQty', 'GrandTotal', 
                      'IsActive', 'CreatedDate', 'UpdatedDate', 'CreatedUserID', 'BatchCode','BatchList',
                    'is_inclusive', 'WorkOrderDetails','CostSum','GrandCostSum','ProductCode','ProductList',
                    'ProductListMaster','sum_salesPrice','sum_cost','detailID','VATPercMaster','IGSTPercMaster',
                    'InclusiveMaster','PriceCategoryID','StandardSalesPrice','SalesPrice1','SalesPrice2','SalesPrice3')

    
    def get_StandardSalesPrice(self,instance):
        CompanyID = self.context.get("CompanyID")
        PriceListID = instance.PriceListID
        StandardSalesPrice = 0
        if PriceList.objects.filter(CompanyID=CompanyID,PriceListID=PriceListID).exists():
            StandardSalesPrice = PriceList.objects.filter(CompanyID=CompanyID,PriceListID=PriceListID).first().SalesPrice
        return StandardSalesPrice

    
    def get_SalesPrice1(self,instance):
        CompanyID = self.context.get("CompanyID")
        PriceListID = instance.PriceListID
        SalesPrice1 = 0
        if PriceList.objects.filter(CompanyID=CompanyID,PriceListID=PriceListID).exists():
            SalesPrice1 = PriceList.objects.filter(CompanyID=CompanyID,PriceListID=PriceListID).first().SalesPrice1
        return SalesPrice1

    def get_SalesPrice2(self,instance):
        CompanyID = self.context.get("CompanyID")
        PriceListID = instance.PriceListID
        SalesPrice2 = 0
        if PriceList.objects.filter(CompanyID=CompanyID,PriceListID=PriceListID).exists():
            SalesPrice2 = PriceList.objects.filter(CompanyID=CompanyID,PriceListID=PriceListID).first().SalesPrice2
        return SalesPrice2


    def get_SalesPrice3(self,instance):
        CompanyID = self.context.get("CompanyID")
        PriceListID = instance.PriceListID
        SalesPrice3 = 0
        if PriceList.objects.filter(CompanyID=CompanyID,PriceListID=PriceListID).exists():
            SalesPrice3 = PriceList.objects.filter(CompanyID=CompanyID,PriceListID=PriceListID).first().SalesPrice3
        return SalesPrice3

    def get_VATPercMaster(self,instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = instance.ProductID
        VATPercMaster = 0
        VatID = Product.objects.get(CompanyID=CompanyID,ProductID=ProductID).VatID
        if TaxCategory.objects.filter(CompanyID=CompanyID,TaxID=VatID).exists():
            VATPercMaster = TaxCategory.objects.get(CompanyID=CompanyID,TaxID=VatID).SalesTax
        return VATPercMaster

    def get_InclusiveMaster(self,instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = instance.ProductID
        InclusiveMaster = Product.objects.get(CompanyID=CompanyID,ProductID=ProductID).is_inclusive
        return InclusiveMaster

    def get_IGSTPercMaster(self,instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = instance.ProductID
        IGSTPercMaster = 0
        GST = Product.objects.get(CompanyID=CompanyID,ProductID=ProductID).GST
        if TaxCategory.objects.filter(CompanyID=CompanyID,TaxID=GST).exists():
            IGSTPercMaster = TaxCategory.objects.get(CompanyID=CompanyID,TaxID=GST).SalesTax
        return IGSTPercMaster
    
    
    def get_sum_salesPrice(self, instance):
        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        WorkOrderMasterID = instance.WorkOrderMasterID
        workOrder_details = WorkOrderDetails.objects.filter(
            CompanyID=CompanyID, WorkOrderMasterID=WorkOrderMasterID, BranchID=BranchID)
        sum_salesPrice = workOrder_details.aggregate(Sum('UnitPrice'))
        sum_salesPrice = sum_salesPrice['UnitPrice__sum']
        return sum_salesPrice

    def get_detailID(self,instance):
        detailID = 0
        return detailID

    def get_sum_cost(self, instance):
        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        WorkOrderMasterID = instance.WorkOrderMasterID
        workOrder_details = WorkOrderDetails.objects.filter(
            CompanyID=CompanyID, WorkOrderMasterID=WorkOrderMasterID, BranchID=BranchID)
        sum_cost = workOrder_details.aggregate(Sum('CostPerPrice'))
        sum_cost = sum_cost['CostPerPrice__sum']
        return sum_cost


    def get_UnitList(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = instance.ProductID
        BranchID = instance.BranchID
        UnitList = PriceList.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)
        serialized = PriceListRestSerializer(UnitList, many=True, context={
                                             "CompanyID": CompanyID, "PriceRounding": PriceRounding})
        return serialized.data

    def get_BatchPurchasePrice(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = instance.ProductID
        BranchID = instance.BranchID
        BatchCode = instance.BatchCode
        PriceListID = instance.PriceListID
        if Batch.objects.filter(BranchID=BranchID, BatchCode=BatchCode, CompanyID=CompanyID).exists():
            BatchPurchasePrice = Batch.objects.get(
                BranchID=BranchID, BatchCode=BatchCode, CompanyID=CompanyID).PurchasePrice
        else:
            BatchPurchasePrice = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID).PurchasePrice
        return BatchPurchasePrice

    def get_ManufactureDate(self, instance):
        date = ""
        if instance.ManufactureDate:
            date = instance.ManufactureDate

        return date

    def get_ExpiryDate(self, instance):
        date = ""
        if instance.ExpiryDate:
            date = instance.ExpiryDate

        return date

    def get_is_inclusive(self, instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = instance.ProductID
        BranchID = instance.BranchID
        is_inclusive = False
        if Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID).exists():
            product_ins = Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID)
            VatID = product_ins.VatID
            GST = product_ins.GST
            Tax1 = product_ins.Tax1
            Tax2 = product_ins.Tax2
            Tax3 = product_ins.Tax3
            VatInclusive = False
            GSTInclusive = False
            Tax1Inclusive = False
            Tax2Inclusive = False
            Tax3Inclusive = False

            if VatID:
                VatInclusive = TaxCategory.objects.get(
                    CompanyID=CompanyID, TaxID=VatID, BranchID=BranchID).Inclusive
            if GST:
                GSTInclusive = TaxCategory.objects.get(
                    CompanyID=CompanyID, TaxID=GST, BranchID=BranchID).Inclusive
            if Tax1:
                Tax1Inclusive = TaxCategory.objects.get(
                    CompanyID=CompanyID, TaxID=Tax1, BranchID=BranchID).Inclusive
            if Tax2:
                Tax2Inclusive = TaxCategory.objects.get(
                    CompanyID=CompanyID, TaxID=Tax2, BranchID=BranchID).Inclusive
            if Tax3:
                Tax3Inclusive = TaxCategory.objects.get(
                    CompanyID=CompanyID, TaxID=Tax3, BranchID=BranchID).Inclusive

            if VatInclusive == True or GSTInclusive == True or Tax1Inclusive == True or Tax2Inclusive == True or Tax2Inclusive == True:
                is_inclusive = True

        return is_inclusive

    def get_WareHouseName(self, instance):
        CompanyID = self.context.get("CompanyID")
        WareHouseID = instance.WareHouseID
        BranchID = instance.BranchID
        WareHouseName = ""
        if Warehouse.objects.filter(CompanyID=CompanyID, BranchID=BranchID, WarehouseID=WareHouseID).exists():
            WareHouseName = Warehouse.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, WarehouseID=WareHouseID).WarehouseName

        return WareHouseName

    def get_ProductQty(self, instance):
        PriceRounding = self.context.get("PriceRounding")
        ProductQty = instance.ProductQty

        return converted_float(ProductQty)

    def get_GrandTotal(self, instance):
        PriceRounding = self.context.get("PriceRounding")
        GrandTotal = instance.GrandTotal

        return converted_float(GrandTotal)

    def get_ProductName(self, instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = instance.ProductID
        BranchID = instance.BranchID
        ProductName = ""
        if Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID).exists():
            ProductName = Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID).ProductName

        return ProductName

    def get_ProductCode(self, instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = instance.ProductID
        BranchID = instance.BranchID
        ProductCode = ""
        if Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID).exists():
            ProductCode = Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID).ProductCode

        return ProductCode

    def get_UnitName(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceListID = instance.PriceListID
        BranchID = instance.BranchID
        UnitName = ""
        if PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID).UnitID
            UnitName = Unit.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, UnitID=UnitID).UnitName

        return UnitName

    def get_ProductListMaster(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        produc_instances = Product.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID).first()
        ProductList = []
        ProductList.append({
            "ProductName": produc_instances.ProductName,
            "ProductID": produc_instances.ProductID,
        })

        return ProductList

    def get_ProductList(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        WorkOrderMasterID = instances.WorkOrderMasterID
        workOrder_details = WorkOrderDetails.objects.filter(
            CompanyID=CompanyID, WorkOrderMasterID=WorkOrderMasterID, BranchID=BranchID)

        product_ids = workOrder_details.values_list('ProductID', flat=True)
        produc_instances = Product.objects.filter(
            CompanyID=CompanyID, ProductID__in=product_ids)
        ProductList = []
        for p in produc_instances:
            ProductList.append({
                "ProductName": p.ProductName,
                "ProductID": p.ProductID,
            })

        return ProductList

    def get_Barcode(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceListID = instance.PriceListID
        BranchID = instance.BranchID
        Barcode = ""
        if PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID).exists():
            Barcode = PriceList.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID).Barcode

        return Barcode

    def get_AutoBarcode(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceListID = instance.PriceListID
        BranchID = instance.BranchID
        AutoBarcode = ""
        if PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID).exists():
            AutoBarcode = PriceList.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID).AutoBarcode

        return AutoBarcode

    def get_BatchCode(self, instance):

        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        WorkOrderMasterID = instance.WorkOrderMasterID
        BatchCode = instance.BatchCode
        if not BatchCode:
            BatchCode = ""
            if Batch.objects.filter(CompanyID=CompanyID, ProductID=instance.ProductID, BranchID=BranchID, ConnectID=WorkOrderMasterID, StockIn__gt=0, PriceListID=instance.PriceListID).exists():
                BatchIns = Batch.objects.filter(
                    CompanyID=CompanyID, ProductID=instance.ProductID, BranchID=BranchID, ConnectID=WorkOrderMasterID, StockIn__gt=0, PriceListID=instance.PriceListID).last()
                BatchCode = BatchIns.BatchCode
        return BatchCode

    def get_BatchList(self, instance):
        BatchList = []
        CompanyID = self.context.get("CompanyID")
        # PriceRounding = int(self.context.get("PriceRounding"))
        BranchID = instance.BranchID
        ProductID = instance.ProductID
        is_batch = get_GeneralSettings(CompanyID,BranchID,"EnableProductBatchWise")
        if is_batch == True and Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
            batch_details = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
            batchList = Batch_ListSerializer(batch_details, many=True, context={
                "CompanyID": CompanyID})
            BatchList = batchList.data
        return BatchList
    
    
    def get_WorkOrderDetails(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = int(self.context.get("PriceRounding"))
        workorder_details = WorkOrderDetails.objects.filter(
            CompanyID=CompanyID, WorkOrderMasterID=instance.WorkOrderMasterID, BranchID=instance.BranchID).order_by('WorkOrderDetailsID')
        serialized = WorkOrderDetailsRestSerializer(workorder_details, many=True, context={"CompanyID": CompanyID,
                                                                                           "PriceRounding": PriceRounding})

        return serialized.data


class WorkOrder1Serializer(serializers.ModelSerializer):
    ExpiryDate = serializers.SerializerMethodField()
    ManufactureDate = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    GrandTotal_Rounded = serializers.SerializerMethodField()
    ProductName = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrderMaster
        fields = ('id', 'WorkOrderMasterID', 'VoucherNo', 'Date', 'ManufactureDate', 'ExpiryDate',
                  'ProductQty', 'GrandTotal_Rounded',  'GrandTotal','CostSum','Amount',
                  'TotalQty','GrandTotal','GrandCostSum','ProductName')

    def get_ProductName(self, instance):
        ProductName = ""
        CompanyID = self.context.get("CompanyID")
        ProductID = instance.ProductID
        if Product.objects.filter(CompanyID=CompanyID,ProductID=ProductID).exists():
            ProductName = Product.objects.filter(CompanyID=CompanyID,ProductID=ProductID).first().ProductName
        return ProductName

    def get_ManufactureDate(self, instance):
        date = ""
        if instance.ManufactureDate:
            date = instance.ManufactureDate
        return date

    def get_ExpiryDate(self, instance):
        date = ""
        if instance.ExpiryDate:
            date = instance.ExpiryDate

        return date

    def get_GrandTotal_Rounded(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        GrandTotal = instances.GrandTotal
        if not GrandTotal:
            GrandTotal = 0
        GrandTotal_Rounded = round(GrandTotal, PriceRounding)

        return str(GrandTotal_Rounded)

    def get_GrandTotal(self, instance):
        PriceRounding = self.context.get("PriceRounding")
        GrandTotal = instance.GrandTotal
        if not GrandTotal:
            GrandTotal = 0
        GrandTotal = round(GrandTotal, PriceRounding)

        return converted_float(GrandTotal)


class WorkOrderDetailsRestSerializer(serializers.ModelSerializer):

    ProductName = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()
    Barcode = serializers.SerializerMethodField()
    AutoBarcode = serializers.SerializerMethodField()
    NetAmount = serializers.SerializerMethodField()
    BatchList = serializers.SerializerMethodField()
    UnitList = serializers.SerializerMethodField()
    Qty = serializers.SerializerMethodField()
    detailID = serializers.SerializerMethodField()
    unq_id = serializers.SerializerMethodField()
    is_inclusive = serializers.SerializerMethodField()
    ProductCode = serializers.SerializerMethodField()
    UnitPrice = serializers.SerializerMethodField()
    SalesPrice = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()
    total_sales = serializers.SerializerMethodField()
    StandardSalesPrice = serializers.SerializerMethodField()
    SalesPrice1 = serializers.SerializerMethodField()
    SalesPrice2 = serializers.SerializerMethodField()
    SalesPrice3 = serializers.SerializerMethodField()
    ProductCodeVal = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrderDetails
        fields = ('id', 'unq_id', 'CompanyID', 'BatchCode', 'WorkOrderDetailsID', 'BranchID', 'Action', 'WorkOrderMasterID', 'ProductName', 'ProductID',
                  'Qty', 'PriceListID', 'UnitName', 'Barcode', 'AutoBarcode', 'UnitPrice', 'CostPerPrice','CostSum', 'Amount', 'NetAmount', 'is_inclusive',
                   'CreatedDate', 'UpdatedDate', 'CreatedUserID', 'BatchList', 'detailID', 'UnitList','ProductCodeVal',
                   'ProductCode','SalesPrice','total_cost','total_sales','StandardSalesPrice','SalesPrice1','SalesPrice2','SalesPrice3')

    def get_StandardSalesPrice(self,instance):
        CompanyID = self.context.get("CompanyID")
        PriceListID = instance.PriceListID
        StandardSalesPrice = 0
        if PriceList.objects.filter(CompanyID=CompanyID,PriceListID=PriceListID).exists():
            StandardSalesPrice = PriceList.objects.filter(CompanyID=CompanyID,PriceListID=PriceListID).first().SalesPrice
        return StandardSalesPrice

    
    def get_SalesPrice1(self,instance):
        CompanyID = self.context.get("CompanyID")
        PriceListID = instance.PriceListID
        SalesPrice1 = 0
        if PriceList.objects.filter(CompanyID=CompanyID,PriceListID=PriceListID).exists():
            SalesPrice1 = PriceList.objects.filter(CompanyID=CompanyID,PriceListID=PriceListID).first().SalesPrice1
        return SalesPrice1

    def get_SalesPrice2(self,instance):
        CompanyID = self.context.get("CompanyID")
        PriceListID = instance.PriceListID
        SalesPrice2 = 0
        if PriceList.objects.filter(CompanyID=CompanyID,PriceListID=PriceListID).exists():
            SalesPrice2 = PriceList.objects.filter(CompanyID=CompanyID,PriceListID=PriceListID).first().SalesPrice2
        return SalesPrice2


    def get_SalesPrice3(self,instance):
        CompanyID = self.context.get("CompanyID")
        PriceListID = instance.PriceListID
        SalesPrice3 = 0
        if PriceList.objects.filter(CompanyID=CompanyID,PriceListID=PriceListID).exists():
            SalesPrice3 = PriceList.objects.filter(CompanyID=CompanyID,PriceListID=PriceListID).first().SalesPrice3
        return SalesPrice3
    
    
    def get_UnitPrice(self, instance):
        UnitPrice = instance.CostPerPrice
        return UnitPrice

    def get_SalesPrice(self, instance):
        SalesPrice = instance.UnitPrice
        return SalesPrice

    def get_total_cost(self, instance):
        total_cost = instance.CostSum
        return total_cost

    def get_total_sales(self, instance):
        total_sales = instance.Amount
        return total_sales

    def get_ProductName(self, instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = instance.ProductID
        if Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID).exists():
            product = Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID)
            ProductName = product.ProductName
        else:
            ProductName = ""
        return ProductName
    
    def get_ProductCode(self, instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = instance.ProductID
        ProductCode = ""
        if Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID).exists():
            ProductCode = Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID).ProductCode
        return ProductCode

    def get_ProductCodeVal(self, instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = instance.ProductID
        ProductCode = ""
        if Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID).exists():
            ProductCode = Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID).ProductCode
        return ProductCode

    def get_is_inclusive(self, instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = instance.ProductID
        BranchID = instance.BranchID
        is_inclusive = False
        if Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID).exists():
            product_ins = Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID)
            VatID = product_ins.VatID
            GST = product_ins.GST
            Tax1 = product_ins.Tax1
            Tax2 = product_ins.Tax2
            Tax3 = product_ins.Tax3
            VatInclusive = False
            GSTInclusive = False
            Tax1Inclusive = False
            Tax2Inclusive = False
            Tax3Inclusive = False

            if VatID:
                VatInclusive = TaxCategory.objects.get(
                    CompanyID=CompanyID, TaxID=VatID, BranchID=BranchID).Inclusive
            if GST:
                GSTInclusive = TaxCategory.objects.get(
                    CompanyID=CompanyID, TaxID=GST, BranchID=BranchID).Inclusive
            if Tax1:
                Tax1Inclusive = TaxCategory.objects.get(
                    CompanyID=CompanyID, TaxID=Tax1, BranchID=BranchID).Inclusive
            if Tax2:
                Tax2Inclusive = TaxCategory.objects.get(
                    CompanyID=CompanyID, TaxID=Tax2, BranchID=BranchID).Inclusive
            if Tax3:
                Tax3Inclusive = TaxCategory.objects.get(
                    CompanyID=CompanyID, TaxID=Tax3, BranchID=BranchID).Inclusive

            if VatInclusive == True or GSTInclusive == True or Tax1Inclusive == True or Tax2Inclusive == True or Tax2Inclusive == True:
                is_inclusive = True

        return is_inclusive

    def get_detailID(self, instance):

        detailID = 0

        return detailID

    def get_unq_id(self, instance):
        unq_id = instance.id
        return unq_id

    def get_UnitName(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceListID = instance.PriceListID
        BranchID = instance.BranchID
        UnitName = ""
        if PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID).UnitID
            UnitName = Unit.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, UnitID=UnitID).UnitName

        return UnitName

    def get_Barcode(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceListID = instance.PriceListID
        BranchID = instance.BranchID
        Barcode = ""
        if PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID).exists():
            Barcode = PriceList.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID).Barcode

        return Barcode

    def get_AutoBarcode(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceListID = instance.PriceListID
        BranchID = instance.BranchID
        AutoBarcode = ""
        if PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID).exists():
            AutoBarcode = PriceList.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID).AutoBarcode

        return AutoBarcode

    def get_NetAmount(self, instance):

        NetAmount = instance.Amount
        return NetAmount

    def get_Qty(self, instance):
        PriceRounding = self.context.get("PriceRounding")
        Qty = round(instance.Qty, PriceRounding)

        return converted_float(Qty)

    def get_BatchList(self, instance):
        BatchCode_list = []
        CompanyID = self.context.get("CompanyID")
        PriceRounding = int(self.context.get("PriceRounding"))
        BranchID = instance.BranchID
        ProductID = instance.ProductID
        BatchCode_list = []
        is_batch = get_GeneralSettings(CompanyID,BranchID,"EnableProductBatchWise")
        if is_batch == True and Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
            batch_details = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
            BatchCode_list = Batch_ListSerializer(batch_details, many=True, context={"CompanyID": CompanyID,
                                                                                     "PriceRounding": PriceRounding})
            BatchCode_list = BatchCode_list.data
        return BatchCode_list

    def get_UnitList(self, instance):
        UnitList = []
        CompanyID = self.context.get("CompanyID")
        PriceRounding = int(self.context.get("PriceRounding"))
        BranchID = instance.BranchID
        ProductID = instance.ProductID
        if PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
            unit_details = PriceList.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
            UnitList = UnitListSerializer(unit_details, many=True, context={"CompanyID": CompanyID,
                                                                            "PriceRounding": PriceRounding})
            UnitList = UnitList.data
        return UnitList


class Batch_ListSerializer(serializers.ModelSerializer):

    BatchCodeTest = serializers.SerializerMethodField()
    BatchCodePurchase = serializers.SerializerMethodField()
    Stock = serializers.SerializerMethodField()
    base_unit = serializers.SerializerMethodField()
    Date = serializers.SerializerMethodField()
    ProductName = serializers.SerializerMethodField()
    ProductGroupName = serializers.SerializerMethodField()
    CompanyID = serializers.SerializerMethodField()

    class Meta:
        model = Batch
        fields = ('id', 'CompanyID', 'BatchCode', 'BatchCodeTest', 'BatchCodePurchase', 'Stock',
                  'PurchasePrice', 'SalesPrice', 'PriceListID', 'ProductID', 'ManufactureDate', 'ExpiryDate', 'base_unit',
                  'Date', 'ProductName', 'ProductGroupName')

    def get_CompanyID(self, batch_details):
        return str(batch_details.CompanyID)

    def get_ProductGroupName(self, batch_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = batch_details.ProductID
        BranchID = batch_details.BranchID
        ProductGroupName = ""
        if Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID).exists():
            ProductGroupID = Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID).ProductGroupID
            if ProductGroup.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=ProductGroupID).exists():
                ProductGroupName = ProductGroup.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=ProductGroupID).GroupName
        return ProductGroupName

    def get_ProductName(self, batch_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = batch_details.ProductID
        BranchID = batch_details.BranchID
        ProductName = ""
        if Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID).exists():
            ProductName = Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID).ProductName
        return ProductName

    def get_BatchCodeTest(self, batch_details):
        Stock_in = batch_details.StockIn
        Stock_out = batch_details.StockOut
        stock = converted_float(Stock_in) - converted_float(Stock_out)
        BatchCodeTest = str(batch_details.BatchCode) + "   Stock=" + str(
            round(stock, 2))+"   SalesPrice=" + str(round(batch_details.SalesPrice, 2)),
        return BatchCodeTest

    def get_BatchCodePurchase(self, batch_details):
        Stock_in = batch_details.StockIn
        Stock_out = batch_details.StockOut
        stock = converted_float(Stock_in) - converted_float(Stock_out)
        BatchCodePurchase = str(batch_details.BatchCode) + "   Stock=" + str(round(
            stock, 2))+"   PurchasePrice=" + str(round(batch_details.PurchasePrice, 2)),
        return BatchCodePurchase

    def get_Stock(self, batch_details):
        Stock_in = batch_details.StockIn
        Stock_out = batch_details.StockOut
        Stock = converted_float(Stock_in) - converted_float(Stock_out)
        return Stock

    def get_base_unit(self, batch_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = batch_details.BranchID
        ProductID = batch_details.ProductID
        base_unit = ""
        if PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, DefaultUnit=True).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, DefaultUnit=True).UnitID
            if Unit.objects.filter(CompanyID=CompanyID, BranchID=BranchID, UnitID=UnitID).exists():
                base_unit = Unit.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, UnitID=UnitID).UnitName
        return base_unit

    def get_Date(self, batch_details):
        CreatedDate = batch_details.CreatedDate
        Date = CreatedDate.date()
        return str(Date)


class UnitListSerializer(serializers.ModelSerializer):

    UnitName = serializers.SerializerMethodField()

    class Meta:
        model = PriceList
        fields = ('id', 'PriceListID', 'UnitName',)

    def get_UnitName(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceListID = instance.PriceListID
        BranchID = instance.BranchID
        UnitName = ""
        if PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID).UnitID
            UnitName = Unit.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, UnitID=UnitID).UnitName

        return UnitName



class Batch_ListSalesSerializer(serializers.ModelSerializer):
    
    Stock = serializers.SerializerMethodField()
    base_unit = serializers.SerializerMethodField()
    Date = serializers.SerializerMethodField()
    ProductName = serializers.SerializerMethodField()
    ProductGroupName = serializers.SerializerMethodField()
    CompanyID = serializers.SerializerMethodField()

    class Meta:
        model = Batch
        fields = ('id', 'BatchCode', 'Stock',
                  'PurchasePrice', 'SalesPrice', 'PriceListID', 'ProductID', 'ManufactureDate', 'ExpiryDate','ProductName')

 

    def get_ProductName(self, batch_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = batch_details.ProductID
        BranchID = batch_details.BranchID
        ProductName = ""
        if Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID).exists():
            ProductName = Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID).ProductName
        return ProductName


    def get_Stock(self, batch_details):
        Stock_in = batch_details.StockIn
        Stock_out = batch_details.StockOut
        Stock = converted_float(Stock_in) - converted_float(Stock_out)
        return Stock
