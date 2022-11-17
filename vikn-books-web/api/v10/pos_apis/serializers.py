from main.functions import converted_float
from rest_framework import serializers
from brands import models as table
# from api.v9.priceLists.serializers import PriceListRestSerializer
from api.v10.companySettings.serializers import CompanySettingsRestSerializer
from django.db.models import Q, Prefetch, Sum


class PriceListSerializer(serializers.ModelSerializer):

    UnitName = serializers.SerializerMethodField()

    class Meta:
        model = table.PriceList
        fields = ('id', 'PriceListID', 'BranchID', 'MRP', 'ProductID', 'UnitID', 'UnitName',
                  'SalesPrice', 'PurchasePrice', 'SalesPrice1', 'SalesPrice2', 'SalesPrice3', 'MultiFactor', 'Barcode', 'AutoBarcode')

    def get_UnitName(self, instances):
        CompanyID = self.context.get("CompanyID")

        UnitID = instances.UnitID
        BranchID = instances.BranchID
        UnitName = ""
        if table.Unit.objects.filter(CompanyID=CompanyID, UnitID=UnitID).exists():
            UnitName = table.Unit.objects.get(
                CompanyID=CompanyID, UnitID=UnitID).UnitName

        return UnitName


class POS_ProductList_Serializer(serializers.ModelSerializer):
    UnitList = serializers.SerializerMethodField()
    GST_Tax = serializers.SerializerMethodField()
    VAT_Tax = serializers.SerializerMethodField()

    class Meta:
        model = table.Product
        fields = ('id', 'ProductID', 'ProductName', 'ProductCode', 'Description',
                  'UnitList', 'GST_Tax', 'VAT_Tax', 'VatID', 'GST', 'is_inclusive')

    def get_UnitList(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID
        UnitList = table.PriceList.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID)
        serialized = PriceListSerializer(UnitList, many=True, context={
            "CompanyID": CompanyID, "PriceRounding": PriceRounding})
        return serialized.data

    def get_GST_Tax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.GST
        BranchID = instance.BranchID
        if table.TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = table.TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
            SalesTax = tax.SalesTax
            return str(SalesTax)
        else:
            return "0"

    def get_VAT_Tax(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TaxID = instance.VatID
        BranchID = instance.BranchID
        if table.TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = table.TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
            SalesTax = tax.SalesTax
            return str(SalesTax)
        else:
            return "0"


class POS_Sales_Serializer(serializers.ModelSerializer):
    LedgerName = serializers.SerializerMethodField()
    SubTotal = serializers.SerializerMethodField()
    TenderCash = serializers.SerializerMethodField()
    ItemDetails = serializers.SerializerMethodField()

    class Meta:
        model = table.SalesMaster
        fields = ('id', 'LedgerID', 'LedgerName', 'CustomerName', 'SubTotal', 'TotalDiscount', 'TotalTax', 'GrandTotal', 'Balance',
                  'TenderCash', 'BillDiscPercent', 'TaxType', 'CashReceived', 'BankAmount', 'CardTypeID', 'CardNumber', 'ItemDetails',
                  'SGSTAmount', 'CGSTAmount', 'IGSTAmount', 'RoundOff')

    def get_LedgerName(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        LedgerID = instance.LedgerID
        BranchID = instance.BranchID
        LedgerName = ""
        if table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():
            LedgerName = table.AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID).LedgerName
        return LedgerName

    def get_SubTotal(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        SubTotal = instance.TotalGrossAmt
        return SubTotal

    def get_TenderCash(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        TenderCash = instance.CashReceived
        return TenderCash

    def get_ItemDetails(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        BranchID = instance.BranchID
        SalesMasterID = instance.SalesMasterID
        ItemDetails = []
        if table.SalesDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SalesMasterID=SalesMasterID).exists():
            details = table.SalesDetails.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, SalesMasterID=SalesMasterID)
            serialized = Pos_SalesDetailSerializer(details, many=True, context={
                "CompanyID": CompanyID, "PriceRounding": PriceRounding})
            ItemDetails = serialized.data
        return ItemDetails


class Pos_SalesDetailSerializer(serializers.ModelSerializer):
    ProductName = serializers.SerializerMethodField()
    ProductCode = serializers.SerializerMethodField()
    UnitList = serializers.SerializerMethodField()
    Description = serializers.SerializerMethodField()

    class Meta:
        model = table.SalesDetails
        fields = ('id', 'SalesDetailsID', 'Qty', 'ProductID', 'ProductName', 'UnitPrice', 'InclusivePrice', 'ProductCode', 'UnitList',
                  'PriceListID', 'DiscountPerc', 'DiscountAmount', 'GrossAmount', 'TaxableAmount', 'VATPerc', 'VATAmount', 'SGSTPerc', 'SGSTAmount', 'CGSTPerc',
                  'CGSTAmount', 'IGSTPerc', 'IGSTAmount', 'NetAmount', 'Description')

    def get_UnitList(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID
        UnitList = table.PriceList.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID)
        serialized = PriceListSerializer(UnitList, many=True, context={
            "CompanyID": CompanyID, "PriceRounding": PriceRounding})
        return serialized.data

    def get_Description(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID
        Description = ""
        if table.Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID).exists():
            Description = table.Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID).Description
        return Description

    def get_ProductName(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID
        ProductName = ""
        if table.Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID).exists():
            ProductName = table.Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID).ProductName
        return ProductName

    def get_ProductCode(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID
        ProductCode = ""
        if table.Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID).exists():
            ProductCode = table.Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID).ProductCode
        return ProductCode


