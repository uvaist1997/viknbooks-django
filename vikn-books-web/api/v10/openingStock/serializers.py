from rest_framework import serializers
from brands.models import OpeningStockMaster, OpeningStockDetails, Warehouse, Product, PriceList, Unit, UserTable
from django.contrib.auth.models import User
from api.v10.priceLists.serializers import PriceListRestSerializer
from main.functions import converted_float, get_BranchSettings


class OpeningStockMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = OpeningStockMaster
        fields = ('id', 'BranchID', 'VoucherNo', 'Date', 'WarehouseID',
                  'Notes', 'TotalQty', 'GrandTotal', 'IsActive', 'CreatedDate', 'CreatedUserID')


class OpeningStockMaster1RestSerializer(serializers.ModelSerializer):

    WareHouseName = serializers.SerializerMethodField()
    TotalQty = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    GrandTotal_Rounded = serializers.SerializerMethodField()

    class Meta:
        model = OpeningStockMaster
        fields = ('id', 'OpeningStockMasterID', 'BranchID', 'Action', 'VoucherNo', 'Date', 'WarehouseID', 'WareHouseName',
                  'Notes', 'TotalQty', 'GrandTotal', 'GrandTotal_Rounded', 'CreatedDate', 'UpdatedDate', 'CreatedUserID')

    def get_TotalQty(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalQty = instances.TotalQty
        TotalQty = round(TotalQty, PriceRounding)
        return converted_float(TotalQty)

    def get_GrandTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        GrandTotal = instances.GrandTotal
        GrandTotal = round(GrandTotal, PriceRounding)
        return converted_float(GrandTotal)

    def get_WareHouseName(self, instance):

        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        WarehouseID = instance.WarehouseID
        WarehouseInstance = Warehouse.objects.get(
            CompanyID=CompanyID, WarehouseID=WarehouseID)

        WareHouseName = WarehouseInstance.WarehouseName

        return str(WareHouseName)

    def get_GrandTotal_Rounded(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        GrandTotal = instances.GrandTotal

        GrandTotal_Rounded = round(GrandTotal, PriceRounding)

        return str(GrandTotal_Rounded)


class OpeningStockMasterRestSerializer(serializers.ModelSerializer):

    OpeningStockDetails = serializers.SerializerMethodField()
    WareHouseName = serializers.SerializerMethodField()
    TotalQty = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    ProductList = serializers.SerializerMethodField()

    class Meta:
        model = OpeningStockMaster
        fields = ('id', 'OpeningStockMasterID', 'BranchID', 'Action', 'VoucherNo', 'Date','as_on_date', 'WarehouseID', 'WareHouseName',
                  'Notes', 'TotalQty', 'GrandTotal', 'IsActive', 'CreatedDate', 'UpdatedDate', 'CreatedUserID', 'OpeningStockDetails',
                  'ProductList')

    def get_OpeningStockDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        opening_stock_details = OpeningStockDetails.objects.filter(
            CompanyID=CompanyID, OpeningStockMasterID=instances.OpeningStockMasterID, BranchID=instances.BranchID).order_by('OpeningStockDetailsID')
        serialized = OpeningStockDetailsRestSerializer(opening_stock_details, many=True, context={"PriceRounding": PriceRounding,
                                                                                                  "CompanyID": CompanyID})

        return serialized.data

    def get_ProductList(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        OpeningStockMasterID = instances.OpeningStockMasterID
        openingStock_details = OpeningStockDetails.objects.filter(
            CompanyID=CompanyID, OpeningStockMasterID=OpeningStockMasterID, BranchID=BranchID)

        product_ids = openingStock_details.values_list('ProductID', flat=True)
        produc_instances = Product.objects.filter(
            CompanyID=CompanyID, ProductID__in=product_ids)
        ProductList = []
        for p in produc_instances:
            ProductList.append({
                "ProductName": p.ProductName,
                "ProductID": p.ProductID,
            })

        return ProductList

    def get_TotalQty(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalQty = instances.TotalQty
        # TotalQty = round(TotalQty,PriceRounding)
        return converted_float(TotalQty)

    def get_GrandTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        GrandTotal = instances.GrandTotal
        # GrandTotal = round(GrandTotal,PriceRounding)
        return converted_float(GrandTotal)

    def get_WareHouseName(self, instance):

        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        WarehouseID = instance.WarehouseID
        WarehouseInstance = Warehouse.objects.get(
            CompanyID=CompanyID, WarehouseID=WarehouseID)

        WareHouseName = WarehouseInstance.WarehouseName

        return str(WareHouseName)


class OpeningStockDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = OpeningStockDetails
        fields = ('id', 'BranchID', 'ProductID', 'Qty', 'PriceListID',
                  'Rate', 'Amount')


class OpeningStockDetailsRestSerializer(serializers.ModelSerializer):

    Qty = serializers.SerializerMethodField()
    Rate = serializers.SerializerMethodField()
    Amount = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()
    ProductName = serializers.SerializerMethodField()
    unq_id = serializers.SerializerMethodField()
    detailID = serializers.SerializerMethodField()
    UnitList = serializers.SerializerMethodField()
    PurchasePrice = serializers.SerializerMethodField()
    ProductCode = serializers.SerializerMethodField()
    Barcode = serializers.SerializerMethodField()

    class Meta:
        model = OpeningStockDetails
        fields = ('id', 'OpeningStockDetailsID', 'Action', 'BranchID', 'OpeningStockMasterID', 'ProductID', 'Qty', 'PriceListID',
                  'UnitName', 'ProductName', 'Rate', 'Amount', 'unq_id', 'detailID', 'UnitList', 'PurchasePrice',
                  'ProductCode', 'Barcode')

    def get_ProductCode(self, opening_stock_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = opening_stock_details.ProductID
        ProductCode = ""
        if Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID).exists():
            ProductCode = Product.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID).first().ProductCode
        return ProductCode
    
    def get_Barcode(self, opening_stock_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = opening_stock_details.ProductID
        PriceListID = opening_stock_details.PriceListID
        Barcode = ""
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID).exists():
            Barcode = PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID).first().Barcode
        return Barcode
    
    
    def get_Qty(self, opening_stock_details):
        PriceRounding = self.context.get("PriceRounding")
        Qty = opening_stock_details.Qty
        # Qty = round(Qty,PriceRounding)
        return converted_float(Qty)

    def get_Rate(self, opening_stock_details):
        PriceRounding = self.context.get("PriceRounding")
        Rate = opening_stock_details.Rate
        # Rate = round(Rate,PriceRounding)
        return converted_float(Rate)

    def get_PurchasePrice(self, opening_stock_details):
        PriceRounding = self.context.get("PriceRounding")
        PurchasePrice = opening_stock_details.Rate
        # Rate = round(Rate,PriceRounding)
        return converted_float(PurchasePrice)

    def get_Amount(self, opening_stock_details):
        PriceRounding = self.context.get("PriceRounding")
        Amount = opening_stock_details.Amount
        # Amount = round(Amount,PriceRounding)
        return converted_float(Amount)

    def get_ProductName(self, opening_stock_details):

        CompanyID = self.context.get("CompanyID")

        ProductID = opening_stock_details.ProductID
        BranchID = opening_stock_details.BranchID

        if Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID).exists():
            product = Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID)
            ProductName = product.ProductName
        else:
            ProductName = ""

        return ProductName

    def get_UnitName(self, opening_stock_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = opening_stock_details.PriceListID
        BranchID = opening_stock_details.BranchID
        if PriceList.objects.filter(CompanyID=CompanyID, PriceListID=PriceListID).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListID).UnitID
            UnitName = Unit.objects.get(
                CompanyID=CompanyID, UnitID=UnitID).UnitName
        else:
            UnitName = ""

        return UnitName

    def get_unq_id(self, opening_stock_details):
        CompanyID = self.context.get("CompanyID")
        unq_id = opening_stock_details.id
        return unq_id

    def get_detailID(self, opening_stock_details):
        detailID = 0
        return detailID

    def get_UnitList(self, opening_stock_details):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = opening_stock_details.ProductID
        BranchID = opening_stock_details.BranchID

        UnitList = PriceList.objects.filter(
            ProductID=ProductID, CompanyID=CompanyID)
        serialized = PriceListRestSerializer(UnitList, many=True, context={
                                             "CompanyID": CompanyID, "PriceRounding": PriceRounding})

        return serialized.data


