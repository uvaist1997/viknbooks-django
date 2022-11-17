from django.db.models import F, Q, Sum
from fatoora import Fatoora
from rest_framework import serializers

from api.v10.priceLists.serializers import PriceListRestSerializer
from api.v10.workOrder.serializers import Batch_ListSalesSerializer, Batch_ListSerializer

# trunk-ignore(flake8/F401)
from brands.models import (
    AccountLedger,
    Batch,
    BillWiseDetails,
    BillWiseMaster,
    CompanySettings,
    Country,
    Employee,
    LedgerPosting,
    LoyaltyPoint,
    Parties,
    PriceList,
    Product,
    PurchaseDetails,
    PurchaseMaster,
    PurchaseReturnDetails,
    PurchaseReturnMaster,
    QrCode,
    Route,
    SalesDetails,
    SalesEstimateDetails,
    SalesEstimateMaster,
    SalesMaster,
    SalesOrderMaster,
    SalesReturnDetails,
    SalesReturnMaster,
    SerialNumbers,
    State,
    StockPosting,
    StockRate,
    TaxCategory,
    TransactionTypes,
    Unit,
    UserAdrress,
    Warehouse,
    PaymentMaster,
    ReceiptMaster
)
from main.functions import converted_float, generateQrCode, get_BalanceFromLedgerPost, get_GeneralSettings, get_ProductStock, get_company

# from api.v10.sales.functions import GST_finalList_fun
# from api.v10.sales import functions as func


def get_treatment_name(Treatment, type):
    TreatmentName = ""
    if type == "GST" and Treatment:
        GST_Treatments = [
            {"value": "0", "name": "Registered Business - Regular"},
            {"value": "1", "name": "Registered Business - Composition"},
            {"value": "2", "name": "Unregistered Business"},
            {"value": "3", "name": "Consumer"},
            {"value": "4", "name": "Overseas"},
            {"value": "5", "name": "Special Economic Zone"},
            {"value": "6", "name": "Deemed Export"},
        ]

        try:
            TreatmentName = GST_Treatments[int(Treatment)]["name"]
        except:
            TreatmentName = ""
    elif type == "VAT":
        VAT_Treatments = [
            {"value": "0", "name": "Business to Business(B2B)"},
            {"value": "1", "name": "Business to Customer(B2C)"},
        ]
        try:
            TreatmentName = VAT_Treatments[int(Treatment)]["name"]
        except:
            TreatmentName = ""

    return TreatmentName


def GST_finalList_fun(instance, Detail, type_tx, PriceRounding, TransactionType):
    shipping_tax_amount = 0
    half_shipping_tax_amount = 0
    if TransactionType == "Sales":
        shipping_tax_amount = instance.shipping_tax_amount
        half_shipping_tax_amount = converted_float(shipping_tax_amount) / 2
    if type_tx == "SGST":
        SGST_perc_list = []
        GST_final_list = []
        for i in Detail:
            if not i.SGSTPerc in SGST_perc_list and i.SGSTPerc > 0:
                SGST_perc_list.append(i.SGSTPerc)
                SGSTAmount = converted_float(i.SGSTAmount) + converted_float(
                    half_shipping_tax_amount
                )
                GST_final_list.append(
                    {
                        "key": round(converted_float(i.SGSTPerc), PriceRounding),
                        "val": converted_float(SGSTAmount),
                    }
                )
            else:
                for f in GST_final_list:
                    if round(converted_float(f["key"]), 2) == round(
                        converted_float(i.SGSTPerc), 2
                    ):
                        val_amt = f["val"]
                        f["val"] = converted_float(val_amt) + converted_float(
                            i.SGSTAmount
                        )
    else:
        IGST_perc_list = []
        GST_final_list = []
        for i in Detail:
            if not i.IGSTPerc in IGST_perc_list and i.IGSTPerc > 0:
                IGST_perc_list.append(i.IGSTPerc)
                IGSTAmount = converted_float(i.IGSTAmount) + converted_float(
                    shipping_tax_amount
                )
                
                GST_final_list.append(
                    {
                        "key": round(converted_float(i.IGSTPerc), PriceRounding),
                        "val": converted_float(IGSTAmount),
                    }
                )
            else:
                for f in GST_final_list:
                    if round(converted_float(f["key"]), 2) == round(
                        converted_float(i.IGSTPerc), 2
                    ):
                        val_amt = f["val"]
                        f["val"] = converted_float(val_amt) + converted_float(
                            i.IGSTAmount
                        )

    return GST_final_list


class SalesMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesMaster
        fields = (
            "LoyaltyCustomerID",
            "id",
            "BranchID",
            "Action",
            "VoucherNo",
            "Date",
            "CreditPeriod",
            "LedgerID",
            "OldLedgerBalance",
            "GST_Treatment",
            "VAT_Treatment",
            "Status",
            "PriceCategoryID",
            "EmployeeID",
            "SalesAccount",
            "CustomerName",
            "Address1",
            "Address2",
            "Address3",
            "Notes",
            "FinacialYearID",
            "TotalGrossAmt",
            "AddlDiscPercent",
            "AddlDiscAmt",
            "TotalDiscount",
            "TotalTax",
            "NetTotal",
            "AdditionalCost",
            "GrandTotal",
            "RoundOff",
            "CashReceived",
            "BankAmount",
            "WarehouseID",
            "TableID",
            "SeatNumber",
            "NoOfGuests",
            "INOUT",
            "TokenNumber",
            "CardTypeID",
            "CardNumber",
            "IsActive",
            "IsPosted",
            "SalesType",
            "CreatedUserID",
            "TaxID",
            "TaxType",
            "BillDiscPercent",
            "BillDiscAmt",
            "VATAmount",
            "SGSTAmount",
            "CGSTAmount",
            "IGSTAmount",
            "TAX1Amount",
            "TAX2Amount",
            "TAX3Amount",
            "Balance",
            "TransactionTypeID",
        )