class POS_BranchList_Serializer(serializers.ModelSerializer):
    TaxNo = serializers.SerializerMethodField()
    CountryName = serializers.SerializerMethodField()

    class Meta:
        model = table.Branch
        fields = ('id', 'BranchName', 'DisplayName', 'BranchID',
                  'Building', 'City', 'Phone', 'TaxNo', 'CountryName')

    def get_TaxNo(self, instances):
        VATNumber = instances.VATNumber
        GSTNumber = instances.GSTNumber
        is_gst = instances.is_gst
        is_vat = instances.is_vat
        TaxNo = ""
        if is_gst == True and GSTNumber:
            TaxNo = GSTNumber
        if is_vat == True and VATNumber:
            TaxNo = VATNumber
        return TaxNo

    def get_CountryName(self, instances):
        CountryName = instances.country.Country_Name
        return CountryName


class POSEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = table.Employee
        fields = ('id', 'EmployeeID', 'FirstName')


class POS_ProductListFilter_Serializer(serializers.ModelSerializer):
    UnitName = serializers.SerializerMethodField()
    PurchasePrice = serializers.SerializerMethodField()
    SalesPrice = serializers.SerializerMethodField()
    Stock = serializers.SerializerMethodField()

    class Meta:
        model = table.Product
        fields = ('id', 'ProductID', 'ProductName', 'ProductCode', 'Description',
                  'PurchasePrice', 'SalesPrice', 'Stock', 'UnitName')

    def get_UnitName(self, instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = instance.ProductID
        UnitName = ""
        if table.PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            UnitID = table.PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).UnitID
            UnitName = table.Unit.objects.get(
                CompanyID=CompanyID, UnitID=UnitID).UnitName
        return UnitName

    def get_PurchasePrice(self, instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = instance.ProductID
        PurchasePrice = 0
        if table.PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            PurchasePrice = table.PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).PurchasePrice
        return PurchasePrice

    def get_SalesPrice(self, instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = instance.ProductID
        SalesPrice = 0
        if table.PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).exists():
            SalesPrice = table.PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True).SalesPrice
        return SalesPrice

    def get_Stock(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = self.context.get("BranchID")
        WarehouseID = self.context.get("WarehouseID")
        ProductID = instances.ProductID
        Stock = 0
        if table.StockPosting.objects.filter(CompanyID=CompanyID, ProductID=ProductID).exists():
            stock_instances = table.StockPosting.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID)
            if BranchID:
                stock_instances = stock_instances.filter(BranchID=BranchID)
            if WarehouseID:
                stock_instances = stock_instances.filter(
                    WareHouseID=WarehouseID)
            Stock = 0
            if stock_instances:
                QtyIn_sum = stock_instances.aggregate(Sum('QtyIn'))
                QtyIn_sum = QtyIn_sum['QtyIn__sum']
                QtyOut_sum = stock_instances.aggregate(Sum('QtyOut'))
                QtyOut_sum = QtyOut_sum['QtyOut__sum']
                Stock = converted_float(QtyIn_sum) - converted_float(QtyOut_sum)
        return Stock


