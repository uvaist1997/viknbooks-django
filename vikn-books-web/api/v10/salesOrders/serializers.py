from rest_framework import serializers
from django.db.models import F, Q, Sum
from api.v10.priceLists.serializers import PriceListRestSerializer
from api.v10.sales.serializers import (
    SerialNumberSerializer,
    ShippingAddressListSerializer,
)
from brands.models import (
    AccountLedger,
    LedgerPosting,
    Parties,
    PriceList,
    Product,
    ProductBarcode,
    SalesOrderDetails,
    SalesOrderMaster,
    SerialNumbers,
    State,
    TaxCategory,
    Unit,
    UserAdrress,
    Employee,
)
from main.functions import converted_float, get_ProductStock


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


class SalesOrderMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrderMaster
        fields = (
            "id",
            "BranchID",
            "Action",
            "VoucherNo",
            "Date",
            "LedgerID",
            "PriceCategoryID",
            "CustomerName",
            "Address1",
            "Address2",
            "Notes",
            "FinacialYearID",
            "TotalTax",
            "NetTotal",
            "BillDiscount",
            "GrandTotal",
            "RoundOff",
            "IsActive",
            "IsInvoiced",
            "CreatedUserID",
        )


def GST_finalList_fun(instance, Detail, type_tx, PriceRounding, TransactionType):
    shipping_tax_amount = 0
    half_shipping_tax_amount = 0
    if TransactionType == "Sales":
        shipping_tax_amount = 0
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
                    half_shipping_tax_amount
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


