import datetime
import os
import re
import sys

from django.db import IntegrityError, transaction
from django.db.models import Prefetch, Q, Sum
from api.v10.reportQuerys.functions import salesReturn_register_report_data
from fatoora import Fatoora
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, renderer_classes,authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from api.v10.accountLedgers.functions import UpdateLedgerBalance, get_auto_LedgerPostid
from api.v10.brands.serializers import ListSerializer
from api.v10.loyaltyProgram.functions import get_point_auto_id
from api.v10.products.functions import get_auto_AutoBatchCode, update_stock
from api.v10.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
from api.v10.sales.functions import (
    SetBatchInSales,
    get_BillwiseDetailsID,
    get_BillwiseMasterID,
    get_actual_point,
    get_auto_stockPostid,
    get_Genrate_VoucherNo,
    handleBillwiseChanges,
)
from api.v10.sales.serializers import ListSerializerforReport
from api.v10.salesReturns.functions import (
    generate_serializer_errors,
    get_auto_id,
    get_auto_idMaster,
    sales_return_point,
)
from api.v10.salesReturns.serializers import (
    SalesReturnDetailsRestSerializer,
    SalesReturnDetailsSerializer,
    SalesReturnMaster1RestSerializer,
    SalesReturnMasterReportSerializer,
    SalesReturnMasterRestSerializer,
    SalesReturnMasterSerializer,
)
from brands.models import (
    AccountLedger,
    Batch,
    BillWiseDetails,
    BillWiseMaster,
    Branch,
    Customer,
    GeneralSettings,
    LedgerPosting,
    LedgerPosting_Log,
    LoyaltyCustomer,
    LoyaltyPoint,
    LoyaltyPoint_Log,
    LoyaltyProgram,
    Parties,
    PriceList,
    Product,
    ProductGroup,
    QrCode,
    SalesDetails,
    SalesMaster,
    SalesReturnDetails,
    SalesReturnDetails_Log,
    SalesReturnDetailsDummy,
    SalesReturnMaster,
    SalesReturnMaster_Log,
    SerialNumbers,
    StockPosting,
    StockPosting_Log,
    StockRate,
    StockTrans,
    UserAdrress,
    UserTable,
    VoucherNoTable,
    Warehouse,
)
from main.functions import (
    activity_log,
    converted_float,
    get_GeneralSettings,
    get_LedgerBalance,
    get_company,
    get_ModelInstance,
    get_nth_day_date,
    list_pagination,
    update_voucher_table,
)


