from rest_framework import serializers
from brands.models import PurchaseMaster, PurchaseDetails, AccountLedger, Product, Warehouse, PriceList, Unit, TaxCategory, PriceCategory, WorkOrderMaster, Batch, WorkOrderDetails
from api.v6.priceLists.serializers import PriceListRestSerializer


class WorkOrderSerializer(serializers.ModelSerializer):
    BatchCode = serializers.SerializerMethodField()
    WorkOrderDetails = serializers.SerializerMethodField()
    ExpiryDate = serializers.SerializerMethodField()
    ManufactureDate = serializers.SerializerMethodField()
    WareHouseName = serializers.SerializerMethodField()
    ProductName = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()
    Barcode = serializers.SerializerMethodField()
    AutoBarcode = serializers.SerializerMethodField()
    ProductQty = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    is_inclusive = serializers.SerializerMethodField()
    BatchPurchasePrice = serializers.SerializerMethodField()
    UnitList = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrderMaster
        fields = ('id', 'WorkOrderMasterID','BatchPurchasePrice', 'BranchID','UnitList', 'Action', 'VoucherNo', 'Date', 'WareHouseID', 'WareHouseName', 'Notes', 'ProductID', 'ProductName', 'ManufactureDate', 'ExpiryDate',
                  'ProductQty', 'CostPerPrice', 'UnitPrice', 'PriceListID', 'Barcode', 'AutoBarcode', 'UnitName', 'Amount', 'Weight', 'TotalQty', 'GrandTotal', 'IsActive', 'CreatedDate', 'UpdatedDate', 'CreatedUserID', 'BatchCode',
                  'is_inclusive', 'WorkOrderDetails')

    def get_UnitList(self, purchase_details):

        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        ProductID = purchase_details.ProductID
        BranchID = purchase_details.BranchID

        UnitList = PriceList.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)

        serialized = PriceListRestSerializer(UnitList, many=True, context={
                                             "CompanyID": CompanyID, "PriceRounding": PriceRounding})

        return serialized.data


    def get_BatchPurchasePrice(self, purchase_details):

        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        ProductID = purchase_details.ProductID
        BranchID = purchase_details.BranchID
        BatchCode = purchase_details.BatchCode
        PriceListID = purchase_details.PriceListID
        if BatchCode:
            BatchPurchasePrice = Batch.objects.get(BranchID=BranchID,BatchCode=BatchCode,CompanyID=CompanyID).PurchasePrice
        else:
            BatchPurchasePrice = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID,PriceListID=PriceListID).PurchasePrice

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
        if Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).exists():
            product_ins = Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)
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

        return float(ProductQty)

    def get_GrandTotal(self, instance):
        PriceRounding = self.context.get("PriceRounding")
        GrandTotal = instance.GrandTotal

        return float(GrandTotal)

    def get_ProductName(self, instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = instance.ProductID
        BranchID = instance.BranchID
        ProductName = ""
        if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
            ProductName = Product.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).ProductName

        return ProductName

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

    class Meta:
        model = WorkOrderMaster
        fields = ('id', 'WorkOrderMasterID', 'VoucherNo', 'Date','ManufactureDate', 'ExpiryDate',
                  'ProductQty','GrandTotal_Rounded',  'GrandTotal')

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

        GrandTotal_Rounded = round(GrandTotal, PriceRounding)

        return str(GrandTotal_Rounded)

    def get_GrandTotal(self, instance):
        PriceRounding = self.context.get("PriceRounding")
        GrandTotal = round(instance.GrandTotal, PriceRounding)

        return float(GrandTotal)




class WorkOrderDetailsRestSerializer(serializers.ModelSerializer):

    ProductName = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()
    Barcode = serializers.SerializerMethodField()
    AutoBarcode = serializers.SerializerMethodField()
    NetAmount = serializers.SerializerMethodField()
    BatchCode_list = serializers.SerializerMethodField()
    UnitList = serializers.SerializerMethodField()
    Qty = serializers.SerializerMethodField()
    detailID = serializers.SerializerMethodField()
    unq_id = serializers.SerializerMethodField()
    is_inclusive = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrderDetails
        fields = ('id', 'unq_id', 'CompanyID', 'BatchCode', 'WorkOrderDetailsID', 'BranchID', 'Action', 'WorkOrderMasterID', 'ProductName', 'ProductID',
                  'Qty', 'PriceListID', 'UnitName', 'Barcode', 'AutoBarcode', 'UnitPrice', 'CostPerPrice', 'Amount', 'NetAmount', 'is_inclusive', 'CreatedDate', 'UpdatedDate', 'CreatedUserID', 'BatchCode_list', 'detailID', 'UnitList')

    def get_ProductName(self, instance):

        CompanyID = self.context.get("CompanyID")

        ProductID = instance.ProductID
        BranchID = instance.BranchID

        if Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).exists():
            product = Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)
            ProductName = product.ProductName
        else:
            ProductName = ""

        return ProductName

    def get_is_inclusive(self, instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = instance.ProductID
        BranchID = instance.BranchID
        is_inclusive = False
        if Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).exists():
            product_ins = Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)
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

        CompanyID = self.context.get("CompanyID")

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

        return float(Qty)

    def get_BatchCode_list(self, instance):
        BatchCode_list = []
        CompanyID = self.context.get("CompanyID")
        PriceRounding = int(self.context.get("PriceRounding"))
        BranchID = instance.BranchID
        ProductID = instance.ProductID
        BatchCode_list = []
        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
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

    class Meta:
        model = Batch
        fields = ('id', 'CompanyID', 'BatchCode', 'BatchCodeTest', 'BatchCodePurchase', 'Stock',
                  'PurchasePrice', 'SalesPrice', 'PriceListID', 'ProductID', 'ManufactureDate', 'ExpiryDate')

    def get_BatchCodeTest(self, batch_details):
        Stock_in = batch_details.StockIn
        Stock_out = batch_details.StockIn
        stock = float(Stock_in) - float(Stock_out)
        BatchCodeTest = str(batch_details.BatchCode) + "   Stock=" + str(
            round(stock, 2))+"   SalesPrice=" + str(round(batch_details.SalesPrice, 2)),
        return BatchCodeTest

    def get_BatchCodePurchase(self, batch_details):
        Stock_in = batch_details.StockIn
        Stock_out = batch_details.StockIn
        stock = float(Stock_in) - float(Stock_out)
        BatchCodePurchase = str(batch_details.BatchCode) + "   Stock=" + str(round(
            stock, 2))+"   PurchasePrice=" + str(round(batch_details.PurchasePrice, 2)),
        return BatchCodePurchase

    def get_Stock(self, batch_details):
        Stock_in = batch_details.StockIn
        Stock_out = batch_details.StockIn
        Stock = float(Stock_in) - float(Stock_out)
        return Stock


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
