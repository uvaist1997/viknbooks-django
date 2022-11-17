from rest_framework import serializers
from brands.models import StockPosting, Product, ExcessStockMaster, ExcessStockDetails,ShortageStockMaster,ShortageStockDetails,DamageStockMaster,DamageStockDetails,UsedStockMaster,\
UsedStockDetails,Warehouse, Unit, PriceList,AccountLedger
from django.contrib.auth.models import User
from api.v6.priceLists.serializers import PriceListRestSerializer
from brands import models as tables


class StockPostingSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockPosting
        fields = ('id','BranchID','Action','Date','VoucherMasterID','ProductID',
            'BatchID','WareHouseID','QtyIn','QtyOut','Rate','PriceListID','IsActive','CreatedUserID')


def get_voucherNo(CompanyID,BranchID,VoucherType,VoucherMasterID):
    VoucherNo = ""
    Unq_id = ""
    LedgerName = ""
    if VoucherType == 'JL':
        if tables.JournalMaster.objects.filter(CompanyID=CompanyID,JournalMasterID=VoucherMasterID,BranchID=BranchID).exists():
            instances = tables.JournalMaster.objects.get(CompanyID=CompanyID,JournalMasterID=VoucherMasterID,BranchID=BranchID)
            VoucherNo = instances.VoucherNo
            Unq_id = instances.id
    elif VoucherType == 'SI':
        if tables.SalesMaster.objects.filter(CompanyID=CompanyID,SalesMasterID=VoucherMasterID,BranchID=BranchID).exists():
            instances = tables.SalesMaster.objects.get(CompanyID=CompanyID,SalesMasterID=VoucherMasterID,BranchID=BranchID)
            VoucherNo = instances.VoucherNo
            LedgerID = instances.LedgerID
            Unq_id = instances.id
            if tables.AccountLedger.objects.filter(CompanyID=CompanyID,BranchID=BranchID,LedgerID=LedgerID).exists():
                LedgerName = tables.AccountLedger.objects.get(CompanyID=CompanyID,BranchID=BranchID,LedgerID=LedgerID).LedgerName
    elif VoucherType == 'PI':
        if tables.PurchaseMaster.objects.filter(CompanyID=CompanyID,PurchaseMasterID=VoucherMasterID,BranchID=BranchID).exists():
            instances = tables.PurchaseMaster.objects.get(CompanyID=CompanyID,PurchaseMasterID=VoucherMasterID,BranchID=BranchID)
            VoucherNo = instances.VoucherNo
            Unq_id = instances.id
            LedgerID = instances.LedgerID
            if tables.AccountLedger.objects.filter(CompanyID=CompanyID,BranchID=BranchID,LedgerID=LedgerID).exists():
                LedgerName = tables.AccountLedger.objects.get(CompanyID=CompanyID,BranchID=BranchID,LedgerID=LedgerID).LedgerName
    elif VoucherType == 'SR':
        if tables.SalesReturnMaster.objects.filter(CompanyID=CompanyID,SalesReturnMasterID=VoucherMasterID,BranchID=BranchID).exists():
            instances = tables.SalesReturnMaster.objects.get(CompanyID=CompanyID,SalesReturnMasterID=VoucherMasterID,BranchID=BranchID)
            VoucherNo = instances.VoucherNo
            Unq_id = instances.id
            LedgerID = instances.LedgerID
            if tables.AccountLedger.objects.filter(CompanyID=CompanyID,BranchID=BranchID,LedgerID=LedgerID).exists():
                LedgerName = tables.AccountLedger.objects.get(CompanyID=CompanyID,BranchID=BranchID,LedgerID=LedgerID).LedgerName
    elif VoucherType == 'PR':
        if tables.PurchaseReturnMaster.objects.filter(CompanyID=CompanyID,PurchaseReturnMasterID=VoucherMasterID,BranchID=BranchID).exists():
            instances = tables.PurchaseReturnMaster.objects.get(CompanyID=CompanyID,PurchaseReturnMasterID=VoucherMasterID,BranchID=BranchID)
            VoucherNo = instances.VoucherNo
            Unq_id = instances.id
            LedgerID = instances.LedgerID
            if tables.AccountLedger.objects.filter(CompanyID=CompanyID,BranchID=BranchID,LedgerID=LedgerID).exists():
                LedgerName = tables.AccountLedger.objects.get(CompanyID=CompanyID,BranchID=BranchID,LedgerID=LedgerID).LedgerName
    elif VoucherType == 'SO':
        if tables.SalesOrderMaster.objects.filter(CompanyID=CompanyID,SalesOrderMasterID=VoucherMasterID,BranchID=BranchID).exists():
            instances = tables.SalesOrderMaster.objects.get(CompanyID=CompanyID,SalesOrderMasterID=VoucherMasterID,BranchID=BranchID)
            VoucherNo = instances.VoucherNo
            Unq_id = instances.id
            LedgerID = instances.LedgerID
            if tables.AccountLedger.objects.filter(CompanyID=CompanyID,BranchID=BranchID,LedgerID=LedgerID).exists():
                LedgerName = tables.AccountLedger.objects.get(CompanyID=CompanyID,BranchID=BranchID,LedgerID=LedgerID).LedgerName
    elif VoucherType == 'PO':
        if tables.PurchaseOrderMaster.objects.filter(CompanyID=CompanyID,PurchaseOrderMasterID=VoucherMasterID,BranchID=BranchID).exists():
            instances = tables.PurchaseOrderMaster.objects.get(CompanyID=CompanyID,PurchaseOrderMasterID=VoucherMasterID,BranchID=BranchID)
            VoucherNo = instances.VoucherNo
            Unq_id = instances.id
            LedgerID = instances.LedgerID
            if tables.AccountLedger.objects.filter(CompanyID=CompanyID,BranchID=BranchID,LedgerID=LedgerID).exists():
                LedgerName = tables.AccountLedger.objects.get(CompanyID=CompanyID,BranchID=BranchID,LedgerID=LedgerID).LedgerName
    elif VoucherType == 'SE':
        if tables.SalesEstimateMaster.objects.filter(CompanyID=CompanyID,SalesEstimateMasterID=VoucherMasterID,BranchID=BranchID).exists():
            instances = tables.SalesEstimateMaster.objects.get(CompanyID=CompanyID,SalesEstimateMasterID=VoucherMasterID,BranchID=BranchID)
            VoucherNo = instances.VoucherNo
            Unq_id = instances.id
            LedgerID = instances.LedgerID
            if tables.AccountLedger.objects.filter(CompanyID=CompanyID,BranchID=BranchID,LedgerID=LedgerID).exists():
                LedgerName = tables.AccountLedger.objects.get(CompanyID=CompanyID,BranchID=BranchID,LedgerID=LedgerID).LedgerName
    elif VoucherType == 'CP' or VoucherType == 'BP':
        if tables.PaymentMaster.objects.filter(CompanyID=CompanyID,PaymentMasterID=VoucherMasterID,BranchID=BranchID).exists():
            instances = tables.PaymentMaster.objects.get(CompanyID=CompanyID,PaymentMasterID=VoucherMasterID,BranchID=BranchID)
            VoucherNo = instances.VoucherNo
            Unq_id = instances.id
    elif VoucherType == 'CR' or VoucherType == 'BR':
        if tables.ReceiptMaster.objects.filter(CompanyID=CompanyID,ReceiptMasterID=VoucherMasterID,BranchID=BranchID).exists():
            instances = tables.ReceiptMaster.objects.get(CompanyID=CompanyID,ReceiptMasterID=VoucherMasterID,BranchID=BranchID)
            VoucherNo = instances.VoucherNo
            Unq_id = instances.id
    elif VoucherType == 'ST':
        if tables.StockTransferMaster_ID.objects.filter(CompanyID=CompanyID,StockTransferMasterID=VoucherMasterID,BranchID=BranchID).exists():
            instances = tables.StockTransferMaster_ID.objects.get(CompanyID=CompanyID,StockTransferMasterID=VoucherMasterID,BranchID=BranchID)
            VoucherNo = instances.VoucherNo
            Unq_id = instances.id
    elif VoucherType == 'ES':
        if tables.ExcessStockMaster.objects.filter(CompanyID=CompanyID,ExcessStockMasterID=VoucherMasterID,BranchID=BranchID).exists():
            instances = tables.ExcessStockMaster.objects.get(CompanyID=CompanyID,ExcessStockMasterID=VoucherMasterID,BranchID=BranchID)
            VoucherNo = instances.VoucherNo
            Unq_id = instances.id
    elif VoucherType == 'SS':
        if tables.ShortageStockMaster.objects.filter(CompanyID=CompanyID,ShortageStockMasterID=VoucherMasterID,BranchID=BranchID).exists():
            instances = tables.ShortageStockMaster.objects.get(CompanyID=CompanyID,ShortageStockMasterID=VoucherMasterID,BranchID=BranchID)
            VoucherNo = instances.VoucherNo
            Unq_id = instances.id
    elif VoucherType == 'DS':
        if tables.DamageStockMaster.objects.filter(CompanyID=CompanyID,DamageStockMasterID=VoucherMasterID,BranchID=BranchID).exists():
            instances = tables.DamageStockMaster.objects.get(CompanyID=CompanyID,DamageStockMasterID=VoucherMasterID,BranchID=BranchID)
            VoucherNo = instances.VoucherNo
            Unq_id = instances.id
    elif VoucherType == 'US':
        if tables.UsedStockMaster.objects.filter(CompanyID=CompanyID,UsedStockMasterID=VoucherMasterID,BranchID=BranchID).exists():
            instances = tables.UsedStockMaster.objects.get(CompanyID=CompanyID,UsedStockMasterID=VoucherMasterID,BranchID=BranchID)
            VoucherNo = instances.VoucherNo
            Unq_id = instances.id
    elif VoucherType == 'OS':
        if tables.OpeningStockMaster.objects.filter(CompanyID=CompanyID,OpeningStockMasterID=VoucherMasterID,BranchID=BranchID).exists():
            instances = tables.OpeningStockMaster.objects.get(CompanyID=CompanyID,OpeningStockMasterID=VoucherMasterID,BranchID=BranchID)
            VoucherNo = instances.VoucherNo
            Unq_id = instances.id
  
    return VoucherNo,Unq_id,LedgerName