class SalesMasterRestSerializer(serializers.ModelSerializer):
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
    SalesAccountName = serializers.SerializerMethodField()
    WareHouseName = serializers.SerializerMethodField()
    CardTypeName = serializers.SerializerMethodField()
    DetailID = serializers.SerializerMethodField()
    BillDiscPercent = serializers.SerializerMethodField()
    BillDiscAmt = serializers.SerializerMethodField()
    is_customer = serializers.SerializerMethodField()
    LoyaltyPoint = serializers.SerializerMethodField()
    LoyaltyValue = serializers.SerializerMethodField()
    LoyaltyCustomerName = serializers.SerializerMethodField()
    qr_image = serializers.SerializerMethodField()
    GrandTotal_print = serializers.SerializerMethodField()
    NetTotal_print = serializers.SerializerMethodField()
    GrossAmt_print = serializers.SerializerMethodField()
    TotalDiscount_print = serializers.SerializerMethodField()
    TotalTax_print = serializers.SerializerMethodField()
    Balance_print = serializers.SerializerMethodField()
    TotalTaxableAmount_print = serializers.SerializerMethodField()
    VATAmount_print = serializers.SerializerMethodField()
    GSTNumber = serializers.SerializerMethodField()
    GST_Treatment = serializers.SerializerMethodField()
    VAT_Treatment = serializers.SerializerMethodField()
    # =====
    Tax_no = serializers.SerializerMethodField()
    CRNo = serializers.SerializerMethodField()
    Mobile = serializers.SerializerMethodField()
    City = serializers.SerializerMethodField()
    State = serializers.SerializerMethodField()
    Country = serializers.SerializerMethodField()
    PostalCode = serializers.SerializerMethodField()
    Attention = serializers.SerializerMethodField()
    PrintCustomerName = serializers.SerializerMethodField()
    PrintAddress = serializers.SerializerMethodField()
    ProductList = serializers.SerializerMethodField()
    ShippingAddress = serializers.SerializerMethodField()
    ShippingAddressList = serializers.SerializerMethodField()
    Place_of_Supply = serializers.SerializerMethodField()
    SGST_final_list = serializers.SerializerMethodField()
    IGST_final_list = serializers.SerializerMethodField()
    VATNumber = serializers.SerializerMethodField()
    EmployeeName = serializers.SerializerMethodField()
    EmployeePhone = serializers.SerializerMethodField()
    LedgerBalance = serializers.SerializerMethodField()
    GST_Treatment_Name = serializers.SerializerMethodField()
    VAT_Treatment_Name = serializers.SerializerMethodField()
    ShipAddress1 = serializers.SerializerMethodField()
    ShipAddress2 = serializers.SerializerMethodField()
    ShipCity = serializers.SerializerMethodField()
    ShipStateName = serializers.SerializerMethodField()
    ShipCountryName = serializers.SerializerMethodField()
    ShipDistrict = serializers.SerializerMethodField()
    Phone_Shipping = serializers.SerializerMethodField()
    PostalCode_Shipping = serializers.SerializerMethodField()
    billing_address_single = serializers.SerializerMethodField()
    BillingAddressList = serializers.SerializerMethodField()
    Address1 = serializers.SerializerMethodField()
    TenderCash = serializers.SerializerMethodField()
    TenderCashBalance = serializers.SerializerMethodField()
    LoyaltyCustomerID_ID = serializers.SerializerMethodField()
    LoyaltyCustomerValue = serializers.SerializerMethodField()
    LoyaltyCustomerPoint = serializers.SerializerMethodField()
    LoyaltyCustomer_AccountLedgerID = serializers.SerializerMethodField()
    is_billwised = serializers.SerializerMethodField()
    billwise_status = serializers.SerializerMethodField()
    paid_amount = serializers.SerializerMethodField()
    InvoiceBalance = serializers.SerializerMethodField()
    RouteName = serializers.SerializerMethodField()
    DueDate = serializers.SerializerMethodField()

    class Meta:
        model = SalesMaster

        fields = (
            "id",
            "Tax_no",
            "CRNo",
            "Mobile",
            "City",
            "State",
            "Country",
            "PostalCode",
            "GrossAmt_print",
            "VATAmount_print",
            "TotalTaxableAmount_print",
            "NetTotal_print",
            "TotalTax_print",
            "Balance_print",
            "TotalDiscount_print",
            "GrandTotal_print",
            "qr_image",
            "ShippingCharge",
            "shipping_tax_amount",
            "TaxTypeID",
            "SAC",
            "SalesTax",
            "LoyaltyCustomerID",
            "LoyaltyCustomerID_ID",
            "LoyaltyCustomerName",
            "TotalTaxableAmount",
            "SalesMasterID",
            "BranchID",
            "Action",
            "VoucherNo",
            "Date",
            "CreditPeriod",
            "LedgerID",
            "LedgerName",
            "OldLedgerBalance",
            "CashID",
            "BankID",
            "Country_of_Supply",
            "State_of_Supply",
            "VAT_Treatment",
            "PriceCategoryID",
            "EmployeeID",
            "SalesAccount",
            "SalesAccountName",
            "CustomerName",
            "Address1",
            "Address2",
            "Address3",
            "PrintAddress",
            "ProductList",
            "Notes",
            "FinacialYearID",
            "TotalGrossAmt",
            "AddlDiscPercent",
            "AddlDiscAmt",
            "TotalDiscount",
            "TotalTax",
            "GST_Treatment",
            "GSTNumber",
            "ShippingAddress",
            "NetTotal",
            "AdditionalCost",
            "GrandTotal",
            "RoundOff",
            "CashReceived",
            "CashAmount",
            "BankAmount",
            "WarehouseID",
            "WareHouseName",
            "TableID",
            "SeatNumber",
            "NoOfGuests",
            "INOUT",
            "TokenNumber",
            "CardTypeID",
            "CardTypeName",
            "CardNumber",
            "IsActive",
            "IsPosted",
            "SalesType",
            "CreatedDate",
            "UpdatedDate",
            "CreatedUserID",
            "TaxID",
            "TaxType",
            "BillDiscPercent",
            "BillDiscAmt",
            "VATAmount",
            "SGSTAmount",
            "CGSTAmount",
            "IGSTAmount",
            "Status",
            "Attention",
            "PrintCustomerName",
            "ShippingAddressList",
            "TAX1Amount",
            "TAX2Amount",
            "TAX3Amount",
            "KFCAmount",
            "Balance",
            "TransactionTypeID",
            "DetailID",
            "is_customer",
            "SalesDetails",
            "LoyaltyPoint",
            "LoyaltyValue",
            "Place_of_Supply",
            "SGST_final_list",
            "IGST_final_list",
            "VATNumber",
            "EmployeeName",
            "EmployeePhone",
            "LedgerBalance",
            "GST_Treatment_Name",
            "VAT_Treatment_Name",
            "OrderNo",
            "ShipAddress1",
            "ShipAddress2",
            "ShipCity",
            "ShipStateName",
            "ShipCountryName",
            "ShipDistrict",
            "Phone_Shipping",
            "PostalCode_Shipping",
            "billing_address_single",
            "BillingAddressList",
            "is_manual_roundoff",
            "TenderCash",
            "TenderCashBalance",
            "LoyaltyCustomerValue",
            "LoyaltyCustomerPoint",
            "LoyaltyCustomer_AccountLedgerID",
            "is_billwised",
            "billwise_status",
            "paid_amount",
            "InvoiceBalance",
            "RouteName",
            "DueDate"
        )
        
    def get_DueDate(self, instance):
        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        LedgerID = instance.LedgerID
        InvoiceNo = instance.VoucherNo
        DueDate = None
        if BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID,InvoiceNo=InvoiceNo,CustomerID=LedgerID,VoucherType="SI").exists():
            bill_ins = BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID,InvoiceNo=InvoiceNo,CustomerID=LedgerID,VoucherType="SI").first()
            DueDate = bill_ins.DueDate
        return DueDate
        
    def get_RouteName(self, instance):
        RouteName = ""
        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        LedgerID = instance.LedgerID
        if Parties.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID).exists():
            RouteID = Parties.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID).first().RouteID
            if Route.objects.filter(CompanyID=CompanyID,BranchID=BranchID, RouteID=RouteID).exists():
                RouteName = Route.objects.filter(
                    CompanyID=CompanyID,BranchID=BranchID, RouteID=RouteID).first().RouteName
        return RouteName
        
    def get_InvoiceBalance(self, instance):
        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        InvoiceNo = instance.VoucherNo
        SalesMasterID = instance.SalesMasterID
        GrandTotal = instance.GrandTotal
        InvoiceBalance = 0
        if BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=InvoiceNo, TransactionID=SalesMasterID).exists():
            billwise_ins = BillWiseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=InvoiceNo, TransactionID=SalesMasterID).first()
            Payments = billwise_ins.Payments
            InvoiceBalance = converted_float(GrandTotal) - converted_float(Payments)
        return InvoiceBalance
        
    def get_paid_amount(self, instance):
        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        InvoiceNo = instance.VoucherNo
        SalesMasterID = instance.SalesMasterID
        Payments = 0
        if BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=InvoiceNo, TransactionID=SalesMasterID).exists():
            billwise_ins = BillWiseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=InvoiceNo, TransactionID=SalesMasterID).first()
            Payments = billwise_ins.Payments
        return Payments
    
    
    def get_billwise_status(self, instance):
        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        InvoiceNo = instance.VoucherNo
        SalesMasterID = instance.SalesMasterID
        GrandTotal = instance.GrandTotal
        billwise_status = "paid"
        
        if BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=InvoiceNo,TransactionID=SalesMasterID).exists():
            billwise_ins = BillWiseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=InvoiceNo, TransactionID=SalesMasterID).first()
            Payments = billwise_ins.Payments
           
            if converted_float(Payments) == converted_float(0):
                billwise_status = "unpaid"
            elif converted_float(Payments) < converted_float(GrandTotal):
                billwise_status = "partially paid"
        return billwise_status
        
    def get_is_billwised(self, instance):
        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        InvoiceNo = instance.VoucherNo
        is_billwised = False
        if BillWiseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=InvoiceNo, VoucherType="SI",Payments__gt=0).exclude(PaymentVoucherType="SI").exists():
            is_billwised = True
        return is_billwised
    
    
    def get_LoyaltyCustomer_AccountLedgerID(self, instances):
        LoyaltyCustomerID = ""
        if instances.LoyaltyCustomerID:
            if instances.LoyaltyCustomerID:
                # AccountLedgerID = instances.LoyaltyCustomerID.AccountLedgerID.pk
                LoyaltyCustomerID = instances.LoyaltyCustomerID.LoyaltyCustomerID

        return str(LoyaltyCustomerID)


    def get_LoyaltyCustomerValue(self, instance):
        LoyaltyCustomerValue = 0
        CompanyID = self.context.get("CompanyID")
        if LoyaltyPoint.objects.filter(CompanyID=instance.CompanyID,VoucherType="SI",VoucherMasterID=instance.SalesMasterID,is_Radeem=True):
            LoyaltyCustomerValue = LoyaltyPoint.objects.get(CompanyID=instance.CompanyID,VoucherType="SI",VoucherMasterID=instance.SalesMasterID,is_Radeem=True).Value
        return LoyaltyCustomerValue

    def get_LoyaltyCustomerPoint(self, instance):
        LoyaltyCustomerPoint = 0
        CompanyID = self.context.get("CompanyID")
        if LoyaltyPoint.objects.filter(CompanyID=instance.CompanyID,VoucherType="SI",VoucherMasterID=instance.SalesMasterID,is_Radeem=True):
            LoyaltyCustomerPoint = LoyaltyPoint.objects.get(CompanyID=instance.CompanyID,VoucherType="SI",VoucherMasterID=instance.SalesMasterID,is_Radeem=True).Point
        return LoyaltyCustomerPoint

    def get_TenderCash(self, instance):
        CompanyID = self.context.get("CompanyID")
        CashReceived = instance.CashReceived
        BankAmount = instance.BankAmount
        TenderCash = CashReceived+BankAmount
        return TenderCash

    def get_TenderCashBalance(self, instance):
        PriceRounding = self.context.get("PriceRounding")

        CompanyID = self.context.get("CompanyID")
        CashReceived = instance.CashReceived
        NetTotal = instance.NetTotal
        BankAmount = instance.BankAmount
        TenderCash = CashReceived+BankAmount
        TenderCashBalance = TenderCash - NetTotal

        return round(TenderCashBalance,PriceRounding)

    def get_Address1(self, instance):
        Address1 = instance.Address1
        if instance.BillingAddress:
            CustomerStateName = ""
            if instance.BillingAddress.state:
                CustomerStateName = instance.BillingAddress.state.Name
            Address1 = (
                str(instance.BillingAddress.Address1)
                + str(",")
                + str(instance.BillingAddress.City)
                + str(",")
                + str(CustomerStateName)
                + str(",")
                + str(instance.BillingAddress.PostalCode)
            )
        return Address1

    def get_ShipAddress1(self, instances):
        CompanyID = self.context.get("CompanyID")
        ShipAddress1 = ""
        LedgerID = instances.LedgerID
        if Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
            ShipAddress1 = (
                Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID)
                .first()
                .Address1_Shipping
            )
        return ShipAddress1

    def get_ShipAddress2(self, instances):
        CompanyID = self.context.get("CompanyID")
        ShipAddress2 = ""
        LedgerID = instances.LedgerID
        if Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
            ShipAddress2 = (
                Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID)
                .first()
                .Address2_Shipping
            )
        return ShipAddress2

    def get_ShipCity(self, instances):
        CompanyID = self.context.get("CompanyID")
        ShipCity = ""
        LedgerID = instances.LedgerID
        if Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
            ShipCity = (
                Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID)
                .first()
                .City_Shipping
            )
        return ShipCity

    def get_Phone_Shipping(self, instances):
        CompanyID = self.context.get("CompanyID")
        Phone_Shipping = ""
        LedgerID = instances.LedgerID
        if Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
            Phone_Shipping = (
                Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID)
                .first()
                .Phone_Shipping
            )
        return Phone_Shipping

    def get_PostalCode_Shipping(self, instances):
        CompanyID = self.context.get("CompanyID")
        PostalCode_Shipping = ""
        LedgerID = instances.LedgerID
        if Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
            PostalCode_Shipping = (
                Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID)
                .first()
                .PostalCode_Shipping
            )
        return PostalCode_Shipping

    def get_ShipDistrict(self, instances):
        CompanyID = self.context.get("CompanyID")
        ShipDistrict = ""
        LedgerID = instances.LedgerID
        if Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
            ShipDistrict = (
                Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID)
                .first()
                .District_shipping
            )
        return ShipDistrict

    def get_ShipStateName(self, instances):
        CompanyID = self.context.get("CompanyID")
        ShipStateName = ""
        LedgerID = instances.LedgerID
        if Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
            State_Shipping = (
                Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID)
                .first()
                .State_Shipping
            )
            if State_Shipping:
                ShipStateName = State.objects.get(id=State_Shipping).Name
        return ShipStateName

    def get_ShipCountryName(self, instances):
        CompanyID = self.context.get("CompanyID")
        ShipCountryName = ""
        LedgerID = instances.LedgerID
        if Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
            Country_Shipping = (
                Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID)
                .first()
                .Country_Shipping
            )
            if Country_Shipping:
                ShipCountryName = Country.objects.get(id=Country_Shipping).Country_Name
        return ShipCountryName

    def get_GST_Treatment_Name(self, instance):
        CompanyID = self.context.get("CompanyID")
        GST_Treatment = instance.GST_Treatment
        GST_Treatment_Name = ""
        GST_Treatment_Name = get_treatment_name(GST_Treatment, "GST")
        return GST_Treatment_Name

    def get_VAT_Treatment_Name(self, instance):
        CompanyID = self.context.get("CompanyID")
        VAT_Treatment = instance.VAT_Treatment
        VAT_Treatment_Name = ""
        VAT_Treatment_Name = get_treatment_name(VAT_Treatment, "VAT")
        return VAT_Treatment_Name

    def get_LedgerBalance(self, instance):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instance.LedgerID
        BranchID = instance.BranchID
        LedgerBalance = 0
        if LedgerPosting.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        ).exists():
            ledger_instances = LedgerPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            )
            debit_sum = ledger_instances.aggregate(Sum("Debit"))
            debit_sum = debit_sum["Debit__sum"]
            credit_sum = ledger_instances.aggregate(Sum("Credit"))
            credit_sum = credit_sum["Credit__sum"]
            LedgerBalance = converted_float(debit_sum) - converted_float(credit_sum)
        return LedgerBalance


    def get_EmployeeName(self, instance):
        CompanyID = self.context.get("CompanyID")
        EmployeeID = instance.EmployeeID
        EmployeeName = ""
        if Employee.objects.filter(CompanyID=CompanyID, EmployeeID=EmployeeID).exists():
            EmployeeName = (
                Employee.objects.filter(CompanyID=CompanyID, EmployeeID=EmployeeID)
                .first()
                .FirstName
            )
        return EmployeeName

        
    def get_EmployeePhone(self, instance):
        CompanyID = self.context.get("CompanyID")
        EmployeeID = instance.EmployeeID
        Phone = ""
        if Employee.objects.filter(CompanyID=CompanyID, EmployeeID=EmployeeID).exists():
            Phone = (
                Employee.objects.filter(CompanyID=CompanyID, EmployeeID=EmployeeID)
                .first()
                .Phone
            )
        return Phone

    def get_SGST_final_list(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        BranchID = instances.BranchID
        SalesMasterID = instances.SalesMasterID
        sales_details = SalesDetails.objects.filter(
            CompanyID=CompanyID, SalesMasterID=SalesMasterID, BranchID=BranchID
        )
        SGST_final_list = GST_finalList_fun(
            instances, sales_details, "SGST", PriceRounding, "Sales"
        )
        return SGST_final_list

    def get_IGST_final_list(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        BranchID = instances.BranchID
        SalesMasterID = instances.SalesMasterID
        sales_details = SalesDetails.objects.filter(
            CompanyID=CompanyID, SalesMasterID=SalesMasterID, BranchID=BranchID
        )
        IGST_final_list = GST_finalList_fun(
            instances, sales_details, "IGST", PriceRounding, "Sales"
        )
        return IGST_final_list

    def get_ShippingAddress(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        ShippingAddress = instances.ShippingAddress
        if ShippingAddress:
            ShippingAddress = ShippingAddress.id
        else:
            ShippingAddress = None

        return str(ShippingAddress)

    def get_ShippingAddressList(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        ShippingAddressList = []
        if UserAdrress.objects.filter(
            CompanyID=CompanyID, Branch__BranchID=BranchID, Party__LedgerID=LedgerID,Type="ShippingAddress"
        ).exists():
            shipping_instances = UserAdrress.objects.filter(
                CompanyID=CompanyID, Branch__BranchID=BranchID, Party__LedgerID=LedgerID, Type="ShippingAddress"
            )
            serialized = ShippingAddressListSerializer(
                shipping_instances, many=True, context={"CompanyID": CompanyID}
            )
            ShippingAddressList = serialized.data
            
        # ShippingAddress = instances.ShippingAddress
        # ShippingAddressList = []
        # if ShippingAddress:
        #     Attention = ShippingAddress.Attention
        #     Address1 = ShippingAddress.Address1
        #     Mobile = ShippingAddress.Mobile

        #     ShippingAddressList.append({
        #             "Attention": Attention,
        #             "Address1": Address1,
        #             "Mobile": Mobile,
        #         })

        return ShippingAddressList
    
    def get_billing_address_single(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        LedgerID = instances.LedgerID
        BillingAddress = instances.BillingAddress
        billing_address_single = {}
        CustomerStateName = ""
        if BillingAddress:
            if BillingAddress.state:
                    CustomerStateName = BillingAddress.state.Name
            Billing_Address = (
                str(BillingAddress.Address1)
                + str(",")
                + str(BillingAddress.City)
                + str(",")
                + str(CustomerStateName)
                + str(",")
                + str(BillingAddress.PostalCode)
            )
            billing_address_single = {
                "id": str(BillingAddress.id),
                "Attention": BillingAddress.Attention,
                "Address1": Billing_Address,
                "Mobile": BillingAddress.Mobile,
            }
        return billing_address_single

    def get_BillingAddressList(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        BillingAddressList = []
        if UserAdrress.objects.filter(
            CompanyID=CompanyID, Branch__BranchID=BranchID, Party__LedgerID=LedgerID,Type="BillingAddress"
        ).exists():
            shipping_instances = UserAdrress.objects.filter(
                CompanyID=CompanyID, Branch__BranchID=BranchID, Party__LedgerID=LedgerID, Type="BillingAddress"
            )
            serialized = ShippingAddressListSerializer(
                shipping_instances, many=True, context={"CompanyID": CompanyID}
            )
            BillingAddressList = serialized.data
        return BillingAddressList

    def get_ProductList(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        SalesMasterID = instances.SalesMasterID
        WarehouseID = instances.WarehouseID
        sales_details = SalesDetails.objects.filter(
            CompanyID=CompanyID, SalesMasterID=SalesMasterID, BranchID=BranchID
        )

        product_ids = sales_details.values_list("ProductID", flat=True)
        produc_instances = Product.objects.filter(
            CompanyID=CompanyID, ProductID__in=product_ids
        )
        ProductList = []
        for p in produc_instances:
            sale_ins = sales_details.filter(ProductID=p.ProductID).first()
            BatchCode = sale_ins.BatchCode
            PriceListID = sale_ins.PriceListID
            price_ins = PriceList.objects.filter(
                CompanyID=CompanyID, PriceListID=PriceListID
            ).first()
            SalesPrice = price_ins.SalesPrice
            PurchasePrice = price_ins.PurchasePrice
            Stock = get_ProductStock(
                CompanyID, BranchID, p.ProductID, WarehouseID, BatchCode
            )
            ProductList.append(
                {
                    "id": str(p.id),
                    "product_id": str(p.id),
                    "ProductCode": p.ProductCode,
                    "ProductName": p.ProductName,
                    "ProductID": p.ProductID,
                    "Stock": Stock,
                    "SalesPrice": SalesPrice,
                    "PurchasePrice": PurchasePrice,
                    "BatchCode": BatchCode
                }
            )

        return ProductList

    def get_Attention(self, instances):
        CompanyID = self.context.get("CompanyID")
        Attention = ""
        LedgerID = instances.LedgerID
        if Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
            Attention = (
                Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID)
                .first()
                .Attention
            )

        return Attention

    def get_PrintAddress(self, instances):
        CompanyID = self.context.get("CompanyID")
        Address = ""
        LedgerID = instances.LedgerID
        if Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
            Address = (
                Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID)
                .first()
                .Address1
            )
        return Address

    def get_PrintCustomerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        DisplayName = ""
        LedgerID = instances.LedgerID
        if Parties.objects.filter(
            LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID
        ).exists():
            party = Parties.objects.get(
                LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID
            )
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
            if Parties.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).exists():
                pary_ins = Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
                ).first()
                GST_Treatment = pary_ins.GST_Treatment
        return str(GST_Treatment)

    def get_VAT_Treatment(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        VAT_Treatment = instances.VAT_Treatment
        if not VAT_Treatment:
            VAT_Treatment = ""
            if Parties.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).exists():
                pary_ins = Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
                ).first()
                VAT_Treatment = pary_ins.VAT_Treatment
        return str(VAT_Treatment)

    def get_Tax_no(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        is_gst = get_GeneralSettings(CompanyID, BranchID, "GST")
        is_vat = get_GeneralSettings(CompanyID, BranchID, "VAT")
        Tax_no = ""
        if Parties.objects.filter(
            LedgerID=instances.LedgerID, CompanyID=CompanyID
        ).exists():
            party = Parties.objects.get(
                LedgerID=instances.LedgerID, CompanyID=CompanyID
            )
            if is_vat:
                Tax_no = party.VATNumber
            if is_gst:
                Tax_no = party.GSTNumber
        return str(Tax_no)

    def get_CRNo(self, instances):

        CompanyID = self.context.get("CompanyID")
        CR_no = ""
        if Parties.objects.filter(
            LedgerID=instances.LedgerID, CompanyID=CompanyID
        ).exists():
            CR_no = Parties.objects.get(
                LedgerID=instances.LedgerID, CompanyID=CompanyID
            ).CRNo

        return str(CR_no)

    def get_Mobile(self, instances):

        CompanyID = self.context.get("CompanyID")
        Mobile = ""
        if Parties.objects.filter(
            LedgerID=instances.LedgerID, CompanyID=CompanyID
        ).exists():
            Mobile = Parties.objects.get(
                LedgerID=instances.LedgerID, CompanyID=CompanyID
            ).Mobile

        return str(Mobile)

    def get_City(self, instances):
        CompanyID = self.context.get("CompanyID")

        City = ""

        LedgerID = instances.LedgerID
        if Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
            City = (
                Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID)
                .first()
                .City
            )

        return City

    def get_State(self, instances):
        CompanyID = self.context.get("CompanyID")
        State_Name = ""
        LedgerID = instances.LedgerID
        if Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
            if Parties.objects.get(LedgerID=LedgerID, CompanyID=CompanyID).State:
                pk = (
                    Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID)
                    .first()
                    .State
                )              
                if State.objects.filter(pk=pk).exists():
                    State_Name = State.objects.get(pk=pk).Name

        return State_Name

    def get_Place_of_Supply(self, instances):
        CompanyID = self.context.get("CompanyID")
        State_Name = ""

        try:
            if State.objects.filter(pk=instances.State_of_Supply).exists():
                State_Name = State.objects.get(pk=instances.State_of_Supply).Name
        except:
            pass

        return State_Name

    def get_Country(self, instances):
        CompanyID = self.context.get("CompanyID")

        Country_Name = ""

        LedgerID = instances.LedgerID
        if Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
            if Parties.objects.get(LedgerID=LedgerID, CompanyID=CompanyID).Country:
                pk = (
                    Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID)
                    .first()
                    .Country
                )
                if Country.objects.filter(pk=pk).exists():
                    Country_Name = Country.objects.get(pk=pk).Country_Name

        return Country_Name

    def get_PostalCode(self, instances):
        CompanyID = self.context.get("CompanyID")
        PostalCode = ""
        LedgerID = instances.LedgerID
        if Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
            PostalCode = (
                Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID)
                .first()
                .PostalCode
            )

        return PostalCode

    def get_GSTNumber(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        GSTNumber = ""
        if Parties.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        ).exists():
            pary_ins = Parties.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).first()
            GSTNumber = pary_ins.GSTNumber
        return str(GSTNumber)

    def get_VATNumber(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        VATNumber = ""
        if Parties.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        ).exists():
            pary_ins = Parties.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).first()
            VATNumber = pary_ins.VATNumber
        return str(VATNumber)

    def get_TotalTaxableAmount_print(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalTaxableAmount = instances.TotalTaxableAmount
        TotalTaxableAmount = str(round(TotalTaxableAmount, PriceRounding))
        return str(TotalTaxableAmount)

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

    # def get_qr_image(self, instances):
    #     CompanyID = self.context.get("CompanyID")
    #     LedgerID = instances.LedgerID
    #     BranchID = instances.BranchID
    #     pk = str(instances.id)
    #     qr_image = None
    #     if QrCode.objects.filter(voucher_type="SI",master_id=pk).exists():
    #         qr_image = QrCode.objects.get(voucher_type="SI",master_id=pk).qr_code.url

    #     return qr_image

    def get_qr_image(self, instance):
        CompanyID = self.context.get("CompanyID")
        request = self.context.get("request")
        # CompanyID = get_company(CompanyID)
        generateQrCode(instance,"SI")
        # LedgerID = instance.LedgerID
        # BranchID = instance.BranchID
        # pk = str(instance.id)
        # qr_code = None
        # if QrCode.objects.filter(voucher_type="SI", master_id=pk).exists():
        #     qr_code = QrCode.objects.get(voucher_type="SI", master_id=pk)
        # serialized = QRCodeSerializer(
        #     qr_code, context={"CompanyID": CompanyID, "request": request}
        # )
        # print("=======================>>>>")
        # print(serialized.data.get("qr_code"))
        # return serialized.data.get("qr_code")
        
        pk = str(instance.id)
        if QrCode.objects.filter(voucher_type="SI", master_id=pk).exists():
            qr_code = QrCode.objects.get(voucher_type="SI", master_id=pk)
        serialized = QRCodeSerializer(
            qr_code, context={"CompanyID": CompanyID, "request": request}
        )
        return serialized.data.get("qr_code")

    def get_LoyaltyCustomerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        if instances.LoyaltyCustomerID:
            FirstName = instances.LoyaltyCustomerID.FirstName

        else:
            FirstName = ""

        return FirstName

    def get_LoyaltyCustomerID_ID(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        LoyaltyCustomerID = 0
        if instances.LoyaltyCustomerID:
            LoyaltyCustomerID = instances.LoyaltyCustomerID.LoyaltyCustomerID

        return LoyaltyCustomerID

    def get_LoyaltyPoint(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        if LoyaltyPoint.objects.filter(
            CompanyID=CompanyID,
            VoucherMasterID=instances.SalesMasterID,
            BranchID=BranchID,
            VoucherType="SI",
            is_Radeem=False,
        ).exists():
            instance = LoyaltyPoint.objects.get(
                CompanyID=CompanyID,
                VoucherMasterID=instances.SalesMasterID,
                BranchID=BranchID,
                VoucherType="SI",
                is_Radeem=False,
            )

            point = instance.Point
        else:
            point = ""

        return point

    def get_LoyaltyValue(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        if LoyaltyPoint.objects.filter(
            CompanyID=CompanyID,
            VoucherMasterID=instances.SalesMasterID,
            BranchID=BranchID,
            VoucherType="SI",
            is_Radeem=False,
        ).exists():
            instance = LoyaltyPoint.objects.get(
                CompanyID=CompanyID,
                VoucherMasterID=instances.SalesMasterID,
                BranchID=BranchID,
                VoucherType="SI",
                is_Radeem=False,
            )

            value = instance.Value
        else:
            value = ""

        return value

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID
        ).exists():
            ledger = AccountLedger.objects.get(CompanyID=CompanyID, LedgerID=LedgerID)

            LedgerName = ledger.LedgerName
        else:
            LedgerName = ""

        return LedgerName

    def get_is_customer(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        is_customer = False
        groups = [10, 29]
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=groups
        ).exists():
            is_customer = True

        return is_customer

    def get_CardTypeName(self, instances):
        CompanyID = self.context.get("CompanyID")
        TransactionTypesID = instances.CardTypeID
        BranchID = instances.BranchID

        if TransactionTypes.objects.filter(
            CompanyID=CompanyID,
            TransactionTypesID=TransactionTypesID,
            BranchID=BranchID,
        ).exists():

            transactionType = TransactionTypes.objects.get(
                CompanyID=CompanyID,
                TransactionTypesID=TransactionTypesID,
                BranchID=BranchID,
            )
            Name = transactionType.Name

        else:
            Name = ""

        CardTypeName = Name

        return CardTypeName

    def get_DetailID(self, instances):

        return ""

    def get_WareHouseName(self, instances):
        CompanyID = self.context.get("CompanyID")

        WarehouseID = instances.WarehouseID
        BranchID = instances.BranchID

        wareHouse = Warehouse.objects.get(CompanyID=CompanyID, WarehouseID=WarehouseID)

        WareHouseName = wareHouse.WarehouseName

        return WareHouseName

    def get_SalesAccountName(self, instances):
        CompanyID = self.context.get("CompanyID")
        SalesAccount = instances.SalesAccount
        BranchID = instances.BranchID

        SalesAccountName = ""
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=SalesAccount
        ).exists():
            ledger = AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=SalesAccount
            )
            SalesAccountName = ledger.LedgerName

        return SalesAccountName

    def get_SalesDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        print(PriceRounding)

        SalesMasterID = instances.SalesMasterID
        WarehouseID = instances.WarehouseID
        BranchID = instances.BranchID
        print(SalesMasterID, "SalesMasterID")
        sales_details = SalesDetails.objects.filter(
            CompanyID=CompanyID, SalesMasterID=SalesMasterID, BranchID=BranchID
        ).order_by("SalesDetailsID")
        serialized = SalesDetailsRestSerializer(
            sales_details,
            many=True,
            context={
                "CompanyID": CompanyID,
                "PriceRounding": PriceRounding,
                "WarehouseID": WarehouseID,
                "BranchID": BranchID,
            },
        )

        return serialized.data

    def get_TotalGrossAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalGrossAmt = instances.TotalGrossAmt

        # TotalGrossAmt = round(TotalGrossAmt, PriceRounding)

        return converted_float(TotalGrossAmt)

    def get_AddlDiscPercent(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        AddlDiscPercent = instances.AddlDiscPercent

        # AddlDiscPercent = round(AddlDiscPercent, PriceRounding)

        return converted_float(AddlDiscPercent)

    def get_AddlDiscAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        AddlDiscAmt = instances.AddlDiscAmt

        # AddlDiscAmt = round(AddlDiscAmt, PriceRounding)

        return converted_float(AddlDiscAmt)

    def get_TotalDiscount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalDiscount = instances.TotalDiscount

        # TotalDiscount = round(TotalDiscount, PriceRounding)

        return converted_float(TotalDiscount)

    def get_TotalTax(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalTax = instances.TotalTax

        # TotalTax = round(TotalTax, PriceRounding)

        return converted_float(TotalTax)

    def get_BillDiscPercent(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscPercent = instances.BillDiscPercent

        # BillDiscPercent = round(BillDiscPercent, PriceRounding)

        return converted_float(BillDiscPercent)

    def get_BillDiscAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscAmt = instances.BillDiscAmt

        # BillDiscAmt = round(BillDiscAmt, PriceRounding)

        return converted_float(BillDiscAmt)

    def get_NetTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        NetTotal = instances.NetTotal

        # NetTotal = round(NetTotal, PriceRounding)

        return converted_float(NetTotal)

    def get_AdditionalCost(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        AdditionalCost = instances.AdditionalCost

        # AdditionalCost = round(AdditionalCost, PriceRounding)

        return converted_float(AdditionalCost)

    def get_GrandTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        GrandTotal = instances.GrandTotal

        # GrandTotal = round(GrandTotal, PriceRounding)

        return converted_float(GrandTotal)

    def get_RoundOff(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        RoundOff = instances.RoundOff

        # RoundOff = round(RoundOff, PriceRounding)

        return converted_float(RoundOff)

    def get_CashReceived(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CashReceived = instances.CashReceived

        # CashReceived = round(CashReceived, PriceRounding)

        return converted_float(CashReceived)

    def get_CashAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CashAmount = instances.CashAmount

        # CashAmount = round(CashAmount, PriceRounding)

        return converted_float(CashAmount)

    def get_BankAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BankAmount = instances.BankAmount

        # BankAmount = round(BankAmount, PriceRounding)

        return converted_float(BankAmount)


class SalesMasterRest1Serializer(serializers.ModelSerializer):

    TotalTax = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    TotalTax_rounded = serializers.SerializerMethodField()
    TotalGrossAmt_rounded = serializers.SerializerMethodField()
    GrandTotal_Rounded = serializers.SerializerMethodField()
    is_billwised = serializers.SerializerMethodField()
    billwise_status = serializers.SerializerMethodField()

    class Meta:
        model = SalesMaster

        fields = (
            "id",
            "SalesMasterID",
            "VoucherNo",
            "Date",
            "TotalTax_rounded",
            "GrandTotal_Rounded",
            "LedgerName",
            "CustomerName",
            "TotalTax",
            "Status",
            "TotalGrossAmt_rounded",
            "GrandTotal",
            "is_billwised",
            "billwise_status"
        )
        
    def get_billwise_status(self, instance):
        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        SalesMasterID = instance.SalesMasterID
        billwise_status = "paid"
        if BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=VoucherNo, TransactionID=SalesMasterID, VoucherType="SI").exists():
            instance = BillWiseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=VoucherNo, TransactionID=SalesMasterID, VoucherType="SI").first()
            if instance.Payments == 0:
                billwise_status = "unpaid"
            elif instance.InvoiceAmount > instance.Payments:
                billwise_status = "partially paid"
        return billwise_status

    def get_is_billwised(self, instance):
        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        SalesMasterID = instance.SalesMasterID
        is_billwised = False
        if (
            BillWiseMaster.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                InvoiceNo=VoucherNo,
                TransactionID=SalesMasterID,
                VoucherType="SI",
            )
            .exclude(Payments=0)
            .exists()
        ):
            is_billwised = True
        return is_billwised

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID
        ).exists():
            ledger = AccountLedger.objects.get(CompanyID=CompanyID, LedgerID=LedgerID)

            LedgerName = ledger.LedgerName
        else:
            LedgerName = ""

        return LedgerName

    def get_TotalTax(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalTax = instances.TotalTax
        # TotalTax = round(TotalTax, PriceRounding)

        return converted_float(TotalTax)

    def get_GrandTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        GrandTotal = instances.GrandTotal
        # GrandTotal = round(GrandTotal, PriceRounding)
        return converted_float(GrandTotal)

    def get_TotalTax_rounded(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalTax = instances.TotalTax
        TotalTax_rounded = round(TotalTax, PriceRounding)
        return str(TotalTax_rounded)

    def get_TotalGrossAmt_rounded(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalGrossAmt = instances.TotalGrossAmt
        TotalGrossAmt_rounded = round(TotalGrossAmt, PriceRounding)
        return str(TotalGrossAmt_rounded)

    def get_GrandTotal_Rounded(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        GrandTotal = instances.GrandTotal
        GrandTotal_Rounded = round(GrandTotal, PriceRounding)
        return str(GrandTotal_Rounded)


class ShippingAddressListSerializer(serializers.ModelSerializer):
    CompanyID = serializers.SerializerMethodField()
    BranchID = serializers.SerializerMethodField()
    LedgerID = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    Address1 = serializers.SerializerMethodField()
    class Meta:
        model = UserAdrress
        fields = ('id','CompanyID','BranchID','Type','LedgerID','Attention','Address1',
                  'Address2','City','District','state','country','PostalCode','OfficePhone',
                  'WorkPhone','Mobile','WebURL','Email','IsDefault','AdditionalNo')
        
    def get_CompanyID(self, instance):
        CompanyID = ""
        if instance.CompanyID:
            CompanyID = instance.CompanyID.id
        return str(CompanyID)
    
    def get_BranchID(self, instance):
        BranchID = 1
        if instance.Branch:
            BranchID = instance.Branch.id
        return str(BranchID)
    
    def get_LedgerID(self, instance):
        LedgerID = ""
        if instance.Party:
            LedgerID = instance.Party.LedgerID
        return str(LedgerID)

    def get_state(self, instance):
        state = ""
        if instance.state:
            state = instance.state.id
        return str(state)
    
    def get_country(self, instance):
        country = ""
        if instance.country:
            country = instance.country.id
        return str(country)
    
    def get_Address1(self, instance):
        CustomerStateName = ""
        Billing_Address = ""
        if instance.state:
            CustomerStateName = instance.state.Name
        Billing_Address = (
            str(instance.Address1)
            + str(",")
            + str(instance.City)
            + str(",")
            + str(CustomerStateName)
            + str(",")
            + str(instance.PostalCode)
        )
        return Billing_Address


class SalesDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesDetails
        fields = (
            "id",
            "BranchID",
            "Action",
            "SalesMasterID",
            "ProductID",
            "Qty",
            "FreeQty",
            "UnitPrice",
            "ReturnQty",
            "RateWithTax",
            "CostPerPrice",
            "PriceListID",
            "DiscountPerc",
            "DiscountAmount",
            "GrossAmount",
            "TaxableAmount",
            "VATPerc",
            "VATAmount",
            "SGSTPerc",
            "SGSTAmount",
            "CGSTPerc",
            "CGSTAmount",
            "IGSTPerc",
            "IGSTAmount",
            "NetAmount",
            "CreatedDate",
            "CreatedUserID",
            "Flavour",
            "TAX1Perc",
            "TAX1Amount",
            "TAX2Perc",
            "TAX2Amount",
            "TAX3Perc",
            "TAX3Amount",
        )


class SalesDetailsRestSerializer(serializers.ModelSerializer):
    Qty = serializers.SerializerMethodField()
    FreeQty = serializers.SerializerMethodField()
    UnitPrice = serializers.SerializerMethodField()
    InclusivePrice = serializers.SerializerMethodField()
    RateWithTax = serializers.SerializerMethodField()
    CostPerPrice = serializers.SerializerMethodField()
    DiscountPerc = serializers.SerializerMethodField()
    DiscountAmount = serializers.SerializerMethodField()
    AddlDiscPerc = serializers.SerializerMethodField()
    AddlDiscAmt = serializers.SerializerMethodField()
    GrossAmount = serializers.SerializerMethodField()
    TaxableAmount = serializers.SerializerMethodField()
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
    detailID = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    TAX1Amount = serializers.SerializerMethodField()
    TAX1Perc = serializers.SerializerMethodField()
    TAX2Amount = serializers.SerializerMethodField()
    TAX2Perc = serializers.SerializerMethodField()
    TAX3Perc = serializers.SerializerMethodField()
    TAX3Amount = serializers.SerializerMethodField()
    DeliveryDetailsID = serializers.SerializerMethodField()
    OrderDetailsID = serializers.SerializerMethodField()
    ExistingQty = serializers.SerializerMethodField()
    is_VAT_inclusive = serializers.SerializerMethodField()
    is_GST_inclusive = serializers.SerializerMethodField()
    is_TAX1_inclusive = serializers.SerializerMethodField()
    is_TAX2_inclusive = serializers.SerializerMethodField()
    is_TAX3_inclusive = serializers.SerializerMethodField()
    unitPriceRounded = serializers.SerializerMethodField()
    quantityRounded = serializers.SerializerMethodField()
    actualSalesPrice = serializers.SerializerMethodField()
    netAmountRounded = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    BatchCode = serializers.SerializerMethodField()
    ActualUnitPrice = serializers.SerializerMethodField()
    SerialNos = serializers.SerializerMethodField()
    ProductCode = serializers.SerializerMethodField()
    HSNCode = serializers.SerializerMethodField()
    UnitList = serializers.SerializerMethodField()
    is_inclusive = serializers.SerializerMethodField()
    is_kfc = serializers.SerializerMethodField()
    ProductTaxName = serializers.SerializerMethodField()
    GST_Inclusive = serializers.SerializerMethodField()
    Vat_Inclusive = serializers.SerializerMethodField()
    SalesPrice = serializers.SerializerMethodField()
    ActualProductTaxName = serializers.SerializerMethodField()
    ActualProductTaxID = serializers.SerializerMethodField()
    VATAmount_print = serializers.SerializerMethodField()
    VATPerc_print = serializers.SerializerMethodField()
    NetAmount_print = serializers.SerializerMethodField()
    DiscountAmount_print = serializers.SerializerMethodField()
    TaxableAmount_print = serializers.SerializerMethodField()
    unitPrice_print = serializers.SerializerMethodField()
    BatchList = serializers.SerializerMethodField()
    product_description = serializers.SerializerMethodField()
    ManufactureDatePrint = serializers.SerializerMethodField()
    ExpiryDatePrint = serializers.SerializerMethodField()
    SalesPrice1 = serializers.SerializerMethodField()
    SalesPrice2 = serializers.SerializerMethodField()
    SalesPrice3 = serializers.SerializerMethodField()
    PurchasePrice = serializers.SerializerMethodField()
    ProductCodeVal = serializers.SerializerMethodField()
    Stock = serializers.SerializerMethodField()
    detail_errors = serializers.SerializerMethodField()
    Barcode = serializers.SerializerMethodField()
    gstPer = serializers.SerializerMethodField()
    TotalTaxRounded = serializers.SerializerMethodField()

    class Meta:
        model = SalesDetails
        fields = (
            "id",
            "unitPrice_print",
            "TaxableAmount_print",
            "DiscountAmount_print",
            "NetAmount_print",
            "VATPerc_print",
            "VATAmount_print",
            "unq_id",
            "SalesDetailsID",
            "BranchID",
            "Action",
            "SalesMasterID",
            "ProductID",
            "ProductName",
            "ProductTaxID",
            "Qty",
            "FreeQty",
            "UnitPrice",
            "ReturnQty",
            "InclusivePrice",
            "ActualUnitPrice",
            "SerialNos",
            "is_kfc",
            "RateWithTax",
            "CostPerPrice",
            "PriceListID",
            "UnitName",
            "DiscountPerc",
            "DiscountAmount",
            "AddlDiscPerc",
            "AddlDiscAmt",
            "GrossAmount",
            "TaxableAmount",
            "VATPerc",
            "VATAmount",
            "SGSTPerc",
            "SGSTAmount",
            "CGSTPerc",
            "Description",
            "ProductTaxName",
            "CGSTAmount",
            "IGSTPerc",
            "IGSTAmount",
            "KFCAmount",
            "KFCPerc",
            "NetAmount",
            "CreatedDate",
            "CreatedUserID",
            "Flavour",
            "TAX1Perc",
            "TAX1Amount",
            "TAX2Perc",
            "TAX2Amount",
            "TAX3Perc",
            "TAX3Amount",
            "TotalTax",
            "DeliveryDetailsID",
            "OrderDetailsID",
            "detailID",
            "ExistingQty",
            "is_VAT_inclusive",
            "is_GST_inclusive",
            "is_TAX1_inclusive",
            "is_TAX2_inclusive",
            "is_TAX3_inclusive",
            "UnitList",
            "is_inclusive",
            "unitPriceRounded",
            "quantityRounded",
            "actualSalesPrice",
            "netAmountRounded",
            "BatchCode",
            "ProductCode",
            "HSNCode",
            "GST_Inclusive",
            "Vat_Inclusive",
            "SalesPrice",
            "ActualProductTaxName",
            "ActualProductTaxID",
            "BatchList",
            "product_description",
            "ManufactureDatePrint",
            "ExpiryDatePrint",
            "SalesPrice1",
            "SalesPrice2",
            "SalesPrice3",
            "PurchasePrice",
            "ProductCodeVal",
            "Stock",
            "detail_errors",
            "Barcode",
            "gstPer",
            "TotalTaxRounded",
            "IsReturn"
        )

    def get_detail_errors(self, sales_details):
        detail_errors = {"Qty": "", "UnitPrice": ""}
        return detail_errors
    
    def get_TotalTaxRounded(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        TAX1Amount = purchase_details.TAX1Amount
        TAX2Amount = purchase_details.TAX2Amount
        TAX3Amount = purchase_details.TAX3Amount
        VATAmount = purchase_details.VATAmount
        IGSTAmount = purchase_details.IGSTAmount
        SGSTAmount = purchase_details.SGSTAmount
        CGSTAmount = purchase_details.CGSTAmount
        KFCAmount = purchase_details.KFCAmount

        TotalTax = (
            converted_float(TAX1Amount)
            + converted_float(TAX2Amount)
            + converted_float(TAX3Amount)
            + converted_float(VATAmount)
            + converted_float(IGSTAmount)
            + converted_float(SGSTAmount)
            + converted_float(CGSTAmount)
            + converted_float(KFCAmount)
        )
        return converted_float(TotalTax)
    
    def get_gstPer(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        IGSTPerc = sales_details.IGSTPerc
        return converted_float(IGSTPerc)

    def get_Stock(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        WarehouseID = self.context.get("WarehouseID")
        BranchID = self.context.get("BranchID")
        ProductID = sales_details.ProductID
        BatchCode = sales_details.BatchCode
        Stock = 0
        EnableProductBatchWise = get_GeneralSettings(
            CompanyID, BranchID, "EnableProductBatchWise"
        )
        if EnableProductBatchWise == True:
            if Batch.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                BatchCode=BatchCode,
                WareHouseID=WarehouseID,
            ).exists():
                Batch_ins = (
                    Batch.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        BatchCode=BatchCode,
                        WareHouseID=WarehouseID,
                    )
                    .order_by("BatchCode")
                    .last()
                )
                batch_pricelistID = Batch_ins.PriceListID
                batch_MultiFactor = PriceList.objects.get(
                    CompanyID=CompanyID, PriceListID=batch_pricelistID
                ).MultiFactor
                total_stockIN = converted_float(Batch_ins.StockIn) / converted_float(
                    batch_MultiFactor
                )
                total_stockOUT = converted_float(Batch_ins.StockOut) / converted_float(
                    batch_MultiFactor
                )

                Stock = converted_float(total_stockIN) - converted_float(total_stockOUT)
        else:
            if StockPosting.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                ProductID=ProductID,
                WareHouseID=WarehouseID,
            ):
                stock_ins = StockPosting.objects.filter(
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    ProductID=ProductID,
                    WareHouseID=WarehouseID,
                )
                qtyIn_sum = stock_ins.aggregate(Sum("QtyIn"))
                qtyIn_sum = qtyIn_sum["QtyIn__sum"]
                qtyOut_sum = stock_ins.aggregate(Sum("QtyOut"))
                qtyOut_sum = qtyOut_sum["QtyOut__sum"]
                Stock = converted_float(qtyIn_sum) - converted_float(qtyOut_sum)
        return Stock

    def get_ManufactureDatePrint(self, sales_details):
        ManufactureDate = ""
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        BatchCode = sales_details.BatchCode
        if Batch.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode
        ).exists():
            batch_details = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode
            ).first()
            if batch_details.ManufactureDate:
                ManufactureDate = batch_details.ManufactureDate
                Date = ManufactureDate.strftime("%Y/%m")
                ManufactureDate = Date
        return ManufactureDate

    def get_ExpiryDatePrint(self, sales_details):
        ExpiryDate = ""
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        BatchCode = sales_details.BatchCode
        if Batch.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode
        ).exists():
            batch_details = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode
            ).first()
            if batch_details.ExpiryDate:
                ExpiryDate = batch_details.ExpiryDate
                Date = ExpiryDate.strftime("%Y/%m")
                ExpiryDate = Date
        return ExpiryDate

    def get_BatchList(self, sales_details):
        BatchList = []
        CompanyID = self.context.get("CompanyID")
        # PriceRounding = int(self.context.get("PriceRounding"))
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        check_EnableProductBatchWise = get_GeneralSettings(
            CompanyID, BranchID, "check_EnableProductBatchWise"
        )
        if (
            check_EnableProductBatchWise
            and Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
            ).exists()
        ):
            batch_details = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
            )
            batchList = Batch_ListSalesSerializer(
                batch_details, many=True, context={"CompanyID": CompanyID}
            )
            BatchList = batchList.data
        return BatchList

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

    def get_unitPrice_print(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        UnitPrice = purchaseReturn_details.UnitPrice
        UnitPrice = round(UnitPrice, PriceRounding)
        return str(UnitPrice)

    def get_TaxableAmount_print(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")

        TaxableAmount = salesReturn_details.TaxableAmount
        TaxableAmount = round(TaxableAmount, PriceRounding)

        return str(TaxableAmount)

    def get_DiscountAmount_print(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        DiscountAmount = salesReturn_details.DiscountAmount
        DiscountAmount = round(DiscountAmount, PriceRounding)

        return str(DiscountAmount)

    def get_NetAmount_print(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        NetAmount = sales_details.NetAmount

        NetAmount = round(NetAmount, PriceRounding)

        return str(NetAmount)

    def get_ActualProductTaxName(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductTaxID = sales_details.ProductTaxID
        BranchID = sales_details.BranchID
        ActualProductTaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=ProductTaxID).exists():
            ActualProductTaxName = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=ProductTaxID
            ).TaxName
        return ActualProductTaxName

    def get_ActualProductTaxID(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ActualProductTaxID = sales_details.ProductTaxID
        return ActualProductTaxID

    def get_Vat_Inclusive(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        ProductTaxID = sales_details.ProductTaxID
        if ProductTaxID:
            VatID = ProductTaxID
        else:
            VatID = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID).VatID
        Inclusive = False
        if VatID and TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=VatID).exists():
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=VatID
            ).Inclusive
        return Inclusive

    def get_GST_Inclusive(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        ProductTaxID = sales_details.ProductTaxID
        Inclusive = False
        if ProductTaxID:
            GST = ProductTaxID
        else:
            GST = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID).GST
        if GST and TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=GST).exists():
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=GST
            ).Inclusive
        return Inclusive

    def get_PurchasePrice(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = sales_details.PriceListID
        PurchasePrice = 0
        if PriceList.objects.filter(
            CompanyID=CompanyID, PriceListID=PriceListID
        ).exists():
            PurchasePrice = PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListID
            ).PurchasePrice
        return converted_float(PurchasePrice)

    def get_SalesPrice(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = sales_details.PriceListID
        SalesPrice = 0
        if PriceList.objects.filter(
            CompanyID=CompanyID, PriceListID=PriceListID
        ).exists():
            SalesPrice = PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListID
            ).SalesPrice
        return converted_float(SalesPrice)

    def get_Barcode(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = sales_details.PriceListID
        Barcode = 0
        if PriceList.objects.filter(
            CompanyID=CompanyID, PriceListID=PriceListID
        ).exists():
            if PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListID
            ).Barcode:
                Barcode = PriceList.objects.get(
                    CompanyID=CompanyID, PriceListID=PriceListID
                ).Barcode
        return Barcode

    def get_SalesPrice1(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = sales_details.PriceListID
        SalesPrice1 = 0
        if PriceList.objects.filter(
            CompanyID=CompanyID, PriceListID=PriceListID
        ).exists():
            SalesPrice1 = PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListID
            ).SalesPrice1
        return converted_float(SalesPrice1)

    def get_SalesPrice2(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = sales_details.PriceListID
        SalesPrice2 = 0
        if PriceList.objects.filter(
            CompanyID=CompanyID, PriceListID=PriceListID
        ).exists():
            SalesPrice2 = PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListID
            ).SalesPrice2
        return converted_float(SalesPrice2)

    def get_SalesPrice3(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = sales_details.PriceListID
        SalesPrice3 = 0
        if PriceList.objects.filter(
            CompanyID=CompanyID, PriceListID=PriceListID
        ).exists():
            SalesPrice3 = PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListID
            ).SalesPrice3
        return converted_float(SalesPrice3)

    def get_ProductTaxName(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductTaxID = sales_details.ProductTaxID
        ProductTaxName = ""
        if TaxCategory.objects.filter(CompanyID=CompanyID, TaxID=ProductTaxID).exists():
            ProductTaxName = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=ProductTaxID
            ).TaxName
        return ProductTaxName

    def get_ProductName(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = sales_details.ProductID
        product = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)
        ProductName = product.ProductName
        return ProductName

    def get_is_kfc(self, sales_details):
        KFCAmount = sales_details.KFCAmount
        is_kfc = False
        if converted_float(KFCAmount) > 0:
            is_kfc = True
        return is_kfc

    def get_UnitList(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = sales_details.ProductID
        UnitList = PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID)
        serialized = PriceListRestSerializer(
            UnitList,
            many=True,
            context={"CompanyID": CompanyID, "PriceRounding": PriceRounding},
        )
        return serialized.data

    def get_ProductCode(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = sales_details.ProductID
        product = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)
        ProductCode = product.ProductCode
        return ProductCode

    def get_ProductCodeVal(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = sales_details.ProductID
        product = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)
        ProductCode = product.ProductCode
        return ProductCode

    def get_HSNCode(self, sales_details):

        CompanyID = self.context.get("CompanyID")

        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID

        product = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)

        HSNCode = product.HSNCode

        return HSNCode

    def get_BatchCode(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        BatchCode = sales_details.BatchCode
        BranchID = sales_details.BranchID
        if not BatchCode:
            BatchCode = 0

        return BatchCode

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

        return converted_float(InclusivePrice)

    def get_unitPriceRounded(self, sales_details):
        UnitPrice = sales_details.UnitPrice
        return converted_float(UnitPrice)

    def get_quantityRounded(self, sales_details):
        Qty = sales_details.Qty
        return converted_float(Qty)

    def get_actualSalesPrice(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = sales_details.PriceListID
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        SalesPrice = 0
        if PriceList.objects.filter(
            ProductID=ProductID, CompanyID=CompanyID, PriceListID=PriceListID
        ).exists():
            SalesPrice = PriceList.objects.get(
                ProductID=ProductID, CompanyID=CompanyID, PriceListID=PriceListID
            ).SalesPrice
        return converted_float(SalesPrice)

    def get_netAmountRounded(self, sales_details):
        NetAmount = sales_details.NetAmount
        return converted_float(NetAmount)

    def get_is_inclusive(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        is_inclusive = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID
        ).is_inclusive

        return is_inclusive

    def get_is_VAT_inclusive(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        VatID = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID).VatID
        Inclusive = TaxCategory.objects.get(CompanyID=CompanyID, TaxID=VatID).Inclusive
        return Inclusive

    def get_is_GST_inclusive(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        GST = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID).GST
        Inclusive = False
        if GST:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=GST
            ).Inclusive
        return Inclusive

    def get_is_TAX1_inclusive(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        Tax1 = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID).Tax1
        Inclusive = False
        if Tax1:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax1
            ).Inclusive
        return Inclusive

    def get_is_TAX2_inclusive(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        Tax2 = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID).Tax2
        Inclusive = False
        if Tax2:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax2
            ).Inclusive
        return Inclusive

    def get_is_TAX3_inclusive(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        Tax3 = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID).Tax3
        Inclusive = False
        if Tax3:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax3
            ).Inclusive
        return Inclusive

    def get_ExistingQty(self, sales_details):
        Qty = sales_details.Qty
        ExistingQty = Qty
        return converted_float(ExistingQty)

    def get_DeliveryDetailsID(self, instances):

        return 1

    def get_OrderDetailsID(self, instances):

        return 1

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

        TotalTax = (
            converted_float(TAX1Amount)
            + converted_float(TAX2Amount)
            + converted_float(TAX3Amount)
            + converted_float(VATAmount)
            + converted_float(IGSTAmount)
            + converted_float(SGSTAmount)
            + converted_float(CGSTAmount)
            + converted_float(KFCAmount)
        )

        return converted_float(TotalTax)

    def get_unq_id(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        unq_id = purchase_details.id

        return str(unq_id)

    def get_detailID(self, purchase_details):

        detailID = 0

        return detailID

    def get_UnitName(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        PriceListID = purchase_details.PriceListID
        BranchID = purchase_details.BranchID

        if PriceList.objects.filter(
            CompanyID=CompanyID, PriceListID=PriceListID
        ).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListID
            ).UnitID
            UnitName = Unit.objects.get(UnitID=UnitID, CompanyID=CompanyID).UnitName
        else:
            UnitName = ""

        return UnitName

    def get_Qty(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        Qty = sales_details.Qty

        # Qty = round(Qty, PriceRounding)

        return converted_float(Qty)

    def get_FreeQty(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        FreeQty = sales_details.FreeQty

        # FreeQty = round(FreeQty, PriceRounding)

        return converted_float(FreeQty)

    def get_UnitPrice(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        UnitPrice = sales_details.UnitPrice

        # UnitPrice = round(UnitPrice, PriceRounding)

        return converted_float(UnitPrice)

    def get_ActualUnitPrice(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        ActualUnitPrice = sales_details.UnitPrice

        # ActualUnitPrice = round(ActualUnitPrice, PriceRounding)

        return converted_float(ActualUnitPrice)

    def get_RateWithTax(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        RateWithTax = sales_details.RateWithTax

        # RateWithTax = round(RateWithTax, PriceRounding)

        return converted_float(RateWithTax)

    def get_CostPerPrice(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        CostPerPrice = sales_details.CostPerPrice

        # CostPerPrice = round(CostPerPrice, PriceRounding)

        return converted_float(CostPerPrice)

    def get_DiscountPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        DiscountPerc = sales_details.DiscountPerc

        # DiscountPerc = round(DiscountPerc, PriceRounding)

        return converted_float(DiscountPerc)

    def get_DiscountAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        DiscountAmount = sales_details.DiscountAmount

        # DiscountAmount = round(DiscountAmount, PriceRounding)

        return converted_float(DiscountAmount)

    def get_GrossAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        GrossAmount = sales_details.GrossAmount

        # GrossAmount = round(GrossAmount, PriceRounding)

        return converted_float(GrossAmount)

    def get_TaxableAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TaxableAmount = sales_details.TaxableAmount

        # TaxableAmount = round(TaxableAmount, PriceRounding)

        return converted_float(TaxableAmount)

    def get_VATPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        VATPerc = sales_details.VATPerc

        # VATPerc = round(VATPerc, PriceRounding)

        return converted_float(VATPerc)

    def get_VATPerc_print(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        VATPerc = sales_details.VATPerc

        VATPerc = str(round(VATPerc, PriceRounding))
        if "." in VATPerc:
            is_decimal = VATPerc.split(".")
            if int(is_decimal[1]) == 0:
                VATPerc = is_decimal[0]

        return str(VATPerc)

    def get_VATAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        VATAmount = sales_details.VATAmount

        # VATAmount = round(VATAmount, PriceRounding)

        return converted_float(VATAmount)

    def get_VATAmount_print(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        VATAmount = sales_details.VATAmount

        VATAmount = round(VATAmount, PriceRounding)

        return str(VATAmount)

    def get_SGSTPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        SGSTPerc = sales_details.SGSTPerc

        # SGSTPerc = round(SGSTPerc, PriceRounding)

        return converted_float(SGSTPerc)

    def get_SGSTAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        SGSTAmount = sales_details.SGSTAmount

        # SGSTAmount = round(SGSTAmount, PriceRounding)

        return converted_float(SGSTAmount)

    def get_CGSTPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        CGSTPerc = sales_details.CGSTPerc

        # CGSTPerc = round(CGSTPerc, PriceRounding)

        return converted_float(CGSTPerc)

    def get_CGSTAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        CGSTAmount = sales_details.CGSTAmount

        # CGSTAmount = round(CGSTAmount, PriceRounding)

        return converted_float(CGSTAmount)

    def get_IGSTPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        IGSTPerc = sales_details.IGSTPerc

        # IGSTPerc = round(IGSTPerc, PriceRounding)

        return converted_float(IGSTPerc)

    def get_IGSTAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        IGSTAmount = sales_details.IGSTAmount

        # IGSTAmount = round(IGSTAmount, PriceRounding)

        return converted_float(IGSTAmount)

    def get_NetAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        NetAmount = sales_details.NetAmount

        # NetAmount = round(NetAmount, PriceRounding)

        return converted_float(NetAmount)

    def get_AddlDiscPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        AddlDiscPerc = sales_details.AddlDiscPerc

        if not AddlDiscPerc:
            AddlDiscPerc = 0
        #     AddlDiscPerc = round(AddlDiscPerc, PriceRounding)
        # else:

        return converted_float(AddlDiscPerc)

    def get_AddlDiscAmt(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        AddlDiscAmt = sales_details.AddlDiscAmt

        if not AddlDiscAmt:
            AddlDiscAmt = 0
        #     AddlDiscAmt = round(AddlDiscAmt, PriceRounding)
        # else:

        return converted_float(AddlDiscAmt)

    def get_TAX1Perc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX1Perc = sales_details.TAX1Perc

        if not TAX1Perc:
            TAX1Perc = 0
        #     TAX1Perc = round(TAX1Perc, PriceRounding)
        # else:

        return converted_float(TAX1Perc)

    def get_TAX2Perc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX2Perc = sales_details.TAX2Perc

        if not TAX2Perc:
            TAX2Perc = 0
        #     TAX2Perc = round(TAX2Perc, PriceRounding)
        # else:

        return converted_float(TAX2Perc)

    def get_TAX3Perc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX3Perc = sales_details.TAX3Perc

        if not TAX3Perc:
            TAX3Perc = 0
        #     TAX3Perc = round(TAX3Perc, PriceRounding)
        # else:

        return converted_float(TAX3Perc)

    def get_TAX1Amount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX1Amount = sales_details.TAX1Amount

        if not TAX1Amount:
            TAX1Amount = 0
        #     TAX1Amount = round(TAX1Amount, PriceRounding)
        # else:

        return converted_float(TAX1Amount)

    def get_TAX2Amount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX2Amount = sales_details.TAX2Amount

        if TAX2Amount:
            TAX2Amount = 0
        #     TAX2Amount = round(TAX2Amount, PriceRounding)
        # else:

        return converted_float(TAX2Amount)

    def get_TAX3Amount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX3Amount = sales_details.TAX3Amount

        if TAX3Amount:
            TAX3Amount = 0
        #     TAX3Amount = round(TAX3Amount, PriceRounding)
        # else:

        return converted_float(TAX3Amount)

    def get_SerialNos(self, sales_details):
        SerialNos = []
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        SalesMasterID = sales_details.SalesMasterID
        SalesDetailsID = sales_details.SalesDetailsID
        if SerialNumbers.objects.filter(
            CompanyID=CompanyID,
            BranchID=BranchID,
            SalesMasterID=SalesMasterID,
            SalesDetailsID=SalesDetailsID,
            VoucherType="SI",
        ).exists():
            Serial_details = SerialNumbers.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                SalesMasterID=SalesMasterID,
                SalesDetailsID=SalesDetailsID,
                VoucherType="SI",
            )
            SerialNos = SerialNumberSerializer(
                Serial_details, many=True, context={"CompanyID": CompanyID}
            )
            SerialNos = SerialNos.data
        return SerialNos


class SerialNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = SerialNumbers
        fields = (
            "SerialNoID",
            "SerialNo",
            "ItemCode",
            "SalesMasterID",
            "SalesDetailsID",
        )

class ListSerializerforSummaryReport(serializers.Serializer):

    FromDate = serializers.DateField()
    ToDate = serializers.DateField()

class ListSerializerforReport(serializers.Serializer):

    BranchID = serializers.IntegerField()
    FromDate = serializers.DateField()
    ToDate = serializers.DateField()


class ListSerializerforStockReport(serializers.Serializer):

    BranchID = serializers.IntegerField()
    WareHouseID = serializers.IntegerField()


class ListSerializerforStockValueReport(serializers.Serializer):

    BranchID = serializers.IntegerField()
    WareHouseID = serializers.IntegerField()
    ToDate = serializers.DateField()


class ListSerializerforStockValueReportSingle(serializers.Serializer):

    BranchID = serializers.IntegerField()
    WareHouseID = serializers.IntegerField()
    FromDate = serializers.DateField()
    ToDate = serializers.DateField()
    ProductID = serializers.IntegerField()


# ============


class SalesGSTReportSerializer(serializers.ModelSerializer):

    # SalesDetails = serializers.SerializerMethodField()
    TaxableValue = serializers.SerializerMethodField()
    # TotalTaxableAmount = serializers.SerializerMethodField()
    TotalQty = serializers.SerializerMethodField()

    # id = serializers.SerializerMethodField()

    class Meta:
        model = SalesMaster
        fields = (
            "id",
            "SalesMasterID",
            "TotalTaxableAmount",
            "SGSTAmount",
            "CGSTAmount",
            "IGSTAmount",
            "BranchID",
            "Action",
            "VoucherNo",
            "TaxType",
            "Date",
            "CreditPeriod",
            "SalesType",
            "TotalQty",
            "LedgerID",
            "PriceCategoryID",
            "EmployeeID",
            "SalesAccount",
            "CustomerName",
            "TaxableValue",
            "KFCAmount",
            "TotalTax",
        )

    def get_TaxableValue(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CompanyID = self.context.get("CompanyID")
        SalesMasterID = instances.SalesMasterID
        BranchID = instances.BranchID
        sales_details = SalesDetails.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, SalesMasterID=SalesMasterID
        )
        taxable_value = sales_details.aggregate(Sum("TaxableAmount"))
        taxable_value = taxable_value["TaxableAmount__sum"]

        return converted_float(taxable_value)

    def get_TotalQty(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        SalesMasterID = instances.SalesMasterID
        BranchID = instances.BranchID
        TotalQty = 0
        sales_details = SalesDetails.objects.filter(
            CompanyID=CompanyID, SalesMasterID=SalesMasterID, BranchID=BranchID
        )
        for i in sales_details:
            TotalQty += i.Qty
        return converted_float(TotalQty)

    # def get_TotalTaxableAmount(self, instances):
    #     CompanyID = self.context.get("CompanyID")
    #     PriceRounding = self.context.get("PriceRounding")
    #     print(PriceRounding)

    #     SalesMasterID = instances.SalesMasterID
    #     BranchID = instances.BranchID
    #     TotalTaxableAmount = 0
    #     sales_details = SalesDetails.objects.filter(
    #         CompanyID=CompanyID, SalesMasterID=SalesMasterID, BranchID=BranchID)
    #     for i in sales_details:
    #         TotalTaxableAmount += i.TaxableAmount

    #     return converted_float(TotalTaxableAmount)


# ===============
class SalesMasterReportSerializer(serializers.ModelSerializer):

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
    SalesAccountName = serializers.SerializerMethodField()
    WareHouseName = serializers.SerializerMethodField()
    CardTypeName = serializers.SerializerMethodField()
    DetailID = serializers.SerializerMethodField()
    BillDiscPercent = serializers.SerializerMethodField()
    BillDiscAmt = serializers.SerializerMethodField()
    CashSales = serializers.SerializerMethodField()
    BankSales = serializers.SerializerMethodField()
    CreditSales = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    LedgerBalance = serializers.SerializerMethodField()
    AccountGroupUnder = serializers.SerializerMethodField()
    OldLedgerBalance = serializers.SerializerMethodField()
    Balance = serializers.SerializerMethodField()
    CashName = serializers.SerializerMethodField()
    BankName = serializers.SerializerMethodField()
    Country_of_Supply_name = serializers.SerializerMethodField()
    State_of_Supply_name = serializers.SerializerMethodField()
    Country_of_Supply = serializers.SerializerMethodField()
    State_of_Supply = serializers.SerializerMethodField()
    billwise_status = serializers.SerializerMethodField()
    EmployeeName = serializers.SerializerMethodField()

    class Meta:
        model = SalesMaster
        fields = (
            "id",
            "SalesMasterID",
            "BranchID",
            "Action",
            "VoucherNo",
            "Date",
            "CashID",
            "BankID",
            "CashName",
            "BankName",
            "CreditPeriod",
            "LedgerID",
            "LedgerName",
            "LedgerBalance",
            "OldLedgerBalance",
            "AccountGroupUnder",
            "GST_Treatment",
            "VAT_Treatment",
            "PriceCategoryID",
            "EmployeeID",
            "SalesAccount",
            "SalesAccountName",
            "CustomerName",
            "Address1",
            "Address2",
            "Address3",
            "Notes",
            "FinacialYearID",
            "TotalGrossAmt",
            "AddlDiscPercent",
            "AddlDiscAmt",
            "TotalDiscount",
            "TotalTax",
            "Country_of_Supply",
            "State_of_Supply",
            "NetTotal",
            "AdditionalCost",
            "GrandTotal",
            "RoundOff",
            "CashReceived",
            "CashAmount",
            "BankAmount",
            "WarehouseID",
            "WareHouseName",
            "TableID",
            "SeatNumber",
            "NoOfGuests",
            "INOUT",
            "TokenNumber",
            "CardTypeID",
            "CardTypeName",
            "CardNumber",
            "IsActive",
            "IsPosted",
            "SalesType",
            "CreatedDate",
            "UpdatedDate",
            "CreatedUserID",
            "TaxID",
            "TaxType",
            "BillDiscPercent",
            "BillDiscAmt",
            "VATAmount",
            "SGSTAmount",
            "CGSTAmount",
            "IGSTAmount",
            "Country_of_Supply_name",
            "State_of_Supply_name",
            "TAX1Amount",
            "TAX2Amount",
            "TAX3Amount",
            "Balance",
            "TransactionTypeID",
            "DetailID",
            "CashSales",
            "BankSales",
            "CreditSales",
            "SalesDetails",
            "billwise_status",
            "EmployeeName"
        )
        
    
    def get_EmployeeName(self, instance):
        EmployeeName = ""
        CompanyID = self.context.get("CompanyID")
        EmployeeID = instance.EmployeeID
        BranchID = instance.BranchID
        if Employee.objects.filter(CompanyID=CompanyID,BranchID=BranchID,EmployeeID=EmployeeID).exists():
            EmployeeName = Employee.objects.filter(CompanyID=CompanyID,BranchID=BranchID,EmployeeID=EmployeeID).first().FirstName
        return EmployeeName
        
    def get_billwise_status(self, instance):
        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        InvoiceNo = instance.VoucherNo
        SalesMasterID = instance.SalesMasterID
        GrandTotal = instance.GrandTotal
        billwise_status = "paid"

        if BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=InvoiceNo, TransactionID=SalesMasterID).exists():
            billwise_ins = BillWiseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=InvoiceNo, TransactionID=SalesMasterID).first()
            Payments = billwise_ins.Payments

            if converted_float(Payments) == converted_float(0):
                billwise_status = "unpaid"
            elif converted_float(Payments) < converted_float(GrandTotal):
                billwise_status = "partially paid"
        return billwise_status

    def get_Country_of_Supply(self, instances):
        CompanyID = self.context.get("CompanyID")
        Country_of_Supply = instances.Country_of_Supply
        return str(Country_of_Supply)

    def get_State_of_Supply(self, instances):
        CompanyID = self.context.get("CompanyID")
        State_of_Supply = instances.State_of_Supply
        return str(State_of_Supply)

    def get_Country_of_Supply_name(self, instances):
        CompanyID = self.context.get("CompanyID")
        Country_of_Supply = instances.Country_of_Supply
        Country_of_Supply_name = ""
        if Country_of_Supply:
            if Country.objects.filter(id=Country_of_Supply).exists():
                Country_of_Supply_name = Country.objects.get(
                    id=Country_of_Supply
                ).Country_Name
        return Country_of_Supply_name

    def get_State_of_Supply_name(self, instances):
        CompanyID = self.context.get("CompanyID")
        State_of_Supply = instances.State_of_Supply
        State_of_Supply_name = ""
        if State_of_Supply:
            if State.objects.filter(id=State_of_Supply).exists():
                State_of_Supply_name = State.objects.get(id=State_of_Supply).Name
        return State_of_Supply_name

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID
        ).exists():
            ledger = AccountLedger.objects.get(CompanyID=CompanyID, LedgerID=LedgerID)

            LedgerName = ledger.LedgerName
        else:
            LedgerName = ""

        return LedgerName

    def get_CashName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.CashID
        BranchID = instances.BranchID

        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID
        ).exists():
            ledger = AccountLedger.objects.get(CompanyID=CompanyID, LedgerID=LedgerID)
            CashName = ledger.LedgerName
        else:
            CashName = ""
        return CashName

    def get_BankName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.BankID
        BranchID = instances.BranchID

        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID
        ).exists():
            ledger = AccountLedger.objects.get(CompanyID=CompanyID, LedgerID=LedgerID)
            BankName = ledger.LedgerName
        else:
            BankName = ""
        return BankName

    def get_OldLedgerBalance(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        OldLedgerBalance = instances.OldLedgerBalance

        OldLedgerBalance = round(OldLedgerBalance, PriceRounding)

        return converted_float(OldLedgerBalance)

    def get_AccountGroupUnder(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        AccountGroupUnder = 0

        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID
        ).exists():
            AccountGroupUnder = AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID
            ).AccountGroupUnder

        return AccountGroupUnder

    def get_LedgerBalance(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        ledger_instances = LedgerPosting.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        )
        Balance = 0
        TotalDebit = 0
        TotalCredit = 0

        for i in ledger_instances:
            TotalDebit += i.Debit
            TotalCredit += i.Credit

        LedgerBalance = converted_float(TotalDebit) - converted_float(TotalCredit)

        return LedgerBalance

    def get_id(self, instances):
        id = instances.id

        return str(id)

    def get_CashSales(self, instances):
        CompanyID = self.context.get("CompanyID")
        FromDate = self.context.get("FromDate")
        ToDate = self.context.get("ToDate")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        TotalDebit = 0
        TotalCredit = 0
        account_instance = AccountLedger.objects.filter(
            CompanyID=CompanyID, AccountGroupUnder=9
        )
        print(LedgerID, "ledger_ids", "cash_salessssss", account_instance)
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, AccountGroupUnder=9
        ).exists():
            account_instance = AccountLedger.objects.filter(
                CompanyID=CompanyID, AccountGroupUnder=9
            )
            ledger_ids = account_instance.values_list("LedgerID", flat=True)
            print(ledger_ids, "cash_salessssss")
            if LedgerPosting.objects.filter(
                CompanyID=CompanyID,
                LedgerID__in=ledger_ids,
                Date__gte=FromDate,
                Date__lte=ToDate,
                VoucherType="SI",
                VoucherMasterID=instances.SalesMasterID,
            ).exists():
                ledger_ins = LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    LedgerID__in=ledger_ids,
                    Date__gte=FromDate,
                    Date__lte=ToDate,
                    VoucherType="SI",
                    VoucherMasterID=instances.SalesMasterID,
                )
                for i in ledger_ins:
                    print(i.id, "forloop")
                    TotalDebit += converted_float(i.Debit)
                    TotalCredit += converted_float(i.Credit)

        CashSales = converted_float(TotalDebit) - converted_float(TotalCredit)
        return CashSales

    def get_BankSales(self, instances):
        CompanyID = self.context.get("CompanyID")
        FromDate = self.context.get("FromDate")
        ToDate = self.context.get("ToDate")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        TotalDebit = 0
        TotalCredit = 0
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, AccountGroupUnder=8
        ).exists():
            account_instance = AccountLedger.objects.filter(
                CompanyID=CompanyID, AccountGroupUnder=8
            )
            ledger_ids = account_instance.values_list("LedgerID", flat=True)
            print(ledger_ids, "bank_salessssss")
            if LedgerPosting.objects.filter(
                CompanyID=CompanyID,
                LedgerID__in=ledger_ids,
                Date__gte=FromDate,
                Date__lte=ToDate,
                VoucherType="SI",
                VoucherMasterID=instances.SalesMasterID,
            ).exists():
                ledger_ins = LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    LedgerID__in=ledger_ids,
                    Date__gte=FromDate,
                    Date__lte=ToDate,
                    VoucherType="SI",
                    VoucherMasterID=instances.SalesMasterID,
                )
                for i in ledger_ins:
                    TotalDebit += converted_float(i.Debit)
                    TotalCredit += converted_float(i.Credit)

        BankSales = converted_float(TotalDebit) - converted_float(TotalCredit)
        return BankSales

    def get_CreditSales(self, instances):
        CompanyID = self.context.get("CompanyID")
        FromDate = self.context.get("FromDate")
        ToDate = self.context.get("ToDate")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        GrandTotal = 0
        CreditSales = 0
        TotalDebit = 0
        TotalCredit = 0

        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=[8, 9]
        ).exists():
            account_instance = AccountLedger.objects.filter(
                CompanyID=CompanyID, AccountGroupUnder__in=[8, 9]
            )
            ledger_ids = account_instance.values_list("LedgerID", flat=True)
            if LedgerPosting.objects.filter(
                CompanyID=CompanyID,
                LedgerID__in=ledger_ids,
                Date__gte=FromDate,
                Date__lte=ToDate,
                VoucherType="SI",
                VoucherMasterID=instances.SalesMasterID,
            ).exists():
                TotalDebit = LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    LedgerID__in=ledger_ids,
                    Date__gte=FromDate,
                    Date__lte=ToDate,
                    VoucherType="SI",
                    VoucherMasterID=instances.SalesMasterID,
                ).aggregate(Sum("Debit"))["Debit__sum"]
                TotalCredit = LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    LedgerID__in=ledger_ids,
                    Date__gte=FromDate,
                    Date__lte=ToDate,
                    VoucherType="SI",
                    VoucherMasterID=instances.SalesMasterID,
                ).aggregate(Sum("Credit"))["Credit__sum"]
                # for i in ledger_ins:
                #     TotalDebit += converted_float(i.Debit)
                #     TotalCredit += converted_float(i.Credit)

            CreditSales = converted_float(TotalDebit) - converted_float(TotalCredit)
            GrandTotal = instances.GrandTotal
            print(
                GrandTotal,
                CreditSales,
                "converted_float(IFFFFFFFF) - converted_float(CreditSales)",
            )
            CreditSales = converted_float(GrandTotal) - converted_float(CreditSales)
        else:
            print(instances.SalesMasterID, "ELSE............")
            account_instance = AccountLedger.objects.filter(CompanyID=CompanyID)
            ledger_ids = account_instance.values_list("LedgerID", flat=True)
            if LedgerPosting.objects.filter(
                CompanyID=CompanyID,
                LedgerID=LedgerID,
                Date__gte=FromDate,
                Date__lte=ToDate,
                VoucherType="SI",
                VoucherMasterID=instances.SalesMasterID,
            ).exists():
                TotalDebit = LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    LedgerID=LedgerID,
                    Date__gte=FromDate,
                    Date__lte=ToDate,
                    VoucherType="SI",
                    VoucherMasterID=instances.SalesMasterID,
                ).aggregate(Sum("Debit"))["Debit__sum"]
                TotalCredit = LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    LedgerID=LedgerID,
                    Date__gte=FromDate,
                    Date__lte=ToDate,
                    VoucherType="SI",
                    VoucherMasterID=instances.SalesMasterID,
                ).aggregate(Sum("Credit"))["Credit__sum"]
                # for i in ledger_ins:
                #     TotalDebit += converted_float(i.Debit)
                #     TotalCredit += converted_float(i.Credit)
                #     print(i.pk, "************************************")

            CreditSales = converted_float(TotalDebit) - converted_float(TotalCredit)
            GrandTotal = instances.GrandTotal
            print(
                TotalDebit,
                TotalCredit,
                CreditSales,
                "converted_float(ELSEEEEEEEEEE) - converted_float(CreditSales)",
            )

        return CreditSales

    def get_CardTypeName(self, instances):
        CompanyID = self.context.get("CompanyID")
        TransactionTypesID = instances.CardTypeID
        BranchID = instances.BranchID

        if TransactionTypes.objects.filter(
            CompanyID=CompanyID,
            TransactionTypesID=TransactionTypesID,
            BranchID=BranchID,
        ).exists():

            transactionType = TransactionTypes.objects.get(
                CompanyID=CompanyID,
                TransactionTypesID=TransactionTypesID,
                BranchID=BranchID,
            )
            Name = transactionType.Name

        else:
            Name = ""

        CardTypeName = Name

        return CardTypeName

    def get_DetailID(self, instances):

        return ""

    def get_Balance(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        Balance = instances.Balance

        Balance = round(Balance, PriceRounding)

        return converted_float(Balance)

    def get_WareHouseName(self, instances):
        CompanyID = self.context.get("CompanyID")

        WarehouseID = instances.WarehouseID
        BranchID = instances.BranchID

        wareHouse = Warehouse.objects.get(CompanyID=CompanyID, WarehouseID=WarehouseID)

        WareHouseName = wareHouse.WarehouseName

        return WareHouseName

    def get_SalesAccountName(self, instances):
        CompanyID = self.context.get("CompanyID")
        SalesAccount = instances.SalesAccount
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(CompanyID=CompanyID, LedgerID=SalesAccount)

        SalesAccountName = ledger.LedgerName

        return SalesAccountName

    def get_SalesDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        print(PriceRounding)

        SalesMasterID = instances.SalesMasterID
        WarehouseID = instances.WarehouseID
        BranchID = instances.BranchID
        sales_details = SalesDetails.objects.filter(
            CompanyID=CompanyID, SalesMasterID=SalesMasterID, BranchID=BranchID
        )
        serialized = SalesDetailsRestSerializer(
            sales_details,
            many=True,
            context={
                "CompanyID": CompanyID,
                "PriceRounding": PriceRounding,
                "WarehouseID": WarehouseID,
            },
        )

        return serialized.data

    def get_TotalGrossAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalGrossAmt = instances.TotalGrossAmt

        TotalGrossAmt = round(TotalGrossAmt, PriceRounding)

        return converted_float(TotalGrossAmt)

    def get_AddlDiscPercent(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        AddlDiscPercent = instances.AddlDiscPercent

        AddlDiscPercent = round(AddlDiscPercent, PriceRounding)

        return converted_float(AddlDiscPercent)

    def get_AddlDiscAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        AddlDiscAmt = instances.AddlDiscAmt

        AddlDiscAmt = round(AddlDiscAmt, PriceRounding)

        return converted_float(AddlDiscAmt)

    def get_TotalDiscount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalDiscount = instances.TotalDiscount

        TotalDiscount = round(TotalDiscount, PriceRounding)

        return converted_float(TotalDiscount)

    def get_TotalTax(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalTax = instances.TotalTax

        TotalTax = round(TotalTax, PriceRounding)

        return converted_float(TotalTax)

    def get_BillDiscPercent(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscPercent = instances.BillDiscPercent

        BillDiscPercent = round(BillDiscPercent, PriceRounding)

        return converted_float(BillDiscPercent)

    def get_BillDiscAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscAmt = instances.BillDiscAmt

        BillDiscAmt = round(BillDiscAmt, PriceRounding)

        return converted_float(BillDiscAmt)

    def get_NetTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        NetTotal = instances.NetTotal

        NetTotal = round(NetTotal, PriceRounding)

        return converted_float(NetTotal)

    def get_AdditionalCost(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        AdditionalCost = instances.AdditionalCost

        AdditionalCost = round(AdditionalCost, PriceRounding)

        return converted_float(AdditionalCost)

    def get_GrandTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        GrandTotal = instances.GrandTotal

        GrandTotal = round(GrandTotal, PriceRounding)

        return converted_float(GrandTotal)

    def get_RoundOff(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        RoundOff = instances.RoundOff

        RoundOff = round(RoundOff, PriceRounding)

        return converted_float(RoundOff)

    def get_CashReceived(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CashReceived = instances.CashReceived

        CashReceived = round(CashReceived, PriceRounding)

        return converted_float(CashReceived)

    def get_CashAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CashAmount = instances.CashAmount

        CashAmount = round(CashAmount, PriceRounding)

        return converted_float(CashAmount)

    def get_BankAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BankAmount = instances.BankAmount

        BankAmount = round(BankAmount, PriceRounding)

        return converted_float(BankAmount)


class SalesReportNewSerializer(serializers.ModelSerializer):
    LedgerName = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    TotalDiscount = serializers.SerializerMethodField()
    NetTotal = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    TotalGrossAmt = serializers.SerializerMethodField()
    CashSales = serializers.SerializerMethodField()
    BankSales = serializers.SerializerMethodField()
    CreditSales = serializers.SerializerMethodField()
    BillDiscAmt = serializers.SerializerMethodField()

    class Meta:
        model = SalesMaster
        fields = (
            "id",
            "VoucherNo",
            "BillDiscAmt",
            "Date",
            "LedgerID",
            "LedgerName",
            "EmployeeID",
            "CustomerName",
            "TotalGrossAmt",
            "TotalDiscount",
            "TotalTax",
            "NetTotal",
            "GrandTotal",
            "CashSales",
            "BankSales",
            "CreditSales",
        )

    def get_BillDiscAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscAmt = round(instances.BillDiscAmt, PriceRounding)
        return converted_float(BillDiscAmt)

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID
        ).exists():
            ledger = AccountLedger.objects.get(CompanyID=CompanyID, LedgerID=LedgerID)

            LedgerName = ledger.LedgerName
        else:
            LedgerName = ""

        return LedgerName

    def get_CashSales(self, instances):
        CompanyID = self.context.get("CompanyID")
        FromDate = self.context.get("FromDate")
        ToDate = self.context.get("ToDate")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        TotalDebit = 0
        TotalCredit = 0
        account_instance = AccountLedger.objects.filter(
            CompanyID=CompanyID, AccountGroupUnder=9
        )
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, AccountGroupUnder=9
        ).exists():
            account_instance = AccountLedger.objects.filter(
                CompanyID=CompanyID, AccountGroupUnder=9
            )
            ledger_ids = account_instance.values_list("LedgerID", flat=True)
            if LedgerPosting.objects.filter(
                CompanyID=CompanyID,
                LedgerID__in=ledger_ids,
                Date__gte=FromDate,
                Date__lte=ToDate,
                VoucherType="SI",
                VoucherMasterID=instances.SalesMasterID,
            ).exists():
                ledger_ins = LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    LedgerID__in=ledger_ids,
                    Date__gte=FromDate,
                    Date__lte=ToDate,
                    VoucherType="SI",
                    VoucherMasterID=instances.SalesMasterID,
                )
                for i in ledger_ins:
                    print(i.id, "forloop")
                    TotalDebit += converted_float(i.Debit)
                    TotalCredit += converted_float(i.Credit)

        CashSales = converted_float(TotalDebit) - converted_float(TotalCredit)
        return CashSales

    def get_BankSales(self, instances):
        CompanyID = self.context.get("CompanyID")
        FromDate = self.context.get("FromDate")
        ToDate = self.context.get("ToDate")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        TotalDebit = 0
        TotalCredit = 0
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, AccountGroupUnder=8
        ).exists():
            account_instance = AccountLedger.objects.filter(
                CompanyID=CompanyID, AccountGroupUnder=8
            )
            ledger_ids = account_instance.values_list("LedgerID", flat=True)
            if LedgerPosting.objects.filter(
                CompanyID=CompanyID,
                LedgerID__in=ledger_ids,
                Date__gte=FromDate,
                Date__lte=ToDate,
                VoucherType="SI",
                VoucherMasterID=instances.SalesMasterID,
            ).exists():
                ledger_ins = LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    LedgerID__in=ledger_ids,
                    Date__gte=FromDate,
                    Date__lte=ToDate,
                    VoucherType="SI",
                    VoucherMasterID=instances.SalesMasterID,
                )
                for i in ledger_ins:
                    TotalDebit += converted_float(i.Debit)
                    TotalCredit += converted_float(i.Credit)

        BankSales = converted_float(TotalDebit) - converted_float(TotalCredit)
        return BankSales

    def get_CreditSales(self, instances):
        CompanyID = self.context.get("CompanyID")
        FromDate = self.context.get("FromDate")
        ToDate = self.context.get("ToDate")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        GrandTotal = 0
        CreditSales = 0
        TotalDebit = 0
        TotalCredit = 0

        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=[8, 9]
        ).exists():
            account_instance = AccountLedger.objects.filter(
                CompanyID=CompanyID, AccountGroupUnder__in=[8, 9]
            )
            ledger_ids = account_instance.values_list("LedgerID", flat=True)
            if LedgerPosting.objects.filter(
                CompanyID=CompanyID,
                LedgerID__in=ledger_ids,
                Date__gte=FromDate,
                Date__lte=ToDate,
                VoucherType="SI",
                VoucherMasterID=instances.SalesMasterID,
            ).exists():
                TotalDebit = LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    LedgerID__in=ledger_ids,
                    Date__gte=FromDate,
                    Date__lte=ToDate,
                    VoucherType="SI",
                    VoucherMasterID=instances.SalesMasterID,
                ).aggregate(Sum("Debit"))["Debit__sum"]
                TotalCredit = LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    LedgerID__in=ledger_ids,
                    Date__gte=FromDate,
                    Date__lte=ToDate,
                    VoucherType="SI",
                    VoucherMasterID=instances.SalesMasterID,
                ).aggregate(Sum("Credit"))["Credit__sum"]
                # for i in ledger_ins:
                #     TotalDebit += converted_float(i.Debit)
                #     TotalCredit += converted_float(i.Credit)

            CreditSales = converted_float(TotalDebit) - converted_float(TotalCredit)
            GrandTotal = instances.GrandTotal

            CreditSales = converted_float(GrandTotal) - converted_float(CreditSales)
        else:
            print(instances.SalesMasterID, "ELSE............")
            account_instance = AccountLedger.objects.filter(CompanyID=CompanyID)
            ledger_ids = account_instance.values_list("LedgerID", flat=True)
            if LedgerPosting.objects.filter(
                CompanyID=CompanyID,
                LedgerID=LedgerID,
                Date__gte=FromDate,
                Date__lte=ToDate,
                VoucherType="SI",
                VoucherMasterID=instances.SalesMasterID,
            ).exists():
                TotalDebit = LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    LedgerID=LedgerID,
                    Date__gte=FromDate,
                    Date__lte=ToDate,
                    VoucherType="SI",
                    VoucherMasterID=instances.SalesMasterID,
                ).aggregate(Sum("Debit"))["Debit__sum"]
                TotalCredit = LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    LedgerID=LedgerID,
                    Date__gte=FromDate,
                    Date__lte=ToDate,
                    VoucherType="SI",
                    VoucherMasterID=instances.SalesMasterID,
                ).aggregate(Sum("Credit"))["Credit__sum"]
                # for i in ledger_ins:
                #     TotalDebit += converted_float(i.Debit)
                #     TotalCredit += converted_float(i.Credit)
                #     print(i.pk, "************************************")

            CreditSales = converted_float(TotalDebit) - converted_float(TotalCredit)
            GrandTotal = instances.GrandTotal

        return CreditSales

    def get_TotalGrossAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalGrossAmt = instances.TotalGrossAmt

        TotalGrossAmt = round(TotalGrossAmt, PriceRounding)

        return converted_float(TotalGrossAmt)

    def get_TotalDiscount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalDiscount = instances.TotalDiscount

        TotalDiscount = round(TotalDiscount, PriceRounding)

        return converted_float(TotalDiscount)

    def get_TotalTax(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalTax = instances.TotalTax

        TotalTax = round(TotalTax, PriceRounding)

        return converted_float(TotalTax)

    def get_NetTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        NetTotal = instances.NetTotal

        NetTotal = round(NetTotal, PriceRounding)

        return converted_float(NetTotal)

    def get_AdditionalCost(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        AdditionalCost = instances.AdditionalCost

        AdditionalCost = round(AdditionalCost, PriceRounding)

        return converted_float(AdditionalCost)

    def get_GrandTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        GrandTotal = instances.GrandTotal

        GrandTotal = round(GrandTotal, PriceRounding)

        return converted_float(GrandTotal)


class SalesDetailsReportSerializer(serializers.ModelSerializer):

    Qty = serializers.SerializerMethodField()
    FreeQty = serializers.SerializerMethodField()
    UnitPrice = serializers.SerializerMethodField()
    RateWithTax = serializers.SerializerMethodField()
    CostPerPrice = serializers.SerializerMethodField()
    DiscountPerc = serializers.SerializerMethodField()
    DiscountAmount = serializers.SerializerMethodField()
    GrossAmount = serializers.SerializerMethodField()
    TaxableAmount = serializers.SerializerMethodField()
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
    DetailsID = serializers.SerializerMethodField()
    MasterID = serializers.SerializerMethodField()

    class Meta:
        model = SalesDetails
        fields = (
            "id",
            "DetailsID",
            "BranchID",
            "Action",
            "MasterID",
            "ProductID",
            "ProductName",
            "Qty",
            "FreeQty",
            "UnitPrice",
            "ReturnQty",
            "RateWithTax",
            "CostPerPrice",
            "PriceListID",
            "DiscountPerc",
            "DiscountAmount",
            "GrossAmount",
            "TaxableAmount",
            "VATPerc",
            "VATAmount",
            "SGSTPerc",
            "SGSTAmount",
            "CGSTPerc",
            "CGSTAmount",
            "IGSTPerc",
            "IGSTAmount",
            "NetAmount",
            "CreatedDate",
            "CreatedUserID",
            "Flavour",
            "TAX1Perc",
            "TAX1Amount",
            "TAX2Perc",
            "TAX2Amount",
            "TAX3Perc",
            "TAX3Amount",
        )

    def get_ProductName(self, sales_details):

        CompanyID = self.context.get("CompanyID")

        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID

        product = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)

        ProductName = product.ProductName

        return ProductName

    def get_DetailsID(self, sales_details):

        DetailsID = sales_details.SalesDetailsID

        return DetailsID

    def get_MasterID(self, sales_details):

        MasterID = sales_details.SalesMasterID

        return MasterID

    def get_Qty(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        Qty = sales_details.Qty

        Qty = round(Qty, PriceRounding)

        return converted_float(Qty)

    def get_FreeQty(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        FreeQty = sales_details.FreeQty

        FreeQty = round(FreeQty, PriceRounding)

        return converted_float(FreeQty)

    def get_UnitPrice(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        UnitPrice = sales_details.UnitPrice

        UnitPrice = round(UnitPrice, PriceRounding)

        return converted_float(UnitPrice)

    def get_RateWithTax(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        RateWithTax = sales_details.RateWithTax

        RateWithTax = round(RateWithTax, PriceRounding)

        return converted_float(RateWithTax)

    def get_CostPerPrice(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        CostPerPrice = sales_details.CostPerPrice

        CostPerPrice = round(CostPerPrice, PriceRounding)

        return converted_float(CostPerPrice)

    def get_DiscountPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        DiscountPerc = sales_details.DiscountPerc

        DiscountPerc = round(DiscountPerc, PriceRounding)

        return converted_float(DiscountPerc)

    def get_DiscountAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        DiscountAmount = sales_details.DiscountAmount

        DiscountAmount = round(DiscountAmount, PriceRounding)

        return converted_float(DiscountAmount)

    def get_GrossAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        GrossAmount = sales_details.GrossAmount

        GrossAmount = round(GrossAmount, PriceRounding)

        return converted_float(GrossAmount)

    def get_TaxableAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TaxableAmount = sales_details.TaxableAmount

        TaxableAmount = round(TaxableAmount, PriceRounding)

        return converted_float(TaxableAmount)

    def get_VATPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        VATPerc = sales_details.VATPerc

        VATPerc = round(VATPerc, PriceRounding)

        return converted_float(VATPerc)

    def get_VATAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        VATAmount = sales_details.VATAmount

        VATAmount = round(VATAmount, PriceRounding)

        return converted_float(VATAmount)

    def get_SGSTPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        SGSTPerc = sales_details.SGSTPerc

        SGSTPerc = round(SGSTPerc, PriceRounding)

        return converted_float(SGSTPerc)

    def get_SGSTAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        SGSTAmount = sales_details.SGSTAmount

        SGSTAmount = round(SGSTAmount, PriceRounding)

        return converted_float(SGSTAmount)

    def get_CGSTPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        CGSTPerc = sales_details.CGSTPerc

        CGSTPerc = round(CGSTPerc, PriceRounding)

        return converted_float(CGSTPerc)

    def get_CGSTAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        CGSTAmount = sales_details.CGSTAmount

        CGSTAmount = round(CGSTAmount, PriceRounding)

        return converted_float(CGSTAmount)

    def get_IGSTPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        IGSTPerc = sales_details.IGSTPerc

        IGSTPerc = round(IGSTPerc, PriceRounding)

        return converted_float(IGSTPerc)

    def get_IGSTAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        IGSTAmount = sales_details.IGSTAmount

        IGSTAmount = round(IGSTAmount, PriceRounding)

        return converted_float(IGSTAmount)

    def get_NetAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        NetAmount = sales_details.NetAmount

        NetAmount = round(NetAmount, PriceRounding)

        return converted_float(NetAmount)


class SalesMasterForReturnSerializer(serializers.ModelSerializer):

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
    SalesAccountName = serializers.SerializerMethodField()
    WareHouseName = serializers.SerializerMethodField()
    CardTypeName = serializers.SerializerMethodField()
    DetailID = serializers.SerializerMethodField()
    BillDiscPercent = serializers.SerializerMethodField()
    BillDiscAmt = serializers.SerializerMethodField()
    ProductList = serializers.SerializerMethodField()
    LedgerList = serializers.SerializerMethodField()
    is_customer = serializers.SerializerMethodField()
    Mobile = serializers.SerializerMethodField()
    GSTNumber = serializers.SerializerMethodField()

    class Meta:
        model = SalesMaster
        fields = (
            "id",
            "SalesMasterID",
            "BranchID",
            "Action",
            "VoucherNo",
            "Date",
            "CreditPeriod",
            "LedgerID",
            "LedgerName",
            "ProductList",
            "Mobile",
            "LedgerList",
            "GSTNumber",
            "Country_of_Supply",
            "State_of_Supply",
            "VAT_Treatment",
            "PriceCategoryID",
            "EmployeeID",
            "SalesAccount",
            "SalesAccountName",
            "CustomerName",
            "Address1",
            "Address2",
            "Address3",
            "GST_Treatment",
            "Notes",
            "FinacialYearID",
            "TotalGrossAmt",
            "AddlDiscPercent",
            "AddlDiscAmt",
            "TotalDiscount",
            "TotalTax",
            "is_customer",
            "NetTotal",
            "AdditionalCost",
            "GrandTotal",
            "RoundOff",
            "CashReceived",
            "CashAmount",
            "BankAmount",
            "WarehouseID",
            "WareHouseName",
            "TableID",
            "SeatNumber",
            "NoOfGuests",
            "INOUT",
            "TokenNumber",
            "CardTypeID",
            "CardTypeName",
            "CardNumber",
            "IsActive",
            "IsPosted",
            "SalesType",
            "CreatedDate",
            "UpdatedDate",
            "CreatedUserID",
            "TaxID",
            "TaxType",
            "BillDiscPercent",
            "BillDiscAmt",
            "VATAmount",
            "SGSTAmount",
            "CGSTAmount",
            "IGSTAmount",
            "TAX1Amount",
            "TAX2Amount",
            "TAX3Amount",
            "Balance",
            "TransactionTypeID",
            "DetailID",
            "SalesDetails",
        )

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(CompanyID=CompanyID, LedgerID=LedgerID)

        LedgerName = ledger.LedgerName

        return LedgerName

    def get_GSTNumber(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        GSTNumber = ""
        if Parties.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        ).exists():
            pary_ins = Parties.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).first()
            GSTNumber = pary_ins.GSTNumber
        return str(GSTNumber)

    def get_LedgerList(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        LedgerID = instances.LedgerID
        balance = get_BalanceFromLedgerPost(CompanyID, LedgerID, BranchID)
        LedgerName = AccountLedger.objects.get(
            CompanyID=CompanyID, LedgerID=LedgerID
        ).LedgerName
        LedgerList = [
            {
                "name": LedgerName,
                "LedgerID": LedgerID,
                "Balance": balance
            }
        ]

        return LedgerList

    def get_Mobile(self, instances):

        CompanyID = self.context.get("CompanyID")
        Mobile = ""
        if Parties.objects.filter(
            LedgerID=instances.LedgerID, CompanyID=CompanyID
        ).exists():
            Mobile = Parties.objects.get(
                LedgerID=instances.LedgerID, CompanyID=CompanyID
            ).Mobile

        return str(Mobile)

    def get_is_customer(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        is_customer = False
        groups = [10, 29]
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=groups
        ).exists():
            is_customer = True

        return is_customer

    def get_ProductList(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        SalesMasterID = instances.SalesMasterID
        sales_details = SalesDetails.objects.filter(
            CompanyID=CompanyID, SalesMasterID=SalesMasterID, BranchID=BranchID
        )

        product_ids = sales_details.values_list("ProductID", flat=True)
        produc_instances = Product.objects.filter(
            CompanyID=CompanyID, ProductID__in=product_ids
        )
        ProductList = []
        for p in produc_instances:
            ProductList.append(
                {
                    "ProductName": p.ProductName,
                    "ProductID": p.ProductID,
                }
            )

        return ProductList

    def get_BillDiscPercent(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscPercent = instances.BillDiscPercent

        BillDiscPercent = round(BillDiscPercent, PriceRounding)

        return converted_float(BillDiscPercent)

    def get_BillDiscAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscAmt = instances.BillDiscAmt

        BillDiscAmt = round(BillDiscAmt, PriceRounding)

        return converted_float(BillDiscAmt)

    def get_CardTypeName(self, instances):
        CompanyID = self.context.get("CompanyID")
        TransactionTypesID = instances.CardTypeID
        BranchID = instances.BranchID

        if TransactionTypes.objects.filter(
            CompanyID=CompanyID,
            TransactionTypesID=TransactionTypesID,
            BranchID=BranchID,
        ).exists():

            transactionType = TransactionTypes.objects.get(
                CompanyID=CompanyID,
                TransactionTypesID=TransactionTypesID,
                BranchID=BranchID,
            )
            Name = transactionType.Name

        else:
            Name = ""

        CardTypeName = Name

        return CardTypeName

    def get_DetailID(self, instances):

        return ""

    def get_WareHouseName(self, instances):
        CompanyID = self.context.get("CompanyID")

        WarehouseID = instances.WarehouseID
        BranchID = instances.BranchID
        WareHouseName = ""
        if Warehouse.objects.filter(
            CompanyID=CompanyID, WarehouseID=WarehouseID, BranchID=BranchID
        ).exists():
            WareHouseName = Warehouse.objects.get(
                CompanyID=CompanyID, WarehouseID=WarehouseID, BranchID=BranchID
            ).WarehouseName

        return WareHouseName

    def get_SalesAccountName(self, instances):
        CompanyID = self.context.get("CompanyID")
        SalesAccount = instances.SalesAccount
        BranchID = instances.BranchID
        SalesAccountName = ""
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=SalesAccount
        ).exists():
            SalesAccountName = AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=SalesAccount
            ).LedgerName

        return SalesAccountName

    def get_SalesDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        SalesMasterID = instances.SalesMasterID
        BranchID = instances.BranchID
        sales_details = SalesDetails.objects.filter(
            CompanyID=CompanyID,
            SalesMasterID=SalesMasterID,
            BranchID=BranchID,
            ReturnQty__gt=0,
        )
        serialized = SalesDetailsForReturnsSerializer(
            sales_details,
            many=True,
            context={"CompanyID": CompanyID, "PriceRounding": PriceRounding},
        )

        return serialized.data

    def get_TotalGrossAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalGrossAmt = instances.TotalGrossAmt

        TotalGrossAmt = round(TotalGrossAmt, PriceRounding)

        return converted_float(TotalGrossAmt)

    def get_AddlDiscPercent(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        AddlDiscPercent = instances.AddlDiscPercent

        AddlDiscPercent = round(AddlDiscPercent, PriceRounding)

        return converted_float(AddlDiscPercent)

    def get_AddlDiscAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        AddlDiscAmt = instances.AddlDiscAmt

        AddlDiscAmt = round(AddlDiscAmt, PriceRounding)

        return converted_float(AddlDiscAmt)

    def get_TotalDiscount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalDiscount = instances.TotalDiscount

        TotalDiscount = round(TotalDiscount, PriceRounding)

        return converted_float(TotalDiscount)

    def get_TotalTax(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalTax = instances.TotalTax

        TotalTax = round(TotalTax, PriceRounding)

        return converted_float(TotalTax)

    def get_NetTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        NetTotal = instances.NetTotal

        NetTotal = round(NetTotal, PriceRounding)

        return converted_float(NetTotal)

    def get_AdditionalCost(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        AdditionalCost = instances.AdditionalCost

        AdditionalCost = round(AdditionalCost, PriceRounding)

        return converted_float(AdditionalCost)

    def get_GrandTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        GrandTotal = instances.GrandTotal

        GrandTotal = round(GrandTotal, PriceRounding)

        return converted_float(GrandTotal)

    def get_RoundOff(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        RoundOff = instances.RoundOff

        RoundOff = round(RoundOff, PriceRounding)

        return converted_float(RoundOff)

    def get_CashReceived(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CashReceived = instances.CashReceived

        CashReceived = round(CashReceived, PriceRounding)

        return converted_float(CashReceived)

    def get_CashAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CashAmount = instances.CashAmount

        CashAmount = round(CashAmount, PriceRounding)

        return converted_float(CashAmount)

    def get_BankAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BankAmount = instances.BankAmount

        BankAmount = round(BankAmount, PriceRounding)

        return converted_float(BankAmount)


class SalesEstimateForOrderSerializer(serializers.ModelSerializer):

    SalesDetails = serializers.SerializerMethodField()
    TotalGrossAmt = serializers.SerializerMethodField()
    # AddlDiscPercent = serializers.SerializerMethodField()
    # AddlDiscAmt = serializers.SerializerMethodField()
    # TotalDiscount = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    NetTotal = serializers.SerializerMethodField()
    # AdditionalCost = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    RoundOff = serializers.SerializerMethodField()
    # CashReceived = serializers.SerializerMethodField()
    # CashAmount = serializers.SerializerMethodField()
    # BankAmount = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    # SalesAccountName = serializers.SerializerMethodField()
    # WareHouseName = serializers.SerializerMethodField()
    # CardTypeName = serializers.SerializerMethodField()
    DetailID = serializers.SerializerMethodField()
    BillDiscPercent = serializers.SerializerMethodField()
    BillDiscAmt = serializers.SerializerMethodField()
    ProductList = serializers.SerializerMethodField()
    is_customer = serializers.SerializerMethodField()

    class Meta:
        model = SalesEstimateMaster
        fields = (
            "id",
            "CompanyID",
            "SalesEstimateMasterID",
            "BranchID",
            "Action",
            "VoucherNo",
            "Date",
            "DeliveryDate",
            "LedgerID",
            "PriceCategoryID",
            "CustomerName",
            "Address1",
            "Address2",
            "Notes",
            "FinacialYearID",
            "TotalTax",
            "TotalGrossAmt",
            "NetTotal",
            "TaxID",
            "TaxType",
            "DetailID",
            "BillDiscPercent",
            "BillDiscAmt",
            "GrandTotal",
            "RoundOff",
            "IsActive",
            "CreatedDate",
            "UpdatedDate",
            "CreatedUserID",
            "SalesDetails",
            "LedgerName",
            "ProductList",
            "State_of_Supply",
            "Country_of_Supply",
            "GST_Treatment",
            "VAT_Treatment",
            "VATAmount",
            "SGSTAmount",
            "CGSTAmount",
            "IGSTAmount",
            "is_customer",
        )

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(CompanyID=CompanyID, LedgerID=LedgerID)

        LedgerName = ledger.LedgerName

        return LedgerName

    def get_is_customer(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        is_customer = False
        groups = [10, 29]
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=groups
        ).exists():
            is_customer = True
        return is_customer

    def get_ProductList(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        SalesEstimateMasterID = instances.SalesEstimateMasterID
        sales_details = SalesEstimateDetails.objects.filter(
            CompanyID=CompanyID,
            SalesEstimateMasterID=SalesEstimateMasterID,
            BranchID=BranchID,
        )

        product_ids = sales_details.values_list("ProductID", flat=True)
        produc_instances = Product.objects.filter(
            CompanyID=CompanyID, ProductID__in=product_ids
        )
        ProductList = []
        for p in produc_instances:
            ProductList.append(
                {
                    "ProductName": p.ProductName,
                    "ProductID": p.ProductID,
                }
            )

        return ProductList

    def get_BillDiscPercent(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscPercent = instances.BillDiscPercent

        BillDiscPercent = round(BillDiscPercent, PriceRounding)

        return converted_float(BillDiscPercent)

    def get_BillDiscAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscAmt = instances.BillDiscAmt

        BillDiscAmt = round(BillDiscAmt, PriceRounding)

        return converted_float(BillDiscAmt)

    def get_CardTypeName(self, instances):
        CompanyID = self.context.get("CompanyID")
        TransactionTypesID = instances.CardTypeID
        BranchID = instances.BranchID

        if TransactionTypes.objects.filter(
            CompanyID=CompanyID,
            TransactionTypesID=TransactionTypesID,
            BranchID=BranchID,
        ).exists():

            transactionType = TransactionTypes.objects.get(
                CompanyID=CompanyID,
                TransactionTypesID=TransactionTypesID,
                BranchID=BranchID,
            )
            Name = transactionType.Name

        else:
            Name = ""

        CardTypeName = Name

        return CardTypeName

    def get_DetailID(self, instances):

        return ""

    # def get_WareHouseName(self, instances):
    #     CompanyID = self.context.get("CompanyID")

    #     WarehouseID = instances.WarehouseID
    #     BranchID = instances.BranchID
    #     WareHouseName = ""
    #     if Warehouse.objects.filter(CompanyID=CompanyID, WarehouseID=WarehouseID, BranchID=BranchID).exists():
    #         WareHouseName = Warehouse.objects.get(
    #             CompanyID=CompanyID, WarehouseID=WarehouseID, BranchID=BranchID).WarehouseName

    #     return WareHouseName

    # def get_SalesAccountName(self, instances):
    #     CompanyID = self.context.get("CompanyID")
    #     SalesAccount = instances.SalesAccount
    #     BranchID = instances.BranchID
    #     SalesAccountName = ""
    #     if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=SalesAccount, BranchID=BranchID).exists():
    #         SalesAccountName = AccountLedger.objects.get(
    #             CompanyID=CompanyID, LedgerID=SalesAccount, BranchID=BranchID).LedgerName

    #     return SalesAccountName

    def get_SalesDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        SalesEstimateMasterID = instances.SalesEstimateMasterID
        BranchID = instances.BranchID
        sales_details = SalesEstimateDetails.objects.filter(
            CompanyID=CompanyID,
            SalesEstimateMasterID=SalesEstimateMasterID,
            BranchID=BranchID,
        )
        serialized = SalesEstimateDetailsForOrdersSerializer(
            sales_details,
            many=True,
            context={"CompanyID": CompanyID, "PriceRounding": PriceRounding},
        )

        return serialized.data

    def get_TotalGrossAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalGrossAmt = instances.TotalGrossAmt

        TotalGrossAmt = round(TotalGrossAmt, PriceRounding)

        return converted_float(TotalGrossAmt)

    # def get_AddlDiscPercent(self, instances):
    #     PriceRounding = self.context.get("PriceRounding")
    #     AddlDiscPercent = instances.AddlDiscPercent

    #     AddlDiscPercent = round(AddlDiscPercent, PriceRounding)

    #     return converted_float(AddlDiscPercent)

    # def get_AddlDiscAmt(self, instances):
    #     PriceRounding = self.context.get("PriceRounding")
    #     AddlDiscAmt = instances.AddlDiscAmt

    #     AddlDiscAmt = round(AddlDiscAmt, PriceRounding)

    #     return converted_float(AddlDiscAmt)

    # def get_TotalDiscount(self, instances):
    #     PriceRounding = self.context.get("PriceRounding")
    #     TotalDiscount = instances.TotalDiscount

    #     TotalDiscount = round(TotalDiscount, PriceRounding)

    #     return converted_float(TotalDiscount)

    def get_TotalTax(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalTax = instances.TotalTax

        TotalTax = round(TotalTax, PriceRounding)

        return converted_float(TotalTax)

    def get_NetTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        NetTotal = instances.NetTotal

        NetTotal = round(NetTotal, PriceRounding)

        return converted_float(NetTotal)

    # def get_AdditionalCost(self, instances):
    #     PriceRounding = self.context.get("PriceRounding")
    #     AdditionalCost = instances.AdditionalCost

    #     AdditionalCost = round(AdditionalCost, PriceRounding)

    #     return converted_float(AdditionalCost)

    def get_GrandTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        GrandTotal = instances.GrandTotal

        GrandTotal = round(GrandTotal, PriceRounding)

        return converted_float(GrandTotal)

    def get_RoundOff(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        RoundOff = instances.RoundOff

        RoundOff = round(RoundOff, PriceRounding)

        return converted_float(RoundOff)

    # def get_CashReceived(self, instances):
    #     PriceRounding = self.context.get("PriceRounding")
    #     CashReceived = instances.CashReceived

    #     CashReceived = round(CashReceived, PriceRounding)

    #     return converted_float(CashReceived)

    # def get_CashAmount(self, instances):
    #     PriceRounding = self.context.get("PriceRounding")
    #     CashAmount = instances.CashAmount

    #     CashAmount = round(CashAmount, PriceRounding)

    #     return converted_float(CashAmount)

    # def get_BankAmount(self, instances):
    #     PriceRounding = self.context.get("PriceRounding")
    #     BankAmount = instances.BankAmount

    #     BankAmount = round(BankAmount, PriceRounding)

    #     return converted_float(BankAmount)


class SalesEstimateDetailsForOrdersSerializer(serializers.ModelSerializer):

    Qty = serializers.SerializerMethodField()
    FreeQty = serializers.SerializerMethodField()
    UnitPrice = serializers.SerializerMethodField()
    InclusivePrice = serializers.SerializerMethodField()
    RateWithTax = serializers.SerializerMethodField()
    # CostPerPrice = serializers.SerializerMethodField()
    DiscountPerc = serializers.SerializerMethodField()
    DiscountAmount = serializers.SerializerMethodField()
    # AddlDiscPerc = serializers.SerializerMethodField()
    # AddlDiscAmt = serializers.SerializerMethodField()
    GrossAmount = serializers.SerializerMethodField()
    TaxableAmount = serializers.SerializerMethodField()
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
    detailID = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    TAX1Amount = serializers.SerializerMethodField()
    TAX1Perc = serializers.SerializerMethodField()
    TAX2Amount = serializers.SerializerMethodField()
    TAX2Perc = serializers.SerializerMethodField()
    TAX3Perc = serializers.SerializerMethodField()
    TAX3Amount = serializers.SerializerMethodField()
    DeliveryDetailsID = serializers.SerializerMethodField()
    # OrderDetailsID = serializers.SerializerMethodField()
    # ExistingQty = serializers.SerializerMethodField()
    UnitList = serializers.SerializerMethodField()
    BatchCode_list = serializers.SerializerMethodField()
    BatchCode = serializers.SerializerMethodField()
    SerialNos = serializers.SerializerMethodField()

    class Meta:
        model = SalesEstimateDetails
        fields = (
            "id",
            "BranchID",
            "Action",
            "SalesEstimateMasterID",
            "ProductID",
            "TAX1Perc",
            "TAX1Amount",
            "TAX1Perc",
            "TAX2Perc",
            "ProductName",
            "UnitList",
            "detailID",
            "SerialNos",
            "ProductTaxID",
            "Qty",
            "FreeQty",
            "UnitPrice",
            "InclusivePrice",
            "TAX3Perc",
            "DeliveryDetailsID",
            "TAX2Amount",
            "TotalTax",
            "TAX3Amount",
            "RateWithTax",
            "PriceListID",
            "DiscountPerc",
            "DiscountAmount",
            "BatchCode",
            "BatchCode_list",
            "unq_id",
            "GrossAmount",
            "TaxableAmount",
            "VATPerc",
            "VATAmount",
            "SGSTPerc",
            "SGSTAmount",
            "CGSTPerc",
            "UnitName",
            "CGSTAmount",
            "IGSTPerc",
            "IGSTAmount",
            "NetAmount",
            "CreatedUserID",
        )

    def get_SerialNos(self, sales_details):
        return []

    def get_ProductName(self, sales_details):

        CompanyID = self.context.get("CompanyID")

        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID

        product = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)

        ProductName = product.ProductName

        return ProductName

    def get_BatchCode(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        BatchCode = sales_details.BatchCode
        BranchID = sales_details.BranchID
        if not BatchCode:
            BatchCode = 0

        return str(BatchCode)

    def get_BatchCode_list(self, sales_details):
        BatchCode_list = []
        CompanyID = self.context.get("CompanyID")
        PriceRounding = int(self.context.get("PriceRounding"))
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        BatchCode_list = []
        if Batch.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
        ).exists():
            batch_details = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
            )
            BatchCode_list = Batch_ListSerializer(
                batch_details,
                many=True,
                context={"CompanyID": CompanyID, "PriceRounding": PriceRounding},
            )
            BatchCode_list = BatchCode_list.data
        return BatchCode_list

    def get_UnitList(self, purchase_details):

        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        ProductID = purchase_details.ProductID
        BranchID = purchase_details.BranchID

        UnitList = PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID)

        serialized = PriceListRestSerializer(
            UnitList,
            many=True,
            context={"CompanyID": CompanyID, "PriceRounding": PriceRounding},
        )

        return serialized.data

    # def get_ExistingQty(self, sales_details):
    #     ReturnQty = sales_details.ReturnQty
    #     ExistingQty = ReturnQty
    #     return ExistingQty

    def get_DeliveryDetailsID(self, instances):

        return 1

    # def get_OrderDetailsID(self, instances):

    #     return 1

    def get_TotalTax(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        TAX1Amount = purchase_details.TAX1Amount
        TAX2Amount = purchase_details.TAX2Amount
        TAX3Amount = purchase_details.TAX3Amount
        VATAmount = purchase_details.VATAmount
        IGSTAmount = purchase_details.IGSTAmount
        SGSTAmount = purchase_details.SGSTAmount
        CGSTAmount = purchase_details.CGSTAmount

        TotalTax = (
            TAX1Amount
            + TAX2Amount
            + TAX3Amount
            + VATAmount
            + IGSTAmount
            + SGSTAmount
            + CGSTAmount
        )

        return TotalTax

    def get_unq_id(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        unq_id = purchase_details.id

        return unq_id

    def get_detailID(self, purchase_details):

        detailID = 0

        return detailID

    def get_UnitName(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        PriceListID = purchase_details.PriceListID
        BranchID = purchase_details.BranchID

        if PriceList.objects.filter(
            CompanyID=CompanyID, PriceListID=PriceListID
        ).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListID
            ).UnitID
            UnitName = Unit.objects.get(CompanyID=CompanyID, UnitID=UnitID).UnitName
        else:
            UnitName = ""

        return UnitName

    def get_Qty(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        # Qty = sales_details.ReturnQty
        Qty = sales_details.Qty

        Qty = round(Qty, PriceRounding)

        return converted_float(Qty)

    def get_FreeQty(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        FreeQty = sales_details.FreeQty

        FreeQty = round(FreeQty, PriceRounding)

        return converted_float(FreeQty)

    def get_UnitPrice(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        UnitPrice = sales_details.UnitPrice

        UnitPrice = round(UnitPrice, PriceRounding)

        return converted_float(UnitPrice)

    def get_InclusivePrice(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        InclusivePrice = sales_details.InclusivePrice

        InclusivePrice = round(InclusivePrice, PriceRounding)

        return converted_float(InclusivePrice)

    def get_RateWithTax(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        RateWithTax = sales_details.RateWithTax

        RateWithTax = round(RateWithTax, PriceRounding)

        return converted_float(RateWithTax)

    # def get_CostPerPrice(self, sales_details):
    #     PriceRounding = self.context.get("PriceRounding")
    #     CostPerPrice = sales_details.CostPerPrice

    #     CostPerPrice = round(CostPerPrice, PriceRounding)

    #     return converted_float(CostPerPrice)

    def get_DiscountPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        DiscountPerc = sales_details.DiscountPerc

        DiscountPerc = round(DiscountPerc, PriceRounding)

        return converted_float(DiscountPerc)

    def get_DiscountAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        DiscountAmount = sales_details.DiscountAmount

        DiscountAmount = round(DiscountAmount, PriceRounding)

        return converted_float(DiscountAmount)

    def get_GrossAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        GrossAmount = sales_details.GrossAmount

        GrossAmount = round(GrossAmount, PriceRounding)

        return converted_float(GrossAmount)

    def get_TaxableAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TaxableAmount = sales_details.TaxableAmount

        TaxableAmount = round(TaxableAmount, PriceRounding)

        return converted_float(TaxableAmount)

    def get_VATPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        VATPerc = sales_details.VATPerc

        VATPerc = round(VATPerc, PriceRounding)

        return converted_float(VATPerc)

    def get_VATAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        VATAmount = sales_details.VATAmount

        VATAmount = round(VATAmount, PriceRounding)

        return converted_float(VATAmount)

    def get_SGSTPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        SGSTPerc = sales_details.SGSTPerc

        SGSTPerc = round(SGSTPerc, PriceRounding)

        return converted_float(SGSTPerc)

    def get_SGSTAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        SGSTAmount = sales_details.SGSTAmount

        SGSTAmount = round(SGSTAmount, PriceRounding)

        return converted_float(SGSTAmount)

    def get_CGSTPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        CGSTPerc = sales_details.CGSTPerc

        CGSTPerc = round(CGSTPerc, PriceRounding)

        return converted_float(CGSTPerc)

    def get_CGSTAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        CGSTAmount = sales_details.CGSTAmount

        CGSTAmount = round(CGSTAmount, PriceRounding)

        return converted_float(CGSTAmount)

    def get_IGSTPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        IGSTPerc = sales_details.IGSTPerc

        IGSTPerc = round(IGSTPerc, PriceRounding)

        return converted_float(IGSTPerc)

    def get_IGSTAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        IGSTAmount = sales_details.IGSTAmount

        IGSTAmount = round(IGSTAmount, PriceRounding)

        return converted_float(IGSTAmount)

    def get_NetAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        NetAmount = sales_details.NetAmount

        NetAmount = round(NetAmount, PriceRounding)

        return converted_float(NetAmount)

    # def get_AddlDiscPerc(self, sales_details):
    #     PriceRounding = self.context.get("PriceRounding")
    #     AddlDiscPerc = sales_details.AddlDiscPerc

    #     if AddlDiscPerc:
    #         AddlDiscPerc = round(AddlDiscPerc, PriceRounding)
    #     else:
    #         AddlDiscPerc = 0

    #     return converted_float(AddlDiscPerc)

    # def get_AddlDiscAmt(self, sales_details):
    #     PriceRounding = self.context.get("PriceRounding")
    #     AddlDiscAmt = sales_details.AddlDiscAmt

    #     if AddlDiscAmt:
    #         AddlDiscAmt = round(AddlDiscAmt, PriceRounding)
    #     else:
    #         AddlDiscAmt = 0

    #     return converted_float(AddlDiscAmt)

    def get_TAX1Perc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX1Perc = sales_details.TAX1Perc

        if TAX1Perc:
            TAX1Perc = round(TAX1Perc, PriceRounding)
        else:
            TAX1Perc = 0

        return converted_float(TAX1Perc)

    def get_TAX2Perc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX2Perc = sales_details.TAX2Perc

        if TAX2Perc:
            TAX2Perc = round(TAX2Perc, PriceRounding)
        else:
            TAX2Perc = 0

        return converted_float(TAX2Perc)

    def get_TAX3Perc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX3Perc = sales_details.TAX3Perc

        if TAX3Perc:
            TAX3Perc = round(TAX3Perc, PriceRounding)
        else:
            TAX3Perc = 0

        return converted_float(TAX3Perc)

    def get_TAX1Amount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX1Amount = sales_details.TAX1Amount

        if TAX1Amount:
            TAX1Amount = round(TAX1Amount, PriceRounding)
        else:
            TAX1Amount = 0

        return converted_float(TAX1Amount)

    def get_TAX2Amount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX2Amount = sales_details.TAX2Amount

        if TAX2Amount:
            TAX2Amount = round(TAX2Amount, PriceRounding)
        else:
            TAX2Amount = 0

        return converted_float(TAX2Amount)

    def get_TAX3Amount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX3Amount = sales_details.TAX3Amount

        if TAX3Amount:
            TAX3Amount = round(TAX3Amount, PriceRounding)
        else:
            TAX3Amount = 0

        return converted_float(TAX3Amount)


class SalesDetailsForReturnsSerializer(serializers.ModelSerializer):
    Qty = serializers.SerializerMethodField()
    FreeQty = serializers.SerializerMethodField()
    UnitPrice = serializers.SerializerMethodField()
    InclusivePrice = serializers.SerializerMethodField()
    RateWithTax = serializers.SerializerMethodField()
    CostPerPrice = serializers.SerializerMethodField()
    DiscountPerc = serializers.SerializerMethodField()
    DiscountAmount = serializers.SerializerMethodField()
    AddlDiscPerc = serializers.SerializerMethodField()
    AddlDiscAmt = serializers.SerializerMethodField()
    GrossAmount = serializers.SerializerMethodField()
    TaxableAmount = serializers.SerializerMethodField()
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
    detailID = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    TAX1Amount = serializers.SerializerMethodField()
    TAX1Perc = serializers.SerializerMethodField()
    TAX2Amount = serializers.SerializerMethodField()
    TAX2Perc = serializers.SerializerMethodField()
    TAX3Perc = serializers.SerializerMethodField()
    TAX3Amount = serializers.SerializerMethodField()
    DeliveryDetailsID = serializers.SerializerMethodField()
    OrderDetailsID = serializers.SerializerMethodField()
    ExistingQty = serializers.SerializerMethodField()
    UnitList = serializers.SerializerMethodField()
    BatchList = serializers.SerializerMethodField()
    BatchCode_list = serializers.SerializerMethodField()
    BatchCode = serializers.SerializerMethodField()
    ActualUnitPrice = serializers.SerializerMethodField()
    HSNCode = serializers.SerializerMethodField()
    SerialNos = serializers.SerializerMethodField()
    ProductCode = serializers.SerializerMethodField()
    is_inclusive = serializers.SerializerMethodField()
    is_kfc = serializers.SerializerMethodField()

    class Meta:
        model = SalesDetails
        fields = (
            "id",
            "unq_id",
            "SalesDetailsID",
            "BranchID",
            "Action",
            "SalesMasterID",
            "ProductID",
            "ProductName",
            "ProductTaxID",
            "Qty",
            "FreeQty",
            "UnitPrice",
            "InclusivePrice",
            "ReturnQty",
            "BatchList",
            "ActualUnitPrice",
            "HSNCode",
            "RateWithTax",
            "CostPerPrice",
            "PriceListID",
            "UnitName",
            "DiscountPerc",
            "DiscountAmount",
            "AddlDiscPerc",
            "AddlDiscAmt",
            "GrossAmount",
            "TaxableAmount",
            "VATPerc",
            "VATAmount",
            "SGSTPerc",
            "SGSTAmount",
            "CGSTPerc",
            "SerialNos",
            "ProductCode",
            "is_kfc",
            "CGSTAmount",
            "IGSTPerc",
            "IGSTAmount",
            "NetAmount",
            "CreatedDate",
            "CreatedUserID",
            "Flavour",
            "BatchCode",
            "is_inclusive",
            "TAX1Perc",
            "TAX1Amount",
            "TAX2Perc",
            "TAX2Amount",
            "TAX3Perc",
            "TAX3Amount",
            "TotalTax",
            "DeliveryDetailsID",
            "OrderDetailsID",
            "detailID",
            "ExistingQty",
            "UnitList",
            "BatchCode_list",
        )

    def get_ProductName(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID
        product = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)
        ProductName = product.ProductName
        return ProductName

    def get_is_inclusive(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        is_inclusive = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID
        ).is_inclusive

        return is_inclusive

    def get_is_kfc(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        KFCAmount = sales_details.KFCAmount
        is_kfc = False
        if converted_float(KFCAmount) > 0:
            is_kfc = True
        return is_kfc

    def get_SerialNos(self, sales_details):
        SerialNos = []
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        SalesMasterID = sales_details.SalesMasterID
        SalesDetailsID = sales_details.SalesDetailsID
        if SerialNumbers.objects.filter(
            CompanyID=CompanyID,
            BranchID=BranchID,
            SalesMasterID=SalesMasterID,
            SalesDetailsID=SalesDetailsID,
            VoucherType="SI",
        ).exists():
            Serial_details = SerialNumbers.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                SalesMasterID=SalesMasterID,
                SalesDetailsID=SalesDetailsID,
                VoucherType="SI",
            )
            SerialNos = SerialNumberSerializer(
                Serial_details, many=True, context={"CompanyID": CompanyID}
            )
            SerialNos = SerialNos.data
        return SerialNos

    def get_ProductCode(self, sales_details):

        CompanyID = self.context.get("CompanyID")
        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID
        product = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)

        ProductCode = product.ProductCode
        return ProductCode

    def get_HSNCode(self, sales_details):

        CompanyID = self.context.get("CompanyID")

        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID

        product = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)

        HSNCode = product.HSNCode

        return HSNCode

    def get_BatchCode(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        BatchCode = sales_details.BatchCode
        BranchID = sales_details.BranchID
        if not BatchCode:
            BatchCode = 0

        return str(BatchCode)

    def get_BatchList(self, sales_details):
        BatchCode_list = []
        CompanyID = self.context.get("CompanyID")
        PriceRounding = int(self.context.get("PriceRounding"))
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        BatchCode_list = []
        if Batch.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
        ).exists():
            batch_details = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
            )
            BatchCode_list = Batch_ListSerializer(
                batch_details,
                many=True,
                context={"CompanyID": CompanyID, "PriceRounding": PriceRounding},
            )
            BatchCode_list = BatchCode_list.data
        return BatchCode_list

    def get_BatchCode_list(self, sales_details):
        BatchCode_list = []
        CompanyID = self.context.get("CompanyID")
        PriceRounding = int(self.context.get("PriceRounding"))
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        BatchCode_list = []
        if Batch.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
        ).exists():
            batch_details = Batch.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID
            )
            BatchCode_list = Batch_ListSerializer(
                batch_details,
                many=True,
                context={"CompanyID": CompanyID, "PriceRounding": PriceRounding},
            )
            BatchCode_list = BatchCode_list.data
        return BatchCode_list

    def get_UnitList(self, purchase_details):

        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        ProductID = purchase_details.ProductID
        BranchID = purchase_details.BranchID

        UnitList = PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID)

        serialized = PriceListRestSerializer(
            UnitList,
            many=True,
            context={"CompanyID": CompanyID, "PriceRounding": PriceRounding},
        )

        return serialized.data

    def get_ExistingQty(self, sales_details):
        ReturnQty = sales_details.ReturnQty
        ExistingQty = ReturnQty
        return ExistingQty

    def get_DeliveryDetailsID(self, instances):

        return 1

    def get_OrderDetailsID(self, instances):

        return 1

    def get_TotalTax(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        TAX1Amount = purchase_details.TAX1Amount
        TAX2Amount = purchase_details.TAX2Amount
        TAX3Amount = purchase_details.TAX3Amount
        VATAmount = purchase_details.VATAmount
        IGSTAmount = purchase_details.IGSTAmount
        SGSTAmount = purchase_details.SGSTAmount
        CGSTAmount = purchase_details.CGSTAmount

        TotalTax = (
            TAX1Amount
            + TAX2Amount
            + TAX3Amount
            + VATAmount
            + CGSTAmount
            + SGSTAmount
            + IGSTAmount
        )

        return TotalTax

    def get_unq_id(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        unq_id = purchase_details.id

        return unq_id

    def get_detailID(self, purchase_details):

        detailID = 0

        return detailID

    def get_UnitName(self, purchase_details):

        CompanyID = self.context.get("CompanyID")

        PriceListID = purchase_details.PriceListID
        BranchID = purchase_details.BranchID

        if PriceList.objects.filter(
            CompanyID=CompanyID, PriceListID=PriceListID
        ).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListID
            ).UnitID
            UnitName = Unit.objects.get(CompanyID=CompanyID, UnitID=UnitID).UnitName
        else:
            UnitName = ""

        return UnitName

    def get_Qty(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        Qty = sales_details.ReturnQty

        Qty = round(Qty, PriceRounding)

        return converted_float(Qty)

    def get_FreeQty(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        FreeQty = sales_details.FreeQty

        FreeQty = round(FreeQty, PriceRounding)

        return converted_float(FreeQty)

    def get_UnitPrice(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        UnitPrice = sales_details.UnitPrice

        UnitPrice = round(UnitPrice, PriceRounding)

        return converted_float(UnitPrice)

    def get_ActualUnitPrice(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        ActualUnitPrice = sales_details.UnitPrice

        ActualUnitPrice = round(ActualUnitPrice, PriceRounding)

        return converted_float(ActualUnitPrice)

    def get_InclusivePrice(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        InclusivePrice = sales_details.InclusivePrice

        InclusivePrice = round(InclusivePrice, PriceRounding)

        return converted_float(InclusivePrice)

    def get_RateWithTax(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        RateWithTax = sales_details.RateWithTax

        RateWithTax = round(RateWithTax, PriceRounding)

        return converted_float(RateWithTax)

    def get_CostPerPrice(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        CostPerPrice = sales_details.CostPerPrice

        CostPerPrice = round(CostPerPrice, PriceRounding)

        return converted_float(CostPerPrice)

    def get_DiscountPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        DiscountPerc = sales_details.DiscountPerc

        DiscountPerc = round(DiscountPerc, PriceRounding)

        return converted_float(DiscountPerc)

    def get_DiscountAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        DiscountAmount = sales_details.DiscountAmount

        DiscountAmount = round(DiscountAmount, PriceRounding)

        return converted_float(DiscountAmount)

    def get_GrossAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        GrossAmount = sales_details.GrossAmount

        GrossAmount = round(GrossAmount, PriceRounding)

        return converted_float(GrossAmount)

    def get_TaxableAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TaxableAmount = sales_details.TaxableAmount

        TaxableAmount = round(TaxableAmount, PriceRounding)

        return converted_float(TaxableAmount)

    def get_VATPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        VATPerc = sales_details.VATPerc

        VATPerc = round(VATPerc, PriceRounding)

        return converted_float(VATPerc)

    def get_VATAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        VATAmount = sales_details.VATAmount

        VATAmount = round(VATAmount, PriceRounding)

        return converted_float(VATAmount)

    def get_SGSTPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        SGSTPerc = sales_details.SGSTPerc

        SGSTPerc = round(SGSTPerc, PriceRounding)

        return converted_float(SGSTPerc)

    def get_SGSTAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        SGSTAmount = sales_details.SGSTAmount

        SGSTAmount = round(SGSTAmount, PriceRounding)

        return converted_float(SGSTAmount)

    def get_CGSTPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        CGSTPerc = sales_details.CGSTPerc

        CGSTPerc = round(CGSTPerc, PriceRounding)

        return converted_float(CGSTPerc)

    def get_CGSTAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        CGSTAmount = sales_details.CGSTAmount

        CGSTAmount = round(CGSTAmount, PriceRounding)

        return converted_float(CGSTAmount)

    def get_IGSTPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        IGSTPerc = sales_details.IGSTPerc

        IGSTPerc = round(IGSTPerc, PriceRounding)

        return converted_float(IGSTPerc)

    def get_IGSTAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        IGSTAmount = sales_details.IGSTAmount

        IGSTAmount = round(IGSTAmount, PriceRounding)

        return converted_float(IGSTAmount)

    def get_NetAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        NetAmount = sales_details.NetAmount

        NetAmount = round(NetAmount, PriceRounding)

        return converted_float(NetAmount)

    def get_AddlDiscPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        AddlDiscPerc = sales_details.AddlDiscPerc

        if AddlDiscPerc:
            AddlDiscPerc = round(AddlDiscPerc, PriceRounding)
        else:
            AddlDiscPerc = 0

        return converted_float(AddlDiscPerc)

    def get_AddlDiscAmt(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        AddlDiscAmt = sales_details.AddlDiscAmt

        if AddlDiscAmt:
            AddlDiscAmt = round(AddlDiscAmt, PriceRounding)
        else:
            AddlDiscAmt = 0

        return converted_float(AddlDiscAmt)

    def get_TAX1Perc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX1Perc = sales_details.TAX1Perc

        if TAX1Perc:
            TAX1Perc = round(TAX1Perc, PriceRounding)
        else:
            TAX1Perc = 0

        return converted_float(TAX1Perc)

    def get_TAX2Perc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX2Perc = sales_details.TAX2Perc

        if TAX2Perc:
            TAX2Perc = round(TAX2Perc, PriceRounding)
        else:
            TAX2Perc = 0

        return converted_float(TAX2Perc)

    def get_TAX3Perc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX3Perc = sales_details.TAX3Perc

        if TAX3Perc:
            TAX3Perc = round(TAX3Perc, PriceRounding)
        else:
            TAX3Perc = 0

        return converted_float(TAX3Perc)

    def get_TAX1Amount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX1Amount = sales_details.TAX1Amount

        if TAX1Amount:
            TAX1Amount = round(TAX1Amount, PriceRounding)
        else:
            TAX1Amount = 0

        return converted_float(TAX1Amount)

    def get_TAX2Amount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX2Amount = sales_details.TAX2Amount

        if TAX2Amount:
            TAX2Amount = round(TAX2Amount, PriceRounding)
        else:
            TAX2Amount = 0

        return converted_float(TAX2Amount)

    def get_TAX3Amount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX3Amount = sales_details.TAX3Amount

        if TAX3Amount:
            TAX3Amount = round(TAX3Amount, PriceRounding)
        else:
            TAX3Amount = 0

        return converted_float(TAX3Amount)


class StockSerializer(serializers.ModelSerializer):

    AutoBarcode = serializers.SerializerMethodField()
    PurchasePrice = serializers.SerializerMethodField()
    SalesPrice = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()
    BaseUnitName = serializers.SerializerMethodField()
    is_BasicUnit = serializers.SerializerMethodField()
    MultiFactor = serializers.SerializerMethodField()
    WareHouseName = serializers.SerializerMethodField()
    Qty = serializers.SerializerMethodField()
    Cost = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "AutoBarcode",
            "ProductCode",
            "ProductID",
            "ProductName",
            "WareHouseName",
            "PurchasePrice",
            "SalesPrice",
            "UnitName",
            "BaseUnitName",
            "is_BasicUnit",
            "MultiFactor",
            "Qty",
            "Cost",
        )

    def get_Cost(self, instance):

        CompanyID = self.context.get("CompanyID")
        # WareHouseID = self.context.get("WareHouseID")
        ToDate = self.context.get("ToDate")

        ProductID = instance.ProductID
        BranchID = instance.BranchID

        Cost = 0
        VoucherTypes = ["PI", "OS", "ES"]
        if StockPosting.objects.filter(
            ProductID=ProductID,
            CompanyID=CompanyID,
            QtyIn__gt=0,
            Date__lte=ToDate,
            VoucherType__in=VoucherTypes,
        ).exists():
            stock_ins = StockPosting.objects.filter(
                ProductID=ProductID,
                CompanyID=CompanyID,
                QtyIn__gt=0,
                Date__lte=ToDate,
                VoucherType__in=VoucherTypes,
            )
            TotalQtyInRate = 0
            TotalQtyIn = 0
            TotalQtyInRate = stock_ins.aggregate(total_sum=Sum(F("QtyIn") * F("Rate")))
            TotalQtyIn = stock_ins.aggregate(Sum("QtyIn"))
            TotalQtyInRate = converted_float(TotalQtyInRate["total_sum"])
            TotalQtyIn = TotalQtyIn["QtyIn__sum"]

            Cost = converted_float(TotalQtyInRate) / converted_float(TotalQtyIn)

        return Cost

    def get_Qty(self, instance):

        CompanyID = self.context.get("CompanyID")
        ToDate = self.context.get("ToDate")
        WareHouseID = self.context.get("WareHouseID")
        if not WareHouseID:
            WareHouseID = 0

        ProductID = instance.ProductID
        BranchID = instance.BranchID

        Qty = 0
        if WareHouseID > 0:
            if StockPosting.objects.filter(
                ProductID=ProductID,
                CompanyID=CompanyID,
                WareHouseID=WareHouseID,
                Date__lte=ToDate,
            ).exists():
                stock_ins = StockPosting.objects.filter(
                    ProductID=ProductID,
                    CompanyID=CompanyID,
                    WareHouseID=WareHouseID,
                    Date__lte=ToDate,
                )
                TotalQtyIn = 0
                TotalQtyOut = 0
                for s in stock_ins:
                    TotalQtyIn += s.QtyIn
                    TotalQtyOut += s.QtyOut
                    if ProductID == 524:
                        print(WareHouseID, s.IsActive, "THHHHHAMARASHERYYYYYYYYYYY")

                Qty = converted_float(TotalQtyIn) - converted_float(TotalQtyOut)
        else:
            if StockPosting.objects.filter(
                ProductID=ProductID, CompanyID=CompanyID, Date__lte=ToDate
            ).exists():
                stock_ins = StockPosting.objects.filter(
                    ProductID=ProductID, CompanyID=CompanyID, Date__lte=ToDate
                )
                TotalQtyIn = 0
                TotalQtyOut = 0
                for s in stock_ins:
                    TotalQtyIn += s.QtyIn
                    TotalQtyOut += s.QtyOut

                Qty = converted_float(TotalQtyIn) - converted_float(TotalQtyOut)

        return Qty

    def get_WareHouseName(self, instance):

        CompanyID = self.context.get("CompanyID")
        WareHouseID = self.context.get("WareHouseID")

        BranchID = instance.BranchID
        WareHouseName = ""
        if Warehouse.objects.filter(
            CompanyID=CompanyID, WarehouseID=WareHouseID
        ).exists():
            WareHouseName = Warehouse.objects.get(
                CompanyID=CompanyID, WarehouseID=WareHouseID
            ).WarehouseName

        return WareHouseName

    def get_AutoBarcode(self, final_instance):

        CompanyID = self.context.get("CompanyID")
        ProductID = final_instance.ProductID
        BranchID = final_instance.BranchID
        AutoBarcode = PriceList.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True
        ).AutoBarcode

        return AutoBarcode

    def get_PurchasePrice(self, final_instance):

        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = final_instance.ProductID
        BranchID = final_instance.BranchID
        PurchasePrice = PriceList.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True
        ).PurchasePrice

        return converted_float(round(PurchasePrice, PriceRounding))

    def get_SalesPrice(self, final_instance):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = final_instance.ProductID
        BranchID = final_instance.BranchID
        SalesPrice = PriceList.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True
        ).SalesPrice

        return converted_float(round(SalesPrice, PriceRounding))

    def get_UnitName(self, final_instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = final_instance.ProductID
        BranchID = final_instance.BranchID
        UnitName = ""
        if PriceList.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, UnitInReports=True
        ).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, UnitInReports=True
            ).UnitID
            UnitName = Unit.objects.get(CompanyID=CompanyID, UnitID=UnitID).UnitName
        else:
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True
            ).UnitID
            UnitName = Unit.objects.get(CompanyID=CompanyID, UnitID=UnitID).UnitName

        return UnitName

    def get_BaseUnitName(self, final_instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = final_instance.ProductID
        BranchID = final_instance.BranchID
        BaseUnitName = ""
        if PriceList.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True
        ).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True
            ).UnitID
            BaseUnitName = Unit.objects.get(CompanyID=CompanyID, UnitID=UnitID).UnitName

        return BaseUnitName

    def get_is_BasicUnit(self, final_instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = final_instance.ProductID
        BranchID = final_instance.BranchID

        is_BasicUnit = False
        if PriceList.objects.filter(
            CompanyID=CompanyID,
            ProductID=ProductID,
            UnitInReports=True,
            DefaultUnit=True,
        ).exists():

            is_BasicUnit = True

        return is_BasicUnit

    def get_MultiFactor(self, final_instance):
        CompanyID = self.context.get("CompanyID")
        ProductID = final_instance.ProductID
        BranchID = final_instance.BranchID
        MultiFactor = 1
        if PriceList.objects.filter(
            CompanyID=CompanyID,
            ProductID=ProductID,
            UnitInReports=True,
            DefaultUnit=False,
        ).exists():
            MultiFactor = PriceList.objects.get(
                CompanyID=CompanyID,
                ProductID=ProductID,
                UnitInReports=True,
                DefaultUnit=False,
            ).MultiFactor
        return converted_float(MultiFactor)


class StockRateSerializer(serializers.ModelSerializer):

    ProductName = serializers.SerializerMethodField()
    WareHouseName = serializers.SerializerMethodField()
    TotalCost = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()

    class Meta:
        model = StockRate
        fields = (
            "id",
            "WareHouseID",
            "WareHouseName",
            "ProductName",
            "UnitName",
            "Date",
            "PurchasePrice",
            "SalesPrice",
            "Qty",
            "Cost",
            "TotalCost",
        )

    def get_ProductName(self, instance):

        CompanyID = self.context.get("CompanyID")
        ProductID = instance.ProductID
        BranchID = instance.BranchID
        ProductName = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID
        ).ProductName

        return ProductName

    def get_UnitName(self, instance):

        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        PriceListID = instance.PriceListID
        UnitID = PriceList.objects.get(
            CompanyID=CompanyID, PriceListID=PriceListID, DefaultUnit=True
        ).UnitID
        UnitName = Unit.objects.get(CompanyID=CompanyID, UnitID=UnitID).UnitName

        return UnitName

    def get_WareHouseName(self, instance):

        CompanyID = self.context.get("CompanyID")
        WareHouseID = instance.WareHouseID
        BranchID = instance.BranchID
        WareHouseName = Warehouse.objects.get(
            CompanyID=CompanyID, WarehouseID=WareHouseID
        ).WarehouseName

        return WareHouseName

    def get_TotalCost(self, instance):

        CompanyID = self.context.get("CompanyID")
        Qty = instance.Qty
        Cost = instance.Cost
        TotalCost = converted_float(Qty) * converted_float(Cost)

        return TotalCost


class SalesPrintSerializer(serializers.ModelSerializer):

    Details = serializers.SerializerMethodField()
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
    AccountName = serializers.SerializerMethodField()
    MasterID = serializers.SerializerMethodField()
    Types = serializers.SerializerMethodField()
    BillDiscAmt = serializers.SerializerMethodField()
    BillDiscPercent = serializers.SerializerMethodField()
    VATAmount = serializers.SerializerMethodField()
    SGSTAmount = serializers.SerializerMethodField()
    CGSTAmount = serializers.SerializerMethodField()
    IGSTAmount = serializers.SerializerMethodField()
    TAX1Amount = serializers.SerializerMethodField()
    TAX2Amount = serializers.SerializerMethodField()
    TAX3Amount = serializers.SerializerMethodField()
    Balance = serializers.SerializerMethodField()
    OldLedgerBalance = serializers.SerializerMethodField()
    PartyName = serializers.SerializerMethodField()
    DisplayName = serializers.SerializerMethodField()
    FirstName = serializers.SerializerMethodField()
    LastName = serializers.SerializerMethodField()
    Address1 = serializers.SerializerMethodField()
    Address2 = serializers.SerializerMethodField()
    City = serializers.SerializerMethodField()
    LedgerBalance = serializers.SerializerMethodField()
    TaxNo = serializers.SerializerMethodField()
    PhoneNo = serializers.SerializerMethodField()
    CustomerCRNo = serializers.SerializerMethodField()
    TotalQty = serializers.SerializerMethodField()
    qr_image = serializers.SerializerMethodField()
    is_b2b = serializers.SerializerMethodField()
    Currency = serializers.SerializerMethodField()

    class Meta:
        model = SalesMaster
        fields = (
            "MasterID",
            "BranchID",
            "Action",
            "VoucherNo",
            "Date",
            "TotalQty",
            "CreditPeriod",
            "LedgerID",
            "LedgerName",
            "OldLedgerBalance",
            "PhoneNo",
            "CustomerCRNo",
            "PriceCategoryID",
            "EmployeeID",
            "SalesAccount",
            "AccountName",
            "CustomerName",
            "Address1",
            "Address2",
            "Address3",
            "Notes",
            "FinacialYearID",
            "TotalGrossAmt",
            "AddlDiscPercent",
            "AddlDiscAmt",
            "TotalDiscount",
            "TotalTax",
            "NetTotal",
            "AdditionalCost",
            "GrandTotal",
            "RoundOff",
            "CashReceived",
            "CashAmount",
            "BankAmount",
            "WarehouseID",
            "TableID",
            "SeatNumber",
            "NoOfGuests",
            "INOUT",
            "TokenNumber",
            "CardTypeID",
            "CardNumber",
            "IsActive",
            "IsPosted",
            "Types",
            "CreatedDate",
            "UpdatedDate",
            "CreatedUserID",
            "TaxID",
            "TaxType",
            "BillDiscPercent",
            "BillDiscAmt",
            "VATAmount",
            "SGSTAmount",
            "CGSTAmount",
            "IGSTAmount",
            "TaxNo",
            "TAX1Amount",
            "TAX2Amount",
            "TAX3Amount",
            "Balance",
            "TransactionTypeID",
            "Details",
            "PartyName",
            "DisplayName",
            "FirstName",
            "LastName",
            "Address1",
            "Address2",
            "City",
            "LedgerBalance",
            "qr_image",
            "is_b2b",
            "Currency"
        )
        
    # def get_qr_image(self, instances):
    #     CompanyID = self.context.get("CompanyID")
    #     request = self.context.get("request")
    #     LedgerID = instances.LedgerID
    #     BranchID = instances.BranchID
    #     pk = str(instances.id)
    #     qr_code = None
    #     if QrCode.objects.filter(voucher_type="SI", master_id=pk).exists():
    #         qr_code = QrCode.objects.get(voucher_type="SI", master_id=pk)
    #     serialized = QRCodeSerializer(
    #         qr_code, context={"CompanyID": CompanyID, "request": request}
    #     )

    #     return serialized.data.get("qr_code")
    
    def get_Currency(self, instance):
        CompanyID = self.context.get("CompanyID")
        Currency = ""
        if CompanyID.Country:
            Currency = CompanyID.Country.Symbol
        return Currency
    
    def get_is_b2b(self, instance):
        is_b2b = False
        CompanyID = self.context.get("CompanyID")
        LedgerID = instance.LedgerID
        if Parties.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():
            party_instance = Parties.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).first()
            if party_instance.VATNumber or party_instance.GSTNumber:
                is_b2b = True
        return is_b2b
    
    def get_qr_image(self, instance):
        CompanyID = self.context.get("CompanyID")
        request = self.context.get("request")
        generateQrCode(instance, "SI")
        pk = str(instance.id)
        if QrCode.objects.filter(voucher_type="SI", master_id=pk).exists():
            qr_code = QrCode.objects.get(voucher_type="SI", master_id=pk)
        serialized = QRCodeSerializer(
            qr_code, context={"CompanyID": CompanyID, "request": request}
        )
        return serialized.data.get("qr_code")
    

    def get_TaxNo(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        TaxNo = ""
        if Parties.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():
            party_instance = Parties.objects.filter(
                CompanyID=CompanyID, LedgerID=LedgerID
            ).first()
            if party_instance.VATNumber:
                TaxNo = party_instance.VATNumber
            elif party_instance.GSTNumber:
                TaxNo = party_instance.GSTNumber
        return TaxNo

    def get_LedgerBalance(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        ledger_instances = LedgerPosting.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        )
        Balance = 0
        TotalDebit = 0
        TotalCredit = 0

        for i in ledger_instances:
            TotalDebit += i.Debit
            TotalCredit += i.Credit

        LedgerBalance = converted_float(TotalDebit) - converted_float(TotalCredit)

        return LedgerBalance

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(CompanyID=CompanyID, LedgerID=LedgerID)

        LedgerName = ledger.LedgerName

        return LedgerName

    def get_PartyName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        PartyName = ""
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=[10, 29]
        ).exists():
            PartyName = Parties.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID
            ).PartyName
        return PartyName

    def get_DisplayName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        DisplayName = ""
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=[10, 29]
        ).exists():
            DisplayName = Parties.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID
            ).DisplayName
        return DisplayName

    def get_FirstName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        FirstName = ""
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=[10, 29]
        ).exists():
            FirstName = Parties.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID
            ).FirstName
        return FirstName

    def get_LastName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        LastName = ""
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=[10, 29]
        ).exists():
            LastName = Parties.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID
            ).LastName
        return LastName

    def get_Address1(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        Address1 = ""
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=[10, 29]
        ).exists():
            if Parties.objects.get(CompanyID=CompanyID, LedgerID=LedgerID).Address1:
                Address1 = Parties.objects.get(
                    CompanyID=CompanyID, LedgerID=LedgerID
                ).Address1
        return Address1

    def get_Address2(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        Address2 = ""
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=[10, 29]
        ).exists():
            if Parties.objects.get(CompanyID=CompanyID, LedgerID=LedgerID).Address2:
                Address2 = Parties.objects.get(
                    CompanyID=CompanyID, LedgerID=LedgerID
                ).Address2
        return Address2

    def get_PhoneNo(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        Mobile = ""
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=[10, 29]
        ).exists():
            if Parties.objects.get(CompanyID=CompanyID, LedgerID=LedgerID).Mobile:
                Mobile = Parties.objects.get(
                    CompanyID=CompanyID, LedgerID=LedgerID
                ).Mobile
        return Mobile

    def get_CustomerCRNo(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        CRNo = ""
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=[10, 29]
        ).exists():
            if Parties.objects.get(CompanyID=CompanyID, LedgerID=LedgerID).CRNo:
                CRNo = Parties.objects.get(CompanyID=CompanyID, LedgerID=LedgerID).CRNo
        return CRNo

    def get_TotalQty(self, instances):
        CompanyID = self.context.get("CompanyID")
        TotalQty = 0
        SalesMasterID = instances.SalesMasterID
        BranchID = instances.BranchID
        sales_details = SalesDetails.objects.filter(
            CompanyID=CompanyID, SalesMasterID=SalesMasterID, BranchID=BranchID
        )
        TotalQty = sales_details.aggregate(Sum("Qty"))
        TotalQty = TotalQty["Qty__sum"]

        return converted_float(TotalQty)

    def get_City(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        City = ""
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=[10, 29]
        ).exists():
            if Parties.objects.get(CompanyID=CompanyID, LedgerID=LedgerID).City:
                City = Parties.objects.get(CompanyID=CompanyID, LedgerID=LedgerID).City
        return City

    def get_OldLedgerBalance(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        OldLedgerBalance = instances.OldLedgerBalance

        OldLedgerBalance = round(OldLedgerBalance, PriceRounding)

        return converted_float(OldLedgerBalance)

    def get_AccountName(self, instances):
        CompanyID = self.context.get("CompanyID")
        SalesAccount = instances.SalesAccount
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(CompanyID=CompanyID, LedgerID=SalesAccount)

        AccountName = ledger.LedgerName

        return AccountName

    def get_MasterID(self, instances):

        MasterID = instances.SalesMasterID

        return MasterID

    def get_Types(self, instances):

        Types = instances.SalesType

        return Types

    def get_Details(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        SalesMasterID = instances.SalesMasterID
        BranchID = instances.BranchID
        sales_details = SalesDetails.objects.filter(
            CompanyID=CompanyID, SalesMasterID=SalesMasterID, BranchID=BranchID
        )
        serialized = SalesDetailsPrintSerializer(
            sales_details,
            many=True,
            context={"CompanyID": CompanyID, "PriceRounding": PriceRounding},
        )

        return serialized.data

    def get_BillDiscAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscAmt = instances.BillDiscAmt

        BillDiscAmt = round(BillDiscAmt, PriceRounding)

        return converted_float(BillDiscAmt)

    def get_BillDiscPercent(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscPercent = instances.BillDiscPercent

        BillDiscPercent = round(BillDiscPercent, PriceRounding)

        return converted_float(BillDiscPercent)

    def get_VATAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        VATAmount = instances.VATAmount

        VATAmount = round(VATAmount, PriceRounding)

        return converted_float(VATAmount)

    def get_SGSTAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        SGSTAmount = instances.SGSTAmount

        SGSTAmount = round(SGSTAmount, PriceRounding)

        return converted_float(SGSTAmount)

    def get_CGSTAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CGSTAmount = instances.CGSTAmount

        CGSTAmount = round(CGSTAmount, PriceRounding)

        return converted_float(CGSTAmount)

    def get_IGSTAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        IGSTAmount = instances.IGSTAmount

        IGSTAmount = round(IGSTAmount, PriceRounding)

        return converted_float(IGSTAmount)

    def get_TAX1Amount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TAX1Amount = instances.TAX1Amount

        TAX1Amount = round(TAX1Amount, PriceRounding)

        return converted_float(TAX1Amount)

    def get_TAX2Amount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TAX2Amount = instances.TAX2Amount

        TAX2Amount = round(TAX2Amount, PriceRounding)

        return converted_float(TAX2Amount)

    def get_TAX3Amount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TAX3Amount = instances.TAX3Amount

        TAX3Amount = round(TAX3Amount, PriceRounding)

        return converted_float(TAX3Amount)

    def get_Balance(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        Balance = instances.Balance

        Balance = round(Balance, PriceRounding)

        return converted_float(Balance)

    def get_TotalGrossAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalGrossAmt = instances.TotalGrossAmt

        TotalGrossAmt = round(TotalGrossAmt, PriceRounding)

        return converted_float(TotalGrossAmt)

    def get_AddlDiscPercent(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        AddlDiscPercent = instances.AddlDiscPercent

        AddlDiscPercent = round(AddlDiscPercent, PriceRounding)

        return converted_float(AddlDiscPercent)

    def get_AddlDiscAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        AddlDiscAmt = instances.AddlDiscAmt

        AddlDiscAmt = round(AddlDiscAmt, PriceRounding)

        return converted_float(AddlDiscAmt)

    def get_TotalDiscount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalDiscount = instances.TotalDiscount

        TotalDiscount = round(TotalDiscount, PriceRounding)

        return converted_float(TotalDiscount)

    def get_TotalTax(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalTax = instances.TotalTax

        TotalTax = round(TotalTax, PriceRounding)

        return converted_float(TotalTax)

    def get_NetTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        NetTotal = instances.NetTotal

        NetTotal = round(NetTotal, PriceRounding)
        return converted_float(NetTotal)

    def get_AdditionalCost(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        AdditionalCost = instances.AdditionalCost

        AdditionalCost = round(AdditionalCost, PriceRounding)

        return converted_float(AdditionalCost)

    def get_GrandTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        GrandTotal = instances.GrandTotal

        GrandTotal = round(GrandTotal, PriceRounding)

        return converted_float(GrandTotal)

    def get_RoundOff(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        RoundOff = instances.RoundOff

        RoundOff = round(RoundOff, PriceRounding)

        return converted_float(RoundOff)

    def get_CashReceived(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CashReceived = instances.CashReceived

        CashReceived = round(CashReceived, PriceRounding)

        return converted_float(CashReceived)

    def get_CashAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CashAmount = instances.CashAmount

        CashAmount = round(CashAmount, PriceRounding)

        return converted_float(CashAmount)

    def get_BankAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BankAmount = instances.BankAmount

        BankAmount = round(BankAmount, PriceRounding)

        return converted_float(BankAmount)


class SalesDetailsPrintSerializer(serializers.ModelSerializer):

    Qty = serializers.SerializerMethodField()
    FreeQty = serializers.SerializerMethodField()
    UnitPrice = serializers.SerializerMethodField()
    RateWithTax = serializers.SerializerMethodField()
    CostPerPrice = serializers.SerializerMethodField()
    DiscountPerc = serializers.SerializerMethodField()
    DiscountAmount = serializers.SerializerMethodField()
    GrossAmount = serializers.SerializerMethodField()
    TaxableAmount = serializers.SerializerMethodField()
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
    DetailsID = serializers.SerializerMethodField()
    MasterID = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()
    Description = serializers.SerializerMethodField()

    class Meta:
        model = SalesDetails
        fields = (
            "DetailsID",
            "BranchID",
            "Action",
            "MasterID",
            "ProductID",
            "ProductName",
            "Qty",
            "FreeQty",
            "UnitPrice",
            "ReturnQty",
            "UnitName",
            "Description",
            "RateWithTax",
            "CostPerPrice",
            "PriceListID",
            "DiscountPerc",
            "DiscountAmount",
            "GrossAmount",
            "TaxableAmount",
            "VATPerc",
            "VATAmount",
            "SGSTPerc",
            "SGSTAmount",
            "CGSTPerc",
            "CGSTAmount",
            "IGSTPerc",
            "IGSTAmount",
            "NetAmount",
            "CreatedDate",
            "CreatedUserID",
            "Flavour",
            "TAX1Perc",
            "TAX1Amount",
            "TAX2Perc",
            "TAX2Amount",
            "TAX3Perc",
            "TAX3Amount",
        )

    def get_ProductName(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID
        product = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)
        ProductName = product.ProductName
        return ProductName

    def get_Description(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID
        product = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)
        Description = product.Description
        return Description

    def get_UnitName(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = purchase_details.PriceListID
        BranchID = purchase_details.BranchID

        UnitName = ""
        if PriceList.objects.filter(
            CompanyID=CompanyID, PriceListID=PriceListID
        ).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListID
            ).UnitID
            UnitName = Unit.objects.get(UnitID=UnitID, CompanyID=CompanyID).UnitName

        return UnitName

    def get_DetailsID(self, sales_details):

        DetailsID = sales_details.SalesDetailsID

        return DetailsID

    def get_MasterID(self, sales_details):

        MasterID = sales_details.SalesMasterID

        return MasterID

    def get_Qty(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        Qty = sales_details.Qty

        Qty = round(Qty, PriceRounding)

        return converted_float(Qty)

    def get_FreeQty(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        FreeQty = sales_details.FreeQty

        FreeQty = round(FreeQty, PriceRounding)

        return converted_float(FreeQty)

    def get_UnitPrice(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        UnitPrice = sales_details.UnitPrice

        UnitPrice = round(UnitPrice, PriceRounding)

        return converted_float(UnitPrice)

    def get_RateWithTax(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        RateWithTax = sales_details.RateWithTax

        RateWithTax = round(RateWithTax, PriceRounding)

        return converted_float(RateWithTax)

    def get_CostPerPrice(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        CostPerPrice = sales_details.CostPerPrice

        CostPerPrice = round(CostPerPrice, PriceRounding)

        return converted_float(CostPerPrice)

    def get_DiscountPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        DiscountPerc = sales_details.DiscountPerc

        DiscountPerc = round(DiscountPerc, PriceRounding)

        return converted_float(DiscountPerc)

    def get_DiscountAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        DiscountAmount = sales_details.DiscountAmount

        DiscountAmount = round(DiscountAmount, PriceRounding)

        return converted_float(DiscountAmount)

    def get_GrossAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        GrossAmount = sales_details.GrossAmount

        GrossAmount = round(GrossAmount, PriceRounding)

        return converted_float(GrossAmount)

    def get_TaxableAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TaxableAmount = sales_details.TaxableAmount

        TaxableAmount = round(TaxableAmount, PriceRounding)

        return converted_float(TaxableAmount)

    def get_VATPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        VATPerc = sales_details.VATPerc

        VATPerc = round(VATPerc, PriceRounding)

        return converted_float(VATPerc)

    def get_VATAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        VATAmount = sales_details.VATAmount

        VATAmount = round(VATAmount, PriceRounding)

        return converted_float(VATAmount)

    def get_SGSTPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        SGSTPerc = sales_details.SGSTPerc

        SGSTPerc = round(SGSTPerc, PriceRounding)

        return converted_float(SGSTPerc)

    def get_SGSTAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        SGSTAmount = sales_details.SGSTAmount

        SGSTAmount = round(SGSTAmount, PriceRounding)

        return converted_float(SGSTAmount)

    def get_CGSTPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        CGSTPerc = sales_details.CGSTPerc

        CGSTPerc = round(CGSTPerc, PriceRounding)

        return converted_float(CGSTPerc)

    def get_CGSTAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        CGSTAmount = sales_details.CGSTAmount

        CGSTAmount = round(CGSTAmount, PriceRounding)

        return converted_float(CGSTAmount)

    def get_IGSTPerc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        IGSTPerc = sales_details.IGSTPerc

        IGSTPerc = round(IGSTPerc, PriceRounding)

        return converted_float(IGSTPerc)

    def get_IGSTAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        IGSTAmount = sales_details.IGSTAmount

        IGSTAmount = round(IGSTAmount, PriceRounding)

        return converted_float(IGSTAmount)

    def get_NetAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        NetAmount = sales_details.NetAmount

        NetAmount = round(NetAmount, PriceRounding)

        return converted_float(NetAmount)


class SalesIntegratedSerializer(serializers.ModelSerializer):
    CashSale = serializers.SerializerMethodField()
    CreditSale = serializers.SerializerMethodField()
    BankSale = serializers.SerializerMethodField()
    CashSaleReturn = serializers.SerializerMethodField()
    CreditSaleReturn = serializers.SerializerMethodField()
    BankSaleReturn = serializers.SerializerMethodField()

    class Meta:
        model = LedgerPosting
        fields = (
            "CashSale",
            "CreditSale",
            "BankSale",
            "CashSaleReturn",
            "CreditSaleReturn",
            "BankSaleReturn",
        )

    def get_CashSale(self, instances):
        CompanyID = self.context.get("CompanyID")
        FromDate = self.context.get("FromDate")
        ToDate = self.context.get("ToDate")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        TotalDebit = 0
        TotalCredit = 0
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder=9
        ).exists():
            if LedgerPosting.objects.filter(
                CompanyID=CompanyID,
                LedgerID=LedgerID,
                Date__gte=FromDate,
                Date__lte=ToDate,
                VoucherType="SI",
            ).exists():
                ledger_ins = LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    LedgerID=LedgerID,
                    Date__gte=FromDate,
                    Date__lte=ToDate,
                    VoucherType="SI",
                )
                for i in ledger_ins:
                    TotalDebit += converted_float(i.Debit)
                    TotalCredit += converted_float(i.Credit)

        CashSales = converted_float(TotalDebit) - converted_float(TotalCredit)
        return CashSales

    def get_BankSale(self, instances):
        CompanyID = self.context.get("CompanyID")
        FromDate = self.context.get("FromDate")
        ToDate = self.context.get("ToDate")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        TotalDebit = 0
        TotalCredit = 0
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder=8
        ).exists():
            if LedgerPosting.objects.filter(
                CompanyID=CompanyID,
                LedgerID=LedgerID,
                Date__gte=FromDate,
                Date__lte=ToDate,
                VoucherType="SI",
            ).exists():
                ledger_ins = LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    LedgerID=LedgerID,
                    Date__gte=FromDate,
                    Date__lte=ToDate,
                    VoucherType="SI",
                )
                for i in ledger_ins:
                    TotalDebit += converted_float(i.Debit)
                    TotalCredit += converted_float(i.Credit)

        BankSales = converted_float(TotalDebit) - converted_float(TotalCredit)
        return BankSales

    def get_CreditSales(self, instances):
        CompanyID = self.context.get("CompanyID")
        FromDate = self.context.get("FromDate")
        ToDate = self.context.get("ToDate")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        TotalDebit = 0
        TotalCredit = 0
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=[10, 29]
        ).exists():
            if LedgerPosting.objects.filter(
                CompanyID=CompanyID,
                LedgerID=LedgerID,
                Date__gte=FromDate,
                Date__lte=ToDate,
                VoucherType="SI",
            ).exists():
                ledger_ins = LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    LedgerID=LedgerID,
                    Date__gte=FromDate,
                    Date__lte=ToDate,
                    VoucherType="SI",
                )
                for i in ledger_ins:
                    TotalDebit += converted_float(i.Debit)
                    TotalCredit += converted_float(i.Credit)

        CreditSales = converted_float(TotalDebit) - converted_float(TotalCredit)
        return CreditSales

    def get_CashSaleReturn(self, instance):

        CompanyID = self.context.get("CompanyID")
        ProductID = instance.ProductID
        BranchID = instance.BranchID
        ProductName = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID
        ).ProductName

        return ProductName

    def get_CreditSaleReturne(self, instance):

        CompanyID = self.context.get("CompanyID")
        WareHouseID = instance.WareHouseID
        BranchID = instance.BranchID
        WareHouseName = Warehouse.objects.get(
            CompanyID=CompanyID, WarehouseID=WareHouseID
        ).WarehouseName

        return WareHouseName

    def get_BankSaleReturn(self, instance):

        CompanyID = self.context.get("CompanyID")
        Qty = instance.Qty
        Cost = instance.Cost
        TotalCost = converted_float(Qty) * converted_float(Cost)

        return TotalCost


class BatchSerializer(serializers.ModelSerializer):
    ManufactureDate = serializers.SerializerMethodField()
    ExpiryDate = serializers.SerializerMethodField()
    WareHouseName = serializers.SerializerMethodField()
    ProductName = serializers.SerializerMethodField()
    Stock = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()

    class Meta:
        model = Batch
        fields = (
            "id",
            "BatchCode",
            "CompanyID",
            "ProductName",
            "Stock",
            "BranchID",
            "ManufactureDate",
            "ExpiryDate",
            "BatchCode",
            "StockIn",
            "StockOut",
            "PurchasePrice",
            "SalesPrice",
            "PriceListID",
            "UnitName",
            "ProductID",
            "WareHouseID",
            "WareHouseName",
        )

    def get_ManufactureDate(self, instance):
        date = ""
        if instance.ManufactureDate:
            date = instance.ManufactureDate

        return date

    def get_UnitName(self, instance):
        CompanyID = self.context.get("CompanyID")
        UnitName = ""
        PriceListID = instance.PriceListID
        BranchID = instance.BranchID
        UnitID = PriceList.objects.get(
            CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID
        ).UnitID
        UnitName = Unit.objects.get(
            CompanyID=CompanyID, BranchID=BranchID, UnitID=UnitID
        ).UnitName
        return UnitName

    def get_ExpiryDate(self, instance):
        date = ""
        if instance.ExpiryDate:
            date = instance.ExpiryDate

        return date

    def get_WareHouseName(self, instance):

        CompanyID = self.context.get("CompanyID")
        WareHouseID = instance.WareHouseID
        BranchID = instance.BranchID
        WareHouseName = Warehouse.objects.get(
            CompanyID=CompanyID, WarehouseID=WareHouseID
        ).WarehouseName

        return WareHouseName

    def get_Stock(self, instance):
        CompanyID = self.context.get("CompanyID")
        batch_pricelistID = instance.PriceListID
        BranchID = instance.BranchID
        batch_MultiFactor = PriceList.objects.get(
            CompanyID=CompanyID, BranchID=BranchID, PriceListID=batch_pricelistID
        ).MultiFactor
        StockIn = instance.StockIn
        StockOut = instance.StockOut
        batch_StockIn = converted_float(StockIn) / converted_float(batch_MultiFactor)
        batch_StockOut = converted_float(StockOut) / converted_float(batch_MultiFactor)
        stock = converted_float(batch_StockIn) - converted_float(batch_StockOut)

        return stock

    def get_ProductName(self, instance):

        CompanyID = self.context.get("CompanyID")
        ProductID = instance.ProductID
        BranchID = instance.BranchID
        ProductName = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID
        ).ProductName

        return ProductName


class SalesSummaryReportSerializer(serializers.ModelSerializer):

    TotalGrossAmt = serializers.SerializerMethodField()
    NetTotal = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    CashSales = serializers.SerializerMethodField()
    BankSales = serializers.SerializerMethodField()
    CreditSales = serializers.SerializerMethodField()

    class Meta:
        model = SalesMaster
        fields = (
            "id",
            "SalesMasterID",
            "BranchID",
            "Action",
            "VoucherNo",
            "Date",
            "LedgerID",
            "LedgerName",
            "TotalGrossAmt",
            "NetTotal",
            "GrandTotal",
            "VATAmount",
            "SGSTAmount",
            "CGSTAmount",
            "IGSTAmount",
            "TAX1Amount",
            "TAX2Amount",
            "TAX3Amount",
            "CashSales",
            "BankSales",
            "CreditSales",
        )

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID
        ).exists():
            ledger = AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID
            )

            LedgerName = ledger.LedgerName
        else:
            LedgerName = ""

        return LedgerName

    def get_CashSales(self, instances):
        CompanyID = self.context.get("CompanyID")
        FromDate = self.context.get("FromDate")
        ToDate = self.context.get("ToDate")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        TotalDebit = 0
        TotalCredit = 0
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder=9
        ).exists():
            if LedgerPosting.objects.filter(
                CompanyID=CompanyID,
                LedgerID=LedgerID,
                Date__gte=FromDate,
                Date__lte=ToDate,
                VoucherType="SI",
            ).exists():

                ledger_ins = LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    LedgerID=LedgerID,
                    Date__gte=FromDate,
                    Date__lte=ToDate,
                    VoucherType="SI",
                )
                for i in ledger_ins:
                    TotalDebit += converted_float(i.Debit)
                    TotalCredit += converted_float(i.Credit)

        CashSales = converted_float(TotalDebit) - converted_float(TotalCredit)
        return CashSales

    def get_BankSales(self, instances):
        CompanyID = self.context.get("CompanyID")
        FromDate = self.context.get("FromDate")
        ToDate = self.context.get("ToDate")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        TotalDebit = 0
        TotalCredit = 0
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder=8
        ).exists():
            if LedgerPosting.objects.filter(
                CompanyID=CompanyID,
                LedgerID=LedgerID,
                Date__gte=FromDate,
                Date__lte=ToDate,
                VoucherType="SI",
            ).exists():
                ledger_ins = LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    LedgerID=LedgerID,
                    Date__gte=FromDate,
                    Date__lte=ToDate,
                    VoucherType="SI",
                )
                for i in ledger_ins:
                    TotalDebit += converted_float(i.Debit)
                    TotalCredit += converted_float(i.Credit)

        BankSales = converted_float(TotalDebit) - converted_float(TotalCredit)
        return BankSales

    def get_CreditSales(self, instances):
        CompanyID = self.context.get("CompanyID")
        FromDate = self.context.get("FromDate")
        ToDate = self.context.get("ToDate")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        TotalDebit = 0
        TotalCredit = 0
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=[10, 29]
        ).exists():
            if LedgerPosting.objects.filter(
                CompanyID=CompanyID,
                LedgerID=LedgerID,
                Date__gte=FromDate,
                Date__lte=ToDate,
                VoucherType="SI",
            ).exists():
                ledger_ins = LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    LedgerID=LedgerID,
                    Date__gte=FromDate,
                    Date__lte=ToDate,
                    VoucherType="SI",
                )
                for i in ledger_ins:
                    TotalDebit += converted_float(i.Debit)
                    TotalCredit += converted_float(i.Credit)

        CreditSales = converted_float(TotalDebit) - converted_float(TotalCredit)
        return CreditSales

    def get_TotalGrossAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalGrossAmt = instances.TotalGrossAmt

        TotalGrossAmt = round(TotalGrossAmt, PriceRounding)

        return converted_float(TotalGrossAmt)

    def get_NetTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        NetTotal = instances.NetTotal

        NetTotal = round(NetTotal, PriceRounding)

        return converted_float(NetTotal)

    def get_GrandTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        GrandTotal = instances.GrandTotal

        GrandTotal = round(GrandTotal, PriceRounding)

        return converted_float(GrandTotal)


class SupplierVsProductReportSerializer(serializers.ModelSerializer):

    LastPurchasePrice = serializers.SerializerMethodField()
    LastPurchaseQty = serializers.SerializerMethodField()
    TotalSales = serializers.SerializerMethodField()
    TotalSalesAmount = serializers.SerializerMethodField()
    AvgSalesRate = serializers.SerializerMethodField()
    TotalPurchase = serializers.SerializerMethodField()
    TotalPurchaseAmount = serializers.SerializerMethodField()
    AvgPurchaseRate = serializers.SerializerMethodField()
    TotalSalesReturn = serializers.SerializerMethodField()
    TotalSalesReturnAmount = serializers.SerializerMethodField()
    AvgSalesReturnRate = serializers.SerializerMethodField()
    TotalPurchaseReturn = serializers.SerializerMethodField()
    TotalPurchaseReturnAmount = serializers.SerializerMethodField()
    AvgPurchaseReturnRate = serializers.SerializerMethodField()
    CurrentStock = serializers.SerializerMethodField()
    Unit = serializers.SerializerMethodField()
    Code = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "ProductID",
            "Code",
            "ProductName",
            "LastPurchasePrice",
            "LastPurchaseQty",
            "TotalSales",
            "TotalSalesAmount",
            "AvgSalesRate",
            "TotalPurchase",
            "TotalPurchaseAmount",
            "AvgPurchaseRate",
            "TotalSalesReturn",
            "TotalSalesReturnAmount",
            "AvgSalesReturnRate",
            "TotalPurchaseReturn",
            "TotalPurchaseReturnAmount",
            "AvgPurchaseReturnRate",
            "CurrentStock",
            "Unit",
        )

    def get_Code(self, instances):
        CompanyID = self.context.get("CompanyID")
        Code = instances.ProductCode
        return Code

    def get_LastPurchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        LastPurchasePrice = 0
        if PurchaseDetails.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
        ).exists():
            LastPurchasePrice = (
                PurchaseDetails.objects.filter(
                    CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
                )
                .first()
                .UnitPrice
            )

        return str(LastPurchasePrice)

    def get_LastPurchaseQty(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        LastPurchaseQty = 0
        if PurchaseDetails.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
        ).exists():
            LastPurchaseQty = (
                PurchaseDetails.objects.filter(
                    CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
                )
                .first()
                .Qty
            )

        return str(LastPurchaseQty)

    def get_TotalSales(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        TotalSales = 0
        if SalesDetails.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
        ).exists():
            salesDetails_ins = SalesDetails.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
            )

            TotalSales = salesDetails_ins.aggregate(Sum("Qty"))
            TotalSales = TotalSales["Qty__sum"]
        return str(TotalSales)

    def get_TotalSalesAmount(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        TotalSalesAmount = 0
        if SalesDetails.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
        ).exists():
            salesDetails_ins = SalesDetails.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
            )

            TotalSalesAmount = salesDetails_ins.aggregate(Sum("GrossAmount"))
            TotalSalesAmount = TotalSalesAmount["GrossAmount__sum"]
        return str(TotalSalesAmount)

    def get_AvgSalesRate(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        AvgSalesRate = 0
        if SalesDetails.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
        ).exists():
            salesDetails_ins = SalesDetails.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
            )
            MultiFactor = PriceList.objects.get(
                CompanyID=CompanyID,
                BranchID=BranchID,
                ProductID=ProductID,
                DefaultUnit=True,
            ).MultiFactor
            AvgSalesRate = 0
            for s in salesDetails_ins:
                if not converted_float(s.Qty) == 0:
                    oneAvg = (
                        converted_float(s.Qty)
                        * converted_float(MultiFactor)
                        * converted_float(s.UnitPrice)
                    ) / (converted_float(s.Qty) * converted_float(MultiFactor))
                    AvgSalesRate += oneAvg
        return str(AvgSalesRate)

    def get_TotalPurchase(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        TotalPurchase = 0
        if PurchaseDetails.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
        ).exists():
            purchaseDetails_ins = PurchaseDetails.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
            )

            TotalPurchase = purchaseDetails_ins.aggregate(Sum("Qty"))
            TotalPurchase = TotalPurchase["Qty__sum"]
        return str(TotalPurchase)

    def get_TotalPurchaseAmount(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        TotalPurchaseAmount = 0
        if PurchaseDetails.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
        ).exists():
            purchaseDetails_ins = PurchaseDetails.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
            )
            TotalPurchaseAmount = purchaseDetails_ins.aggregate(Sum("GrossAmount"))
            TotalPurchaseAmount = TotalPurchaseAmount["GrossAmount__sum"]
        return str(TotalPurchaseAmount)

    def get_AvgPurchaseRate(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        AvgPurchaseRate = 0
        if PurchaseDetails.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
        ).exists():
            purchaseDetails_ins = PurchaseDetails.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
            )
            MultiFactor = PriceList.objects.get(
                CompanyID=CompanyID,
                BranchID=BranchID,
                ProductID=ProductID,
                DefaultUnit=True,
            ).MultiFactor
            AvgPurchaseRate = 0
            for s in purchaseDetails_ins:
                if not converted_float(s.Qty) == 0:
                    oneAvg = (
                        converted_float(s.Qty)
                        * converted_float(MultiFactor)
                        * converted_float(s.UnitPrice)
                    ) / (converted_float(s.Qty) * converted_float(MultiFactor))
                    AvgPurchaseRate += oneAvg
        return str(AvgPurchaseRate)

    def get_TotalSalesReturn(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        TotalSalesReturn = 0
        if SalesReturnDetails.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
        ).exists():
            salesReturnDetails_ins = SalesReturnDetails.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
            )

            TotalSalesReturn = salesReturnDetails_ins.aggregate(Sum("Qty"))
            TotalSalesReturn = TotalSalesReturn["Qty__sum"]
        return str(TotalSalesReturn)

    def get_TotalSalesReturnAmount(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        TotalSalesReturnAmount = 0
        if SalesReturnDetails.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
        ).exists():
            salesReturnDetails_ins = SalesReturnDetails.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
            )
            TotalSalesReturnAmount = salesReturnDetails_ins.aggregate(
                Sum("GrossAmount")
            )
            TotalSalesReturnAmount = TotalSalesReturnAmount["GrossAmount__sum"]
        return str(TotalSalesReturnAmount)

    def get_AvgSalesReturnRate(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        AvgSalesReturnRate = 0
        if SalesReturnDetails.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
        ).exists():
            salesReturnDetails_ins = SalesReturnDetails.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
            )
            MultiFactor = PriceList.objects.get(
                CompanyID=CompanyID,
                BranchID=BranchID,
                ProductID=ProductID,
                DefaultUnit=True,
            ).MultiFactor
            AvgSalesReturnRate = 0
            for s in salesReturnDetails_ins:
                oneAvg = (
                    converted_float(s.Qty)
                    * converted_float(MultiFactor)
                    * converted_float(s.UnitPrice)
                ) / (converted_float(s.Qty) * converted_float(MultiFactor))
                AvgSalesReturnRate += oneAvg
        return str(AvgSalesReturnRate)

    def get_TotalPurchaseReturn(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        TotalPurchaseReturn = 0
        if PurchaseReturnDetails.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
        ).exists():
            purchaseReturnDetails_ins = PurchaseReturnDetails.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
            )

            TotalPurchaseReturn = purchaseReturnDetails_ins.aggregate(Sum("Qty"))
            TotalPurchaseReturn = TotalPurchaseReturn["Qty__sum"]
        return str(TotalPurchaseReturn)

    def get_TotalPurchaseReturnAmount(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        TotalPurchaseReturnAmount = 0
        if PurchaseReturnDetails.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
        ).exists():
            purchaseReturnDetails_ins = PurchaseReturnDetails.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
            )
            TotalPurchaseReturnAmount = purchaseReturnDetails_ins.aggregate(
                Sum("GrossAmount")
            )
            TotalPurchaseReturnAmount = TotalPurchaseReturnAmount["GrossAmount__sum"]
        return str(TotalPurchaseReturnAmount)

    def get_AvgPurchaseReturnRate(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        AvgPurchaseReturnRate = 0
        if PurchaseReturnDetails.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
        ).exists():
            purchaseReturnDetails_ins = PurchaseReturnDetails.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
            )
            MultiFactor = PriceList.objects.get(
                CompanyID=CompanyID,
                BranchID=BranchID,
                ProductID=ProductID,
                DefaultUnit=True,
            ).MultiFactor
            AvgPurchaseReturnRate = 0
            for s in purchaseReturnDetails_ins:
                oneAvg = (
                    converted_float(s.Qty)
                    * converted_float(MultiFactor)
                    * converted_float(s.UnitPrice)
                ) / (converted_float(s.Qty) * converted_float(MultiFactor))
                AvgPurchaseReturnRate += oneAvg
        return str(AvgPurchaseReturnRate)

    def get_CurrentStock(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        CurrentStock = 0
        if StockPosting.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
        ).exists():
            QtyIn_sum = StockPosting.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
            ).aggregate(Sum("QtyIn"))
            QtyIn_sum = QtyIn_sum["QtyIn__sum"]
            QtyOut_sum = StockPosting.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
            ).aggregate(Sum("QtyOut"))
            QtyOut_sum = QtyOut_sum["QtyOut__sum"]
            CurrentStock = converted_float(QtyIn_sum) - converted_float(QtyOut_sum)
        return str(CurrentStock)

    def get_Unit(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = instances.ProductID
        BranchID = instances.BranchID
        UnitName = ""
        if PriceList.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True
        ).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True
            ).UnitID
            UnitName = Unit.objects.get(CompanyID=CompanyID, UnitID=UnitID).UnitName
        return str(UnitName)


