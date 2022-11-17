from django.db.models import F, Q, Sum
from rest_framework import serializers

from api.v10.priceLists.serializers import PriceListRestSerializer
from api.v10.sales import functions as func
from api.v10.sales.serializers import SerialNumberSerializer
from api.v10.workOrder.serializers import Batch_ListSerializer
from brands.models import (
    AccountLedger,
    Batch,
    BillWiseDetails,
    BillWiseMaster,
    Country,
    LedgerPosting,
    Parties,
    PriceList,
    Product,
    PurchaseReturnDetails,
    PurchaseReturnMaster,
    QrCode,
    SerialNumbers,
    State,
    TaxCategory,
    Unit,
    Warehouse,
)
from main.functions import converted_float, generateQrCode, get_ProductStock, get_company


class PurchaseReturnMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseReturnMaster
        fields = (
            "id",
            "BranchID",
            "Action",
            "VoucherNo",
            "VoucherDate",
            "RefferenceBillNo",
            "RefferenceBillDate",
            "VenderInvoiceDate",
            "CreditPeriod",
            "Country_of_Supply",
            "State_of_Supply",
            "GST_Treatment",
            "LedgerID",
            "PriceCategoryID",
            "EmployeeID",
            "PurchaseAccount",
            "DeliveryMasterID",
            "OrderMasterID",
            "CustomerName",
            "Address1",
            "Address2",
            "Address3",
            "Notes",
            "FinacialYearID",
            "TotalGrossAmt",
            "TotalTax",
            "NetTotal",
            "AdditionalCost",
            "GrandTotal",
            "RoundOff",
            "WarehouseID",
            "IsActive",
            "VAT_Treatment",
            "TaxID",
            "TaxType",
            "VATAmount",
            "SGSTAmount",
            "CGSTAmount",
            "IGSTAmount",
            "TAX1Amount",
            "TAX2Amount",
            "TAX3Amount",
            "AddlDiscPercent",
            "AddlDiscAmt",
            "TotalDiscount",
            "BillDiscPercent",
            "BillDiscAmt",
        )