class SalesOrderMasterRestSerializer(serializers.ModelSerializer):

    SalesOrderDetails = serializers.SerializerMethodField()
    # DetailID = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    TotalGrossAmt = serializers.SerializerMethodField()
    NetTotal = serializers.SerializerMethodField()
    is_customer = serializers.SerializerMethodField()
    ProductList = serializers.SerializerMethodField()
    ShippingAddress = serializers.SerializerMethodField()
    ShippingAddressList = serializers.SerializerMethodField()
    GrandTotal_print = serializers.SerializerMethodField()
    Place_of_Supply = serializers.SerializerMethodField()
    GrossAmt_print = serializers.SerializerMethodField()
    TotalDiscount_print = serializers.SerializerMethodField()
    DiscountAmount_print = serializers.SerializerMethodField()
    TotalTax_print = serializers.SerializerMethodField()
    PrintCustomerName = serializers.SerializerMethodField()
    PhoneNo = serializers.SerializerMethodField()
    Mobile = serializers.SerializerMethodField()
    BillDiscAmt = serializers.SerializerMethodField()
    GST_Treatment = serializers.SerializerMethodField()
    GST_Treatment_Name = serializers.SerializerMethodField()
    VAT_Treatment_Name = serializers.SerializerMethodField()
    RoundOff = serializers.SerializerMethodField()
    GSTNumber = serializers.SerializerMethodField()
    LedgerBalance = serializers.SerializerMethodField()
    VATAmount_print = serializers.SerializerMethodField()
    RoundOff = serializers.SerializerMethodField()
    VATNumber = serializers.SerializerMethodField()
    SGST_final_list = serializers.SerializerMethodField()
    IGST_final_list = serializers.SerializerMethodField()
    billing_address_single = serializers.SerializerMethodField()
    BillingAddressList = serializers.SerializerMethodField()
    Address1 = serializers.SerializerMethodField()
    EmployeeName = serializers.SerializerMethodField()
    EmployeePhone = serializers.SerializerMethodField()

    class Meta:
        model = SalesOrderMaster
        fields = (
            "id",
            "SalesOrderMasterID",
            "ShippingCharge",
            "shipping_tax_amount",
            "TaxTypeID",
            "SAC",
            "SalesTax",
            "BranchID",
            "Action",
            "VoucherNo",
            "Date",
            "LedgerID",
            "LedgerName",
            "PriceCategoryID",
            "CustomerName",
            "Address1",
            "TotalGrossAmt",
            "TaxID",
            "TaxType",
            "Country_of_Supply",
            "State_of_Supply",
            "GST_Treatment",
            "VAT_Treatment",
            "TokenNumber",
            "Phone",
            "Address2",
            "Notes",
            "FinacialYearID",
            "TotalTax",
            "NetTotal",
            "is_customer",
            "VATAmount",
            "SGSTAmount",
            "CGSTAmount",
            "IGSTAmount",
            "TAX1Amount",
            "TAX2Amount",
            "TAX3Amount",
            "BillDiscAmt",
            "BillDiscPercent",
            "GrandTotal",
            "RoundOff",
            "DeliveryDate",
            "IsActive",
            "IsInvoiced",
            "CreatedDate",
            "UpdatedDate",
            "CreatedUserID",
            "SalesOrderDetails",
            "ProductList",
            "ShippingAddress",
            "ShippingAddressList",
            "EstimateNo",
            "GrandTotal_print",
            "Place_of_Supply",
            "GrossAmt_print",
            "TotalDiscount",
            "TotalDiscount_print",
            "DiscountAmount_print",
            "TotalTax_print",
            "PrintCustomerName",
            "PhoneNo",
            "Mobile",
            "GST_Treatment_Name",
            "VAT_Treatment_Name",
            "GSTNumber",
            "LedgerBalance",
            "VATAmount_print",
            "RoundOff",
            "VATNumber",
            "SGST_final_list",
            "IGST_final_list",
            "billing_address_single",
            "BillingAddressList",
            "EmployeeID",
            "EmployeeName",
            "EmployeePhone"
        )
    
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
                "id": BillingAddress.id,
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
            CompanyID=CompanyID, Branch__BranchID=BranchID, Party__LedgerID=LedgerID, Type="BillingAddress"
        ).exists():
            shipping_instances = UserAdrress.objects.filter(
                CompanyID=CompanyID, Branch__BranchID=BranchID, Party__LedgerID=LedgerID, Type="BillingAddress"
            )
            serialized = ShippingAddressListSerializer(
                shipping_instances, many=True, context={"CompanyID": CompanyID}
            )
            BillingAddressList = serialized.data
        return BillingAddressList

    def get_SGST_final_list(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        BranchID = instances.BranchID
        SalesOrderMasterID = instances.SalesOrderMasterID
        sales_details = SalesOrderDetails.objects.filter(
            CompanyID=CompanyID,
            SalesOrderMasterID=SalesOrderMasterID,
            BranchID=BranchID,
        )
        SGST_final_list = GST_finalList_fun(
            instances, sales_details, "SGST", PriceRounding, "Sales"
        )
        return SGST_final_list

    def get_IGST_final_list(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        BranchID = instances.BranchID
        SalesOrderMasterID = instances.SalesOrderMasterID
        sales_details = SalesOrderDetails.objects.filter(
            CompanyID=CompanyID,
            SalesOrderMasterID=SalesOrderMasterID,
            BranchID=BranchID,
        )
        IGST_final_list = GST_finalList_fun(
            instances, sales_details, "IGST", PriceRounding, "Sales"
        )
        return IGST_final_list

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

    def get_RoundOff(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        RoundOff = instances.RoundOff

    def get_VATAmount_print(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        VATAmount = instances.VATAmount
        VATAmount = str(round(VATAmount, PriceRounding))
        return str(VATAmount)

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

    def get_RoundOff(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        RoundOff = instances.RoundOff

        # RoundOff = round(RoundOff, PriceRounding)

        return converted_float(RoundOff)

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

    def get_BillDiscAmt(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        BillDiscAmt = instances.BillDiscAmt

        # BillDiscAmt = round(BillDiscAmt, PriceRounding)

        return converted_float(BillDiscAmt)

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

    def get_PhoneNo(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        # trunk-ignore(flake8/F841)
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

    def get_TotalTax_print(self, instances):
        PriceRounding = self.context.get("PriceRounding")
        TotalTax = instances.TotalTax

        TotalTax = str(round(TotalTax, PriceRounding))

        return str(TotalTax)

    def get_DiscountAmount_print(self, salesReturn_details):
        PriceRounding = self.context.get("PriceRounding")
        DiscountAmount = salesReturn_details.TotalDiscount
        DiscountAmount = round(DiscountAmount, PriceRounding)

        return str(DiscountAmount)

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

    def get_Place_of_Supply(self, instances):
        CompanyID = self.context.get("CompanyID")
        State_Name = ""

        try:
            if State.objects.filter(pk=instances.State_of_Supply).exists():
                State_Name = State.objects.get(pk=instances.State_of_Supply).Name
        except:
            pass

        return State_Name

    def get_GrandTotal_print(self, instances):
        CompanyID = self.context.get("CompanyID")

        PriceRounding = self.context.get("PriceRounding")

        GrandTotal = instances.GrandTotal
        GrandTotal_print = str(round(GrandTotal, PriceRounding))
        return str(GrandTotal_print)

    def get_ShippingAddress(self, instances):
        ShippingAddress = instances.ShippingAddress
        if ShippingAddress:
            ShippingAddress = ShippingAddress.id
        else:
            ShippingAddress = None

        return str(ShippingAddress)

    def get_ShippingAddressList(self, instances):
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
        SalesOrderMasterID = instances.SalesOrderMasterID
        WarehouseID = 1
        sales_details = SalesOrderDetails.objects.filter(
            CompanyID=CompanyID,
            SalesOrderMasterID=SalesOrderMasterID,
            BranchID=BranchID,
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
                    "id": p.id,
                    "product_id": p.id,
                    "ProductCode": p.ProductCode,
                    "ProductName": p.ProductName,
                    "ProductID": p.ProductID,
                    "Stock": Stock,
                    "SalesPrice": SalesPrice,
                    "PurchasePrice": PurchasePrice,
                }
            )

        return ProductList

    def get_SalesOrderDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        salesOrder_details = SalesOrderDetails.objects.filter(
            CompanyID=CompanyID,
            SalesOrderMasterID=instances.SalesOrderMasterID,
            BranchID=instances.BranchID,
        ).order_by("SalesOrderDetailsID")
        serialized = SalesOrderDetailsRestSerializer(
            salesOrder_details,
            many=True,
            context={"CompanyID": CompanyID, "PriceRounding": PriceRounding},
        )

        return serialized.data

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

    def get_TotalTax(self, instances):
        TotalTax = converted_float(instances.TotalTax)
        # TotalTax = round(TotalTax, 2)
        return TotalTax

    def get_GrandTotal(self, instances):
        GrandTotal = converted_float(instances.GrandTotal)
        # GrandTotal = round(GrandTotal, 2)
        return GrandTotal

    def get_TotalGrossAmt(self, instances):
        TotalGrossAmt = converted_float(instances.TotalGrossAmt)
        # TotalGrossAmt = round(TotalGrossAmt, 2)
        return TotalGrossAmt

    def get_NetTotal(self, instances):
        NetTotal = converted_float(instances.NetTotal)
        # NetTotal = round(NetTotal, 2)
        return NetTotal

    def get_DetailID(self, instances):

        return ""

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(CompanyID=CompanyID, LedgerID=LedgerID)

        LedgerName = ledger.LedgerName

        return LedgerName


class SalesOrderMaster1RestSerializer(serializers.ModelSerializer):

    LedgerName = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    TotalTax_rounded = serializers.SerializerMethodField()
    TotalGrossAmt_rounded = serializers.SerializerMethodField()
    GrandTotal_Rounded = serializers.SerializerMethodField()

    class Meta:
        model = SalesOrderMaster
        fields = (
            "id",
            "SalesOrderMasterID",
            "TotalTax_rounded",
            "GrandTotal_Rounded",
            "VoucherNo",
            "Date",
            "LedgerID",
            "LedgerName",
            "CustomerName",
            "TotalTax",
            "GrandTotal",
            "DeliveryDate",
            "IsInvoiced",
            "TotalGrossAmt_rounded",
        )

    def get_TotalTax(self, instances):
        TotalTax = converted_float(instances.TotalTax)
        TotalTax = round(TotalTax, 2)
        return TotalTax

    def get_GrandTotal(self, instances):
        GrandTotal = converted_float(instances.GrandTotal)
        GrandTotal = round(GrandTotal, 2)
        return GrandTotal

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(CompanyID=CompanyID, LedgerID=LedgerID)

        LedgerName = ledger.LedgerName

        return LedgerName

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


class SalesOrderDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrderDetails
        fields = (
            "id",
            "BranchID",
            "Action",
            "SalesOrderMasterID",
            "ProductID",
            "Qty",
            "FreeQty",
            "UnitPrice",
            "RateWithTax",
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
            "CreatedUserID",
        )


class SalesOrderDetailsRestSerializer(serializers.ModelSerializer):
    Qty = serializers.SerializerMethodField()
    FreeQty = serializers.SerializerMethodField()
    ReturnQty = serializers.SerializerMethodField()
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
    UnitList = serializers.SerializerMethodField()
    SerialNos = serializers.SerializerMethodField()
    is_inclusive = serializers.SerializerMethodField()
    ActualUnitPrice = serializers.SerializerMethodField()
    ProductCode = serializers.SerializerMethodField()
    HSNCode = serializers.SerializerMethodField()
    ProductTaxName = serializers.SerializerMethodField()
    GST_Inclusive = serializers.SerializerMethodField()
    Vat_Inclusive = serializers.SerializerMethodField()
    SalesPrice = serializers.SerializerMethodField()
    PurchasePrice = serializers.SerializerMethodField()
    ActualProductTaxID = serializers.SerializerMethodField()
    ActualProductTaxName = serializers.SerializerMethodField()
    SalesDetailsID = serializers.SerializerMethodField()
    gstPer = serializers.SerializerMethodField()
    TotalTaxRounded = serializers.SerializerMethodField()
    ProductCodeVal = serializers.SerializerMethodField()
    detail_errors = serializers.SerializerMethodField()
    DiscountAmount_print = serializers.SerializerMethodField()
    VATPerc_print = serializers.SerializerMethodField()
    product_description = serializers.SerializerMethodField()
    OrderFlavour = serializers.SerializerMethodField()
    OrderFlavourName = serializers.SerializerMethodField()
    current_stock = serializers.SerializerMethodField()
    multi_factor = serializers.SerializerMethodField()
    Barcode = serializers.SerializerMethodField()
    
    class Meta:
        model = SalesOrderDetails
        fields = (
            "id",
            "unq_id",
            "SalesOrderDetailsID",
            "BranchID",
            "Action",
            "SalesOrderMasterID",
            "ProductID",
            "ProductName",
            "Qty",
            "FreeQty",
            "UnitPrice",
            "ReturnQty",
            "InclusivePrice",
            "AddlDiscPerc",
            "AddlDiscAmt",
            "UnitList",
            "ProductTaxID",
            "RateWithTax",
            "CostPerPrice",
            "PriceListID",
            "UnitName",
            "DiscountPerc",
            "DiscountAmount",
            "ActualProductTaxID",
            "GrossAmount",
            "TaxableAmount",
            "VATPerc",
            "VATAmount",
            "SGSTPerc",
            "SGSTAmount",
            "CGSTPerc",
            "SerialNos",
            "ActualProductTaxName",
            "CGSTAmount",
            "IGSTPerc",
            "IGSTAmount",
            "KFCAmount",
            "NetAmount",
            "CreatedDate",
            "CreatedUserID",
            "ActualUnitPrice",
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
            "ProductCodeVal",
            "unitPriceRounded",
            "quantityRounded",
            "actualSalesPrice",
            "netAmountRounded",
            "BatchCode",
            "is_inclusive",
            "ProductCode",
            "HSNCode",
            "ProductTaxName",
            "GST_Inclusive",
            "Vat_Inclusive",
            "SalesPrice",
            "SalesDetailsID",
            "gstPer",
            "TotalTaxRounded",
            "detail_errors",
            "DiscountAmount_print",
            "VATPerc_print",
            "product_description",
            "Description",
            "OrderFlavour",
            "current_stock",
            "multi_factor",
            "OrderFlavourName",
            "PurchasePrice",
            "Barcode"
        )
        
    def get_Barcode(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        Barcode = ""
        ProductID = sales_details.ProductID
        PriceListID = sales_details.PriceListID
        if PriceList.objects.filter(CompanyID=CompanyID, PriceListID=PriceListID).exists():
            price_ins = PriceList.objects.filter(
                CompanyID=CompanyID, PriceListID=PriceListID).first()
            UnitID = price_ins.UnitID
            if ProductBarcode.objects.filter(CompanyID=CompanyID, ProductID__ProductID=ProductID, UnitID__UnitID=UnitID).exists():
                Barcode = ProductBarcode.objects.filter(
                    CompanyID=CompanyID, ProductID__ProductID=ProductID, UnitID__UnitID=UnitID).first().Barcode
        return Barcode
        
    def get_multi_factor(self, salesdetails):
        CompanyID = self.context.get("CompanyID")
        PriceListID = salesdetails.PriceListID
        MultiFactor = ""
        if PriceList.objects.filter(CompanyID=CompanyID, PriceListID=PriceListID).exists():
            MultiFactor = PriceList.objects.filter(
                CompanyID=CompanyID, PriceListID=PriceListID).first().MultiFactor
        return converted_float(MultiFactor)

    def get_current_stock(self, salesdetails):
        CompanyID = self.context.get("CompanyID")
        ProductID = salesdetails.ProductID
        BranchID = salesdetails.BranchID
        WarehouseID = 1
        BatchCode = ""
        current_stock = get_ProductStock(
            CompanyID, BranchID, ProductID, WarehouseID, BatchCode)
        return converted_float(current_stock)
        
    def get_OrderFlavour(self, purchaseReturn_details):
        flavour = None
        if purchaseReturn_details.flavour:
            flavour = purchaseReturn_details.flavour.id
        return flavour
    
    def get_OrderFlavourName(self, purchaseReturn_details):
        name = ""
        if purchaseReturn_details.flavour:
            name = purchaseReturn_details.flavour.FlavourName
        return name

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

    def get_VATPerc_print(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        VATPerc = sales_details.VATPerc

        VATPerc = str(round(VATPerc, PriceRounding))
        if "." in VATPerc:
            is_decimal = VATPerc.split(".")
            if int(is_decimal[1]) == 0:
                VATPerc = is_decimal[0]

        return str(VATPerc)

    def get_DiscountAmount_print(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        DiscountAmount = sales_details.DiscountAmount
        DiscountAmount = round(DiscountAmount, PriceRounding)

        return str(DiscountAmount)

    def get_detail_errors(self, sales_details):
        detail_errors = {"Qty": "", "UnitPrice": ""}
        return detail_errors

    def get_ActualProductTaxID(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductTaxID = sales_details.ProductTaxID
        return ProductTaxID


    def get_TotalTaxRounded(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        TAX1Amount = sales_details.TAX1Amount
        TAX2Amount = sales_details.TAX2Amount
        TAX3Amount = sales_details.TAX3Amount
        VATAmount = sales_details.VATAmount
        IGSTAmount = sales_details.IGSTAmount
        SGSTAmount = sales_details.SGSTAmount
        CGSTAmount = sales_details.CGSTAmount

        TotalTax = (
            TAX1Amount
            + TAX2Amount
            + TAX3Amount
            + VATAmount
            + CGSTAmount
            + SGSTAmount
            + IGSTAmount
        )
        return converted_float(TotalTax)

    def get_gstPer(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        IGSTPerc = sales_details.IGSTPerc
        return converted_float(IGSTPerc)

    def get_SalesDetailsID(self, sales_details):
        SalesDetailsID = 1
        return SalesDetailsID

    def get_ActualProductTaxName(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductTaxID = sales_details.ProductTaxID
        BranchID = sales_details.BranchID
        ProductTaxName = ""
        if TaxCategory.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, TaxID=ProductTaxID
        ).exists():
            ProductTaxName = TaxCategory.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, TaxID=ProductTaxID
            ).TaxName
        return ProductTaxName

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
        if VatID:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=VatID, BranchID=BranchID
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
        if GST:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=GST, BranchID=BranchID
            ).Inclusive
        return Inclusive

    def get_PurchasePrice(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = sales_details.PriceListID
        BranchID = sales_details.BranchID
        PurchasePrice = 0
        if PriceList.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID
        ).exists():
            PurchasePrice = PriceList.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID
            ).PurchasePrice
        return converted_float(PurchasePrice)
    
    def get_SalesPrice(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = sales_details.PriceListID
        BranchID = sales_details.BranchID
        SalesPrice = 0
        if PriceList.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID
        ).exists():
            SalesPrice = PriceList.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID
            ).SalesPrice
        return converted_float(SalesPrice)

    def get_ProductTaxName(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductTaxID = sales_details.ProductTaxID
        BranchID = sales_details.BranchID
        ProductTaxName = ""
        if TaxCategory.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, TaxID=ProductTaxID
        ).exists():
            ProductTaxName = TaxCategory.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, TaxID=ProductTaxID
            ).TaxName
        return ProductTaxName

    def get_ProductName(self, sales_details):

        CompanyID = self.context.get("CompanyID")

        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID

        product = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
        )

        ProductName = product.ProductName
        return ProductName

    def get_ProductCode(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID
        product = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
        )
        ProductCode = product.ProductCode
        return ProductCode

    def get_ProductCodeVal(self, sales_details):
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

    def get_UnitList(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID

        UnitList = PriceList.objects.filter(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
        )

        serialized = PriceListRestSerializer(
            UnitList,
            many=True,
            context={"CompanyID": CompanyID, "PriceRounding": PriceRounding},
        )

        return serialized.data

    def get_ActualUnitPrice(self, purchase_details):
        PriceRounding = self.context.get("PriceRounding")
        ActualUnitPrice = purchase_details.UnitPrice

        # ActualUnitPrice = round(ActualUnitPrice, PriceRounding)
        return str(ActualUnitPrice)

    def get_SerialNos(self, sales_details):
        SerialNos = []
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        SalesMasterID = sales_details.SalesOrderMasterID
        SalesDetailsID = sales_details.SalesOrderDetailsID
        if SerialNumbers.objects.filter(
            CompanyID=CompanyID,
            BranchID=BranchID,
            SalesMasterID=SalesMasterID,
            SalesDetailsID=SalesDetailsID,
            VoucherType="SO",
        ).exists():
            Serial_details = SerialNumbers.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                SalesMasterID=SalesMasterID,
                SalesDetailsID=SalesDetailsID,
                VoucherType="SO",
            )
            SerialNos = SerialNumberSerializer(
                Serial_details, many=True, context={"CompanyID": CompanyID}
            )
            SerialNos = SerialNos.data
        return SerialNos

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

    def get_Flavour(self, instances):
        Flavour = ""
        return Flavour

    def get_InclusivePrice(self, sales_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        # PriceRounding = 2
        InclusivePrice = sales_details.InclusivePrice
        if InclusivePrice:
            # InclusivePrice = round(InclusivePrice, PriceRounding)
            InclusivePrice = InclusivePrice
        else:
            InclusivePrice = 0
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
            ProductID=ProductID,
            CompanyID=CompanyID,
            PriceListID=PriceListID,
            BranchID=BranchID,
        ).exists():
            SalesPrice = PriceList.objects.get(
                ProductID=ProductID,
                CompanyID=CompanyID,
                PriceListID=PriceListID,
                BranchID=BranchID,
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
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
        ).is_inclusive

        return is_inclusive

    # def get_is_inclusive(self, sales_details):
    #     CompanyID = self.context.get("CompanyID")
    #     BranchID = sales_details.BranchID
    #     ProductID = sales_details.ProductID
    #     GST = Product.objects.get(
    #         CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).GST
    #     GstInclusive = False
    #     if GST:
    #         GstInclusive = TaxCategory.objects.get(
    #             CompanyID=CompanyID, TaxID=GST, BranchID=BranchID).Inclusive

    #     VatID = Product.objects.get(
    #         CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).VatID
    #     VatInclusive = TaxCategory.objects.get(
    #         CompanyID=CompanyID, TaxID=VatID, BranchID=BranchID).Inclusive
    #     Inclusive = False
    #     if GstInclusive == True or VatInclusive == True:
    #         Inclusive == True

    #     return Inclusive

    def get_is_VAT_inclusive(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        VatID = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
        ).VatID
        Inclusive = TaxCategory.objects.get(
            CompanyID=CompanyID, TaxID=VatID, BranchID=BranchID
        ).Inclusive
        return Inclusive

    def get_is_GST_inclusive(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        GST = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
        ).GST
        Inclusive = False
        if GST:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=GST, BranchID=BranchID
            ).Inclusive
        return Inclusive

    def get_is_TAX1_inclusive(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        Tax1 = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
        ).Tax1
        Inclusive = False
        if Tax1:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax1, BranchID=BranchID
            ).Inclusive
        return Inclusive

    def get_is_TAX2_inclusive(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        Tax2 = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
        ).Tax2
        Inclusive = False
        if Tax2:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax2, BranchID=BranchID
            ).Inclusive
        return Inclusive

    def get_is_TAX3_inclusive(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = sales_details.BranchID
        ProductID = sales_details.ProductID
        Tax3 = Product.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID
        ).Tax3
        Inclusive = False
        if Tax3:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax3, BranchID=BranchID
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
        TotalTax = (
            TAX1Amount
            + TAX2Amount
            + TAX3Amount
            + VATAmount
            + CGSTAmount
            + SGSTAmount
            + IGSTAmount
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
            CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID
        ).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID
            ).UnitID
            UnitName = Unit.objects.get(
                BranchID=BranchID, UnitID=UnitID, CompanyID=CompanyID
            ).UnitName
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

    def get_ReturnQty(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        ReturnQty = sales_details.Qty
        # ReturnQty = round(Qty, PriceRounding)
        return converted_float(ReturnQty)

    def get_UnitPrice(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        UnitPrice = sales_details.UnitPrice
        # UnitPrice = round(UnitPrice, PriceRounding)
        return converted_float(UnitPrice)

    def get_RateWithTax(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        RateWithTax = sales_details.RateWithTax
        # RateWithTax = round(RateWithTax, PriceRounding)
        return converted_float(RateWithTax)

    def get_CostPerPrice(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        # CostPerPrice = sales_details.CostPerPrice
        CostPerPrice = 0
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

    def get_VATAmount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        VATAmount = sales_details.VATAmount
        # VATAmount = round(VATAmount, PriceRounding)
        return converted_float(VATAmount)

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
        AddlDiscPerc = 0
        return converted_float(AddlDiscPerc)

    def get_AddlDiscAmt(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        AddlDiscAmt = 0
        return converted_float(AddlDiscAmt)

    def get_TAX1Perc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX1Perc = sales_details.TAX1Perc
        if not TAX1Perc:
            TAX1Perc = 0
        return converted_float(TAX1Perc)

    def get_TAX2Perc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX2Perc = sales_details.TAX2Perc
        if not TAX2Perc:
            TAX2Perc = 0
        return converted_float(TAX2Perc)

    def get_TAX3Perc(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX3Perc = sales_details.TAX3Perc
        if not TAX3Perc:
            TAX3Perc = 0
        return converted_float(TAX3Perc)

    def get_TAX1Amount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX1Amount = sales_details.TAX1Amount
        if not TAX1Amount:
            TAX1Amount = 0
        return converted_float(TAX1Amount)

    def get_TAX2Amount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX2Amount = sales_details.TAX2Amount
        if not TAX2Amount:
            TAX2Amount = 0
        return converted_float(TAX2Amount)

    def get_TAX3Amount(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        TAX3Amount = sales_details.TAX3Amount
        if not TAX3Amount:
            TAX3Amount = 0
        return converted_float(TAX3Amount)


class SalesOrderReportSerializer(serializers.ModelSerializer):

    LedgerName = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    NetTotal = serializers.SerializerMethodField()

    class Meta:
        model = SalesOrderMaster
        fields = (
            "id",
            "SalesOrderMasterID",
            "BranchID",
            "Action",
            "VoucherNo",
            "Date",
            "LedgerID",
            "LedgerName",
            "CustomerName",
            "IsInvoiced",
            "TotalTax",
            "NetTotal",
            "GrandTotal",
        )

    def get_TotalTax(self, instances):
        TotalTax = converted_float(instances.TotalTax)
        TotalTax = round(TotalTax, 2)
        return TotalTax

    def get_NetTotal(self, instances):
        NetTotal = converted_float(instances.NetTotal)
        NetTotal = round(NetTotal, 2)
        return NetTotal

    def get_GrandTotal(self, instances):
        GrandTotal = converted_float(instances.GrandTotal)
        GrandTotal = round(GrandTotal, 2)
        return GrandTotal

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(
            LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID
        )

        LedgerName = ledger.LedgerName

        return LedgerName



class SalesOrderPrintSerializer(serializers.ModelSerializer):
    
    Details = serializers.SerializerMethodField()
    DetailID = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    TotalQty = serializers.SerializerMethodField()

    class Meta:
        model = SalesOrderMaster
        fields = (
            "id",
            "SalesOrderMasterID",
            "BranchID",
            "Action",
            "VoucherNo",
            "Date",
            "DetailID",
            "LedgerID",
            "LedgerName",
            "VATAmount",
            "SGSTAmount",
            "CGSTAmount",
            "IGSTAmount",
            "TAX1Amount",
            "TAX2Amount",
            "TAX3Amount",
            "PriceCategoryID",
            "CustomerName",
            "Address1",
            "DeliveryDate",
            "IsInvoiced",
            "Address2",
            "Notes",
            "FinacialYearID",
            "TotalTax",
            "NetTotal",
            "TaxID",
            "TaxType",
            "GrandTotal",
            "RoundOff",
            "IsActive",
            "CreatedDate",
            "UpdatedDate",
            "CreatedUserID",
            "Details",
            "TotalGrossAmt",
            "TotalDiscount",
            "TotalQty"
        )

    def get_TotalQty(self, instances):
        CompanyID = self.context.get("CompanyID")
        TotalQty = 0
        SalesOrderMasterID = instances.SalesOrderMasterID
        BranchID = instances.BranchID
        sales_details = SalesOrderDetails.objects.filter(
            CompanyID=CompanyID, SalesOrderMasterID=SalesOrderMasterID, BranchID=BranchID
        )
        TotalQty = sales_details.aggregate(Sum("Qty"))
        TotalQty = TotalQty["Qty__sum"]

        return converted_float(TotalQty)
    
    
    def get_Details(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")

        salesOrder_details = SalesOrderDetails.objects.filter(
            SalesOrderMasterID=instances.SalesOrderMasterID,
            BranchID=instances.BranchID,
            CompanyID=CompanyID
        )
        serialized = SalesDetailsPrintSerializer(
            salesOrder_details,
            many=True,
            context={"PriceRounding": PriceRounding, "CompanyID": CompanyID},
        )

        return serialized.data

    def get_DetailID(self, instances):

        return ""

    def get_TotalTax(self, instances):
        TotalTax = converted_float(instances.TotalTax)
        TotalTax = round(TotalTax, 2)
        return TotalTax

    def get_GrandTotal(self, instances):
        GrandTotal = converted_float(instances.GrandTotal)
        GrandTotal = round(GrandTotal, 2)
        return GrandTotal

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(LedgerID=LedgerID, CompanyID=CompanyID)

        LedgerName = ledger.LedgerName

        return LedgerName
    
    
    
    
class SalesDetailsPrintSerializer(serializers.ModelSerializer):
    Qty = serializers.SerializerMethodField()
    UnitPrice = serializers.SerializerMethodField()
    NetAmount = serializers.SerializerMethodField()
    ProductName = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()
    Description = serializers.SerializerMethodField()

    class Meta:
        model = SalesOrderDetails
        fields = ("ProductName", "Qty", "UnitPrice",
                  "UnitName", "NetAmount", "Description")

    def get_Description(self, sales_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = sales_details.ProductID
        BranchID = sales_details.BranchID
        Description = ""
        if Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID).exists():
            product = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)
            Description = product.Description
        return Description
    
    
    def get_ProductName(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = purchase_details.ProductID
        BranchID = purchase_details.BranchID

        if Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID).exists():
            product = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)
            ProductName = product.ProductName
        else:
            ProductName = ""

        return ProductName

    def get_UnitName(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = purchase_details.PriceListID
        BranchID = purchase_details.BranchID

        UnitName = ""
        if PriceList.objects.filter(
            CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID
        ).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID
            ).UnitID
            UnitName = Unit.objects.get(
                BranchID=BranchID, UnitID=UnitID, CompanyID=CompanyID
            ).UnitName

        return UnitName

    def get_Qty(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        Qty = purchase_details.Qty

        if Qty:
            Qty = round(Qty, PriceRounding)
        else:
            Qty = 0

        return str(Qty)

    def get_UnitPrice(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        UnitPrice = purchase_details.UnitPrice
        if UnitPrice:
            UnitPrice = round(UnitPrice, PriceRounding)
        else:
            UnitPrice = 0

        return str(UnitPrice)

    def get_NetAmount(self, purchase_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        NetAmount = purchase_details.NetAmount

        if NetAmount:
            NetAmount = round(NetAmount, PriceRounding)
        else:
            NetAmount = 0

        return str(NetAmount)