class ProductVsSuppliersReportSerializer(serializers.ModelSerializer):
    LastPurchasePrice = serializers.SerializerMethodField()
    LastPurchaseQty = serializers.SerializerMethodField()
    TotalSales = serializers.SerializerMethodField()
    TotalSalesAmount = serializers.SerializerMethodField()
    AvgSalesRate = serializers.SerializerMethodField()
    TotalPurchase = serializers.SerializerMethodField()
    TotalPurchaseAmount = serializers.SerializerMethodField()
    AvgPurchaseRate = serializers.SerializerMethodField()
    TotalSalesReturn = serializers.SerializerMethodField()
    TotalSalesReturnAmount = serializers.SerializerMethodField()
    AvgSalesReturnRate = serializers.SerializerMethodField()
    TotalPurchaseReturn = serializers.SerializerMethodField()
    TotalPurchaseReturnAmount = serializers.SerializerMethodField()
    AvgPurchaseReturnRate = serializers.SerializerMethodField()
    CurrentStock = serializers.SerializerMethodField()
    Unit = serializers.SerializerMethodField()
    Code = serializers.SerializerMethodField()
    ProductName = serializers.SerializerMethodField()

    class Meta:
        model = Parties
        fields = (
            "id",
            "PartyID",
            "Code",
            "LedgerID",
            "ProductName",
            "LastPurchasePrice",
            "LastPurchaseQty",
            "TotalSales",
            "TotalSalesAmount",
            "AvgSalesRate",
            "TotalPurchase",
            "TotalPurchaseAmount",
            "AvgPurchaseRate",
            "TotalSalesReturn",
            "TotalSalesReturnAmount",
            "AvgSalesReturnRate",
            "TotalPurchaseReturn",
            "TotalPurchaseReturnAmount",
            "AvgPurchaseReturnRate",
            "CurrentStock",
            "Unit",
        )

    def get_Code(self, instances):
        CompanyID = self.context.get("CompanyID")
        Code = instances.PartyCode
        return Code

    def get_ProductName(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductName = instances.PartyName
        return ProductName

    def get_LastPurchasePrice(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = self.context.get("ProductID")
        BranchID = instances.BranchID
        LedgerID = instances.LedgerID
        LastPurchasePrice = 0

        if PurchaseMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        ).exists():
            purchase_master_ids = PurchaseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).values_list("PurchaseMasterID", flat=True)
            if PurchaseDetails.objects.filter(
                CompanyID=CompanyID,
                ProductID=ProductID,
                PurchaseMasterID__in=purchase_master_ids,
                BranchID=BranchID,
            ).exists():
                LastPurchasePrice = (
                    PurchaseDetails.objects.filter(
                        CompanyID=CompanyID,
                        ProductID=ProductID,
                        PurchaseMasterID__in=purchase_master_ids,
                        BranchID=BranchID,
                    )
                    .first()
                    .UnitPrice
                )

        return converted_float(LastPurchasePrice)

    def get_LastPurchaseQty(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = self.context.get("ProductID")
        BranchID = instances.BranchID
        LedgerID = instances.LedgerID
        LastPurchaseQty = 0

        if PurchaseMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        ).exists():
            purchase_master_ids = PurchaseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).values_list("PurchaseMasterID", flat=True)
            if PurchaseDetails.objects.filter(
                CompanyID=CompanyID,
                ProductID=ProductID,
                PurchaseMasterID__in=purchase_master_ids,
                BranchID=BranchID,
            ).exists():
                LastPurchaseQty = (
                    PurchaseDetails.objects.filter(
                        CompanyID=CompanyID,
                        ProductID=ProductID,
                        PurchaseMasterID__in=purchase_master_ids,
                        BranchID=BranchID,
                    )
                    .first()
                    .Qty
                )
        return converted_float(LastPurchaseQty)

    def get_TotalSales(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = self.context.get("ProductID")
        BranchID = instances.BranchID
        LedgerID = instances.LedgerID
        TotalSales = 0

        if SalesMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        ).exists():
            sales_master_ids = SalesMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).values_list("SalesMasterID", flat=True)
            if SalesDetails.objects.filter(
                CompanyID=CompanyID,
                ProductID=ProductID,
                SalesMasterID__in=sales_master_ids,
                BranchID=BranchID,
            ).exists():
                detail_ins = SalesDetails.objects.filter(
                    CompanyID=CompanyID,
                    ProductID=ProductID,
                    SalesMasterID__in=sales_master_ids,
                    BranchID=BranchID,
                )
                TotalSales = detail_ins.aggregate(Sum("Qty"))
                TotalSales = TotalSales["Qty__sum"]
        return converted_float(TotalSales)

    def get_TotalSalesAmount(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = self.context.get("ProductID")
        BranchID = instances.BranchID
        LedgerID = instances.LedgerID
        TotalSalesAmount = 0

        if SalesMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        ).exists():
            sales_master_ids = SalesMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).values_list("SalesMasterID", flat=True)
            if SalesDetails.objects.filter(
                CompanyID=CompanyID,
                ProductID=ProductID,
                SalesMasterID__in=sales_master_ids,
                BranchID=BranchID,
            ).exists():
                salesDetails_ins = SalesDetails.objects.filter(
                    CompanyID=CompanyID,
                    ProductID=ProductID,
                    SalesMasterID__in=sales_master_ids,
                    BranchID=BranchID,
                )
                TotalSalesAmount = salesDetails_ins.aggregate(Sum("GrossAmount"))
                TotalSalesAmount = TotalSalesAmount["GrossAmount__sum"]
        return converted_float(TotalSalesAmount)

    def get_AvgSalesRate(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = self.context.get("ProductID")
        BranchID = instances.BranchID
        LedgerID = instances.LedgerID
        AvgSalesRate = 0

        if SalesMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        ).exists():
            sales_master_ids = SalesMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).values_list("SalesMasterID", flat=True)
            if SalesDetails.objects.filter(
                CompanyID=CompanyID,
                ProductID=ProductID,
                SalesMasterID__in=sales_master_ids,
                BranchID=BranchID,
            ).exists():
                salesDetails_ins = SalesDetails.objects.filter(
                    CompanyID=CompanyID,
                    ProductID=ProductID,
                    SalesMasterID__in=sales_master_ids,
                    BranchID=BranchID,
                )
                MultiFactor = PriceList.objects.get(
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    ProductID=ProductID,
                    DefaultUnit=True,
                ).MultiFactor
                AvgSalesRate = 0
                for s in salesDetails_ins:
                    oneAvg = (
                        converted_float(s.Qty)
                        * converted_float(MultiFactor)
                        * converted_float(s.UnitPrice)
                    ) / (converted_float(s.Qty) * converted_float(MultiFactor))
                    AvgSalesRate += oneAvg

        return converted_float(AvgSalesRate)

    def get_TotalPurchase(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = self.context.get("ProductID")
        BranchID = instances.BranchID
        LedgerID = instances.LedgerID
        TotalPurchase = 0

        if PurchaseMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        ).exists():
            purchase_master_ids = PurchaseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).values_list("PurchaseMasterID", flat=True)
            if PurchaseDetails.objects.filter(
                CompanyID=CompanyID,
                ProductID=ProductID,
                PurchaseMasterID__in=purchase_master_ids,
                BranchID=BranchID,
            ).exists():
                detail_ins = PurchaseDetails.objects.filter(
                    CompanyID=CompanyID,
                    ProductID=ProductID,
                    PurchaseMasterID__in=purchase_master_ids,
                    BranchID=BranchID,
                )
                TotalPurchase = detail_ins.aggregate(Sum("Qty"))
                TotalPurchase = TotalPurchase["Qty__sum"]
        return converted_float(TotalPurchase)

    def get_TotalPurchaseAmount(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = self.context.get("ProductID")
        BranchID = instances.BranchID
        LedgerID = instances.LedgerID
        TotalPurchaseAmount = 0

        if PurchaseMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        ).exists():
            purchase_master_ids = PurchaseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).values_list("PurchaseMasterID", flat=True)
            if PurchaseDetails.objects.filter(
                CompanyID=CompanyID,
                ProductID=ProductID,
                PurchaseMasterID__in=purchase_master_ids,
                BranchID=BranchID,
            ).exists():
                purchaseDetails_ins = PurchaseDetails.objects.filter(
                    CompanyID=CompanyID,
                    ProductID=ProductID,
                    PurchaseMasterID__in=purchase_master_ids,
                    BranchID=BranchID,
                )
                TotalPurchaseAmount = purchaseDetails_ins.aggregate(Sum("GrossAmount"))
                TotalPurchaseAmount = TotalPurchaseAmount["GrossAmount__sum"]
        return converted_float(TotalPurchaseAmount)

    def get_AvgPurchaseRate(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = self.context.get("ProductID")
        BranchID = instances.BranchID
        LedgerID = instances.LedgerID
        AvgPurchaseRate = 0

        if PurchaseMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        ).exists():
            purchase_master_ids = PurchaseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).values_list("PurchaseMasterID", flat=True)
            if PurchaseDetails.objects.filter(
                CompanyID=CompanyID,
                ProductID=ProductID,
                PurchaseMasterID__in=purchase_master_ids,
                BranchID=BranchID,
            ).exists():
                purchaseDetails_ins = PurchaseDetails.objects.filter(
                    CompanyID=CompanyID,
                    ProductID=ProductID,
                    PurchaseMasterID__in=purchase_master_ids,
                    BranchID=BranchID,
                )
                MultiFactor = PriceList.objects.get(
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    ProductID=ProductID,
                    DefaultUnit=True,
                ).MultiFactor
                AvgPurchaseRate = 0
                for s in purchaseDetails_ins:
                    oneAvg = (
                        converted_float(s.Qty)
                        * converted_float(MultiFactor)
                        * converted_float(s.UnitPrice)
                    ) / (converted_float(s.Qty) * converted_float(MultiFactor))
                    AvgPurchaseRate += oneAvg
        return converted_float(AvgPurchaseRate)

    def get_TotalSalesReturn(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = self.context.get("ProductID")
        BranchID = instances.BranchID
        LedgerID = instances.LedgerID
        TotalSalesReturn = 0

        if SalesReturnMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        ).exists():
            salesReturn_master_ids = SalesReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).values_list("SalesReturnMasterID", flat=True)
            if SalesReturnDetails.objects.filter(
                CompanyID=CompanyID,
                ProductID=ProductID,
                SalesReturnMasterID__in=salesReturn_master_ids,
                BranchID=BranchID,
            ).exists():
                detail_ins = SalesReturnDetails.objects.filter(
                    CompanyID=CompanyID,
                    ProductID=ProductID,
                    SalesReturnMasterID__in=salesReturn_master_ids,
                    BranchID=BranchID,
                )
                TotalSalesReturn = detail_ins.aggregate(Sum("Qty"))
                TotalSalesReturn = TotalSalesReturn["Qty__sum"]
        return converted_float(TotalSalesReturn)

    def get_TotalSalesReturnAmount(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = self.context.get("ProductID")
        BranchID = instances.BranchID
        LedgerID = instances.LedgerID
        TotalSalesReturnAmount = 0

        if SalesReturnMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        ).exists():
            salesReturn_master_ids = SalesReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).values_list("SalesReturnMasterID", flat=True)
            if SalesReturnDetails.objects.filter(
                CompanyID=CompanyID,
                ProductID=ProductID,
                SalesReturnMasterID__in=salesReturn_master_ids,
                BranchID=BranchID,
            ).exists():
                detail_ins = SalesReturnDetails.objects.filter(
                    CompanyID=CompanyID,
                    ProductID=ProductID,
                    SalesReturnMasterID__in=salesReturn_master_ids,
                    BranchID=BranchID,
                )
                TotalSalesReturnAmount = detail_ins.aggregate(Sum("GrossAmount"))
                TotalSalesReturnAmount = TotalSalesReturnAmount["GrossAmount__sum"]
        return converted_float(TotalSalesReturnAmount)

    def get_AvgSalesReturnRate(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = self.context.get("ProductID")
        BranchID = instances.BranchID
        LedgerID = instances.LedgerID
        AvgSalesReturnRate = 0

        if SalesReturnMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        ).exists():
            purchase_master_ids = SalesReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).values_list("SalesReturnMasterID", flat=True)
            if SalesReturnDetails.objects.filter(
                CompanyID=CompanyID,
                ProductID=ProductID,
                SalesReturnMasterID__in=purchase_master_ids,
                BranchID=BranchID,
            ).exists():
                detail_ins = SalesReturnDetails.objects.filter(
                    CompanyID=CompanyID,
                    ProductID=ProductID,
                    SalesReturnMasterID__in=purchase_master_ids,
                    BranchID=BranchID,
                )
                MultiFactor = PriceList.objects.get(
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    ProductID=ProductID,
                    DefaultUnit=True,
                ).MultiFactor
                AvgSalesReturnRate = 0
                for s in detail_ins:
                    oneAvg = (
                        converted_float(s.Qty)
                        * converted_float(MultiFactor)
                        * converted_float(s.UnitPrice)
                    ) / (converted_float(s.Qty) * converted_float(MultiFactor))
                    AvgSalesReturnRate += oneAvg
        return converted_float(AvgSalesReturnRate)

    def get_TotalPurchaseReturn(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = self.context.get("ProductID")
        BranchID = instances.BranchID
        LedgerID = instances.LedgerID
        TotalPurchaseReturn = 0

        if PurchaseReturnMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        ).exists():
            purchaseReturn_master_ids = PurchaseReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).values_list("PurchaseReturnMasterID", flat=True)
            if PurchaseReturnDetails.objects.filter(
                CompanyID=CompanyID,
                ProductID=ProductID,
                PurchaseReturnMasterID__in=purchaseReturn_master_ids,
                BranchID=BranchID,
            ).exists():
                detail_ins = PurchaseReturnDetails.objects.filter(
                    CompanyID=CompanyID,
                    ProductID=ProductID,
                    PurchaseReturnMasterID__in=purchaseReturn_master_ids,
                    BranchID=BranchID,
                )
                TotalPurchaseReturn = detail_ins.aggregate(Sum("Qty"))
                TotalPurchaseReturn = TotalPurchaseReturn["Qty__sum"]
        return converted_float(TotalPurchaseReturn)

    def get_TotalPurchaseReturnAmount(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = self.context.get("ProductID")
        BranchID = instances.BranchID
        LedgerID = instances.LedgerID
        TotalPurchaseReturnAmount = 0

        if PurchaseReturnMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        ).exists():
            purchaseReturn_master_ids = PurchaseReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).values_list("PurchaseReturnMasterID", flat=True)
            if PurchaseReturnDetails.objects.filter(
                CompanyID=CompanyID,
                ProductID=ProductID,
                PurchaseReturnMasterID__in=purchaseReturn_master_ids,
                BranchID=BranchID,
            ).exists():
                detail_ins = PurchaseReturnDetails.objects.filter(
                    CompanyID=CompanyID,
                    ProductID=ProductID,
                    PurchaseReturnMasterID__in=purchaseReturn_master_ids,
                    BranchID=BranchID,
                )
                TotalPurchaseReturnAmount = detail_ins.aggregate(Sum("GrossAmount"))
                TotalPurchaseReturnAmount = TotalPurchaseReturnAmount[
                    "GrossAmount__sum"
                ]
        return converted_float(TotalPurchaseReturnAmount)

    def get_AvgPurchaseReturnRate(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = self.context.get("ProductID")
        BranchID = instances.BranchID
        LedgerID = instances.LedgerID
        AvgPurchaseReturnRate = 0

        if PurchaseReturnMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        ).exists():
            purchaseReturn_master_ids = PurchaseReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).values_list("PurchaseReturnMasterID", flat=True)
            if PurchaseReturnDetails.objects.filter(
                CompanyID=CompanyID,
                ProductID=ProductID,
                PurchaseReturnMasterID__in=purchaseReturn_master_ids,
                BranchID=BranchID,
            ).exists():
                detail_ins = PurchaseReturnDetails.objects.filter(
                    CompanyID=CompanyID,
                    ProductID=ProductID,
                    PurchaseReturnMasterID__in=purchaseReturn_master_ids,
                    BranchID=BranchID,
                )
                MultiFactor = PriceList.objects.get(
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    ProductID=ProductID,
                    DefaultUnit=True,
                ).MultiFactor
                AvgPurchaseReturnRate = 0
                for s in detail_ins:
                    oneAvg = (
                        converted_float(s.Qty)
                        * converted_float(MultiFactor)
                        * converted_float(s.UnitPrice)
                    ) / (converted_float(s.Qty) * converted_float(MultiFactor))
                    AvgPurchaseReturnRate += oneAvg
        return converted_float(AvgPurchaseReturnRate)

    def get_CurrentStock(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = self.context.get("ProductID")
        BranchID = instances.BranchID
        CurrentStock = 0
        if StockPosting.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
        ).exists():
            QtyIn_sum = StockPosting.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
            ).aggregate(Sum("QtyIn"))
            QtyIn_sum = QtyIn_sum["QtyIn__sum"]
            QtyOut_sum = StockPosting.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
            ).aggregate(Sum("QtyOut"))
            QtyOut_sum = QtyOut_sum["QtyOut__sum"]
            CurrentStock = converted_float(QtyIn_sum) - converted_float(QtyOut_sum)
        return converted_float(CurrentStock)

    def get_Unit(self, instances):
        CompanyID = self.context.get("CompanyID")
        ProductID = self.context.get("ProductID")
        BranchID = instances.BranchID
        UnitName = ""
        if PriceList.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True
        ).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True
            ).UnitID
            UnitName = Unit.objects.get(CompanyID=CompanyID, UnitID=UnitID).UnitName
        return UnitName


