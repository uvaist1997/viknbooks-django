from rest_framework import serializers
from brands import models as table
from api.v8.priceLists.serializers import PriceListRestSerializer
from api.v8.companySettings.serializers import CompanySettingsRestSerializer


class POSHoldMasterSerializer(serializers.ModelSerializer):

    class Meta:
        model = table.POSHoldMaster
        fields = ('id','BranchID','VoucherNo','InvoiceNo','Date','LedgerID',
            'PriceCategoryID','EmployeeID','SalesAccount',
            'HoldStatus','CustomerName','Address1','Address2','Address3','Notes',
            'FinacialYearID','TotalTax','NetTotal','BillDiscount','GrandTotal',
            'RoundOff','CashReceived','CashAmount','BankAmount','WarehouseID','TableID',
            'SeatNumber','NoOfGuests','INOUT','TokenNumber','IsActive','CreatedDate','CreatedUserID')


class POSHoldMasterRestSerializer(serializers.ModelSerializer):

    POSHoldDetails = serializers.SerializerMethodField()

    class Meta:
        model = table.POSHoldMaster
        fields = ('id','POSHoldMasterID','BranchID','Action','VoucherNo','InvoiceNo','Date','LedgerID',
            'PriceCategoryID','EmployeeID','SalesAccount',
            'HoldStatus','CustomerName','Address1','Address2','Address3','Notes','FinacialYearID',
            'TotalTax','NetTotal','BillDiscount','GrandTotal','RoundOff','CashReceived','CashAmount',
            'BankAmount','WarehouseID','TableID','SeatNumber','NoOfGuests','INOUT','TokenNumber','IsActive','CreatedDate','CreatedUserID','POSHoldDetails')


    def get_POSHoldDetails(self, instances):
        poshold_details = table.POSHoldDetails.objects.filter(POSHoldMasterID=instances.POSHoldMasterID,BranchID=instances.BranchID)
        serialized = POSHoldDetailsRestSerializer(poshold_details,many=True,)

        return serialized.data 




class POSHoldDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = table.POSHoldDetails
        fields = ('id','BranchID','ProductID','Qty','FreeQty',
            'UnitPrice','RateWithTax','CostPerPrice',
            'PriceListID','TaxID','TaxType','DiscountPerc','DiscountAmount','GrossAmount',
            'TaxableAmount','VATPerc','VATAmount','SGSTPerc','SGSTAmount',
            'CGSTPerc','CGSTAmount','IGSTPerc','IGSTAmount','NetAmount','Flavour')


class POSHoldDetailsRestSerializer(serializers.ModelSerializer):

    class Meta:
        model = table.POSHoldDetails
        fields = ('id','POSHoldDetailsID','BranchID','Action','POSHoldMasterID','ProductID','Qty','FreeQty',
            'UnitPrice','RateWithTax','CostPerPrice',
            'PriceListID','TaxID','TaxType','DiscountPerc','DiscountAmount','GrossAmount','TaxableAmount',
            'VATPerc','VATAmount','SGSTPerc','SGSTAmount','CGSTPerc','CGSTAmount','IGSTPerc',
            'IGSTAmount','NetAmount','Flavour')



class POS_Role_Serializer(serializers.ModelSerializer):
    class Meta:
        model = table.POS_Role
        fields = ('id','RoleName','show_dining','show_take_away','show_online','show_car','show_kitchen')


class POS_User_Serializer(serializers.ModelSerializer):
    UserName = serializers.SerializerMethodField()
    RoleName = serializers.SerializerMethodField()
    class Meta:
        model = table.POS_User
        fields = ('id','User','UserName','Role','RoleName','PinNo',)

    def get_UserName(self, instances):
        User = instances.User
        return User.FirstName

    def get_RoleName(self, instances):
        Role = instances.Role
        return Role.RoleName


class POS_Table_Serializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    priceid = serializers.SerializerMethodField()
    SalesOrderID = serializers.SerializerMethodField()
    SalesMasterID = serializers.SerializerMethodField()
    SalesOrderGrandTotal = serializers.SerializerMethodField()
    SalesGrandTotal = serializers.SerializerMethodField()
    OrderTime = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    class Meta:
        model = table.POS_Table
        fields = ('id','title','description','PriceCategory','Status','priceid','SalesOrderID','SalesMasterID'
            ,'SalesOrderGrandTotal','SalesGrandTotal','OrderTime','IsActive')


    def get_id(self, instances):
        id = instances.id
        return str(id)

    def get_SalesMasterID(self, instances):
        table_id = instances.id
        CompanyID = instances.CompanyID
        BranchID = instances.BranchID
        SalesMasterID = ""
        if table.SalesMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Table__id=table_id,Status="Invoiced").exists():
            sales_invoice = table.SalesMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Table__id=table_id,Status="Invoiced").first()
            SalesMasterID = sales_invoice.id
        return str(SalesMasterID)


    def get_SalesOrderID(self, instances):
        table_id = instances.id
        CompanyID = instances.CompanyID
        BranchID = instances.BranchID
        salesOrderID = ""
        if table.SalesOrderMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Table__id=table_id,Status="Ordered").exists():
            sales_order = table.SalesOrderMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Table__id=table_id,Status="Ordered").first()
            salesOrderID = sales_order.id
        return str(salesOrderID)


    def get_OrderTime(self, instances):
        table_id = instances.id
        CompanyID = instances.CompanyID
        BranchID = instances.BranchID
        OrderTime = ""
        if table.SalesOrderMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Table__id=table_id,Status="Ordered").exists():
            sales_order = table.SalesOrderMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Table__id=table_id,Status="Ordered").first()
            OrderTime = sales_order.OrderTime
        return OrderTime


    def get_SalesOrderGrandTotal(self, instances):
        table_id = instances.id
        CompanyID = instances.CompanyID
        BranchID = instances.BranchID
        GrandTotal = 0
        if table.SalesOrderMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Table__id=table_id,Status="Ordered").exists():
            sales_order = table.SalesOrderMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Table__id=table_id,Status="Ordered").first()
            GrandTotal = sales_order.GrandTotal
        return float(GrandTotal)


    def get_SalesGrandTotal(self, instances):
        table_id = instances.id
        CompanyID = instances.CompanyID
        BranchID = instances.BranchID
        GrandTotal = 0
        if table.SalesMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Table__id=table_id,Status="Invoiced").exists():
            sales_invoice = table.SalesMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Table__id=table_id,Status="Invoiced").first()
            GrandTotal = sales_invoice.GrandTotal
        return float(GrandTotal)
    

    def get_title(self, instances):
        title = instances.TableName
        return title

    def get_description(self, instances):
        description = ""
        if instances.PriceCategory:
            description = instances.PriceCategory.PriceCategoryName
        return description

    def get_priceid(self, instances):
        priceid = ""
        if instances.PriceCategory:
            priceid = instances.PriceCategory.id
        return str(priceid)