class PurchaseReturn1MasterRestSerializer(serializers.ModelSerializer):

    LedgerName = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    TotalTax_rounded = serializers.SerializerMethodField()
    GrandTotal_Rounded = serializers.SerializerMethodField()
    TotalGrossAmt_Rounded = serializers.SerializerMethodField()
    is_billwised = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseReturnMaster
        fields = (
            "id",
            "PurchaseReturnMasterID",
            "VoucherNo",
            "VoucherDate",
            "RefferenceBillNo",
            "RefferenceBillDate",
            "VenderInvoiceDate",
            "CustomerName",
            "TotalTax_rounded",
            "GrandTotal_Rounded",
            "LedgerID",
            "LedgerName",
            "TotalTax",
            "GrandTotal",
            "TotalGrossAmt_Rounded",
            "is_billwised",
        )

    def get_is_billwised(self, instance):
        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        PurchaseReturnMasterID = instance.PurchaseReturnMasterID
        is_billwised = False
        if (
            BillWiseMaster.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                InvoiceNo=VoucherNo,
                TransactionID=PurchaseReturnMasterID,
                VoucherType="PR",
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

        ledger = AccountLedger.objects.get(CompanyID=CompanyID, LedgerID=LedgerID)

        LedgerName = ledger.LedgerName

        return LedgerName

    def get_TotalTax(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalTax = instances.TotalTax

        if TotalTax:
            TotalTax = round(TotalTax, PriceRounding)
        else:
            TotalTax = 0

        return converted_float(TotalTax)

    def get_GrandTotal(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))

        GrandTotal = instances.GrandTotal

        if GrandTotal:
            GrandTotal = round(GrandTotal, PriceRounding)
        else:
            GrandTotal = 0

        return converted_float(GrandTotal)

    def get_TotalGrossAmt_Rounded(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalGrossAmt = instances.TotalGrossAmt

        TotalGrossAmt_rounded = round(TotalGrossAmt, PriceRounding)

        return str(TotalGrossAmt_rounded)

    def get_TotalTax_rounded(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalTax = instances.TotalTax

        TotalTax_rounded = round(TotalTax, PriceRounding)

        return str(TotalTax_rounded)

    def get_GrandTotal_Rounded(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        GrandTotal = instances.GrandTotal

        GrandTotal_Rounded = round(GrandTotal, PriceRounding)

        return str(GrandTotal_Rounded)


class PurchaseReturnMasterRestSerializer(serializers.ModelSerializer):
    PurchaseReturnDetails = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    DetailID = serializers.SerializerMethodField()
    PurchaseAccountName = serializers.SerializerMethodField()
    WareHouseName = serializers.SerializerMethodField()
    AddlDiscPercent = serializers.SerializerMethodField()
    BillDiscPercent = serializers.SerializerMethodField()
    RoundOff = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    TotalGrossAmt = serializers.SerializerMethodField()
    AddlDiscAmt = serializers.SerializerMethodField()
    NetTotal = serializers.SerializerMethodField()
    TotalDiscount = serializers.SerializerMethodField()
    VATAmount = serializers.SerializerMethodField()
    SGSTAmount = serializers.SerializerMethodField()
    CGSTAmount = serializers.SerializerMethodField()
    IGSTAmount = serializers.SerializerMethodField()
    TAX1Amount = serializers.SerializerMethodField()
    TAX2Amount = serializers.SerializerMethodField()
    TAX3Amount = serializers.SerializerMethodField()
    BillDiscAmt = serializers.SerializerMethodField()
    is_customer = serializers.SerializerMethodField()
    Country_of_Supply_name = serializers.SerializerMethodField()
    State_of_Supply_name = serializers.SerializerMethodField()
    TotalGrossAmt_print = serializers.SerializerMethodField()
    TotalDiscount_print = serializers.SerializerMethodField()
    qr_image = serializers.SerializerMethodField()
    # ========
    GrandTotal_print = serializers.SerializerMethodField()
    NetTotal_print = serializers.SerializerMethodField()
    GrossAmt_print = serializers.SerializerMethodField()
    TotalDiscount_print = serializers.SerializerMethodField()
    TotalTax_print = serializers.SerializerMethodField()
    TotalTaxableAmount_print = serializers.SerializerMethodField()
    VATAmount_print = serializers.SerializerMethodField()
    GSTNumber = serializers.SerializerMethodField()
    GST_Treatment = serializers.SerializerMethodField()
    VAT_Treatment = serializers.SerializerMethodField()
    Attention = serializers.SerializerMethodField()
    PrintAddress = serializers.SerializerMethodField()
    PrintCustomerName = serializers.SerializerMethodField()
    VATNumber = serializers.SerializerMethodField()

    Tax_no = serializers.SerializerMethodField()
    CRNo = serializers.SerializerMethodField()
    Mobile = serializers.SerializerMethodField()
    City = serializers.SerializerMethodField()
    State = serializers.SerializerMethodField()
    Country = serializers.SerializerMethodField()
    PostalCode = serializers.SerializerMethodField()
    ProductList = serializers.SerializerMethodField()
    Balance = serializers.SerializerMethodField()
    SGST_final_list = serializers.SerializerMethodField()
    IGST_final_list = serializers.SerializerMethodField()
    Date = serializers.SerializerMethodField()
    Place_of_Supply = serializers.SerializerMethodField()
    is_billwised = serializers.SerializerMethodField()
    # ======

    class Meta:
        model = PurchaseReturnMaster
        fields = (
            "id",
            "Attention",
            "PrintAddress",
            "PrintCustomerName",
            "Tax_no",
            "CRNo",
            "Mobile",
            "City",
            "State",
            "Country",
            "PostalCode",
            "GrandTotal_print",
            "NetTotal_print",
            "GrossAmt_print",
            "TotalDiscount_print",
            "TotalTax_print",
            "TotalTaxableAmount_print",
            "VATAmount_print",
            "GSTNumber",
            "qr_image",
            "TotalDiscount_print",
            "TotalGrossAmt_print",
            "PurchaseReturnMasterID",
            "BranchID",
            "Action",
            "VoucherNo",
            "VoucherDate",
            "RefferenceBillNo",
            "RefferenceBillDate",
            "VenderInvoiceDate",
            "CreditPeriod",
            "DetailID",
            "WareHouseName",
            "Country_of_Supply",
            "State_of_Supply",
            "GST_Treatment",
            "LedgerID",
            "LedgerName",
            "PriceCategoryID",
            "EmployeeID",
            "PurchaseAccount",
            "PurchaseAccountName",
            "DeliveryMasterID",
            "OrderMasterID",
            "CustomerName",
            "Address1",
            "Address2",
            "Address3",
            "is_customer",
            "Notes",
            "FinacialYearID",
            "TotalGrossAmt",
            "TotalTax",
            "Country_of_Supply_name",
            "State_of_Supply_name",
            "NetTotal",
            "AdditionalCost",
            "GrandTotal",
            "RoundOff",
            "WarehouseID",
            "IsActive",
            "CreatedDate",
            "UpdatedDate",
            "CreatedUserID",
            "TaxID",
            "TaxType",
            "VATAmount",
            "SGSTAmount",
            "CGSTAmount",
            "IGSTAmount",
            "TAX1Amount",
            "TAX2Amount",
            "TAX3Amount",
            "VAT_Treatment",
            "AddlDiscPercent",
            "AddlDiscAmt",
            "TotalDiscount",
            "BillDiscPercent",
            "BillDiscAmt",
            "PurchaseReturnDetails",
            "ProductList",
            "Balance",
            "SGST_final_list",
            "IGST_final_list",
            "VATNumber",
            "Date",
            "Place_of_Supply",
            "is_billwised",
        )
        
    def get_is_billwised(self, instance):
        CompanyID = self.context.get("CompanyID")
        BranchID = instance.BranchID
        InvoiceNo = instance.VoucherNo
        is_billwised = False
        if BillWiseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=InvoiceNo, VoucherType="PR", Payments__gt=0).exclude(PaymentVoucherType="PR").exists():
            is_billwised = True
        return is_billwised

    def get_Place_of_Supply(self, instances):
        CompanyID = self.context.get("CompanyID")
        State_Name = ""
        try:
            if State.objects.filter(pk=instances.State_of_Supply).exists():
                State_Name = State.objects.get(pk=instances.State_of_Supply).Name
        except:
            pass

        return State_Name

    def get_Date(self, instances):
        return str(instances.VoucherDate)

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

    def get_SGST_final_list(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        BranchID = instances.BranchID
        PurchaseReturnMasterID = instances.PurchaseReturnMasterID
        purchase_details = PurchaseReturnDetails.objects.filter(
            CompanyID=CompanyID,
            PurchaseReturnMasterID=PurchaseReturnMasterID,
            BranchID=BranchID,
        )
        SGST_final_list = func.GST_finalList_fun(
            instances, purchase_details, "SGST", PriceRounding, "PurchaseReturn"
        )
        return SGST_final_list

    def get_IGST_final_list(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = self.context.get("PriceRounding")
        BranchID = instances.BranchID
        PurchaseReturnMasterID = instances.PurchaseReturnMasterID
        purchase_details = PurchaseReturnDetails.objects.filter(
            CompanyID=CompanyID,
            PurchaseReturnMasterID=PurchaseReturnMasterID,
            BranchID=BranchID,
        )
        IGST_final_list = func.GST_finalList_fun(
            instances, purchase_details, "IGST", PriceRounding, "PurchaseReturn"
        )
        return IGST_final_list

    def get_ProductList(self, instances):
        CompanyID = self.context.get("CompanyID")
        BranchID = instances.BranchID
        WarehouseID = instances.WarehouseID
        PurchaseReturnMasterID = instances.PurchaseReturnMasterID
        purchase_details = PurchaseReturnDetails.objects.filter(
            CompanyID=CompanyID,
            PurchaseReturnMasterID=PurchaseReturnMasterID,
            BranchID=BranchID,
        )

        product_ids = purchase_details.values_list("ProductID", flat=True)
        produc_instances = Product.objects.filter(
            CompanyID=CompanyID, ProductID__in=product_ids
        )
        ProductList = []
        for p in produc_instances:
            sale_ins = purchase_details.filter(ProductID=p.ProductID).first()
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
                    "ProductName": p.ProductName,
                    "ProductID": p.ProductID,
                    "ProductCode": p.ProductCode,
                    "id": p.id,
                    "Stock": Stock,
                    "SalesPrice": SalesPrice,
                    "PurchasePrice": PurchasePrice,
                }
            )

        return ProductList

    def get_Balance(self, instances):
        CompanyID = self.context.get("CompanyID")
        LedgerID = instances.LedgerID
        BranchID = instances.BranchID
        Balance = 0
        if LedgerPosting.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
        ).exists():
            ledgers = LedgerPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID
            )
            total_debit = ledgers.aggregate(Sum("Debit"))
            total_debit = total_debit["Debit__sum"]
            total_credit = ledgers.aggregate(Sum("Credit"))
            total_credit = total_credit["Credit__sum"]
            Balance = converted_float(total_debit) - converted_float(total_credit)
        return converted_float(Balance)

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

    def get_Tax_no(self, instances):

        CompanyID = self.context.get("CompanyID")
        Tax_no = ""
        if Parties.objects.filter(
            LedgerID=instances.LedgerID, CompanyID=CompanyID
        ).exists():
            Tax_no = Parties.objects.get(
                LedgerID=instances.LedgerID, CompanyID=CompanyID
            ).VATNumber

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

        return str(City)

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
                a = Parties.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID)
                # for i in a:
                #     print(i.State,"//////////////////////UVAIS///////////////////////////")
                if State.objects.filter(pk=pk).exists():
                    State_Name = State.objects.get(pk=pk).Name

        return str(State_Name)

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

        return str(Country_Name)

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

        return str(PostalCode)

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

    # def get_qr_image(self, instances):
    #     CompanyID = self.context.get("CompanyID")
    #     LedgerID = instances.LedgerID
    #     BranchID = instances.BranchID
    #     pk = str(instances.id)
    #     qr_image = None
    #     if QrCode.objects.filter(voucher_type="PR",master_id=pk).exists():
    #         qr_image = QrCode.objects.get(voucher_type="PR",master_id=pk).qr_code.url

    #     return qr_image

    # def get_qr_image(self, instances):
    #     CompanyID = self.context.get("CompanyID")
    #     request = self.context.get("request")
    #     LedgerID = instances.LedgerID
    #     BranchID = instances.BranchID
    #     pk = str(instances.id)
    #     qr_code = None
    #     if QrCode.objects.filter(voucher_type="PR", master_id=pk).exists():
    #         qr_code = QrCode.objects.get(voucher_type="PR", master_id=pk)
    #     serialized = QRCodeSerializer(
    #         qr_code, context={"CompanyID": CompanyID, "request": request}
    #     )

    #     return serialized.data.get("qr_code")
    
    def get_qr_image(self, instance):
        CompanyID = self.context.get("CompanyID")
        request = self.context.get("request")
        # CompanyID = get_company(CompanyID)
        generateQrCode(instance, "PR")
        pk = str(instance.id)
        if QrCode.objects.filter(voucher_type="PR", master_id=pk).exists():
            qr_code = QrCode.objects.get(voucher_type="PR", master_id=pk)
        serialized = QRCodeSerializer(
            qr_code, context={"CompanyID": CompanyID, "request": request}
        )
        return serialized.data.get("qr_code")

    def get_TotalDiscount_print(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalDiscount = instances.TotalDiscount
        if TotalDiscount:
            TotalDiscount = round(TotalDiscount, PriceRounding)
        else:
            TotalDiscount = 0

        return str(TotalDiscount)

    def get_TotalGrossAmt_print(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))

        TotalGrossAmt = instances.TotalGrossAmt

        if TotalGrossAmt:
            TotalGrossAmt = round(TotalGrossAmt, PriceRounding)
        else:
            TotalGrossAmt = 0

        return str(TotalGrossAmt)

    def get_PurchaseReturnDetails(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = int(self.context.get("PriceRounding"))
        BranchID = instances.BranchID
        purchaseReturn_details = PurchaseReturnDetails.objects.filter(
            CompanyID=CompanyID,
            PurchaseReturnMasterID=instances.PurchaseReturnMasterID,
            BranchID=BranchID,
        ).order_by("PurchaseReturnDetailsID")
        serialized = PurchaseReturnDetailsRestSerializer(
            purchaseReturn_details,
            many=True,
            context={"CompanyID": CompanyID, "PriceRounding": PriceRounding},
        )

        return serialized.data

    def get_Country_of_Supply_name(self, instances):
        CompanyID = self.context.get("CompanyID")
        Country_of_Supply = instances.Country_of_Supply
        Country_of_Supply_name = ""
        if Country_of_Supply:
            if Country.objects.filter(id=Country_of_Supply).exists():
                Country_of_Supply_name = Country.objects.get(
                    id=Country_of_Supply
                ).Country_Name
        return str(Country_of_Supply_name)

    def get_State_of_Supply_name(self, instances):
        CompanyID = self.context.get("CompanyID")
        State_of_Supply = instances.State_of_Supply
        State_of_Supply_name = ""
        if State_of_Supply:
            if State.objects.filter(id=State_of_Supply).exists():
                State_of_Supply_name = State.objects.get(id=State_of_Supply).Name
        return str(State_of_Supply_name)

    def get_DetailID(self, instances):

        return ""

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

    def get_WareHouseName(self, instances):
        CompanyID = self.context.get("CompanyID")

        WarehouseID = instances.WarehouseID
        BranchID = instances.BranchID

        wareHouse = Warehouse.objects.get(CompanyID=CompanyID, WarehouseID=WarehouseID)

        WareHouseName = wareHouse.WarehouseName

        return str(WareHouseName)

    def get_PurchaseAccountName(self, instances):
        CompanyID = self.context.get("CompanyID")

        PurchaseAccount = instances.PurchaseAccount
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(
            CompanyID=CompanyID, LedgerID=PurchaseAccount, BranchID=BranchID
        )

        PurchaseAccountName = ledger.LedgerName

        return str(PurchaseAccountName)

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(CompanyID=CompanyID, LedgerID=LedgerID)

        LedgerName = ledger.LedgerName

        return str(LedgerName)

    def get_AddlDiscPercent(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        AddlDiscPercent = instances.AddlDiscPercent

        # if AddlDiscPercent:
        #     AddlDiscPercent = round(AddlDiscPercent,PriceRounding)
        # else:
        #     AddlDiscPercent = 0

        return converted_float(AddlDiscPercent)

    def get_BillDiscPercent(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        BillDiscPercent = instances.BillDiscPercent

        # if BillDiscPercent:
        #     BillDiscPercent = round(BillDiscPercent,PriceRounding)
        # else:
        #     BillDiscPercent = 0

        return converted_float(BillDiscPercent)

    def get_RoundOff(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        RoundOff = instances.RoundOff

        # if RoundOff:
        #     RoundOff = round(RoundOff,PriceRounding)
        # else:
        #     RoundOff = 0

        return converted_float(RoundOff)

    def get_TotalTax(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalTax = instances.TotalTax

        # if TotalTax:
        #     TotalTax = round(TotalTax,PriceRounding)
        # else:
        #     TotalTax = 0

        return converted_float(TotalTax)

    def get_GrandTotal(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))

        GrandTotal = instances.GrandTotal

        # if GrandTotal:
        #     GrandTotal = round(GrandTotal,PriceRounding)
        # else:
        #     GrandTotal = 0

        return converted_float(GrandTotal)

    def get_TotalGrossAmt(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))

        TotalGrossAmt = instances.TotalGrossAmt

        # if TotalGrossAmt:
        #     TotalGrossAmt = round(TotalGrossAmt,PriceRounding)
        # else:
        #     TotalGrossAmt = 0

        return converted_float(TotalGrossAmt)

    def get_AddlDiscAmt(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        AddlDiscAmt = instances.AddlDiscAmt
        # if AddlDiscAmt:
        #     AddlDiscAmt = round(AddlDiscAmt,PriceRounding)
        # else:
        #     AddlDiscAmt = 0

        return converted_float(AddlDiscAmt)

    def get_NetTotal(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        NetTotal = instances.NetTotal
        # if NetTotal:
        #     NetTotal = round(NetTotal,PriceRounding)
        # else:
        #     NetTotal = 0

        return converted_float(NetTotal)

    def get_TotalDiscount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalDiscount = instances.TotalDiscount
        # if TotalDiscount:
        #     TotalDiscount = round(TotalDiscount,PriceRounding)
        # else:
        #     TotalDiscount = 0

        return converted_float(TotalDiscount)

    def get_VATAmount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        VATAmount = instances.VATAmount
        # if VATAmount:
        #     VATAmount = round(VATAmount,PriceRounding)
        # else:
        #     VATAmount = 0

        return converted_float(VATAmount)

    def get_SGSTAmount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        SGSTAmount = instances.SGSTAmount
        # if SGSTAmount:
        #     SGSTAmount = round(SGSTAmount,PriceRounding)
        # else:
        #     SGSTAmount = 0

        return converted_float(SGSTAmount)

    def get_CGSTAmount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        CGSTAmount = instances.CGSTAmount
        # if CGSTAmount:
        #     CGSTAmount = round(CGSTAmount,PriceRounding)
        # else:
        #     CGSTAmount = 0

        return converted_float(CGSTAmount)

    def get_IGSTAmount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        IGSTAmount = instances.IGSTAmount
        # if IGSTAmount:
        #     IGSTAmount = round(IGSTAmount,PriceRounding)
        # else:
        #     IGSTAmount = 0

        return converted_float(IGSTAmount)

    def get_TAX1Amount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX1Amount = instances.TAX1Amount
        # if TAX1Amount:
        #     TAX1Amount = round(TAX1Amount,PriceRounding)
        # else:
        #     TAX1Amount = 0

        return converted_float(TAX1Amount)

    def get_TAX2Amount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX2Amount = instances.TAX2Amount
        # if TAX2Amount:
        #     TAX2Amount = round(TAX2Amount,PriceRounding)
        # else:
        #     TAX2Amount = 0

        return converted_float(TAX2Amount)

    def get_TAX3Amount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX3Amount = instances.TAX3Amount
        # if TAX3Amount:
        #     TAX3Amount = round(TAX3Amount,PriceRounding)
        # else:
        #     TAX3Amount = 0

        return converted_float(TAX3Amount)

    def get_BillDiscAmt(self, instances):
        print(instances.id, "SERIALIZERRR@@!!")
        PriceRounding = int(self.context.get("PriceRounding"))
        BillDiscAmt = instances.BillDiscAmt
        # if BillDiscAmt:
        #     BillDiscAmt = round(BillDiscAmt,PriceRounding)
        # else:
        #     BillDiscAmt = 0

        return converted_float(BillDiscAmt)


class PurchaseReturnDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseReturnDetails
        fields = (
            "id",
            "BranchID",
            "Action",
            "PurchaseReturnMasterID",
            "DeliveryDetailsID",
            "OrderDetailsID",
            "ProductID",
            "Qty",
            "FreeQty",
            "UnitPrice",
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
            "AddlDiscPerc",
            "AddlDiscAmt",
            "TAX1Perc",
            "TAX1Amount",
            "TAX2Perc",
            "TAX2Amount",
            "TAX3Perc",
            "TAX3Amount",
        )


class PurchaseReturnDetailsRestSerializer(serializers.ModelSerializer):

    ProductName = serializers.SerializerMethodField()
    unq_id = serializers.SerializerMethodField()
    detailID = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()
    AddlDiscPerc = serializers.SerializerMethodField()
    AddlDiscAmt = serializers.SerializerMethodField()
    UnitPrice = serializers.SerializerMethodField()
    InclusivePrice = serializers.SerializerMethodField()
    DiscountPerc = serializers.SerializerMethodField()
    DiscountAmount = serializers.SerializerMethodField()
    Qty = serializers.SerializerMethodField()
    FreeQty = serializers.SerializerMethodField()
    RateWithTax = serializers.SerializerMethodField()
    CostPerPrice = serializers.SerializerMethodField()
    GrossAmount = serializers.SerializerMethodField()
    TaxableAmount = serializers.SerializerMethodField()
    VATAmount = serializers.SerializerMethodField()
    SGSTAmount = serializers.SerializerMethodField()
    CGSTAmount = serializers.SerializerMethodField()
    IGSTAmount = serializers.SerializerMethodField()
    TAX1Amount = serializers.SerializerMethodField()
    TAX2Amount = serializers.SerializerMethodField()
    TAX3Amount = serializers.SerializerMethodField()
    NetAmount = serializers.SerializerMethodField()
    is_VAT_inclusive = serializers.SerializerMethodField()
    is_GST_inclusive = serializers.SerializerMethodField()
    is_TAX1_inclusive = serializers.SerializerMethodField()
    is_TAX2_inclusive = serializers.SerializerMethodField()
    is_TAX3_inclusive = serializers.SerializerMethodField()
    unitPriceRounded = serializers.SerializerMethodField()
    quantityRounded = serializers.SerializerMethodField()
    actualPurchasePrice = serializers.SerializerMethodField()
    netAmountRounded = serializers.SerializerMethodField()
    BatchCode = serializers.SerializerMethodField()
    VATPerc = serializers.SerializerMethodField()
    SGSTPerc = serializers.SerializerMethodField()
    CGSTPerc = serializers.SerializerMethodField()
    IGSTPerc = serializers.SerializerMethodField()
    UnitList = serializers.SerializerMethodField()
    is_inclusive = serializers.SerializerMethodField()
    ActualUnitPrice = serializers.SerializerMethodField()
    ProductCode = serializers.SerializerMethodField()
    HSNCode = serializers.SerializerMethodField()
    GST_Inclusive = serializers.SerializerMethodField()
    Vat_Inclusive = serializers.SerializerMethodField()
    PurchasePrice = serializers.SerializerMethodField()
    ProductTaxName = serializers.SerializerMethodField()
    ActualProductTaxName = serializers.SerializerMethodField()
    ActualProductTaxID = serializers.SerializerMethodField()
    unitPrice_print = serializers.SerializerMethodField()
    NetAmount_print = serializers.SerializerMethodField()
    VATAmount_print = serializers.SerializerMethodField()
    VATPerc_print = serializers.SerializerMethodField()
    NetAmount_print = serializers.SerializerMethodField()
    DiscountAmount_print = serializers.SerializerMethodField()
    TaxableAmount_print = serializers.SerializerMethodField()
    product_description = serializers.SerializerMethodField()
    BatchList = serializers.SerializerMethodField()
    ManufactureDatePrint = serializers.SerializerMethodField()
    ExpiryDatePrint = serializers.SerializerMethodField()
    ProductCodeVal = serializers.SerializerMethodField()
    SerialNos = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseReturnDetails
        fields = (
            "id",
            "TaxableAmount_print",
            "DiscountAmount_print",
            "NetAmount_print",
            "VATAmount_print",
            "VATPerc_print",
            "NetAmount_print",
            "unitPrice_print",
            "PurchaseReturnDetailsID",
            "BranchID",
            "Action",
            "PurchaseReturnMasterID",
            "DeliveryDetailsID",
            "OrderDetailsID",
            "ProductID",
            "Qty",
            "FreeQty",
            "UnitPrice",
            "InclusivePrice",
            "ProductName",
            "unq_id",
            "detailID",
            "TotalTax",
            "UnitName",
            "AddlDiscPerc",
            "ProductTaxID",
            "RateWithTax",
            "CostPerPrice",
            "PriceListID",
            "DiscountPerc",
            "DiscountAmount",
            "AddlDiscAmt",
            "is_inclusive",
            "UnitList",
            "GrossAmount",
            "TaxableAmount",
            "VATPerc",
            "VATAmount",
            "SGSTPerc",
            "SGSTAmount",
            "CGSTPerc",
            "BatchCode",
            "ActualUnitPrice",
            "CGSTAmount",
            "IGSTPerc",
            "IGSTAmount",
            "NetAmount",
            "CreatedDate",
            "UpdatedDate",
            "CreatedUserID",
            "AddlDiscPerc",
            "AddlDiscAmt",
            "TAX1Perc",
            "TAX1Amount",
            "TAX2Perc",
            "TAX2Amount",
            "TAX3Perc",
            "TAX3Amount",
            "is_VAT_inclusive",
            "is_GST_inclusive",
            "is_TAX1_inclusive",
            "is_TAX2_inclusive",
            "is_TAX3_inclusive",
            "unitPriceRounded",
            "quantityRounded",
            "actualPurchasePrice",
            "netAmountRounded",
            "ProductCode",
            "HSNCode",
            "PurchasePrice",
            "GST_Inclusive",
            "Vat_Inclusive",
            "ProductTaxName",
            "ActualProductTaxName",
            "ActualProductTaxID",
            "product_description",
            "BatchList",
            "ManufactureDatePrint",
            "ExpiryDatePrint",
            "ProductCodeVal",
            "SerialNos",
            "Description"
        )

    def get_SerialNos(self, purchase_details):
        SerialNos = []
        CompanyID = self.context.get("CompanyID")
        BranchID = purchase_details.BranchID
        PurchaseReturnMasterID = purchase_details.PurchaseReturnMasterID
        PurchaseReturnDetailsID = purchase_details.PurchaseReturnDetailsID
        if SerialNumbers.objects.filter(
            CompanyID=CompanyID,
            BranchID=BranchID,
            SalesMasterID=PurchaseReturnMasterID,
            SalesDetailsID=PurchaseReturnDetailsID,
            VoucherType="PR",
        ).exists():
            Serial_details = SerialNumbers.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                SalesMasterID=PurchaseReturnMasterID,
                SalesDetailsID=PurchaseReturnDetailsID,
                VoucherType="PR",
            )
            SerialNos = SerialNumberSerializer(
                Serial_details, many=True, context={"CompanyID": CompanyID}
            )
            SerialNos = SerialNos.data
        return SerialNos

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
            ManufactureDate = batch_details.ManufactureDate
            if ManufactureDate:
                Date = ManufactureDate.strftime("%Y/%d")
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
            ExpiryDate = batch_details.ExpiryDate
            if ExpiryDate:
                Date = ExpiryDate.strftime("%Y/%d")
                ExpiryDate = Date
        return ExpiryDate

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

    def get_VATPerc_print(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        VATPerc = sales_details.VATPerc

        VATPerc = round(VATPerc, PriceRounding)

        return str(VATPerc)

    def get_VATAmount_print(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        VATAmount = sales_details.VATAmount
        print(VATAmount, "((((((((******))))))))")

        VATAmount = round(VATAmount, PriceRounding)

        return str(VATAmount)

    def get_NetAmount_print(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        NetAmount = purchaseReturn_details.NetAmount
        NetAmount = round(NetAmount, PriceRounding)
        return str(NetAmount)

    def get_unitPrice_print(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        UnitPrice = purchaseReturn_details.UnitPrice
        UnitPrice = round(UnitPrice, PriceRounding)
        return str(UnitPrice)

    def get_ActualProductTaxName(self, purchaseReturn_details):
        CompanyID = self.context.get("CompanyID")
        ProductTaxID = purchaseReturn_details.ProductTaxID
        BranchID = purchaseReturn_details.BranchID
        ActualProductTaxName = ""
        if TaxCategory.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, TaxID=ProductTaxID
        ).exists():
            ActualProductTaxName = TaxCategory.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, TaxID=ProductTaxID
            ).TaxName
        return str(ActualProductTaxName)

    def get_ActualProductTaxID(self, purchaseReturn_details):
        CompanyID = self.context.get("CompanyID")
        ActualProductTaxID = purchaseReturn_details.ProductTaxID
        return ActualProductTaxID

    def get_PurchasePrice(self, purchaseReturn_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = purchaseReturn_details.PriceListID
        BranchID = purchaseReturn_details.BranchID
        PurchasePrice = 0
        if PriceList.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID
        ).exists():
            PurchasePrice = PriceList.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID
            ).PurchasePrice
        return converted_float(PurchasePrice)

    def get_ProductTaxName(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        ProductTaxID = purchase_details.ProductTaxID
        BranchID = purchase_details.BranchID
        ProductTaxName = ""
        if TaxCategory.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, TaxID=ProductTaxID
        ).exists():
            ProductTaxName = TaxCategory.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, TaxID=ProductTaxID
            ).TaxName
        return str(ProductTaxName)

    def get_Vat_Inclusive(self, purchaseReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchaseReturn_details.BranchID
        ProductID = purchaseReturn_details.ProductID
        ProductTaxID = purchaseReturn_details.ProductTaxID
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

    def get_GST_Inclusive(self, purchaseReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchaseReturn_details.BranchID
        ProductID = purchaseReturn_details.ProductID
        ProductTaxID = purchaseReturn_details.ProductTaxID
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

    def get_ProductName(self, purchaseReturn_details):
        CompanyID = self.context.get("CompanyID")
        ProductID = purchaseReturn_details.ProductID
        BranchID = purchaseReturn_details.BranchID

        if Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID).exists():

            product = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)
            ProductName = product.ProductName
        else:
            ProductName = ""

        return ProductName

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

    def get_ActualUnitPrice(self, sales_details):
        PriceRounding = self.context.get("PriceRounding")
        ActualUnitPrice = sales_details.UnitPrice

        # ActualUnitPrice = round(ActualUnitPrice, PriceRounding)
        return converted_float(ActualUnitPrice)

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

    def get_is_inclusive(self, purchase_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchase_details.BranchID
        ProductID = purchase_details.ProductID
        pro_ins = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID)
        GST = pro_ins.GST
        VatID = pro_ins.VatID
        Tax1 = pro_ins.Tax1
        Tax2 = pro_ins.Tax2
        Tax3 = pro_ins.Tax3
        is_inclusive = False
        GST_inclusive = False
        VAT_inclusive = False
        Tax1_inclusive = False
        Tax2_inclusive = False
        Tax3_inclusive = False
        if GST:
            GST_inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=GST
            ).Inclusive
        if VatID:
            VAT_inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=VatID
            ).Inclusive
        if Tax1:
            Tax1_inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax1
            ).Inclusive
        if Tax2:
            Tax2_inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax2
            ).Inclusive
        if Tax3:
            Tax3_inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax3
            ).Inclusive

        if (
            GST_inclusive == True
            or VAT_inclusive == True
            or Tax1_inclusive == True
            or Tax2_inclusive == True
            or Tax3_inclusive == True
        ):
            is_inclusive = True

        return is_inclusive

    def get_BatchCode(self, purchaseReturn_details):
        CompanyID = self.context.get("CompanyID")
        BatchCode = purchaseReturn_details.BatchCode
        BranchID = purchaseReturn_details.BranchID
        if not BatchCode:
            BatchCode = 0

        return BatchCode

    def get_VATPerc(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        VATPerc = purchaseReturn_details.VATPerc

        # if VATPerc:
        #     VATPerc = round(VATPerc, PriceRounding)
        # else:
        #     VATPerc = 0

        return converted_float(VATPerc)

    def get_SGSTPerc(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        SGSTPerc = purchaseReturn_details.SGSTPerc

        # if SGSTPerc:
        #     SGSTPerc = round(SGSTPerc, PriceRounding)
        # else:
        #     SGSTPerc = 0

        return converted_float(SGSTPerc)

    def get_CGSTPerc(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        CGSTPerc = purchaseReturn_details.CGSTPerc

        # if CGSTPerc:
        #     CGSTPerc = round(CGSTPerc, PriceRounding)
        # else:
        #     CGSTPerc = 0

        return converted_float(CGSTPerc)

    def get_IGSTPerc(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        IGSTPerc = purchaseReturn_details.IGSTPerc

        # if IGSTPerc:
        #     IGSTPerc = round(IGSTPerc, PriceRounding)
        # else:
        #     IGSTPerc = 0

        return converted_float(IGSTPerc)

    def get_InclusivePrice(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        # PriceRounding = 2
        InclusivePrice = purchaseReturn_details.InclusivePrice
        # if InclusivePrice:
        #     InclusivePrice = round(InclusivePrice,PriceRounding)
        # else:
        #     InclusivePrice = 0

        return converted_float(InclusivePrice)

    def get_unitPriceRounded(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        UnitPrice = purchaseReturn_details.UnitPrice
        # UnitPrice = round(UnitPrice,PriceRounding)
        return converted_float(UnitPrice)

    def get_quantityRounded(self, purchaseReturn_details):
        Qty = purchaseReturn_details.Qty
        return str(Qty)

    def get_actualPurchasePrice(self, purchaseReturn_details):
        CompanyID = self.context.get("CompanyID")
        PriceListID = purchaseReturn_details.PriceListID
        BranchID = purchaseReturn_details.BranchID
        ProductID = purchaseReturn_details.ProductID
        PurchasePrice = 0
        if PriceList.objects.filter(
            ProductID=ProductID, CompanyID=CompanyID, PriceListID=PriceListID
        ).exists():
            PurchasePrice = PriceList.objects.get(
                ProductID=ProductID, CompanyID=CompanyID, PriceListID=PriceListID
            ).PurchasePrice
        return converted_float(PurchasePrice)

    def get_netAmountRounded(self, purchaseReturn_details):
        NetAmount = purchaseReturn_details.NetAmount
        return str(NetAmount)

    def get_is_VAT_inclusive(self, purchaseReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchaseReturn_details.BranchID
        ProductID = purchaseReturn_details.ProductID
        Inclusive = False
        VatID = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID).VatID
        if VatID:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=VatID
            ).Inclusive
        return Inclusive

    def get_is_GST_inclusive(self, purchaseReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchaseReturn_details.BranchID
        ProductID = purchaseReturn_details.ProductID
        Inclusive = False
        GST = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID).GST
        if GST:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=GST
            ).Inclusive
        return Inclusive

    def get_is_TAX1_inclusive(self, purchaseReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchaseReturn_details.BranchID
        ProductID = purchaseReturn_details.ProductID
        Inclusive = False
        Tax1 = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID).Tax1
        if Tax1:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax1
            ).Inclusive
        return Inclusive

    def get_is_TAX2_inclusive(self, purchaseReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchaseReturn_details.BranchID
        ProductID = purchaseReturn_details.ProductID
        Inclusive = False
        Tax2 = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID).Tax2
        if Tax2:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax2
            ).Inclusive
        return Inclusive

    def get_is_TAX3_inclusive(self, purchaseReturn_details):
        CompanyID = self.context.get("CompanyID")
        BranchID = purchaseReturn_details.BranchID
        ProductID = purchaseReturn_details.ProductID
        Inclusive = False
        Tax3 = Product.objects.get(CompanyID=CompanyID, ProductID=ProductID).Tax3
        if Tax3:
            Inclusive = TaxCategory.objects.get(
                CompanyID=CompanyID, TaxID=Tax3
            ).Inclusive
        return Inclusive

    def get_UnitPrice(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        UnitPrice = purchaseReturn_details.UnitPrice

        # if UnitPrice:
        #     UnitPrice = round(UnitPrice,PriceRounding)
        # else:
        #     UnitPrice = 0

        return converted_float(UnitPrice)

    def get_Qty(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        Qty = purchaseReturn_details.Qty

        # if Qty:
        #     Qty = round(Qty,PriceRounding)
        # else:
        #     Qty = 0

        return converted_float(Qty)

    def get_FreeQty(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        FreeQty = purchaseReturn_details.FreeQty

        # if FreeQty:
        #     FreeQty = round(FreeQty,PriceRounding)
        # else:
        #     FreeQty = 0

        return converted_float(FreeQty)

    def get_RateWithTax(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        RateWithTax = purchaseReturn_details.RateWithTax

        # if RateWithTax:
        #     RateWithTax = round(RateWithTax,PriceRounding)
        # else:
        #     RateWithTax = 0

        return converted_float(RateWithTax)

    def get_CostPerPrice(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        CostPerPrice = purchaseReturn_details.CostPerPrice

        # if CostPerPrice:
        #     CostPerPrice = round(CostPerPrice,PriceRounding)
        # else:
        #     CostPerPrice = 0

        return converted_float(CostPerPrice)

    def get_GrossAmount(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        GrossAmount = purchaseReturn_details.GrossAmount

        # if GrossAmount:
        #     GrossAmount = round(GrossAmount,PriceRounding)
        # else:
        #     GrossAmount = 0

        return converted_float(GrossAmount)

    def get_TaxableAmount(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        TaxableAmount = purchaseReturn_details.TaxableAmount

        # if TaxableAmount:
        #     TaxableAmount = round(TaxableAmount,PriceRounding)
        # else:
        #     TaxableAmount = 0

        return converted_float(TaxableAmount)

    def get_VATAmount(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        VATAmount = purchaseReturn_details.VATAmount

        # if VATAmount:
        #     VATAmount = round(VATAmount,PriceRounding)
        # else:
        #     VATAmount = 0

        return converted_float(VATAmount)

    def get_SGSTAmount(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        SGSTAmount = purchaseReturn_details.SGSTAmount

        # if SGSTAmount:
        #     SGSTAmount = round(SGSTAmount,PriceRounding)
        # else:
        #     SGSTAmount = 0

        return converted_float(SGSTAmount)

    def get_CGSTAmount(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        CGSTAmount = purchaseReturn_details.CGSTAmount

        # if CGSTAmount:
        #     CGSTAmount = round(CGSTAmount,PriceRounding)
        # else:
        #     CGSTAmount = 0

        return converted_float(CGSTAmount)

    def get_IGSTAmount(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        IGSTAmount = purchaseReturn_details.IGSTAmount

        # if IGSTAmount:
        #     IGSTAmount = round(IGSTAmount,PriceRounding)
        # else:
        #     IGSTAmount = 0

        return converted_float(IGSTAmount)

    def get_TAX1Amount(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX1Amount = purchaseReturn_details.TAX1Amount

        # if TAX1Amount:
        #     TAX1Amount = round(TAX1Amount,PriceRounding)
        # else:
        #     TAX1Amount = 0

        return converted_float(TAX1Amount)

    def get_TAX2Amount(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX2Amount = purchaseReturn_details.TAX2Amount

        # if TAX2Amount:
        #     TAX2Amount = round(TAX2Amount,PriceRounding)
        # else:
        #     TAX2Amount = 0

        return converted_float(TAX2Amount)

    def get_TAX3Amount(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX3Amount = purchaseReturn_details.TAX3Amount

        # if TAX3Amount:
        #     TAX3Amount = round(TAX3Amount,PriceRounding)
        # else:
        #     TAX3Amount = 0

        return converted_float(TAX3Amount)

    def get_NetAmount(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        NetAmount = purchaseReturn_details.NetAmount

        # if NetAmount:
        #     NetAmount = round(NetAmount,PriceRounding)
        # else:
        #     NetAmount = 0

        return converted_float(NetAmount)

    def get_DiscountPerc(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        DiscountPerc = purchaseReturn_details.DiscountPerc

        # if DiscountPerc:
        #     DiscountPerc = round(DiscountPerc,PriceRounding)
        # else:
        #     DiscountPerc = 0

        return converted_float(DiscountPerc)

    def get_DiscountAmount(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        DiscountAmount = purchaseReturn_details.DiscountAmount

        # if DiscountAmount:
        #     DiscountAmount = round(DiscountAmount,PriceRounding)
        # else:
        #     DiscountAmount = 0

        return converted_float(DiscountAmount)

    def get_AddlDiscPerc(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        AddlDiscPerc = purchaseReturn_details.AddlDiscPerc

        # if AddlDiscPerc:
        #     AddlDiscPerc = round(AddlDiscPerc,PriceRounding)
        # else:
        #     AddlDiscPerc = 0

        return converted_float(AddlDiscPerc)

    def get_AddlDiscAmt(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        AddlDiscAmt = purchaseReturn_details.AddlDiscAmt

        # if AddlDiscAmt:
        #     AddlDiscAmt = round(AddlDiscAmt,PriceRounding)
        # else:
        #     AddlDiscAmt = 0

        return converted_float(AddlDiscAmt)

    def get_UnitName(self, purchaseReturn_details):

        CompanyID = self.context.get("CompanyID")

        PriceListID = purchaseReturn_details.PriceListID
        BranchID = purchaseReturn_details.BranchID

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

    def get_TotalTax(self, purchaseReturn_details):

        CompanyID = self.context.get("CompanyID")

        TAX1Amount = purchaseReturn_details.TAX1Amount
        TAX2Amount = purchaseReturn_details.TAX2Amount
        TAX3Amount = purchaseReturn_details.TAX3Amount
        VATAmount = purchaseReturn_details.VATAmount
        IGSTAmount = purchaseReturn_details.IGSTAmount
        SGSTAmount = purchaseReturn_details.SGSTAmount
        CGSTAmount = purchaseReturn_details.CGSTAmount

        TotalTax = (
            TAX1Amount
            + TAX2Amount
            + TAX3Amount
            + VATAmount
            + IGSTAmount
            + SGSTAmount
            + CGSTAmount
        )

        return converted_float(TotalTax)

    def get_unq_id(self, purchaseReturn_details):

        CompanyID = self.context.get("CompanyID")

        unq_id = purchaseReturn_details.id

        return str(unq_id)

    def get_detailID(self, purchaseReturn_details):

        detailID = 0
        return detailID


class PurchaseReturnPrintSerializer(serializers.ModelSerializer):

    Details = serializers.SerializerMethodField()
    LedgerName = serializers.SerializerMethodField()
    DetailID = serializers.SerializerMethodField()
    PurchaseAccountName = serializers.SerializerMethodField()
    WareHouseName = serializers.SerializerMethodField()
    AddlDiscPercent = serializers.SerializerMethodField()
    BillDiscPercent = serializers.SerializerMethodField()
    RoundOff = serializers.SerializerMethodField()
    TotalTax = serializers.SerializerMethodField()
    GrandTotal = serializers.SerializerMethodField()
    TotalGrossAmt = serializers.SerializerMethodField()
    AddlDiscAmt = serializers.SerializerMethodField()
    NetTotal = serializers.SerializerMethodField()
    TotalDiscount = serializers.SerializerMethodField()
    VATAmount = serializers.SerializerMethodField()
    SGSTAmount = serializers.SerializerMethodField()
    CGSTAmount = serializers.SerializerMethodField()
    IGSTAmount = serializers.SerializerMethodField()
    TAX1Amount = serializers.SerializerMethodField()
    TAX2Amount = serializers.SerializerMethodField()
    TAX3Amount = serializers.SerializerMethodField()
    BillDiscAmt = serializers.SerializerMethodField()
    TaxNo = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseReturnMaster
        fields = (
            "PurchaseReturnMasterID",
            "BranchID",
            "Action",
            "VoucherNo",
            "VoucherDate",
            "RefferenceBillNo",
            "RefferenceBillDate",
            "VenderInvoiceDate",
            "CreditPeriod",
            "DetailID",
            "WareHouseName",
            "LedgerID",
            "LedgerName",
            "PriceCategoryID",
            "EmployeeID",
            "PurchaseAccount",
            "PurchaseAccountName",
            "DeliveryMasterID",
            "OrderMasterID",
            "CustomerName",
            "Address1",
            "Address2",
            "Address3",
            "Notes",
            "FinacialYearID",
            "TotalGrossAmt",
            "TotalTax",
            "TaxNo",
            "NetTotal",
            "AdditionalCost",
            "GrandTotal",
            "RoundOff",
            "WarehouseID",
            "IsActive",
            "CreatedDate",
            "UpdatedDate",
            "CreatedUserID",
            "TaxID",
            "TaxType",
            "VATAmount",
            "SGSTAmount",
            "CGSTAmount",
            "IGSTAmount",
            "TAX1Amount",
            "TAX2Amount",
            "TAX3Amount",
            "AddlDiscPercent",
            "AddlDiscAmt",
            "TotalDiscount",
            "BillDiscPercent",
            "BillDiscAmt",
            "Details",
        )

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

    def get_Details(self, instances):
        CompanyID = self.context.get("CompanyID")
        PriceRounding = int(self.context.get("PriceRounding"))
        BranchID = instances.BranchID
        purchaseReturn_details = PurchaseReturnDetails.objects.filter(
            CompanyID=CompanyID,
            PurchaseReturnMasterID=instances.PurchaseReturnMasterID,
            BranchID=BranchID,
        )
        serialized = PurchaseReturnDetailsPrintSerializer(
            purchaseReturn_details,
            many=True,
            context={"CompanyID": CompanyID, "PriceRounding": PriceRounding},
        )

        return serialized.data

    def get_DetailID(self, instances):

        return ""

    def get_WareHouseName(self, instances):
        CompanyID = self.context.get("CompanyID")

        WarehouseID = instances.WarehouseID
        BranchID = instances.BranchID

        wareHouse = Warehouse.objects.get(CompanyID=CompanyID, WarehouseID=WarehouseID)

        WareHouseName = wareHouse.WarehouseName

        return WareHouseName

    def get_PurchaseAccountName(self, instances):
        CompanyID = self.context.get("CompanyID")

        PurchaseAccount = instances.PurchaseAccount
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(
            CompanyID=CompanyID, LedgerID=PurchaseAccount, BranchID=BranchID
        )

        PurchaseAccountName = ledger.LedgerName

        return PurchaseAccountName

    def get_LedgerName(self, instances):
        CompanyID = self.context.get("CompanyID")

        LedgerID = instances.LedgerID
        BranchID = instances.BranchID

        ledger = AccountLedger.objects.get(CompanyID=CompanyID, LedgerID=LedgerID)

        LedgerName = ledger.LedgerName

        return LedgerName

    def get_AddlDiscPercent(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        AddlDiscPercent = instances.AddlDiscPercent

        if AddlDiscPercent:
            AddlDiscPercent = round(AddlDiscPercent, PriceRounding)
        else:
            AddlDiscPercent = 0

        return converted_float(AddlDiscPercent)

    def get_BillDiscPercent(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        BillDiscPercent = instances.BillDiscPercent

        if BillDiscPercent:
            BillDiscPercent = round(BillDiscPercent, PriceRounding)
        else:
            BillDiscPercent = 0

        return converted_float(BillDiscPercent)

    def get_RoundOff(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        RoundOff = instances.RoundOff

        if RoundOff:
            RoundOff = round(RoundOff, PriceRounding)
        else:
            RoundOff = 0

        return converted_float(RoundOff)

    def get_TotalTax(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalTax = instances.TotalTax

        if TotalTax:
            TotalTax = round(TotalTax, PriceRounding)
        else:
            TotalTax = 0

        return converted_float(TotalTax)

    def get_GrandTotal(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))

        GrandTotal = instances.GrandTotal

        if GrandTotal:
            GrandTotal = round(GrandTotal, PriceRounding)
        else:
            GrandTotal = 0

        return converted_float(GrandTotal)

    def get_TotalGrossAmt(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))

        TotalGrossAmt = instances.TotalGrossAmt

        if TotalGrossAmt:
            TotalGrossAmt = round(TotalGrossAmt, PriceRounding)
        else:
            TotalGrossAmt = 0

        return converted_float(TotalGrossAmt)

    def get_AddlDiscAmt(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        AddlDiscAmt = instances.AddlDiscAmt
        if AddlDiscAmt:
            AddlDiscAmt = round(AddlDiscAmt, PriceRounding)
        else:
            AddlDiscAmt = 0

        return converted_float(AddlDiscAmt)

    def get_NetTotal(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        NetTotal = instances.NetTotal
        if NetTotal:
            NetTotal = round(NetTotal, PriceRounding)
        else:
            NetTotal = 0

        return converted_float(NetTotal)

    def get_TotalDiscount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TotalDiscount = instances.TotalDiscount
        if TotalDiscount:
            TotalDiscount = round(TotalDiscount, PriceRounding)
        else:
            TotalDiscount = 0

        return converted_float(TotalDiscount)

    def get_VATAmount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        VATAmount = instances.VATAmount
        if VATAmount:
            VATAmount = round(VATAmount, PriceRounding)
        else:
            VATAmount = 0

        return converted_float(VATAmount)

    def get_SGSTAmount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        SGSTAmount = instances.SGSTAmount
        if SGSTAmount:
            SGSTAmount = round(SGSTAmount, PriceRounding)
        else:
            SGSTAmount = 0

        return converted_float(SGSTAmount)

    def get_CGSTAmount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        CGSTAmount = instances.CGSTAmount
        if CGSTAmount:
            CGSTAmount = round(CGSTAmount, PriceRounding)
        else:
            CGSTAmount = 0

        return converted_float(CGSTAmount)

    def get_IGSTAmount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        IGSTAmount = instances.IGSTAmount
        if IGSTAmount:
            IGSTAmount = round(IGSTAmount, PriceRounding)
        else:
            IGSTAmount = 0

        return converted_float(IGSTAmount)

    def get_TAX1Amount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX1Amount = instances.TAX1Amount
        if TAX1Amount:
            TAX1Amount = round(TAX1Amount, PriceRounding)
        else:
            TAX1Amount = 0

        return converted_float(TAX1Amount)

    def get_TAX2Amount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX2Amount = instances.TAX2Amount
        if TAX2Amount:
            TAX2Amount = round(TAX2Amount, PriceRounding)
        else:
            TAX2Amount = 0

        return converted_float(TAX2Amount)

    def get_TAX3Amount(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        TAX3Amount = instances.TAX3Amount
        if TAX3Amount:
            TAX3Amount = round(TAX3Amount, PriceRounding)
        else:
            TAX3Amount = 0

        return converted_float(TAX3Amount)

    def get_BillDiscAmt(self, instances):
        PriceRounding = int(self.context.get("PriceRounding"))
        BillDiscAmt = instances.BillDiscAmt
        if BillDiscAmt:
            BillDiscAmt = round(BillDiscAmt, PriceRounding)
        else:
            BillDiscAmt = 0

        return converted_float(BillDiscAmt)


class PurchaseReturnDetailsPrintSerializer(serializers.ModelSerializer):

    ProductName = serializers.SerializerMethodField()
    UnitPrice = serializers.SerializerMethodField()
    Qty = serializers.SerializerMethodField()
    NetAmount = serializers.SerializerMethodField()
    UnitName = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseReturnDetails
        fields = ("Qty", "UnitPrice", "ProductName", "NetAmount", "UnitName")

    def get_ProductName(self, purchaseReturn_details):

        CompanyID = self.context.get("CompanyID")
        ProductID = purchaseReturn_details.ProductID
        BranchID = purchaseReturn_details.BranchID

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
            CompanyID=CompanyID, PriceListID=PriceListID
        ).exists():
            UnitID = PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListID
            ).UnitID
            UnitName = Unit.objects.get(
                BranchID=BranchID, UnitID=UnitID, CompanyID=CompanyID
            ).UnitName

        return UnitName

    def get_UnitPrice(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        UnitPrice = purchaseReturn_details.UnitPrice

        if UnitPrice:
            UnitPrice = round(UnitPrice, PriceRounding)
        else:
            UnitPrice = 0

        return str(UnitPrice)

    def get_Qty(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        Qty = purchaseReturn_details.Qty

        if Qty:
            Qty = round(Qty, PriceRounding)
        else:
            Qty = 0

        return str(Qty)

    def get_NetAmount(self, purchaseReturn_details):
        PriceRounding = int(self.context.get("PriceRounding"))
        NetAmount = purchaseReturn_details.NetAmount

        if NetAmount:
            NetAmount = round(NetAmount, PriceRounding)
        else:
            NetAmount = 0

        return str(NetAmount)


class QRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QrCode
        fields = ("qr_code",)