class StockValueInventoryFlowSerializer(serializers.ModelSerializer):

    Qty = serializers.SerializerMethodField()
    Cost = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ("id", "Qty", "Cost")

    def get_Cost(self, instance):

        CompanyID = self.context.get("CompanyID")
        WareHouseID = self.context.get("WareHouseID")
        ToDate = self.context.get("ToDate")
        FromDate = self.context.get("FromDate")

        ProductID = instance.ProductID
        BranchID = instance.BranchID

        Cost = 0

        if StockPosting.objects.filter(
            ProductID=ProductID,
            CompanyID=CompanyID,
            QtyIn__gt=0,
            Date__gte=FromDate,
            Date__lte=ToDate,
            VoucherType="PI",
        ).exists():
            stock_ins = StockPosting.objects.filter(
                ProductID=ProductID,
                CompanyID=CompanyID,
                QtyIn__gt=0,
                Date__gte=FromDate,
                Date__lte=ToDate,
                VoucherType="PI",
            )
            if not WareHouseID == 0:
                stock_ins = stock_ins.filter(WareHouseID=WareHouseID)
            TotalQtyInRate = 0
            TotalQtyIn = 0
            TotalQtyInRate = stock_ins.aggregate(total_sum=Sum(F("QtyIn") * F("Rate")))
            TotalQtyIn = stock_ins.aggregate(Sum("QtyIn"))
            TotalQtyIn = TotalQtyIn["QtyIn__sum"]
            TotalQtyInRate = TotalQtyInRate["total_sum"]
            Cost = converted_float(TotalQtyInRate) / converted_float(TotalQtyIn)

        return Cost

    def get_Qty(self, instance):

        CompanyID = self.context.get("CompanyID")
        WareHouseID = self.context.get("WareHouseID")
        ToDate = self.context.get("ToDate")
        FromDate = self.context.get("FromDate")

        ProductID = instance.ProductID
        BranchID = instance.BranchID

        Qty = 0

        if StockPosting.objects.filter(
            ProductID=ProductID,
            CompanyID=CompanyID,
            Date__gte=FromDate,
            Date__lte=ToDate,
        ).exists():
            stock_ins = StockPosting.objects.filter(
                ProductID=ProductID,
                CompanyID=CompanyID,
                Date__gte=FromDate,
                Date__lte=ToDate,
            )
            if not WareHouseID == 0:
                stock_ins = stock_ins.filter(WareHouseID=WareHouseID)
            TotalQtyIn = 0
            TotalQtyOut = 0
            for s in stock_ins:
                TotalQtyIn += s.QtyIn
                TotalQtyOut += s.QtyOut

            Qty = converted_float(TotalQtyIn) - converted_float(TotalQtyOut)

        return Qty


