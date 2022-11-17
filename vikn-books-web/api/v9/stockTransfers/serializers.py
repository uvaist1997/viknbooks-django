from django.db.models import Sum
from rest_framework import serializers

from api.v9.priceLists.serializers import PriceListRestSerializer
from api.v9.products.serializers import ProductSearchSerializer
from brands.models import (
    Batch,
    GeneralSettings,
    PriceList,
    Product,
    StockPosting,
    StockTransferDetails,
    StockTransferMaster_ID,
    Unit,
    Warehouse,
)
from main.functions import converted_float


class StockTransferMaster_IDSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockTransferMaster_ID
        fields = (
            "id",
            "BranchID",
            "VoucherNo",
            "Date",
            "Notes",
            "TransferredByID",
            "WarehouseFromID",
            "WarehouseToID",
            "TotalQty",
            "GrandTotal",
            "IsActive",
            "CreatedDate",
            "CreatedUserID",
        )


class StockTransferMaster1_IDRestSerializer(serializers.ModelSerializer):

    WarehouseFromName = serializers.SerializerMethodField()
    WarehouseToName = serializers.SerializerMethodField()
    TotalQty = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    GrandTotal_Rounded = serializers.SerializerMethodField()
    MaxGrandTotal = serializers.SerializerMethodField()

    class Meta:
        model = StockTransferMaster_ID
        fields = (
            "id",
            "StockTransferMasterID",
            "GrandTotal_Rounded",
            "BranchID",
            "Action",
            "VoucherNo",
            "Date",
            "Notes",
            "TransferredByID",
            "WarehouseFromID",
            "WarehouseFromName",
            "WarehouseToID",
            "WarehouseToName",
            "TotalQty",
            "GrandTotal",
            "MaxGrandTotal",
            "IsActive",
            "CreatedDate",
            "CreatedUserID",
            "IsTaken"
        )

    def get_WarehouseFromName(self, instance):

        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        WarehouseID = instance.WarehouseFromID
        WarehouseInstance = Warehouse.objects.get(
            CompanyID=CompanyID, WarehouseID=WarehouseID
        )

        WareHouseName = WarehouseInstance.WarehouseName

        return str(WareHouseName)

    def get_WarehouseToName(self, instance):

        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        WarehouseID = instance.WarehouseToID
        WarehouseInstance = Warehouse.objects.get(
            CompanyID=CompanyID, WarehouseID=WarehouseID
        )

        WareHouseName = WarehouseInstance.WarehouseName

        return str(WareHouseName)

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

    def get_MaxGrandTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        MaxGrandTotal = instances.MaxGrandTotal
        # if MaxGrandTotal == None:
        #     MaxGrandTotal = 0
        # MaxGrandTotal = round(MaxGrandTotal, PriceRounding)
        return converted_float(MaxGrandTotal)

    def get_GrandTotal_Rounded(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        GrandTotal = instances.GrandTotal

        GrandTotal_Rounded = round(GrandTotal, PriceRounding)

        return str(GrandTotal_Rounded)


class StockTransferMaster_IDRestSerializer(serializers.ModelSerializer):

    Details = serializers.SerializerMethodField()
    WarehouseFromName = serializers.SerializerMethodField()
    WarehouseToName = serializers.SerializerMethodField()
    TotalQty = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    MaxGrandTotal = serializers.SerializerMethodField()
    ProductList = serializers.SerializerMethodField()

    class Meta:
        model = StockTransferMaster_ID
        fields = (
            "id",
            "StockTransferMasterID",
            "BranchID",
            "Action",
            "VoucherNo",
            "Date",
            "Notes",
            "TransferredByID",
            "WarehouseFromID",
            "WarehouseFromName",
            "WarehouseToID",
            "WarehouseToName",
            "TotalQty",
            "GrandTotal",
            "MaxGrandTotal",
            "IsActive",
            "CreatedDate",
            "CreatedUserID",
            "Details",
            "BranchFromID",
            "BranchToID",
            "ProductList",
            "StockOrderNo"
        )

    def get_Details(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        WarehouseFromID = instances.WarehouseFromID

        stockTransfer_details = StockTransferDetails.objects.filter(
            CompanyID=CompanyID,
            StockTransferMasterID=instances.StockTransferMasterID,
            BranchID=instances.BranchID,
        )
        serialized = StockTransferDetailsRestSerializer(
            stockTransfer_details,
            many=True,
            context={
                "PriceRounding": PriceRounding,
                "CompanyID": CompanyID,
                "WarehouseFromID": WarehouseFromID,
            },
        )

        return serialized.data

    def get_ProductList(self, instances):
        CompanyID = self.context.get("CompanyID")
        request = self.context.get("request")
        PriceRounding = self.context.get("PriceRounding")
        BranchID = instances.BranchID
        WarehouseID = instances.WarehouseFromID
        StockTransferMasterID = instances.StockTransferMasterID
        stockTransfer_details = StockTransferDetails.objects.filter(
            CompanyID=CompanyID,
            StockTransferMasterID=StockTransferMasterID,
            BranchID=BranchID,
        )

        product_ids = stockTransfer_details.values_list("ProductID", flat=True)
        produc_instances = Product.objects.filter(
            CompanyID=CompanyID, ProductID__in=product_ids
        )
        serialized = ProductSearchSerializer(
            produc_instances,
            many=True,
            context={
                "request": request,
                "CompanyID": CompanyID,
                "PriceRounding": PriceRounding,
                "WarehouseID": WarehouseID,
            },
        )
        # for p in produc_instances:
        #     ProductList.append({
        #         "ProductName": p.ProductName,
        #         "ProductID": p.ProductID,
        #     })

        return serialized.data

    def get_WarehouseFromName(self, instance):

        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        WarehouseID = instance.WarehouseFromID
        WarehouseInstance = Warehouse.objects.get(
            CompanyID=CompanyID, WarehouseID=WarehouseID
        )

        WareHouseName = WarehouseInstance.WarehouseName

        return str(WareHouseName)

    def get_WarehouseToName(self, instance):

        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        WarehouseID = instance.WarehouseToID
        WarehouseInstance = Warehouse.objects.get(
            CompanyID=CompanyID, WarehouseID=WarehouseID
        )

        WareHouseName = WarehouseInstance.WarehouseName

        return str(WareHouseName)

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

    def get_MaxGrandTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        MaxGrandTotal = instances.MaxGrandTotal
        # MaxGrandTotal = round(MaxGrandTotal,PriceRounding)
        if not MaxGrandTotal:
            MaxGrandTotal = 0
        return converted_float(MaxGrandTotal)


class StockTransferDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockTransferDetails
        fields = ("id", "BranchID", "ProductID", "Qty", "PriceListID", "Rate", "Amount")


class StockTransferDetailsRestSerializer(serializers.ModelSerializer):
    Qty = serializers.SerializerMethodField()
    Rate = serializers.SerializerMethodField()
    MaXRate = serializers.SerializerMethodField()
    MaxAmount = serializers.SerializerMethodField()
    Amount = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()
    ProductName = serializers.SerializerMethodField()
    unq_id = serializers.SerializerMethodField()
    detailID = serializers.SerializerMethodField()
    ProductCode = serializers.SerializerMethodField()
    HSNCode = serializers.SerializerMethodField()
    Stock = serializers.SerializerMethodField()
    UnitList = serializers.SerializerMethodField()
    product_description = serializers.SerializerMethodField()
    Description = serializers.SerializerMethodField()

    class Meta:
        model = StockTransferDetails
        fields = (
            "id",
            "StockTransferDetailsID",
            "BranchID",
            "Action",
            "StockTransferMasterID",
            "ProductID",
            "Qty",
            "PriceListID",
            "Rate",
            "MaXRate",
            "Amount",
            "MaxAmount",
            "UnitName",
            "ProductName",
            "unq_id",
            "detailID",
            "ProductCode",
            "HSNCode",
            "Stock",
            "UnitList",
            "product_description",
            "Description"
        )

    def get_Description(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID
        product = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)
        Description = product.Description
        return Description
    
    
    def get_product_description(self, purchaseReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchaseReturn_details.BranchID
        ProductID = purchaseReturn_details.ProductID
        Description = ""
        if Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID).exists():
            Description = Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID
            ).Description
        return str(Description)

    def get_UnitList(self, stockTransfer_details):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = stockTransfer_details.ProductID
        BranchID = stockTransfer_details.BranchID

        UnitList = PriceList.objects.filter(ProductID=ProductID, CompanyID=CompanyID)
        serialized = PriceListRestSerializer(
            UnitList,
            many=True,
            context={"CompanyID": CompanyID, "PriceRounding": PriceRounding},
        )

        return serialized.data

    def get_Stock(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        WarehouseFromID = self.context.get("WarehouseFromID")
        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID
        check_EnableProductBatchWise = False
        total_stockIN = 0
        total_stockOUT = 0
        if GeneralSettings.objects.filter(
            CompanyID=CompanyID,
            BranchID=BranchID,
            SettingsType="EnableProductBatchWise",
        ).exists():
            check_EnableProductBatchWise = GeneralSettings.objects.get(
                BranchID=BranchID,
                CompanyID=CompanyID,
                SettingsType="EnableProductBatchWise",
            ).SettingsValue
        if (
            check_EnableProductBatchWise == "True"
            or check_EnableProductBatchWise == True
        ):
            if Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
            ).exists():
                Batch_ins = Batch.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
                )
                total_stockIN = Batch_ins.aggregate(Sum("StockIn"))
                total_stockIN = total_stockIN["StockIn__sum"]
                total_stockOUT = Batch_ins.aggregate(Sum("StockOut"))
                total_stockOUT = total_stockOUT["StockOut__sum"]
                # Stock = converted_float(total_stockIN) - converted_float(total_stockOUT)
        else:
            if StockPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
            ):
                stock_ins = StockPosting.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
                )
                total_stockIN = stock_ins.aggregate(Sum("QtyIn"))
                total_stockIN = total_stockIN["QtyIn__sum"]
                total_stockOUT = stock_ins.aggregate(Sum("QtyOut"))
                total_stockOUT = total_stockOUT["QtyOut__sum"]

        Stock = converted_float(total_stockIN) - converted_float(total_stockOUT)
        return Stock

    def get_ProductCode(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID
        product = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
        )

        ProductCode = product.ProductCode
        return ProductCode

    def get_HSNCode(self, sales_details):

        CompanyID = self.context.get("CompanyID")

        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID

        product = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
        )

        HSNCode = product.HSNCode

        return HSNCode

    def get_Qty(self, stockTransfer_details):
        PriceRounding = self.context.get("PriceRounding")
        Qty = stockTransfer_details.Qty
        # Qty = round(Qty,PriceRounding)
        return converted_float(Qty)

    def get_Rate(self, stockTransfer_details):
        PriceRounding = self.context.get("PriceRounding")
        Rate = stockTransfer_details.Rate
        # Rate = round(Rate,PriceRounding)
        return converted_float(Rate)

    def get_Amount(self, stockTransfer_details):
        PriceRounding = self.context.get("PriceRounding")
        Amount = stockTransfer_details.Amount
        # Amount = round(Amount,PriceRounding)
        return converted_float(Amount)

    def get_MaXRate(self, stockTransfer_details):
        PriceRounding = self.context.get("PriceRounding")
        MaxRate = stockTransfer_details.MaxRate
        # MaxRate = round(MaxRate,PriceRounding)
        return converted_float(MaxRate)

    def get_MaxAmount(self, stockTransfer_details):
        PriceRounding = self.context.get("PriceRounding")
        MaxAmount = stockTransfer_details.MaxAmount
        # MaxAmount = round(MaxAmount,PriceRounding)
        if not MaxAmount:
            MaxAmount = 0
        return converted_float(MaxAmount)

    def get_ProductName(self, stockTransfer_details):

        CompanyID = self.context.get("CompanyID")

        ProductID = stockTransfer_details.ProductID
        BranchID = stockTransfer_details.BranchID

        if Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID).exists():
            product = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)
            ProductName = product.ProductName
        else:
            ProductName = ""

        return ProductName

    def get_UnitName(self, stockTransfer_details):

        CompanyID = self.context.get("CompanyID")

        PriceListID = stockTransfer_details.PriceListID
        BranchID = stockTransfer_details.BranchID

        if PriceList.objects.filter(
            CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID
        ).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID
            ).UnitID
            UnitName = Unit.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, UnitID=UnitID
            ).UnitName
        else:
            UnitName = ""

        return UnitName

    def get_unq_id(self, stockTransfer_details):

        CompanyID = self.context.get("CompanyID")

        unq_id = stockTransfer_details.id

        return unq_id

    def get_detailID(self, stockTransfer_details):

        detailID = 0

        return detailID