class POS_ProductGroup_Serializer(serializers.ModelSerializer):
    class Meta:
        model = table.ProductGroup
        fields = ('id','ProductGroupID','GroupName')


class POS_Product_Serializer(serializers.ModelSerializer):
    DefaultUnitID = serializers.SerializerMethodField()
    DefaultUnitName = serializers.SerializerMethodField()
    DefaultSalesPrice = serializers.SerializerMethodField()
    DefaultPurchasePrice = serializers.SerializerMethodField()
    GST_SalesTax = serializers.SerializerMethodField()
    SalesTax = serializers.SerializerMethodField()
    GST_TaxName = serializers.SerializerMethodField()
    VAT_TaxName = serializers.SerializerMethodField()
    GST_ID = serializers.SerializerMethodField()

    class Meta:
        model = table.Product
        fields = ('id','ProductID','ProductName','DefaultUnitID','DefaultUnitName','DefaultSalesPrice','DefaultPurchasePrice',
            'GST_SalesTax','SalesTax','GST_TaxName','VAT_TaxName','GST_ID','is_inclusive','VatID','Description')


    def get_GST_ID(self, instances):
        CompanyID = self.context.get("CompanyID")
        GST_ID = instances.GST
        return GST_ID


    def get_GST_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")
        TaxID = instances.GST
        BranchID = instances.BranchID
        GST_TaxName = ""
        if table.TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = table.TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
            GST_TaxName = tax.TaxName

        return GST_TaxName

    def get_VAT_TaxName(self, instances):
        CompanyID = self.context.get("CompanyID")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        VAT_TaxName = ""
        if table.TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = table.TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
            VAT_TaxName = tax.TaxName

        return VAT_TaxName


    def get_SalesTax(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        TaxID = instances.VatID
        BranchID = instances.BranchID
        SalesTax = ""
        if table.TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID).exists():
            tax = table.TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=TaxID, BranchID=BranchID)
            SalesTax = tax.SalesTax
        return str(SalesTax)

    def get_GST_SalesTax(self, instance):
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

    def get_DefaultUnitID(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        DefaultUnitID = 0
        if table.PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            DefaultUnitID = table.PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).PriceListID
        return DefaultUnitID


    def get_DefaultUnitName(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        UnitID = 0
        DefaultUnitName = ""
        if table.PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            UnitID = table.PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).UnitID
            DefaultUnitName = table.Unit.objects.get(
                BranchID=BranchID, UnitID=UnitID, CompanyID=CompanyID).UnitName

        return DefaultUnitName


    def get_DefaultSalesPrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if table.PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            unitInstance = table.PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
            get_DefaultSalesPrice = unitInstance.SalesPrice
        else:
            get_DefaultSalesPrice = 0

        return get_DefaultSalesPrice


    def get_DefaultPurchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        if table.PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True).exists():
            unitInstance = table.PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID, DefaultUnit=True)
            DefaultPurchasePrice = unitInstance.PurchasePrice
        else:
            DefaultPurchasePrice = 0

        return DefaultPurchasePrice



class POS_Order_Serializer(serializers.ModelSerializer):
    SalesOrderID = serializers.SerializerMethodField()
    SalesOrderGrandTotal = serializers.SerializerMethodField()
    SalesGrandTotal = serializers.SerializerMethodField()
    SalesID = serializers.SerializerMethodField()
    class Meta:
        model = table.SalesOrderMaster
        fields = ('SalesOrderID','CustomerName','TokenNumber','Phone','Status','Type','SalesOrderGrandTotal','SalesID','OrderTime',
            'SalesGrandTotal')

    def get_SalesOrderID(self, instances):
        SalesOrderID = instances.id
        return str(SalesOrderID)

    def get_SalesOrderGrandTotal(self, instances):
        SalesOrderGrandTotal = instances.GrandTotal
        return str(SalesOrderGrandTotal)


    def get_SalesGrandTotal(self, instances):
        InvoiceID = instances.InvoiceID
        BranchID = instances.BranchID
        CompanyID = instances.CompanyID
        GrandTotal = ""
        if table.SalesMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,SalesMasterID=InvoiceID).exists():
            GrandTotal = table.SalesMaster.objects.get(CompanyID=CompanyID,BranchID=BranchID,SalesMasterID=InvoiceID).GrandTotal
        return str(GrandTotal)

    def get_SalesID(self, instances):
        InvoiceID = instances.InvoiceID
        BranchID = instances.BranchID
        CompanyID = instances.CompanyID
        SalesID = ""
        if table.SalesMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,SalesMasterID=InvoiceID).exists():
            SalesID = table.SalesMaster.objects.get(CompanyID=CompanyID,BranchID=BranchID,SalesMasterID=InvoiceID).id
        return str(SalesID)



class OrderReason_Serializer(serializers.ModelSerializer):
    class Meta:
        model = table.CancelReasons
        fields = ('id','BranchID','Reason')

    