class ToDateCheckSerializer(serializers.Serializer):
    ToDate = serializers.DateField()


class FilterOrderSerializer(serializers.ModelSerializer):
    is_checked = serializers.SerializerMethodField()

    class Meta:
        model = SalesOrderMaster
        fields = ("id", "SalesOrderMasterID", "VoucherNo", "Date", "is_checked")

    def get_is_checked(self, instances):
        is_checked = False
        return is_checked


class FilterEstimateSerializer(serializers.ModelSerializer):
    is_checked = serializers.SerializerMethodField()

    class Meta:
        model = SalesEstimateMaster
        fields = ("id", "SalesEstimateMasterID", "VoucherNo", "Date", "is_checked")

    def get_is_checked(self, instances):
        is_checked = False
        return is_checked


class BillWiseSerializer(serializers.ModelSerializer):

    NetAmount = serializers.SerializerMethodField()
    NetCost = serializers.SerializerMethodField()
    Profit = serializers.SerializerMethodField()

    class Meta:
        model = SalesMaster
        fields = (
            "id",
            "Date",
            "VoucherNo",
            "TotalGrossAmt",
            "VATAmount",
            "NetAmount",
            "TotalTax",
            "NetCost",
            "Profit",
            "GrandTotal",
        )

    def get_NetAmount(self, instance):
        # CompanyID = self.context.get("CompanyID")
        # NetTotal = instance.NetTotal
        # BranchID = instance.BranchID
        # TotalGrossAmt = instance.TotalGrossAmt
        # TotalDiscount = instance.TotalDiscount
        # NetAmount = converted_float(TotalGrossAmt) - converted_float(TotalDiscount)
        NetAmount = instance.NetTotal
        return str(NetAmount)

    def get_NetCost(self, instance):
        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        SalesMasterID = instance.SalesMasterID

        salesdetail_ins = SalesDetails.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, SalesMasterID=SalesMasterID
        )
        NetCost = 0
        if salesdetail_ins:
            NetCosts = salesdetail_ins.aggregate(
                total_sum=Sum(F("CostPerPrice") * F("Qty"))
            )

            NetCost = NetCosts["total_sum"]

        return str(NetCost)

    def get_Profit(self, instance):
        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        SalesMasterID = instance.SalesMasterID

        salesdetail_ins = SalesDetails.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, SalesMasterID=SalesMasterID
        )
        Profit = 0
        if salesdetail_ins:
            NetCosts = salesdetail_ins.aggregate(
                total_sum=Sum(F("CostPerPrice") * F("Qty"))
            )

            NetCost = NetCosts["total_sum"]

            TotalGrossAmt = instance.TotalGrossAmt
            TotalDiscount = instance.TotalDiscount
            NetAmount = converted_float(TotalGrossAmt) - converted_float(TotalDiscount)

            Profit = converted_float(NetAmount) - converted_float(NetCost)

        return str(Profit)