class StockTransferRegisterReportSerializer(serializers.ModelSerializer):

    WarehouseFromName = serializers.SerializerMethodField()
    WarehouseToName = serializers.SerializerMethodField()
    TotalQty = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    MaxGrandTotal = serializers.SerializerMethodField()

    class Meta:
        model = StockTransferMaster_ID
        fields = (
            "id",
            "StockTransferMasterID",
            "BranchID",
            "Action",
            "VoucherNo",
            "Date",
            "WarehouseFromID",
            "WarehouseFromName",
            "WarehouseToID",
            "WarehouseToName",
            "TotalQty",
            "GrandTotal",
            "MaxGrandTotal",
        )

    def get_WarehouseFromName(self, instance):

        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        WarehouseID = instance.WarehouseFromID
        WarehouseInstance = Warehouse.objects.get(
            CompanyID=CompanyID, WarehouseID=WarehouseID
        )

        WareHouseName = WarehouseInstance.WarehouseName

        return str(WareHouseName)

    def get_WarehouseToName(self, instance):

        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        WarehouseID = instance.WarehouseToID
        WarehouseInstance = Warehouse.objects.get(
            CompanyID=CompanyID, WarehouseID=WarehouseID
        )

        WareHouseName = WarehouseInstance.WarehouseName

        return str(WareHouseName)

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

    def get_MaxGrandTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        MaxGrandTotal = instances.MaxGrandTotal
        MaxGrandTotal = round(MaxGrandTotal, PriceRounding)
        return converted_float(MaxGrandTotal)