class POS_Sales_PrintSerializer(serializers.ModelSerializer):

    SalesDetails = serializers.SerializerMethodField()
    TotalGrossAmt = serializers.SerializerMethodField()
    AddlDiscPercent = serializers.SerializerMethodField()
    AddlDiscAmt = serializers.SerializerMethodField()
    TotalDiscount = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    NetTotal = serializers.SerializerMethodField()
    AdditionalCost = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    RoundOff = serializers.SerializerMethodField()
    CashReceived = serializers.SerializerMethodField()
    CashAmount = serializers.SerializerMethodField()
    BankAmount = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    BillDiscPercent = serializers.SerializerMethodField()
    BillDiscAmt = serializers.SerializerMethodField()
    qr_image = serializers.SerializerMethodField()
    GrandTotal_print = serializers.SerializerMethodField()
    NetTotal_print = serializers.SerializerMethodField()
    GrossAmt_print = serializers.SerializerMethodField()
    TotalDiscount_print = serializers.SerializerMethodField()
    TotalTax_print = serializers.SerializerMethodField()
    Balance_print = serializers.SerializerMethodField()
    VATAmount_print = serializers.SerializerMethodField()
    GSTNumber = serializers.SerializerMethodField()
    GST_Treatment = serializers.SerializerMethodField()
    # =====
    Tax_no = serializers.SerializerMethodField()
    CRNo = serializers.SerializerMethodField()
    Mobile = serializers.SerializerMethodField()
    City = serializers.SerializerMethodField()
    State = serializers.SerializerMethodField()
    Country = serializers.SerializerMethodField()
    PostalCode = serializers.SerializerMethodField()
    PrintCustomerName = serializers.SerializerMethodField()
    PrintAddress = serializers.SerializerMethodField()
    CompanyDetails = serializers.SerializerMethodField()
    OrderPhone = serializers.SerializerMethodField()


    class Meta:
        model = table.SalesMaster

        fields = ('id','Tax_no','CRNo','Mobile','City','State','Country','PostalCode','GrossAmt_print','VATAmount_print','NetTotal_print','TotalTax_print','Balance_print', 'TotalDiscount_print','GrandTotal_print','qr_image', 'BranchID', 'VoucherNo', 'Date',
                    'LedgerName', 'OldLedgerBalance', 'Country_of_Supply','State_of_Supply','CustomerName', 'Address1', 'Address2', 'Address3','PrintAddress',
                  'Notes', 'FinacialYearID', 'TotalGrossAmt', 'AddlDiscPercent', 'AddlDiscAmt', 'TotalDiscount', 'TotalTax','GST_Treatment','GSTNumber',
                  'NetTotal', 'AdditionalCost', 'GrandTotal', 'RoundOff', 'CashReceived', 'CashAmount', 'BankAmount',  'CreatedUserID',
                   'BillDiscPercent', 'BillDiscAmt', 'VATAmount', 'SGSTAmount', 'CGSTAmount', 'IGSTAmount','PrintCustomerName',
                   'Balance', 'SalesDetails','CompanyDetails','OrderPhone')



    def get_CompanyDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        request = self.context.get("request")
        serialized = CompanySettingsRestSerializer(
            CompanyID, context={"request": request})
        return serialized.data


    def get_OrderPhone(self, instances):
        CompanyID = self.context.get("CompanyID")
        InvoiceID = instances.SalesMasterID
        BranchID = instances.BranchID
        Phone = ""
        if table.SalesOrderMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,InvoiceID=InvoiceID).exists():
            order_instance = table.SalesOrderMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,InvoiceID=InvoiceID).first()
            Phone = order_instance.Phone
        return Phone


    def get_PrintAddress(self, instances):
        CompanyID = self.context.get("CompanyID")
        Address = ""
        LedgerID = instances.LedgerID
        if table.Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
            Address = table.Parties.objects.filter(
                LedgerID=LedgerID, CompanyID=CompanyID).first().Address1
        return Address


    def get_PrintCustomerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        DisplayName = ""
        LedgerID = instances.LedgerID
        if table.Parties.objects.filter(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID).exists():
            party = table.Parties.objects.get(
                LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID)
            DisplayName = party.DisplayName
        return DisplayName

    def get_GST_Treatment(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        GST_Treatment = instances.GST_Treatment
        if not GST_Treatment:
            GST_Treatment = ""
            if table.Parties.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).exists():
                pary_ins = table.Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).first()
                GST_Treatment = pary_ins.GST_Treatment
        return str(GST_Treatment)


    def get_Tax_no(self, instances):

        CompanyID = self.context.get("CompanyID")
        Tax_no = ""
        if table.Parties.objects.filter(LedgerID=instances.LedgerID, CompanyID=CompanyID).exists():
            Tax_no = table.Parties.objects.get(LedgerID=instances.LedgerID, CompanyID=CompanyID).VATNumber

        return str(Tax_no)

    def get_CRNo(self, instances):

        CompanyID = self.context.get("CompanyID")
        CR_no = ""
        if table.Parties.objects.filter(LedgerID=instances.LedgerID, CompanyID=CompanyID).exists():
            CR_no = table.Parties.objects.get(LedgerID=instances.LedgerID, CompanyID=CompanyID).CRNo

        return str(CR_no)

    def get_Mobile(self, instances):

        CompanyID = self.context.get("CompanyID")
        Mobile = ""
        if table.Parties.objects.filter(LedgerID=instances.LedgerID, CompanyID=CompanyID).exists():
            Mobile = table.Parties.objects.get(LedgerID=instances.LedgerID, CompanyID=CompanyID).Mobile

        return str(Mobile)

    def get_City(self, instances):
        CompanyID = self.context.get("CompanyID")
        
        City = ""
        
        LedgerID = instances.LedgerID
        if table.Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
            City = table.Parties.objects.filter(
                LedgerID=LedgerID, CompanyID=CompanyID).first().City

        return City

    def get_State(self, instances):
        CompanyID = self.context.get("CompanyID")
        State_Name = ""
        LedgerID = instances.LedgerID
        if table.Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
            if table.Parties.objects.get(LedgerID=LedgerID, CompanyID=CompanyID).State:
                pk = table.Parties.objects.filter(
                    LedgerID=LedgerID, CompanyID=CompanyID).first().State
                a = table.Parties.objects.filter(
                    LedgerID=LedgerID, CompanyID=CompanyID)
                # for i in a:
                #     print(i.State,"//////////////////////UVAIS///////////////////////////")
                if table.State.objects.filter(pk=pk).exists():
                    State_Name = table.State.objects.get(pk=pk).Name

        return State_Name

    def get_Country(self, instances):
        CompanyID = self.context.get("CompanyID")
        
        Country_Name = ""
        
        LedgerID = instances.LedgerID
        if table.Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
            if table.Parties.objects.get(LedgerID=LedgerID, CompanyID=CompanyID).Country:
                pk = table.Parties.objects.filter(
                    LedgerID=LedgerID, CompanyID=CompanyID).first().Country
                if table.Country.objects.filter(pk=pk).exists():
                    Country_Name = table.Country.objects.get(pk=pk).Country_Name

        return Country_Name

    def get_PostalCode(self, instances):
        CompanyID = self.context.get("CompanyID")
        PostalCode = ""
        LedgerID = instances.LedgerID
        if table.Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
            PostalCode = table.Parties.objects.filter(
                LedgerID=LedgerID, CompanyID=CompanyID).first().PostalCode

        return PostalCode

    def get_GSTNumber(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        GSTNumber = ""
        if table.Parties.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).exists():
            pary_ins = table.Parties.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).first()
            GSTNumber = pary_ins.GSTNumber
        return str(GSTNumber)
    

    def get_VATAmount_print(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        VATAmount = instances.VATAmount
        VATAmount = str(round(VATAmount, PriceRounding))
        return str(VATAmount)

    def get_Balance_print(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        Balance = instances.Balance
        Balance = str(round(Balance, PriceRounding))
        return str(Balance)

    def get_TotalTax_print(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalTax = instances.TotalTax

        TotalTax = str(round(TotalTax, PriceRounding))

        return str(TotalTax)


    def get_TotalDiscount_print(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalDiscount = instances.TotalDiscount

        TotalDiscount = str(round(TotalDiscount, PriceRounding))

        return str(TotalDiscount)


    def get_GrossAmt_print(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        GrossAmount = instances.TotalGrossAmt

        GrossAmt_print = str(round(GrossAmount, PriceRounding))

        return str(GrossAmt_print)


    def get_NetTotal_print(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        NetTotal = instances.NetTotal

        NetTotal = str(round(NetTotal, PriceRounding))

        return str(NetTotal)


    def get_GrandTotal_print(self, instances):
        CompanyID = self.context.get("CompanyID")

        PriceRounding = self.context.get("PriceRounding")

        GrandTotal = instances.GrandTotal
        GrandTotal_print = str(round(GrandTotal, PriceRounding))
        return str(GrandTotal_print)


    def get_qr_image(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        pk = str(instances.id)
        qr_image = None
        if table.QrCode.objects.filter(voucher_type="SI",master_id=pk).exists():
            qr_image = table.QrCode.objects.get(voucher_type="SI",master_id=pk).url

        return qr_image



    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        if table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID).exists():
            ledger = table.AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)

            LedgerName = ledger.LedgerName
        else:
            LedgerName = ""

        return LedgerName



    def get_SalesDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        print(PriceRounding)

        SalesMasterID = instances.SalesMasterID
        BranchID = instances.BranchID
        print(SalesMasterID, 'SalesMasterID')
        sales_details = table.SalesDetails.objects.filter(
            CompanyID=CompanyID, SalesMasterID=SalesMasterID, BranchID=BranchID).order_by('SalesDetailsID')
        for i in sales_details:
            print(i.SalesMasterID)
        serialized = POS_SalesDetailsSerializer(sales_details, many=True, context={"CompanyID": CompanyID,
                                                                                   "PriceRounding": PriceRounding, })

        return serialized.data

    def get_TotalGrossAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalGrossAmt = instances.TotalGrossAmt

        # TotalGrossAmt = round(TotalGrossAmt, PriceRounding)

        return float(TotalGrossAmt)

    def get_AddlDiscPercent(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        AddlDiscPercent = instances.AddlDiscPercent

        # AddlDiscPercent = round(AddlDiscPercent, PriceRounding)

        return float(AddlDiscPercent)

    def get_AddlDiscAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        AddlDiscAmt = instances.AddlDiscAmt

        # AddlDiscAmt = round(AddlDiscAmt, PriceRounding)

        return float(AddlDiscAmt)

    def get_TotalDiscount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalDiscount = instances.TotalDiscount

        # TotalDiscount = round(TotalDiscount, PriceRounding)

        return float(TotalDiscount)

    def get_TotalTax(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalTax = instances.TotalTax

        # TotalTax = round(TotalTax, PriceRounding)

        return float(TotalTax)

    def get_BillDiscPercent(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscPercent = instances.BillDiscPercent

        # BillDiscPercent = round(BillDiscPercent, PriceRounding)

        return float(BillDiscPercent)

    def get_BillDiscAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscAmt = instances.BillDiscAmt

        # BillDiscAmt = round(BillDiscAmt, PriceRounding)

        return float(BillDiscAmt)

    def get_NetTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        NetTotal = instances.NetTotal

        # NetTotal = round(NetTotal, PriceRounding)

        return float(NetTotal)

    def get_AdditionalCost(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        AdditionalCost = instances.AdditionalCost

        # AdditionalCost = round(AdditionalCost, PriceRounding)

        return float(AdditionalCost)

    def get_GrandTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        GrandTotal = instances.GrandTotal

        # GrandTotal = round(GrandTotal, PriceRounding)

        return float(GrandTotal)

    def get_RoundOff(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        RoundOff = instances.RoundOff

        # RoundOff = round(RoundOff, PriceRounding)

        return float(RoundOff)

    def get_CashReceived(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CashReceived = instances.CashReceived

        # CashReceived = round(CashReceived, PriceRounding)

        return float(CashReceived)

    def get_CashAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CashAmount = instances.CashAmount

        # CashAmount = round(CashAmount, PriceRounding)

        return float(CashAmount)

    def get_BankAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BankAmount = instances.BankAmount

        # BankAmount = round(BankAmount, PriceRounding)

        return float(BankAmount)




class POS_SalesDetailsSerializer(serializers.ModelSerializer):

    Qty = serializers.SerializerMethodField()
    UnitPrice = serializers.SerializerMethodField()
    InclusivePrice = serializers.SerializerMethodField()
    DiscountPerc = serializers.SerializerMethodField()
    DiscountAmount = serializers.SerializerMethodField()
    GrossAmount = serializers.SerializerMethodField()
    VATPerc = serializers.SerializerMethodField()
    VATAmount = serializers.SerializerMethodField()
    SGSTPerc = serializers.SerializerMethodField()
    SGSTAmount = serializers.SerializerMethodField()
    CGSTPerc = serializers.SerializerMethodField()
    CGSTAmount = serializers.SerializerMethodField()
    IGSTPerc = serializers.SerializerMethodField()
    IGSTAmount = serializers.SerializerMethodField()
    NetAmount = serializers.SerializerMethodField()
    ProductName = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()
    unq_id = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    unitPriceRounded = serializers.SerializerMethodField()
    quantityRounded = serializers.SerializerMethodField()
    netAmountRounded = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    ActualUnitPrice = serializers.SerializerMethodField()
    ProductTaxName = serializers.SerializerMethodField()
    

    class Meta:
        model = table.SalesDetails
        fields = ('id', 'unq_id', 'SalesDetailsID', 'BranchID','ProductName',
                  'Qty',  'UnitPrice','InclusivePrice', 'ActualUnitPrice','UnitName', 'DiscountPerc', 'DiscountAmount',
                  'GrossAmount','VATPerc', 'VATAmount', 'SGSTPerc', 'SGSTAmount', 'CGSTPerc', 'Description','ProductTaxName',
                  'CGSTAmount', 'IGSTPerc', 'IGSTAmount', 'NetAmount', 'CreatedUserID', 'TotalTax',
                  'unitPriceRounded', 'quantityRounded', 'netAmountRounded')
    

    def get_ProductTaxName(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductTaxID = sales_details.ProductTaxID
        BranchID = sales_details.BranchID
        ProductTaxName = ""
        if table.TaxCategory.objects.filter(CompanyID=CompanyID,BranchID=BranchID,TaxID=ProductTaxID).exists():
            ProductTaxName = table.TaxCategory.objects.get(CompanyID=CompanyID,BranchID=BranchID,TaxID=ProductTaxID).TaxName
        return ProductTaxName


    def get_ProductName(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID
        product = table.Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)
        ProductName = product.ProductName
        return ProductName


    def get_id(self, instances):
        id = instances.id

        return str(id)

    def get_InclusivePrice(self, sales_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        # PriceRounding = 2
        InclusivePrice = sales_details.InclusivePrice
        if not InclusivePrice:
            InclusivePrice = 0
        #     InclusivePrice = round(InclusivePrice, PriceRounding)
        # else:
        #     InclusivePrice = 0

        return float(InclusivePrice)

    def get_unitPriceRounded(self, sales_details):
        UnitPrice = sales_details.UnitPrice
        return float(UnitPrice)

    def get_quantityRounded(self, sales_details):
        Qty = sales_details.Qty
        return float(Qty)

    def get_netAmountRounded(self, sales_details):
        NetAmount = sales_details.NetAmount
        return float(NetAmount)


    def get_TotalTax(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        TAX1Amount = purchase_details.TAX1Amount
        TAX2Amount = purchase_details.TAX2Amount
        TAX3Amount = purchase_details.TAX3Amount
        VATAmount = purchase_details.VATAmount
        IGSTAmount = purchase_details.IGSTAmount
        SGSTAmount = purchase_details.SGSTAmount
        CGSTAmount = purchase_details.CGSTAmount
        KFCAmount = purchase_details.KFCAmount

        TotalTax = (float(TAX1Amount) + float(TAX2Amount) + float(TAX3Amount) +
                    float(VATAmount) + float(IGSTAmount) + float(SGSTAmount) + float(CGSTAmount) + float(KFCAmount))

        return float(TotalTax)

    def get_unq_id(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        unq_id = purchase_details.id

        return str(unq_id)

    def get_UnitName(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        PriceListID = purchase_details.PriceListID
        BranchID = purchase_details.BranchID

        if table.PriceList.objects.filter(CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).exists():
            UnitID = table.PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).UnitID
            UnitName = table.Unit.objects.get(
                BranchID=BranchID, UnitID=UnitID, CompanyID=CompanyID).UnitName
        else:
            UnitName = ""

        return UnitName

    def get_Qty(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        Qty = sales_details.Qty

        # Qty = round(Qty, PriceRounding)

        return float(Qty)


    def get_UnitPrice(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        UnitPrice = sales_details.UnitPrice

        # UnitPrice = round(UnitPrice, PriceRounding)

        return float(UnitPrice)

    def get_ActualUnitPrice(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        ActualUnitPrice = sales_details.UnitPrice

        # ActualUnitPrice = round(ActualUnitPrice, PriceRounding)

        return float(ActualUnitPrice)


    def get_DiscountPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        DiscountPerc = sales_details.DiscountPerc

        # DiscountPerc = round(DiscountPerc, PriceRounding)

        return float(DiscountPerc)

    def get_DiscountAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        DiscountAmount = sales_details.DiscountAmount

        # DiscountAmount = round(DiscountAmount, PriceRounding)

        return float(DiscountAmount)

    def get_GrossAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        GrossAmount = sales_details.GrossAmount

        # GrossAmount = round(GrossAmount, PriceRounding)

        return float(GrossAmount)


    def get_VATPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        VATPerc = sales_details.VATPerc

        # VATPerc = round(VATPerc, PriceRounding)

        return float(VATPerc)

    def get_VATAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        VATAmount = sales_details.VATAmount

        # VATAmount = round(VATAmount, PriceRounding)

        return float(VATAmount)

    def get_SGSTPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        SGSTPerc = sales_details.SGSTPerc

        # SGSTPerc = round(SGSTPerc, PriceRounding)

        return float(SGSTPerc)

    def get_SGSTAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        SGSTAmount = sales_details.SGSTAmount

        # SGSTAmount = round(SGSTAmount, PriceRounding)

        return float(SGSTAmount)

    def get_CGSTPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        CGSTPerc = sales_details.CGSTPerc

        # CGSTPerc = round(CGSTPerc, PriceRounding)

        return float(CGSTPerc)

    def get_CGSTAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        CGSTAmount = sales_details.CGSTAmount

        # CGSTAmount = round(CGSTAmount, PriceRounding)

        return float(CGSTAmount)

    def get_IGSTPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        IGSTPerc = sales_details.IGSTPerc

        # IGSTPerc = round(IGSTPerc, PriceRounding)

        return float(IGSTPerc)

    def get_IGSTAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        IGSTAmount = sales_details.IGSTAmount

        # IGSTAmount = round(IGSTAmount, PriceRounding)

        return float(IGSTAmount)

    def get_NetAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        NetAmount = sales_details.NetAmount

        # NetAmount = round(NetAmount, PriceRounding)

        return float(NetAmount)


    


class POS_SalesOrder_PrintSerializer(serializers.ModelSerializer):

    SalesDetails = serializers.SerializerMethodField()
    TotalGrossAmt = serializers.SerializerMethodField()
    TotalDiscount = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    NetTotal = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    RoundOff = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    BillDiscPercent = serializers.SerializerMethodField()
    BillDiscAmt = serializers.SerializerMethodField()
    GrandTotal_print = serializers.SerializerMethodField()
    NetTotal_print = serializers.SerializerMethodField()
    GrossAmt_print = serializers.SerializerMethodField()
    TotalDiscount_print = serializers.SerializerMethodField()
    TotalTax_print = serializers.SerializerMethodField()
    VATAmount_print = serializers.SerializerMethodField()
    GSTNumber = serializers.SerializerMethodField()
    GST_Treatment = serializers.SerializerMethodField()
    # =====
    Tax_no = serializers.SerializerMethodField()
    CRNo = serializers.SerializerMethodField()
    Mobile = serializers.SerializerMethodField()
    City = serializers.SerializerMethodField()
    State = serializers.SerializerMethodField()
    Country = serializers.SerializerMethodField()
    PostalCode = serializers.SerializerMethodField()
    PrintCustomerName = serializers.SerializerMethodField()
    PrintAddress = serializers.SerializerMethodField()
    CompanyDetails = serializers.SerializerMethodField()
    qr_image = serializers.SerializerMethodField()
    OrderPhone = serializers.SerializerMethodField()


    class Meta:
        model = table.SalesOrderMaster

        fields = ('id','Tax_no','CRNo','Mobile','City','State','Country','PostalCode','GrossAmt_print','VATAmount_print','NetTotal_print','TotalTax_print', 'TotalDiscount_print','GrandTotal_print', 'BranchID', 'VoucherNo', 'Date',
                    'LedgerName', 'Country_of_Supply','State_of_Supply','CustomerName', 'Address1', 'Address2','PrintAddress',
                  'Notes', 'FinacialYearID', 'TotalGrossAmt', 'TotalDiscount', 'TotalTax','GST_Treatment','GSTNumber',
                  'NetTotal', 'GrandTotal', 'RoundOff', 'CreatedUserID','qr_image','OrderPhone',
                   'BillDiscPercent', 'BillDiscAmt', 'VATAmount', 'SGSTAmount', 'CGSTAmount', 'IGSTAmount','PrintCustomerName',
                   'SalesDetails','CompanyDetails')



    def get_CompanyDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        request = self.context.get("request")
        serialized = CompanySettingsRestSerializer(
            CompanyID, context={"request": request})
        return serialized.data


    def get_OrderPhone(self, instances):
        CompanyID = self.context.get("CompanyID")
        OrderPhone = instances.Phone
        return OrderPhone


    def get_PrintAddress(self, instances):
        CompanyID = self.context.get("CompanyID")
        Address = ""
        LedgerID = instances.LedgerID
        if table.Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
            Address = table.Parties.objects.filter(
                LedgerID=LedgerID, CompanyID=CompanyID).first().Address1
        return Address


    def get_qr_image(self, instances):
        qr_image = ""
        return qr_image


    def get_PrintCustomerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        DisplayName = ""
        LedgerID = instances.LedgerID
        if table.Parties.objects.filter(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID).exists():
            party = table.Parties.objects.get(
                LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID)
            DisplayName = party.DisplayName
        return DisplayName

    def get_GST_Treatment(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        GST_Treatment = instances.GST_Treatment
        if not GST_Treatment:
            GST_Treatment = ""
            if table.Parties.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).exists():
                pary_ins = table.Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).first()
                GST_Treatment = pary_ins.GST_Treatment
        return str(GST_Treatment)


    def get_Tax_no(self, instances):

        CompanyID = self.context.get("CompanyID")
        Tax_no = ""
        if table.Parties.objects.filter(LedgerID=instances.LedgerID, CompanyID=CompanyID).exists():
            Tax_no = table.Parties.objects.get(LedgerID=instances.LedgerID, CompanyID=CompanyID).VATNumber

        return str(Tax_no)

    def get_CRNo(self, instances):

        CompanyID = self.context.get("CompanyID")
        CR_no = ""
        if table.Parties.objects.filter(LedgerID=instances.LedgerID, CompanyID=CompanyID).exists():
            CR_no = table.Parties.objects.get(LedgerID=instances.LedgerID, CompanyID=CompanyID).CRNo

        return str(CR_no)

    def get_Mobile(self, instances):

        CompanyID = self.context.get("CompanyID")
        Mobile = ""
        if table.Parties.objects.filter(LedgerID=instances.LedgerID, CompanyID=CompanyID).exists():
            Mobile = table.Parties.objects.get(LedgerID=instances.LedgerID, CompanyID=CompanyID).Mobile

        return str(Mobile)

    def get_City(self, instances):
        CompanyID = self.context.get("CompanyID")
        
        City = ""
        
        LedgerID = instances.LedgerID
        if table.Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
            City = table.Parties.objects.filter(
                LedgerID=LedgerID, CompanyID=CompanyID).first().City

        return City

    def get_State(self, instances):
        CompanyID = self.context.get("CompanyID")
        State_Name = ""
        LedgerID = instances.LedgerID
        if table.Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
            if table.Parties.objects.get(LedgerID=LedgerID, CompanyID=CompanyID).State:
                pk = table.Parties.objects.filter(
                    LedgerID=LedgerID, CompanyID=CompanyID).first().State
                a = table.Parties.objects.filter(
                    LedgerID=LedgerID, CompanyID=CompanyID)
                # for i in a:
                #     print(i.State,"//////////////////////UVAIS///////////////////////////")
                if table.State.objects.filter(pk=pk).exists():
                    State_Name = table.State.objects.get(pk=pk).Name

        return State_Name

    def get_Country(self, instances):
        CompanyID = self.context.get("CompanyID")
        
        Country_Name = ""
        
        LedgerID = instances.LedgerID
        if table.Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
            if table.Parties.objects.get(LedgerID=LedgerID, CompanyID=CompanyID).Country:
                pk = table.Parties.objects.filter(
                    LedgerID=LedgerID, CompanyID=CompanyID).first().Country
                if table.Country.objects.filter(pk=pk).exists():
                    Country_Name = table.Country.objects.get(pk=pk).Country_Name

        return Country_Name

    def get_PostalCode(self, instances):
        CompanyID = self.context.get("CompanyID")
        PostalCode = ""
        LedgerID = instances.LedgerID
        if table.Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
            PostalCode = table.Parties.objects.filter(
                LedgerID=LedgerID, CompanyID=CompanyID).first().PostalCode

        return PostalCode

    def get_GSTNumber(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        GSTNumber = ""
        if table.Parties.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).exists():
            pary_ins = table.Parties.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).first()
            GSTNumber = pary_ins.GSTNumber
        return str(GSTNumber)
    

    def get_VATAmount_print(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        VATAmount = instances.VATAmount
        VATAmount = str(round(VATAmount, PriceRounding))
        return str(VATAmount)

    def get_TotalTax_print(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalTax = instances.TotalTax

        TotalTax = str(round(TotalTax, PriceRounding))

        return str(TotalTax)


    def get_TotalDiscount_print(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalDiscount = instances.TotalDiscount

        TotalDiscount = str(round(TotalDiscount, PriceRounding))

        return str(TotalDiscount)


    def get_GrossAmt_print(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        GrossAmount = instances.TotalGrossAmt

        GrossAmt_print = str(round(GrossAmount, PriceRounding))

        return str(GrossAmt_print)


    def get_NetTotal_print(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        NetTotal = instances.NetTotal

        NetTotal = str(round(NetTotal, PriceRounding))

        return str(NetTotal)


    def get_GrandTotal_print(self, instances):
        CompanyID = self.context.get("CompanyID")

        PriceRounding = self.context.get("PriceRounding")

        GrandTotal = instances.GrandTotal
        GrandTotal_print = str(round(GrandTotal, PriceRounding))
        return str(GrandTotal_print)


    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        if table.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID).exists():
            ledger = table.AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)

            LedgerName = ledger.LedgerName
        else:
            LedgerName = ""

        return LedgerName



    def get_SalesDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        print(PriceRounding)

        SalesOrderMasterID = instances.SalesOrderMasterID
        BranchID = instances.BranchID
        print(SalesOrderMasterID, 'SalesOrderMasterID')
        sales_details = table.SalesOrderDetails.objects.filter(
            CompanyID=CompanyID, SalesOrderMasterID=SalesOrderMasterID, BranchID=BranchID).order_by('SalesOrderDetailsID')
        for i in sales_details:
            print(i.SalesOrderMasterID)
        serialized = POS_SalesOrderDetailsSerializer(sales_details, many=True, context={"CompanyID": CompanyID,
                                                                                   "PriceRounding": PriceRounding, })

        return serialized.data

    def get_TotalGrossAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalGrossAmt = instances.TotalGrossAmt

        # TotalGrossAmt = round(TotalGrossAmt, PriceRounding)

        return float(TotalGrossAmt)


    def get_TotalDiscount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalDiscount = instances.TotalDiscount

        # TotalDiscount = round(TotalDiscount, PriceRounding)

        return float(TotalDiscount)

    def get_TotalTax(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalTax = instances.TotalTax

        # TotalTax = round(TotalTax, PriceRounding)

        return float(TotalTax)

    def get_BillDiscPercent(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscPercent = instances.BillDiscPercent

        # BillDiscPercent = round(BillDiscPercent, PriceRounding)

        return float(BillDiscPercent)

    def get_BillDiscAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscAmt = instances.BillDiscAmt

        # BillDiscAmt = round(BillDiscAmt, PriceRounding)

        return float(BillDiscAmt)

    def get_NetTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        NetTotal = instances.NetTotal

        # NetTotal = round(NetTotal, PriceRounding)

        return float(NetTotal)

    def get_GrandTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        GrandTotal = instances.GrandTotal

        # GrandTotal = round(GrandTotal, PriceRounding)

        return float(GrandTotal)

    def get_RoundOff(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        RoundOff = instances.RoundOff

        # RoundOff = round(RoundOff, PriceRounding)

        return float(RoundOff)




class POS_SalesOrderDetailsSerializer(serializers.ModelSerializer):

    Qty = serializers.SerializerMethodField()
    UnitPrice = serializers.SerializerMethodField()
    InclusivePrice = serializers.SerializerMethodField()
    DiscountPerc = serializers.SerializerMethodField()
    DiscountAmount = serializers.SerializerMethodField()
    GrossAmount = serializers.SerializerMethodField()
    VATPerc = serializers.SerializerMethodField()
    VATAmount = serializers.SerializerMethodField()
    SGSTPerc = serializers.SerializerMethodField()
    SGSTAmount = serializers.SerializerMethodField()
    CGSTPerc = serializers.SerializerMethodField()
    CGSTAmount = serializers.SerializerMethodField()
    IGSTPerc = serializers.SerializerMethodField()
    IGSTAmount = serializers.SerializerMethodField()
    NetAmount = serializers.SerializerMethodField()
    ProductName = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()
    unq_id = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    unitPriceRounded = serializers.SerializerMethodField()
    quantityRounded = serializers.SerializerMethodField()
    netAmountRounded = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    ActualUnitPrice = serializers.SerializerMethodField()
    ProductTaxName = serializers.SerializerMethodField()
    

    class Meta:
        model = table.SalesOrderDetails
        fields = ('id', 'unq_id','BranchID','ProductName',
                  'Qty',  'UnitPrice','InclusivePrice', 'ActualUnitPrice','UnitName', 'DiscountPerc', 'DiscountAmount',
                  'GrossAmount','VATPerc', 'VATAmount', 'SGSTPerc', 'SGSTAmount', 'CGSTPerc','ProductTaxName',
                  'CGSTAmount', 'IGSTPerc', 'IGSTAmount', 'NetAmount', 'CreatedUserID', 'TotalTax',
                  'unitPriceRounded', 'quantityRounded', 'netAmountRounded')
    

    def get_ProductTaxName(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductTaxID = sales_details.ProductTaxID
        BranchID = sales_details.BranchID
        ProductTaxName = ""
        if table.TaxCategory.objects.filter(CompanyID=CompanyID,BranchID=BranchID,TaxID=ProductTaxID).exists():
            ProductTaxName = table.TaxCategory.objects.get(CompanyID=CompanyID,BranchID=BranchID,TaxID=ProductTaxID).TaxName
        return ProductTaxName


    def get_ProductName(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID
        product = table.Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)
        ProductName = product.ProductName
        return ProductName


    def get_id(self, instances):
        id = instances.id

        return str(id)

    def get_InclusivePrice(self, sales_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        # PriceRounding = 2
        InclusivePrice = sales_details.InclusivePrice
        if not InclusivePrice:
            InclusivePrice = 0
        #     InclusivePrice = round(InclusivePrice, PriceRounding)
        # else:
        #     InclusivePrice = 0

        return float(InclusivePrice)

    def get_unitPriceRounded(self, sales_details):
        UnitPrice = sales_details.UnitPrice
        return float(UnitPrice)

    def get_quantityRounded(self, sales_details):
        Qty = sales_details.Qty
        return float(Qty)

    def get_netAmountRounded(self, sales_details):
        NetAmount = sales_details.NetAmount
        return float(NetAmount)


    def get_TotalTax(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        TAX1Amount = purchase_details.TAX1Amount
        TAX2Amount = purchase_details.TAX2Amount
        TAX3Amount = purchase_details.TAX3Amount
        VATAmount = purchase_details.VATAmount
        IGSTAmount = purchase_details.IGSTAmount
        SGSTAmount = purchase_details.SGSTAmount
        CGSTAmount = purchase_details.CGSTAmount
        KFCAmount = purchase_details.KFCAmount

        TotalTax = (float(TAX1Amount) + float(TAX2Amount) + float(TAX3Amount) +
                    float(VATAmount) + float(IGSTAmount) + float(SGSTAmount) + float(CGSTAmount) + float(KFCAmount))

        return float(TotalTax)

    def get_unq_id(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        unq_id = purchase_details.id

        return str(unq_id)

    def get_UnitName(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        PriceListID = purchase_details.PriceListID
        BranchID = purchase_details.BranchID

        if table.PriceList.objects.filter(CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).exists():
            UnitID = table.PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).UnitID
            UnitName = table.Unit.objects.get(
                BranchID=BranchID, UnitID=UnitID, CompanyID=CompanyID).UnitName
        else:
            UnitName = ""

        return UnitName

    def get_Qty(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        Qty = sales_details.Qty

        # Qty = round(Qty, PriceRounding)

        return float(Qty)


    def get_UnitPrice(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        UnitPrice = sales_details.UnitPrice

        # UnitPrice = round(UnitPrice, PriceRounding)

        return float(UnitPrice)

    def get_ActualUnitPrice(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        ActualUnitPrice = sales_details.UnitPrice

        # ActualUnitPrice = round(ActualUnitPrice, PriceRounding)

        return float(ActualUnitPrice)


    def get_DiscountPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        DiscountPerc = sales_details.DiscountPerc

        # DiscountPerc = round(DiscountPerc, PriceRounding)

        return float(DiscountPerc)

    def get_DiscountAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        DiscountAmount = sales_details.DiscountAmount

        # DiscountAmount = round(DiscountAmount, PriceRounding)

        return float(DiscountAmount)

    def get_GrossAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        GrossAmount = sales_details.GrossAmount

        # GrossAmount = round(GrossAmount, PriceRounding)

        return float(GrossAmount)


    def get_VATPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        VATPerc = sales_details.VATPerc

        # VATPerc = round(VATPerc, PriceRounding)

        return float(VATPerc)

    def get_VATAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        VATAmount = sales_details.VATAmount

        # VATAmount = round(VATAmount, PriceRounding)

        return float(VATAmount)

    def get_SGSTPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        SGSTPerc = sales_details.SGSTPerc

        # SGSTPerc = round(SGSTPerc, PriceRounding)

        return float(SGSTPerc)

    def get_SGSTAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        SGSTAmount = sales_details.SGSTAmount

        # SGSTAmount = round(SGSTAmount, PriceRounding)

        return float(SGSTAmount)

    def get_CGSTPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        CGSTPerc = sales_details.CGSTPerc

        # CGSTPerc = round(CGSTPerc, PriceRounding)

        return float(CGSTPerc)

    def get_CGSTAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        CGSTAmount = sales_details.CGSTAmount

        # CGSTAmount = round(CGSTAmount, PriceRounding)

        return float(CGSTAmount)

    def get_IGSTPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        IGSTPerc = sales_details.IGSTPerc

        # IGSTPerc = round(IGSTPerc, PriceRounding)

        return float(IGSTPerc)

    def get_IGSTAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        IGSTAmount = sales_details.IGSTAmount

        # IGSTAmount = round(IGSTAmount, PriceRounding)

        return float(IGSTAmount)

    def get_NetAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        NetAmount = sales_details.NetAmount

        # NetAmount = round(NetAmount, PriceRounding)

        return float(NetAmount)




class POS_LedgerSerializer(serializers.ModelSerializer):

    OpeningBalance = serializers.SerializerMethodField()
    CustomerLedgerBalance = serializers.SerializerMethodField()


    class Meta:
        model = table.AccountLedger
        fields = ('id','LedgerID','LedgerName','OpeningBalance','CustomerLedgerBalance','AccountGroupUnder')


    def get_OpeningBalance(self, instances):

        PriceRounding = self.context.get("PriceRounding")
        OpeningBalance = instances.OpeningBalance

        # OpeningBalance = round(OpeningBalance,PriceRounding)

        return str(OpeningBalance)


    def get_CustomerLedgerBalance(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        Balance = 0
        if table.LedgerPosting.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID).exists():
            ledger_instances = table.LedgerPosting.objects.filter(
                CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)
            TotalDebit = 0
            TotalCredit = 0
            for i in ledger_instances:
                TotalDebit += float(i.Debit)
                TotalCredit += float(i.Credit)

            Balance = float(TotalDebit) - float(TotalCredit)
        return float(Balance)




class Kitchen_Serializer(serializers.ModelSerializer):
    class Meta:
        model = table.Kitchen
        fields = '__all__'




class POS_Table_Serializer1(serializers.ModelSerializer):
    PriceCategoryID = serializers.SerializerMethodField()
    sales_price = serializers.SerializerMethodField()

    class Meta:
        model = table.POS_Table
        fields = ('id','TableName','IsActive','PriceCategoryID','Position','sales_price')

    def get_PriceCategoryID(self, instances):
        PriceCategoryID = ""
        if instances.PriceCategory:
            PriceCategoryID = instances.PriceCategory.id
        return str(PriceCategoryID)

    def get_sales_price(self, instances):
        PriceCategoryName = ""
        if instances.PriceCategory:
            PriceCategoryName = instances.PriceCategory.PriceCategoryName
        return str(PriceCategoryName)