class GST_B2B_Serializer(serializers.ModelSerializer):
    CustomerName = serializers.SerializerMethodField()
    # VoucherNo = serializers.SerializerMethodField()
    Date = serializers.SerializerMethodField()
    # GrandTotal = serializers.SerializerMethodField()
    Customer_GST_No = serializers.SerializerMethodField()
    PlaceOfSupply = serializers.SerializerMethodField()
    ApplicableTaxRate = serializers.SerializerMethodField()
    ReverseCharge = serializers.SerializerMethodField()
    InvoiceType = serializers.SerializerMethodField()
    E_Commerce_GSTIN = serializers.SerializerMethodField()
    CESS_amount = serializers.SerializerMethodField()
    Type = serializers.SerializerMethodField()
    PlaceOfSupply_id = serializers.SerializerMethodField()

    class Meta:
        model = SalesMaster

        fields = (
            "Customer_GST_No",
            "CustomerName",
            "VoucherNo",
            "Date",
            "GrandTotal",
            "PlaceOfSupply",
            "ApplicableTaxRate",
            "ReverseCharge",
            "InvoiceType",
            "E_Commerce_GSTIN",
            "CESS_amount",
            "SalesMasterID",
            "Type",
            "ShippingCharge",
            "shipping_tax_amount",
            "SalesTax",
            "PlaceOfSupply_id",
            "TaxType",
        )

    def get_Date(self, instances):
        Date = instances.Date
        # date_object = datetime.strptime(Date, "%Y-%m-%d")
        Date = Date.strftime("%d-%b-%y")
        return Date

    def get_PlaceOfSupply_id(self, instances):
        CompanyID = self.context.get("CompanyID")
        SalesMasterID = instances.SalesMasterID
        BranchID = instances.BranchID
        LedgerID = instances.LedgerID
        # LedgerID = SalesMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,SalesMasterID=SalesMasterID).first().LedgerID
        BranchID = instances.BranchID
        State_of_Supply = instances.State_of_Supply

        # if SalesMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,SalesMasterID=SalesMasterID).exists():
        #     State_of_Supply = SalesMaster.objects.get(CompanyID=CompanyID,BranchID=BranchID,SalesMasterID=SalesMasterID).State_of_Supply
        if not State_of_Supply:
            if Parties.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).exists():
                State_of_Supply = (
                    Parties.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
                    )
                    .first()
                    .State
                )
        if not State_of_Supply:
            State_of_Supply = "19b4fb50-6882-4d29-81cc-0591191f25e6"
        return State_of_Supply

    def get_Type(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        Type = "OE"

        return Type

    def get_CustomerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        CustomerName = ""
        SalesMasterID = instances.SalesMasterID
        LedgerID = instances.LedgerID
        # LedgerID = SalesMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,SalesMasterID=SalesMasterID).first().LedgerID
        if Parties.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        ).exists():
            CustomerName = (
                Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
                )
                .first()
                .PartyName
            )

        return CustomerName

    # def get_VoucherNo(self, instances):
    #     CompanyID = self.context.get("CompanyID")
    #     BranchID = instances.BranchID
    #     CustomerName = ""
    #     SalesMasterID = instances.SalesMasterID
    #     VoucherNo = SalesMaster.objects.get(CompanyID=CompanyID,BranchID=BranchID,SalesMasterID=SalesMasterID).VoucherNo

    #     return VoucherNo

    # def get_Date(self, instances):
    #     CompanyID = self.context.get("CompanyID")
    #     BranchID = instances.BranchID
    #     CustomerName = ""
    #     SalesMasterID = instances.SalesMasterID
    #     Date = SalesMaster.objects.get(CompanyID=CompanyID,BranchID=BranchID,SalesMasterID=SalesMasterID).Date

    #     return str(Date)

    # def get_GrandTotal(self, instances):
    #     CompanyID = self.context.get("CompanyID")
    #     BranchID = instances.BranchID
    #     CustomerName = ""
    #     SalesMasterID = instances.SalesMasterID
    #     GrandTotal = SalesMaster.objects.get(CompanyID=CompanyID,BranchID=BranchID,SalesMasterID=SalesMasterID).GrandTotal

    #     return converted_float(GrandTotal)

    def get_Customer_GST_No(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        Customer_GST_No = ""
        SalesMasterID = instances.SalesMasterID
        LedgerID = instances.LedgerID
        # LedgerID = SalesMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,SalesMasterID=SalesMasterID).first().LedgerID
        if Parties.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        ).exists():
            Customer_GST_No = (
                Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
                )
                .first()
                .GSTNumber
            )

        return Customer_GST_No

    def get_PlaceOfSupply(self, instances):
        CompanyID = self.context.get("CompanyID")
        SalesMasterID = instances.SalesMasterID
        BranchID = instances.BranchID
        LedgerID = instances.LedgerID
        # LedgerID = SalesMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,SalesMasterID=SalesMasterID).first().LedgerID
        BranchID = instances.BranchID
        State_of_Supply = instances.State_of_Supply
        PlaceOfSupply = "Kerala"
        # if SalesMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,SalesMasterID=SalesMasterID).exists():
        #     State_of_Supply = SalesMaster.objects.get(CompanyID=CompanyID,BranchID=BranchID,SalesMasterID=SalesMasterID).State_of_Supply
        if not State_of_Supply:
            if Parties.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).exists():
                State_of_Supply = (
                    Parties.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
                    )
                    .first()
                    .State
                )
        if State_of_Supply:
            if State.objects.filter(id=State_of_Supply).exists():
                PlaceOfSupply = State.objects.get(id=State_of_Supply).Name
        return PlaceOfSupply

    def get_ApplicableTaxRate(self, instances):
        CompanyID = self.context.get("CompanyID")
        SalesMasterID = instances.SalesMasterID
        ApplicableTaxRate = ""

        return ApplicableTaxRate

    def get_ReverseCharge(self, instances):
        CompanyID = self.context.get("CompanyID")
        SalesMasterID = instances.SalesMasterID
        ReverseCharge = "N"

        return ReverseCharge

    def get_InvoiceType(self, instances):
        CompanyID = self.context.get("CompanyID")
        SalesMasterID = instances.SalesMasterID
        BranchID = instances.BranchID
        LedgerID = instances.LedgerID
        try:
            GST_Treatment = instances.GST_Treatment
        except:
            GST_Treatment = ""

        try:
            VAT_Treatment = instances.VAT_Treatment
        except:
            VAT_Treatment = ""
        InvoiceType = GST_Treatment
        if instances.VATAmount > 0:
            if not VAT_Treatment:
                if Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
                ).exists():
                    InvoiceType = (
                        Parties.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
                        )
                        .first()
                        .VAT_Treatment
                    )
            InvoiceType = get_vatTreatment(InvoiceType)
        else:
            if not GST_Treatment:
                if Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
                ).exists():
                    InvoiceType = (
                        Parties.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
                        )
                        .first()
                        .GST_Treatment
                    )
            InvoiceType = get_B2b_gstTreatment(InvoiceType)
        return InvoiceType

    def get_E_Commerce_GSTIN(self, instances):
        CompanyID = self.context.get("CompanyID")
        SalesMasterID = instances.SalesMasterID
        E_Commerce_GSTIN = ""
        return E_Commerce_GSTIN

    def get_CESS_amount(self, instances):
        CompanyID = self.context.get("CompanyID")
        SalesMasterID = instances.SalesMasterID
        CESS_amount = 0
        return CESS_amount