class Faera_Serializer(serializers.ModelSerializer):
    general_datas = serializers.SerializerMethodField()
    user_datas = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    unq_id = serializers.SerializerMethodField()
    device_id = serializers.SerializerMethodField()
    device_name = serializers.SerializerMethodField()
    device_code = serializers.SerializerMethodField()

    class Meta:
        model = table.POS_Devices
        fields = ('unq_id', 'name', 'device_id', 'device_name',
                  'device_code', 'general_datas', 'user_datas')

    def get_name(self, instance):
        name = instance.Name
        return name
    
    def get_unq_id(self, instance):
        unq_id = instance.id
        return unq_id
    
    def get_device_id(self, instance):
        device_id = instance.DeviceMachineID
        return device_id
    
    def get_device_name(self, instance):
        device_name = instance.DeviceName
        return device_name
    
    def get_device_code(self, instance):
        device_code = instance.DeviceCode
        return device_code
    
    def get_general_datas(self, instance):
        RouteIDs = []
        CompanyID = self.context.get("CompanyID")
        general_datas = {}
        route_list = []
        if table.POS_DevicesRoutes.objects.filter(CompanyID=CompanyID, DeviceID=instance).exists():
            route_ins = table.POS_DevicesRoutes.objects.filter(
                CompanyID=CompanyID, DeviceID=instance)
            RouteIDs = route_ins.values_list("RouteID__id", flat=True)
            for r in route_ins:
                route_list.append({
                    "id": r.RouteID.id,
                    "RouteName": r.RouteID.RouteName,
                })
        PriceCategoryID = None
        PriceCategoryName = ""
        if instance.PriceCategoryID:
            PriceCategoryID = instance.PriceCategoryID.id
            PriceCategoryName = instance.PriceCategoryID.PriceCategoryName
        WarehouseID = None
        WarehouseName = None
        warehouse_id = None
        if instance.WareHouseID:
            WarehouseID = instance.WareHouseID.id
            WarehouseName = instance.WareHouseID.WarehouseName
            warehouse_id = instance.WareHouseID.WarehouseID
            
        general_datas = {
            "auto_incriment": instance.AutoIncrimentQty,
            "stock_alert": instance.StockAlert,
            "PriceCategoryID": PriceCategoryID,
            "WarehouseID": WarehouseID,
            "Route_ids": RouteIDs,
            "route_list": route_list,
            "PriceCategoryName": PriceCategoryName,
            "WarehouseName": WarehouseName,
            "warehouse_id": warehouse_id
        }
        return general_datas
    
    def get_user_datas(self, instance):
        CompanyID = self.context.get("CompanyID")
        user_datas = []
        if table.POS_DevicesUsers.objects.filter(CompanyID=CompanyID, DeviceID=instance).exists():
            user_ins = table.POS_DevicesUsers.objects.filter(
                CompanyID=CompanyID, DeviceID=instance)
            serialized = Faera_UserSerializer(
                user_ins, many=True, context={"CompanyID": CompanyID})
            user_datas = serialized.data
        return user_datas


class Faera_UserSerializer(serializers.ModelSerializer):
    device_id = serializers.SerializerMethodField()
    UserID = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    Role = serializers.SerializerMethodField()

    class Meta:
        model = table.POS_DevicesUsers
        fields = ('id', 'device_id', 'UserID',
                  'username', 'is_edit', 'is_delete', 'Role')

    def get_device_id(self, instance):
        device_id = instance.DeviceID.id
        return device_id
    
    def get_UserID(self, instance):
        UserID = instance.UserTableID.id
        return UserID
    
    def get_username(self, instance):
        username = instance.UserTableID.customer.user.username
        return username
    
    def get_Role(self, instance):
        Role = instance.UserTableID.UserType.UserTypeName
        return Role