@api_view(["POST"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def create_salesReturn(request):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data["CompanyID"]
            CompanyID = get_company(CompanyID)
            CreatedUserID = data["CreatedUserID"]
            PriceRounding = data["PriceRounding"]

            today = datetime.datetime.now()
            BranchID = data["BranchID"]
            VoucherDate = data["VoucherDate"]
            VoucherNo = data["VoucherNo"]
            RefferenceBillNo = data["RefferenceBillNo"]
            RefferenceBillDate = data["RefferenceBillDate"]
            CreditPeriod = data["CreditPeriod"]
            LedgerID = data["LedgerID"]
            PriceCategoryID = data["PriceCategoryID"]
            EmployeeID = data["EmployeeID"]
            SalesAccount = data["SalesAccount"]
            DeliveryMasterID = data["DeliveryMasterID"]
            OrderMasterID = data["OrderMasterID"]
            CustomerName = data["CustomerName"]
            Address1 = data["Address1"]
            Address2 = data["Address2"]
            Address3 = data["Address3"]
            Notes = data["Notes"]
            FinacialYearID = data["FinacialYearID"]
            WarehouseID = data["WarehouseID"]
            TableID = data["TableID"]
            SeatNumber = data["SeatNumber"]
            NoOfGuests = data["NoOfGuests"]
            INOUT = data["INOUT"]
            TokenNumber = data["TokenNumber"]
            IsActive = data["IsActive"]
            IsPosted = data["IsPosted"]
            SalesType = data["SalesType"]
            BatchID = data["BatchID"]
            try:
                TaxID = data["TaxID"]
            except:
                TaxID = 1
            try:
                TaxType = data["TaxType"]
            except:
                TaxType = ""
            # CashAmount = data['CashAmount']

            TotalGrossAmt = converted_float(data["TotalGrossAmt"])
            TotalTax = converted_float(data["TotalTax"])
            NetTotal = converted_float(data["NetTotal"])
            AdditionalCost = converted_float(data["AdditionalCost"])
            GrandTotal = converted_float(data["GrandTotal"])
            RoundOff = converted_float(data["RoundOff"])
            CashReceived = converted_float(data["CashReceived"])
            BankAmount = converted_float(data["BankAmount"])
            VATAmount = converted_float(data["VATAmount"])
            SGSTAmount = converted_float(data["SGSTAmount"])
            CGSTAmount = converted_float(data["CGSTAmount"])
            IGSTAmount = converted_float(data["IGSTAmount"])
            TAX1Amount = converted_float(data["TAX1Amount"])
            TAX2Amount = converted_float(data["TAX2Amount"])
            TAX3Amount = converted_float(data["TAX3Amount"])
            AddlDiscPercent = converted_float(data["AddlDiscPercent"])
            AddlDiscAmt = converted_float(data["AddlDiscAmt"])
            TotalDiscount = converted_float(data["TotalDiscount"])
            BillDiscPercent = converted_float(data["BillDiscPercent"])
            BillDiscAmt = converted_float(data["BillDiscAmt"])
            try:
                TaxTaxableAmount = converted_float(data["TaxTaxableAmount"])
            except:
                TaxTaxableAmount = 0
            try:
                NonTaxTaxableAmount = converted_float(data["NonTaxTaxableAmount"])
            except:
                NonTaxTaxableAmount = 0
            try:
                KFCAmount = converted_float(data["KFCAmount"])
            except:
                KFCAmount = 0

            salesReturnDetails = data["SalesReturnDetails"]
            TotalTaxableAmount = 0
            for salesReturnDetail in salesReturnDetails:
                TaxableAmount = salesReturnDetail["TaxableAmount"]
                TotalTaxableAmount += converted_float(TaxableAmount)

            # TotalGrossAmt = round(TotalGrossAmt, PriceRounding)
            # TotalTax = round(TotalTax, PriceRounding)
            # NetTotal = round(NetTotal, PriceRounding)
            # AdditionalCost = round(AdditionalCost, PriceRounding)
            # GrandTotal = round(GrandTotal, PriceRounding)

            # RoundOff = round(RoundOff, PriceRounding)
            # CashReceived = round(CashReceived, PriceRounding)
            # BankAmount = round(BankAmount, PriceRounding)
            # VATAmount = round(VATAmount, PriceRounding)
            # SGSTAmount = round(SGSTAmount, PriceRounding)

            # CGSTAmount = round(CGSTAmount, PriceRounding)
            # IGSTAmount = round(IGSTAmount, PriceRounding)
            # TAX1Amount = round(TAX1Amount, PriceRounding)
            # TAX2Amount = round(TAX2Amount, PriceRounding)
            # TAX3Amount = round(TAX3Amount, PriceRounding)

            # AddlDiscPercent = round(AddlDiscPercent, PriceRounding)
            # AddlDiscAmt = round(AddlDiscAmt, PriceRounding)
            # TotalDiscount = round(TotalDiscount, PriceRounding)
            # BillDiscPercent = round(BillDiscPercent, PriceRounding)
            # BillDiscAmt = round(BillDiscAmt, PriceRounding)
            # KFCAmount = round(KFCAmount, PriceRounding)

            Action = "A"

            try:
                Country_of_Supply = data["Country_of_Supply"]
            except:
                Country_of_Supply = ""

            try:
                State_of_Supply = data["State_of_Supply"]
            except:
                State_of_Supply = ""

            try:
                GST_Treatment = data["GST_Treatment"]
            except:
                GST_Treatment = ""

            try:
                VAT_Treatment = data["VAT_Treatment"]
            except:
                VAT_Treatment = ""

            VoucherType = "SR"

            # VoucherNo Updated
            try:
                PreFix = data["PreFix"]
            except:
                PreFix = "SR"

            try:
                Seperator = data["Seperator"]
            except:
                Seperator = ""

            try:
                InvoiceNo = data["InvoiceNo"]
            except:
                InvoiceNo = 1
                
            try:
                BillingAddress = data["BillingAddress"]
            except:
                BillingAddress = None
                
            Cash_Account = None
            Bank_Account = None

            if UserTable.objects.filter(
                CompanyID=CompanyID, customer__user__pk=CreatedUserID,Active=True
            ).exists():
                Cash_Account = UserTable.objects.get(
                    CompanyID=CompanyID, customer__user__pk=CreatedUserID,Active=True
                ).Cash_Account
                Bank_Account = UserTable.objects.get(
                    CompanyID=CompanyID, customer__user__pk=CreatedUserID, Active=True
                ).Bank_Account

            try:
                CashID = data["CashID"]
            except:
                CashID = Cash_Account

            try:
                BankID = data["BankID"]
            except:
                BankID = Bank_Account
                
            if BillingAddress:
                if UserAdrress.objects.filter(id=BillingAddress).exists():
                    BillingAddress = UserAdrress.objects.get(
                        id=BillingAddress)
                    
            # checking voucher number already exist
            VoucherNoLow = VoucherNo.lower()
            is_voucherExist = False
            insts = SalesReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID
            )
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True

            check_VoucherNoAutoGenerate = False
            is_SalesReturnOK = True

            if GeneralSettings.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                SettingsType="VoucherNoAutoGenerate",
            ).exists():
                check_VoucherNoAutoGenerate = GeneralSettings.objects.get(
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    SettingsType="VoucherNoAutoGenerate",
                ).SettingsValue

            if is_voucherExist == True and check_VoucherNoAutoGenerate == "True":
                VoucherNo = get_Genrate_VoucherNo(
                    SalesReturnMaster, BranchID, CompanyID, "SR"
                )
                is_SalesReturnOK = True
            elif is_voucherExist == False:
                is_SalesReturnOK = True
            else:
                is_SalesReturnOK = False

            if is_SalesReturnOK:

                SalesReturnMasterID = get_auto_idMaster(
                    SalesReturnMaster, BranchID, CompanyID
                )

                # if Parties.objects.filter(
                #     CompanyID=CompanyID, LedgerID=LedgerID
                # ).exists():

                #     party_instances = Parties.objects.filter(
                #         CompanyID=CompanyID, LedgerID=LedgerID
                #     )

                #     for party_instance in party_instances:

                #         party_instance.PartyName = CustomerName

                #         party_instance.save()

                CashAmount = converted_float(GrandTotal) - converted_float(BankAmount)

                LoyaltyCustomerID = data["LoyaltyCustomerID"]

                loyalty_customer = None
                is_LoyaltyCustomer = False
                if LoyaltyCustomerID:
                    if LoyaltyCustomer.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        LoyaltyCustomerID=LoyaltyCustomerID,
                    ).exists():
                        loyalty_customer = LoyaltyCustomer.objects.get(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            LoyaltyCustomerID=LoyaltyCustomerID,
                        )
                        is_LoyaltyCustomer = True

                update_voucher_table(
                    CompanyID, CreatedUserID, VoucherType, PreFix, Seperator, InvoiceNo
                )

                SalesReturnMaster_Log.objects.create(
                    LoyaltyCustomerID=loyalty_customer,
                    TotalTaxableAmount=TotalTaxableAmount,
                    TransactionID=SalesReturnMasterID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    VoucherDate=VoucherDate,
                    RefferenceBillNo=RefferenceBillNo,
                    RefferenceBillDate=RefferenceBillDate,
                    CreditPeriod=CreditPeriod,
                    LedgerID=LedgerID,
                    PriceCategoryID=PriceCategoryID,
                    EmployeeID=EmployeeID,
                    SalesAccount=SalesAccount,
                    DeliveryMasterID=DeliveryMasterID,
                    OrderMasterID=OrderMasterID,
                    CustomerName=CustomerName,
                    Address1=Address1,
                    Address2=Address2,
                    Address3=Address3,
                    Notes=Notes,
                    FinacialYearID=FinacialYearID,
                    TotalGrossAmt=TotalGrossAmt,
                    TotalTax=TotalTax,
                    NetTotal=NetTotal,
                    AdditionalCost=AdditionalCost,
                    GrandTotal=GrandTotal,
                    RoundOff=RoundOff,
                    CashReceived=CashReceived,
                    CashAmount=CashAmount,
                    BankAmount=BankAmount,
                    WarehouseID=WarehouseID,
                    TableID=TableID,
                    SeatNumber=SeatNumber,
                    NoOfGuests=NoOfGuests,
                    INOUT=INOUT,
                    TokenNumber=TokenNumber,
                    IsActive=IsActive,
                    IsPosted=IsPosted,
                    SalesType=SalesType,
                    CreatedUserID=CreatedUserID,
                    UpdatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    TaxID=TaxID,
                    TaxType=TaxType,
                    VATAmount=VATAmount,
                    SGSTAmount=SGSTAmount,
                    CGSTAmount=CGSTAmount,
                    IGSTAmount=IGSTAmount,
                    TAX1Amount=TAX1Amount,
                    TAX2Amount=TAX2Amount,
                    TAX3Amount=TAX3Amount,
                    AddlDiscPercent=AddlDiscPercent,
                    AddlDiscAmt=AddlDiscAmt,
                    TotalDiscount=TotalDiscount,
                    BillDiscPercent=BillDiscPercent,
                    BillDiscAmt=BillDiscAmt,
                    CompanyID=CompanyID,
                    KFCAmount=KFCAmount,
                    Country_of_Supply=Country_of_Supply,
                    State_of_Supply=State_of_Supply,
                    GST_Treatment=GST_Treatment,
                    VAT_Treatment=VAT_Treatment,
                    TaxTaxableAmount=TaxTaxableAmount,
                    NonTaxTaxableAmount=NonTaxTaxableAmount,
                    BillingAddress=BillingAddress,
                    CashID=CashID,
                    BankID=BankID,
                )

                sales_return_instance = SalesReturnMaster.objects.create(
                    LoyaltyCustomerID=loyalty_customer,
                    TotalTaxableAmount=TotalTaxableAmount,
                    SalesReturnMasterID=SalesReturnMasterID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    VoucherDate=VoucherDate,
                    RefferenceBillNo=RefferenceBillNo,
                    RefferenceBillDate=RefferenceBillDate,
                    CreditPeriod=CreditPeriod,
                    LedgerID=LedgerID,
                    PriceCategoryID=PriceCategoryID,
                    EmployeeID=EmployeeID,
                    SalesAccount=SalesAccount,
                    DeliveryMasterID=DeliveryMasterID,
                    OrderMasterID=OrderMasterID,
                    CustomerName=CustomerName,
                    Address1=Address1,
                    Address2=Address2,
                    Address3=Address3,
                    Notes=Notes,
                    FinacialYearID=FinacialYearID,
                    TotalGrossAmt=TotalGrossAmt,
                    TotalTax=TotalTax,
                    NetTotal=NetTotal,
                    AdditionalCost=AdditionalCost,
                    GrandTotal=GrandTotal,
                    RoundOff=RoundOff,
                    CashReceived=CashReceived,
                    CashAmount=CashAmount,
                    BankAmount=BankAmount,
                    WarehouseID=WarehouseID,
                    TableID=TableID,
                    SeatNumber=SeatNumber,
                    NoOfGuests=NoOfGuests,
                    INOUT=INOUT,
                    TokenNumber=TokenNumber,
                    IsActive=IsActive,
                    IsPosted=IsPosted,
                    SalesType=SalesType,
                    CreatedUserID=CreatedUserID,
                    UpdatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    TaxID=TaxID,
                    TaxType=TaxType,
                    VATAmount=VATAmount,
                    SGSTAmount=SGSTAmount,
                    CGSTAmount=CGSTAmount,
                    IGSTAmount=IGSTAmount,
                    TAX1Amount=TAX1Amount,
                    TAX2Amount=TAX2Amount,
                    TAX3Amount=TAX3Amount,
                    AddlDiscPercent=AddlDiscPercent,
                    AddlDiscAmt=AddlDiscAmt,
                    TotalDiscount=TotalDiscount,
                    BillDiscPercent=BillDiscPercent,
                    BillDiscAmt=BillDiscAmt,
                    CompanyID=CompanyID,
                    KFCAmount=KFCAmount,
                    Country_of_Supply=Country_of_Supply,
                    State_of_Supply=State_of_Supply,
                    GST_Treatment=GST_Treatment,
                    VAT_Treatment=VAT_Treatment,
                    TaxTaxableAmount=TaxTaxableAmount,
                    NonTaxTaxableAmount=NonTaxTaxableAmount,
                    BillingAddress=BillingAddress,
                    CashID=CashID,
                    BankID=BankID,
                )
                
                # ======QRCODE==========
                # url = request.META['HTTP_ORIGIN'] + "/invoice/" + str(sales_return_instance.pk)+str('/')+ str('SR')
                # url = str("http://localhost:3000/invoice/") + str(sales_return_instance.pk)+str('/')+ str('SR')
                if CompanyID.is_vat and CompanyID.VATNumber:
                    tax_number = CompanyID.VATNumber
                elif CompanyID.is_gst and CompanyID.GSTNumber:
                    tax_number = CompanyID.GSTNumber
                else:
                    tax_number = ""

                invoice_date = sales_return_instance.CreatedDate.strftime(
                    "%d-%b-%y %I:%M:%S %p"
                )
                fatoora_obj = Fatoora(
                    seller_name=CompanyID.CompanyName,
                    tax_number=tax_number,  # or "1234567891"
                    invoice_date=str(sales_return_instance.CreatedDate),  # Timestamp
                    total_amount=GrandTotal,  # or 100.0, 100.00, "100.0", "100.00"
                    tax_amount=TotalTax,  # or 15.0, 15.00, "15.0", "15.00"
                )
                url = fatoora_obj.base64

                qr_instance = QrCode.objects.create(
                    voucher_type="SR",
                    master_id=sales_return_instance.pk,
                    url=url,
                )

                # ======END============
                # billwise table insertion
                try:
                    billwiseDetails_datas = data['billwiseDetails_datas']
                except:
                    billwiseDetails_datas = []
                add_return_billwise = True
                if billwiseDetails_datas:
                    for b in billwiseDetails_datas:
                        BillwiseMasterID = b["BillwiseMasterID"]
                        Amount = b["Amount"]
                        BillwiseDetailsID = get_BillwiseDetailsID(
                            BranchID, CompanyID)
                        if BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID).exists():
                            bill_master_instance = BillWiseMaster.objects.filter(
                                CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID).first()
                            master_payment = bill_master_instance.Payments
                            if not Amount:
                                Amount = 0
                            if converted_float(Amount) > 0:
                                add_return_billwise = False
                                bill_master_instance.Payments = converted_float(
                                    master_payment) + converted_float(Amount)
                                bill_master_instance.save()

                                BillWiseDetails.objects.create(
                                    CompanyID=CompanyID,
                                    BranchID=BranchID,
                                    BillwiseDetailsID=BillwiseDetailsID,
                                    BillwiseMasterID=BillwiseMasterID,
                                    InvoiceNo=bill_master_instance.InvoiceNo,
                                    VoucherType=bill_master_instance.VoucherType,
                                    PaymentDate=VoucherDate,
                                    Payments=Amount,
                                    PaymentVoucherType=VoucherType,
                                    PaymentInvoiceNo=VoucherNo
                                )
                    if add_return_billwise:
                        handleBillwiseChanges(CompanyID, BranchID, CashReceived, BankAmount, GrandTotal, LedgerID,
                                              VoucherNo, VoucherType, "create", CreditPeriod, SalesReturnMasterID, VoucherDate)
                else:
                    handleBillwiseChanges(CompanyID,BranchID,CashReceived,BankAmount,GrandTotal,LedgerID,VoucherNo,VoucherType,"create",CreditPeriod,SalesReturnMasterID,VoucherDate)
                # enable_billwise = get_GeneralSettings(
                #     CompanyID, BranchID, "EnableBillwise")
                # total_amount_received = converted_float(
                #     CashReceived) + converted_float(BankAmount)
                # if enable_billwise and converted_float(total_amount_received) <= converted_float(GrandTotal) and AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=[10, 29]).exists():
                #     BillwiseMasterID = get_BillwiseMasterID(
                #         BranchID, CompanyID)
                #     DueDate = get_nth_day_date(CreditPeriod)
                #     BillWiseMaster.objects.create(
                #         CompanyID=CompanyID,
                #         BranchID=BranchID,
                #         BillwiseMasterID=BillwiseMasterID,
                #         InvoiceNo=VoucherNo,
                #         TransactionID=SalesReturnMasterID,
                #         VoucherType=VoucherType,
                #         VoucherDate=VoucherDate,
                #         InvoiceAmount=GrandTotal,
                #         Payments=total_amount_received,
                #         DueDate=DueDate,
                #         CustomerID=LedgerID
                #     )

                #     BillwiseDetailsID = get_BillwiseDetailsID(
                #         BranchID, CompanyID)
                #     BillWiseDetails.objects.create(
                #         CompanyID=CompanyID,
                #         BranchID=BranchID,
                #         BillwiseDetailsID=BillwiseDetailsID,
                #         BillwiseMasterID=BillwiseMasterID,
                #         InvoiceNo=VoucherNo,
                #         VoucherType=VoucherType,
                #         PaymentDate=VoucherDate,
                #         Payments=total_amount_received,
                #         PaymentVoucherType=VoucherType,
                #         PaymentInvoiceNo=VoucherNo
                #     )

                # =====================Loyal Custpmer Point=====================
                is_MinimumSalePrice = data["is_Loyalty_SalesReturn_MinimumSalePrice"]
                today_date = datetime.datetime.now().date()
                print(is_LoyaltyCustomer, "is_LoyaltyCustomeris_LoyaltyCustomer")
                if is_LoyaltyCustomer:
                    if LoyaltyProgram.objects.filter(
                        BranchID=BranchID,
                        CompanyID=CompanyID,
                        FromDate__lte=today_date,
                        ToDate__gte=today_date,
                    ).exists():
                        instance = LoyaltyProgram.objects.get(
                            BranchID=BranchID,
                            CompanyID=CompanyID,
                            FromDate__lte=today_date,
                            ToDate__gte=today_date,
                        )
                        print(instance.ProductType)
                        return_point = 0
                        tot_taxable_amnt = 0
                        salesReturnDetails = data["SalesReturnDetails"]
                        for salesReturnDetail in salesReturnDetails:
                            product_id = salesReturnDetail["ProductID"]
                            print(salesReturnDetail["ProductID"], "uvaissss")
                            TaxableAmount = salesReturnDetail["TaxableAmount"]
                            single_product_point = sales_return_point(
                                instance,
                                product_id,
                                TaxableAmount,
                                BranchID,
                                CompanyID,
                                is_MinimumSalePrice,
                            )
                            tot_taxable_amnt += single_product_point

                        actual_point = get_actual_point(tot_taxable_amnt, instance)
                        print(
                            loyalty_customer,
                            tot_taxable_amnt,
                            "tot_TaxableAmount actual_point",
                            actual_point,
                        )
                        CurrentPoint = 0
                        loyalty_instance = LoyaltyCustomer.objects.get(
                            BranchID=BranchID,
                            CompanyID=CompanyID,
                            LoyaltyCustomerID=loyalty_customer.LoyaltyCustomerID,
                        )
                        # loyalty_instance = LoyaltyPoint.objects.get(BranchID=BranchID,CompanyID=CompanyID,LoyaltyCustomerID=loyalty_customer.LoyaltyCustomerID,VoucherMasterID=SalesReturnMasterID,VoucherType=VoucherType)
                        # print(loyalty_instance.Point,"UNIQUE INSTANCE@@@@@@@@@@@@@@@@@@@@@")
                        # CurrentPoint = loyalty_instance.CurrentPoint
                        l_instances = LoyaltyPoint.objects.filter(
                            LoyaltyCustomerID__id=loyalty_instance.pk,
                            BranchID=BranchID,
                            CompanyID=CompanyID,
                        )
                        for i in l_instances:
                            CurrentPoint += converted_float(i.Point)
                        if converted_float(CurrentPoint) >= converted_float(actual_point):
                            return_point = converted_float(CurrentPoint) - converted_float(actual_point)
                            loyalty_customer.CurrentPoint = return_point
                            loyalty_customer.save()
                            if actual_point:
                                LoyaltyPointID = get_point_auto_id(
                                    LoyaltyPoint, BranchID, CompanyID
                                )
                                ExpiryDate = None
                                LoyaltyPoint.objects.create(
                                    BranchID=BranchID,
                                    LoyaltyPointID=LoyaltyPointID,
                                    Value=actual_point * -1,
                                    VoucherType=VoucherType,
                                    VoucherMasterID=SalesReturnMasterID,
                                    Point=actual_point * -1,
                                    ExpiryDate=ExpiryDate,
                                    LoyaltyCustomerID=loyalty_customer,
                                    LoyaltyProgramID=instance,
                                    is_Radeem=False,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CompanyID=CompanyID,
                                )
                                LoyaltyPoint_Log.objects.create(
                                    BranchID=BranchID,
                                    LoyaltyPointID=LoyaltyPointID,
                                    Value=actual_point * -1,
                                    VoucherType=VoucherType,
                                    VoucherMasterID=SalesReturnMasterID,
                                    Point=actual_point * -1,
                                    ExpiryDate=ExpiryDate,
                                    LoyaltyCustomerID=loyalty_customer,
                                    LoyaltyProgramID=instance,
                                    is_Radeem=False,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CompanyID=CompanyID,
                                )
                        # elif converted_float(CurrentPoint) <= converted_float(actual_point):
                        #     print(return_point, 'ELSEEEEEEEreturn_pointreturn_pointreturn_point')
                        #     actual_point = converted_float(CurrentPoint)
                        #     loyalty_customer.CurrentPoint = 0
                        #     loyalty_customer.save()
                        #     LoyaltyPointID = get_point_auto_id(
                        #         LoyaltyPoint, BranchID, CompanyID)
                        #     ExpiryDate = None
                        #     LoyaltyPoint.objects.create(
                        #         BranchID=BranchID,
                        #         LoyaltyPointID=LoyaltyPointID,
                        #         Value=actual_point*-1,
                        #         VoucherType=VoucherType,
                        #         VoucherMasterID=SalesReturnMasterID,
                        #         Point=actual_point*-1,
                        #         ExpiryDate=ExpiryDate,
                        #         LoyaltyCustomerID=loyalty_customer,
                        #         LoyaltyProgramID=instance,
                        #         is_Radeem=False,

                        #         CreatedDate=today,
                        #         UpdatedDate=today,
                        #         Action=Action,
                        #         CreatedUserID=CreatedUserID,
                        #         CompanyID=CompanyID,
                        #     )
                        #     LoyaltyPoint_Log.objects.create(
                        #         BranchID=BranchID,
                        #         LoyaltyPointID=LoyaltyPointID,
                        #         Value=actual_point*-1,
                        #         VoucherType=VoucherType,
                        #         VoucherMasterID=SalesReturnMasterID,
                        #         Point=actual_point*-1,
                        #         ExpiryDate=ExpiryDate,
                        #         LoyaltyCustomerID=loyalty_customer,
                        #         LoyaltyProgramID=instance,
                        #         is_Radeem=False,

                        #         CreatedDate=today,
                        #         UpdatedDate=today,
                        #         Action=Action,
                        #         CreatedUserID=CreatedUserID,
                        #         CompanyID=CompanyID,
                        #     )
                # =================================END====================================
                account_group = AccountLedger.objects.get(
                    CompanyID=CompanyID, LedgerID=LedgerID
                ).AccountGroupUnder
                # new posting starting from here

                # LedgerPostingID = get_auto_LedgerPostid(
                #     LedgerPosting, BranchID, CompanyID
                # )

                # LedgerPosting.objects.create(
                #     LedgerPostingID=LedgerPostingID,
                #     BranchID=BranchID,
                #     Date=VoucherDate,
                #     VoucherMasterID=SalesReturnMasterID,
                #     VoucherType=VoucherType,
                #     VoucherNo=VoucherNo,
                #     LedgerID=SalesAccount,
                #     RelatedLedgerID=LedgerID,
                #     Debit=GrandTotal,
                #     IsActive=IsActive,
                #     Action=Action,
                #     CreatedUserID=CreatedUserID,
                #     CreatedDate=today,
                #     UpdatedDate=today,
                #     CompanyID=CompanyID,
                # )

                # LedgerPosting_Log.objects.create(
                #     TransactionID=LedgerPostingID,
                #     BranchID=BranchID,
                #     Date=VoucherDate,
                #     VoucherMasterID=SalesReturnMasterID,
                #     VoucherType=VoucherType,
                #     VoucherNo=VoucherNo,
                #     LedgerID=SalesAccount,
                #     RelatedLedgerID=LedgerID,
                #     Debit=GrandTotal,
                #     IsActive=IsActive,
                #     Action=Action,
                #     CreatedUserID=CreatedUserID,
                #     CreatedDate=today,
                #     UpdatedDate=today,
                #     CompanyID=CompanyID,
                # )

                # update_ledger = UpdateLedgerBalance(
                #     CompanyID,
                #     BranchID,
                #     SalesAccount,
                #     SalesReturnMasterID,
                #     VoucherType,
                #     GrandTotal,
                #     "Dr",
                #     "create",
                # )

                # LedgerPostingID = get_auto_LedgerPostid(
                #     LedgerPosting, BranchID, CompanyID
                # )

                # LedgerPosting.objects.create(
                #     LedgerPostingID=LedgerPostingID,
                #     BranchID=BranchID,
                #     Date=VoucherDate,
                #     VoucherMasterID=SalesReturnMasterID,
                #     VoucherType=VoucherType,
                #     VoucherNo=VoucherNo,
                #     LedgerID=LedgerID,
                #     RelatedLedgerID=SalesAccount,
                #     Credit=GrandTotal,
                #     IsActive=IsActive,
                #     Action=Action,
                #     CreatedUserID=CreatedUserID,
                #     CreatedDate=today,
                #     UpdatedDate=today,
                #     CompanyID=CompanyID,
                # )

                # LedgerPosting_Log.objects.create(
                #     TransactionID=LedgerPostingID,
                #     BranchID=BranchID,
                #     Date=VoucherDate,
                #     VoucherMasterID=SalesReturnMasterID,
                #     VoucherType=VoucherType,
                #     VoucherNo=VoucherNo,
                #     LedgerID=LedgerID,
                #     RelatedLedgerID=SalesAccount,
                #     Credit=GrandTotal,
                #     IsActive=IsActive,
                #     Action=Action,
                #     CreatedUserID=CreatedUserID,
                #     CreatedDate=today,
                #     UpdatedDate=today,
                #     CompanyID=CompanyID,
                # )

                # update_ledger = UpdateLedgerBalance(
                #     CompanyID,
                #     BranchID,
                #     LedgerID,
                #     SalesReturnMasterID,
                #     VoucherType,
                #     GrandTotal,
                #     "Cr",
                #     "create",
                # )

                if TaxType == "VAT":
                    if converted_float(VATAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID
                        )

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=55,
                            RelatedLedgerID=SalesAccount,
                            Debit=VATAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=55,
                            RelatedLedgerID=SalesAccount,
                            Debit=VATAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID,
                            BranchID,
                            55,
                            SalesReturnMasterID,
                            VoucherType,
                            VATAmount,
                            "Dr",
                            "create",
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID
                        )

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=55,
                            Credit=VATAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=55,
                            Credit=VATAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID,
                            BranchID,
                            SalesAccount,
                            SalesReturnMasterID,
                            VoucherType,
                            VATAmount,
                            "Cr",
                            "create",
                        )
                # new posting ending  here

                elif (
                    TaxType == "GST Intra-state B2B" or TaxType == "GST Intra-state B2C"
                ):
                    if converted_float(CGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID
                        )

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=3,
                            RelatedLedgerID=SalesAccount,
                            Debit=CGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=3,
                            RelatedLedgerID=SalesAccount,
                            Debit=CGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID,
                            BranchID,
                            3,
                            SalesReturnMasterID,
                            VoucherType,
                            CGSTAmount,
                            "Dr",
                            "create",
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID
                        )

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=3,
                            Credit=CGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=3,
                            Credit=CGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID,
                            BranchID,
                            SalesAccount,
                            SalesReturnMasterID,
                            VoucherType,
                            CGSTAmount,
                            "Cr",
                            "create",
                        )

                    if converted_float(SGSTAmount) > 0:

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID
                        )

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=10,
                            RelatedLedgerID=SalesAccount,
                            Debit=SGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=10,
                            RelatedLedgerID=SalesAccount,
                            Debit=SGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID,
                            BranchID,
                            10,
                            SalesReturnMasterID,
                            VoucherType,
                            SGSTAmount,
                            "Dr",
                            "create",
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID
                        )

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=10,
                            Credit=SGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=10,
                            Credit=SGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID,
                            BranchID,
                            SalesAccount,
                            SalesReturnMasterID,
                            VoucherType,
                            SGSTAmount,
                            "Cr",
                            "create",
                        )

                    if converted_float(KFCAmount) > 0:

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID
                        )

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=93,
                            RelatedLedgerID=SalesAccount,
                            Debit=KFCAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=93,
                            RelatedLedgerID=SalesAccount,
                            Debit=KFCAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID,
                            BranchID,
                            93,
                            SalesReturnMasterID,
                            VoucherType,
                            KFCAmount,
                            "Dr",
                            "create",
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID
                        )

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=93,
                            Credit=KFCAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=93,
                            Credit=KFCAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID,
                            BranchID,
                            SalesAccount,
                            SalesReturnMasterID,
                            VoucherType,
                            KFCAmount,
                            "Cr",
                            "create",
                        )

                elif (
                    TaxType == "GST Inter-state B2B" or TaxType == "GST Inter-state B2C"
                ):
                    if converted_float(IGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID
                        )

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=17,
                            RelatedLedgerID=SalesAccount,
                            Debit=IGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=17,
                            RelatedLedgerID=SalesAccount,
                            Debit=IGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID,
                            BranchID,
                            17,
                            SalesReturnMasterID,
                            VoucherType,
                            IGSTAmount,
                            "Dr",
                            "create",
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID
                        )

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=17,
                            Credit=IGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=17,
                            Credit=IGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID,
                            BranchID,
                            SalesAccount,
                            SalesReturnMasterID,
                            VoucherType,
                            IGSTAmount,
                            "Cr",
                            "create",
                        )

                if not TaxType == "Export":
                    if converted_float(TAX1Amount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID
                        )
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=16,
                            RelatedLedgerID=SalesAccount,
                            Debit=TAX1Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=16,
                            RelatedLedgerID=SalesAccount,
                            Debit=TAX1Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID,
                            BranchID,
                            16,
                            SalesReturnMasterID,
                            VoucherType,
                            TAX1Amount,
                            "Dr",
                            "create",
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID
                        )
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=16,
                            Credit=TAX1Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=16,
                            Credit=TAX1Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID,
                            BranchID,
                            SalesAccount,
                            SalesReturnMasterID,
                            VoucherType,
                            TAX1Amount,
                            "Cr",
                            "create",
                        )

                    if converted_float(TAX2Amount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID
                        )
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=19,
                            RelatedLedgerID=SalesAccount,
                            Debit=TAX2Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=19,
                            RelatedLedgerID=SalesAccount,
                            Debit=TAX2Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID,
                            BranchID,
                            19,
                            SalesReturnMasterID,
                            VoucherType,
                            TAX2Amount,
                            "Dr",
                            "create",
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID
                        )
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=19,
                            Credit=TAX2Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=19,
                            Credit=TAX2Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID,
                            BranchID,
                            SalesAccount,
                            SalesReturnMasterID,
                            VoucherType,
                            TAX2Amount,
                            "Cr",
                            "create",
                        )

                    if converted_float(TAX3Amount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID
                        )
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=22,
                            RelatedLedgerID=SalesAccount,
                            Debit=TAX3Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=22,
                            RelatedLedgerID=SalesAccount,
                            Debit=TAX3Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID,
                            BranchID,
                            22,
                            SalesReturnMasterID,
                            VoucherType,
                            TAX3Amount,
                            "Dr",
                            "create",
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID
                        )
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=22,
                            Credit=TAX3Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=22,
                            Credit=TAX3Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID,
                            BranchID,
                            SalesAccount,
                            SalesReturnMasterID,
                            VoucherType,
                            TAX3Amount,
                            "Cr",
                            "create",
                        )

                if converted_float(RoundOff) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=78,
                        RelatedLedgerID=SalesAccount,
                        Debit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=78,
                        RelatedLedgerID=SalesAccount,
                        Debit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        78,
                        SalesReturnMasterID,
                        VoucherType,
                        RoundOff,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=78,
                        Credit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=78,
                        Credit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        RoundOff,
                        "Cr",
                        "create",
                    )

                if converted_float(RoundOff) < 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    RoundOff = abs(converted_float(RoundOff))

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=78,
                        RelatedLedgerID=SalesAccount,
                        Credit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=78,
                        RelatedLedgerID=SalesAccount,
                        Credit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        78,
                        SalesReturnMasterID,
                        VoucherType,
                        RoundOff,
                        "Cr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=78,
                        Debit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=78,
                        Debit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        RoundOff,
                        "Dr",
                        "create",
                    )

                if converted_float(TotalDiscount) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=74,
                        RelatedLedgerID=SalesAccount,
                        Credit=TotalDiscount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=74,
                        RelatedLedgerID=SalesAccount,
                        Credit=TotalDiscount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        74,
                        SalesReturnMasterID,
                        VoucherType,
                        TotalDiscount,
                        "Cr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=74,
                        Debit=TotalDiscount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=74,
                        Debit=TotalDiscount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        TotalDiscount,
                        "Dr",
                        "create",
                    )
                    
                # credit sales start here
                if (
                    converted_float(CashReceived) == 0
                    and converted_float(BankAmount) == 0
                ):
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        GrandTotal,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        LedgerID,
                        SalesReturnMasterID,
                        VoucherType,
                        GrandTotal,
                        "Cr",
                        "create",
                    )

                # credit sales end here

                # customer with cash and customer with partial cash start here
                elif (
                    (account_group == 10 or account_group ==
                     29 or account_group == 32)
                    and converted_float(CashReceived) > 0
                    and converted_float(BankAmount) == 0
                ):
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        GrandTotal,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        LedgerID,
                        SalesReturnMasterID,
                        VoucherType,
                        GrandTotal,
                        "Cr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=LedgerID,
                        Credit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=LedgerID,
                        Credit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        CashID,
                        SalesReturnMasterID,
                        VoucherType,
                        CashAmount,
                        "Cr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=CashID,
                        Debit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=CashID,
                        Debit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        LedgerID,
                        SalesReturnMasterID,
                        VoucherType,
                        CashAmount,
                        "Dr",
                        "create",
                    )

                # customer with cash and customer with partial cash end here

                # customer with bank and customer with partial bank start here
                elif (
                    (account_group == 10 or account_group ==
                     29 or account_group == 32)
                    and converted_float(CashReceived) == 0
                    and converted_float(BankAmount) > 0
                ):
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        GrandTotal,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        LedgerID,
                        SalesReturnMasterID,
                        VoucherType,
                        GrandTotal,
                        "Cr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=LedgerID,
                        Credit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=LedgerID,
                        Credit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        BankID,
                        SalesReturnMasterID,
                        VoucherType,
                        BankAmount,
                        "Cr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=BankID,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=BankID,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        LedgerID,
                        SalesReturnMasterID,
                        VoucherType,
                        BankAmount,
                        "Dr",
                        "create",
                    )

                # customer with bank and customer with partial bank end here

                # bank with cash and cash with cash start here
                elif (
                    (account_group == 8 or account_group == 9)
                    and converted_float(CashReceived) > 0
                    and converted_float(BankAmount) == 0
                ):
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=CashID,
                        Debit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=CashID,
                        Debit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        CashAmount,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=SalesAccount,
                        Credit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=SalesAccount,
                        Credit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        CashID,
                        SalesReturnMasterID,
                        VoucherType,
                        CashAmount,
                        "Cr",
                        "create",
                    )

                    csh_value = converted_float(GrandTotal) - converted_float(
                        CashReceived
                    )
                    if not converted_float(csh_value) == 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID
                        )

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=LedgerID,
                            RelatedLedgerID=SalesAccount,
                            Credit=csh_value,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=LedgerID,
                            RelatedLedgerID=SalesAccount,
                            Credit=csh_value,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID,
                            BranchID,
                            LedgerID,
                            SalesReturnMasterID,
                            VoucherType,
                            csh_value,
                            "Cr",
                            "create",
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID
                        )

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=LedgerID,
                            Debit=csh_value,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=LedgerID,
                            Debit=csh_value,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID,
                            BranchID,
                            SalesAccount,
                            SalesReturnMasterID,
                            VoucherType,
                            csh_value,
                            "Dr",
                            "create",
                        )
                # bank with cash and cash with cash end here

                # bank with bank and cash with bank start here
                elif (
                    (account_group == 8 or account_group == 9)
                    and converted_float(CashReceived) == 0
                    and converted_float(BankAmount) > 0
                ):
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=BankID,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=BankID,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        BankAmount,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=SalesAccount,
                        Credit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=SalesAccount,
                        Credit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        BankID,
                        SalesReturnMasterID,
                        VoucherType,
                        BankAmount,
                        "Cr",
                        "create",
                    )

                    bnk_value = converted_float(GrandTotal) - converted_float(
                        BankAmount
                    )
                    if not converted_float(bnk_value) == 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID
                        )

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=LedgerID,
                            RelatedLedgerID=SalesAccount,
                            Credit=bnk_value,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=LedgerID,
                            RelatedLedgerID=SalesAccount,
                            Credit=bnk_value,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID,
                            BranchID,
                            LedgerID,
                            SalesReturnMasterID,
                            VoucherType,
                            bnk_value,
                            "Cr",
                            "create",
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID
                        )

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=LedgerID,
                            Debit=bnk_value,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=LedgerID,
                            Debit=bnk_value,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID,
                            BranchID,
                            SalesAccount,
                            SalesReturnMasterID,
                            VoucherType,
                            bnk_value,
                            "Dr",
                            "create",
                        )
                # bank with bank and cash with bank end here

                # customer with partial cash /bank and customer with cash/bank
                elif (
                    (account_group == 10 or account_group ==
                     29 or account_group == 32)
                    and converted_float(CashReceived) > 0
                    and converted_float(BankAmount) > 0
                ):
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        GrandTotal,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        LedgerID,
                        SalesReturnMasterID,
                        VoucherType,
                        GrandTotal,
                        "Cr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=LedgerID,
                        Credit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=LedgerID,
                        Credit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        CashID,
                        SalesReturnMasterID,
                        VoucherType,
                        CashAmount,
                        "Cr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=CashID,
                        Debit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=CashID,
                        Debit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        LedgerID,
                        SalesReturnMasterID,
                        VoucherType,
                        CashAmount,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=LedgerID,
                        Credit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=LedgerID,
                        Credit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        BankID,
                        SalesReturnMasterID,
                        VoucherType,
                        BankAmount,
                        "Cr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=BankID,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=BankID,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        LedgerID,
                        SalesReturnMasterID,
                        VoucherType,
                        BankAmount,
                        "Dr",
                        "create",
                    )
                # customer with partial cash /bank and customer with cash/bank

                # cash with cash/bank start here
                elif (
                    (account_group == 9 or account_group == 8)
                    and converted_float(CashReceived) > 0
                    and converted_float(BankAmount) > 0
                ):

                    total_received = converted_float(CashReceived) + converted_float(
                        BankAmount
                    )
                    Balance_amt = converted_float(GrandTotal) - converted_float(
                        total_received
                    )
                    if not converted_float(Balance_amt) == 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID
                        )

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=LedgerID,
                            Debit=Balance_amt,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=LedgerID,
                            Debit=Balance_amt,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID,
                            BranchID,
                            SalesAccount,
                            SalesReturnMasterID,
                            VoucherType,
                            Balance_amt,
                            "Dr",
                            "create",
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID
                        )

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=LedgerID,
                            RelatedLedgerID=SalesAccount,
                            Credit=Balance_amt,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=LedgerID,
                            RelatedLedgerID=SalesAccount,
                            Credit=Balance_amt,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID,
                            BranchID,
                            LedgerID,
                            SalesReturnMasterID,
                            VoucherType,
                            Balance_amt,
                            "Cr",
                            "create",
                        )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=SalesAccount,
                        Credit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=SalesAccount,
                        Credit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        BankID,
                        SalesReturnMasterID,
                        VoucherType,
                        BankAmount,
                        "Cr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=BankID,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=BankID,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        BankAmount,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=CashID,
                        Debit=CashReceived,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=CashID,
                        Debit=CashReceived,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        CashReceived,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=SalesAccount,
                        Credit=CashReceived,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=SalesAccount,
                        Credit=CashReceived,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        CashID,
                        SalesReturnMasterID,
                        VoucherType,
                        CashReceived,
                        "Cr",
                        "create",
                    )

                # cash with cash/bank end here

                salesReturnDetails = data["SalesReturnDetails"]
                for salesReturnDetail in salesReturnDetails:
                    ProductID = salesReturnDetail["ProductID"]
                    if ProductID:
                        # SalesReturnMasterID = serialized.data['SalesReturnMasterID']
                        DeliveryDetailsID = salesReturnDetail["DeliveryDetailsID"]
                        OrderDetailsID = salesReturnDetail["OrderDetailsID"]
                        Qty = salesReturnDetail["Qty"]
                        FreeQty = salesReturnDetail["FreeQty"]
                        Flavour = salesReturnDetail["Flavour"]

                        UnitPrice = converted_float(salesReturnDetail["UnitPrice"])
                        InclusivePrice = converted_float(salesReturnDetail["InclusivePrice"])
                        RateWithTax = converted_float(salesReturnDetail["RateWithTax"])
                        # CostPerPrice = converted_float(salesReturnDetail['CostPerPrice'])
                        PriceListID = salesReturnDetail["PriceListID"]
                        DiscountPerc = converted_float(salesReturnDetail["DiscountPerc"])
                        DiscountAmount = converted_float(salesReturnDetail["DiscountAmount"])
                        GrossAmount = converted_float(salesReturnDetail["GrossAmount"])
                        TaxableAmount = converted_float(salesReturnDetail["TaxableAmount"])
                        VATPerc = converted_float(salesReturnDetail["VATPerc"])
                        VATAmount = converted_float(salesReturnDetail["VATAmount"])
                        SGSTPerc = converted_float(salesReturnDetail["SGSTPerc"])
                        SGSTAmount = converted_float(salesReturnDetail["SGSTAmount"])
                        CGSTPerc = converted_float(salesReturnDetail["CGSTPerc"])
                        CGSTAmount = converted_float(salesReturnDetail["CGSTAmount"])
                        IGSTPerc = converted_float(salesReturnDetail["IGSTPerc"])
                        IGSTAmount = converted_float(salesReturnDetail["IGSTAmount"])
                        NetAmount = converted_float(salesReturnDetail["NetAmount"])
                        AddlDiscPercent = converted_float(salesReturnDetail["AddlDiscPerc"])
                        AddlDiscAmt = converted_float(salesReturnDetail["AddlDiscAmt"])
                        TAX1Perc = converted_float(salesReturnDetail["TAX1Perc"])
                        TAX1Amount = converted_float(salesReturnDetail["TAX1Amount"])
                        TAX2Perc = converted_float(salesReturnDetail["TAX2Perc"])
                        TAX2Amount = converted_float(salesReturnDetail["TAX2Amount"])
                        TAX3Perc = converted_float(salesReturnDetail["TAX3Perc"])
                        TAX3Amount = converted_float(salesReturnDetail["TAX3Amount"])
                        try:
                            KFCAmount = converted_float(salesReturnDetail["KFCAmount"])
                        except:
                            KFCAmount = 0

                        try:
                            ProductTaxID = salesReturnDetail["ProductTaxID"]
                        except:
                            ProductTaxID = 1

                        CostPerPrice = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID
                        ).PurchasePrice

                        # UnitPrice = round(UnitPrice, PriceRounding)
                        # InclusivePrice = round(InclusivePrice, PriceRounding)
                        # RateWithTax = round(RateWithTax, PriceRounding)
                        # CostPerPrice = round(CostPerPrice, PriceRounding)
                        # DiscountPerc = round(DiscountPerc, PriceRounding)

                        # DiscountAmount = round(DiscountAmount, PriceRounding)
                        # GrossAmount = round(GrossAmount, PriceRounding)
                        # TaxableAmount = round(TaxableAmount, PriceRounding)
                        # VATPerc = round(VATPerc, PriceRounding)
                        # VATAmount = round(VATAmount, PriceRounding)

                        # SGSTPerc = round(SGSTPerc, PriceRounding)
                        # SGSTAmount = round(SGSTAmount, PriceRounding)
                        # CGSTPerc = round(CGSTPerc, PriceRounding)
                        # CGSTAmount = round(CGSTAmount, PriceRounding)
                        # IGSTPerc = round(IGSTPerc, PriceRounding)

                        # IGSTAmount = round(IGSTAmount, PriceRounding)
                        # NetAmount = round(NetAmount, PriceRounding)
                        # AddlDiscPercent = round(AddlDiscPercent, PriceRounding)
                        # AddlDiscAmt = round(AddlDiscAmt, PriceRounding)
                        # TAX1Perc = round(TAX1Perc, PriceRounding)

                        # TAX1Amount = round(TAX1Amount, PriceRounding)
                        # TAX2Perc = round(TAX2Perc, PriceRounding)
                        # TAX2Amount = round(TAX2Amount, PriceRounding)
                        # TAX3Perc = round(TAX3Perc, PriceRounding)
                        # TAX3Amount = round(TAX3Amount, PriceRounding)
                        # KFCAmount = round(KFCAmount, PriceRounding)
                        try:
                            SerialNos = salesReturnDetail["SerialNos"]
                        except:
                            SerialNos = []

                        try:
                            Description = salesReturnDetail["Description"]
                        except:
                            Description = ""
                        try:
                            KFCPerc = salesReturnDetail["KFCPerc"]
                        except:
                            KFCPerc = 0

                        # KFCPerc = round(KFCPerc, PriceRounding)

                        try:
                            BatchCode = salesReturnDetail["BatchCode"]
                        except:
                            BatchCode = 0
                        try:
                            is_inclusive = salesReturnDetail["is_inclusive"]
                        except:
                            is_inclusive = False

                        if is_inclusive == True:
                            Batch_salesPrice = InclusivePrice
                        else:
                            Batch_salesPrice = UnitPrice

                        product_is_Service = Product.objects.get(
                            CompanyID=CompanyID, ProductID=ProductID
                        ).is_Service

                        product_purchasePrice = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID
                        ).PurchasePrice
                        MultiFactor = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID
                        ).MultiFactor

                        qty_batch = converted_float(FreeQty) + converted_float(Qty)
                        Qty_batch = converted_float(MultiFactor) * converted_float(qty_batch)

                        check_AllowUpdateBatchPriceInSales = False
                        check_EnableProductBatchWise = False
                        if product_is_Service == False:
                            if GeneralSettings.objects.filter(
                                CompanyID=CompanyID,
                                BranchID=BranchID,
                                SettingsType="AllowUpdateBatchPriceInSales",
                            ).exists():
                                check_AllowUpdateBatchPriceInSales = (
                                    GeneralSettings.objects.get(
                                        CompanyID=CompanyID,
                                        BranchID=BranchID,
                                        SettingsType="AllowUpdateBatchPriceInSales",
                                    ).SettingsValue
                                )

                            if GeneralSettings.objects.filter(
                                CompanyID=CompanyID,
                                BranchID=BranchID,
                                SettingsType="EnableProductBatchWise",
                            ).exists():
                                check_EnableProductBatchWise = (
                                    GeneralSettings.objects.get(
                                        CompanyID=CompanyID,
                                        BranchID=BranchID,
                                        SettingsType="EnableProductBatchWise",
                                    ).SettingsValue
                                )

                            if (
                                check_EnableProductBatchWise == True
                                or check_EnableProductBatchWise == "True"
                            ):
                                setbach = SetBatchInSales(
                                    CompanyID,
                                    BranchID,
                                    Batch_salesPrice,
                                    Qty_batch,
                                    BatchCode,
                                    check_AllowUpdateBatchPriceInSales,
                                    PriceListID,
                                    "SR",
                                )

                                # if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                                #     if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
                                #         if check_AllowUpdateBatchPriceInSales == "True" or check_AllowUpdateBatchPriceInSales == True:
                                #             batch_ins = Batch.objects.get(
                                #                 CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                                #             StockIn = batch_ins.StockIn
                                #             BatchCode = batch_ins.BatchCode
                                #             NewStock = converted_float(
                                #                 StockIn) + converted_float(Qty_batch)
                                #             batch_ins.StockIn = NewStock
                                #             batch_ins.SalesPrice = Batch_salesPrice
                                #             batch_ins.save()
                                #         else:
                                #             batch_ins = Batch.objects.get(
                                #                 CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                                #             StockIn = batch_ins.StockIn
                                #             BatchCode = batch_ins.BatchCode
                                #             NewStock = converted_float(
                                #                 StockIn) + converted_float(Qty_batch)
                                #             batch_ins.StockIn = NewStock
                                #             batch_ins.save()
                                #     else:
                                #         BatchCode = get_auto_AutoBatchCode(
                                #             Batch, BranchID, CompanyID)
                                #         Batch.objects.create(
                                #             CompanyID=CompanyID,
                                #             BranchID=BranchID,
                                #             BatchCode=BatchCode,
                                #             StockIn=Qty_batch,
                                #             PurchasePrice=product_purchasePrice,
                                #             SalesPrice=Batch_salesPrice,
                                #             PriceListID=PriceListID,
                                #             ProductID=ProductID,
                                #             WareHouseID=WarehouseID,
                                #             CreatedDate=today,
                                #             UpdatedDate=today,
                                #             CreatedUserID=CreatedUserID,
                                #         )

                                # else:
                                #     if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PriceListID=PriceListID).exists():
                                #         batch_ins = Batch.objects.get(
                                #             CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PriceListID=PriceListID)
                                #         StockIn = batch_ins.StockIn
                                #         BatchCode = batch_ins.BatchCode
                                #         NewStock = converted_float(StockIn) + converted_float(Qty_batch)
                                #         batch_ins.StockIn = NewStock
                                #         batch_ins.save()
                                #     else:
                                #         BatchCode = get_auto_AutoBatchCode(
                                #             Batch, BranchID, CompanyID)
                                #         Batch.objects.create(
                                #             CompanyID=CompanyID,
                                #             BranchID=BranchID,
                                #             BatchCode=BatchCode,
                                #             StockIn=Qty_batch,
                                #             PurchasePrice=product_purchasePrice,
                                #             SalesPrice=Batch_salesPrice,
                                #             PriceListID=PriceListID,
                                #             ProductID=ProductID,
                                #             WareHouseID=WarehouseID,
                                #             CreatedDate=today,
                                #             UpdatedDate=today,
                                #             CreatedUserID=CreatedUserID,
                                #         )

                        SalesReturnQty = Qty
                        SalesReturnDetailsID = get_auto_id(
                            SalesReturnDetails, BranchID, CompanyID
                        )

                        if SerialNos:
                            for sn in SerialNos:
                                SerialNumbers.objects.create(
                                    VoucherType="SR",
                                    CompanyID=CompanyID,
                                    SerialNo=sn["SerialNo"],
                                    ItemCode=sn["ItemCode"],
                                    SalesMasterID=SalesReturnMasterID,
                                    SalesDetailsID=SalesReturnDetailsID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CreatedUserID=CreatedUserID,
                                )

                        ledger_instance = SalesReturnDetails_Log.objects.create(
                            TransactionID=SalesReturnDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesReturnMasterID=SalesReturnMasterID,
                            DeliveryDetailsID=DeliveryDetailsID,
                            OrderDetailsID=OrderDetailsID,
                            ProductID=ProductID,
                            Qty=Qty,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            InclusivePrice=InclusivePrice,
                            RateWithTax=RateWithTax,
                            CostPerPrice=CostPerPrice,
                            PriceListID=PriceListID,
                            DiscountPerc=DiscountPerc,
                            DiscountAmount=DiscountAmount,
                            GrossAmount=GrossAmount,
                            TaxableAmount=TaxableAmount,
                            VATPerc=VATPerc,
                            VATAmount=VATAmount,
                            SGSTPerc=SGSTPerc,
                            SGSTAmount=SGSTAmount,
                            CGSTPerc=CGSTPerc,
                            CGSTAmount=CGSTAmount,
                            IGSTPerc=IGSTPerc,
                            IGSTAmount=IGSTAmount,
                            NetAmount=NetAmount,
                            Flavour=Flavour,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            AddlDiscPercent=AddlDiscPercent,
                            AddlDiscAmt=AddlDiscAmt,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            CompanyID=CompanyID,
                            BatchCode=BatchCode,
                            KFCAmount=KFCAmount,
                            KFCPerc=KFCPerc,
                            Description=Description,
                            ProductTaxID=ProductTaxID,
                        )

                        SalesReturnDetails.objects.create(
                            SalesReturnDetailsID=SalesReturnDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesReturnMasterID=SalesReturnMasterID,
                            DeliveryDetailsID=DeliveryDetailsID,
                            OrderDetailsID=OrderDetailsID,
                            ProductID=ProductID,
                            Qty=Qty,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            InclusivePrice=InclusivePrice,
                            RateWithTax=RateWithTax,
                            CostPerPrice=CostPerPrice,
                            PriceListID=PriceListID,
                            DiscountPerc=DiscountPerc,
                            DiscountAmount=DiscountAmount,
                            GrossAmount=GrossAmount,
                            TaxableAmount=TaxableAmount,
                            VATPerc=VATPerc,
                            VATAmount=VATAmount,
                            SGSTPerc=SGSTPerc,
                            SGSTAmount=SGSTAmount,
                            CGSTPerc=CGSTPerc,
                            CGSTAmount=CGSTAmount,
                            IGSTPerc=IGSTPerc,
                            IGSTAmount=IGSTAmount,
                            NetAmount=NetAmount,
                            Flavour=Flavour,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            AddlDiscPercent=AddlDiscPercent,
                            AddlDiscAmt=AddlDiscAmt,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            CompanyID=CompanyID,
                            BatchCode=BatchCode,
                            LogID=ledger_instance.ID,
                            KFCAmount=KFCAmount,
                            KFCPerc=KFCPerc,
                            Description=Description,
                            ProductTaxID=ProductTaxID,
                        )

                        # priceList = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,DefaultUnit=True,BranchID=BranchID)

                        # PriceListID = priceList.PriceListID
                        # MultiFactor = priceList.MultiFactor

                        MultiFactor = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID
                        ).MultiFactor
                        PriceListID = PriceList.objects.get(
                            CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True
                        ).PriceListID

                        # PurchasePrice = priceList.PurchasePrice
                        # SalesPrice = priceList.SalesPrice
                        qty = converted_float(FreeQty) + converted_float(Qty)

                        Qty = converted_float(MultiFactor) * converted_float(qty)
                        Cost = converted_float(CostPerPrice) / converted_float(MultiFactor)

                        # Qy = round(Qty, 4)
                        # Qty = str(Qy)

                        # Ct = round(Cost, 4)
                        # Cost = str(Ct)

                        princeList_instance = PriceList.objects.get(
                            CompanyID=CompanyID,
                            ProductID=ProductID,
                            PriceListID=PriceListID,
                        )
                        PurchasePrice = princeList_instance.PurchasePrice
                        SalesPrice = princeList_instance.SalesPrice

                        if product_is_Service == False:
                            StockPostingID = get_auto_stockPostid(
                                StockPosting, BranchID, CompanyID
                            )

                            pricelist, warehouse = get_ModelInstance(
                                CompanyID, BranchID, PriceListID, WarehouseID
                            )

                            StockPosting.objects.create(
                                StockPostingID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=VoucherDate,
                                VoucherMasterID=SalesReturnMasterID,
                                VoucherDetailID=SalesReturnDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchCode,
                                WareHouseID=WarehouseID,
                                QtyIn=Qty,
                                Rate=Cost,
                                PriceListID=PriceListID,
                                IsActive=IsActive,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                                pricelist=pricelist,
                                warehouse=warehouse,
                            )

                            StockPosting_Log.objects.create(
                                TransactionID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=VoucherDate,
                                VoucherMasterID=SalesReturnMasterID,
                                VoucherDetailID=SalesReturnDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchCode,
                                WareHouseID=WarehouseID,
                                QtyIn=Qty,
                                Rate=Cost,
                                PriceListID=PriceListID,
                                IsActive=IsActive,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )

                            update_stock(CompanyID, BranchID, ProductID)

                            # stockRateInstance = None

                            # if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID).exists():
                            #     stockRateInstance = StockRate.objects.get(
                            #         CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID)

                            #     StockRateID = stockRateInstance.StockRateID
                            #     stockRateInstance.Qty = converted_float(
                            #         stockRateInstance.Qty) + converted_float(Qty)
                            #     stockRateInstance.save()

                            #     if StockTrans.objects.filter(StockRateID=StockRateID, DetailID=SalesReturnDetailsID, MasterID=SalesReturnMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                            #         stockTra_in = StockTrans.objects.filter(
                            #             StockRateID=StockRateID, DetailID=SalesReturnDetailsID, MasterID=SalesReturnMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                            #         stockTra_in.Qty = converted_float(
                            #             stockTra_in.Qty) + converted_float(Qty)
                            #         stockTra_in.save()
                            #     else:
                            #         StockTransID = get_auto_StockTransID(
                            #             StockTrans, BranchID, CompanyID)
                            #         StockTrans.objects.create(
                            #             StockTransID=StockTransID,
                            #             BranchID=BranchID,
                            #             VoucherType=VoucherType,
                            #             StockRateID=StockRateID,
                            #             DetailID=SalesReturnDetailsID,
                            #             MasterID=SalesReturnMasterID,
                            #             Qty=Qty,
                            #             IsActive=IsActive,
                            #             CompanyID=CompanyID,
                            #         )

                            # else:
                            #     StockRateID = get_auto_StockRateID(
                            #         StockRate, BranchID, CompanyID)
                            #     StockRate.objects.create(
                            #         StockRateID=StockRateID,
                            #         BranchID=BranchID,
                            #         BatchID=BatchID,
                            #         PurchasePrice=PurchasePrice,
                            #         SalesPrice=SalesPrice,
                            #         Qty=Qty,
                            #         Cost=Cost,
                            #         ProductID=ProductID,
                            #         WareHouseID=WarehouseID,
                            #         Date=VoucherDate,
                            #         PriceListID=PriceListID,
                            #         CreatedUserID=CreatedUserID,
                            #         CreatedDate=today,
                            #         UpdatedDate=today,
                            #         CompanyID=CompanyID,
                            #     )

                            #     StockTransID = get_auto_StockTransID(
                            #         StockTrans, BranchID, CompanyID)
                            #     StockTrans.objects.create(
                            #         StockTransID=StockTransID,
                            #         BranchID=BranchID,
                            #         VoucherType=VoucherType,
                            #         StockRateID=StockRateID,
                            #         DetailID=SalesReturnDetailsID,
                            #         MasterID=SalesReturnMasterID,
                            #         Qty=Qty,
                            #         IsActive=IsActive,
                            #         CompanyID=CompanyID,
                            #     )

                        if SalesMaster.objects.filter(
                            CompanyID=CompanyID,
                            VoucherNo=RefferenceBillNo,
                            BranchID=BranchID,
                        ).exists():
                            SalesMaster_instance = SalesMaster.objects.get(
                                CompanyID=CompanyID,
                                VoucherNo=RefferenceBillNo,
                                BranchID=BranchID,
                            )
                            SalesMasterID = SalesMaster_instance.SalesMasterID

                            if SalesDetails.objects.filter(
                                CompanyID=CompanyID,
                                SalesMasterID=SalesMasterID,
                                BranchID=BranchID,
                                ProductID=ProductID,
                            ).exists():
                                SalesDetails_instances = SalesDetails.objects.filter(
                                    CompanyID=CompanyID,
                                    SalesMasterID=SalesMasterID,
                                    BranchID=BranchID,
                                    ProductID=ProductID,
                                )

                                for i in SalesDetails_instances:
                                    ReturnQty = i.ReturnQty
                                    SalesReturnQty = SalesReturnQty
                                    ReturnQty = converted_float(ReturnQty) - converted_float(SalesReturnQty)
                                    i.ReturnQty = ReturnQty

                                    i.save()

                # request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sales Return',
                #              'Create', 'Sales Return created successfully.', 'Sales Return saved successfully.')
                cash_Balance = get_LedgerBalance(CompanyID, 1)
                response_data = {
                    "StatusCode": 6000,
                    "id": sales_return_instance.id,
                    "qr_url": qr_instance.qr_code.url,
                    "message": "Sales Return created Successfully!!!",
                    "CashBalance": cash_Balance
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                # request , company, log_type, user, source, action, message, description
                activity_log(
                    request._request,
                    CompanyID,
                    "Warning",
                    CreatedUserID,
                    "Sales Return",
                    "Create",
                    "Sales Return created Failed.",
                    "VoucherNo already exist",
                )

                response_data = {
                    "StatusCode": 6001,
                    "message": "VoucherNo already exist.Please Change Your Prefix!",
                }

                return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again",
        }
        activity_log(
            request._request,
            CompanyID,
            "Error",
            CreatedUserID,
            "Sales Return",
            "Create",
            str(e),
            err_descrb,
        )
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def edit_salesReturn(request, pk):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data["CompanyID"]
            CompanyID = get_company(CompanyID)
            PriceRounding = data["PriceRounding"]
            CreatedUserID = data["CreatedUserID"]

            today = datetime.datetime.now()
            salesReturnkMaster_instance = None
            salesReturnDetails = None
            salesReturnkMaster_instance = SalesReturnMaster.objects.get(
                CompanyID=CompanyID, pk=pk
            )
            SalesReturnMasterID = salesReturnkMaster_instance.SalesReturnMasterID
            BranchID = salesReturnkMaster_instance.BranchID
            VoucherNo = salesReturnkMaster_instance.VoucherNo

            Action = "M"

            if SalesReturnDetails.objects.filter(
                CompanyID=CompanyID,
                BranchID=BranchID,
                SalesReturnMasterID=SalesReturnMasterID,
            ).exists():
                sale_ins = SalesReturnDetails.objects.filter(
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    SalesReturnMasterID=SalesReturnMasterID,
                )
                for i in sale_ins:
                    BatchCode = i.BatchCode
                    Qty = i.Qty
                    instance_MultiFactor = PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=i.PriceListID
                    ).MultiFactor

                    instance_qty_sum = converted_float(i.FreeQty) + converted_float(i.Qty)
                    instance_Qty = converted_float(instance_MultiFactor) * converted_float(instance_qty_sum)
                    if Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode
                    ).exists():
                        batch_ins = Batch.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode
                        )
                        StockIn = batch_ins.StockIn
                        batch_ins.StockIn = converted_float(StockIn) - converted_float(instance_Qty)
                        batch_ins.save()

                    if not StockPosting.objects.filter(
                        CompanyID=CompanyID,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherDetailID=i.SalesReturnDetailsID,
                        BranchID=BranchID,
                        VoucherType="SR",
                    ).exists():
                        StockPosting.objects.filter(
                            CompanyID=CompanyID,
                            VoucherMasterID=SalesReturnMasterID,
                            BranchID=BranchID,
                            VoucherType="SR",
                        ).delete()
                        update_stock(CompanyID, BranchID, i.ProductID)

                    if StockPosting.objects.filter(
                        CompanyID=CompanyID,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherDetailID=i.SalesReturnDetailsID,
                        ProductID=i.ProductID,
                        BranchID=BranchID,
                        VoucherType="SR",
                    ).exists():
                        stock_inst = StockPosting.objects.filter(
                            CompanyID=CompanyID,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherDetailID=i.SalesReturnDetailsID,
                            ProductID=i.ProductID,
                            BranchID=BranchID,
                            VoucherType="SR",
                        ).first()
                        stock_inst.QtyIn = converted_float(stock_inst.QtyIn) - converted_float(instance_Qty)
                        stock_inst.save()
                        update_stock(CompanyID, BranchID, i.ProductID)

            data = request.data

            VoucherDate = data["VoucherDate"]
            RefferenceBillNo = data["RefferenceBillNo"]
            RefferenceBillDate = data["RefferenceBillDate"]
            CreditPeriod = data["CreditPeriod"]
            LedgerID = data["LedgerID"]
            PriceCategoryID = data["PriceCategoryID"]
            EmployeeID = data["EmployeeID"]
            SalesAccount = data["SalesAccount"]
            DeliveryMasterID = data["DeliveryMasterID"]
            OrderMasterID = data["OrderMasterID"]
            CustomerName = data["CustomerName"]
            Address1 = data["Address1"]
            Address2 = data["Address2"]
            Address3 = data["Address3"]
            Notes = data["Notes"]
            FinacialYearID = data["FinacialYearID"]
            WarehouseID = data["WarehouseID"]
            TableID = data["TableID"]
            SeatNumber = data["SeatNumber"]
            NoOfGuests = data["NoOfGuests"]
            INOUT = data["INOUT"]
            TokenNumber = data["TokenNumber"]
            IsActive = data["IsActive"]
            IsPosted = data["IsPosted"]
            SalesType = data["SalesType"]
            BatchID = data["BatchID"]
            try:
                TaxID = data["TaxID"]
            except:
                TaxID = 1
            try:
                TaxType = data["TaxType"]
            except:
                TaxType = ""
            # CashAmount = data['CashAmount']

            TotalGrossAmt = converted_float(data["TotalGrossAmt"])
            TotalTax = converted_float(data["TotalTax"])
            NetTotal = converted_float(data["NetTotal"])
            AdditionalCost = converted_float(data["AdditionalCost"])
            GrandTotal = converted_float(data["GrandTotal"])
            RoundOff = converted_float(data["RoundOff"])
            CashReceived = converted_float(data["CashReceived"])
            BankAmount = converted_float(data["BankAmount"])
            VATAmount = converted_float(data["VATAmount"])
            SGSTAmount = converted_float(data["SGSTAmount"])
            CGSTAmount = converted_float(data["CGSTAmount"])
            IGSTAmount = converted_float(data["IGSTAmount"])
            TAX1Amount = converted_float(data["TAX1Amount"])
            TAX2Amount = converted_float(data["TAX2Amount"])
            TAX3Amount = converted_float(data["TAX3Amount"])
            AddlDiscPercent = converted_float(data["AddlDiscPercent"])
            AddlDiscAmt = converted_float(data["AddlDiscAmt"])
            TotalDiscount = converted_float(data["TotalDiscount"])
            BillDiscPercent = converted_float(data["BillDiscPercent"])
            BillDiscAmt = converted_float(data["BillDiscAmt"])

            try:
                KFCAmount = converted_float(data["KFCAmount"])
            except:
                KFCAmount = 0

            try:
                Country_of_Supply = data["Country_of_Supply"]
            except:
                Country_of_Supply = ""

            try:
                State_of_Supply = data["State_of_Supply"]
            except:
                State_of_Supply = ""

            try:
                GST_Treatment = data["GST_Treatment"]
            except:
                GST_Treatment = ""

            try:
                VAT_Treatment = data["VAT_Treatment"]
            except:
                VAT_Treatment = ""
            try:
                TaxTaxableAmount = converted_float(data["TaxTaxableAmount"])
            except:
                TaxTaxableAmount = 0
            try:
                NonTaxTaxableAmount = converted_float(data["NonTaxTaxableAmount"])
            except:
                NonTaxTaxableAmount = 0
                
            try:
                BillingAddress = data["BillingAddress"]
            except:
                BillingAddress = None
                
            Cash_Account = None
            Bank_Account = None

            if UserTable.objects.filter(
                CompanyID=CompanyID, customer__user__pk=CreatedUserID,Active=True
            ).exists():
                Cash_Account = UserTable.objects.get(
                    CompanyID=CompanyID, customer__user__pk=CreatedUserID,Active=True
                ).Cash_Account
                Bank_Account = UserTable.objects.get(
                    CompanyID=CompanyID, customer__user__pk=CreatedUserID, Active=True
                ).Bank_Account

            try:
                CashID = data["CashID"]
            except:
                CashID = Cash_Account

            try:
                BankID = data["BankID"]
            except:
                BankID = Bank_Account
            
            if BillingAddress:
                if UserAdrress.objects.filter(id=BillingAddress).exists():
                    BillingAddress = UserAdrress.objects.get(
                        id=BillingAddress)

            # KFCAmount = round(KFCAmount, PriceRounding)

            # TotalGrossAmt = round(TotalGrossAmt, PriceRounding)
            # TotalTax = round(TotalTax, PriceRounding)
            # NetTotal = round(NetTotal, PriceRounding)
            # AdditionalCost = round(AdditionalCost, PriceRounding)
            # GrandTotal = round(GrandTotal, PriceRounding)

            # RoundOff = round(RoundOff, PriceRounding)
            # CashReceived = round(CashReceived, PriceRounding)
            # BankAmount = round(BankAmount, PriceRounding)
            # VATAmount = round(VATAmount, PriceRounding)
            # SGSTAmount = round(SGSTAmount, PriceRounding)

            # CGSTAmount = round(CGSTAmount, PriceRounding)
            # IGSTAmount = round(IGSTAmount, PriceRounding)
            # TAX1Amount = round(TAX1Amount, PriceRounding)
            # TAX2Amount = round(TAX2Amount, PriceRounding)
            # TAX3Amount = round(TAX3Amount, PriceRounding)

            # AddlDiscPercent = round(AddlDiscPercent, PriceRounding)
            # AddlDiscAmt = round(AddlDiscAmt, PriceRounding)
            # TotalDiscount = round(TotalDiscount, PriceRounding)
            # BillDiscPercent = round(BillDiscPercent, PriceRounding)
            # BillDiscAmt = round(BillDiscAmt, PriceRounding)

            CashAmount = converted_float(GrandTotal) - converted_float(BankAmount)

            TotalTaxableAmount = 0
            salesReturnDetails = data["SalesReturnDetails"]
            for salesReturnDetail in salesReturnDetails:
                TaxableAmount = salesReturnDetail["TaxableAmount"]
                TotalTaxableAmount += converted_float(TaxableAmount)

            update_ledger = UpdateLedgerBalance(
                CompanyID, BranchID, 0, SalesReturnMasterID, "SR", 0, "Cr", "update"
            )
            if LedgerPosting.objects.filter(
                CompanyID=CompanyID,
                VoucherMasterID=SalesReturnMasterID,
                BranchID=BranchID,
                VoucherType="SR",
            ).exists():
                ledgerPostInstances = LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    VoucherMasterID=SalesReturnMasterID,
                    BranchID=BranchID,
                    VoucherType="SR",
                ).delete()

            # if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=SalesReturnMasterID, BranchID=BranchID, VoucherType="SR").exists():
            #     stockPostingInstances = StockPosting.objects.filter(
            #         CompanyID=CompanyID, VoucherMasterID=SalesReturnMasterID, BranchID=BranchID, VoucherType="SR").delete()

            SalesReturnMaster_Log.objects.create(
                TransactionID=SalesReturnMasterID,
                TotalTaxableAmount=TotalTaxableAmount,
                BranchID=BranchID,
                Action=Action,
                VoucherNo=VoucherNo,
                VoucherDate=VoucherDate,
                RefferenceBillNo=RefferenceBillNo,
                RefferenceBillDate=RefferenceBillDate,
                CreditPeriod=CreditPeriod,
                LedgerID=LedgerID,
                PriceCategoryID=PriceCategoryID,
                EmployeeID=EmployeeID,
                SalesAccount=SalesAccount,
                DeliveryMasterID=DeliveryMasterID,
                OrderMasterID=OrderMasterID,
                CustomerName=CustomerName,
                Address1=Address1,
                Address2=Address2,
                Address3=Address3,
                Notes=Notes,
                FinacialYearID=FinacialYearID,
                TotalGrossAmt=TotalGrossAmt,
                TotalTax=TotalTax,
                NetTotal=NetTotal,
                AdditionalCost=AdditionalCost,
                GrandTotal=GrandTotal,
                RoundOff=RoundOff,
                CashReceived=CashReceived,
                CashAmount=CashAmount,
                BankAmount=BankAmount,
                WarehouseID=WarehouseID,
                TableID=TableID,
                SeatNumber=SeatNumber,
                NoOfGuests=NoOfGuests,
                INOUT=INOUT,
                TokenNumber=TokenNumber,
                IsActive=IsActive,
                IsPosted=IsPosted,
                SalesType=SalesType,
                CreatedUserID=CreatedUserID,
                UpdatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                TaxID=TaxID,
                TaxType=TaxType,
                VATAmount=VATAmount,
                SGSTAmount=SGSTAmount,
                CGSTAmount=CGSTAmount,
                IGSTAmount=IGSTAmount,
                TAX1Amount=TAX1Amount,
                TAX2Amount=TAX2Amount,
                TAX3Amount=TAX3Amount,
                AddlDiscPercent=AddlDiscPercent,
                AddlDiscAmt=AddlDiscAmt,
                TotalDiscount=TotalDiscount,
                BillDiscPercent=BillDiscPercent,
                BillDiscAmt=BillDiscAmt,
                CompanyID=CompanyID,
                KFCAmount=KFCAmount,
                Country_of_Supply=Country_of_Supply,
                State_of_Supply=State_of_Supply,
                GST_Treatment=GST_Treatment,
                VAT_Treatment=VAT_Treatment,
                TaxTaxableAmount=TaxTaxableAmount,
                NonTaxTaxableAmount=NonTaxTaxableAmount,
                BillingAddress=BillingAddress,
                CashID=CashID,
                BankID=BankID,
            )

            if SerialNumbers.objects.filter(
                CompanyID=CompanyID,
                SalesMasterID=SalesReturnMasterID,
                BranchID=BranchID,
                VoucherType="SR",
            ).exists():
                SerialNumbersInstances = SerialNumbers.objects.filter(
                    CompanyID=CompanyID,
                    SalesMasterID=SalesReturnMasterID,
                    BranchID=BranchID,
                    VoucherType="SR",
                )
                for sli in SerialNumbersInstances:
                    sli.delete()

            LoyaltyCustomerID = data["LoyaltyCustomerID"]

            loyalty_customer = None
            is_LoyaltyCustomer = False
            if LoyaltyCustomerID:
                if LoyaltyCustomer.objects.filter(
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    LoyaltyCustomerID=LoyaltyCustomerID,
                ).exists():
                    loyalty_customer = LoyaltyCustomer.objects.get(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        LoyaltyCustomerID=LoyaltyCustomerID,
                    )
                    is_LoyaltyCustomer = True

            salesReturnkMaster_instance.VoucherDate = VoucherDate
            salesReturnkMaster_instance.RefferenceBillNo = RefferenceBillNo
            salesReturnkMaster_instance.RefferenceBillDate = RefferenceBillDate
            salesReturnkMaster_instance.CreditPeriod = CreditPeriod
            salesReturnkMaster_instance.LedgerID = LedgerID
            salesReturnkMaster_instance.PriceCategoryID = PriceCategoryID
            salesReturnkMaster_instance.EmployeeID = EmployeeID
            salesReturnkMaster_instance.SalesAccount = SalesAccount
            salesReturnkMaster_instance.DeliveryMasterID = DeliveryMasterID
            salesReturnkMaster_instance.OrderMasterID = OrderMasterID
            salesReturnkMaster_instance.CustomerName = CustomerName
            salesReturnkMaster_instance.Address1 = Address1
            salesReturnkMaster_instance.Address2 = Address2
            salesReturnkMaster_instance.Address3 = Address3
            salesReturnkMaster_instance.Notes = Notes
            salesReturnkMaster_instance.FinacialYearID = FinacialYearID
            salesReturnkMaster_instance.TotalGrossAmt = TotalGrossAmt
            salesReturnkMaster_instance.TotalTax = TotalTax
            salesReturnkMaster_instance.NetTotal = NetTotal
            salesReturnkMaster_instance.AdditionalCost = AdditionalCost
            salesReturnkMaster_instance.GrandTotal = GrandTotal
            salesReturnkMaster_instance.RoundOff = RoundOff
            salesReturnkMaster_instance.CashReceived = CashReceived
            salesReturnkMaster_instance.CashAmount = CashAmount
            salesReturnkMaster_instance.BankAmount = BankAmount
            salesReturnkMaster_instance.WarehouseID = WarehouseID
            salesReturnkMaster_instance.TableID = TableID
            salesReturnkMaster_instance.SeatNumber = SeatNumber
            salesReturnkMaster_instance.NoOfGuests = NoOfGuests
            salesReturnkMaster_instance.INOUT = INOUT
            salesReturnkMaster_instance.TokenNumber = TokenNumber
            salesReturnkMaster_instance.IsActive = IsActive
            salesReturnkMaster_instance.IsPosted = IsPosted
            salesReturnkMaster_instance.SalesType = SalesType
            salesReturnkMaster_instance.Action = Action
            salesReturnkMaster_instance.UpdatedUserID = CreatedUserID
            salesReturnkMaster_instance.UpdatedDate = today
            salesReturnkMaster_instance.TaxID = TaxID
            salesReturnkMaster_instance.TaxType = TaxType
            salesReturnkMaster_instance.VATAmount = VATAmount
            salesReturnkMaster_instance.SGSTAmount = SGSTAmount
            salesReturnkMaster_instance.CGSTAmount = CGSTAmount
            salesReturnkMaster_instance.IGSTAmount = IGSTAmount
            salesReturnkMaster_instance.TAX1Amount = TAX1Amount
            salesReturnkMaster_instance.TAX2Amount = TAX2Amount
            salesReturnkMaster_instance.TAX3Amount = TAX3Amount
            salesReturnkMaster_instance.AddlDiscPercent = AddlDiscPercent
            salesReturnkMaster_instance.AddlDiscAmt = AddlDiscAmt
            salesReturnkMaster_instance.TotalDiscount = TotalDiscount
            salesReturnkMaster_instance.BillDiscPercent = BillDiscPercent
            salesReturnkMaster_instance.BillDiscAmt = BillDiscAmt
            salesReturnkMaster_instance.TotalTaxableAmount = TotalTaxableAmount
            salesReturnkMaster_instance.Country_of_Supply = Country_of_Supply
            salesReturnkMaster_instance.State_of_Supply = State_of_Supply
            salesReturnkMaster_instance.GST_Treatment = GST_Treatment
            salesReturnkMaster_instance.VAT_Treatment = VAT_Treatment
            salesReturnkMaster_instance.TaxTaxableAmount = TaxTaxableAmount
            salesReturnkMaster_instance.NonTaxTaxableAmount = NonTaxTaxableAmount
            if loyalty_customer:
                salesReturnkMaster_instance.LoyaltyCustomerID = loyalty_customer
            salesReturnkMaster_instance.KFCAmount = KFCAmount
            salesReturnkMaster_instance.BillingAddress = BillingAddress
            salesReturnkMaster_instance.CashID = CashID
            salesReturnkMaster_instance.BankID = BankID
            salesReturnkMaster_instance.save()
            
            # billwise table insertion
            VoucherType = "SR"
            try:
                billwiseDetails_datas = data['billwiseDetails_datas']
            except:
                billwiseDetails_datas = []
            add_return_billwise = True
            if billwiseDetails_datas:
                if BillWiseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PaymentVoucherType="SR", PaymentInvoiceNo=VoucherNo).exists():
                    BillWiseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PaymentVoucherType="SR", PaymentInvoiceNo=VoucherNo).delete()
                
                for b in billwiseDetails_datas:
                    BillwiseMasterID = b["BillwiseMasterID"]
                    Amount = b["Amount"]
                    BillwiseDetailsID = get_BillwiseDetailsID(
                        BranchID, CompanyID)
                    if BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID).exists():
                        bill_master_instance = BillWiseMaster.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID).first()
                        master_payment = bill_master_instance.Payments
                        if not Amount:
                            Amount = 0
                        if converted_float(Amount) > 0:
                            add_return_billwise = False
                            bill_master_instance.Payments = converted_float(
                                master_payment) + converted_float(Amount)
                            bill_master_instance.save()

                            BillWiseDetails.objects.create(
                                CompanyID=CompanyID,
                                BranchID=BranchID,
                                BillwiseDetailsID=BillwiseDetailsID,
                                BillwiseMasterID=BillwiseMasterID,
                                InvoiceNo=bill_master_instance.InvoiceNo,
                                VoucherType=bill_master_instance.VoucherType,
                                PaymentDate=VoucherDate,
                                Payments=Amount,
                                PaymentVoucherType=VoucherType,
                                PaymentInvoiceNo=VoucherNo
                            )
                if add_return_billwise:
                    handleBillwiseChanges(CompanyID, BranchID, CashReceived, BankAmount, GrandTotal,
                                          LedgerID, VoucherNo, VoucherType, "edit", CreditPeriod, SalesReturnMasterID, VoucherDate)
            else:
                handleBillwiseChanges(CompanyID, BranchID, CashReceived, BankAmount, GrandTotal,
                                      LedgerID, VoucherNo, VoucherType, "edit", CreditPeriod, SalesReturnMasterID, VoucherDate)
            
            # enable_billwise = get_GeneralSettings(CompanyID,BranchID,"EnableBillwise")
            # total_amount_received = converted_float(CashReceived) + converted_float(BankAmount)
            # paymnt_sm = 0
            # if enable_billwise and converted_float(total_amount_received) <= converted_float(GrandTotal) and AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, AccountGroupUnder__in=[10, 29]).exists():
            #     if BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=VoucherNo, VoucherType=VoucherType, CustomerID=LedgerID).exists():
            #         billwise_ins = BillWiseMaster.objects.filter(
            #             CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=VoucherNo, VoucherType=VoucherType, CustomerID=LedgerID).first()
            #         billwise_ins.VoucherDate = VoucherDate
            #         billwise_ins.InvoiceAmount = GrandTotal
            #         if BillWiseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=billwise_ins.BillwiseMasterID, InvoiceNo=VoucherNo, PaymentVoucherType=VoucherType, PaymentInvoiceNo=VoucherNo).exists():
            #             billwise_details = BillWiseDetails.objects.filter(
            #                 CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=billwise_ins.BillwiseMasterID, InvoiceNo=VoucherNo, PaymentVoucherType=VoucherType, PaymentInvoiceNo=VoucherNo).first()
            #             billwise_details.Payments = total_amount_received
            #             billwise_details.save()
            #             billwise_details_ins = BillWiseDetails.objects.filter(
            #                 CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=billwise_ins.BillwiseMasterID, InvoiceNo=VoucherNo)
            #             paymnt_sm = billwise_details_ins.aggregate(
            #                 Sum("Payments"))
            #             paymnt_sm = paymnt_sm["Payments__sum"]
            #         billwise_ins.Payments = paymnt_sm
            #         billwise_ins.save()
            #     elif BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=VoucherNo, VoucherType=VoucherType).exists():
            #         billwise_ins = BillWiseMaster.objects.filter(
            #             CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=VoucherNo, VoucherType=VoucherType).first()
            #         billwise_ins.VoucherDate = VoucherDate
            #         billwise_ins.InvoiceAmount = GrandTotal
            #         billwise_ins.CustomerID = LedgerID
            #         if BillWiseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=billwise_ins.BillwiseMasterID, InvoiceNo=VoucherNo, PaymentVoucherType=VoucherType, PaymentInvoiceNo=VoucherNo).exists():
            #             billwise_details = BillWiseDetails.objects.filter(
            #                 CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=billwise_ins.BillwiseMasterID, InvoiceNo=VoucherNo, PaymentVoucherType=VoucherType, PaymentInvoiceNo=VoucherNo).first()
            #             billwise_details.Payments = total_amount_received
            #             billwise_details.save()
            #             billwise_details_ins = BillWiseDetails.objects.filter(
            #                 CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=billwise_ins.BillwiseMasterID, InvoiceNo=VoucherNo)
            #             paymnt_sm = billwise_details_ins.aggregate(
            #                 Sum("Payments"))
            #             paymnt_sm = paymnt_sm["Payments__sum"]
            #         billwise_ins.Payments = paymnt_sm
            #         billwise_ins.save()
            #     else:
            #         BillwiseMasterID = get_BillwiseMasterID(
            #             BranchID, CompanyID)
            #         DueDate = get_nth_day_date(CreditPeriod)
            #         BillWiseMaster.objects.create(
            #             CompanyID=CompanyID,
            #             BranchID=BranchID,
            #             BillwiseMasterID=BillwiseMasterID,
            #             InvoiceNo=VoucherNo,
            #             TransactionID=SalesReturnMasterID,
            #             VoucherType=VoucherType,
            #             VoucherDate=VoucherDate,
            #             InvoiceAmount=GrandTotal,
            #             Payments=total_amount_received,
            #             DueDate=DueDate,
            #             CustomerID=LedgerID
            #         )
            #         BillwiseDetailsID = get_BillwiseDetailsID(
            #             BranchID, CompanyID)
            #         BillWiseDetails.objects.create(
            #             CompanyID=CompanyID,
            #             BranchID=BranchID,
            #             BillwiseDetailsID=BillwiseDetailsID,
            #             BillwiseMasterID=BillwiseMasterID,
            #             InvoiceNo=VoucherNo,
            #             VoucherType=VoucherType,
            #             PaymentDate=VoucherDate,
            #             Payments=total_amount_received,
            #             PaymentVoucherType=VoucherType,
            #             PaymentInvoiceNo=VoucherNo
            #         )

            # =====================Loyal Custpmer Point=====================
            is_MinimumSalePrice = data["is_Loyalty_SalesReturn_MinimumSalePrice"]
            today_date = datetime.datetime.now().date()
            if is_LoyaltyCustomer:
                if LoyaltyProgram.objects.filter(
                    BranchID=BranchID,
                    CompanyID=CompanyID,
                    FromDate__lte=today_date,
                    ToDate__gte=today_date,
                ).exists():
                    program_instance = LoyaltyProgram.objects.get(
                        BranchID=BranchID,
                        CompanyID=CompanyID,
                        FromDate__lte=today_date,
                        ToDate__gte=today_date,
                    )
                    print(program_instance.ProductType)
                    return_point = 0
                    tot_taxable_amnt = 0
                    salesReturnDetails = data["SalesReturnDetails"]
                    for salesReturnDetail in salesReturnDetails:
                        product_id = salesReturnDetail["ProductID"]
                        print(salesReturnDetail["ProductID"], "uvaissss")
                        TaxableAmount = salesReturnDetail["TaxableAmount"]
                        single_product_point = sales_return_point(
                            program_instance,
                            product_id,
                            TaxableAmount,
                            BranchID,
                            CompanyID,
                            is_MinimumSalePrice,
                        )
                        tot_taxable_amnt += single_product_point

                    actual_point = get_actual_point(tot_taxable_amnt, program_instance)
                    print(
                        loyalty_customer,
                        tot_taxable_amnt,
                        "tot_TaxableAmount actual_point",
                        actual_point,
                    )
                    CurrentPoint = 0
                    # loyalty_instance = LoyaltyCustomer.objects.get(
                    #     BranchID=BranchID, CompanyID=CompanyID, LoyaltyCustomerID=loyalty_customer.LoyaltyCustomerID)
                    if LoyaltyPoint.objects.filter(
                        BranchID=BranchID,
                        CompanyID=CompanyID,
                        LoyaltyCustomerID__pk=loyalty_customer.pk,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                    ).exists():
                        loyalty_point_instance = LoyaltyPoint.objects.get(
                            BranchID=BranchID,
                            CompanyID=CompanyID,
                            LoyaltyCustomerID__pk=loyalty_customer.pk,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                        )
                        loyalty_point_instance.delete()
                    CurrentPoint = loyalty_customer.CurrentPoint
                    if converted_float(CurrentPoint) >= converted_float(actual_point):
                        return_point = converted_float(CurrentPoint) - converted_float(actual_point)
                        print(return_point, "return_pointreturn_pointreturn_point")
                        loyalty_customer.CurrentPoint = return_point
                        loyalty_customer.save()
                        if actual_point:
                            LoyaltyPointID = get_point_auto_id(
                                LoyaltyPoint, BranchID, CompanyID
                            )
                            ExpiryDate = None
                            LoyaltyPoint.objects.create(
                                BranchID=BranchID,
                                LoyaltyPointID=LoyaltyPointID,
                                Value=actual_point * -1,
                                VoucherType=VoucherType,
                                VoucherMasterID=salesReturnkMaster_instance.SalesReturnMasterID,
                                Point=actual_point * -1,
                                ExpiryDate=ExpiryDate,
                                LoyaltyCustomerID=loyalty_customer,
                                LoyaltyProgramID=program_instance,
                                is_Radeem=False,
                                CreatedDate=today,
                                UpdatedDate=today,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )
                            LoyaltyPoint_Log.objects.create(
                                BranchID=BranchID,
                                LoyaltyPointID=LoyaltyPointID,
                                Value=actual_point * -1,
                                VoucherType=VoucherType,
                                VoucherMasterID=salesReturnkMaster_instance.SalesReturnMasterID,
                                Point=actual_point * -1,
                                ExpiryDate=ExpiryDate,
                                LoyaltyCustomerID=loyalty_customer,
                                LoyaltyProgramID=program_instance,
                                is_Radeem=False,
                                CreatedDate=today,
                                UpdatedDate=today,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )
                    elif converted_float(CurrentPoint) <= converted_float(actual_point):
                        return_point = converted_float(actual_point) - converted_float(CurrentPoint)
                        print(return_point, "return_pointreturn_pointreturn_point")
                        loyalty_customer.CurrentPoint = return_point
                        loyalty_customer.save()
                        if actual_point:
                            LoyaltyPointID = get_point_auto_id(
                                LoyaltyPoint, BranchID, CompanyID
                            )
                            ExpiryDate = None
                            LoyaltyPoint.objects.create(
                                BranchID=BranchID,
                                LoyaltyPointID=LoyaltyPointID,
                                Value=actual_point * -1,
                                VoucherType=VoucherType,
                                VoucherMasterID=salesReturnkMaster_instance.SalesReturnMasterID,
                                Point=actual_point * -1,
                                ExpiryDate=ExpiryDate,
                                LoyaltyCustomerID=loyalty_customer,
                                LoyaltyProgramID=program_instance,
                                is_Radeem=False,
                                CreatedDate=today,
                                UpdatedDate=today,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )
                            LoyaltyPoint_Log.objects.create(
                                BranchID=BranchID,
                                LoyaltyPointID=LoyaltyPointID,
                                Value=actual_point * -1,
                                VoucherType=VoucherType,
                                VoucherMasterID=salesReturnkMaster_instance.SalesReturnMasterID,
                                Point=actual_point * -1,
                                ExpiryDate=ExpiryDate,
                                LoyaltyCustomerID=loyalty_customer,
                                LoyaltyProgramID=program_instance,
                                is_Radeem=False,
                                CreatedDate=today,
                                UpdatedDate=today,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )
            # =================================END====================================

            # new posting starting from here

            # LedgerPostingID = get_auto_LedgerPostid(LedgerPosting, BranchID, CompanyID)

            # LedgerPosting.objects.create(
            #     LedgerPostingID=LedgerPostingID,
            #     BranchID=BranchID,
            #     Date=VoucherDate,
            #     VoucherMasterID=SalesReturnMasterID,
            #     VoucherType=VoucherType,
            #     VoucherNo=VoucherNo,
            #     LedgerID=SalesAccount,
            #     RelatedLedgerID=LedgerID,
            #     Debit=GrandTotal,
            #     IsActive=IsActive,
            #     Action=Action,
            #     CreatedUserID=CreatedUserID,
            #     CreatedDate=today,
            #     UpdatedDate=today,
            #     CompanyID=CompanyID,
            # )

            # LedgerPosting_Log.objects.create(
            #     TransactionID=LedgerPostingID,
            #     BranchID=BranchID,
            #     Date=VoucherDate,
            #     VoucherMasterID=SalesReturnMasterID,
            #     VoucherType=VoucherType,
            #     VoucherNo=VoucherNo,
            #     LedgerID=SalesAccount,
            #     RelatedLedgerID=LedgerID,
            #     Debit=GrandTotal,
            #     IsActive=IsActive,
            #     Action=Action,
            #     CreatedUserID=CreatedUserID,
            #     CreatedDate=today,
            #     UpdatedDate=today,
            #     CompanyID=CompanyID,
            # )

            # update_ledger = UpdateLedgerBalance(
            #     CompanyID,
            #     BranchID,
            #     SalesAccount,
            #     SalesReturnMasterID,
            #     VoucherType,
            #     GrandTotal,
            #     "Dr",
            #     "create",
            # )

            # LedgerPostingID = get_auto_LedgerPostid(LedgerPosting, BranchID, CompanyID)

            # LedgerPosting.objects.create(
            #     LedgerPostingID=LedgerPostingID,
            #     BranchID=BranchID,
            #     Date=VoucherDate,
            #     VoucherMasterID=SalesReturnMasterID,
            #     VoucherType=VoucherType,
            #     VoucherNo=VoucherNo,
            #     LedgerID=LedgerID,
            #     RelatedLedgerID=SalesAccount,
            #     Credit=GrandTotal,
            #     IsActive=IsActive,
            #     Action=Action,
            #     CreatedUserID=CreatedUserID,
            #     CreatedDate=today,
            #     UpdatedDate=today,
            #     CompanyID=CompanyID,
            # )

            # LedgerPosting_Log.objects.create(
            #     TransactionID=LedgerPostingID,
            #     BranchID=BranchID,
            #     Date=VoucherDate,
            #     VoucherMasterID=SalesReturnMasterID,
            #     VoucherType=VoucherType,
            #     VoucherNo=VoucherNo,
            #     LedgerID=LedgerID,
            #     RelatedLedgerID=SalesAccount,
            #     Credit=GrandTotal,
            #     IsActive=IsActive,
            #     Action=Action,
            #     CreatedUserID=CreatedUserID,
            #     CreatedDate=today,
            #     UpdatedDate=today,
            #     CompanyID=CompanyID,
            # )

            # update_ledger = UpdateLedgerBalance(
            #     CompanyID,
            #     BranchID,
            #     LedgerID,
            #     SalesReturnMasterID,
            #     VoucherType,
            #     GrandTotal,
            #     "Cr",
            #     "create",
            # )
            
            account_group = AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID
            ).AccountGroupUnder

            if TaxType == "VAT":
                if converted_float(VATAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=55,
                        RelatedLedgerID=SalesAccount,
                        Debit=VATAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=55,
                        RelatedLedgerID=SalesAccount,
                        Debit=VATAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        55,
                        SalesReturnMasterID,
                        VoucherType,
                        VATAmount,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=55,
                        Credit=VATAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=55,
                        Credit=VATAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        VATAmount,
                        "Cr",
                        "create",
                    )

            elif TaxType == "GST Intra-state B2B" or TaxType == "GST Intra-state B2C":
                if converted_float(CGSTAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=3,
                        RelatedLedgerID=SalesAccount,
                        Debit=CGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )
                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=3,
                        RelatedLedgerID=SalesAccount,
                        Debit=CGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        3,
                        SalesReturnMasterID,
                        VoucherType,
                        CGSTAmount,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=3,
                        Credit=CGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=3,
                        Credit=CGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        CGSTAmount,
                        "Cr",
                        "create",
                    )

                if converted_float(SGSTAmount) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=10,
                        RelatedLedgerID=SalesAccount,
                        Debit=SGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )
                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=10,
                        RelatedLedgerID=SalesAccount,
                        Debit=SGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        10,
                        SalesReturnMasterID,
                        VoucherType,
                        SGSTAmount,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=10,
                        Credit=SGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=10,
                        Credit=SGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        SGSTAmount,
                        "Cr",
                        "create",
                    )

                if converted_float(KFCAmount) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=93,
                        RelatedLedgerID=SalesAccount,
                        Debit=KFCAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )
                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=93,
                        RelatedLedgerID=SalesAccount,
                        Debit=KFCAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        93,
                        SalesReturnMasterID,
                        VoucherType,
                        KFCAmount,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=93,
                        Credit=KFCAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=93,
                        Credit=KFCAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        KFCAmount,
                        "Cr",
                        "create",
                    )

            elif TaxType == "GST Inter-state B2B" or TaxType == "GST Inter-state B2C":
                if converted_float(IGSTAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=17,
                        RelatedLedgerID=SalesAccount,
                        Debit=IGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=17,
                        RelatedLedgerID=SalesAccount,
                        Debit=IGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        17,
                        SalesReturnMasterID,
                        VoucherType,
                        IGSTAmount,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=17,
                        Credit=IGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=17,
                        Credit=IGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        IGSTAmount,
                        "Cr",
                        "create",
                    )

            if not TaxType == "Export":
                if converted_float(TAX1Amount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=16,
                        RelatedLedgerID=SalesAccount,
                        Debit=TAX1Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=16,
                        RelatedLedgerID=SalesAccount,
                        Debit=TAX1Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        16,
                        SalesReturnMasterID,
                        VoucherType,
                        TAX1Amount,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=16,
                        Credit=TAX1Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=16,
                        Credit=TAX1Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        TAX1Amount,
                        "Cr",
                        "create",
                    )

                if converted_float(TAX2Amount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=19,
                        RelatedLedgerID=SalesAccount,
                        Debit=TAX2Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=19,
                        RelatedLedgerID=SalesAccount,
                        Debit=TAX2Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        19,
                        SalesReturnMasterID,
                        VoucherType,
                        TAX2Amount,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=19,
                        Credit=TAX2Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=19,
                        Credit=TAX2Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        TAX2Amount,
                        "Cr",
                        "create",
                    )

                if converted_float(TAX3Amount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=22,
                        RelatedLedgerID=SalesAccount,
                        Debit=TAX3Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=22,
                        RelatedLedgerID=SalesAccount,
                        Debit=TAX3Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        22,
                        SalesReturnMasterID,
                        VoucherType,
                        TAX3Amount,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=22,
                        Credit=TAX3Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=22,
                        Credit=TAX3Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        TAX3Amount,
                        "Cr",
                        "create",
                    )

            if converted_float(RoundOff) > 0:

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=78,
                    RelatedLedgerID=SalesAccount,
                    Debit=RoundOff,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=78,
                    RelatedLedgerID=SalesAccount,
                    Debit=RoundOff,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    78,
                    SalesReturnMasterID,
                    VoucherType,
                    RoundOff,
                    "Dr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=78,
                    Credit=RoundOff,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=78,
                    Credit=RoundOff,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    SalesAccount,
                    SalesReturnMasterID,
                    VoucherType,
                    RoundOff,
                    "Cr",
                    "create",
                )

            if converted_float(RoundOff) < 0:

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID
                )

                RoundOff = abs(converted_float(RoundOff))

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=78,
                    RelatedLedgerID=SalesAccount,
                    Credit=RoundOff,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=78,
                    RelatedLedgerID=SalesAccount,
                    Credit=RoundOff,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    78,
                    SalesReturnMasterID,
                    VoucherType,
                    RoundOff,
                    "Cr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=78,
                    Debit=RoundOff,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=78,
                    Debit=RoundOff,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    SalesAccount,
                    SalesReturnMasterID,
                    VoucherType,
                    RoundOff,
                    "Dr",
                    "create",
                )

            if converted_float(TotalDiscount) > 0:

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=74,
                    RelatedLedgerID=SalesAccount,
                    Credit=TotalDiscount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=74,
                    RelatedLedgerID=SalesAccount,
                    Credit=TotalDiscount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    74,
                    SalesReturnMasterID,
                    VoucherType,
                    TotalDiscount,
                    "Cr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=74,
                    Debit=TotalDiscount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=74,
                    Debit=TotalDiscount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    SalesAccount,
                    SalesReturnMasterID,
                    VoucherType,
                    TotalDiscount,
                    "Dr",
                    "create",
                )

            # credit sales start here
            if (
                converted_float(CashReceived) == 0
                and converted_float(BankAmount) == 0
            ):
                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=LedgerID,
                    Debit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=LedgerID,
                    Debit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    SalesAccount,
                    SalesReturnMasterID,
                    VoucherType,
                    GrandTotal,
                    "Dr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=SalesAccount,
                    Credit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=SalesAccount,
                    Credit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    LedgerID,
                    SalesReturnMasterID,
                    VoucherType,
                    GrandTotal,
                    "Cr",
                    "create",
                )

            # credit sales end here

            # customer with cash and customer with partial cash start here
            elif (
                (account_group == 10 or account_group ==
                    29 or account_group == 32)
                and converted_float(CashReceived) > 0
                and converted_float(BankAmount) == 0
            ):
                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=LedgerID,
                    Debit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=LedgerID,
                    Debit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    SalesAccount,
                    SalesReturnMasterID,
                    VoucherType,
                    GrandTotal,
                    "Dr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=SalesAccount,
                    Credit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=SalesAccount,
                    Credit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    LedgerID,
                    SalesReturnMasterID,
                    VoucherType,
                    GrandTotal,
                    "Cr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=CashID,
                    RelatedLedgerID=LedgerID,
                    Credit=CashAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=CashID,
                    RelatedLedgerID=LedgerID,
                    Credit=CashAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    CashID,
                    SalesReturnMasterID,
                    VoucherType,
                    CashAmount,
                    "Cr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=CashID,
                    Debit=CashAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=CashID,
                    Debit=CashAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    LedgerID,
                    SalesReturnMasterID,
                    VoucherType,
                    CashAmount,
                    "Dr",
                    "create",
                )

            # customer with cash and customer with partial cash end here

            # customer with bank and customer with partial bank start here
            elif (
                (account_group == 10 or account_group ==
                    29 or account_group == 32)
                and converted_float(CashReceived) == 0
                and converted_float(BankAmount) > 0
            ):
                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=LedgerID,
                    Debit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=LedgerID,
                    Debit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    SalesAccount,
                    SalesReturnMasterID,
                    VoucherType,
                    GrandTotal,
                    "Dr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=SalesAccount,
                    Credit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=SalesAccount,
                    Credit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    LedgerID,
                    SalesReturnMasterID,
                    VoucherType,
                    GrandTotal,
                    "Cr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=BankID,
                    RelatedLedgerID=LedgerID,
                    Credit=BankAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=BankID,
                    RelatedLedgerID=LedgerID,
                    Credit=BankAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    BankID,
                    SalesReturnMasterID,
                    VoucherType,
                    BankAmount,
                    "Cr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=BankID,
                    Debit=BankAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=BankID,
                    Debit=BankAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    LedgerID,
                    SalesReturnMasterID,
                    VoucherType,
                    BankAmount,
                    "Dr",
                    "create",
                )

            # customer with bank and customer with partial bank end here

            # bank with cash and cash with cash start here
            elif (
                (account_group == 8 or account_group == 9)
                and converted_float(CashReceived) > 0
                and converted_float(BankAmount) == 0
            ):
                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=CashID,
                    Debit=CashAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=CashID,
                    Debit=CashAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    SalesAccount,
                    SalesReturnMasterID,
                    VoucherType,
                    CashAmount,
                    "Dr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=CashID,
                    RelatedLedgerID=SalesAccount,
                    Credit=CashAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=CashID,
                    RelatedLedgerID=SalesAccount,
                    Credit=CashAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    CashID,
                    SalesReturnMasterID,
                    VoucherType,
                    CashAmount,
                    "Cr",
                    "create",
                )

                csh_value = converted_float(GrandTotal) - converted_float(
                    CashReceived
                )
                if not converted_float(csh_value) == 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
                        Credit=csh_value,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
                        Credit=csh_value,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        LedgerID,
                        SalesReturnMasterID,
                        VoucherType,
                        csh_value,
                        "Cr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
                        Debit=csh_value,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
                        Debit=csh_value,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        csh_value,
                        "Dr",
                        "create",
                    )
            # bank with cash and cash with cash end here

            # bank with bank and cash with bank start here
            elif (
                (account_group == 8 or account_group == 9)
                and converted_float(CashReceived) == 0
                and converted_float(BankAmount) > 0
            ):
                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=BankID,
                    Debit=BankAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=BankID,
                    Debit=BankAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    SalesAccount,
                    SalesReturnMasterID,
                    VoucherType,
                    BankAmount,
                    "Dr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=BankID,
                    RelatedLedgerID=SalesAccount,
                    Credit=BankAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=BankID,
                    RelatedLedgerID=SalesAccount,
                    Credit=BankAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    BankID,
                    SalesReturnMasterID,
                    VoucherType,
                    BankAmount,
                    "Cr",
                    "create",
                )

                bnk_value = converted_float(GrandTotal) - converted_float(
                    BankAmount
                )
                if not converted_float(bnk_value) == 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
                        Credit=bnk_value,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
                        Credit=bnk_value,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        LedgerID,
                        SalesReturnMasterID,
                        VoucherType,
                        bnk_value,
                        "Cr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
                        Debit=bnk_value,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
                        Debit=bnk_value,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        bnk_value,
                        "Dr",
                        "create",
                    )
            # bank with bank and cash with bank end here

            # customer with partial cash /bank and customer with cash/bank
            elif (
                (account_group == 10 or account_group ==
                    29 or account_group == 32)
                and converted_float(CashReceived) > 0
                and converted_float(BankAmount) > 0
            ):
                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=LedgerID,
                    Debit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=LedgerID,
                    Debit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    SalesAccount,
                    SalesReturnMasterID,
                    VoucherType,
                    GrandTotal,
                    "Dr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=SalesAccount,
                    Credit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=SalesAccount,
                    Credit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    LedgerID,
                    SalesReturnMasterID,
                    VoucherType,
                    GrandTotal,
                    "Cr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=CashID,
                    RelatedLedgerID=LedgerID,
                    Credit=CashAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=CashID,
                    RelatedLedgerID=LedgerID,
                    Credit=CashAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    CashID,
                    SalesReturnMasterID,
                    VoucherType,
                    CashAmount,
                    "Cr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=CashID,
                    Debit=CashAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=CashID,
                    Debit=CashAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    LedgerID,
                    SalesReturnMasterID,
                    VoucherType,
                    CashAmount,
                    "Dr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=BankID,
                    RelatedLedgerID=LedgerID,
                    Credit=BankAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=BankID,
                    RelatedLedgerID=LedgerID,
                    Credit=BankAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    BankID,
                    SalesReturnMasterID,
                    VoucherType,
                    BankAmount,
                    "Cr",
                    "create",
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=BankID,
                    Debit=BankAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=BankID,
                    Debit=BankAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID,
                    BranchID,
                    LedgerID,
                    SalesReturnMasterID,
                    VoucherType,
                    BankAmount,
                    "Dr",
                    "create",
                )
            # customer with partial cash /bank and customer with cash/bank

            # cash with cash/bank start here
            elif (
                (account_group == 9 or account_group == 8)
                and converted_float(CashReceived) > 0
                and converted_float(BankAmount) > 0
            ):

                total_received = converted_float(CashReceived) + converted_float(
                    BankAmount
                )
                Balance_amt = converted_float(GrandTotal) - converted_float(
                    total_received
                )
                if not converted_float(Balance_amt) == 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
                        Debit=Balance_amt,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
                        Debit=Balance_amt,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        Balance_amt,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
                        Credit=Balance_amt,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
                        Credit=Balance_amt,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        LedgerID,
                        SalesReturnMasterID,
                        VoucherType,
                        Balance_amt,
                        "Cr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=SalesAccount,
                        Credit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=SalesAccount,
                        Credit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        BankID,
                        SalesReturnMasterID,
                        VoucherType,
                        BankAmount,
                        "Cr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=BankID,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=BankID,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        BankAmount,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=CashID,
                        Debit=CashReceived,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=CashID,
                        Debit=CashReceived,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        SalesAccount,
                        SalesReturnMasterID,
                        VoucherType,
                        CashReceived,
                        "Dr",
                        "create",
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID
                    )

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=SalesAccount,
                        Credit=CashReceived,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=SalesAccount,
                        Credit=CashReceived,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID,
                        BranchID,
                        CashID,
                        SalesReturnMasterID,
                        VoucherType,
                        CashReceived,
                        "Cr",
                        "create",
                    )

                # cash with cash/bank end here
            # deleted_datas = data["deleted_data"]
            # if deleted_datas:
            #     for deleted_Data in deleted_datas:
            #         SalesReturnDetailsID = deleted_Data['SalesReturnDetailsID']
            #         pk = deleted_Data['unq_id']

            #         if not pk == '':
            #             if SalesReturnDetails.objects.filter(pk=pk).exists():
            #                 deleted_detail = SalesReturnDetails.objects.get(pk=pk)
            #                 deleted_detail.delete()

            #             stockTrans_instance = None
            #             if StockTrans.objects.filter(DetailID=SalesReturnDetailsID,MasterID=SalesReturnMasterID,BranchID=BranchID,VoucherType=VoucherType,IsActive=True).exists():
            #                 stockTrans_instance = StockTrans.objects.get(DetailID=SalesReturnDetailsID,MasterID=SalesReturnMasterID,BranchID=BranchID,VoucherType=VoucherType,IsActive=True)
            #                 qty_in_stockTrans = stockTrans_instance.Qty
            #                 StockRateID = stockTrans_instance.StockRateID
            #                 stockTrans_instance.IsActive = False
            #                 stockTrans_instance.save()

            #                 stockRate_instance = StockRate.objects.get(StockRateID=StockRateID,BranchID=BranchID,WareHouseID=WarehouseID)
            #                 stockRate_instance.Qty = converted_float(stockRate_instance.Qty) - converted_float(qty_in_stockTrans)
            #                 stockRate_instance.save()

            deleted_datas = data["deleted_data"]
            if deleted_datas:
                for deleted_Data in deleted_datas:
                    deleted_pk = deleted_Data["unq_id"]
                    SalesReturnDetailsID_Deleted = deleted_Data["SalesReturnDetailsID"]
                    ProductID_Deleted = deleted_Data["ProductID"]
                    PriceListID_Deleted = deleted_Data["PriceListID"]
                    Rate_Deleted = deleted_Data["Rate"]
                    SalesReturnMasterID_Deleted = deleted_Data["SalesReturnMasterID"]
                    WarehouseID_Deleted = deleted_Data["WarehouseID"]

                    if PriceList.objects.filter(
                        CompanyID=CompanyID,
                        ProductID=ProductID_Deleted,
                        DefaultUnit=True,
                    ).exists():
                        priceList = PriceList.objects.get(
                            CompanyID=CompanyID,
                            ProductID=ProductID_Deleted,
                            DefaultUnit=True,
                        )
                        MultiFactor = priceList.MultiFactor
                        Cost = converted_float(Rate_Deleted) / converted_float(MultiFactor)
                        Ct = round(Cost, 4)
                        Cost_Deleted = str(Ct)

                        if not deleted_pk == "" or not deleted_pk == 0:
                            if SalesReturnDetails.objects.filter(
                                CompanyID=CompanyID, pk=deleted_pk
                            ).exists():
                                deleted_detail = SalesReturnDetails.objects.get(
                                    CompanyID=CompanyID, pk=deleted_pk
                                )

                                deleted_BatchCode = deleted_detail.BatchCode
                                deleted_batch = Batch.objects.filter(
                                    CompanyID=CompanyID,
                                    BranchID=BranchID,
                                    BatchCode=deleted_BatchCode,
                                ).first()

                                MultiFactor = PriceList.objects.get(
                                    CompanyID=CompanyID,
                                    PriceListID=PriceListID_Deleted,
                                    BranchID=BranchID,
                                ).MultiFactor

                                qty_batch = converted_float(deleted_detail.FreeQty) + converted_float(
                                    deleted_detail.Qty
                                )
                                Qty_batch = converted_float(MultiFactor) * converted_float(qty_batch)

                                if Batch.objects.filter(
                                    CompanyID=CompanyID,
                                    BranchID=BranchID,
                                    BatchCode=BatchCode,
                                ).exists():
                                    batch_ins = Batch.objects.get(
                                        CompanyID=CompanyID,
                                        BranchID=BranchID,
                                        BatchCode=BatchCode,
                                    )
                                    StockIn = batch_ins.StockIn
                                    batch_ins.StockIn = converted_float(StockIn) - converted_float(
                                        Qty_batch
                                    )
                                    batch_ins.save()
                                deleted_detail.delete()
                                # if StockRate.objects.filter(CompanyID=CompanyID,ProductID=ProductID_Deleted,PriceListID=PriceListID_Deleted,Cost=Cost_Deleted,WareHouseID=WarehouseID).exists():
                                #     stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,ProductID=ProductID_Deleted,PriceListID=PriceListID_Deleted,Cost=Cost_Deleted,WareHouseID=WarehouseID)
                                #     StockRateID = stockRate_instance.StockRateID
                                #     if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=SalesReturnDetailsID_Deleted,MasterID=SalesReturnMasterID_Deleted,BranchID=BranchID,
                                #         VoucherType=VoucherType,IsActive=True,StockRateID=StockRateID).exists():
                                #         stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID,DetailID=SalesReturnDetailsID_Deleted,MasterID=SalesReturnMasterID_Deleted,BranchID=BranchID,
                                #             VoucherType=VoucherType,IsActive=True,StockRateID=StockRateID)
                                #         qty_in_stockTrans = stockTrans_instance.Qty
                                #         stockRate_instance.Qty = converted_float(stockRate_instance.Qty) - converted_float(qty_in_stockTrans)
                                #         stockRate_instance.save()
                                #         stockTrans_instance.IsActive = False
                                #         stockTrans_instance.save()

                                if StockPosting.objects.filter(
                                    CompanyID=CompanyID,
                                    VoucherMasterID=SalesReturnMasterID_Deleted,
                                    VoucherDetailID=SalesReturnDetailsID_Deleted,
                                    ProductID=ProductID_Deleted,
                                    BranchID=BranchID,
                                    VoucherType="SR",
                                ).exists():
                                    stock_instances_delete = StockPosting.objects.filter(
                                        CompanyID=CompanyID,
                                        VoucherMasterID=SalesReturnMasterID_Deleted,
                                        VoucherDetailID=SalesReturnDetailsID_Deleted,
                                        ProductID=ProductID_Deleted,
                                        BranchID=BranchID,
                                        VoucherType="SR",
                                    )
                                    stock_instances_delete.delete()

                                    update_stock(CompanyID, BranchID, ProductID_Deleted)

                                # if StockTrans.objects.filter(CompanyID=CompanyID, DetailID=SalesReturnDetailsID_Deleted, MasterID=SalesReturnMasterID_Deleted, BranchID=BranchID, VoucherType=VoucherType, IsActive=True).exists():
                                #     stockTrans_instance = StockTrans.objects.filter(
                                #         CompanyID=CompanyID, DetailID=SalesReturnDetailsID_Deleted, MasterID=SalesReturnMasterID_Deleted, BranchID=BranchID, VoucherType=VoucherType, IsActive=True)
                                #     for stck in stockTrans_instance:
                                #         StockRateID = stck.StockRateID
                                #         stck.IsActive = False
                                #         qty_in_stockTrans = stck.Qty
                                #         if StockRate.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, BranchID=BranchID).exists():
                                #             stockRateInstance = StockRate.objects.get(
                                #                 CompanyID=CompanyID, StockRateID=StockRateID, BranchID=BranchID)
                                #             stockRateInstance.Qty = converted_float(
                                #                 stockRateInstance.Qty) - converted_float(qty_in_stockTrans)
                                #             stockRateInstance.save()
                                #         stck.save()

            salesReturnDetails = data["SalesReturnDetails"]

            for salesReturnDetail in salesReturnDetails:
                ProductID = salesReturnDetail["ProductID"]
                if ProductID:
                    pk = salesReturnDetail["unq_id"]
                    detailID = salesReturnDetail["detailID"]
                    # SalesReturnMasterID = serialized.data['SalesReturnMasterID']
                    DeliveryDetailsID = salesReturnDetail["DeliveryDetailsID"]
                    OrderDetailsID = salesReturnDetail["OrderDetailsID"]
                    Qty_detail = salesReturnDetail["Qty"]
                    FreeQty = salesReturnDetail["FreeQty"]
                    Flavour = salesReturnDetail["Flavour"]
                    # AddlDiscPercent = salesReturnDetail['AddlDiscPerc']

                    UnitPrice = converted_float(salesReturnDetail["UnitPrice"])
                    InclusivePrice = converted_float(salesReturnDetail["InclusivePrice"])
                    RateWithTax = converted_float(salesReturnDetail["RateWithTax"])
                    # CostPerPrice = converted_float(salesReturnDetail["CostPerPrice"])
                    PriceListID = converted_float(salesReturnDetail["PriceListID"])
                    DiscountPerc = converted_float(salesReturnDetail["DiscountPerc"])
                    DiscountAmount = converted_float(salesReturnDetail["DiscountAmount"])
                    GrossAmount = converted_float(salesReturnDetail["GrossAmount"])
                    TaxableAmount = converted_float(salesReturnDetail["TaxableAmount"])
                    VATPerc = converted_float(salesReturnDetail["VATPerc"])
                    VATAmount = converted_float(salesReturnDetail["VATAmount"])
                    SGSTPerc = converted_float(salesReturnDetail["SGSTPerc"])
                    SGSTAmount = converted_float(salesReturnDetail["SGSTAmount"])
                    CGSTPerc = converted_float(salesReturnDetail["CGSTPerc"])
                    CGSTAmount = converted_float(salesReturnDetail["CGSTAmount"])
                    IGSTPerc = converted_float(salesReturnDetail["IGSTPerc"])
                    IGSTAmount = converted_float(salesReturnDetail["IGSTAmount"])
                    NetAmount = converted_float(salesReturnDetail["NetAmount"])
                    AddlDiscPercent = AddlDiscPercent
                    AddlDiscAmt = converted_float(salesReturnDetail["AddlDiscAmt"])
                    TAX1Perc = converted_float(salesReturnDetail["TAX1Perc"])
                    TAX1Amount = converted_float(salesReturnDetail["TAX1Amount"])
                    TAX2Perc = converted_float(salesReturnDetail["TAX2Perc"])
                    TAX2Amount = converted_float(salesReturnDetail["TAX2Amount"])
                    TAX3Perc = converted_float(salesReturnDetail["TAX3Perc"])
                    TAX3Amount = converted_float(salesReturnDetail["TAX3Amount"])

                    # UnitPrice = round(UnitPrice, PriceRounding)
                    # InclusivePrice = round(InclusivePrice, PriceRounding)
                    # RateWithTax = round(RateWithTax, PriceRounding)
                    # CostPerPrice = round(CostPerPrice, PriceRounding)
                    # PriceListID = round(PriceListID, PriceRounding)

                    # DiscountPerc = round(DiscountPerc, PriceRounding)
                    # DiscountAmount = round(DiscountAmount, PriceRounding)
                    # GrossAmount = round(GrossAmount, PriceRounding)
                    # TaxableAmount = round(TaxableAmount, PriceRounding)
                    # VATPerc = round(VATPerc, PriceRounding)

                    # VATAmount = round(VATAmount, PriceRounding)
                    # SGSTPerc = round(SGSTPerc, PriceRounding)
                    # SGSTAmount = round(SGSTAmount, PriceRounding)
                    # CGSTPerc = round(CGSTPerc, PriceRounding)
                    # CGSTAmount = round(CGSTAmount, PriceRounding)

                    # IGSTPerc = round(IGSTPerc, PriceRounding)
                    # IGSTAmount = round(IGSTAmount, PriceRounding)
                    # NetAmount = round(NetAmount, PriceRounding)
                    # AddlDiscAmt = round(AddlDiscAmt, PriceRounding)
                    # TAX1Perc = round(TAX1Perc, PriceRounding)

                    # TAX1Amount = round(TAX1Amount, PriceRounding)
                    # TAX2Perc = round(TAX2Perc, PriceRounding)
                    # TAX2Amount = round(TAX2Amount, PriceRounding)
                    # TAX3Perc = round(TAX3Perc, PriceRounding)
                    # TAX3Amount = round(TAX3Amount, PriceRounding)

                    try:
                        SerialNos = salesdetail["SerialNos"]
                    except:
                        SerialNos = []

                    try:
                        Description = salesdetail["Description"]
                    except:
                        Description = ""

                    try:
                        BatchCode = salesReturnDetail["BatchCode"]
                    except:
                        BatchCode = 0
                    try:
                        is_inclusive = salesReturnDetail["is_inclusive"]
                    except:
                        is_inclusive = False

                    if is_inclusive == True:
                        Batch_salesPrice = InclusivePrice
                    else:
                        Batch_salesPrice = UnitPrice

                    try:
                        KFCAmount = salesReturnDetail["KFCAmount"]
                    except:
                        KFCAmount = 0

                    try:
                        KFCPerc = salesReturnDetail["KFCPerc"]
                    except:
                        KFCPerc = 0

                    try:
                        ProductTaxID = salesReturnDetail["ProductTaxID"]
                    except:
                        ProductTaxID = 0

                    # KFCAmount = round(KFCAmount, PriceRounding)
                    # KFCPerc = round(KFCPerc, PriceRounding)
                    CostPerPrice = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID
                        ).PurchasePrice
                        
                    product_is_Service = Product.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID
                    ).is_Service

                    product_purchasePrice = PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=PriceListID
                    ).PurchasePrice
                    MultiFactor = PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=PriceListID
                    ).MultiFactor

                    qty_batch = converted_float(FreeQty) + converted_float(Qty_detail)
                    Qty_batch = converted_float(MultiFactor) * converted_float(qty_batch)

                    check_AllowUpdateBatchPriceInSales = False
                    check_EnableProductBatchWise = False
                    if product_is_Service == False:
                        if GeneralSettings.objects.filter(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            SettingsType="AllowUpdateBatchPriceInSales",
                        ).exists():
                            check_AllowUpdateBatchPriceInSales = (
                                GeneralSettings.objects.get(
                                    CompanyID=CompanyID,
                                    BranchID=BranchID,
                                    SettingsType="AllowUpdateBatchPriceInSales",
                                ).SettingsValue
                            )

                        if GeneralSettings.objects.filter(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            SettingsType="EnableProductBatchWise",
                        ).exists():
                            check_EnableProductBatchWise = GeneralSettings.objects.get(
                                CompanyID=CompanyID,
                                BranchID=BranchID,
                                SettingsType="EnableProductBatchWise",
                            ).SettingsValue

                        if (
                            check_EnableProductBatchWise == True
                            or check_EnableProductBatchWise == "True"
                        ):
                            setbach = SetBatchInSales(
                                CompanyID,
                                BranchID,
                                Batch_salesPrice,
                                Qty_batch,
                                BatchCode,
                                check_AllowUpdateBatchPriceInSales,
                                PriceListID,
                                "SR",
                            )

                            # if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                            #     if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
                            #         if check_AllowUpdateBatchPriceInSales == "True" or check_AllowUpdateBatchPriceInSales == True:
                            #             batch_ins = Batch.objects.get(
                            #                 CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                            #             StockIn = batch_ins.StockIn
                            #             BatchCode = batch_ins.BatchCode
                            #             NewStock = converted_float(StockIn) + converted_float(Qty_batch)
                            #             batch_ins.StockIn = NewStock
                            #             batch_ins.SalesPrice = Batch_salesPrice
                            #             batch_ins.save()
                            #         else:
                            #             batch_ins = Batch.objects.get(
                            #                 CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                            #             StockIn = batch_ins.StockIn
                            #             BatchCode = batch_ins.BatchCode
                            #             NewStock = converted_float(StockIn) + converted_float(Qty_batch)
                            #             batch_ins.StockIn = NewStock
                            #             batch_ins.save()
                            #     else:
                            #         BatchCode = get_auto_AutoBatchCode(
                            #             Batch, BranchID, CompanyID)
                            #         Batch.objects.create(
                            #             CompanyID=CompanyID,
                            #             BranchID=BranchID,
                            #             BatchCode=BatchCode,
                            #             StockIn=Qty_batch,
                            #             PurchasePrice=product_purchasePrice,
                            #             SalesPrice=Batch_salesPrice,
                            #             PriceListID=PriceListID,
                            #             ProductID=ProductID,
                            #             WareHouseID=WarehouseID,
                            #             CreatedDate=today,
                            #             UpdatedDate=today,
                            #             CreatedUserID=CreatedUserID,
                            #         )

                            # else:
                            #     if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PriceListID=PriceListID).exists():
                            #         batch_ins = Batch.objects.get(
                            #             CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PriceListID=PriceListID)
                            #         StockIn = batch_ins.StockIn
                            #         BatchCode = batch_ins.BatchCode
                            #         NewStock = converted_float(StockIn) + converted_float(Qty_batch)
                            #         batch_ins.StockIn = NewStock
                            #         batch_ins.save()
                            #     else:
                            #         BatchCode = get_auto_AutoBatchCode(
                            #             Batch, BranchID, CompanyID)
                            #         Batch.objects.create(
                            #             CompanyID=CompanyID,
                            #             BranchID=BranchID,
                            #             BatchCode=BatchCode,
                            #             StockIn=Qty_batch,
                            #             PurchasePrice=product_purchasePrice,
                            #             SalesPrice=Batch_salesPrice,
                            #             PriceListID=PriceListID,
                            #             ProductID=ProductID,
                            #             WareHouseID=WarehouseID,
                            #             CreatedDate=today,
                            #             UpdatedDate=today,
                            #             CreatedUserID=CreatedUserID,
                            #         )

                    # priceList = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,DefaultUnit=True)

                    # PriceListID_DefUnit = priceList.PriceListID
                    # MultiFactor = priceList.MultiFactor

                    # MultiFactor = PriceList.objects.get(
                    #     CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor
                    PriceListID_DefUnit = PriceList.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True
                    ).PriceListID

                    # PurchasePrice = priceList.PurchasePrice
                    # SalesPrice = priceList.SalesPrice

                    qty = converted_float(FreeQty) + converted_float(Qty_detail)

                    Qty = converted_float(MultiFactor) * converted_float(qty)
                    Cost = converted_float(CostPerPrice) / converted_float(MultiFactor)

                    # Qy = round(Qty, 4)
                    # Qty = str(Qy)

                    # Ct = round(Cost, 4)
                    # Cost = str(Ct)

                    # deleted_datas = data["deleted_data"]
                    # if deleted_datas:
                    #     for deleted_Data in deleted_datas:
                    #         deleted_pk = deleted_Data['unq_id']
                    #         SalesReturnDetailsID = deleted_Data['SalesReturnDetailsID']
                    #         if not deleted_pk == '':
                    #             if SalesReturnDetails.objects.filter(pk=deleted_pk).exists():
                    #                 deleted_detail = SalesReturnDetails.objects.filter(pk=deleted_pk)
                    #                 deleted_detail.delete()

                    #                 if StockRate.objects.filter(ProductID=ProductID,PriceListID=PriceListID,Cost=Cost,WareHouseID=WarehouseID).exists():
                    #                     stockRate_instance = StockRate.objects.get(ProductID=ProductID,PriceListID=PriceListID,Cost=Cost,WareHouseID=WarehouseID)
                    #                     StockRateID = stockRate_instance.StockRateID
                    #                     stockTrans_instance = StockTrans.objects.get(DetailID=SalesReturnDetailsID,MasterID=SalesReturnMasterID,BranchID=BranchID,
                    #                         VoucherType=VoucherType,IsActive=True,StockRateID=StockRateID)
                    #                     qty_in_stockTrans = stockTrans_instance.Qty
                    #                     stockRate_instance.Qty = converted_float(stockRate_instance.Qty) - converted_float(qty_in_stockTrans)
                    #                     stockRate_instance.save()
                    #                     stockTrans_instance.IsActive = False
                    #                     stockTrans_instance.save()

                    princeList_instance = PriceList.objects.get(
                        CompanyID=CompanyID,
                        ProductID=ProductID,
                        PriceListID=PriceListID_DefUnit,
                    )
                    PurchasePrice = princeList_instance.PurchasePrice
                    SalesPrice = princeList_instance.SalesPrice

                    if detailID == 0:
                        salesReturnDetail_instance = SalesReturnDetails.objects.get(
                            CompanyID=CompanyID, pk=pk
                        )

                        SalesReturnDetailsID = (
                            salesReturnDetail_instance.SalesReturnDetailsID
                        )

                        log_instance = SalesReturnDetails_Log.objects.create(
                            TransactionID=SalesReturnDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesReturnMasterID=SalesReturnMasterID,
                            DeliveryDetailsID=DeliveryDetailsID,
                            OrderDetailsID=OrderDetailsID,
                            ProductID=ProductID,
                            Qty=Qty_detail,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            InclusivePrice=InclusivePrice,
                            RateWithTax=RateWithTax,
                            CostPerPrice=CostPerPrice,
                            PriceListID=PriceListID,
                            DiscountPerc=DiscountPerc,
                            DiscountAmount=DiscountAmount,
                            GrossAmount=GrossAmount,
                            TaxableAmount=TaxableAmount,
                            VATPerc=VATPerc,
                            VATAmount=VATAmount,
                            SGSTPerc=SGSTPerc,
                            SGSTAmount=SGSTAmount,
                            CGSTPerc=CGSTPerc,
                            CGSTAmount=CGSTAmount,
                            IGSTPerc=IGSTPerc,
                            IGSTAmount=IGSTAmount,
                            NetAmount=NetAmount,
                            Flavour=Flavour,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            AddlDiscPercent=AddlDiscPercent,
                            AddlDiscAmt=AddlDiscAmt,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            CompanyID=CompanyID,
                            BatchCode=BatchCode,
                            KFCAmount=KFCAmount,
                            KFCPerc=KFCPerc,
                            ProductTaxID=ProductTaxID,
                        )

                        salesReturnDetail_instance.DeliveryDetailsID = DeliveryDetailsID
                        salesReturnDetail_instance.OrderDetailsID = OrderDetailsID
                        salesReturnDetail_instance.ProductID = ProductID
                        salesReturnDetail_instance.Qty = Qty_detail
                        salesReturnDetail_instance.FreeQty = FreeQty
                        salesReturnDetail_instance.UnitPrice = UnitPrice
                        salesReturnDetail_instance.InclusivePrice = InclusivePrice
                        salesReturnDetail_instance.RateWithTax = RateWithTax
                        salesReturnDetail_instance.CostPerPrice = CostPerPrice
                        salesReturnDetail_instance.PriceListID = PriceListID
                        salesReturnDetail_instance.DiscountPerc = DiscountPerc
                        salesReturnDetail_instance.DiscountAmount = DiscountAmount
                        salesReturnDetail_instance.GrossAmount = GrossAmount
                        salesReturnDetail_instance.TaxableAmount = TaxableAmount
                        salesReturnDetail_instance.VATPerc = VATPerc
                        salesReturnDetail_instance.VATAmount = VATAmount
                        salesReturnDetail_instance.SGSTPerc = SGSTPerc
                        salesReturnDetail_instance.SGSTAmount = SGSTAmount
                        salesReturnDetail_instance.CGSTPerc = CGSTPerc
                        salesReturnDetail_instance.CGSTAmount = CGSTAmount
                        salesReturnDetail_instance.IGSTPerc = IGSTPerc
                        salesReturnDetail_instance.IGSTAmount = IGSTAmount
                        salesReturnDetail_instance.NetAmount = NetAmount
                        salesReturnDetail_instance.Flavour = Flavour
                        salesReturnDetail_instance.Action = Action
                        salesReturnDetail_instance.UpdatedUserID = CreatedUserID
                        salesReturnDetail_instance.UpdatedDate = today
                        salesReturnDetail_instance.AddlDiscPercent = AddlDiscPercent
                        salesReturnDetail_instance.AddlDiscAmt = AddlDiscAmt
                        salesReturnDetail_instance.TAX1Perc = TAX1Perc
                        salesReturnDetail_instance.TAX1Amount = TAX1Amount
                        salesReturnDetail_instance.TAX2Perc = TAX2Perc
                        salesReturnDetail_instance.TAX2Amount = TAX2Amount
                        salesReturnDetail_instance.TAX3Perc = TAX3Perc
                        salesReturnDetail_instance.TAX3Amount = TAX3Amount
                        salesReturnDetail_instance.BatchCode = BatchCode
                        salesReturnDetail_instance.LogID = log_instance.ID
                        salesReturnDetail_instance.KFCAmount = KFCAmount
                        salesReturnDetail_instance.KFCPerc = KFCPerc
                        salesReturnDetail_instance.ProductTaxID = ProductTaxID

                        salesReturnDetail_instance.save()

                        if product_is_Service == False:
                            if StockPosting.objects.filter(
                                CompanyID=CompanyID,
                                WareHouseID=WarehouseID,
                                VoucherMasterID=SalesReturnMasterID,
                                VoucherDetailID=SalesReturnDetailsID,
                                BranchID=BranchID,
                                VoucherType="SR",
                                ProductID=ProductID,
                            ).exists():
                                stock_instance = StockPosting.objects.filter(
                                    CompanyID=CompanyID,
                                    WareHouseID=WarehouseID,
                                    VoucherMasterID=SalesReturnMasterID,
                                    VoucherDetailID=SalesReturnDetailsID,
                                    BranchID=BranchID,
                                    VoucherType="SR",
                                    ProductID=ProductID,
                                ).first()
                                stock_instance.QtyIn = Qty
                                stock_instance.Action = Action
                                stock_instance.save()
                            else:
                                StockPostingID = get_auto_stockPostid(
                                    StockPosting, BranchID, CompanyID
                                )
                                pricelist, warehouse = get_ModelInstance(
                                    CompanyID,
                                    BranchID,
                                    PriceListID_DefUnit,
                                    WarehouseID,
                                )

                                StockPosting.objects.create(
                                    StockPostingID=StockPostingID,
                                    BranchID=BranchID,
                                    Action=Action,
                                    Date=VoucherDate,
                                    VoucherMasterID=SalesReturnMasterID,
                                    VoucherDetailID=SalesReturnDetailsID,
                                    VoucherType=VoucherType,
                                    ProductID=ProductID,
                                    BatchID=BatchCode,
                                    WareHouseID=WarehouseID,
                                    QtyIn=Qty,
                                    Rate=Cost,
                                    PriceListID=PriceListID_DefUnit,
                                    IsActive=IsActive,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CreatedUserID=CreatedUserID,
                                    CompanyID=CompanyID,
                                    pricelist=pricelist,
                                    warehouse=warehouse,
                                )

                                StockPosting_Log.objects.create(
                                    TransactionID=StockPostingID,
                                    BranchID=BranchID,
                                    Action=Action,
                                    Date=VoucherDate,
                                    VoucherMasterID=SalesReturnMasterID,
                                    VoucherDetailID=SalesReturnDetailsID,
                                    VoucherType=VoucherType,
                                    ProductID=ProductID,
                                    BatchID=BatchCode,
                                    WareHouseID=WarehouseID,
                                    QtyIn=Qty,
                                    Rate=Cost,
                                    PriceListID=PriceListID_DefUnit,
                                    IsActive=IsActive,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CreatedUserID=CreatedUserID,
                                    CompanyID=CompanyID,
                                )

                            update_stock(CompanyID, BranchID, ProductID)

                        # if product_is_Service == False:

                        #     StockPosting.objects.create(
                        #         StockPostingID=StockPostingID,
                        #         BranchID=BranchID,
                        #         Action=Action,
                        #         Date=VoucherDate,
                        #         VoucherMasterID=SalesReturnMasterID,
                        #         VoucherType=VoucherType,
                        #         ProductID=ProductID,
                        #         BatchID=BatchID,
                        #         WareHouseID=WarehouseID,
                        #         QtyIn=Qty,
                        #         Rate=Cost,
                        #         PriceListID=PriceListID_DefUnit,
                        #         IsActive=IsActive,
                        #         CreatedDate=today,
                        #         UpdatedDate=today,
                        #         CreatedUserID=CreatedUserID,
                        #         CompanyID=CompanyID,
                        #     )

                        #     StockPosting_Log.objects.create(
                        #         TransactionID=StockPostingID,
                        #         BranchID=BranchID,
                        #         Action=Action,
                        #         Date=VoucherDate,
                        #         VoucherMasterID=SalesReturnMasterID,
                        #         VoucherType=VoucherType,
                        #         ProductID=ProductID,
                        #         BatchID=BatchID,
                        #         WareHouseID=WarehouseID,
                        #         QtyIn=Qty,
                        #         Rate=Cost,
                        #         PriceListID=PriceListID_DefUnit,
                        #         IsActive=IsActive,
                        #         CreatedDate=today,
                        #         UpdatedDate=today,
                        #         CreatedUserID=CreatedUserID,
                        #         CompanyID=CompanyID,
                        #     )

                    if detailID == 1:

                        SalesReturnDetailsID = get_auto_id(
                            SalesReturnDetails, BranchID, CompanyID
                        )

                        Action = "A"

                        log_instance = SalesReturnDetails_Log.objects.create(
                            TransactionID=SalesReturnDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesReturnMasterID=SalesReturnMasterID,
                            DeliveryDetailsID=DeliveryDetailsID,
                            OrderDetailsID=OrderDetailsID,
                            ProductID=ProductID,
                            Qty=Qty_detail,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            InclusivePrice=InclusivePrice,
                            RateWithTax=RateWithTax,
                            CostPerPrice=CostPerPrice,
                            PriceListID=PriceListID,
                            DiscountPerc=DiscountPerc,
                            DiscountAmount=DiscountAmount,
                            GrossAmount=GrossAmount,
                            TaxableAmount=TaxableAmount,
                            VATPerc=VATPerc,
                            VATAmount=VATAmount,
                            SGSTPerc=SGSTPerc,
                            SGSTAmount=SGSTAmount,
                            CGSTPerc=CGSTPerc,
                            CGSTAmount=CGSTAmount,
                            IGSTPerc=IGSTPerc,
                            IGSTAmount=IGSTAmount,
                            NetAmount=NetAmount,
                            Flavour=Flavour,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            AddlDiscPercent=AddlDiscPercent,
                            AddlDiscAmt=AddlDiscAmt,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            CompanyID=CompanyID,
                            BatchCode=BatchCode,
                            KFCAmount=KFCAmount,
                            KFCPerc=KFCPerc,
                            ProductTaxID=ProductTaxID,
                        )

                        SalesReturnDetails.objects.create(
                            SalesReturnDetailsID=SalesReturnDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesReturnMasterID=SalesReturnMasterID,
                            DeliveryDetailsID=DeliveryDetailsID,
                            OrderDetailsID=OrderDetailsID,
                            ProductID=ProductID,
                            Qty=Qty_detail,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            InclusivePrice=InclusivePrice,
                            RateWithTax=RateWithTax,
                            CostPerPrice=CostPerPrice,
                            PriceListID=PriceListID,
                            DiscountPerc=DiscountPerc,
                            DiscountAmount=DiscountAmount,
                            GrossAmount=GrossAmount,
                            TaxableAmount=TaxableAmount,
                            VATPerc=VATPerc,
                            VATAmount=VATAmount,
                            SGSTPerc=SGSTPerc,
                            SGSTAmount=SGSTAmount,
                            CGSTPerc=CGSTPerc,
                            CGSTAmount=CGSTAmount,
                            IGSTPerc=IGSTPerc,
                            IGSTAmount=IGSTAmount,
                            NetAmount=NetAmount,
                            Flavour=Flavour,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            AddlDiscPercent=AddlDiscPercent,
                            AddlDiscAmt=AddlDiscAmt,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            CompanyID=CompanyID,
                            BatchCode=BatchCode,
                            LogID=log_instance.ID,
                            KFCAmount=KFCAmount,
                            KFCPerc=KFCPerc,
                            ProductTaxID=ProductTaxID,
                        )

                        if product_is_Service == False:
                            StockPostingID = get_auto_stockPostid(
                                StockPosting, BranchID, CompanyID
                            )
                            pricelist, warehouse = get_ModelInstance(
                                CompanyID, BranchID, PriceListID, WarehouseID
                            )

                            StockPosting.objects.create(
                                StockPostingID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=VoucherDate,
                                VoucherMasterID=SalesReturnMasterID,
                                VoucherDetailID=SalesReturnDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchCode,
                                WareHouseID=WarehouseID,
                                QtyIn=Qty,
                                Rate=Cost,
                                PriceListID=PriceListID_DefUnit,
                                IsActive=IsActive,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                                pricelist=pricelist,
                                warehouse=warehouse,
                            )

                            StockPosting_Log.objects.create(
                                TransactionID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=VoucherDate,
                                VoucherMasterID=SalesReturnMasterID,
                                VoucherDetailID=SalesReturnDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchCode,
                                WareHouseID=WarehouseID,
                                QtyIn=Qty,
                                Rate=Cost,
                                PriceListID=PriceListID_DefUnit,
                                IsActive=IsActive,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )

                            update_stock(CompanyID, BranchID, ProductID)

                    # if product_is_Service == False:
                    #     StockPostingID = get_auto_stockPostid(
                    #         StockPosting, BranchID, CompanyID)
                    #     StockPosting.objects.create(
                    #         StockPostingID=StockPostingID,
                    #         BranchID=BranchID,
                    #         Action=Action,
                    #         Date=VoucherDate,
                    #         VoucherMasterID=SalesReturnMasterID,
                    #         VoucherType=VoucherType,
                    #         ProductID=ProductID,
                    #         BatchID=BatchID,
                    #         WareHouseID=WarehouseID,
                    #         QtyIn=Qty,
                    #         Rate=Cost,
                    #         PriceListID=PriceListID_DefUnit,
                    #         IsActive=IsActive,
                    #         CreatedDate=today,
                    #         UpdatedDate=today,
                    #         CreatedUserID=CreatedUserID,
                    #         CompanyID=CompanyID,
                    #     )

                    #     StockPosting_Log.objects.create(
                    #         TransactionID=StockPostingID,
                    #         BranchID=BranchID,
                    #         Action=Action,
                    #         Date=VoucherDate,
                    #         VoucherMasterID=SalesReturnMasterID,
                    #         VoucherType=VoucherType,
                    #         ProductID=ProductID,
                    #         BatchID=BatchID,
                    #         WareHouseID=WarehouseID,
                    #         QtyIn=Qty,
                    #         Rate=Cost,
                    #         PriceListID=PriceListID_DefUnit,
                    #         IsActive=IsActive,
                    #         CreatedDate=today,
                    #         UpdatedDate=today,
                    #         CreatedUserID=CreatedUserID,
                    #         CompanyID=CompanyID,
                    #     )

                    #     update_stock(CompanyID,BranchID,ProductID)

                    if SerialNos:
                        for sn in SerialNos:
                            SerialNumbers.objects.create(
                                CompanyID=CompanyID,
                                VoucherType="SR",
                                SerialNo=sn["SerialNo"],
                                ItemCode=sn["ItemCode"],
                                SalesMasterID=SalesReturnMasterID,
                                SalesDetailsID=SalesReturnDetailsID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                            )

                    # if detailID == 1:
                    # if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID).exists():
                    #     stockRateInstance = StockRate.objects.get(
                    #         CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID)

                    #     StockRateID = stockRateInstance.StockRateID
                    #     stockRateInstance.Qty = converted_float(
                    #         stockRateInstance.Qty) + converted_float(Qty)
                    #     stockRateInstance.save()

                    #     if StockTrans.objects.filter(StockRateID=StockRateID, DetailID=SalesReturnDetailsID, MasterID=SalesReturnMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                    #         stockTra_in = StockTrans.objects.filter(
                    #             StockRateID=StockRateID, DetailID=SalesReturnDetailsID, MasterID=SalesReturnMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                    #         stockTra_in.Qty = converted_float(
                    #             stockTra_in.Qty) + converted_float(Qty)
                    #         stockTra_in.save()
                    #     else:
                    #         StockTransID = get_auto_StockTransID(
                    #             StockTrans, BranchID, CompanyID)
                    #         StockTrans.objects.create(
                    #             StockTransID=StockTransID,
                    #             BranchID=BranchID,
                    #             VoucherType=VoucherType,
                    #             StockRateID=StockRateID,
                    #             DetailID=SalesReturnDetailsID,
                    #             MasterID=SalesReturnMasterID,
                    #             Qty=Qty,
                    #             IsActive=IsActive,
                    #             CompanyID=CompanyID,
                    #         )

                    # else:
                    #     StockRateID = get_auto_StockRateID(
                    #         StockRate, BranchID, CompanyID)
                    #     StockRate.objects.create(
                    #         StockRateID=StockRateID,
                    #         BranchID=BranchID,
                    #         BatchID=BatchID,
                    #         PurchasePrice=PurchasePrice,
                    #         SalesPrice=SalesPrice,
                    #         Qty=Qty,
                    #         Cost=Cost,
                    #         ProductID=ProductID,
                    #         WareHouseID=WarehouseID,
                    #         Date=VoucherDate,
                    #         PriceListID=PriceListID_DefUnit,
                    #         CreatedUserID=CreatedUserID,
                    #         CreatedDate=today,
                    #         UpdatedDate=today,
                    #         CompanyID=CompanyID,
                    #     )

                    #     StockTransID = get_auto_StockTransID(
                    #         StockTrans, BranchID, CompanyID)
                    #     StockTrans.objects.create(
                    #         StockTransID=StockTransID,
                    #         BranchID=BranchID,
                    #         VoucherType=VoucherType,
                    #         StockRateID=StockRateID,
                    #         DetailID=SalesReturnDetailsID,
                    #         MasterID=SalesReturnMasterID,
                    #         Qty=Qty,
                    #         IsActive=IsActive,
                    #         CompanyID=CompanyID,
                    #     )
                    # else:
                    # if StockRate.objects.filter(CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit, Cost=Cost, WareHouseID=WarehouseID).exists():
                    #     stockRate_instance = StockRate.objects.get(
                    #         CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit, Cost=Cost, WareHouseID=WarehouseID)
                    #     StockRateID = stockRate_instance.StockRateID
                    #     if StockTrans.objects.filter(CompanyID=CompanyID, DetailID=SalesReturnDetailsID, MasterID=SalesReturnMasterID, BranchID=BranchID,
                    #                                  VoucherType=VoucherType, IsActive=True, StockRateID=StockRateID).exists():
                    #         stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID, DetailID=SalesReturnDetailsID, MasterID=SalesReturnMasterID, BranchID=BranchID,
                    #                                                      VoucherType=VoucherType, IsActive=True, StockRateID=StockRateID)

                    #         if converted_float(stockTrans_instance.Qty) < converted_float(Qty):
                    #             deff = converted_float(Qty) - \
                    #                 converted_float(stockTrans_instance.Qty)
                    #             stockTrans_instance.Qty = converted_float(
                    #                 stockTrans_instance.Qty) + converted_float(deff)
                    #             stockTrans_instance.save()

                    #             stockRate_instance.Qty = converted_float(
                    #                 stockRate_instance.Qty) + converted_float(deff)
                    #             stockRate_instance.save()

                    #         elif converted_float(stockTrans_instance.Qty) > converted_float(Qty):
                    #             deff = converted_float(
                    #                 stockTrans_instance.Qty) - converted_float(Qty)
                    #             stockTrans_instance.Qty = converted_float(
                    #                 stockTrans_instance.Qty) - converted_float(deff)
                    #             stockTrans_instance.save()

                    #             stockRate_instance.Qty = converted_float(
                    #                 stockRate_instance.Qty) - converted_float(deff)
                    #             stockRate_instance.save()
                    # ======

                    # ======

                    # if StockTrans.objects.filter(MasterID=SalesReturnMasterID,DetailID=SalesReturnDetailsID,BranchID=BranchID,VoucherType=VoucherType,IsActive=True).exists():
                    #     stockTrans_instance = StockTrans.objects.filter(MasterID=SalesReturnMasterID,DetailID=SalesReturnDetailsID,BranchID=BranchID,VoucherType=VoucherType,IsActive=True).first()
                    #     stockRateID = stockTrans_instance.StockRateID
                    #     stockRate_instance = StockRate.objects.get(StockRateID=stockRateID,BranchID=BranchID,WareHouseID=WarehouseID)

                    #     if converted_float(stockTrans_instance.Qty) < converted_float(Qty):
                    #         deff = converted_float(Qty) - converted_float(stockTrans_instance.Qty)
                    #         stockTrans_instance.Qty = converted_float(stockTrans_instance.Qty) + converted_float(deff)
                    #         stockTrans_instance.save()

                    #         stockRate_instance.Qty = converted_float(stockRate_instance.Qty) + converted_float(deff)
                    #         stockRate_instance.save()

                    #     elif converted_float(stockTrans_instance.Qty) > converted_float(Qty):
                    #         deff = converted_float(stockTrans_instance.Qty) - converted_float(Qty)
                    #         stockTrans_instance.Qty = converted_float(stockTrans_instance.Qty) - converted_float(deff)
                    #         stockTrans_instance.save()

                    #         stockRate_instance.Qty = converted_float(stockRate_instance.Qty) - converted_float(deff)
                    #         stockRate_instance.save()


            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sales Return',
            #              'Edit', 'Sales Return Updated Successfully.', 'Sales Return Updated Successfully.')
            cash_Balance = get_LedgerBalance(CompanyID, 1)
            response_data = {
                "StatusCode": 6000,
                "message": "Sales Returns Updated Successfully!!!",
                "CashBalance": cash_Balance,
            }

            return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again",
        }

        activity_log(
            request._request,
            CompanyID,
            "Error",
            CreatedUserID,
            "Sales Return",
            "Edit",
            str(e),
            err_descrb,
        )
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def list_salesReturnMaster(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]

    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data["BranchID"]

        if SalesReturnMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID
        ).exists():
            instances = SalesReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID
            )
            serialized = SalesReturnMasterRestSerializer(
                instances,
                many=True,
                context={"CompanyID": CompanyID, "PriceRounding": PriceRounding},
            )
            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sales Return',
            #              'List', 'Sales Return List Viewed Successfully.', 'Sales Return List Viewed Successfully.')

            response_data = {"StatusCode": 6000, "data": serialized.data}

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Sales Return',
            #              'List', 'Sales Return List Viewed Failed.', 'Sales Return not found in this branch')
            response_data = {
                "StatusCode": 6001,
                "message": "Sales Return Master not found in this branch.",
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch you enterd is not valid.",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def sales_return_pagination(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]

    page_number = data["page_no"]
    items_per_page = data["items_per_page"]

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]

        if page_number and items_per_page:
            sales_return_object = SalesReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID
            )

            sale_return_sort_pagination = list_pagination(
                sales_return_object, items_per_page, page_number
            )
            sale_serializer = SalesReturnMaster1RestSerializer(
                sale_return_sort_pagination,
                many=True,
                context={
                    "request": request,
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                },
            )
            data = sale_serializer.data
            if not data == None:
                response_data = {
                    "StatusCode": 6000,
                    "data": data,
                    "count": len(sales_return_object),
                }
            else:
                response_data = {"StatusCode": 6001}

            return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def salesReturnMaster(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    instance = None
    if SalesReturnMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = SalesReturnMaster.objects.get(CompanyID=CompanyID, pk=pk)

        serialized = SalesReturnMasterRestSerializer(
            instance, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding}
        )

        # request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sales Return', 'View',
        #              'Sales Return Single Viewed Successfully.', 'Sales Return Single Viewed Successfully.')

        response_data = {"StatusCode": 6000, "data": serialized.data}
    else:
        # request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Sales Return',
        #              'View', 'Sales Return Single Viewed Failed.', 'Sales Return Not Found')
        response_data = {
            "StatusCode": 6001,
            "message": "Sales Return Master Not Found!",
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def delete_salesReturnMaster(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    try:
        selecte_ids = data["selecte_ids"]
    except:
        selecte_ids = []

    today = datetime.datetime.now()
    instances = None
    if selecte_ids:
        if SalesReturnMaster.objects.filter(
            CompanyID=CompanyID, pk__in=selecte_ids
        ).exists():
            instances = SalesReturnMaster.objects.filter(pk__in=selecte_ids)
    else:
        if SalesReturnMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instances = SalesReturnMaster.objects.filter(pk=pk)

    if instances:
        for instance in instances:
            SalesReturnMasterID = instance.SalesReturnMasterID
            LoyaltyCustomerID = instance.LoyaltyCustomerID
            BranchID = instance.BranchID
            VoucherNo = instance.VoucherNo
            VoucherDate = instance.VoucherDate
            RefferenceBillNo = instance.RefferenceBillNo
            RefferenceBillDate = instance.RefferenceBillDate
            CreditPeriod = instance.CreditPeriod
            LedgerID = instance.LedgerID
            PriceCategoryID = instance.PriceCategoryID
            EmployeeID = instance.EmployeeID
            SalesAccount = instance.SalesAccount
            DeliveryMasterID = instance.DeliveryMasterID
            OrderMasterID = instance.OrderMasterID
            CustomerName = instance.CustomerName
            Address1 = instance.Address1
            Address2 = instance.Address2
            Address3 = instance.Address3
            Notes = instance.Notes
            FinacialYearID = instance.FinacialYearID
            TotalGrossAmt = instance.TotalGrossAmt
            TotalTax = instance.TotalTax
            NetTotal = instance.NetTotal
            AdditionalCost = instance.AdditionalCost
            GrandTotal = instance.GrandTotal
            RoundOff = instance.RoundOff
            CashReceived = instance.CashReceived
            CashAmount = instance.CashAmount
            BankAmount = instance.BankAmount
            WarehouseID = instance.WarehouseID
            TableID = instance.TableID
            SeatNumber = instance.SeatNumber
            NoOfGuests = instance.NoOfGuests
            INOUT = instance.INOUT
            TokenNumber = instance.TokenNumber
            IsActive = instance.IsActive
            IsPosted = instance.IsPosted
            SalesType = instance.SalesType
            TaxID = instance.TaxID
            TaxType = instance.TaxType
            VATAmount = instance.VATAmount
            SGSTAmount = instance.SGSTAmount
            CGSTAmount = instance.CGSTAmount
            IGSTAmount = instance.IGSTAmount
            TAX1Amount = instance.TAX1Amount
            TAX2Amount = instance.TAX2Amount
            TAX3Amount = instance.TAX3Amount
            AddlDiscPercent = instance.AddlDiscPercent
            AddlDiscAmt = instance.AddlDiscAmt
            TotalDiscount = instance.TotalDiscount
            BillDiscPercent = instance.BillDiscPercent
            BillDiscAmt = instance.BillDiscAmt
            KFCAmount = instance.KFCAmount
            Country_of_Supply = instance.Country_of_Supply
            State_of_Supply = instance.State_of_Supply
            GST_Treatment = instance.GST_Treatment
            VAT_Treatment = instance.VAT_Treatment
            Action = "D"
            if BillWiseMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,InvoiceNo=VoucherNo,TransactionID=SalesReturnMasterID,VoucherType="SR",Payments__gt=0).exists():
                response_data = {
                    "StatusCode": 6000,
                    "title": "Failed",
                    "message": "You can't Delete this Invoice(" + VoucherNo + ")this has been Paid",
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                if BillWiseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PaymentVoucherType="SR", PaymentInvoiceNo=VoucherNo).exists():
                    BillWiseDetails.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, PaymentVoucherType="SR", PaymentInvoiceNo=VoucherNo).delete()
                SalesReturnMaster_Log.objects.create(
                    TransactionID=SalesReturnMasterID,
                    LoyaltyCustomerID=LoyaltyCustomerID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    VoucherDate=VoucherDate,
                    RefferenceBillNo=RefferenceBillNo,
                    RefferenceBillDate=RefferenceBillDate,
                    CreditPeriod=CreditPeriod,
                    LedgerID=LedgerID,
                    PriceCategoryID=PriceCategoryID,
                    EmployeeID=EmployeeID,
                    SalesAccount=SalesAccount,
                    DeliveryMasterID=DeliveryMasterID,
                    OrderMasterID=OrderMasterID,
                    CustomerName=CustomerName,
                    Address1=Address1,
                    Address2=Address2,
                    Address3=Address3,
                    Notes=Notes,
                    FinacialYearID=FinacialYearID,
                    TotalGrossAmt=TotalGrossAmt,
                    TotalTax=TotalTax,
                    NetTotal=NetTotal,
                    AdditionalCost=AdditionalCost,
                    GrandTotal=GrandTotal,
                    RoundOff=RoundOff,
                    CashReceived=CashReceived,
                    CashAmount=CashAmount,
                    BankAmount=BankAmount,
                    WarehouseID=WarehouseID,
                    TableID=TableID,
                    SeatNumber=SeatNumber,
                    NoOfGuests=NoOfGuests,
                    INOUT=INOUT,
                    TokenNumber=TokenNumber,
                    IsActive=IsActive,
                    IsPosted=IsPosted,
                    SalesType=SalesType,
                    CreatedUserID=CreatedUserID,
                    UpdatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    TaxID=TaxID,
                    TaxType=TaxType,
                    VATAmount=VATAmount,
                    SGSTAmount=SGSTAmount,
                    CGSTAmount=CGSTAmount,
                    IGSTAmount=IGSTAmount,
                    TAX1Amount=TAX1Amount,
                    TAX2Amount=TAX2Amount,
                    TAX3Amount=TAX3Amount,
                    AddlDiscPercent=AddlDiscPercent,
                    AddlDiscAmt=AddlDiscAmt,
                    TotalDiscount=TotalDiscount,
                    BillDiscPercent=BillDiscPercent,
                    BillDiscAmt=BillDiscAmt,
                    CompanyID=CompanyID,
                    KFCAmount=KFCAmount,
                    Country_of_Supply=Country_of_Supply,
                    State_of_Supply=State_of_Supply,
                    GST_Treatment=GST_Treatment,
                    VAT_Treatment=VAT_Treatment,
                )

                if LedgerPosting.objects.filter(
                    CompanyID=CompanyID,
                    VoucherMasterID=SalesReturnMasterID,
                    BranchID=BranchID,
                    VoucherType="SR",
                ).exists():
                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, 0, SalesReturnMasterID, "SR", 0, "Cr", "update"
                    )
                    ledgerPostInstances = LedgerPosting.objects.filter(
                        CompanyID=CompanyID,
                        VoucherMasterID=SalesReturnMasterID,
                        BranchID=BranchID,
                        VoucherType="SR",
                    )

                    for ledgerPostInstance in ledgerPostInstances:

                        LedgerPostingID = ledgerPostInstance.LedgerPostingID
                        VoucherType = ledgerPostInstance.VoucherType
                        VoucherNo = ledgerPostInstance.VoucherNo
                        Debit = ledgerPostInstance.Debit
                        Credit = ledgerPostInstance.Credit
                        IsActive = ledgerPostInstance.IsActive
                        Date = ledgerPostInstance.Date
                        LedgerID = ledgerPostInstance.LedgerID
                        RelatedLedgerID = ledgerPostInstance.RelatedLedgerID

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=LedgerID,
                            RelatedLedgerID=RelatedLedgerID,
                            Credit=Credit,
                            Debit=Debit,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        ledgerPostInstance.delete()

                if StockPosting.objects.filter(
                    CompanyID=CompanyID,
                    VoucherMasterID=SalesReturnMasterID,
                    BranchID=BranchID,
                    VoucherType="SR",
                ).exists():

                    stockPostingInstances = StockPosting.objects.filter(
                        CompanyID=CompanyID,
                        VoucherMasterID=SalesReturnMasterID,
                        BranchID=BranchID,
                        VoucherType="SR",
                    )

                    for stockPostingInstance in stockPostingInstances:

                        StockPostingID = stockPostingInstance.StockPostingID
                        BranchID = stockPostingInstance.BranchID
                        Date = stockPostingInstance.Date
                        VoucherMasterID = stockPostingInstance.VoucherMasterID
                        VoucherDetailID = stockPostingInstance.VoucherDetailID
                        VoucherType = stockPostingInstance.VoucherType
                        ProductID = stockPostingInstance.ProductID
                        BatchID = stockPostingInstance.BatchID
                        WareHouseID = stockPostingInstance.WareHouseID
                        QtyIn = stockPostingInstance.QtyIn
                        QtyOut = stockPostingInstance.QtyOut
                        Rate = stockPostingInstance.Rate
                        PriceListID = stockPostingInstance.PriceListID
                        IsActive = stockPostingInstance.IsActive

                        StockPosting_Log.objects.create(
                            TransactionID=StockPostingID,
                            BranchID=BranchID,
                            Action=Action,
                            Date=Date,
                            VoucherMasterID=VoucherMasterID,
                            VoucherDetailID=VoucherDetailID,
                            VoucherType=VoucherType,
                            ProductID=ProductID,
                            BatchID=BatchID,
                            WareHouseID=WareHouseID,
                            QtyIn=QtyIn,
                            QtyOut=QtyOut,
                            Rate=Rate,
                            PriceListID=PriceListID,
                            IsActive=IsActive,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                        stockPostingInstance.delete()

                        update_stock(CompanyID, BranchID, ProductID)
                        
                # billwise delete 
                if BillWiseMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,InvoiceNo=VoucherNo,TransactionID=SalesReturnMasterID,VoucherType="SR").exists():
                    BillWiseMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,InvoiceNo=VoucherNo,TransactionID=SalesReturnMasterID,VoucherType="SR").delete()

                detail_instances = SalesReturnDetails.objects.filter(
                    CompanyID=CompanyID, SalesReturnMasterID=SalesReturnMasterID
                )

                for detail_instance in detail_instances:

                    SalesReturnDetailsID = detail_instance.SalesReturnDetailsID
                    BranchID = detail_instance.BranchID
                    SalesReturnMasterID = detail_instance.SalesReturnMasterID
                    DeliveryDetailsID = detail_instance.DeliveryDetailsID
                    OrderDetailsID = detail_instance.OrderDetailsID
                    ProductID = detail_instance.ProductID
                    Qty = detail_instance.Qty
                    FreeQty = detail_instance.FreeQty
                    UnitPrice = detail_instance.UnitPrice
                    InclusivePrice = detail_instance.InclusivePrice
                    RateWithTax = detail_instance.RateWithTax
                    CostPerPrice = detail_instance.CostPerPrice
                    PriceListID = detail_instance.PriceListID
                    DiscountPerc = detail_instance.DiscountPerc
                    DiscountAmount = detail_instance.DiscountAmount
                    GrossAmount = detail_instance.GrossAmount
                    TaxableAmount = detail_instance.TaxableAmount
                    VATPerc = detail_instance.VATPerc
                    VATAmount = detail_instance.VATAmount
                    SGSTPerc = detail_instance.SGSTPerc
                    SGSTAmount = detail_instance.SGSTAmount
                    CGSTPerc = detail_instance.CGSTPerc
                    CGSTAmount = detail_instance.CGSTAmount
                    IGSTPerc = detail_instance.IGSTPerc
                    IGSTAmount = detail_instance.IGSTAmount
                    NetAmount = detail_instance.NetAmount
                    Flavour = detail_instance.Flavour
                    CreatedUserID = detail_instance.CreatedUserID
                    UpdatedUserID = detail_instance.UpdatedUserID
                    AddlDiscPercent = detail_instance.AddlDiscPercent
                    AddlDiscAmt = detail_instance.AddlDiscAmt
                    TAX1Perc = detail_instance.TAX1Perc
                    TAX1Amount = detail_instance.TAX1Amount
                    TAX2Perc = detail_instance.TAX2Perc
                    TAX2Amount = detail_instance.TAX2Amount
                    TAX3Perc = detail_instance.TAX3Perc
                    TAX3Amount = detail_instance.TAX3Amount
                    KFCAmount = detail_instance.KFCAmount
                    KFCPerc = detail_instance.KFCPerc
                    ProductTaxID = detail_instance.ProductTaxID

                    update_stock(CompanyID, BranchID, ProductID)

                    BatchCode = detail_instance.BatchCode

                    if Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode
                    ).exists():
                        batch_ins = Batch.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode
                        )
                        MultiFactor = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID
                        ).MultiFactor

                        qty_batch = converted_float(FreeQty) + converted_float(Qty)
                        Qty_batch = converted_float(MultiFactor) * converted_float(qty_batch)
                        StockIn = batch_ins.StockIn
                        batch_ins.StockIn = converted_float(StockIn) - converted_float(Qty_batch)
                        batch_ins.save()

                    SalesReturnDetails_Log.objects.create(
                        TransactionID=SalesReturnDetailsID,
                        BranchID=BranchID,
                        Action=Action,
                        SalesReturnMasterID=SalesReturnMasterID,
                        DeliveryDetailsID=DeliveryDetailsID,
                        OrderDetailsID=OrderDetailsID,
                        ProductID=ProductID,
                        Qty=Qty,
                        FreeQty=FreeQty,
                        UnitPrice=UnitPrice,
                        InclusivePrice=InclusivePrice,
                        RateWithTax=RateWithTax,
                        CostPerPrice=CostPerPrice,
                        PriceListID=PriceListID,
                        DiscountPerc=DiscountPerc,
                        DiscountAmount=DiscountAmount,
                        GrossAmount=GrossAmount,
                        TaxableAmount=TaxableAmount,
                        VATPerc=VATPerc,
                        VATAmount=VATAmount,
                        SGSTPerc=SGSTPerc,
                        SGSTAmount=SGSTAmount,
                        CGSTPerc=CGSTPerc,
                        CGSTAmount=CGSTAmount,
                        IGSTPerc=IGSTPerc,
                        IGSTAmount=IGSTAmount,
                        NetAmount=NetAmount,
                        Flavour=Flavour,
                        CreatedUserID=CreatedUserID,
                        UpdatedUserID=UpdatedUserID,

                        CreatedDate=today,
                        UpdatedDate=today,
                        AddlDiscPercent=AddlDiscPercent,
                        AddlDiscAmt=AddlDiscAmt,
                        TAX1Perc=TAX1Perc,
                        TAX1Amount=TAX1Amount,
                        TAX2Perc=TAX2Perc,
                        TAX2Amount=TAX2Amount,
                        TAX3Perc=TAX3Perc,
                        TAX3Amount=TAX3Amount,
                        CompanyID=CompanyID,
                        BatchCode=BatchCode,
                        KFCAmount=KFCAmount,
                        KFCPerc=KFCPerc,
                        ProductTaxID=ProductTaxID,
                    )

                    # if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=SalesReturnDetailsID,MasterID=SalesReturnMasterID,BranchID=BranchID,VoucherType="SR").exists():
                    #     stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID,DetailID=SalesReturnDetailsID,MasterID=SalesReturnMasterID,BranchID=BranchID,VoucherType="SR")

                    #     stockRateID = stockTrans_instance.StockRateID
                    #     stockTrans_instance.IsActive = False
                    #     stockTrans_instance.save()

                    #     stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,StockRateID=stockRateID,BranchID=BranchID)
                    #     stockRate_instance.Qty = stockTrans_instance.Qty
                    #     stockRate_instance.save()

                    if StockTrans.objects.filter(
                        CompanyID=CompanyID,
                        DetailID=SalesReturnDetailsID,
                        MasterID=SalesReturnMasterID,
                        BranchID=BranchID,
                        VoucherType="SR",
                        IsActive=True,
                    ).exists():
                        stockTrans_instances = StockTrans.objects.filter(
                            CompanyID=CompanyID,
                            DetailID=SalesReturnDetailsID,
                            MasterID=SalesReturnMasterID,
                            BranchID=BranchID,
                            VoucherType="SR",
                            IsActive=True,
                        )

                        for i in stockTrans_instances:
                            stockRateID = i.StockRateID
                            i.IsActive = False
                            i.save()

                            stockRate_instance = StockRate.objects.get(
                                CompanyID=CompanyID,
                                StockRateID=stockRateID,
                                BranchID=BranchID,
                            )
                            stockRate_instance.Qty = converted_float(stockRate_instance.Qty) - converted_float(
                                i.Qty
                            )
                            stockRate_instance.save()

                    detail_instance.delete()
                # =========Loyalty Point ==========
                if LoyaltyPoint.objects.filter(
                    LoyaltyCustomerID=LoyaltyCustomerID,
                    VoucherMasterID=SalesReturnMasterID,
                    VoucherType="SR",
                    BranchID=BranchID,
                    CompanyID=CompanyID,
                ).exists():
                    instances = LoyaltyPoint.objects.filter(
                        LoyaltyCustomerID=LoyaltyCustomerID,
                        VoucherMasterID=SalesReturnMasterID,
                        VoucherType="SR",
                        BranchID=BranchID,
                        CompanyID=CompanyID,
                    ).delete()
                    # for i in instances:
                    #     i.delete()

                # =========Loyalty Point ==========
                instance.delete()
        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Information",
            CreatedUserID,
            "Sales Return",
            "Delete",
            "Sales Return Deleted Successfully.",
            "Sales Return Deleted Successfully.",
        )

        response_data = {
            "StatusCode": 6000,
            "title": "Success",
            "message": "Sales Return Master Deleted Successfully!",
        }
    else:
        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Warning",
            CreatedUserID,
            "Sales Return",
            "Delete",
            "Sales Return Deleted Failed.",
            "Sales Return Master Not Found",
        )

        response_data = {
            "StatusCode": 6001,
            "title": "Failed",
            "message": "Sales Return Master Not Found!",
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def report_salesReturns(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]

    serialized1 = ListSerializerforReport(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data["BranchID"]
        ToDate = serialized1.data["ToDate"]

        if SalesReturnMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, VoucherDate__lte=ToDate
        ).exists():
            instances = SalesReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherDate__lte=ToDate
            )

            serialized = SalesReturnMasterReportSerializer(
                instances, many=True, context={"CompanyID": CompanyID}
            )

            # request , company, log_type, user, source, action, message, description
            activity_log(
                request._request,
                CompanyID,
                "Information",
                CreatedUserID,
                "Sales Return Report",
                "Report",
                "Sales Return Report Viewed Successfully.",
                "Sales Return Report Viewed Successfully.",
            )
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # request , company, log_type, user, source, action, message, description
            activity_log(
                request._request,
                CompanyID,
                "Warning",
                CreatedUserID,
                "Sales Return Report",
                "Report",
                "Sales Return Report Viewed Failed.",
                "No data under this date",
            )
            response_data = {
                "StatusCode": 6001,
                "message": "No data under this date!!!",
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def search_salesReturns(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    product_name = data["product_name"]
    length = data["length"]
    param = data["param"]

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]
        if SalesReturnMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID
        ).exists():
            instances = SalesReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID
            )

            if length < 3:
                if param == "VoucherNo":
                    instances = instances.filter(
                        (Q(VoucherNo__icontains=product_name))
                    )[:10]
                elif param == "VoucherDate":
                    instances = instances.filter(
                        (Q(VoucherDate__icontains=product_name))
                    )[:10]
                elif param == "CustomerName":
                    instances = instances.filter(
                        (Q(CustomerName__icontains=product_name))
                    )[:10]
                else:
                    ledger_ids = []
                    if AccountLedger.objects.filter(
                        CompanyID=CompanyID, LedgerName__icontains=product_name
                    ).exists():
                        ledger_ins = AccountLedger.objects.filter(
                            CompanyID=CompanyID, LedgerName__icontains=product_name
                        )
                        for l in ledger_ins:
                            ledger_ids.append(l.LedgerID)
                    instances = instances.filter((Q(LedgerID__in=ledger_ids)))[:10]
            else:
                if param == "VoucherNo":
                    instances = instances.filter((Q(VoucherNo__icontains=product_name)))
                elif param == "VoucherDate":
                    instances = instances.filter(
                        (Q(VoucherDate__icontains=product_name))
                    )
                elif param == "CustomerName":
                    instances = instances.filter(
                        (Q(CustomerName__icontains=product_name))
                    )
                else:
                    ledger_ids = []
                    if AccountLedger.objects.filter(
                        CompanyID=CompanyID, LedgerName__icontains=product_name
                    ).exists():
                        ledger_ins = AccountLedger.objects.filter(
                            CompanyID=CompanyID, LedgerName__icontains=product_name
                        )
                        for l in ledger_ins:
                            ledger_ids.append(l.LedgerID)
                    instances = instances.filter((Q(LedgerID__in=ledger_ids)))

            serialized = SalesReturnMasterRestSerializer(
                instances,
                many=True,
                context={
                    "request": request,
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "product_name": "product_name",
                },
            )

        response_data = {"StatusCode": 6000, "data": serialized.data}

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def salesReturnRegister_report(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    PriceRounding = data["PriceRounding"]
    ProductFilter = data["ProductFilter"]
    ProductID = data["ProductID"]
    CategoryID = data["CategoryID"]
    GroupID = data["GroupID"]
    WareHouseID = data["WareHouseID"]
    UserID = data["UserID"]
    LedgerID = data["LedgerID"]
    ProductCode = data["ProductCode"]
    BarCode = data["BarCode"]
    serialized1 = ListSerializerforReport(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]
        FromDate = serialized1.data["FromDate"]
        ToDate = serialized1.data["ToDate"]

        produtVal = ProductID
        groupVal = GroupID
        categoryVal = CategoryID
        wareHouseVal = WareHouseID
        userVal = str(UserID)
        branchVal = BranchID
        ledgerVal = LedgerID
        productCodeVal = ProductCode
        barCodeVal = BarCode

        if SalesReturnMaster.objects.filter(
            CompanyID=CompanyID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate
        ).exists():
            saleReturnMaster_instances = SalesReturnMaster.objects.filter(
                CompanyID=CompanyID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate
            )

            if wareHouseVal > 0:
                if saleReturnMaster_instances.filter(WarehouseID=wareHouseVal).exists():
                    saleReturnMaster_instances = saleReturnMaster_instances.filter(
                        WarehouseID=wareHouseVal
                    )
                else:
                    # request , company, log_type, user, source, action, message, description
                    activity_log(
                        request._request,
                        CompanyID,
                        "Warning",
                        CreatedUserID,
                        "SalesReturn Register Report",
                        "Report",
                        "SalesReturn Register Report Viewed Failed.",
                        "SalesReturn is not Found in this Warehouse",
                    )
                    response_data = {
                        "StatusCode": 6001,
                        "message": "SalesReturn is not Found in this Warehouse!",
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
            if userVal > "0":
                UserID = UserTable.objects.get(pk=userVal,Active=True).customer.user.id
                if saleReturnMaster_instances.filter(CreatedUserID=UserID).exists():
                    saleReturnMaster_instances = saleReturnMaster_instances.filter(
                        CreatedUserID=UserID
                    )
                else:
                    # request , company, log_type, user, source, action, message, description
                    activity_log(
                        request._request,
                        CompanyID,
                        "Warning",
                        CreatedUserID,
                        "SalesReturn Register Report",
                        "Report",
                        "SalesReturn Register Report Viewed Failed.",
                        "SalesReturn is not Found by this user",
                    )
                    response_data = {
                        "StatusCode": 6001,
                        "message": "SalesReturn is not Found by this user!",
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
            if branchVal > 0:
                if saleReturnMaster_instances.filter(BranchID=branchVal).exists():
                    saleReturnMaster_instances = saleReturnMaster_instances.filter(
                        BranchID=branchVal
                    )
                else:
                    # request , company, log_type, user, source, action, message, description
                    activity_log(
                        request._request,
                        CompanyID,
                        "Warning",
                        CreatedUserID,
                        "SalesReturn Register Report",
                        "Report",
                        "SalesReturn Register Report Viewed Failed.",
                        "SalesReturn is not Found under this Branch",
                    )
                    response_data = {
                        "StatusCode": 6001,
                        "message": "SalesReturn is not Found under this Branch!",
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
            if ledgerVal > 0:
                if saleReturnMaster_instances.filter(LedgerID=ledgerVal).exists():
                    saleReturnMaster_instances = saleReturnMaster_instances.filter(
                        LedgerID=ledgerVal
                    )
                else:
                    # request , company, log_type, user, source, action, message, description
                    activity_log(
                        request._request,
                        CompanyID,
                        "Warning",
                        CreatedUserID,
                        "SalesReturn Register Report",
                        "Report",
                        "SalesReturn Register Report Viewed Failed.",
                        "SalesReturn is not Found under this Ledger",
                    )
                    response_data = {
                        "StatusCode": 6001,
                        "message": "SalesReturn is not Found under this Ledger!",
                    }

                    return Response(response_data, status=status.HTTP_200_OK)

            masterList = []
            final_array = []
            for i in saleReturnMaster_instances:
                SalesReturnMasterID = i.SalesReturnMasterID
                BranchID = i.BranchID
                Date = i.VoucherDate
                InvoiceNo = i.VoucherNo

                SalesReturnDetail_instances = SalesReturnDetails.objects.filter(
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    SalesReturnMasterID=SalesReturnMasterID,
                )
                if produtVal > 0:
                    SalesReturnDetail_instances = SalesReturnDetail_instances.filter(
                        ProductID=produtVal
                    )
                elif categoryVal > 0:
                    if ProductGroup.objects.filter(
                        CategoryID=categoryVal, CompanyID=CompanyID, BranchID=BranchID
                    ).exists():
                        group_instances = ProductGroup.objects.filter(
                            CategoryID=categoryVal,
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                        )
                        for group_i in group_instances:
                            ProductGroupID = group_i.ProductGroupID
                            if Product.objects.filter(
                                CompanyID=CompanyID,
                                BranchID=BranchID,
                                ProductGroupID=ProductGroupID,
                            ).exists():
                                product_instances = Product.objects.filter(
                                    CompanyID=CompanyID,
                                    BranchID=BranchID,
                                    ProductGroupID=ProductGroupID,
                                )
                                pro_ids = []
                                for product_i in product_instances:
                                    ProductID = product_i.ProductID
                                    pro_ids.append(ProductID)
                                SalesReturnDetail_instances = (
                                    SalesReturnDetail_instances.filter(
                                        ProductID__in=pro_ids
                                    )
                                )
                    else:
                        # request , company, log_type, user, source, action, message, description
                        activity_log(
                            request._request,
                            CompanyID,
                            "Warning",
                            CreatedUserID,
                            "SalesReturn Register Report",
                            "Report",
                            "SalesReturn Register Report Viewed Failed.",
                            "SalesReturn is not Found under this Category",
                        )
                        response_data = {
                            "StatusCode": 6001,
                            "message": "SalesReturn is not Found under this Category!",
                        }

                        return Response(response_data, status=status.HTTP_200_OK)

                elif groupVal > 0:
                    if Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=groupVal
                    ).exists():
                        product_instances = Product.objects.filter(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            ProductGroupID=groupVal,
                        )
                        pro_ids = []
                        for product_i in product_instances:
                            ProductID = product_i.ProductID
                            pro_ids.append(ProductID)
                        SalesReturnDetail_instances = (
                            SalesReturnDetail_instances.filter(ProductID__in=pro_ids)
                        )
                    else:
                        # request , company, log_type, user, source, action, message, description
                        activity_log(
                            request._request,
                            CompanyID,
                            "Warning",
                            CreatedUserID,
                            "SalesReturn Register Report",
                            "Report",
                            "SalesReturn Register Report Viewed Failed.",
                            "SalesReturn is not Found under this Group",
                        )
                        response_data = {
                            "StatusCode": 6001,
                            "message": "SalesReturn is not Found under this Group!",
                        }

                        return Response(response_data, status=status.HTTP_200_OK)

                elif productCodeVal:
                    if Product.objects.filter(
                        CompanyID=CompanyID,
                        BranchID=BranchID,
                        ProductCode=productCodeVal,
                    ).exists():
                        product_instances = Product.objects.filter(
                            CompanyID=CompanyID,
                            BranchID=BranchID,
                            ProductCode=productCodeVal,
                        )
                        pro_ids = []
                        for product_i in product_instances:
                            ProductID = product_i.ProductID
                            pro_ids.append(ProductID)
                        SalesReturnDetail_instances = (
                            SalesReturnDetail_instances.filter(ProductID__in=pro_ids)
                        )
                    else:
                        # request , company, log_type, user, source, action, message, description
                        activity_log(
                            request._request,
                            CompanyID,
                            "Warning",
                            CreatedUserID,
                            "SalesReturn Register Report",
                            "Report",
                            "SalesReturn Register Report Viewed Failed.",
                            "SalesReturn is not Found under this ProductCode",
                        )
                        response_data = {
                            "StatusCode": 6001,
                            "message": "SalesReturn is not Found under this ProductCode!",
                        }

                        return Response(response_data, status=status.HTTP_200_OK)

                elif barCodeVal:
                    if PriceList.objects.filter(
                        Barcode=barCodeVal, CompanyID=CompanyID, BranchID=BranchID
                    ).exists():
                        ProductID = (
                            PriceList.objects.filter(
                                Barcode=barCodeVal,
                                CompanyID=CompanyID,
                                BranchID=BranchID,
                            )
                            .first()
                            .ProductID
                        )
                        SalesReturnDetail_instances = (
                            SalesReturnDetail_instances.filter(ProductID=ProductID)
                        )
                    else:
                        # request , company, log_type, user, source, action, message, description
                        activity_log(
                            request._request,
                            CompanyID,
                            "Warning",
                            CreatedUserID,
                            "SalesReturn Register Report",
                            "Report",
                            "SalesReturn Register Report Viewed Failed.",
                            "SalesReturn is not Found under this Bracode",
                        )
                        response_data = {
                            "StatusCode": 6001,
                            "message": "SalesReturn is not Found under this Bracode!",
                        }

                        return Response(response_data, status=status.HTTP_200_OK)

                for s in SalesReturnDetail_instances:
                    if s.SalesReturnMasterID == SalesReturnMasterID:
                        if not SalesReturnMasterID in masterList:
                            myDict = {
                                "id": i.id,
                                "Date": Date,
                                "InvoiceNo": InvoiceNo,
                                "ProductCode": "",
                                "ProductName": "",
                                "ProductGroup": "",
                                "Barcode": "",
                                "Qty": "",
                                "SalesPrice": "",
                                "GrossAmount": 0,
                                "VATAmount": 0,
                                "NetAmount": 0,
                                "Cost": 0,
                                "Profit": 0,
                            }
                            if (
                                s.InclusivePrice == 0
                                and s.GrossAmount == 0
                                and s.VATAmount == 0
                                and s.NetAmount == 0
                                and s.CostPerPrice == 0
                            ):
                                print("IF CONDI@@@@@@@@@@TION")
                            else:
                                final_array.append(myDict)
                            masterList.append(SalesReturnMasterID)
                    ProductID = s.ProductID
                    PriceListID = s.PriceListID
                    BranchID = s.BranchID
                    product_instance = Product.objects.get(
                        ProductID=ProductID, BranchID=BranchID, CompanyID=CompanyID
                    )
                    ProductCode = product_instance.ProductCode
                    ProductName = product_instance.ProductName
                    ProductGroupID = product_instance.ProductGroupID
                    ProductGroupName = ProductGroup.objects.get(
                        ProductGroupID=ProductGroupID,
                        BranchID=BranchID,
                        CompanyID=CompanyID,
                    ).GroupName
                    Barcode = PriceList.objects.get(
                        PriceListID=PriceListID, BranchID=BranchID, CompanyID=CompanyID
                    ).Barcode
                    Qty = s.Qty
                    SalesReturnPrice = s.InclusivePrice
                    GrossAmount = s.GrossAmount
                    VATAmount = s.VATAmount
                    NetAmount = s.NetAmount
                    Cost = s.CostPerPrice
                    Profit = converted_float(NetAmount) - (converted_float(Qty) * converted_float(Cost))
                    print("===========================")
                    print(SalesReturnPrice)
                    if SalesReturnMasterID in masterList:
                        myDict = {
                            "id": i.id,
                            "Date": "-",
                            "InvoiceNo": "-",
                            "ProductCode": ProductCode,
                            "ProductName": ProductName,
                            "ProductGroup": ProductGroupName,
                            "Barcode": Barcode,
                            "Qty": Qty,
                            "SalesPrice": round(SalesReturnPrice, PriceRounding),
                            "GrossAmount": round(GrossAmount, PriceRounding),
                            "VATAmount": round(VATAmount, PriceRounding),
                            "NetAmount": round(NetAmount, PriceRounding),
                            "Cost": round(Cost, PriceRounding),
                            "Profit": round(Profit, PriceRounding),
                        }

                    if (
                        SalesReturnPrice == 0
                        and GrossAmount == 0
                        and VATAmount == 0
                        and NetAmount == 0
                        and Cost == 0
                        and Profit == 0
                    ):
                        print("IF CONDITION")
                    else:
                        print("ELSE CONDITION")
                        final_array.append(myDict)

            TotalProfit = 0
            TotalCost = 0
            TotalNetAmt = 0
            TotalVatAmt = 0
            TotalGrossAmt = 0

            for f in final_array:
                TotalProfit += f["Profit"]
                TotalCost += f["Cost"]
                TotalNetAmt += f["NetAmount"]
                TotalVatAmt += f["VATAmount"]
                TotalGrossAmt += f["GrossAmount"]

            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'SalesReturn Register Report',
            #              'Report', 'SalesReturn Register Report Viewed Successfully.', 'SalesReturn Register Report Viewed Successfully.')

            response_data = {
                "StatusCode": 6000,
                "data": final_array,
                "TotalProfit": TotalProfit,
                "TotalCost": TotalCost,
                "TotalNetAmt": TotalNetAmt,
                "TotalVatAmt": TotalVatAmt,
                "TotalGrossAmt": TotalGrossAmt,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'SalesReturn Register Report',
            #              'Report', 'SalesReturn Register Report Viewed Failed.', 'No data During This Time Periods')
            response_data = {
                "StatusCode": 6001,
                "message": "No data During This Time Periods!!!",
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {"StatusCode": 6001, "message": "please provide valid datas!!!"}

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def search_salesReturn_list(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    product_name = data["product_name"]
    length = data["length"]

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]
        if SalesReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            ledger_ids = []
            if AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerName__icontains=product_name
            ).exists():
                ledgrs = AccountLedger.objects.filter(
                    CompanyID=CompanyID, LedgerName__icontains=product_name
                )
                ledger_ids = ledgrs.values_list("LedgerID", flat=True)
            if length < 3:
                instances = SalesReturnMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID
                )
                instances = instances.filter(
                    (Q(VoucherNo__icontains=product_name))
                    | (Q(VoucherDate__icontains=product_name))
                    | (Q(CustomerName__icontains=product_name))
                    | (Q(LedgerID__in=ledger_ids))
                )[:10]
            else:
                instances = SalesReturnMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID
                )
                instances = instances.filter(
                    (Q(VoucherNo__icontains=product_name))
                    | (Q(VoucherDate__icontains=product_name))
                    | (Q(CustomerName__icontains=product_name))
                )
            serialized = SalesReturnMaster1RestSerializer(
                instances,
                many=True,
                context={
                    "request": request,
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                },
            )

        response_data = {"StatusCode": 6000, "data": serialized.data}

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch You Enterd is not Valid!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)



@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def salesReturnRegister_report_qry(request):
    data = request.data
    CompanyIDuid = data["CompanyID"]
    CompanyID = get_company(CompanyIDuid)
    PriceRounding = data["PriceRounding"]
    ProductID = data["ProductID"]
    CategoryID = data["CategoryID"]
    GroupID = data["GroupID"]
    WareHouseID = data["WarehouseID"]
    UserID = data["UserID"]
    LedgerID = data["LedgerID"]
    ProductCode = data["ProductCode"]
    Barcode = data["Barcode"]
    serialized1 = ListSerializerforReport(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]
        FromDate = serialized1.data["FromDate"]
        ToDate = serialized1.data["ToDate"]

        if SalesReturnMaster.objects.filter(
            CompanyID=CompanyID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate
        ).exists():
            warehouse_list = []
            user_list = []
            ledger_list = []
            BranchList = [1]
            if Branch.objects.filter(CompanyID=CompanyID).exists():
                BranchList = Branch.objects.filter(CompanyID=CompanyID).values_list('BranchID',flat=True)
            if AccountLedger.objects.filter(CompanyID=CompanyID).exists():
                ledger_list = AccountLedger.objects.filter(CompanyID=CompanyID).values_list('LedgerID',flat=True)
            if Warehouse.objects.filter(CompanyID=CompanyID).exists():
                warehouse_list = Warehouse.objects.filter(CompanyID=CompanyID).values_list('WarehouseID',flat=True)
            if UserTable.objects.filter(CompanyID=CompanyID, Active=True).exists():
                user_list = UserTable.objects.filter(CompanyID=CompanyID,Active=True).values_list('customer_id',flat=True)
                user_list = Customer.objects.filter(id__in=user_list).values_list('user_id',flat=True)
                
            if int(BranchID) > 0:
                BranchList = []
                BranchList.append(int(BranchID))
            if int(LedgerID) > 0:
                ledger_list = []
                ledger_list.append(int(LedgerID))
            if int(WareHouseID) > 0:
                warehouse_list = []
                warehouse_list.append(int(WareHouseID))
            if int(UserID) > 0:
                user_list = []
                user_list.append(int(UserID))
            
            df,details = salesReturn_register_report_data(CompanyIDuid,BranchList,FromDate,ToDate,warehouse_list,user_list,ledger_list,ProductID,GroupID,CategoryID,ProductCode,Barcode)
            response_data = {
                "StatusCode": 6000,
                "data": details
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'sales Register Report',
            #              'Report', 'Sales Register Report Viewed Failed.', 'No data During This Time Periods')
            response_data = {
                "StatusCode": 6001,
                "message": "No data During This Time Periods!!!",
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {"StatusCode": 6001, "message": "please provide valid datas!!!"}

        return Response(response_data, status=status.HTTP_200_OK)