class GST_CDNR_Serializer(serializers.ModelSerializer):
    CustomerName = serializers.SerializerMethodField()
    Customer_GST_No = serializers.SerializerMethodField()
    PlaceOfSupply = serializers.SerializerMethodField()
    ApplicableTaxRate = serializers.SerializerMethodField()
    ReverseCharge = serializers.SerializerMethodField()
    InvoiceType = serializers.SerializerMethodField()
    E_Commerce_GSTIN = serializers.SerializerMethodField()
    CESS_amount = serializers.SerializerMethodField()
    Type = serializers.SerializerMethodField()
    DocumentType = serializers.SerializerMethodField()
    UR_Type = serializers.SerializerMethodField()
    RefferenceBillDate = serializers.SerializerMethodField()
    VoucherDate = serializers.SerializerMethodField()

    class Meta:
        model = SalesReturnMaster

        fields = (
            "Customer_GST_No",
            "CustomerName",
            "VoucherNo",
            "VoucherDate",
            "GrandTotal",
            "PlaceOfSupply",
            "ApplicableTaxRate",
            "ReverseCharge",
            "InvoiceType",
            "E_Commerce_GSTIN",
            "CESS_amount",
            "SalesReturnMasterID",
            "Type",
            "RefferenceBillNo",
            "RefferenceBillDate",
            "DocumentType",
            "UR_Type",
            "TaxType",
        )

    def get_RefferenceBillDate(self, instances):
        Date = instances.RefferenceBillDate
        # date_object = datetime.strptime(Date, "%Y-%m-%d")
        Date = Date.strftime("%d-%b-%y")
        return Date

    def get_VoucherDate(self, instances):
        Date = instances.VoucherDate
        # date_object = datetime.strptime(Date, "%Y-%m-%d")
        Date = Date.strftime("%d-%b-%y")
        return Date

    def get_UR_Type(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        UR_Type = "B2CS"

        return UR_Type

    def get_Type(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        Type = "OE"

        return Type

    def get_DocumentType(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        DocumentType = "C"
        return DocumentType

    def get_CustomerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        CustomerName = ""
        SalesReturnMasterID = instances.SalesReturnMasterID
        LedgerID = instances.LedgerID
        if Parties.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        ).exists():
            CustomerName = (
                Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
                )
                .first()
                .PartyName
            )

        return CustomerName

    def get_Customer_GST_No(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        Customer_GST_No = ""
        SalesReturnMasterID = instances.SalesReturnMasterID
        LedgerID = instances.LedgerID
        if Parties.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        ).exists():
            Customer_GST_No = (
                Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
                )
                .first()
                .GSTNumber
            )

        return Customer_GST_No

    def get_PlaceOfSupply(self, instances):
        CompanyID = self.context.get("CompanyID")
        SalesReturnMasterID = instances.SalesReturnMasterID
        BranchID = instances.BranchID
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        try:
            State_of_Supply = instances.State_of_Supply
        except:
            State_of_Supply = None
        company = CompanySettings.objects.get(id=CompanyID)
        PlaceOfSupply = company.State.Name
        if not State_of_Supply:
            if Parties.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).exists():
                State_of_Supply = (
                    Parties.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
                    )
                    .first()
                    .State
                )
        if State_of_Supply:
            if State.objects.filter(id=State_of_Supply).exists():
                PlaceOfSupply = State.objects.get(id=State_of_Supply).Name
        return PlaceOfSupply

    def get_ApplicableTaxRate(self, instances):
        CompanyID = self.context.get("CompanyID")
        SalesReturnMasterID = instances.SalesReturnMasterID
        ApplicableTaxRate = ""

        return ApplicableTaxRate

    def get_ReverseCharge(self, instances):
        CompanyID = self.context.get("CompanyID")
        SalesReturnMasterID = instances.SalesReturnMasterID
        ReverseCharge = "N"

        return ReverseCharge

    def get_InvoiceType(self, instances):
        CompanyID = self.context.get("CompanyID")
        # SalesMasterID = instances.SalesMasterID
        BranchID = instances.BranchID
        LedgerID = instances.LedgerID
        try:
            GST_Treatment = instances.GST_Treatment
        except:
            GST_Treatment = ""

        try:
            VAT_Treatment = instances.VAT_Treatment
        except:
            VAT_Treatment = ""
        # LedgerID = SalesMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,SalesMasterID=SalesMasterID).first().LedgerID
        InvoiceType = ""
        # if SalesMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,SalesMasterID=SalesMasterID).exists():
        #     InvoiceType = SalesMaster.objects.get(CompanyID=CompanyID,BranchID=BranchID,SalesMasterID=SalesMasterID).GST_Treatment
        if instances.VATAmount > 0:
            if not VAT_Treatment:
                if Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
                ).exists():
                    InvoiceType = (
                        Parties.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
                        )
                        .first()
                        .VAT_Treatment
                    )
            InvoiceType = get_vatTreatment(InvoiceType)
        else:
            if not GST_Treatment:
                if Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
                ).exists():
                    InvoiceType = (
                        Parties.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
                        )
                        .first()
                        .GST_Treatment
                    )
            InvoiceType = get_gstTreatment(InvoiceType)
        return InvoiceType

    def get_E_Commerce_GSTIN(self, instances):
        CompanyID = self.context.get("CompanyID")
        SalesReturnMasterID = instances.SalesReturnMasterID
        E_Commerce_GSTIN = ""
        return E_Commerce_GSTIN

    def get_CESS_amount(self, instances):
        CompanyID = self.context.get("CompanyID")
        SalesReturnMasterID = instances.SalesReturnMasterID
        CESS_amount = 0
        return CESS_amount