class StockPostingRestSerializer(serializers.ModelSerializer):
    WareHouseName = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()
    UserName = serializers.SerializerMethodField()
    VoucherType = serializers.SerializerMethodField()
    VoucherNo = serializers.SerializerMethodField()
    Unq_id = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()

    class Meta:
        model = StockPosting
        fields = ('id','StockPostingID','BranchID','Action','Date','VoucherMasterID','VoucherType','VoucherNo','ProductID','UnitName','UserName',
            'BatchID','WareHouseID','WareHouseName','QtyIn','QtyOut','Rate','PriceListID','IsActive','CreatedDate','UpdatedDate','CreatedUserID','Unq_id',
            'LedgerName')

    def get_LedgerName(self, instance):
        CompanyID = self.context.get("CompanyID")
        VoucherMasterID = instance.VoucherMasterID
        VoucherType = instance.VoucherType
        BranchID = instance.BranchID
        VoucherNo,Unq_id,LedgerName = get_voucherNo(CompanyID,BranchID,VoucherType,VoucherMasterID)
        return LedgerName


    def get_WareHouseName(self, instance):
        CompanyID = self.context.get("CompanyID")
        WarehouseID = instance.WareHouseID
        BranchID = instance.BranchID
        WareHouseName = ""
        if Warehouse.objects.filter(WarehouseID=WarehouseID,BranchID=BranchID,CompanyID=CompanyID).exists():
            WareHouseName = Warehouse.objects.get(WarehouseID=WarehouseID,BranchID=BranchID,CompanyID=CompanyID).WarehouseName
        return WareHouseName


    def get_VoucherNo(self, instance):
        CompanyID = self.context.get("CompanyID")
        VoucherMasterID = instance.VoucherMasterID
        VoucherType = instance.VoucherType
        BranchID = instance.BranchID
        VoucherNo,Unq_id,LedgerName = get_voucherNo(CompanyID,BranchID,VoucherType,VoucherMasterID)
        return VoucherNo


    def get_Unq_id(self, instance):
        CompanyID = self.context.get("CompanyID")
        VoucherMasterID = instance.VoucherMasterID
        VoucherType = instance.VoucherType
        BranchID = instance.BranchID
        VoucherNo,Unq_id,LedgerName = get_voucherNo(CompanyID,BranchID,VoucherType,VoucherMasterID)
        return str(Unq_id)


    def get_UnitName(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceListID = instance.PriceListID
        BranchID = instance.BranchID
        UnitName = ""
        if PriceList.objects.filter(PriceListID=PriceListID,BranchID=BranchID,CompanyID=CompanyID).exists():
            UnitID = PriceList.objects.get(PriceListID=PriceListID,BranchID=BranchID,CompanyID=CompanyID).UnitID
            UnitName = Unit.objects.get(UnitID=UnitID,BranchID=BranchID,CompanyID=CompanyID).UnitName
        return UnitName


    def get_UserName(self, instance):
        CompanyID = self.context.get("CompanyID")
        CreatedUserID = instance.CreatedUserID
        BranchID = instance.BranchID
        UserName = ""
        if User.objects.filter(id=CreatedUserID).exists():
            UserName = User.objects.get(id=CreatedUserID).username
        return UserName


    def get_VoucherType(self, instance):

        if instance.VoucherType == 'JL':
            VoucherType = 'Journal'
        elif instance.VoucherType == 'SI':
            VoucherType = 'Sales Invoice'
        elif instance.VoucherType == 'PI':
            VoucherType = 'Purchase Invoice'
        elif instance.VoucherType == 'SR':
            VoucherType = 'Sales Return'
        elif instance.VoucherType == 'PR':
            VoucherType = 'Purchase Return'
        elif instance.VoucherType == 'SO':
            VoucherType = 'Sales Order'
        elif instance.VoucherType == 'PO':
            VoucherType = 'Purchase Order'
        elif instance.VoucherType == 'CP':
            VoucherType = 'Cash Payment'
        elif instance.VoucherType == 'BP':
            VoucherType = 'Bank Payment'
        elif instance.VoucherType == 'CR':
            VoucherType = 'Cash Receipt'
        elif instance.VoucherType == 'BR':
            VoucherType = 'Bank Receipt'
        elif instance.VoucherType == 'LOB':
            VoucherType = 'Ledger Opening Balance'
        elif instance.VoucherType == 'WO':
            VoucherType = 'Work Order'
        elif instance.VoucherType == 'ST':
            VoucherType = 'Stock Transfer'
        elif instance.VoucherType == 'ES':
            VoucherType = 'Excess Stock'
        elif instance.VoucherType == 'SS':
            VoucherType = 'Shortage Stock'
        elif instance.VoucherType == 'DS':
            VoucherType = 'Damage Stock'
        elif instance.VoucherType == 'US':
            VoucherType = 'Used Stock'
        elif instance.VoucherType == 'OS':
            VoucherType = 'Opening Stock'
        else:
            VoucherType = instance.VoucherType
        return VoucherType



class StockValueAllSerializer(serializers.ModelSerializer):

    VoucherType = serializers.SerializerMethodField()
    QtyIn = serializers.SerializerMethodField()
    QtyOut = serializers.SerializerMethodField()
    Date = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('ProductID','ProductName','QtyIn','QtyOut','VoucherType','Date')

    def get_QtyIn(self, instance):
        DataBase = self.context.get("DataBase")
        ProductID = instance.ProductID
        BranchID = instance.BranchID
        if StockPosting.objects.filter(ProductID=ProductID,BranchID=BranchID).exists():
            stockInstances = StockPosting.objects.filter(ProductID=ProductID,BranchID=BranchID)
            TotalQtyIn = 0
            for si in stockInstances:
                TotalQtyIn += si.QtyIn
            return TotalQtyIn
        else:
            return ""


    def get_QtyOut(self, instance):
        DataBase = self.context.get("DataBase")
        ProductID = instance.ProductID
        BranchID = instance.BranchID
        if StockPosting.objects.filter(ProductID=ProductID,BranchID=BranchID).exists():
            stockInstances = StockPosting.objects.filter(ProductID=ProductID,BranchID=BranchID)
            TotalQtyOut = 0
            for si in stockInstances:
                TotalQtyOut += si.QtyOut
            return TotalQtyOut
        else:
            return ""


    def get_VoucherType(self, instance):
        
        return ""

    def get_Date(self, instance):
        
        return ""



class StockValueSerializer(serializers.ModelSerializer):

    ProductName = serializers.SerializerMethodField()
    WareHouseName = serializers.SerializerMethodField()
    PurchasePrice = serializers.SerializerMethodField()
    SalesPrice = serializers.SerializerMethodField()
    Qty = serializers.SerializerMethodField()
    

    class Meta:
        model = StockPosting
        fields = ('ProductID','ProductName','WareHouseID','WareHouseName','Date','PurchasePrice','SalesPrice','Qty','Cost','TotalCost')

    def get_ProductName(self, instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = instance.ProductID
        BranchID = instance.BranchID
        ProductName = ""
        if Product.objects.filter(ProductID=ProductID,BranchID=BranchID,CompanyID=CompanyID).exists():
            ProductName = Product.objects.get(ProductID=ProductID,BranchID=BranchID,CompanyID=CompanyID).ProductName
        return ProductName


    def get_WareHouseName(self, instance):
        CompanyID = self.context.get("CompanyID")
        WarehouseID = instance.WareHouseID
        BranchID = instance.BranchID
        WareHouseName = ""
        if Warehouse.objects.filter(WarehouseID=WarehouseID,BranchID=BranchID,CompanyID=CompanyID).exists():
            WareHouseName = Warehouse.objects.get(WarehouseID=WarehouseID,BranchID=BranchID,CompanyID=CompanyID).WarehouseName
        return WareHouseName


    def get_PurchasePrice(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceListID = instance.PriceListID
        BranchID = instance.BranchID
        PurchasePrice = 0
        if PriceList.objects.filter(PriceListID=PriceListID,BranchID=BranchID,CompanyID=CompanyID).exists():
            PurchasePrice = PriceList.objects.get(PriceListID=PriceListID,BranchID=BranchID,CompanyID=CompanyID).PurchasePrice
        return PurchasePrice


    def get_SalesPrice(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceListID = instance.PriceListID
        BranchID = instance.BranchID
        SalesPrice = 0
        if PriceList.objects.filter(PriceListID=PriceListID,BranchID=BranchID,CompanyID=CompanyID).exists():
            SalesPrice = PriceList.objects.get(PriceListID=PriceListID,BranchID=BranchID,CompanyID=CompanyID).SalesPrice
        return SalesPrice


    def get_Qty(self, instance):
        CompanyID = self.context.get("CompanyID")
        PriceListID = instance.PriceListID
        BranchID = instance.BranchID
        SalesPrice = 0
        if PriceList.objects.filter(PriceListID=PriceListID,BranchID=BranchID,CompanyID=CompanyID).exists():
            SalesPrice = PriceList.objects.get(PriceListID=PriceListID,BranchID=BranchID,CompanyID=CompanyID).SalesPrice
        return SalesPrice


   



class StockValueSingleSerializer(serializers.ModelSerializer):

    ProductName = serializers.SerializerMethodField()
    QtyIn = serializers.SerializerMethodField()
    QtyOut = serializers.SerializerMethodField()

    class Meta:
        model = StockPosting
        fields = ('id','StockPostingID','BranchID','Date','VoucherType','ProductID'
            ,'WareHouseID','QtyIn','QtyOut','ProductName')


    def get_ProductName(self, instance):
        
        return ""


    def get_QtyIn(self, instances):

        QtyIn = instances.QtyIn

        QtyIn = round(QtyIn,2)

        return str(QtyIn)


    def get_QtyOut(self, instances):

        QtyOut = instances.QtyOut

        QtyOut = round(QtyOut,2)

        return str(QtyOut)


class ExcessStockMaster1Serializer(serializers.ModelSerializer):
    TotalQty = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    WarehouseName = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    CompanyID = serializers.SerializerMethodField()
    GrandTotal_Rounded = serializers.SerializerMethodField()

    class Meta:
        model = ExcessStockMaster
        fields = ('id','CompanyID','ExcessStockMasterID','BranchID','Action','VoucherNo','Date','Notes',
            'WarehouseID','WarehouseName','TotalQty','GrandTotal','CreatedDate','GrandTotal_Rounded')


    def get_id(self, instances):
        id = instances.id
        return str(id)

    def get_CompanyID(self, instances):
        CompanyID = instances.CompanyID
        return str(CompanyID)


    def get_WarehouseName(self, instances):
        CompanyID = self.context.get("CompanyID")
        WarehouseID = instances.WarehouseID
        BranchID = instances.BranchID
        WarehouseName = ""
        if Warehouse.objects.filter(CompanyID=CompanyID,WarehouseID=WarehouseID,BranchID=BranchID).exists():
            WarehouseName = Warehouse.objects.get(CompanyID=CompanyID,WarehouseID=WarehouseID,BranchID=BranchID).WarehouseName

        return WarehouseName


    def get_TotalQty(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalQty = instances.TotalQty

        TotalQty = round(TotalQty,PriceRounding)

        return float(TotalQty)

    def get_GrandTotal(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        GrandTotal = instances.GrandTotal
        GrandTotal = round(GrandTotal,PriceRounding)

        return float(GrandTotal)

    def get_GrandTotal_Rounded(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        GrandTotal = instances.GrandTotal

        GrandTotal_Rounded = round(GrandTotal, PriceRounding)

        return str(GrandTotal_Rounded)



class ExcessStockMasterSerializer(serializers.ModelSerializer):
    Details = serializers.SerializerMethodField()
    TotalQty = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    WarehouseName = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    CompanyID = serializers.SerializerMethodField()

    class Meta:
        model = ExcessStockMaster
        fields = ('id','CompanyID','ExcessStockMasterID','BranchID','Action','VoucherNo','Date','Notes',
            'WarehouseID','WarehouseName','TotalQty','GrandTotal','CreatedDate','LastUPDDate','Details')


    def get_Details(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ExcessStockMasterID = instances.ExcessStockMasterID
        BranchID = instances.BranchID
        details = ExcessStockDetails.objects.filter(CompanyID=CompanyID,ExcessStockMasterID=ExcessStockMasterID,BranchID=BranchID)
        serialized = ExcessStockDetailSerializer(details,many=True,context={"CompanyID":CompanyID,"PriceRounding" : PriceRounding})

        return serialized.data


    def get_id(self, instances):
        id = instances.id
        return str(id)

    def get_CompanyID(self, instances):
        CompanyID = instances.CompanyID
        return str(CompanyID)


    def get_WarehouseName(self, instances):
        CompanyID = self.context.get("CompanyID")
        WarehouseID = instances.WarehouseID
        BranchID = instances.BranchID
        WarehouseName = ""
        if Warehouse.objects.filter(CompanyID=CompanyID,WarehouseID=WarehouseID,BranchID=BranchID).exists():
            WarehouseName = Warehouse.objects.get(CompanyID=CompanyID,WarehouseID=WarehouseID,BranchID=BranchID).WarehouseName

        return WarehouseName


    def get_TotalQty(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalQty = instances.TotalQty

        # TotalQty = round(TotalQty,PriceRounding)

        return float(TotalQty)

    def get_GrandTotal(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        GrandTotal = instances.GrandTotal
        # GrandTotal = round(GrandTotal,PriceRounding)

        return float(GrandTotal)



class ExcessStockDetailSerializer(serializers.ModelSerializer):

    Stock = serializers.SerializerMethodField()
    ExcessStock = serializers.SerializerMethodField()
    ProductName = serializers.SerializerMethodField()
    detailID = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    CompanyID = serializers.SerializerMethodField()
    UnitList = serializers.SerializerMethodField()

    class Meta:
        model = ExcessStockDetails
        fields = ('id','CompanyID','UnitList','ExcessStockDetailsID','BranchID','Action','ExcessStockMasterID','ProductID','ProductName','Stock',
            'PriceListID','ExcessStock','CreatedDate','LastUPDDate','CreatedUserID','LastUPDUserID','CostPerItem','detailID')



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


    def get_ExcessStock(self, details):
        PriceRounding = int(self.context.get("PriceRounding"))
        ExcessStock = details.ExcessStock
        # ExcessStock = round(ExcessStock,PriceRounding)

        return float(ExcessStock)


    def get_id(self, details):
        id = details.id
        return str(id)

    def get_CompanyID(self, details):
        CompanyID = details.CompanyID
        return str(CompanyID)


    def get_Stock(self, details):
        PriceRounding = int(self.context.get("PriceRounding"))
        Stock = details.Stock
        # Stock = round(Stock,PriceRounding)

        return float(Stock)


    def get_detailID(self, details):
        detailID = 0
        return detailID


    def get_ProductName(self, details):

        CompanyID = self.context.get("CompanyID")

        ProductID = details.ProductID
        BranchID = details.BranchID

        if Product.objects.filter(CompanyID=CompanyID,ProductID=ProductID,BranchID=BranchID).exists():
            product = Product.objects.get(CompanyID=CompanyID,ProductID=ProductID,BranchID=BranchID)
            ProductName = product.ProductName
        else:
            ProductName = ""

        return ProductName


class ShortageStockMaster1Serializer(serializers.ModelSerializer):
    TotalQty = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    CompanyID = serializers.SerializerMethodField()
    WarehouseName = serializers.SerializerMethodField()
    GrandTotal_Rounded = serializers.SerializerMethodField()

    class Meta:
        model = ShortageStockMaster
        fields = ('id','CompanyID','ShortageStockMasterID','BranchID','Action','VoucherNo','Date','Notes','WarehouseName',
            'WarehouseID','TotalQty','GrandTotal','CreatedDate','LastUPDDate','GrandTotal_Rounded')

    def get_GrandTotal_Rounded(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        GrandTotal = instances.GrandTotal

        GrandTotal_Rounded = round(GrandTotal, PriceRounding)

        return str(GrandTotal_Rounded)


    def get_id(self, instances):
        id = instances.id
        return str(id)

    def get_CompanyID(self, instances):
        CompanyID = instances.CompanyID
        return str(CompanyID)

    def get_WarehouseName(self, instances):
        CompanyID = self.context.get("CompanyID")
        WarehouseID = instances.WarehouseID
        BranchID = instances.BranchID
        WarehouseName = ""
        if Warehouse.objects.filter(CompanyID=CompanyID,WarehouseID=WarehouseID,BranchID=BranchID).exists():
            WarehouseName = Warehouse.objects.get(CompanyID=CompanyID,WarehouseID=WarehouseID,BranchID=BranchID).WarehouseName

        return WarehouseName


    def get_TotalQty(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalQty = instances.TotalQty

        TotalQty = round(TotalQty,PriceRounding)

        return float(TotalQty)

    def get_GrandTotal(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        GrandTotal = instances.GrandTotal
        GrandTotal = round(GrandTotal,PriceRounding)

        return float(GrandTotal)


class ShortageStockMasterSerializer(serializers.ModelSerializer):
    Details = serializers.SerializerMethodField()
    TotalQty = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    CompanyID = serializers.SerializerMethodField()
    WarehouseName = serializers.SerializerMethodField()

    class Meta:
        model = ShortageStockMaster
        fields = ('id','CompanyID','ShortageStockMasterID','BranchID','Action','VoucherNo','Date','Notes','WarehouseName',
            'WarehouseID','TotalQty','GrandTotal','CreatedDate','LastUPDDate','Details')


    def get_Details(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ShortageStockMasterID = instances.ShortageStockMasterID
        BranchID = instances.BranchID
        details = ShortageStockDetails.objects.filter(CompanyID=CompanyID,ShortageStockMasterID=ShortageStockMasterID,BranchID=BranchID)
        serialized = ShortageStockDetailSerializer(details,many=True,context={"CompanyID":CompanyID,"PriceRounding" : PriceRounding})

        return serialized.data


    def get_id(self, instances):
        id = instances.id
        return str(id)

    def get_CompanyID(self, instances):
        CompanyID = instances.CompanyID
        return str(CompanyID)

    def get_WarehouseName(self, instances):
        CompanyID = self.context.get("CompanyID")
        WarehouseID = instances.WarehouseID
        BranchID = instances.BranchID
        WarehouseName = ""
        if Warehouse.objects.filter(CompanyID=CompanyID,WarehouseID=WarehouseID,BranchID=BranchID).exists():
            WarehouseName = Warehouse.objects.get(CompanyID=CompanyID,WarehouseID=WarehouseID,BranchID=BranchID).WarehouseName

        return WarehouseName


    def get_TotalQty(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalQty = instances.TotalQty

        TotalQty = round(TotalQty,PriceRounding)

        return float(TotalQty)

    def get_GrandTotal(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        GrandTotal = instances.GrandTotal
        # GrandTotal = round(GrandTotal,PriceRounding)

        return float(GrandTotal)



class ShortageStockDetailSerializer(serializers.ModelSerializer):

    ShortageStock = serializers.SerializerMethodField()
    ProductName = serializers.SerializerMethodField()
    detailID = serializers.SerializerMethodField()
    Stock = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    CompanyID = serializers.SerializerMethodField()
    UnitList = serializers.SerializerMethodField()


    class Meta:
        model = ShortageStockDetails
        fields = ('id','CompanyID','UnitList','ShortageStockDetailsID','BranchID','Action','ShortageStockMasterID','ProductID','ProductName','Stock',
            'PriceListID','ShortageStock','CreatedDate','LastUPDDate','CreatedUserID','LastUPDUserID','CostPerItem','detailID')


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



    def get_ShortageStock(self, details):
        PriceRounding = int(self.context.get("PriceRounding"))
        ShortageStock = details.ShortageStock
        # ShortageStock = round(ShortageStock,PriceRounding)

        return float(ShortageStock)

    def get_id(self, details):
        id = details.id
        return str(id)

    def get_CompanyID(self, details):
        CompanyID = details.CompanyID
        return str(CompanyID)

    def get_Stock(self, details):
        PriceRounding = int(self.context.get("PriceRounding"))
        Stock = details.Stock
        # Stock = round(Stock,PriceRounding)
        return float(Stock)


    def get_detailID(self, details):
        detailID = 0
        return detailID


    def get_ProductName(self, details):

        CompanyID = self.context.get("CompanyID")

        ProductID = details.ProductID
        BranchID = details.BranchID

        if Product.objects.filter(CompanyID=CompanyID,ProductID=ProductID,BranchID=BranchID).exists():
            product = Product.objects.get(CompanyID=CompanyID,ProductID=ProductID,BranchID=BranchID)
            ProductName = product.ProductName
        else:
            ProductName = ""

        return ProductName


class DamageStockMaster1Serializer(serializers.ModelSerializer):
    GrandTotal_Rounded = serializers.SerializerMethodField()
    TotalQty = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    CompanyID = serializers.SerializerMethodField()
    WarehouseName = serializers.SerializerMethodField()

    class Meta:
        model = DamageStockMaster
        fields = ('id','CompanyID','DamageStockMasterID','BranchID','Action','VoucherNo','Date','Notes',
            'WarehouseID','WarehouseName','TotalQty','GrandTotal','CreatedDate','LastUPDDate','GrandTotal_Rounded')


    def get_GrandTotal_Rounded(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        GrandTotal = instances.GrandTotal

        GrandTotal_Rounded = round(GrandTotal, PriceRounding)

        return str(GrandTotal_Rounded)


    def get_TotalQty(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalQty = instances.TotalQty

        TotalQty = round(TotalQty,PriceRounding)

        return float(TotalQty)

    def get_GrandTotal(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        GrandTotal = instances.GrandTotal
        GrandTotal = round(GrandTotal,PriceRounding)

        return float(GrandTotal)

    def get_WarehouseName(self, instances):
        CompanyID = self.context.get("CompanyID")
        WarehouseID = instances.WarehouseID
        BranchID = instances.BranchID
        WarehouseName = ""
        if Warehouse.objects.filter(CompanyID=CompanyID,WarehouseID=WarehouseID,BranchID=BranchID).exists():
            WarehouseName = Warehouse.objects.get(CompanyID=CompanyID,WarehouseID=WarehouseID,BranchID=BranchID).WarehouseName

        return WarehouseName


    def get_id(self, instances):
        id = instances.id
        return str(id)

    def get_CompanyID(self, instances):
        CompanyID = instances.CompanyID
        return str(CompanyID)




class DamageStockMasterSerializer(serializers.ModelSerializer):
    Details = serializers.SerializerMethodField()
    TotalQty = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    CompanyID = serializers.SerializerMethodField()
    WarehouseName = serializers.SerializerMethodField()

    class Meta:
        model = DamageStockMaster
        fields = ('id','CompanyID','DamageStockMasterID','BranchID','Action','VoucherNo','Date','Notes',
            'WarehouseID','WarehouseName','TotalQty','GrandTotal','CreatedDate','LastUPDDate','Details')


    def get_Details(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        DamageStockMasterID = instances.DamageStockMasterID
        BranchID = instances.BranchID
        details = DamageStockDetails.objects.filter(CompanyID=CompanyID,DamageStockMasterID=DamageStockMasterID,BranchID=BranchID)
        serialized = DamageStockDetailSerializer(details,many=True,context={"CompanyID":CompanyID,"PriceRounding" : PriceRounding})

        return serialized.data


    def get_TotalQty(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalQty = instances.TotalQty

        # TotalQty = round(TotalQty,PriceRounding)

        return float(TotalQty)

    def get_GrandTotal(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        GrandTotal = instances.GrandTotal
        # GrandTotal = round(GrandTotal,PriceRounding)

        return float(GrandTotal)

    def get_WarehouseName(self, instances):
        CompanyID = self.context.get("CompanyID")
        WarehouseID = instances.WarehouseID
        BranchID = instances.BranchID
        WarehouseName = ""
        if Warehouse.objects.filter(CompanyID=CompanyID,WarehouseID=WarehouseID,BranchID=BranchID).exists():
            WarehouseName = Warehouse.objects.get(CompanyID=CompanyID,WarehouseID=WarehouseID,BranchID=BranchID).WarehouseName

        return WarehouseName


    def get_id(self, instances):
        id = instances.id
        return str(id)

    def get_CompanyID(self, instances):
        CompanyID = instances.CompanyID
        return str(CompanyID)



class DamageStockDetailSerializer(serializers.ModelSerializer):

    DamageStock = serializers.SerializerMethodField()
    ProductName = serializers.SerializerMethodField()
    detailID = serializers.SerializerMethodField()
    Stock = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    CompanyID = serializers.SerializerMethodField()
    UnitList = serializers.SerializerMethodField()


    class Meta:
        model = DamageStockDetails
        fields = ('id','UnitList','CompanyID','DamageStockDetailsID','BranchID','Action','DamageStockMasterID','ProductID','ProductName','Stock',
            'PriceListID','DamageStock','CreatedDate','LastUPDDate','CreatedUserID','LastUPDUserID','CostPerItem','detailID')



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


    def get_DamageStock(self, details):
        PriceRounding = int(self.context.get("PriceRounding"))
        DamageStock = details.DamageStock
        # DamageStock = round(DamageStock,PriceRounding)

        return float(DamageStock)

    def get_Stock(self, details):
        PriceRounding = int(self.context.get("PriceRounding"))
        Stock = details.Stock
        # Stock = round(Stock,PriceRounding)
        return float(Stock)


    def get_detailID(self, details):
        detailID = 0
        return detailID

    def get_id(self, details):
        id = details.id
        return str(id)

    def get_CompanyID(self, details):
        CompanyID = details.CompanyID
        return str(CompanyID)


    def get_ProductName(self, details):

        CompanyID = self.context.get("CompanyID")

        ProductID = details.ProductID
        BranchID = details.BranchID

        if Product.objects.filter(CompanyID=CompanyID,ProductID=ProductID,BranchID=BranchID).exists():
            product = Product.objects.get(CompanyID=CompanyID,ProductID=ProductID,BranchID=BranchID)
            ProductName = product.ProductName
        else:
            ProductName = ""

        return ProductName


class UsedStockMaster1Serializer(serializers.ModelSerializer):
    GrandTotal_Rounded = serializers.SerializerMethodField()
    TotalQty = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    CompanyID = serializers.SerializerMethodField()
    WarehouseName = serializers.SerializerMethodField()

    class Meta:
        model = UsedStockMaster
        fields = ('id','CompanyID','UsedStockMasterID','BranchID','Action','VoucherNo','Date','Notes',
            'WarehouseID','WarehouseName','TotalQty','GrandTotal','CreatedDate','LastUPDDate','GrandTotal_Rounded')


    def get_GrandTotal_Rounded(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        GrandTotal = instances.GrandTotal

        GrandTotal_Rounded = round(GrandTotal, PriceRounding)

        return str(GrandTotal_Rounded)



    def get_TotalQty(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalQty = instances.TotalQty

        TotalQty = round(TotalQty,PriceRounding)

        return float(TotalQty)

    def get_GrandTotal(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        GrandTotal = instances.GrandTotal
        GrandTotal = round(GrandTotal,PriceRounding)

        return float(GrandTotal)


    def get_WarehouseName(self, instances):
        CompanyID = self.context.get("CompanyID")
        WarehouseID = instances.WarehouseID
        BranchID = instances.BranchID
        WarehouseName = ""
        if Warehouse.objects.filter(CompanyID=CompanyID,WarehouseID=WarehouseID,BranchID=BranchID).exists():
            WarehouseName = Warehouse.objects.get(CompanyID=CompanyID,WarehouseID=WarehouseID,BranchID=BranchID).WarehouseName

        return WarehouseName


    def get_id(self, instances):
        id = instances.id
        return str(id)

    def get_CompanyID(self, instances):
        CompanyID = instances.CompanyID
        return str(CompanyID)


class UsedStockMasterSerializer(serializers.ModelSerializer):
    Details = serializers.SerializerMethodField()
    TotalQty = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    CompanyID = serializers.SerializerMethodField()
    WarehouseName = serializers.SerializerMethodField()

    class Meta:
        model = UsedStockMaster
        fields = ('id','CompanyID','UsedStockMasterID','BranchID','Action','VoucherNo','Date','Notes',
            'WarehouseID','WarehouseName','TotalQty','GrandTotal','CreatedDate','LastUPDDate','Details')


    def get_Details(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        UsedStockMasterID = instances.UsedStockMasterID
        BranchID = instances.BranchID
        details = UsedStockDetails.objects.filter(CompanyID=CompanyID,UsedStockMasterID=UsedStockMasterID,BranchID=BranchID)
        serialized = UsedStockDetailSerializer(details,many=True,context={"CompanyID":CompanyID,"PriceRounding" : PriceRounding})

        return serialized.data


    def get_TotalQty(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalQty = instances.TotalQty

        # TotalQty = round(TotalQty,PriceRounding)

        return float(TotalQty)

    def get_GrandTotal(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        GrandTotal = instances.GrandTotal
        # GrandTotal = round(GrandTotal,PriceRounding)

        return float(GrandTotal)


    def get_WarehouseName(self, instances):
        CompanyID = self.context.get("CompanyID")
        WarehouseID = instances.WarehouseID
        BranchID = instances.BranchID
        WarehouseName = ""
        if Warehouse.objects.filter(CompanyID=CompanyID,WarehouseID=WarehouseID,BranchID=BranchID).exists():
            WarehouseName = Warehouse.objects.get(CompanyID=CompanyID,WarehouseID=WarehouseID,BranchID=BranchID).WarehouseName

        return WarehouseName


    def get_id(self, instances):
        id = instances.id
        return str(id)

    def get_CompanyID(self, instances):
        CompanyID = instances.CompanyID
        return str(CompanyID)



class UsedStockDetailSerializer(serializers.ModelSerializer):

    UsedStock = serializers.SerializerMethodField()
    ProductName = serializers.SerializerMethodField()
    detailID = serializers.SerializerMethodField()
    Stock = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    CompanyID = serializers.SerializerMethodField()
    UnitList = serializers.SerializerMethodField()

    class Meta:
        model = UsedStockDetails
        fields = ('id','CompanyID','UsedStockDetailsID','BranchID','Action','UsedStockMasterID','ProductID','ProductName','Stock',
            'PriceListID','UsedStock','UnitList','CreatedDate','LastUPDDate','CreatedUserID','LastUPDUserID','CostPerItem','detailID')


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

    def get_UsedStock(self, details):
        PriceRounding = int(self.context.get("PriceRounding"))
        UsedStock = details.UsedStock
        # UsedStock = round(UsedStock,PriceRounding)

        return float(UsedStock)

    def get_Stock(self, details):
        PriceRounding = int(self.context.get("PriceRounding"))
        Stock = details.Stock
        # Stock = round(Stock,PriceRounding)
        return float(Stock)


    def get_detailID(self, details):
        detailID = 0
        return detailID


    def get_id(self, details):
        id = details.id
        return str(id)

    def get_CompanyID(self, details):
        CompanyID = details.CompanyID
        return str(CompanyID)


    def get_ProductName(self, details):

        CompanyID = self.context.get("CompanyID")

        ProductID = details.ProductID
        BranchID = details.BranchID

        if Product.objects.filter(CompanyID=CompanyID,ProductID=ProductID,BranchID=BranchID).exists():
            product = Product.objects.get(CompanyID=CompanyID,ProductID=ProductID,BranchID=BranchID)
            ProductName = product.ProductName
        else:
            ProductName = ""

        return ProductName