class OpeningStockFilterSerializer(serializers.ModelSerializer):

    Qty = serializers.SerializerMethodField()
    Rate = serializers.SerializerMethodField()
    Amount = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()
    PriceListID = serializers.SerializerMethodField()
    UnitList = serializers.SerializerMethodField()
    AutoBarcode = serializers.SerializerMethodField()
    ProductCode = serializers.SerializerMethodField()
    PurchasePrice = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'BranchID', 'ProductID', 'Qty', 'PriceListID',
                  'UnitName', 'ProductName', 'Rate', 'Amount', 'UnitList', 'ProductCode', 'AutoBarcode', 'PurchasePrice')

    def get_Qty(self, instances):
        Qty = 1
        return converted_float(Qty)

    def get_UnitList(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        UnitList = []

        pricelist_list = PriceList.objects.filter(
            CompanyID=CompanyID)
        if pricelist_list.filter(ProductID=ProductID).exists():
            price_ins = pricelist_list.filter(
                ProductID=ProductID)
            for p in price_ins:
                UnitID = PriceList.objects.get(
                    CompanyID=CompanyID, PriceListID=p.PriceListID).UnitID
                UnitName = Unit.objects.get(
                    CompanyID=CompanyID, UnitID=UnitID).UnitName
                price_dict = {
                    "PriceListID": p.PriceListID,
                    "UnitName": UnitName
                }
                UnitList.append(price_dict)

        return UnitList

    def get_Rate(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        PurchasePrice = 0
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            PurchasePrice = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).PurchasePrice
        Rate = round(PurchasePrice, PriceRounding)
        return converted_float(Rate)
        # return Rate

    def get_PurchasePrice(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID

        PurchasePrice = 0
        if get_BranchSettings(CompanyID, "productsForAllBranches"):
            pricelist_list = PriceList.objects.filter(
                CompanyID=CompanyID)
        else:
            pricelist_list = PriceList.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
        if pricelist_list.filter(ProductID=ProductID, DefaultUnit=True).exists():
            PurchasePrice = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).PurchasePrice
        PurchasePrice = round(PurchasePrice, PriceRounding)
        return converted_float(PurchasePrice)

    def get_Amount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        PurchasePrice = 0
        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            PurchasePrice = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).PurchasePrice
        Amount = round(PurchasePrice, PriceRounding)
        # Amount = 0
        return converted_float(Amount)

    def get_UnitName(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID

        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).UnitID
            UnitName = Unit.objects.get(
                CompanyID=CompanyID, UnitID=UnitID).UnitName
        else:
            UnitName = ""

        return UnitName

    def get_PriceListID(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID

        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            PriceListID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).PriceListID
        else:
            PriceListID = ""

        return PriceListID

    def get_AutoBarcode(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID

        if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            AutoBarcode = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).AutoBarcode
        else:
            AutoBarcode = ""

        return AutoBarcode

    def get_ProductCode(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID

        if Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID).exists():
            ProductCode = Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID).ProductCode
        else:
            ProductCode = ""

        return ProductCode


class OpeningStockReportSerializer(serializers.ModelSerializer):

    WareHouseName = serializers.SerializerMethodField()
    TotalQty = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    UserName = serializers.SerializerMethodField()

    class Meta:
        model = OpeningStockMaster
        fields = ('id', 'OpeningStockMasterID', 'BranchID', 'VoucherNo', 'Date', 'WarehouseID', 'WareHouseName',
                  'Notes', 'TotalQty', 'GrandTotal', 'UserName')

    def get_TotalQty(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalQty = instances.TotalQty
        TotalQty = round(TotalQty, PriceRounding)
        return converted_float(TotalQty)

    def get_GrandTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        GrandTotal = instances.GrandTotal
        GrandTotal = round(GrandTotal, PriceRounding)
        return converted_float(GrandTotal)

    def get_WareHouseName(self, instance):

        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        WarehouseID = instance.WarehouseID
        WarehouseInstance = Warehouse.objects.get(
            CompanyID=CompanyID, WarehouseID=WarehouseID)

        WareHouseName = WarehouseInstance.WarehouseName

        return str(WareHouseName)

    def get_UserName(self, instance):
        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        UserID = instance.CreatedUserID
        user_name = User.objects.get(id=UserID).username

        return str(user_name)