def get_gstTreatment(InvoiceType):
    GST_Treatment = ""
    if InvoiceType:
        if InvoiceType == "0":
            GST_Treatment = "Registered Business - Regular"
        elif InvoiceType == "1":
            GST_Treatment = "Registered Business - Composition"
        elif InvoiceType == "2":
            GST_Treatment = "Unregistered Business"
        elif InvoiceType == "3":
            GST_Treatment = "Consumer"
        elif InvoiceType == "4":
            GST_Treatment = "Overseas"
        elif InvoiceType == "5":
            GST_Treatment = "Special Economic Zone"
        elif InvoiceType == "6":
            GST_Treatment = "Deemed Export"
        return GST_Treatment
    else:
        return GST_Treatment


def get_B2b_gstTreatment(InvoiceType):
    GST_Treatment = ""
    if InvoiceType:
        if InvoiceType == "0":
            GST_Treatment = "Regular"
        elif InvoiceType == "1":
            GST_Treatment = "Regular"
        elif InvoiceType == "2":
            GST_Treatment = "Unregistered Business"
        elif InvoiceType == "3":
            GST_Treatment = "Consumer"
        elif InvoiceType == "4":
            GST_Treatment = "Overseas"
        elif InvoiceType == "5":
            GST_Treatment = "SEZ supplies without payment"
        elif InvoiceType == "6":
            GST_Treatment = "Deemed Exp"
        return GST_Treatment
    else:
        return GST_Treatment


def get_vatTreatment(InvoiceType):
    VAT_Treatment = ""
    if InvoiceType:
        if InvoiceType == "0":
            VAT_Treatment = "Business to Business(B2B)"
        elif InvoiceType == "1":
            VAT_Treatment = "Business to Customer(B2C)"
        return VAT_Treatment
    else:
        return VAT_Treatment


class QRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QrCode
        fields = ("qr_code",)


class SalesMobileReportSerializer(serializers.ModelSerializer):
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
    SalesAccountName = serializers.SerializerMethodField()
    WareHouseName = serializers.SerializerMethodField()
    CardTypeName = serializers.SerializerMethodField()
    DetailID = serializers.SerializerMethodField()
    BillDiscPercent = serializers.SerializerMethodField()
    BillDiscAmt = serializers.SerializerMethodField()
    CashSales = serializers.SerializerMethodField()
    BankSales = serializers.SerializerMethodField()
    CreditSales = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    LedgerBalance = serializers.SerializerMethodField()
    AccountGroupUnder = serializers.SerializerMethodField()
    OldLedgerBalance = serializers.SerializerMethodField()
    Balance = serializers.SerializerMethodField()
    CashName = serializers.SerializerMethodField()
    BankName = serializers.SerializerMethodField()
    Country_of_Supply_name = serializers.SerializerMethodField()
    State_of_Supply_name = serializers.SerializerMethodField()
    Country_of_Supply = serializers.SerializerMethodField()
    State_of_Supply = serializers.SerializerMethodField()

    class Meta:
        model = SalesMaster
        fields = (
            "id",
            "SalesMasterID",
            "BranchID",
            "Action",
            "VoucherNo",
            "Date",
            "CashID",
            "BankID",
            "CashName",
            "BankName",
            "CreditPeriod",
            "LedgerID",
            "LedgerName",
            "LedgerBalance",
            "OldLedgerBalance",
            "AccountGroupUnder",
            "GST_Treatment",
            "VAT_Treatment",
            "PriceCategoryID",
            "EmployeeID",
            "SalesAccount",
            "SalesAccountName",
            "CustomerName",
            "Address1",
            "Address2",
            "Address3",
            "Notes",
            "FinacialYearID",
            "TotalGrossAmt",
            "AddlDiscPercent",
            "AddlDiscAmt",
            "TotalDiscount",
            "TotalTax",
            "Country_of_Supply",
            "State_of_Supply",
            "NetTotal",
            "AdditionalCost",
            "GrandTotal",
            "RoundOff",
            "CashReceived",
            "CashAmount",
            "BankAmount",
            "WarehouseID",
            "WareHouseName",
            "TableID",
            "SeatNumber",
            "NoOfGuests",
            "INOUT",
            "TokenNumber",
            "CardTypeID",
            "CardTypeName",
            "CardNumber",
            "IsActive",
            "IsPosted",
            "SalesType",
            "CreatedDate",
            "UpdatedDate",
            "CreatedUserID",
            "TaxID",
            "TaxType",
            "BillDiscPercent",
            "BillDiscAmt",
            "VATAmount",
            "SGSTAmount",
            "CGSTAmount",
            "IGSTAmount",
            "Country_of_Supply_name",
            "State_of_Supply_name",
            "TAX1Amount",
            "TAX2Amount",
            "TAX3Amount",
            "Balance",
            "TransactionTypeID",
            "DetailID",
            "CashSales",
            "BankSales",
            "CreditSales",
        )

    def get_Country_of_Supply(self, instances):
        CompanyID = self.context.get("CompanyID")
        Country_of_Supply = instances.Country_of_Supply
        return str(Country_of_Supply)

    def get_State_of_Supply(self, instances):
        CompanyID = self.context.get("CompanyID")
        State_of_Supply = instances.State_of_Supply
        return str(State_of_Supply)

    def get_Country_of_Supply_name(self, instances):
        CompanyID = self.context.get("CompanyID")
        Country_of_Supply = instances.Country_of_Supply
        Country_of_Supply_name = ""
        if Country_of_Supply:
            if Country.objects.filter(id=Country_of_Supply).exists():
                Country_of_Supply_name = Country.objects.get(
                    id=Country_of_Supply
                ).Country_Name
        return Country_of_Supply_name

    def get_State_of_Supply_name(self, instances):
        CompanyID = self.context.get("CompanyID")
        State_of_Supply = instances.State_of_Supply
        State_of_Supply_name = ""
        if State_of_Supply:
            if State.objects.filter(id=State_of_Supply).exists():
                State_of_Supply_name = State.objects.get(id=State_of_Supply).Name
        return State_of_Supply_name

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID
        ).exists():
            ledger = AccountLedger.objects.get(CompanyID=CompanyID, LedgerID=LedgerID)

            LedgerName = ledger.LedgerName
        else:
            LedgerName = ""

        return LedgerName

    def get_CashName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.CashID
        BranchID = instances.BranchID

        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID
        ).exists():
            ledger = AccountLedger.objects.get(CompanyID=CompanyID, LedgerID=LedgerID)
            CashName = ledger.LedgerName
        else:
            CashName = ""
        return CashName

    def get_BankName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.BankID
        BranchID = instances.BranchID

        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID
        ).exists():
            ledger = AccountLedger.objects.get(CompanyID=CompanyID, LedgerID=LedgerID)
            BankName = ledger.LedgerName
        else:
            BankName = ""
        return BankName

    def get_OldLedgerBalance(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        OldLedgerBalance = instances.OldLedgerBalance

        OldLedgerBalance = round(OldLedgerBalance, PriceRounding)

        return converted_float(OldLedgerBalance)

    def get_AccountGroupUnder(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        AccountGroupUnder = 0

        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID
        ).exists():
            AccountGroupUnder = AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID
            ).AccountGroupUnder

        return AccountGroupUnder

    def get_LedgerBalance(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        ledger_instances = LedgerPosting.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        )
        Balance = 0
        TotalDebit = 0
        TotalCredit = 0

        for i in ledger_instances:
            TotalDebit += i.Debit
            TotalCredit += i.Credit

        LedgerBalance = converted_float(TotalDebit) - converted_float(TotalCredit)

        return LedgerBalance

    def get_id(self, instances):
        id = instances.id

        return str(id)

    def get_CashSales(self, instances):
        CompanyID = self.context.get("CompanyID")
        FromDate = self.context.get("FromDate")
        ToDate = self.context.get("ToDate")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        TotalDebit = 0
        TotalCredit = 0
        account_instance = AccountLedger.objects.filter(
            CompanyID=CompanyID, AccountGroupUnder=9
        )
        print(LedgerID, "ledger_ids", "cash_salessssss", account_instance)
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, AccountGroupUnder=9
        ).exists():
            account_instance = AccountLedger.objects.filter(
                CompanyID=CompanyID, AccountGroupUnder=9
            )
            ledger_ids = account_instance.values_list("LedgerID", flat=True)
            print(ledger_ids, "cash_salessssss")
            if LedgerPosting.objects.filter(
                CompanyID=CompanyID,
                LedgerID__in=ledger_ids,
                Date__gte=FromDate,
                Date__lte=ToDate,
                VoucherType="SI",
                VoucherMasterID=instances.SalesMasterID,
            ).exists():
                ledger_ins = LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    LedgerID__in=ledger_ids,
                    Date__gte=FromDate,
                    Date__lte=ToDate,
                    VoucherType="SI",
                    VoucherMasterID=instances.SalesMasterID,
                )
                for i in ledger_ins:
                    print(i.id, "forloop")
                    TotalDebit += converted_float(i.Debit)
                    TotalCredit += converted_float(i.Credit)

        CashSales = converted_float(TotalDebit) - converted_float(TotalCredit)
        return CashSales

    def get_BankSales(self, instances):
        CompanyID = self.context.get("CompanyID")
        FromDate = self.context.get("FromDate")
        ToDate = self.context.get("ToDate")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        TotalDebit = 0
        TotalCredit = 0
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, AccountGroupUnder=8
        ).exists():
            account_instance = AccountLedger.objects.filter(
                CompanyID=CompanyID, AccountGroupUnder=8
            )
            ledger_ids = account_instance.values_list("LedgerID", flat=True)
            print(ledger_ids, "bank_salessssss")
            if LedgerPosting.objects.filter(
                CompanyID=CompanyID,
                LedgerID__in=ledger_ids,
                Date__gte=FromDate,
                Date__lte=ToDate,
                VoucherType="SI",
                VoucherMasterID=instances.SalesMasterID,
            ).exists():
                ledger_ins = LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    LedgerID__in=ledger_ids,
                    Date__gte=FromDate,
                    Date__lte=ToDate,
                    VoucherType="SI",
                    VoucherMasterID=instances.SalesMasterID,
                )
                for i in ledger_ins:
                    TotalDebit += converted_float(i.Debit)
                    TotalCredit += converted_float(i.Credit)

        BankSales = converted_float(TotalDebit) - converted_float(TotalCredit)
        return BankSales

    def get_CreditSales(self, instances):
        CompanyID = self.context.get("CompanyID")
        FromDate = self.context.get("FromDate")
        ToDate = self.context.get("ToDate")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        GrandTotal = 0
        CreditSales = 0
        TotalDebit = 0
        TotalCredit = 0

        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=[8, 9]
        ).exists():
            account_instance = AccountLedger.objects.filter(
                CompanyID=CompanyID, AccountGroupUnder__in=[8, 9]
            )
            ledger_ids = account_instance.values_list("LedgerID", flat=True)
            if LedgerPosting.objects.filter(
                CompanyID=CompanyID,
                LedgerID__in=ledger_ids,
                Date__gte=FromDate,
                Date__lte=ToDate,
                VoucherType="SI",
                VoucherMasterID=instances.SalesMasterID,
            ).exists():
                TotalDebit = LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    LedgerID__in=ledger_ids,
                    Date__gte=FromDate,
                    Date__lte=ToDate,
                    VoucherType="SI",
                    VoucherMasterID=instances.SalesMasterID,
                ).aggregate(Sum("Debit"))["Debit__sum"]
                TotalCredit = LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    LedgerID__in=ledger_ids,
                    Date__gte=FromDate,
                    Date__lte=ToDate,
                    VoucherType="SI",
                    VoucherMasterID=instances.SalesMasterID,
                ).aggregate(Sum("Credit"))["Credit__sum"]
                # for i in ledger_ins:
                #     TotalDebit += converted_float(i.Debit)
                #     TotalCredit += converted_float(i.Credit)

            CreditSales = converted_float(TotalDebit) - converted_float(TotalCredit)
            GrandTotal = instances.GrandTotal
            print(
                GrandTotal,
                CreditSales,
                "converted_float(IFFFFFFFF) - converted_float(CreditSales)",
            )
            CreditSales = converted_float(GrandTotal) - converted_float(CreditSales)
        else:
            print(instances.SalesMasterID, "ELSE............")
            account_instance = AccountLedger.objects.filter(CompanyID=CompanyID)
            ledger_ids = account_instance.values_list("LedgerID", flat=True)
            if LedgerPosting.objects.filter(
                CompanyID=CompanyID,
                LedgerID=LedgerID,
                Date__gte=FromDate,
                Date__lte=ToDate,
                VoucherType="SI",
                VoucherMasterID=instances.SalesMasterID,
            ).exists():
                TotalDebit = LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    LedgerID=LedgerID,
                    Date__gte=FromDate,
                    Date__lte=ToDate,
                    VoucherType="SI",
                    VoucherMasterID=instances.SalesMasterID,
                ).aggregate(Sum("Debit"))["Debit__sum"]
                TotalCredit = LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    LedgerID=LedgerID,
                    Date__gte=FromDate,
                    Date__lte=ToDate,
                    VoucherType="SI",
                    VoucherMasterID=instances.SalesMasterID,
                ).aggregate(Sum("Credit"))["Credit__sum"]
                # for i in ledger_ins:
                #     TotalDebit += converted_float(i.Debit)
                #     TotalCredit += converted_float(i.Credit)
                #     print(i.pk, "************************************")

            CreditSales = converted_float(TotalDebit) - converted_float(TotalCredit)
            GrandTotal = instances.GrandTotal
            print(
                TotalDebit,
                TotalCredit,
                CreditSales,
                "converted_float(ELSEEEEEEEEEE) - converted_float(CreditSales)",
            )

        return CreditSales

    def get_CardTypeName(self, instances):
        CompanyID = self.context.get("CompanyID")
        TransactionTypesID = instances.CardTypeID
        BranchID = instances.BranchID

        if TransactionTypes.objects.filter(
            CompanyID=CompanyID,
            TransactionTypesID=TransactionTypesID,
            BranchID=BranchID,
        ).exists():

            transactionType = TransactionTypes.objects.get(
                CompanyID=CompanyID,
                TransactionTypesID=TransactionTypesID,
                BranchID=BranchID,
            )
            Name = transactionType.Name

        else:
            Name = ""

        CardTypeName = Name

        return CardTypeName

    def get_DetailID(self, instances):

        return ""

    def get_Balance(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        Balance = instances.Balance

        Balance = round(Balance, PriceRounding)

        return converted_float(Balance)

    def get_WareHouseName(self, instances):
        CompanyID = self.context.get("CompanyID")

        WarehouseID = instances.WarehouseID
        BranchID = instances.BranchID

        wareHouse = Warehouse.objects.get(CompanyID=CompanyID, WarehouseID=WarehouseID)

        WareHouseName = wareHouse.WarehouseName

        return WareHouseName

    def get_SalesAccountName(self, instances):
        CompanyID = self.context.get("CompanyID")
        SalesAccount = instances.SalesAccount
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(CompanyID=CompanyID, LedgerID=SalesAccount)

        SalesAccountName = ledger.LedgerName

        return SalesAccountName

    def get_TotalGrossAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalGrossAmt = instances.TotalGrossAmt

        TotalGrossAmt = round(TotalGrossAmt, PriceRounding)

        return converted_float(TotalGrossAmt)

    def get_AddlDiscPercent(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        AddlDiscPercent = instances.AddlDiscPercent

        AddlDiscPercent = round(AddlDiscPercent, PriceRounding)

        return converted_float(AddlDiscPercent)

    def get_AddlDiscAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        AddlDiscAmt = instances.AddlDiscAmt

        AddlDiscAmt = round(AddlDiscAmt, PriceRounding)

        return converted_float(AddlDiscAmt)

    def get_TotalDiscount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalDiscount = instances.TotalDiscount

        TotalDiscount = round(TotalDiscount, PriceRounding)

        return converted_float(TotalDiscount)

    def get_TotalTax(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalTax = instances.TotalTax

        TotalTax = round(TotalTax, PriceRounding)

        return converted_float(TotalTax)

    def get_BillDiscPercent(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscPercent = instances.BillDiscPercent

        BillDiscPercent = round(BillDiscPercent, PriceRounding)

        return converted_float(BillDiscPercent)

    def get_BillDiscAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscAmt = instances.BillDiscAmt

        BillDiscAmt = round(BillDiscAmt, PriceRounding)

        return converted_float(BillDiscAmt)

    def get_NetTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        NetTotal = instances.NetTotal

        NetTotal = round(NetTotal, PriceRounding)

        return converted_float(NetTotal)

    def get_AdditionalCost(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        AdditionalCost = instances.AdditionalCost

        AdditionalCost = round(AdditionalCost, PriceRounding)

        return converted_float(AdditionalCost)

    def get_GrandTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        GrandTotal = instances.GrandTotal

        GrandTotal = round(GrandTotal, PriceRounding)

        return converted_float(GrandTotal)

    def get_RoundOff(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        RoundOff = instances.RoundOff

        RoundOff = round(RoundOff, PriceRounding)

        return converted_float(RoundOff)

    def get_CashReceived(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CashReceived = instances.CashReceived

        CashReceived = round(CashReceived, PriceRounding)

        return converted_float(CashReceived)

    def get_CashAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CashAmount = instances.CashAmount

        CashAmount = round(CashAmount, PriceRounding)

        return converted_float(CashAmount)

    def get_BankAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BankAmount = instances.BankAmount

        BankAmount = round(BankAmount, PriceRounding)

        return converted_float(BankAmount)


class SalesHistorySerializer(serializers.ModelSerializer):
    LedgerID = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    VoucherNo = serializers.SerializerMethodField()
    Date = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()

    class Meta:
        model = SalesDetails
        fields = (
            "id",
            "LedgerName",
            "LedgerID",
            "VoucherNo",
            "Date",
            "Qty",
            "UnitName",
            "UnitPrice",
            "ProductID",
        )

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = self.context.get("LedgerID")
        LedgerName = ""
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID
        ).exists():
            LedgerName = (
                AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID)
                .first()
                .LedgerName
            )
        return LedgerName

    def get_LedgerID(self, instances):
        LedgerID = self.context.get("LedgerID")
        return LedgerID

    def get_VoucherNo(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        SalesMasterID = instances.SalesMasterID
        VoucherNo = ""
        if SalesMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, SalesMasterID=SalesMasterID
        ).exists():
            VoucherNo = (
                SalesMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, SalesMasterID=SalesMasterID
                )
                .first()
                .VoucherNo
            )
        return VoucherNo

    def get_Date(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        SalesMasterID = instances.SalesMasterID
        Date = ""
        if SalesMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, SalesMasterID=SalesMasterID
        ).exists():
            Date = (
                SalesMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, SalesMasterID=SalesMasterID
                )
                .first()
                .Date
            )
        return Date

    def get_UnitName(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        PriceListID = instances.PriceListID
        UnitName = ""
        if PriceList.objects.filter(
            CompanyID=CompanyID, PriceListID=PriceListID
        ).exists():
            UnitID = (
                PriceList.objects.filter(CompanyID=CompanyID, PriceListID=PriceListID)
                .first()
                .UnitID
            )
            if Unit.objects.filter(
                CompanyID=CompanyID, UnitID=UnitID, BranchID=BranchID
            ).exists():
                UnitName = (
                    Unit.objects.filter(
                        CompanyID=CompanyID, UnitID=UnitID, BranchID=BranchID
                    )
                    .first()
                    .UnitName
                )
        return UnitName


class SalesSingleSerializer(serializers.ModelSerializer):
    SalesDetails = serializers.SerializerMethodField()
    TotalGrossAmt = serializers.SerializerMethodField()
    TotalDiscount = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    NetTotal = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    RoundOff = serializers.SerializerMethodField()
    CashReceived = serializers.SerializerMethodField()
    CashAmount = serializers.SerializerMethodField()
    BankAmount = serializers.SerializerMethodField()
    BillDiscPercent = serializers.SerializerMethodField()
    BillDiscAmt = serializers.SerializerMethodField()
    is_customer = serializers.SerializerMethodField()
    GSTNumber = serializers.SerializerMethodField()
    GST_Treatment = serializers.SerializerMethodField()
    VAT_Treatment = serializers.SerializerMethodField()
    # =====
    Tax_no = serializers.SerializerMethodField()
    Mobile = serializers.SerializerMethodField()
    ShippingAddress = serializers.SerializerMethodField()
    ShippingAddressList = serializers.SerializerMethodField()
    ProductList = serializers.SerializerMethodField()

    class Meta:
        model = SalesMaster

        fields = (
            "id",
            "Tax_no",
            "Mobile",
            "ShippingCharge",
            "shipping_tax_amount",
            "TaxTypeID",
            "SAC",
            "SalesTax",
            "TotalTaxableAmount",
            "VoucherNo",
            "Date",
            "LedgerID",
            "CashID",
            "BankID",
            "Country_of_Supply",
            "State_of_Supply",
            "VAT_Treatment",
            "PriceCategoryID",
            "EmployeeID",
            "SalesAccount",
            "CustomerName",
            "Address1",
            "ProductList",
            "Notes",
            "TotalGrossAmt",
            "TotalDiscount",
            "TotalTax",
            "GST_Treatment",
            "GSTNumber",
            "ShippingAddress",
            "NetTotal",
            "GrandTotal",
            "RoundOff",
            "CashReceived",
            "CashAmount",
            "BankAmount",
            "WarehouseID",
            "CardTypeID",
            "CardNumber",
            "IsActive",
            "TaxID",
            "TaxType",
            "BillDiscPercent",
            "BillDiscAmt",
            "VATAmount",
            "SGSTAmount",
            "CGSTAmount",
            "IGSTAmount",
            "ShippingAddressList",
            "Balance",
            "TransactionTypeID",
            "is_customer",
            "SalesDetails",
        )

    def get_ShippingAddress(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        ShippingAddress = instances.ShippingAddress
        if ShippingAddress:
            ShippingAddress = ShippingAddress.id
        else:
            ShippingAddress = None

        return str(ShippingAddress)

    def get_ShippingAddressList(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        ShippingAddressList = []
        if UserAdrress.objects.filter(
            CompanyID=CompanyID, Branch__BranchID=BranchID, Party__LedgerID=LedgerID
        ).exists():
            shipping_instances = UserAdrress.objects.filter(
                CompanyID=CompanyID, Branch__BranchID=BranchID, Party__LedgerID=LedgerID
            )
            serialized = ShippingAddressListSerializer(
                shipping_instances, many=True, context={"CompanyID": CompanyID}
            )
            ShippingAddressList = serialized.data

        return ShippingAddressList

    def get_ProductList(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        SalesMasterID = instances.SalesMasterID
        sales_details = SalesDetails.objects.filter(
            CompanyID=CompanyID, SalesMasterID=SalesMasterID, BranchID=BranchID
        )

        product_ids = sales_details.values_list("ProductID", flat=True)
        produc_instances = Product.objects.filter(
            CompanyID=CompanyID, ProductID__in=product_ids
        )
        ProductList = []
        for p in produc_instances:
            ProductList.append(
                {
                    "id": p.id,
                    "product_id": p.id,
                    "ProductCode": p.ProductCode,
                    "ProductName": p.ProductName,
                    "ProductID": p.ProductID,
                }
            )

        return ProductList

    def get_GST_Treatment(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        GST_Treatment = instances.GST_Treatment
        if not GST_Treatment:
            GST_Treatment = ""
            if Parties.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).exists():
                pary_ins = Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
                ).first()
                GST_Treatment = pary_ins.GST_Treatment
        return str(GST_Treatment)

    def get_VAT_Treatment(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        VAT_Treatment = instances.VAT_Treatment
        if not VAT_Treatment:
            VAT_Treatment = ""
            if Parties.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).exists():
                pary_ins = Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
                ).first()
                VAT_Treatment = pary_ins.VAT_Treatment
        return str(VAT_Treatment)

    def get_Tax_no(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        is_gst = get_GeneralSettings(CompanyID, BranchID, "GST")
        is_vat = get_GeneralSettings(CompanyID, BranchID, "VAT")
        Tax_no = ""
        if Parties.objects.filter(
            LedgerID=instances.LedgerID, CompanyID=CompanyID
        ).exists():
            party = Parties.objects.get(
                LedgerID=instances.LedgerID, CompanyID=CompanyID
            )
            if is_vat:
                Tax_no = party.VATNumber
            if is_gst:
                Tax_no = party.GSTNumber
        return str(Tax_no)

    def get_Mobile(self, instances):

        CompanyID = self.context.get("CompanyID")
        Mobile = ""
        if Parties.objects.filter(
            LedgerID=instances.LedgerID, CompanyID=CompanyID
        ).exists():
            Mobile = Parties.objects.get(
                LedgerID=instances.LedgerID, CompanyID=CompanyID
            ).Mobile

        return str(Mobile)

    def get_GSTNumber(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        GSTNumber = ""
        if Parties.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        ).exists():
            pary_ins = Parties.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).first()
            GSTNumber = pary_ins.GSTNumber
        return str(GSTNumber)

    def get_VATNumber(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        VATNumber = ""
        if Parties.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        ).exists():
            pary_ins = Parties.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            ).first()
            VATNumber = pary_ins.VATNumber
        return str(VATNumber)

    def get_is_customer(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        is_customer = False
        groups = [10, 29]
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=groups
        ).exists():
            is_customer = True

        return is_customer

    def get_SalesDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        SalesMasterID = instances.SalesMasterID
        WarehouseID = instances.WarehouseID
        BranchID = instances.BranchID
        sales_details = SalesDetails.objects.filter(
            CompanyID=CompanyID, SalesMasterID=SalesMasterID, BranchID=BranchID
        ).order_by("SalesDetailsID")
        serialized = SalesDetailsRestSerializer(
            sales_details,
            many=True,
            context={
                "CompanyID": CompanyID,
                "PriceRounding": PriceRounding,
                "WarehouseID": WarehouseID,
                "BranchID": BranchID,
            },
        )

        return serialized.data

    def get_TotalGrossAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalGrossAmt = instances.TotalGrossAmt

        # TotalGrossAmt = round(TotalGrossAmt, PriceRounding)

        return converted_float(TotalGrossAmt)

    def get_TotalDiscount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalDiscount = instances.TotalDiscount

        # TotalDiscount = round(TotalDiscount, PriceRounding)

        return converted_float(TotalDiscount)

    def get_TotalTax(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalTax = instances.TotalTax

        # TotalTax = round(TotalTax, PriceRounding)

        return converted_float(TotalTax)

    def get_BillDiscPercent(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscPercent = instances.BillDiscPercent

        # BillDiscPercent = round(BillDiscPercent, PriceRounding)

        return converted_float(BillDiscPercent)

    def get_BillDiscAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscAmt = instances.BillDiscAmt

        # BillDiscAmt = round(BillDiscAmt, PriceRounding)

        return converted_float(BillDiscAmt)

    def get_NetTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        NetTotal = instances.NetTotal
        # NetTotal = round(NetTotal, PriceRounding)
        return converted_float(NetTotal)

    def get_GrandTotal(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        GrandTotal = instances.GrandTotal

        # GrandTotal = round(GrandTotal, PriceRounding)

        return converted_float(GrandTotal)

    def get_RoundOff(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        RoundOff = instances.RoundOff

        # RoundOff = round(RoundOff, PriceRounding)

        return converted_float(RoundOff)

    def get_CashReceived(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CashReceived = instances.CashReceived

        # CashReceived = round(CashReceived, PriceRounding)

        return converted_float(CashReceived)

    def get_CashAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        CashAmount = instances.CashAmount

        # CashAmount = round(CashAmount, PriceRounding)

        return converted_float(CashAmount)

    def get_BankAmount(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BankAmount = instances.BankAmount

        # BankAmount = round(BankAmount, PriceRounding)

        return converted_float(BankAmount)


class SalesSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalesMaster

        fields = (
            "id",
            "VoucherNo",
            "Date",
            "GrandTotal"
        )
        
class SalesReturnSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SalesReturnMaster

        fields = (
            "id",
            "VoucherNo",
            "VoucherDate",
            "GrandTotal"
        )
        
class PurchaseSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PurchaseMaster

        fields = (
            "id",
            "VoucherNo",
            "Date",
            "GrandTotal"
        )
        
class PurchaseReturnSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PurchaseReturnMaster

        fields = (
            "id",
            "VoucherNo",
            "VoucherDate",
            "GrandTotal"
        )
        

class PaymentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PaymentMaster

        fields = (
            "id",
            "VoucherNo",
            "Date",
            "TotalAmount"
        )
        

class ReceiptSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReceiptMaster

        fields = (
            "id",
            "VoucherNo",
            "Date",
            "TotalAmount"
        )
