from datetime import date
from brands.models import SalesMaster, SalesMaster_Log, SalesDetails, SalesDetails_Log, StockPosting, LedgerPosting,\
    StockPosting_Log, LedgerPosting_Log, Parties, SalesDetailsDummy, StockRate, StockTrans, PriceList, DamageStockMaster, JournalMaster,\
    OpeningStockMaster, PaymentMaster, PurchaseMaster, PurchaseOrderMaster, PurchaseReturnMaster, ReceiptMaster, SalesOrderMaster, SalesEstimateMaster,\
    SalesReturnMaster, StockReceiptMaster_ID, DamageStockMaster, StockTransferMaster_ID, AccountGroup, SalesReturnDetails,\
    AccountLedger, PurchaseDetails, PurchaseReturnDetails, Product, UserTable, ProductGroup, ExcessStockMaster, ShortageStockMaster, DamageStockMaster,\
    UsedStockMaster, GeneralSettings, CompanySettings, WorkOrderMaster, Batch, SerialNumbers, LoyaltyCustomer, LoyaltyProgram, LoyaltyPoint, LoyaltyPoint_Log,\
    SalesOrderDetails, AccountLedger_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v5.sales.serializers import SalesEstimateForOrderSerializer, SalesMasterSerializer, SalesMasterRestSerializer, SalesMasterRest1Serializer, SalesDetailsSerializer,\
    SalesDetailsRestSerializer, BatchSerializer, ListSerializerforReport, SalesMasterReportSerializer, SalesMasterForReturnSerializer, StockSerializer, StockRateSerializer, SalesIntegratedSerializer,\
    SalesSummaryReportSerializer, SupplierVsProductReportSerializer, SalesGSTReportSerializer, ProductVsSuppliersReportSerializer, FilterOrderSerializer,BillWiseSerializer
from api.v5.brands.serializers import ListSerializer
from api.v5.salesOrders.serializers import SalesOrderDetailsRestSerializer
from api.v5.purchases.serializers import PurchaseMasterRestSerializer, PurchasePrintSerializer
from api.v5.salesReturns.serializers import SalesReturnMasterRestSerializer, SalesReturnMasterReportSerializer
from api.v5.purchaseReturns.serializers import PurchaseReturnMasterRestSerializer, PurchaseReturnPrintSerializer
from api.v5.sales.functions import set_LoyaltyCalculation, get_Program, edit_LoyaltyCalculation, generate_serializer_errors, get_month, get_stock_value
from rest_framework import status
from api.v5.sales.functions import get_auto_id, get_auto_idMaster, get_auto_stockPostid, get_date_list
from api.v5.accountLedgers.functions import get_auto_LedgerPostid
from api.v5.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
import datetime
from datetime import date, timedelta
import re
import sys
import os
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from api.v5.ledgerPosting.functions import convertOrderdDict
from main.functions import get_company, activity_log
from api.v5.stockPostings.serializers import StockPostingSerializer, StockPostingRestSerializer, ExcessStockMasterSerializer, ShortageStockMasterSerializer, DamageStockMasterSerializer, UsedStockMasterSerializer, UsedStockDetailSerializer
from api.v5.companySettings.serializers import CompanySettingsRestSerializer
from api.v5.products.functions import get_auto_AutoBatchCode
from django.db.models import Max
from api.v5.salesOrders.serializers import SalesOrderMasterRestSerializer
from api.v5.purchaseOrders.serializers import PurchaseOrderPrintSerializer
from api.v5.sales.functions import get_Genrate_VoucherNo
from django.db.models import Q, Prefetch, Sum
from api.v5.loyaltyProgram.functions import get_point_auto_id
from django.db import transaction, IntegrityError
from api.v5.accountLedgers.functions import get_LedgerCode, get_auto_id as generated_ledgerID
import math


def call_paginator_all(model_object, page_number, items_per_page):
    paginator = Paginator(model_object, items_per_page)
    content = paginator.page(page_number)
    return content


def list_pagination(list_value, items_per_page, page_no):
    paginator_object = Paginator(list_value, items_per_page)
    get_value = paginator_object.page(page_no).object_list
    return get_value


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def create_sale(request):
    try:
        with transaction.atomic():
            data = request.data

            PriceRounding = data['PriceRounding']

            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            CreatedUserID = data['CreatedUserID']

            today = datetime.datetime.now()
            BranchID = data['BranchID']

            VoucherNo = data['VoucherNo']
            Date = data['Date']
            CreditPeriod = data['CreditPeriod']
            LedgerID = data['LedgerID']
            PriceCategoryID = data['PriceCategoryID']
            EmployeeID = data['EmployeeID']
            SalesAccount = data['SalesAccount']
            CustomerName = data['CustomerName']
            Address1 = data['Address1']
            Address2 = data['Address2']
            Address3 = data['Address3']
            Notes = data['Notes']
            TransactionTypeID = data['TransactionTypeID']
            WarehouseID = data['WarehouseID']
            IsActive = data['IsActive']
            TaxID = data['TaxID']
            TaxType = data['TaxType']
            FinacialYearID = data['FinacialYearID']

            TotalGrossAmt = float(data['TotalGrossAmt'])
            TotalTax = float(data['TotalTax'])
            NetTotal = float(data['NetTotal'])
            AddlDiscAmt = float(data['AddlDiscAmt'])
            AdditionalCost = float(data['AdditionalCost'])
            TotalDiscount = float(data['TotalDiscount'])
            RoundOff = float(data['RoundOff'])
            AddlDiscPercent = float(data['AddlDiscPercent'])
            GrandTotal = float(data['GrandTotal'])

            VATAmount = float(data['VATAmount'])
            SGSTAmount = float(data['SGSTAmount'])
            CGSTAmount = float(data['CGSTAmount'])
            IGSTAmount = float(data['IGSTAmount'])
            TAX1Amount = float(data['TAX1Amount'])
            TAX2Amount = float(data['TAX2Amount'])
            TAX3Amount = float(data['TAX3Amount'])
            KFCAmount = float(data['KFCAmount'])
            BillDiscPercent = float(data['BillDiscPercent'])
            BankAmount = float(data['BankAmount'])
            BillDiscAmt = float(data['BillDiscAmt'])
            Balance = float(data['Balance'])
            OldLedgerBalance = float(data['OldLedgerBalance'])

            # TotalGrossAmt = round(TotalGrossAmt, PriceRounding)
            # TotalTax = round(TotalTax, PriceRounding)
            # NetTotal = round(NetTotal, PriceRounding)
            # AddlDiscPercent = round(AddlDiscPercent, PriceRounding)
            # AddlDiscAmt = round(AddlDiscAmt, PriceRounding)
            # AdditionalCost = round(AdditionalCost, PriceRounding)
            # TotalDiscount = round(TotalDiscount, PriceRounding)
            # GrandTotal = round(GrandTotal, PriceRounding)
            # RoundOff = round(RoundOff, PriceRounding)

            # VATAmount = round(VATAmount, PriceRounding)
            # SGSTAmount = round(SGSTAmount, PriceRounding)
            # CGSTAmount = round(CGSTAmount, PriceRounding)
            # IGSTAmount = round(IGSTAmount, PriceRounding)
            # TAX1Amount = round(TAX1Amount, PriceRounding)
            # TAX2Amount = round(TAX2Amount, PriceRounding)
            # TAX3Amount = round(TAX3Amount, PriceRounding)
            # KFCAmount = round(KFCAmount, PriceRounding)
            # BillDiscPercent = round(BillDiscPercent, PriceRounding)
            # BankAmount = round(BankAmount, PriceRounding)
            # BillDiscAmt = round(BillDiscAmt, PriceRounding)
            # Balance = round(Balance, PriceRounding)
            # OldLedgerBalance = round(OldLedgerBalance, PriceRounding)

            BatchID = data['BatchID']
            CashReceived = data['CashReceived']
            # CashAmount = data['CashAmount']
            TableID = data['TableID']
            SeatNumber = data['SeatNumber']
            NoOfGuests = data['NoOfGuests']
            INOUT = data['INOUT']
            TokenNumber = data['TokenNumber']
            CardTypeID = data['CardTypeID']
            CardNumber = data['CardNumber']
            IsPosted = data['IsPosted']
            SalesType = data['SalesType']

            try:
                OrderNo = data['OrderNo']
            except:
                OrderNo = "SO0"

            try:
                order_vouchers = data['order_vouchers']
            except:
                order_vouchers = []
            # =========
            details = data["SalesDetails"]
            TotalTaxableAmount = 0
            for i in details:
                TotalTaxableAmount += float(i['TaxableAmount'])
            # =========

            print("--------------------------------,")
            print(OrderNo)
            print(order_vouchers)
            Cash_Account = None
            Bank_Account = None

            if UserTable.objects.filter(CompanyID=CompanyID, customer__user__pk=CreatedUserID).exists():
                Cash_Account = UserTable.objects.get(
                    CompanyID=CompanyID, customer__user__pk=CreatedUserID).Cash_Account
                Bank_Account = UserTable.objects.get(
                    CompanyID=CompanyID, customer__user__pk=CreatedUserID).Bank_Account

            try:
                CashID = data['CashID']
            except:
                CashID = Cash_Account

            try:
                BankID = data['BankID']
            except:
                BankID = Bank_Account

            try:
                ShippingCharge = data['ShippingCharge']
            except:
                ShippingCharge = 0

            try:
                shipping_tax_amount = data['shipping_tax_amount']
            except:
                shipping_tax_amount = 0

            try:
                TaxTypeID = data['TaxTypeID']
            except:
                TaxTypeID = ""

            try:
                SAC = data['SAC']
            except:
                SAC = ""

            try:
                SalesTax = data['SalesTax']
            except:
                SalesTax = 0

            VoucherType = "SI"

            if SalesOrderMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherNo=OrderNo, IsInvoiced="N").exists():
                order_instance = SalesOrderMaster.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, VoucherNo=OrderNo, IsInvoiced="N")
                order_instance.IsInvoiced = "I"
                order_instance.save()
            else:
                if order_vouchers:
                    order_instances = SalesOrderMaster.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, VoucherNo__in=order_vouchers, IsInvoiced="N")
                    for b in order_instances:
                        b.IsInvoiced = "I"
                        b.save()

            Action = "A"

            def max_id():
                general_settings_id = GeneralSettings.objects.filter(
                    CompanyID=CompanyID).aggregate(Max('GeneralSettingsID'))
                general_settings_id = general_settings_id.get(
                    'GeneralSettingsID__max', 0)
                general_settings_id += 1
                return general_settings_id

            try:
                ShowTotalTax = data['ShowTotalTax']
                is_except = False
            except:
                ShowTotalTax = False
                is_except = True

            if is_except == False:
                if not GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowTotalTax").exists():
                    GeneralSettings.objects.create(
                        CompanyID=CompanyID,
                        GeneralSettingsID=max_id(),
                        SettingsType="ShowTotalTax",
                        SettingsValue=ShowTotalTax,
                        BranchID=1, GroupName="Inventory",
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        Action=Action
                    )
                else:
                    GeneralSettings.objects.filter(
                        CompanyID=CompanyID,
                        SettingsType="ShowTotalTax"
                    ).update(
                        SettingsValue=ShowTotalTax,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        Action=Action
                    )

            AllowCashReceiptMoreSaleAmt = data['AllowCashReceiptMoreSaleAmt']

            # checking voucher number already exist
            VoucherNoLow = VoucherNo.lower()
            is_voucherExist = False
            insts = SalesMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True

            check_VoucherNoAutoGenerate = False
            is_SaleOK = True

            if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="VoucherNoAutoGenerate").exists():
                check_VoucherNoAutoGenerate = GeneralSettings.objects.get(
                    CompanyID=CompanyID, SettingsType="VoucherNoAutoGenerate").SettingsValue

            if is_voucherExist == True and check_VoucherNoAutoGenerate == "True":
                VoucherNo = get_Genrate_VoucherNo(
                    SalesMaster, BranchID, CompanyID, "SI")
                is_SaleOK = True
            elif is_voucherExist == False:
                is_SaleOK = True
            else:
                is_SaleOK = False

            if is_SaleOK:

                SalesMasterID = get_auto_idMaster(
                    SalesMaster, BranchID, CompanyID)

                if Parties.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID).exists():

                    party_instances = Parties.objects.filter(
                        CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)

                    for party_instance in party_instances:

                        party_instance.PartyName = CustomerName

                        party_instance.save()

                if AllowCashReceiptMoreSaleAmt == True or AllowCashReceiptMoreSaleAmt == "true":
                    CashAmount = CashReceived
                elif float(Balance) < 0:
                    CashAmount = float(GrandTotal) - float(BankAmount)
                else:
                    CashAmount = CashReceived

                # Loyalty Customer instance
                LoyaltyCustomerID = data['LoyaltyCustomerID']

                loyalty_customer = None
                is_LoyaltyCustomer = False
                if LoyaltyCustomerID:
                    if LoyaltyCustomer.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LoyaltyCustomerID=LoyaltyCustomerID).exists():
                        loyalty_customer = LoyaltyCustomer.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, LoyaltyCustomerID=LoyaltyCustomerID)
                        is_LoyaltyCustomer = True
                SalesMaster_Log.objects.create(
                    LoyaltyCustomerID=loyalty_customer,
                    TotalTaxableAmount=TotalTaxableAmount,
                    TransactionID=SalesMasterID,
                    BranchID=BranchID,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    CreditPeriod=CreditPeriod,
                    LedgerID=LedgerID,
                    PriceCategoryID=PriceCategoryID,
                    EmployeeID=EmployeeID,
                    SalesAccount=SalesAccount,
                    CustomerName=CustomerName,
                    Address1=Address1,
                    Address2=Address2,
                    Address3=Address3,
                    Notes=Notes,
                    FinacialYearID=FinacialYearID,
                    TotalGrossAmt=TotalGrossAmt,
                    AddlDiscPercent=AddlDiscPercent,
                    AddlDiscAmt=AddlDiscAmt,
                    TotalDiscount=TotalDiscount,
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
                    CardTypeID=CardTypeID,
                    CardNumber=CardNumber,
                    IsActive=IsActive,
                    IsPosted=IsPosted,
                    SalesType=SalesType,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    # TaxID=TaxID,
                    # TaxType=TaxType,
                    BillDiscPercent=BillDiscPercent,
                    BillDiscAmt=BillDiscAmt,
                    VATAmount=VATAmount,
                    SGSTAmount=SGSTAmount,
                    CGSTAmount=CGSTAmount,
                    IGSTAmount=IGSTAmount,
                    TAX1Amount=TAX1Amount,
                    TAX2Amount=TAX2Amount,
                    TAX3Amount=TAX3Amount,
                    KFCAmount=KFCAmount,
                    Balance=Balance,
                    TransactionTypeID=TransactionTypeID,
                    CompanyID=CompanyID,
                    OldLedgerBalance=OldLedgerBalance,
                    BankID=BankID,
                    CashID=CashID,
                    ShippingCharge=ShippingCharge,
                    shipping_tax_amount=shipping_tax_amount,
                    TaxTypeID=TaxTypeID,
                    SAC=SAC,
                    SalesTax=SalesTax,
                )

                sales_instance = SalesMaster.objects.create(
                    LoyaltyCustomerID=loyalty_customer,
                    TotalTaxableAmount=TotalTaxableAmount,
                    SalesMasterID=SalesMasterID,
                    BranchID=BranchID,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    CreditPeriod=CreditPeriod,
                    LedgerID=LedgerID,
                    PriceCategoryID=PriceCategoryID,
                    EmployeeID=EmployeeID,
                    SalesAccount=SalesAccount,
                    CustomerName=CustomerName,
                    Address1=Address1,
                    Address2=Address2,
                    Address3=Address3,
                    Notes=Notes,
                    FinacialYearID=FinacialYearID,
                    TotalGrossAmt=TotalGrossAmt,
                    AddlDiscPercent=AddlDiscPercent,
                    AddlDiscAmt=AddlDiscAmt,
                    TotalDiscount=TotalDiscount,
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
                    CardTypeID=CardTypeID,
                    CardNumber=CardNumber,
                    IsActive=IsActive,
                    IsPosted=IsPosted,
                    SalesType=SalesType,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    TaxID=TaxID,
                    TaxType=TaxType,
                    BillDiscPercent=BillDiscPercent,
                    BillDiscAmt=BillDiscAmt,
                    VATAmount=VATAmount,
                    SGSTAmount=SGSTAmount,
                    CGSTAmount=CGSTAmount,
                    IGSTAmount=IGSTAmount,
                    TAX1Amount=TAX1Amount,
                    TAX2Amount=TAX2Amount,
                    TAX3Amount=TAX3Amount,
                    KFCAmount=KFCAmount,
                    Balance=Balance,
                    TransactionTypeID=TransactionTypeID,
                    CompanyID=CompanyID,
                    OldLedgerBalance=OldLedgerBalance,
                    BankID=BankID,
                    CashID=CashID,
                    ShippingCharge=ShippingCharge,
                    shipping_tax_amount=shipping_tax_amount,
                    TaxTypeID=TaxTypeID,
                    SAC=SAC,
                    SalesTax=SalesTax,
                )
                details = data["SalesDetails"]

                if is_LoyaltyCustomer:
                    Loyalty_Point_Expire = data['Loyalty_Point_Expire']
                    try:
                        RadeemPoint = data['RadeemPoint']
                    except:
                        RadeemPoint = None
                    # set_LoyaltyCalculation(sales_instance, loyalty_customer,
                    #                        details, Loyalty_Point_Expire, Action, RadeemPoint)
                    set_LoyaltyCalculation(
                        sales_instance, loyalty_customer, details, Loyalty_Point_Expire, Action, RadeemPoint)
                    # ===========================

                account_group = AccountLedger.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).AccountGroupUnder

                # new posting starting from here
                if float(shipping_tax_amount) > 0:
                    if AccountLedger.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerName="Shipping Charges").exists():
                        RelativeLedgerID = AccountLedger.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, LedgerName="Shipping Charges").LedgerID
                    else:
                        RelativeLedgerID = generated_ledgerID(
                            AccountLedger, BranchID, CompanyID)
                        ShippingChargeLedgerCode = get_LedgerCode(
                            AccountLedger, BranchID, CompanyID)

                        AccountLedger.objects.create(
                            LedgerID=RelativeLedgerID,
                            BranchID=BranchID,
                            LedgerName="Shipping Charges",
                            LedgerCode=ShippingChargeLedgerCode,
                            AccountGroupUnder=71,
                            OpeningBalance=0,
                            CrOrDr="Dr",
                            Notes=Notes,
                            IsActive=True,
                            IsDefault=True,
                            CreatedDate=today,
                            UpdatedDate=today,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                        AccountLedger_Log.objects.create(
                            BranchID=BranchID,
                            TransactionID=RelativeLedgerID,
                            LedgerName="Shipping Charges",
                            LedgerCode=ShippingChargeLedgerCode,
                            AccountGroupUnder=71,
                            OpeningBalance=0,
                            CrOrDr="Dr",
                            Notes=Notes,
                            IsActive=True,
                            IsDefault=True,
                            CreatedDate=today,
                            UpdatedDate=today,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=RelativeLedgerID,
                        Debit=shipping_tax_amount,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=RelativeLedgerID,
                        Debit=shipping_tax_amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=RelativeLedgerID,
                        RelatedLedgerID=SalesAccount,
                        Credit=shipping_tax_amount,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=RelativeLedgerID,
                        RelatedLedgerID=SalesAccount,
                        Credit=shipping_tax_amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                if TaxType == 'VAT':
                    if float(VATAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=55,
                            RelatedLedgerID=SalesAccount,
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
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=55,
                            RelatedLedgerID=SalesAccount,
                            Credit=VATAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=55,
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
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=55,
                            Debit=VATAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                elif TaxType == 'GST Intra-state B2B' or TaxType == 'GST Intra-state B2C':
                    if float(CGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=3,
                            RelatedLedgerID=SalesAccount,
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
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=3,
                            RelatedLedgerID=SalesAccount,
                            Credit=CGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=3,
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
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=3,
                            Debit=CGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                    if float(SGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=10,
                            RelatedLedgerID=SalesAccount,
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
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=10,
                            RelatedLedgerID=SalesAccount,
                            Credit=SGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=10,
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
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=10,
                            Debit=SGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                    if float(KFCAmount) > 0:

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=93,
                            RelatedLedgerID=SalesAccount,
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
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=93,
                            RelatedLedgerID=SalesAccount,
                            Credit=KFCAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=93,
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
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=93,
                            Debit=KFCAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                elif TaxType == 'GST Inter-state B2B' or TaxType == 'GST Inter-state B2C':
                    if float(IGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=7,
                            RelatedLedgerID=SalesAccount,
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
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=7,
                            RelatedLedgerID=SalesAccount,
                            Credit=IGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=7,
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
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=7,
                            Debit=IGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                if not TaxType == 'Export':
                    if float(TAX1Amount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=16,
                            RelatedLedgerID=SalesAccount,
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
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=16,
                            RelatedLedgerID=SalesAccount,
                            Credit=TAX1Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=16,
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
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=16,
                            Debit=TAX1Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                    if float(TAX2Amount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=19,
                            RelatedLedgerID=SalesAccount,
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
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=19,
                            RelatedLedgerID=SalesAccount,
                            Credit=TAX2Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=19,
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
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=19,
                            Debit=TAX2Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                    if float(TAX3Amount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=22,
                            RelatedLedgerID=SalesAccount,
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
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=22,
                            RelatedLedgerID=SalesAccount,
                            Credit=TAX3Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=22,
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
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=22,
                            Debit=TAX3Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                if float(RoundOff) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
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

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
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

                if float(RoundOff) < 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    RoundOff = abs(float(RoundOff))

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
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

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
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

                if float(TotalDiscount) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=74,
                        RelatedLedgerID=SalesAccount,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=74,
                        RelatedLedgerID=SalesAccount,
                        Debit=TotalDiscount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=74,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=74,
                        Credit=TotalDiscount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                # credit sales start here
                if float(CashReceived) == 0 and float(BankAmount) == 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                # credit sales end here

                # customer with cash and customer with partial cash start here
                elif (account_group == 10 or account_group == 29 or account_group == 32) and float(CashReceived) > 0 and float(BankAmount) == 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=LedgerID,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=LedgerID,
                        Debit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=CashID,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=CashID,
                        Credit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                # customer with cash and customer with partial cash end here

                # customer with bank and customer with partial bank start here
                elif (account_group == 10 or account_group == 29 or account_group == 32) and float(CashReceived) == 0 and float(BankAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=LedgerID,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=LedgerID,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=BankID,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=BankID,
                        Credit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                # customer with bank and customer with partial bank end here

                # bank with cash and cash with cash start here
                elif (account_group == 8 or account_group == 9) and float(CashReceived) > 0 and float(BankAmount) == 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=CashID,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=CashID,
                        Credit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=SalesAccount,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=SalesAccount,
                        Debit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    csh_value = float(GrandTotal) - float(CashReceived)
                    if float(csh_value) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=LedgerID,
                            RelatedLedgerID=SalesAccount,
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
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=LedgerID,
                            RelatedLedgerID=SalesAccount,
                            Debit=csh_value,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=LedgerID,
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
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=LedgerID,
                            Credit=csh_value,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                # bank with cash and cash with cash end here

                # bank with bank and cash with bank start here
                elif (account_group == 8 or account_group == 9) and float(CashReceived) == 0 and float(BankAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=BankID,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=BankID,
                        Credit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=SalesAccount,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=SalesAccount,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    bnk_value = float(GrandTotal) - float(BankAmount)
                    if not float(bnk_value) == 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=LedgerID,
                            RelatedLedgerID=SalesAccount,
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
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=LedgerID,
                            RelatedLedgerID=SalesAccount,
                            Debit=bnk_value,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=LedgerID,
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
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=LedgerID,
                            Credit=bnk_value,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                # bank with bank and cash with bank end here

                # customer with partial cash /bank and customer with cash/bank
                elif (account_group == 10 or account_group == 29 or account_group == 32) and float(CashReceived) > 0 and float(BankAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=LedgerID,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=LedgerID,
                        Debit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=CashID,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=CashID,
                        Credit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=LedgerID,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=LedgerID,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=BankID,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
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
                # customer with partial cash /bank and customer with cash/bank

                # cash with cash/bank start here
                elif (account_group == 9 or account_group == 8) and float(CashReceived) > 0 and float(BankAmount) > 0:
                    if float(Balance) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=CashID,
                            Credit=Balance,
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
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=SalesAccount,
                            RelatedLedgerID=CashID,
                            Credit=Balance,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=CashID,
                            RelatedLedgerID=SalesAccount,
                            Debit=Balance,
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
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=CashID,
                            RelatedLedgerID=SalesAccount,
                            Debit=Balance,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=SalesAccount,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=SalesAccount,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=BankID,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=BankID,
                        Credit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=CashID,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=CashID,
                        Credit=CashReceived,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=SalesAccount,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=SalesAccount,
                        Debit=CashReceived,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                # cash with cash/bank end here
                # new posting ending here

                salesdetails = data["SalesDetails"]
                if SalesDetails:
                    for salesdetail in salesdetails:

                        ProductID = salesdetail['ProductID']
                        if ProductID:
                            Qty = salesdetail['Qty']
                            FreeQty = salesdetail['FreeQty']
                            Flavour = salesdetail['Flavour']
                            PriceListID = salesdetail['PriceListID']
                            BatchCode = salesdetail['BatchCode']
                            is_inclusive = salesdetail['is_inclusive']

                            UnitPrice = float(salesdetail['UnitPrice'])
                            InclusivePrice = float(
                                salesdetail['InclusivePrice'])
                            RateWithTax = float(salesdetail['RateWithTax'])
                            CostPerPrice = float(salesdetail['CostPerPrice'])
                            AddlDiscPerc = float(salesdetail['AddlDiscPerc'])
                            AddlDiscAmt = float(salesdetail['AddlDiscAmt'])
                            DiscountPerc = salesdetail['DiscountPerc']
                            DiscountAmount = salesdetail['DiscountAmount']
                            GrossAmount = float(salesdetail['GrossAmount'])
                            TaxableAmount = float(salesdetail['TaxableAmount'])
                            VATPerc = float(salesdetail['VATPerc'])
                            VATAmount = float(salesdetail['VATAmount'])
                            SGSTPerc = float(salesdetail['SGSTPerc'])
                            SGSTAmount = float(salesdetail['SGSTAmount'])
                            CGSTPerc = float(salesdetail['CGSTPerc'])
                            CGSTAmount = float(salesdetail['CGSTAmount'])
                            IGSTPerc = float(salesdetail['IGSTPerc'])
                            IGSTAmount = float(salesdetail['IGSTAmount'])
                            NetAmount = float(salesdetail['NetAmount'])
                            KFCAmount = float(salesdetail['KFCAmount'])
                            TAX1Perc = float(salesdetail['TAX1Perc'])
                            TAX1Amount = float(salesdetail['TAX1Amount'])
                            TAX2Perc = float(salesdetail['TAX2Perc'])
                            TAX2Amount = float(salesdetail['TAX2Amount'])
                            TAX3Perc = float(salesdetail['TAX3Perc'])
                            TAX3Amount = float(salesdetail['TAX3Amount'])

                            # UnitPrice = round(UnitPrice, PriceRounding)
                            # InclusivePrice = round(InclusivePrice, PriceRounding)
                            # RateWithTax = round(RateWithTax, PriceRounding)

                            CostPerPrice = PriceList.objects.get(
                                CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).PurchasePrice

                            # CostPerPrice = round(CostPerPrice, PriceRounding)
                            # AddlDiscPerc = round(AddlDiscPerc, PriceRounding)

                            # AddlDiscAmt = round(AddlDiscAmt, PriceRounding)
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
                            # TAX1Perc = round(TAX1Perc, PriceRounding)

                            # TAX1Amount = round(TAX1Amount, PriceRounding)
                            # TAX2Perc = round(TAX2Perc, PriceRounding)
                            # TAX2Amount = round(TAX2Amount, PriceRounding)
                            # TAX3Perc = round(TAX3Perc, PriceRounding)
                            # TAX3Amount = round(TAX3Amount, PriceRounding)
                            # KFCAmount = round(KFCAmount, PriceRounding)

                            try:
                                SerialNos = salesdetail['SerialNos']
                            except:
                                SerialNos = []

                            try:
                                Description = salesdetail['Description']
                            except:
                                Description = ""

                            try:
                                KFCPerc = salesdetail['KFCPerc']
                            except:
                                KFCPerc = 0

                            # KFCPerc = round(KFCPerc, PriceRounding)
                            # BatchCode = ""

                            if is_inclusive == True:
                                Batch_salesPrice = InclusivePrice
                            else:
                                Batch_salesPrice = UnitPrice

                            product_is_Service = Product.objects.get(
                                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).is_Service
                            print("==================-----------------",
                                  product_is_Service)
                            product_purchasePrice = PriceList.objects.get(
                                CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID).PurchasePrice
                            MultiFactor = PriceList.objects.get(
                                CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor

                            qty_batch = float(FreeQty) + float(Qty)
                            Qty_batch = float(MultiFactor) * float(qty_batch)

                            check_AllowUpdateBatchPriceInSales = False
                            if product_is_Service == False:
                                if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="AllowUpdateBatchPriceInSales").exists():
                                    check_AllowUpdateBatchPriceInSales = GeneralSettings.objects.get(
                                        CompanyID=CompanyID, SettingsType="AllowUpdateBatchPriceInSales").SettingsValue

                                if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                                    check_EnableProductBatchWise = GeneralSettings.objects.get(
                                        CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
                                    # check_BatchCriteria = "PurchasePriceAndSalesPrice"

                                    if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                                        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
                                            if check_AllowUpdateBatchPriceInSales == "True" or check_AllowUpdateBatchPriceInSales == True:
                                                batch_ins = Batch.objects.get(
                                                    CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                                                StockOut = batch_ins.StockOut
                                                BatchCode = batch_ins.BatchCode
                                                NewStock = float(
                                                    StockOut) + float(Qty_batch)
                                                batch_ins.StockOut = NewStock
                                                batch_ins.SalesPrice = Batch_salesPrice
                                                batch_ins.save()
                                            else:
                                                batch_ins = Batch.objects.get(
                                                    CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                                                StockOut = batch_ins.StockOut
                                                BatchCode = batch_ins.BatchCode
                                                NewStock = float(
                                                    StockOut) + float(Qty_batch)
                                                batch_ins.StockOut = NewStock
                                                batch_ins.save()
                                        else:
                                            BatchCode = get_auto_AutoBatchCode(
                                                Batch, BranchID, CompanyID)
                                            Batch.objects.create(
                                                CompanyID=CompanyID,
                                                BranchID=BranchID,
                                                BatchCode=BatchCode,
                                                StockOut=Qty_batch,
                                                PurchasePrice=product_purchasePrice,
                                                SalesPrice=Batch_salesPrice,
                                                PriceListID=PriceListID,
                                                ProductID=ProductID,
                                                WareHouseID=WarehouseID,
                                                CreatedDate=today,
                                                UpdatedDate=today,
                                                CreatedUserID=CreatedUserID,
                                            )

                                    else:
                                        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PriceListID=PriceListID).exists():
                                            batch_ins = Batch.objects.get(
                                                CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PriceListID=PriceListID)
                                            StockOut = batch_ins.StockOut
                                            BatchCode = batch_ins.BatchCode
                                            NewStock = float(
                                                StockOut) + float(Qty_batch)
                                            batch_ins.StockOut = NewStock
                                            batch_ins.save()
                                        else:
                                            BatchCode = get_auto_AutoBatchCode(
                                                Batch, BranchID, CompanyID)
                                            Batch.objects.create(
                                                CompanyID=CompanyID,
                                                BranchID=BranchID,
                                                BatchCode=BatchCode,
                                                StockOut=Qty_batch,
                                                PurchasePrice=product_purchasePrice,
                                                SalesPrice=Batch_salesPrice,
                                                PriceListID=PriceListID,
                                                ProductID=ProductID,
                                                WareHouseID=WarehouseID,
                                                CreatedDate=today,
                                                UpdatedDate=today,
                                                CreatedUserID=CreatedUserID,
                                            )

                            SalesDetailsID = get_auto_id(
                                SalesDetails, BranchID, CompanyID)

                            if SerialNos:
                                print(SerialNos)
                                print(
                                    "serialllllllllllllllllllllllllllllllllllllll")
                                for sn in SerialNos:
                                    try:
                                        SerialNo = sn['SerialNo']
                                    except:
                                        SerialNo = ""
                                    try:
                                        ItemCode = sn['ItemCode']
                                    except:
                                        ItemCode = ""

                                    SerialNumbers.objects.create(
                                        VoucherType="SI",
                                        CompanyID=CompanyID,
                                        SerialNo=SerialNo,
                                        ItemCode=ItemCode,
                                        SalesMasterID=SalesMasterID,
                                        SalesDetailsID=SalesDetailsID,
                                        CreatedDate=today,
                                        UpdatedDate=today,
                                        CreatedUserID=CreatedUserID,
                                    )

                            log_instance = SalesDetails_Log.objects.create(
                                TransactionID=SalesDetailsID,
                                BranchID=BranchID,
                                Action=Action,
                                SalesMasterID=SalesMasterID,
                                ProductID=ProductID,
                                Qty=Qty,
                                ReturnQty=Qty,
                                FreeQty=FreeQty,
                                UnitPrice=UnitPrice,
                                InclusivePrice=InclusivePrice,
                                RateWithTax=RateWithTax,
                                CostPerPrice=CostPerPrice,
                                PriceListID=PriceListID,
                                AddlDiscPerc=AddlDiscPerc,
                                AddlDiscAmt=AddlDiscAmt,
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
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                Flavour=Flavour,
                                TAX1Perc=TAX1Perc,
                                TAX1Amount=TAX1Amount,
                                TAX2Perc=TAX2Perc,
                                TAX2Amount=TAX2Amount,
                                TAX3Perc=TAX3Perc,
                                TAX3Amount=TAX3Amount,
                                KFCAmount=KFCAmount,
                                CompanyID=CompanyID,
                                BatchCode=BatchCode,
                                Description=Description,
                                KFCPerc=KFCPerc
                            )

                            SalesDetails.objects.create(
                                SalesDetailsID=SalesDetailsID,
                                BranchID=BranchID,
                                Action=Action,
                                SalesMasterID=SalesMasterID,
                                ProductID=ProductID,
                                Qty=Qty,
                                ReturnQty=Qty,
                                FreeQty=FreeQty,
                                UnitPrice=UnitPrice,
                                InclusivePrice=InclusivePrice,
                                RateWithTax=RateWithTax,
                                CostPerPrice=CostPerPrice,
                                PriceListID=PriceListID,
                                AddlDiscPerc=AddlDiscPerc,
                                AddlDiscAmt=AddlDiscAmt,
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
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                Flavour=Flavour,
                                TAX1Perc=TAX1Perc,
                                TAX1Amount=TAX1Amount,
                                TAX2Perc=TAX2Perc,
                                TAX2Amount=TAX2Amount,
                                TAX3Perc=TAX3Perc,
                                TAX3Amount=TAX3Amount,
                                KFCAmount=KFCAmount,
                                CompanyID=CompanyID,
                                BatchCode=BatchCode,
                                LogID=log_instance.ID,
                                Description=Description,
                                KFCPerc=KFCPerc
                            )

                            if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="SalesPriceUpdate").exists():
                                check_SalesPriceUpdate = GeneralSettings.objects.get(
                                    CompanyID=CompanyID, SettingsType="SalesPriceUpdate", BranchID=BranchID).SettingsValue
                                if check_SalesPriceUpdate == "True" or check_SalesPriceUpdate == True:
                                    pri_ins = PriceList.objects.get(
                                        CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID)
                                    pri_ins.SalesPrice = Batch_salesPrice
                                    pri_ins.save()

                            if product_is_Service == False:

                                # priceList = PriceList.objects.get(CompanyID=CompanyID,PriceListID=PriceListID,BranchID=BranchID)

                                # MultiFactor = PriceList.objects.get(
                                #     CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor
                                PriceListID_DefUnit = PriceList.objects.get(
                                    CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

                                # PriceListID_DefUnit = priceList.PriceListID
                                # MultiFactor = priceList.MultiFactor

                                # PurchasePrice = priceList.PurchasePrice
                                # SalesPrice = priceList.SalesPrice

                                qty = float(FreeQty) + float(Qty)

                                Qty = float(MultiFactor) * float(qty)
                                Cost = float(CostPerPrice) / float(MultiFactor)

                                # Qy = round(Qty, 4)
                                # Qty = str(Qy)

                                # Ct = round(Cost, 4)
                                # Cost = str(Ct)

                                princeList_instance = PriceList.objects.get(
                                    CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit, BranchID=BranchID)
                                PurchasePrice = princeList_instance.PurchasePrice
                                SalesPrice = princeList_instance.SalesPrice

                                changQty = Qty
                                if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID_DefUnit).exists():
                                    if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID, Qty__gt=0, PriceListID=PriceListID_DefUnit).exists():
                                        stockRate_instances = StockRate.objects.filter(
                                            CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID, Qty__gt=0, PriceListID=PriceListID_DefUnit)
                                        count = stockRate_instances.count()
                                        last = 0
                                        for stockRate_instance in stockRate_instances:
                                            last = float(last) + float(1)
                                            StockRateID = stockRate_instance.StockRateID
                                            stock_post_cost = stockRate_instance.Cost
                                            if float(stockRate_instance.Qty) > float(changQty):
                                                # stockRate_instance.Qty = float(
                                                #     stockRate_instance.Qty) - float(changQty)
                                                # changQty = float(stockRate_instance.Qty) - float(changQty)
                                                lastQty = float(
                                                    stockRate_instance.Qty) - float(changQty)
                                                chqy = changQty
                                                changQty = 0
                                                stockRate_instance.Qty = lastQty
                                                stockRate_instance.save()

                                                if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                               VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit).exists():
                                                    stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                                                  VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit)
                                                    QtyOut = stockPost_instance.QtyOut
                                                    newQty = float(
                                                        QtyOut) + float(chqy)

                                                    stockPost_instance.QtyOut = newQty
                                                    stockPost_instance.save()
                                                else:
                                                    StockPostingID = get_auto_stockPostid(
                                                        StockPosting, BranchID, CompanyID)
                                                    StockPosting.objects.create(
                                                        StockPostingID=StockPostingID,
                                                        BranchID=BranchID,
                                                        Action=Action,
                                                        Date=Date,
                                                        VoucherMasterID=SalesMasterID,
                                                        VoucherType=VoucherType,
                                                        ProductID=ProductID,
                                                        BatchID=BatchID,
                                                        WareHouseID=WarehouseID,
                                                        QtyOut=chqy,
                                                        Rate=stock_post_cost,
                                                        PriceListID=PriceListID_DefUnit,
                                                        IsActive=IsActive,
                                                        CreatedDate=today,
                                                        UpdatedDate=today,
                                                        CreatedUserID=CreatedUserID,
                                                        CompanyID=CompanyID,
                                                    )

                                                    StockPosting_Log.objects.create(
                                                        TransactionID=StockPostingID,
                                                        BranchID=BranchID,
                                                        Action=Action,
                                                        Date=Date,
                                                        VoucherMasterID=SalesMasterID,
                                                        VoucherType=VoucherType,
                                                        ProductID=ProductID,
                                                        BatchID=BatchID,
                                                        WareHouseID=WarehouseID,
                                                        QtyOut=chqy,
                                                        Rate=stock_post_cost,
                                                        PriceListID=PriceListID_DefUnit,
                                                        IsActive=IsActive,
                                                        CreatedDate=today,
                                                        UpdatedDate=today,
                                                        CreatedUserID=CreatedUserID,
                                                        CompanyID=CompanyID,
                                                    )

                                                if StockTrans.objects.filter(StockRateID=StockRateID, DetailID=SalesDetailsID, MasterID=SalesMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                                                    stockTra_in = StockTrans.objects.filter(
                                                        StockRateID=StockRateID, DetailID=SalesDetailsID, MasterID=SalesMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                                                    stockTra_in.Qty = float(
                                                        stockTra_in.Qty) + float(chqy)
                                                    stockTra_in.save()
                                                else:
                                                    StockTransID = get_auto_StockTransID(
                                                        StockTrans, BranchID, CompanyID)
                                                    StockTrans.objects.create(
                                                        StockTransID=StockTransID,
                                                        BranchID=BranchID,
                                                        VoucherType=VoucherType,
                                                        StockRateID=StockRateID,
                                                        DetailID=SalesDetailsID,
                                                        MasterID=SalesMasterID,
                                                        Qty=chqy,
                                                        IsActive=IsActive,
                                                        CompanyID=CompanyID,
                                                    )
                                                break
                                            elif float(stockRate_instance.Qty) < float(changQty):
                                                if float(changQty) > float(stockRate_instance.Qty):
                                                    changQty = float(changQty) - \
                                                        float(
                                                            stockRate_instance.Qty)
                                                    stckQty = stockRate_instance.Qty
                                                    stockRate_instance.Qty = 0
                                                    stockRate_instance.save()

                                                    if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                                   VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit).exists():
                                                        stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                                                      VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit)
                                                        QtyOut = stockPost_instance.QtyOut
                                                        newQty = float(QtyOut) + \
                                                            float(stckQty)
                                                        stockPost_instance.QtyOut = newQty
                                                        stockPost_instance.save()
                                                    else:
                                                        StockPostingID = get_auto_stockPostid(
                                                            StockPosting, BranchID, CompanyID)
                                                        StockPosting.objects.create(
                                                            StockPostingID=StockPostingID,
                                                            BranchID=BranchID,
                                                            Action=Action,
                                                            Date=Date,
                                                            VoucherMasterID=SalesMasterID,
                                                            VoucherType=VoucherType,
                                                            ProductID=ProductID,
                                                            BatchID=BatchID,
                                                            WareHouseID=WarehouseID,
                                                            QtyOut=stckQty,
                                                            Rate=stock_post_cost,
                                                            PriceListID=PriceListID_DefUnit,
                                                            IsActive=IsActive,
                                                            CreatedDate=today,
                                                            UpdatedDate=today,
                                                            CreatedUserID=CreatedUserID,
                                                            CompanyID=CompanyID,
                                                        )

                                                        StockPosting_Log.objects.create(
                                                            TransactionID=StockPostingID,
                                                            BranchID=BranchID,
                                                            Action=Action,
                                                            Date=Date,
                                                            VoucherMasterID=SalesMasterID,
                                                            VoucherType=VoucherType,
                                                            ProductID=ProductID,
                                                            BatchID=BatchID,
                                                            WareHouseID=WarehouseID,
                                                            QtyOut=stckQty,
                                                            Rate=stock_post_cost,
                                                            PriceListID=PriceListID_DefUnit,
                                                            IsActive=IsActive,
                                                            CreatedDate=today,
                                                            UpdatedDate=today,
                                                            CreatedUserID=CreatedUserID,
                                                            CompanyID=CompanyID,
                                                        )
                                                    if StockTrans.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, DetailID=SalesDetailsID, MasterID=SalesMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                                                        stockTra_in = StockTrans.objects.filter(
                                                            CompanyID=CompanyID, StockRateID=StockRateID, DetailID=SalesDetailsID, MasterID=SalesMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                                                        stockTra_in.Qty = float(
                                                            stockTra_in.Qty) + float(stckQty)
                                                        stockTra_in.save()
                                                    else:
                                                        StockTransID = get_auto_StockTransID(
                                                            StockTrans, BranchID, CompanyID)
                                                        StockTrans.objects.create(
                                                            StockTransID=StockTransID,
                                                            BranchID=BranchID,
                                                            VoucherType=VoucherType,
                                                            StockRateID=StockRateID,
                                                            DetailID=SalesDetailsID,
                                                            MasterID=SalesMasterID,
                                                            Qty=stckQty,
                                                            IsActive=IsActive,
                                                            CompanyID=CompanyID,
                                                        )
                                                else:
                                                    if changQty < 0:
                                                        changQty = 0
                                                    # chqty = changQty
                                                    changQty = float(
                                                        stockRate_instance.Qty) - float(changQty)
                                                    chqty = changQty
                                                    stockRate_instance.Qty = changQty
                                                    changQty = 0
                                                    stockRate_instance.save()

                                                    if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                                   VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit).exists():
                                                        stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                                                      VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit)
                                                        QtyOut = stockPost_instance.QtyOut
                                                        newQty = float(
                                                            QtyOut) + float(chqty)
                                                        stockPost_instance.QtyOut = newQty
                                                        stockPost_instance.save()
                                                    else:
                                                        StockPostingID = get_auto_stockPostid(
                                                            StockPosting, BranchID, CompanyID)
                                                        StockPosting.objects.create(
                                                            StockPostingID=StockPostingID,
                                                            BranchID=BranchID,
                                                            Action=Action,
                                                            Date=Date,
                                                            VoucherMasterID=SalesMasterID,
                                                            VoucherType=VoucherType,
                                                            ProductID=ProductID,
                                                            BatchID=BatchID,
                                                            WareHouseID=WarehouseID,
                                                            QtyOut=chqty,
                                                            Rate=stock_post_cost,
                                                            PriceListID=PriceListID_DefUnit,
                                                            IsActive=IsActive,
                                                            CreatedDate=today,
                                                            UpdatedDate=today,
                                                            CreatedUserID=CreatedUserID,
                                                            CompanyID=CompanyID,
                                                        )

                                                        StockPosting_Log.objects.create(
                                                            TransactionID=StockPostingID,
                                                            BranchID=BranchID,
                                                            Action=Action,
                                                            Date=Date,
                                                            VoucherMasterID=SalesMasterID,
                                                            VoucherType=VoucherType,
                                                            ProductID=ProductID,
                                                            BatchID=BatchID,
                                                            WareHouseID=WarehouseID,
                                                            QtyOut=chqty,
                                                            Rate=stock_post_cost,
                                                            PriceListID=PriceListID_DefUnit,
                                                            IsActive=IsActive,
                                                            CreatedDate=today,
                                                            UpdatedDate=today,
                                                            CreatedUserID=CreatedUserID,
                                                            CompanyID=CompanyID,
                                                        )

                                                    if StockTrans.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, DetailID=SalesDetailsID, MasterID=SalesMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                                                        stockTra_in = StockTrans.objects.filter(
                                                            CompanyID=CompanyID, StockRateID=StockRateID, DetailID=SalesDetailsID, MasterID=SalesMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                                                        stockTra_in.Qty = float(
                                                            stockTra_in.Qty) + float(chqty)
                                                        stockTra_in.save()
                                                    else:
                                                        StockTransID = get_auto_StockTransID(
                                                            StockTrans, BranchID, CompanyID)
                                                        StockTrans.objects.create(
                                                            StockTransID=StockTransID,
                                                            BranchID=BranchID,
                                                            VoucherType=VoucherType,
                                                            StockRateID=StockRateID,
                                                            DetailID=SalesDetailsID,
                                                            MasterID=SalesMasterID,
                                                            Qty=chqty,
                                                            IsActive=IsActive,
                                                            CompanyID=CompanyID,
                                                        )

                                            elif float(stockRate_instance.Qty) == float(changQty):
                                                chty = stockRate_instance.Qty
                                                stockRate_instance.Qty = 0
                                                changQty = 0
                                                stockRate_instance.save()

                                                if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                               VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit).exists():
                                                    stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                                                  VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit)
                                                    QtyOut = stockPost_instance.QtyOut
                                                    newQty = float(QtyOut) + \
                                                        float(chty)
                                                    stockPost_instance.QtyOut = newQty
                                                    stockPost_instance.save()
                                                else:
                                                    StockPostingID = get_auto_stockPostid(
                                                        StockPosting, BranchID, CompanyID)
                                                    StockPosting.objects.create(
                                                        StockPostingID=StockPostingID,
                                                        BranchID=BranchID,
                                                        Action=Action,
                                                        Date=Date,
                                                        VoucherMasterID=SalesMasterID,
                                                        VoucherType=VoucherType,
                                                        ProductID=ProductID,
                                                        BatchID=BatchID,
                                                        WareHouseID=WarehouseID,
                                                        QtyOut=chty,
                                                        Rate=stock_post_cost,
                                                        PriceListID=PriceListID_DefUnit,
                                                        IsActive=IsActive,
                                                        CreatedDate=today,
                                                        UpdatedDate=today,
                                                        CreatedUserID=CreatedUserID,
                                                        CompanyID=CompanyID,
                                                    )

                                                    StockPosting_Log.objects.create(
                                                        TransactionID=StockPostingID,
                                                        BranchID=BranchID,
                                                        Action=Action,
                                                        Date=Date,
                                                        VoucherMasterID=SalesMasterID,
                                                        VoucherType=VoucherType,
                                                        ProductID=ProductID,
                                                        BatchID=BatchID,
                                                        WareHouseID=WarehouseID,
                                                        QtyOut=chty,
                                                        Rate=stock_post_cost,
                                                        PriceListID=PriceListID_DefUnit,
                                                        IsActive=IsActive,
                                                        CreatedDate=today,
                                                        UpdatedDate=today,
                                                        CreatedUserID=CreatedUserID,
                                                        CompanyID=CompanyID,
                                                    )

                                                if StockTrans.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, DetailID=SalesDetailsID, MasterID=SalesMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                                                    stockTra_in = StockTrans.objects.filter(
                                                        CompanyID=CompanyID, StockRateID=StockRateID, DetailID=SalesDetailsID, MasterID=SalesMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                                                    stockTra_in.Qty = float(
                                                        stockTra_in.Qty) + float(chty)
                                                    stockTra_in.save()
                                                else:
                                                    StockTransID = get_auto_StockTransID(
                                                        StockTrans, BranchID, CompanyID)
                                                    StockTrans.objects.create(
                                                        StockTransID=StockTransID,
                                                        BranchID=BranchID,
                                                        VoucherType=VoucherType,
                                                        StockRateID=StockRateID,
                                                        DetailID=SalesDetailsID,
                                                        MasterID=SalesMasterID,
                                                        Qty=chty,
                                                        IsActive=IsActive,
                                                        CompanyID=CompanyID,
                                                    )
                                                break

                                    if float(changQty) > 0:
                                        if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID, Qty__lte=0, PriceListID=PriceListID_DefUnit).exists():
                                            stockRate_instance = StockRate.objects.filter(
                                                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID, Qty__lte=0, PriceListID=PriceListID_DefUnit).first()
                                            stock_post_cost = stockRate_instance.Cost
                                            if float(changQty) > 0:
                                                stockRate_instance.Qty = float(
                                                    stockRate_instance.Qty) - float(changQty)
                                                stockRate_instance.save()

                                                if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                               VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit).exists():
                                                    stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                                                  VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit)
                                                    QtyOut = stockPost_instance.QtyOut
                                                    newQty = float(QtyOut) + \
                                                        float(changQty)
                                                    stockPost_instance.QtyOut = newQty
                                                    stockPost_instance.save()
                                                else:
                                                    StockPostingID = get_auto_stockPostid(
                                                        StockPosting, BranchID, CompanyID)
                                                    StockPosting.objects.create(
                                                        StockPostingID=StockPostingID,
                                                        BranchID=BranchID,
                                                        Action=Action,
                                                        Date=Date,
                                                        VoucherMasterID=SalesMasterID,
                                                        VoucherType=VoucherType,
                                                        ProductID=ProductID,
                                                        BatchID=BatchID,
                                                        WareHouseID=WarehouseID,
                                                        QtyOut=changQty,
                                                        Rate=stock_post_cost,
                                                        PriceListID=PriceListID_DefUnit,
                                                        IsActive=IsActive,
                                                        CreatedDate=today,
                                                        UpdatedDate=today,
                                                        CreatedUserID=CreatedUserID,
                                                        CompanyID=CompanyID,
                                                    )

                                                    StockPosting_Log.objects.create(
                                                        TransactionID=StockPostingID,
                                                        BranchID=BranchID,
                                                        Action=Action,
                                                        Date=Date,
                                                        VoucherMasterID=SalesMasterID,
                                                        VoucherType=VoucherType,
                                                        ProductID=ProductID,
                                                        BatchID=BatchID,
                                                        WareHouseID=WarehouseID,
                                                        QtyOut=changQty,
                                                        Rate=stock_post_cost,
                                                        PriceListID=PriceListID_DefUnit,
                                                        IsActive=IsActive,
                                                        CreatedDate=today,
                                                        UpdatedDate=today,
                                                        CreatedUserID=CreatedUserID,
                                                        CompanyID=CompanyID,
                                                    )

                                                if not StockTrans.objects.filter(CompanyID=CompanyID,
                                                                                 StockRateID=stockRate_instance.StockRateID,
                                                                                 DetailID=SalesDetailsID,
                                                                                 MasterID=SalesMasterID,
                                                                                 VoucherType=VoucherType,
                                                                                 BranchID=BranchID).exists():

                                                    StockTransID = get_auto_StockTransID(
                                                        StockTrans, BranchID, CompanyID)
                                                    StockTrans.objects.create(
                                                        CompanyID=CompanyID,
                                                        StockTransID=StockTransID,
                                                        BranchID=BranchID,
                                                        VoucherType=VoucherType,
                                                        StockRateID=stockRate_instance.StockRateID,
                                                        DetailID=SalesDetailsID,
                                                        MasterID=SalesMasterID,
                                                        Qty=changQty,
                                                        IsActive=IsActive
                                                    )
                                else:
                                    if float(Qty) > 0:
                                        qty = float(Qty) * -1
                                    StockRateID = get_auto_StockRateID(
                                        StockRate, BranchID, CompanyID)
                                    StockRate.objects.create(
                                        StockRateID=StockRateID,
                                        BranchID=BranchID,
                                        BatchID=BatchID,
                                        PurchasePrice=PurchasePrice,
                                        SalesPrice=SalesPrice,
                                        Qty=qty,
                                        Cost=Cost,
                                        ProductID=ProductID,
                                        WareHouseID=WarehouseID,
                                        Date=Date,
                                        PriceListID=PriceListID_DefUnit,
                                        CreatedUserID=CreatedUserID,
                                        CreatedDate=today,
                                        UpdatedDate=today,
                                        CompanyID=CompanyID,
                                    )

                                    StockPostingID = get_auto_stockPostid(
                                        StockPosting, BranchID, CompanyID)
                                    StockPosting.objects.create(
                                        StockPostingID=StockPostingID,
                                        BranchID=BranchID,
                                        Action=Action,
                                        Date=Date,
                                        VoucherMasterID=SalesMasterID,
                                        VoucherType=VoucherType,
                                        ProductID=ProductID,
                                        BatchID=BatchID,
                                        WareHouseID=WarehouseID,
                                        QtyOut=Qty,
                                        Rate=Cost,
                                        PriceListID=PriceListID_DefUnit,
                                        IsActive=IsActive,
                                        CreatedDate=today,
                                        UpdatedDate=today,
                                        CreatedUserID=CreatedUserID,
                                        CompanyID=CompanyID,
                                    )

                                    StockPosting_Log.objects.create(
                                        TransactionID=StockPostingID,
                                        BranchID=BranchID,
                                        Action=Action,
                                        Date=Date,
                                        VoucherMasterID=SalesMasterID,
                                        VoucherType=VoucherType,
                                        ProductID=ProductID,
                                        BatchID=BatchID,
                                        WareHouseID=WarehouseID,
                                        QtyOut=Qty,
                                        Rate=Cost,
                                        PriceListID=PriceListID_DefUnit,
                                        IsActive=IsActive,
                                        CreatedDate=today,
                                        UpdatedDate=today,
                                        CreatedUserID=CreatedUserID,
                                        CompanyID=CompanyID,
                                    )
                                    StockTransID = get_auto_StockTransID(
                                        StockTrans, BranchID, CompanyID)
                                    StockTrans.objects.create(
                                        StockTransID=StockTransID,
                                        BranchID=BranchID,
                                        VoucherType=VoucherType,
                                        StockRateID=StockRateID,
                                        DetailID=SalesDetailsID,
                                        MasterID=SalesMasterID,
                                        Qty=qty,
                                        IsActive=IsActive,
                                        CompanyID=CompanyID,
                                    )

                # request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sales Invoice',
                #              'Create', 'Sales Invoice created successfully.', 'Sales Invoice saved successfully.')

                response_data = {
                    "StatusCode": 6000,
                    "id": sales_instance.id,
                    "message": "Sales created Successfully!!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                # request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Sales Invoice',
                             'Create', 'Sales Invoice created Failed.', 'VoucherNo already exist')

                response_data = {
                    "StatusCode": 6001,
                    "message": "VoucherNo already exist!"
                }

                return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again"
        }

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Sales',
                     'Create', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def edit_sales(request, pk):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            CreatedUserID = data['CreatedUserID']
            PriceRounding = data['PriceRounding']

            today = datetime.datetime.now()
            salesMaster_instance = None
            ledgerPostInstances = None
            salesDetails = None

            salesMaster_instance = SalesMaster.objects.get(
                CompanyID=CompanyID, pk=pk)

            SalesMasterID = salesMaster_instance.SalesMasterID
            VoucherNo = salesMaster_instance.VoucherNo
            BranchID = salesMaster_instance.BranchID
            OldLedgerBalance = salesMaster_instance.OldLedgerBalance

            Action = "M"

            try:
                LoyaltyCustomerID = data['LoyaltyCustomerID']
            except:
                LoyaltyCustomerID = None

            Date = data['Date']
            CreditPeriod = data['CreditPeriod']
            LedgerID = data['LedgerID']
            PriceCategoryID = data['PriceCategoryID']
            EmployeeID = data['EmployeeID']
            SalesAccount = data['SalesAccount']
            CustomerName = data['CustomerName']
            Address1 = data['Address1']
            Address2 = data['Address2']
            Address3 = data['Address3']
            Notes = data['Notes']
            FinacialYearID = data['FinacialYearID']
            TaxID = data['TaxID']
            TaxType = data['TaxType']
            WarehouseID = data['WarehouseID']
            TableID = data['TableID']
            SeatNumber = data['SeatNumber']
            NoOfGuests = data['NoOfGuests']
            INOUT = data['INOUT']
            TokenNumber = data['TokenNumber']
            CardTypeID = data['CardTypeID']
            CardNumber = data['CardNumber']
            IsActive = data['IsActive']
            IsPosted = data['IsPosted']
            SalesType = data['SalesType']
            BatchID = data['BatchID']

            TotalGrossAmt = float(data['TotalGrossAmt'])
            AddlDiscPercent = float(data['AddlDiscPercent'])
            AddlDiscAmt = float(data['AddlDiscAmt'])
            TotalDiscount = float(data['TotalDiscount'])
            TotalTax = float(data['TotalTax'])
            NetTotal = float(data['NetTotal'])
            AdditionalCost = float(data['AdditionalCost'])
            GrandTotal = float(data['GrandTotal'])
            RoundOff = float(data['RoundOff'])
            CashReceived = float(data['CashReceived'])
            BankAmount = float(data['BankAmount'])
            BillDiscPercent = float(data['BillDiscPercent'])
            BillDiscAmt = float(data['BillDiscAmt'])
            VATAmount = float(data['VATAmount'])
            SGSTAmount = float(data['SGSTAmount'])
            CGSTAmount = float(data['CGSTAmount'])
            IGSTAmount = float(data['IGSTAmount'])
            TAX1Amount = float(data['TAX1Amount'])
            TAX2Amount = float(data['TAX2Amount'])
            TAX3Amount = float(data['TAX3Amount'])

            try:
                KFCAmount = float(data['KFCAmount'])
            except:
                KFCAmount = 0

            Cash_Account = None
            Bank_Account = None

            if UserTable.objects.filter(CompanyID=CompanyID, customer__user__pk=CreatedUserID).exists():
                Cash_Account = UserTable.objects.get(
                    CompanyID=CompanyID, customer__user__pk=CreatedUserID).Cash_Account
                Bank_Account = UserTable.objects.get(
                    CompanyID=CompanyID, customer__user__pk=CreatedUserID).Bank_Account

            try:
                CashID = data['CashID']
            except:
                CashID = Cash_Account

            try:
                BankID = data['BankID']
            except:
                BankID = Bank_Account

            Balance = float(data['Balance'])

            AllowCashReceiptMoreSaleAmt = data['AllowCashReceiptMoreSaleAmt']

            # TotalGrossAmt = round(TotalGrossAmt, PriceRounding)
            # AddlDiscPercent = round(AddlDiscPercent, PriceRounding)
            # AddlDiscAmt = round(AddlDiscAmt, PriceRounding)
            # TotalDiscount = round(TotalDiscount, PriceRounding)
            # TotalTax = round(TotalTax, PriceRounding)
            # NetTotal = round(NetTotal, PriceRounding)

            # AdditionalCost = round(AdditionalCost, PriceRounding)
            # GrandTotal = round(GrandTotal, PriceRounding)
            # RoundOff = round(RoundOff, PriceRounding)
            # CashReceived = round(CashReceived, PriceRounding)
            # BankAmount = round(BankAmount, PriceRounding)

            # BillDiscPercent = round(BillDiscPercent, PriceRounding)
            # BillDiscAmt = round(BillDiscAmt, PriceRounding)
            # VATAmount = round(VATAmount, PriceRounding)
            # SGSTAmount = round(SGSTAmount, PriceRounding)
            # CGSTAmount = round(CGSTAmount, PriceRounding)

            # IGSTAmount = round(IGSTAmount, PriceRounding)
            # TAX1Amount = round(TAX1Amount, PriceRounding)
            # TAX2Amount = round(TAX2Amount, PriceRounding)
            # TAX3Amount = round(TAX3Amount, PriceRounding)
            # KFCAmount = round(KFCAmount, PriceRounding)
            # Balance = round(Balance, PriceRounding)

            TransactionTypeID = data['TransactionTypeID']

            if AllowCashReceiptMoreSaleAmt == True or AllowCashReceiptMoreSaleAmt == "true":
                CashAmount = CashReceived
            elif float(Balance) < 0:
                CashAmount = float(GrandTotal) - float(BankAmount)
            else:
                CashAmount = CashReceived

            try:
                ShippingCharge = data['ShippingCharge']
            except:
                ShippingCharge = 0

            try:
                shipping_tax_amount = data['shipping_tax_amount']
            except:
                shipping_tax_amount = 0

            try:
                TaxTypeID = data['TaxTypeID']
            except:
                TaxTypeID = ""

            try:
                SAC = data['SAC']
            except:
                SAC = ""

            try:
                SalesTax = data['SalesTax']
            except:
                SalesTax = 0

              # =========
            details = data["SalesDetails"]
            TotalTaxableAmount = 0
            for i in details:
                TotalTaxableAmount+= float(i['TaxableAmount'])
            # =========

            # Loyalty Customer instance
            is_LoyaltyCustomer = False
            loyalty_customer = None
            if LoyaltyCustomerID:
                if LoyaltyCustomer.objects.filter(pk=LoyaltyCustomerID).exists():
                    loyalty_customer = LoyaltyCustomer.objects.get(
                        pk=LoyaltyCustomerID)
                    is_LoyaltyCustomer = True

            SalesMaster_Log.objects.create(
                LoyaltyCustomerID=loyalty_customer,
                TotalTaxableAmount=TotalTaxableAmount,
                TransactionID=SalesMasterID,
                BranchID=BranchID,
                VoucherNo=VoucherNo,
                Date=Date,
                CreditPeriod=CreditPeriod,
                LedgerID=LedgerID,
                PriceCategoryID=PriceCategoryID,
                EmployeeID=EmployeeID,
                SalesAccount=SalesAccount,
                CustomerName=CustomerName,
                Address1=Address1,
                Address2=Address2,
                Address3=Address3,
                Notes=Notes,
                FinacialYearID=FinacialYearID,
                TotalGrossAmt=TotalGrossAmt,
                AddlDiscPercent=AddlDiscPercent,
                AddlDiscAmt=AddlDiscAmt,
                TotalDiscount=TotalDiscount,
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
                CardTypeID=CardTypeID,
                CardNumber=CardNumber,
                IsActive=IsActive,
                IsPosted=IsPosted,
                SalesType=SalesType,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                TaxID=TaxID,
                TaxType=TaxType,
                BillDiscPercent=BillDiscPercent,
                BillDiscAmt=BillDiscAmt,
                VATAmount=VATAmount,
                SGSTAmount=SGSTAmount,
                CGSTAmount=CGSTAmount,
                IGSTAmount=IGSTAmount,
                TAX1Amount=TAX1Amount,
                TAX2Amount=TAX2Amount,
                TAX3Amount=TAX3Amount,
                Balance=Balance,
                TransactionTypeID=TransactionTypeID,
                CompanyID=CompanyID,
                KFCAmount=KFCAmount,
                OldLedgerBalance=OldLedgerBalance,
                CashID=CashID,
                BankID=BankID,
                ShippingCharge=ShippingCharge,
                shipping_tax_amount=shipping_tax_amount,
                TaxTypeID=TaxTypeID,
                SAC=SAC,
                SalesTax=SalesTax,
            )
            if SerialNumbers.objects.filter(CompanyID=CompanyID, SalesMasterID=SalesMasterID, BranchID=BranchID, VoucherType="SI").exists():
                SerialNumbersInstances = SerialNumbers.objects.filter(
                    CompanyID=CompanyID, SalesMasterID=SalesMasterID, BranchID=BranchID, VoucherType="SI")
                for sli in SerialNumbersInstances:
                    sli.delete()

            if LedgerPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=SalesMasterID, BranchID=BranchID, VoucherType="SI").exists():
                ledgerPostInstances = LedgerPosting.objects.filter(
                    CompanyID=CompanyID, VoucherMasterID=SalesMasterID, BranchID=BranchID, VoucherType="SI")
                for ledgerPostInstance in ledgerPostInstances:
                    ledgerPostInstance.delete()

            if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=SalesMasterID, BranchID=BranchID, VoucherType="SI").exists():
                stockPostingInstances = StockPosting.objects.filter(
                    CompanyID=CompanyID, VoucherMasterID=SalesMasterID, BranchID=BranchID, VoucherType="SI")
                for stockPostingInstance in stockPostingInstances:
                    stockPostingInstance.delete()

            if StockTrans.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType="SI", MasterID=SalesMasterID, IsActive=True).exists():
                trans_ins = StockTrans.objects.filter(
                    CompanyID=CompanyID, VoucherType="SI", MasterID=SalesMasterID, IsActive=True)
                for s in trans_ins:
                    trans_StockRateID = s.StockRateID
                    trans_Qty = s.Qty
                    if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, StockRateID=trans_StockRateID).exists():
                        rate_ins = StockRate.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, StockRateID=trans_StockRateID)
                        rate_ins.Qty = float(rate_ins.Qty) + float(trans_Qty)
                        rate_ins.save()
                    s.IsActive = False
                    s.save()

            if SalesDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SalesMasterID=SalesMasterID).exists():
                sale_ins = SalesDetails.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, SalesMasterID=SalesMasterID)
                for i in sale_ins:
                    BatchCode = i.BatchCode
                    Qty = i.Qty
                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
                        batch_ins = Batch.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                        StockOut = batch_ins.StockOut
                        batch_ins.StockOut = float(StockOut) - float(Qty)
                        batch_ins.save()

            salesMaster_instance.Date = Date
            salesMaster_instance.CreditPeriod = CreditPeriod
            salesMaster_instance.LedgerID = LedgerID
            salesMaster_instance.PriceCategoryID = PriceCategoryID
            salesMaster_instance.EmployeeID = EmployeeID
            salesMaster_instance.SalesAccount = SalesAccount
            salesMaster_instance.CustomerName = CustomerName
            salesMaster_instance.Address1 = Address1
            salesMaster_instance.Address2 = Address2
            salesMaster_instance.Address3 = Address3
            salesMaster_instance.Notes = Notes
            salesMaster_instance.FinacialYearID = FinacialYearID
            salesMaster_instance.TotalGrossAmt = TotalGrossAmt
            salesMaster_instance.AddlDiscPercent = AddlDiscPercent
            salesMaster_instance.AddlDiscAmt = AddlDiscAmt
            salesMaster_instance.TotalDiscount = TotalDiscount
            salesMaster_instance.TotalTax = TotalTax
            salesMaster_instance.NetTotal = NetTotal
            salesMaster_instance.AdditionalCost = AdditionalCost
            salesMaster_instance.GrandTotal = GrandTotal
            salesMaster_instance.RoundOff = RoundOff
            salesMaster_instance.CashReceived = CashReceived
            salesMaster_instance.CashAmount = CashAmount
            salesMaster_instance.BankAmount = BankAmount
            salesMaster_instance.WarehouseID = WarehouseID
            salesMaster_instance.TableID = TableID
            salesMaster_instance.SeatNumber = SeatNumber
            salesMaster_instance.NoOfGuests = NoOfGuests
            salesMaster_instance.INOUT = INOUT
            salesMaster_instance.TokenNumber = TokenNumber
            salesMaster_instance.CardTypeID = CardTypeID
            salesMaster_instance.CardNumber = CardNumber
            salesMaster_instance.IsActive = IsActive
            salesMaster_instance.IsPosted = IsPosted
            salesMaster_instance.SalesType = SalesType
            salesMaster_instance.CreatedUserID = CreatedUserID
            salesMaster_instance.UpdatedDate = today
            salesMaster_instance.Action = Action
            salesMaster_instance.TaxID = TaxID
            salesMaster_instance.TaxType = TaxType
            salesMaster_instance.BillDiscPercent = BillDiscPercent
            salesMaster_instance.BillDiscAmt = BillDiscAmt
            salesMaster_instance.VATAmount = VATAmount
            salesMaster_instance.SGSTAmount = SGSTAmount
            salesMaster_instance.CGSTAmount = CGSTAmount
            salesMaster_instance.IGSTAmount = IGSTAmount
            salesMaster_instance.TAX1Amount = TAX1Amount
            salesMaster_instance.TAX2Amount = TAX2Amount
            salesMaster_instance.TAX3Amount = TAX3Amount
            salesMaster_instance.KFCAmount = KFCAmount
            salesMaster_instance.Balance = Balance
            salesMaster_instance.TransactionTypeID = TransactionTypeID
            salesMaster_instance.CashID = CashID
            salesMaster_instance.BankID = BankID
            salesMaster_instance.ShippingCharge = ShippingCharge
            salesMaster_instance.shipping_tax_amount = shipping_tax_amount
            salesMaster_instance.TaxTypeID = TaxTypeID
            salesMaster_instance.SAC = SAC
            salesMaster_instance.SalesTax = SalesTax
            salesMaster_instance.TotalTaxableAmount = TotalTaxableAmount

            # Taiking Loyalty Customer instance
            if loyalty_customer:
                salesMaster_instance.LoyaltyCustomerID = loyalty_customer

            LoyaltyCustomerID = loyalty_customer,
            salesMaster_instance.save()

            # if SalesDetails.objects.filter(CompanyID=CompanyID,BranchID=BranchID,SalesMasterID=SalesMasterID).exists():
            #     sale_ins = SalesDetails.objects.filter(CompanyID=CompanyID,BranchID=BranchID,SalesMasterID=SalesMasterID)
            #     for i in sale_ins:
            #         BatchCode = i.BatchCode
            #         Qty = i.Qty
            #         if Batch.objects.filter(CompanyID=CompanyID,BranchID=BranchID,BatchCode=BatchCode).exists():
            #             Batch_ins = Batch.objects.get(CompanyID=CompanyID,BranchID=BranchID,BatchCode=BatchCode)
            #             stock_out_ins = Batch_ins.StockOut
            #             Batch_ins.StockOut = float(Batch_ins.StockOut) - float(Qty)
            #             Batch_ins.save()
            # ====== Loyalty Program Point

            Loyalty_Point_Expire = data['Loyalty_Point_Expire']
            if is_LoyaltyCustomer:
                details = data["SalesDetails"]

                try:
                    RadeemPoint = data['RadeemPoint']
                except:
                    RadeemPoint = None
                edit_LoyaltyCalculation(
                    salesMaster_instance, loyalty_customer, details, Loyalty_Point_Expire, RadeemPoint)
                # ===========================

            VoucherType = "SI"

            account_group = AccountLedger.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).AccountGroupUnder

            # new posting starting from here
            if float(shipping_tax_amount) > 0:
                if AccountLedger.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerName="Shipping Charges").exists():
                    RelativeLedgerID = AccountLedger.objects.get(
                        CompanyID=CompanyID, BranchID=BranchID, LedgerName="Shipping Charges").LedgerID
                else:
                    RelativeLedgerID = generated_ledgerID(
                        AccountLedger, BranchID, CompanyID)
                    ShippingChargeLedgerCode = get_LedgerCode(
                        AccountLedger, BranchID, CompanyID)

                    AccountLedger.objects.create(
                        LedgerID=RelativeLedgerID,
                        BranchID=BranchID,
                        LedgerName="Shipping Charges",
                        LedgerCode=ShippingChargeLedgerCode,
                        AccountGroupUnder=71,
                        OpeningBalance=0,
                        CrOrDr="Dr",
                        Notes=Notes,
                        IsActive=True,
                        IsDefault=True,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                    )

                    AccountLedger_Log.objects.create(
                        BranchID=BranchID,
                        TransactionID=RelativeLedgerID,
                        LedgerName="Shipping Charges",
                        LedgerCode=ShippingChargeLedgerCode,
                        AccountGroupUnder=71,
                        OpeningBalance=0,
                        CrOrDr="Dr",
                        Notes=Notes,
                        IsActive=True,
                        IsDefault=True,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                    )
                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=RelativeLedgerID,
                    Debit=shipping_tax_amount,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=RelativeLedgerID,
                    Debit=shipping_tax_amount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=RelativeLedgerID,
                    RelatedLedgerID=SalesAccount,
                    Credit=shipping_tax_amount,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=RelativeLedgerID,
                    RelatedLedgerID=SalesAccount,
                    Credit=shipping_tax_amount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )
            if TaxType == 'VAT':
                if float(VATAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=55,
                        RelatedLedgerID=SalesAccount,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=55,
                        RelatedLedgerID=SalesAccount,
                        Credit=VATAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=55,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=55,
                        Debit=VATAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

            elif TaxType == 'GST Intra-state B2B' or TaxType == 'GST Intra-state B2C':
                if float(CGSTAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=3,
                        RelatedLedgerID=SalesAccount,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=3,
                        RelatedLedgerID=SalesAccount,
                        Credit=CGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=3,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=3,
                        Debit=CGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                if float(SGSTAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=10,
                        RelatedLedgerID=SalesAccount,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=10,
                        RelatedLedgerID=SalesAccount,
                        Credit=SGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=10,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=10,
                        Debit=SGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                if float(KFCAmount) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=93,
                        RelatedLedgerID=SalesAccount,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=93,
                        RelatedLedgerID=SalesAccount,
                        Credit=KFCAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=93,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=93,
                        Debit=KFCAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

            elif TaxType == 'GST Inter-state B2B' or TaxType == 'GST Inter-state B2C':
                if float(IGSTAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=7,
                        RelatedLedgerID=SalesAccount,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=7,
                        RelatedLedgerID=SalesAccount,
                        Credit=IGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=7,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=7,
                        Debit=IGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

            if not TaxType == 'Export':
                if float(TAX1Amount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=16,
                        RelatedLedgerID=SalesAccount,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=16,
                        RelatedLedgerID=SalesAccount,
                        Credit=TAX1Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=16,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=16,
                        Debit=TAX1Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                if float(TAX2Amount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=19,
                        RelatedLedgerID=SalesAccount,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=19,
                        RelatedLedgerID=SalesAccount,
                        Credit=TAX2Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=19,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=19,
                        Debit=TAX2Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                if float(TAX3Amount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=22,
                        RelatedLedgerID=SalesAccount,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=22,
                        RelatedLedgerID=SalesAccount,
                        Credit=TAX3Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=22,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=22,
                        Debit=TAX3Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

            if float(RoundOff) > 0:

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
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

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
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

            if float(RoundOff) < 0:

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                RoundOff = abs(float(RoundOff))

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
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

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
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

            if float(TotalDiscount) > 0:

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=74,
                    RelatedLedgerID=SalesAccount,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=74,
                    RelatedLedgerID=SalesAccount,
                    Debit=TotalDiscount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=74,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=74,
                    Credit=TotalDiscount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

            # credit sales start here
            if float(CashReceived) == 0 and float(BankAmount) == 0:
                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=LedgerID,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=LedgerID,
                    Credit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=SalesAccount,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=SalesAccount,
                    Debit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

            # credit sales end here

            # customer with cash and customer with partial cash start here
            elif (account_group == 10 or account_group == 29 or account_group == 32) and float(CashReceived) > 0 and float(BankAmount) == 0:
                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=LedgerID,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=LedgerID,
                    Credit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=SalesAccount,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=SalesAccount,
                    Debit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=CashID,
                    RelatedLedgerID=LedgerID,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=CashID,
                    RelatedLedgerID=LedgerID,
                    Debit=CashAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=CashID,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=CashID,
                    Credit=CashAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

            # customer with cash and customer with partial cash end here

            # customer with bank and customer with partial bank start here
            elif (account_group == 10 or account_group == 29 or account_group == 32) and float(CashReceived) == 0 and float(BankAmount) > 0:
                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=LedgerID,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=LedgerID,
                    Credit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=SalesAccount,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=SalesAccount,
                    Debit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=BankID,
                    RelatedLedgerID=LedgerID,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=BankID,
                    RelatedLedgerID=LedgerID,
                    Debit=BankAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=BankID,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=BankID,
                    Credit=BankAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

            # customer with bank and customer with partial bank end here

            # bank with cash and cash with cash start here
            elif (account_group == 8 or account_group == 9) and float(CashReceived) > 0 and float(BankAmount) == 0:
                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=CashID,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=CashID,
                    Credit=CashAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=CashID,
                    RelatedLedgerID=SalesAccount,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=CashID,
                    RelatedLedgerID=SalesAccount,
                    Debit=CashAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                csh_value = float(GrandTotal) - float(CashReceived)
                if float(csh_value) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
                        Debit=csh_value,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
                        Credit=csh_value,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )
            # bank with cash and cash with cash end here

            # bank with bank and cash with bank start here
            elif (account_group == 8 or account_group == 9) and float(CashReceived) == 0 and float(BankAmount) > 0:
                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=BankID,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=BankID,
                    Credit=BankAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=BankID,
                    RelatedLedgerID=SalesAccount,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=BankID,
                    RelatedLedgerID=SalesAccount,
                    Debit=BankAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                bnk_value = float(GrandTotal) - float(BankAmount)
                if not float(bnk_value) == 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=SalesAccount,
                        Debit=bnk_value,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=LedgerID,
                        Credit=bnk_value,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

            # bank with bank and cash with bank end here

            # customer with partial cash /bank and customer with cash/bank
            elif (account_group == 10 or account_group == 29 or account_group == 32) and float(CashReceived) > 0 and float(BankAmount) > 0:
                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=LedgerID,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=LedgerID,
                    Credit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=SalesAccount,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=SalesAccount,
                    Debit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=CashID,
                    RelatedLedgerID=LedgerID,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=CashID,
                    RelatedLedgerID=LedgerID,
                    Debit=CashAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=CashID,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=CashID,
                    Credit=CashAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=BankID,
                    RelatedLedgerID=LedgerID,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=BankID,
                    RelatedLedgerID=LedgerID,
                    Debit=BankAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=BankID,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
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
            # customer with partial cash /bank and customer with cash/bank

            # cash with cash/bank start here
            elif (account_group == 9 or account_group == 8) and float(CashReceived) > 0 and float(BankAmount) > 0:
                if float(Balance) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=CashID,
                        Credit=Balance,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=SalesAccount,
                        RelatedLedgerID=CashID,
                        Credit=Balance,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=SalesAccount,
                        Debit=Balance,
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
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=SalesAccount,
                        Debit=Balance,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=BankID,
                    RelatedLedgerID=SalesAccount,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=BankID,
                    RelatedLedgerID=SalesAccount,
                    Debit=BankAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=BankID,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=BankID,
                    Credit=BankAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=CashID,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=SalesAccount,
                    RelatedLedgerID=CashID,
                    Credit=CashReceived,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=CashID,
                    RelatedLedgerID=SalesAccount,
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
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=CashID,
                    RelatedLedgerID=SalesAccount,
                    Debit=CashReceived,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

            # cash with cash/bank end here
            # new posting ending here

            # deleted_datas = data["deleted_data"]
            # if deleted_datas:
            #     for deleted_Data in deleted_datas:
            #         pk = deleted_Data['unq_id']
            #         SalesDetailsID = deleted_Data['SalesDetailsID']

            #         if not pk == '':
            #             if SalesDetails.objects.filter(pk=pk).exists():
            #                 deleted_detail = SalesDetails.objects.filter(pk=pk)
            #                 deleted_detail.delete()
            #                 stockTrans_instance = None
            #                 if StockTrans.objects.filter(DetailID=SalesDetailsID,BranchID=BranchID,VoucherType=VoucherType,IsActive=True).exists():
            #                     stockTrans_instance = StockTrans.objects.get(DetailID=SalesDetailsID,BranchID=BranchID,VoucherType=VoucherType,IsActive=True)
            #                     qty_in_stockTrans = stockTrans_instance.Qty
            #                     StockRateID = stockTrans_instance.StockRateID
            #                     stockTrans_instance.IsActive = False
            #                     stockTrans_instance.save()

            #                     stockRate_instance = StockRate.objects.get(StockRateID=StockRateID,BranchID=BranchID,WareHouseID=WarehouseID)
            #                     stockRate_instance.Qty = float(stockRate_instance.Qty) - float(qty_in_stockTrans)
            #                     stockRate_instance.save()

            deleted_datas = data["deleted_data"]
            if deleted_datas:
                for deleted_Data in deleted_datas:
                    deleted_pk = deleted_Data['unq_id']
                    SalesDetailsID_Deleted = deleted_Data['SalesDetailsID']
                    ProductID_Deleted = deleted_Data['ProductID']
                    PriceListID_Deleted = deleted_Data['PriceListID']
                    Rate_Deleted = deleted_Data['Rate']
                    SalesMasterID_Deleted = deleted_Data['SalesMasterID']
                    WarehouseID_Deleted = deleted_Data['WarehouseID']

                    if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID_Deleted, DefaultUnit=True).exists():
                        priceList = PriceList.objects.get(
                            CompanyID=CompanyID, ProductID=ProductID_Deleted, DefaultUnit=True)
                        MultiFactor = priceList.MultiFactor
                        Cost = float(Rate_Deleted) / float(MultiFactor)
                        Ct = round(Cost, 4)
                        Cost_Deleted = str(Ct)

                        if not deleted_pk == '' or not deleted_pk == 0:
                            if SalesDetails.objects.filter(CompanyID=CompanyID, pk=deleted_pk).exists():
                                deleted_detail = SalesDetails.objects.filter(
                                    CompanyID=CompanyID, pk=deleted_pk)
                                deleted_detail.delete()

                                # if StockRate.objects.filter(CompanyID=CompanyID,ProductID=ProductID_Deleted,PriceListID=PriceListID_Deleted,WareHouseID=WarehouseID_Deleted).exists():
                                #     stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,ProductID=ProductID_Deleted,PriceListID=PriceListID_Deleted,WareHouseID=WarehouseID_Deleted)
                                #     StockRateID = stockRate_instance.StockRateID
                                #     if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=SalesDetailsID_Deleted,MasterID=SalesMasterID_Deleted,BranchID=BranchID,
                                #         VoucherType=VoucherType,IsActive=True,StockRateID=StockRateID).exists():
                                #         stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID,DetailID=SalesDetailsID_Deleted,MasterID=SalesMasterID_Deleted,BranchID=BranchID,
                                #             VoucherType=VoucherType,IsActive=True,StockRateID=StockRateID)
                                #         qty_in_stockTrans = stockTrans_instance.Qty
                                #         stockRate_instance.Qty = float(stockRate_instance.Qty) + float(qty_in_stockTrans)
                                #         stockRate_instance.save()
                                #         stockTrans_instance.IsActive = False
                                #         stockTrans_instance.save()

                                if StockTrans.objects.filter(CompanyID=CompanyID, DetailID=SalesDetailsID_Deleted, MasterID=SalesMasterID_Deleted, BranchID=BranchID, VoucherType=VoucherType, IsActive=True).exists():
                                    stockTrans_instance = StockTrans.objects.filter(
                                        CompanyID=CompanyID, DetailID=SalesDetailsID_Deleted, MasterID=SalesMasterID_Deleted, BranchID=BranchID, VoucherType=VoucherType, IsActive=True)
                                    for stck in stockTrans_instance:
                                        StockRateID = stck.StockRateID
                                        stck.IsActive = False
                                        qty_in_stockTrans = stck.Qty
                                        if StockRate.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, BranchID=BranchID).exists():
                                            stockRateInstance = StockRate.objects.get(
                                                CompanyID=CompanyID, StockRateID=StockRateID, BranchID=BranchID)
                                            stockRateInstance.Qty = float(
                                                stockRateInstance.Qty) + float(qty_in_stockTrans)
                                            stockRateInstance.save()
                                        stck.save()

            salesdetails = data["SalesDetails"]

            for salesdetail in salesdetails:
                ProductID = salesdetail['ProductID']
                if ProductID:
                    pk = salesdetail['unq_id']
                    detailID = salesdetail['detailID']
                    Qty_detail = salesdetail['Qty']
                    FreeQty = salesdetail['FreeQty']
                    PriceListID = salesdetail['PriceListID']
                    Flavour = salesdetail['Flavour']
                    BatchCode = salesdetail['BatchCode']
                    try:
                        is_inclusive = salesdetail['is_inclusive']
                    except:
                        is_inclusive = False

                    UnitPrice = float(salesdetail['UnitPrice'])
                    InclusivePrice = float(salesdetail['InclusivePrice'])
                    RateWithTax = float(salesdetail['RateWithTax'])
                    CostPerPrice = float(salesdetail['CostPerPrice'])
                    AddlDiscPerc = float(salesdetail['AddlDiscPerc'])
                    AddlDiscAmt = float(salesdetail['AddlDiscAmt'])
                    DiscountPerc = float(salesdetail['DiscountPerc'])
                    DiscountAmount = float(salesdetail['DiscountAmount'])
                    GrossAmount = float(salesdetail['GrossAmount'])
                    TaxableAmount = float(salesdetail['TaxableAmount'])
                    VATPerc = float(salesdetail['VATPerc'])
                    VATAmount = float(salesdetail['VATAmount'])
                    SGSTPerc = float(salesdetail['SGSTPerc'])
                    SGSTAmount = float(salesdetail['SGSTAmount'])
                    CGSTPerc = float(salesdetail['CGSTPerc'])
                    CGSTAmount = float(salesdetail['CGSTAmount'])
                    IGSTPerc = float(salesdetail['IGSTPerc'])
                    IGSTAmount = float(salesdetail['IGSTAmount'])
                    NetAmount = float(salesdetail['NetAmount'])
                    TAX1Perc = float(salesdetail['TAX1Perc'])
                    TAX1Amount = float(salesdetail['TAX1Amount'])
                    TAX2Perc = float(salesdetail['TAX2Perc'])
                    TAX2Amount = float(salesdetail['TAX2Amount'])
                    TAX3Perc = float(salesdetail['TAX3Perc'])
                    TAX3Amount = float(salesdetail['TAX3Amount'])
                    KFCAmount = float(salesdetail['KFCAmount'])

                    try:
                        SerialNos = salesdetail['SerialNos']
                    except:
                        SerialNos = []

                    try:
                        Description = salesdetail['Description']
                    except:
                        Description = ""

                    try:
                        KFCPerc = salesdetail['KFCPerc']
                    except:
                        KFCPerc = 0

                    # UnitPrice = round(UnitPrice, PriceRounding)
                    # InclusivePrice = round(InclusivePrice, PriceRounding)
                    # RateWithTax = round(RateWithTax, PriceRounding)

                    CostPerPrice = PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).PurchasePrice
                    # CostPerPrice = round(CostPerPrice, PriceRounding)

                    # AddlDiscPerc = round(AddlDiscPerc, PriceRounding)

                    # AddlDiscAmt = round(AddlDiscAmt, PriceRounding)
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
                    # TAX1Perc = round(TAX1Perc, PriceRounding)

                    # TAX1Amount = round(TAX1Amount, PriceRounding)
                    # TAX2Perc = round(TAX2Perc, PriceRounding)
                    # TAX2Amount = round(TAX2Amount, PriceRounding)
                    # TAX3Perc = round(TAX3Perc, PriceRounding)
                    # TAX3Amount = round(TAX3Amount, PriceRounding)
                    # KFCAmount = round(KFCAmount, PriceRounding)
                    # KFCPerc = round(KFCPerc, PriceRounding)

                    if is_inclusive == True:
                        Batch_salesPrice = InclusivePrice
                    else:
                        Batch_salesPrice = UnitPrice

                    product_is_Service = Product.objects.get(
                        CompanyID=CompanyID,ProductID=ProductID).is_Service

                    MultiFactor = PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor

                    qty_batch = float(FreeQty) + float(Qty_detail)
                    Qty_batch = float(MultiFactor) * float(qty_batch)
                    if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="SalesPriceUpdate").exists():
                        check_SalesPriceUpdate = GeneralSettings.objects.get(
                            CompanyID=CompanyID, SettingsType="SalesPriceUpdate", BranchID=BranchID).SettingsValue
                        if check_SalesPriceUpdate == "True" or check_SalesPriceUpdate == True:
                            pri_ins = PriceList.objects.get(
                                CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID)
                            pri_ins.SalesPrice = Batch_salesPrice
                            pri_ins.save()

                    product_purchasePrice = PriceList.objects.get(
                        CompanyID=CompanyID, BranchID=BranchID, PriceListID=PriceListID).PurchasePrice
                    check_AllowUpdateBatchPriceInSales = False

                    if product_is_Service == False:
                        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="AllowUpdateBatchPriceInSales").exists():
                            check_AllowUpdateBatchPriceInSales = GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="AllowUpdateBatchPriceInSales").SettingsValue
                        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                            check_EnableProductBatchWise = GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
                            # check_BatchCriteria = "PurchasePriceAndSalesPrice"

                            if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
                                    if check_AllowUpdateBatchPriceInSales == "True" or check_AllowUpdateBatchPriceInSales == True:
                                        batch_ins = Batch.objects.get(
                                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                                        StockOut = batch_ins.StockOut
                                        BatchCode = batch_ins.BatchCode
                                        NewStock = float(
                                            StockOut) + float(Qty_batch)
                                        batch_ins.StockOut = NewStock
                                        batch_ins.SalesPrice = Batch_salesPrice
                                        batch_ins.save()
                                    else:
                                        batch_ins = Batch.objects.get(
                                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                                        StockOut = batch_ins.StockOut
                                        BatchCode = batch_ins.BatchCode
                                        NewStock = float(
                                            StockOut) + float(Qty_batch)
                                        batch_ins.StockOut = NewStock
                                        batch_ins.save()
                                else:
                                    BatchCode = get_auto_AutoBatchCode(
                                        Batch, BranchID, CompanyID)
                                    Batch.objects.create(
                                        CompanyID=CompanyID,
                                        BranchID=BranchID,
                                        BatchCode=BatchCode,
                                        StockOut=Qty_batch,
                                        PurchasePrice=product_purchasePrice,
                                        SalesPrice=Batch_salesPrice,
                                        PriceListID=PriceListID,
                                        ProductID=ProductID,
                                        WareHouseID=WarehouseID,
                                        CreatedDate=today,
                                        UpdatedDate=today,
                                        CreatedUserID=CreatedUserID,
                                    )

                            else:
                                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PriceListID=PriceListID).exists():
                                    batch_ins = Batch.objects.get(
                                        CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PriceListID=PriceListID)
                                    StockOut = batch_ins.StockOut
                                    BatchCode = batch_ins.BatchCode
                                    NewStock = float(
                                        StockOut) + float(Qty_batch)
                                    batch_ins.StockOut = NewStock
                                    batch_ins.save()
                                else:
                                    BatchCode = get_auto_AutoBatchCode(
                                        Batch, BranchID, CompanyID)
                                    Batch.objects.create(
                                        CompanyID=CompanyID,
                                        BranchID=BranchID,
                                        BatchCode=BatchCode,
                                        StockOut=Qty_batch,
                                        PurchasePrice=product_purchasePrice,
                                        SalesPrice=Batch_salesPrice,
                                        PriceListID=PriceListID,
                                        ProductID=ProductID,
                                        WareHouseID=WarehouseID,
                                        CreatedDate=today,
                                        UpdatedDate=today,
                                        CreatedUserID=CreatedUserID,
                                    )

                    # priceList = PriceList.objects.get(CompanyID=CompanyID,PriceListID=PriceListID,BranchID=BranchID)

                    # MultiFactor = PriceList.objects.get(
                    #     CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor
                    PriceListID_DefUnit = PriceList.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

                    # PriceListID_DefUnit = priceList.PriceListID
                    # MultiFactor = priceList.MultiFactor

                    # PurchasePrice = priceList.PurchasePrice
                    # SalesPrice = priceList.SalesPrice

                    qty = float(FreeQty) + float(Qty_detail)

                    Qty = float(MultiFactor) * float(qty)
                    Cost = float(CostPerPrice) / float(MultiFactor)

                    # Qy = round(Qty, 4)
                    # Qty = str(Qy)

                    # Ct = round(Cost, 4)
                    # Cost = str(Ct)

                    princeList_instance = PriceList.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit, BranchID=BranchID)
                    PurchasePrice = princeList_instance.PurchasePrice
                    SalesPrice = princeList_instance.SalesPrice

                    if detailID == 0:

                        salesDetail_instance = SalesDetails.objects.get(
                            CompanyID=CompanyID, pk=pk)
                        SalesDetailsID = salesDetail_instance.SalesDetailsID

                        log_instance = SalesDetails_Log.objects.create(
                            TransactionID=SalesDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesMasterID=SalesMasterID,
                            ProductID=ProductID,
                            Qty=Qty_detail,
                            ReturnQty=Qty_detail,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            InclusivePrice=InclusivePrice,
                            RateWithTax=RateWithTax,
                            CostPerPrice=CostPerPrice,
                            PriceListID=PriceListID,
                            DiscountPerc=DiscountPerc,
                            DiscountAmount=DiscountAmount,
                            AddlDiscPerc=AddlDiscPerc,
                            AddlDiscAmt=AddlDiscAmt,
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
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            Flavour=Flavour,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            KFCAmount=KFCAmount,
                            CompanyID=CompanyID,
                            BatchCode=BatchCode,
                            Description=Description,
                            KFCPerc=KFCPerc
                        )

                        salesDetail_instance.ProductID = ProductID
                        salesDetail_instance.Qty = Qty_detail
                        salesDetail_instance.ReturnQty = Qty_detail
                        salesDetail_instance.FreeQty = FreeQty
                        salesDetail_instance.UnitPrice = UnitPrice
                        salesDetail_instance.InclusivePrice = InclusivePrice
                        salesDetail_instance.RateWithTax = RateWithTax
                        salesDetail_instance.CostPerPrice = CostPerPrice
                        salesDetail_instance.PriceListID = PriceListID
                        salesDetail_instance.DiscountPerc = DiscountPerc
                        salesDetail_instance.DiscountAmount = DiscountAmount
                        salesDetail_instance.AddlDiscPerc = AddlDiscPerc
                        salesDetail_instance.AddlDiscAmt = AddlDiscAmt
                        salesDetail_instance.GrossAmount = GrossAmount
                        salesDetail_instance.TaxableAmount = TaxableAmount
                        salesDetail_instance.VATPerc = VATPerc
                        salesDetail_instance.VATAmount = VATAmount
                        salesDetail_instance.SGSTPerc = SGSTPerc
                        salesDetail_instance.SGSTAmount = SGSTAmount
                        salesDetail_instance.CGSTPerc = CGSTPerc
                        salesDetail_instance.CGSTAmount = CGSTAmount
                        salesDetail_instance.IGSTPerc = IGSTPerc
                        salesDetail_instance.IGSTAmount = IGSTAmount
                        salesDetail_instance.NetAmount = NetAmount
                        salesDetail_instance.CreatedUserID = CreatedUserID
                        salesDetail_instance.UpdatedDate = today
                        salesDetail_instance.Flavour = Flavour
                        salesDetail_instance.Action = Action
                        salesDetail_instance.CreatedDate = today
                        salesDetail_instance.TAX1Perc = TAX1Perc
                        salesDetail_instance.TAX1Amount = TAX1Amount
                        salesDetail_instance.TAX2Perc = TAX2Perc
                        salesDetail_instance.TAX2Amount = TAX2Amount
                        salesDetail_instance.TAX3Perc = TAX3Perc
                        salesDetail_instance.TAX3Amount = TAX3Amount
                        salesDetail_instance.KFCAmount = KFCAmount
                        salesDetail_instance.BatchCode = BatchCode
                        salesDetail_instance.LogID = log_instance.ID
                        salesDetail_instance.Description = Description
                        salesDetail_instance.KFCPerc = KFCPerc

                        salesDetail_instance.save()

                        # StockPostingID = get_auto_stockPostid(
                        #     StockPosting, BranchID, CompanyID)
                        # StockPosting.objects.create(
                        #     StockPostingID=StockPostingID,
                        #     BranchID=BranchID,
                        #     Action=Action,
                        #     Date=Date,
                        #     VoucherMasterID=SalesMasterID,
                        #     VoucherType=VoucherType,
                        #     ProductID=ProductID,
                        #     BatchID=BatchID,
                        #     WareHouseID=WarehouseID,
                        #     QtyOut=Qty,
                        #     Rate=Cost,
                        #     PriceListID=PriceListID_DefUnit,
                        #     IsActive=IsActive,
                        #     CreatedDate=today,
                        #     UpdatedDate=today,
                        #     CreatedUserID=CreatedUserID,
                        #     CompanyID=CompanyID,
                        # )

                        # StockPosting_Log.objects.create(
                        #     TransactionID=StockPostingID,
                        #     BranchID=BranchID,
                        #     Action=Action,
                        #     Date=Date,
                        #     VoucherMasterID=SalesMasterID,
                        #     VoucherType=VoucherType,
                        #     ProductID=ProductID,
                        #     BatchID=BatchID,
                        #     WareHouseID=WarehouseID,
                        #     QtyOut=Qty,
                        #     Rate=Cost,
                        #     PriceListID=PriceListID_DefUnit,
                        #     IsActive=IsActive,
                        #     CreatedDate=today,
                        #     UpdatedDate=today,
                        #     CreatedUserID=CreatedUserID,
                        #     CompanyID=CompanyID,
                        # )

                    if detailID == 1:

                        Action = "A"

                        SalesDetailsID = get_auto_id(
                            SalesDetails, BranchID, CompanyID)

                        log_instance = SalesDetails_Log.objects.create(
                            TransactionID=SalesDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesMasterID=SalesMasterID,
                            ProductID=ProductID,
                            Qty=Qty_detail,
                            ReturnQty=Qty_detail,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            InclusivePrice=InclusivePrice,
                            RateWithTax=RateWithTax,
                            CostPerPrice=CostPerPrice,
                            PriceListID=PriceListID,
                            DiscountPerc=DiscountPerc,
                            DiscountAmount=DiscountAmount,
                            AddlDiscPerc=AddlDiscPerc,
                            AddlDiscAmt=AddlDiscAmt,
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
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            Flavour=Flavour,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            KFCAmount=KFCAmount,
                            CompanyID=CompanyID,
                            Description=Description,
                            KFCPerc=KFCPerc
                        )

                        SalesDetails.objects.create(
                            SalesDetailsID=SalesDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            SalesMasterID=SalesMasterID,
                            ProductID=ProductID,
                            Qty=Qty_detail,
                            ReturnQty=Qty_detail,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            InclusivePrice=InclusivePrice,
                            RateWithTax=RateWithTax,
                            CostPerPrice=CostPerPrice,
                            PriceListID=PriceListID,
                            DiscountPerc=DiscountPerc,
                            DiscountAmount=DiscountAmount,
                            AddlDiscPerc=AddlDiscPerc,
                            AddlDiscAmt=AddlDiscAmt,
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
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            Flavour=Flavour,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            KFCAmount=KFCAmount,
                            CompanyID=CompanyID,
                            LogID=log_instance.ID,
                            Description=Description,
                            KFCPerc=KFCPerc
                        )

                        # StockPostingID = get_auto_stockPostid(
                        #     StockPosting, BranchID, CompanyID)
                        # StockPosting.objects.create(
                        #     StockPostingID=StockPostingID,
                        #     BranchID=BranchID,
                        #     Action=Action,
                        #     Date=Date,
                        #     VoucherMasterID=SalesMasterID,
                        #     VoucherType=VoucherType,
                        #     ProductID=ProductID,
                        #     BatchID=BatchID,
                        #     WareHouseID=WarehouseID,
                        #     QtyOut=Qty,
                        #     Rate=Cost,
                        #     PriceListID=PriceListID_DefUnit,
                        #     IsActive=IsActive,
                        #     CreatedDate=today,
                        #     UpdatedDate=today,
                        #     CreatedUserID=CreatedUserID,
                        #     CompanyID=CompanyID,
                        # )

                        # StockPosting_Log.objects.create(
                        #     TransactionID=StockPostingID,
                        #     BranchID=BranchID,
                        #     Action=Action,
                        #     Date=Date,
                        #     VoucherMasterID=SalesMasterID,
                        #     VoucherType=VoucherType,
                        #     ProductID=ProductID,
                        #     BatchID=BatchID,
                        #     WareHouseID=WarehouseID,
                        #     QtyOut=Qty,
                        #     Rate=Cost,
                        #     PriceListID=PriceListID_DefUnit,
                        #     IsActive=IsActive,
                        #     CreatedDate=today,
                        #     UpdatedDate=today,
                        #     CreatedUserID=CreatedUserID,
                        #     CompanyID=CompanyID,
                        # )

                    if SerialNos:
                        for sn in SerialNos:
                            try:
                                SerialNo = sn['SerialNo']
                            except:
                                SerialNo = ""
                            try:
                                ItemCode = sn['ItemCode']
                            except:
                                ItemCode = ""

                            SerialNumbers.objects.create(
                                CompanyID=CompanyID,
                                VoucherType="SI",
                                SerialNo=SerialNo,
                                ItemCode=ItemCode,
                                SalesMasterID=SalesMasterID,
                                SalesDetailsID=SalesDetailsID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                            )
                    if product_is_Service == False:
                        changQty = Qty
                        if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID_DefUnit).exists():
                            if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID, Qty__gt=0, PriceListID=PriceListID_DefUnit).exists():
                                stockRate_instances = StockRate.objects.filter(
                                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID, Qty__gt=0, PriceListID=PriceListID_DefUnit)
                                count = stockRate_instances.count()
                                last = 0
                                for stockRate_instance in stockRate_instances:
                                    last = float(last) + float(1)
                                    StockRateID = stockRate_instance.StockRateID
                                    stock_post_cost = stockRate_instance.Cost
                                    if float(stockRate_instance.Qty) > float(changQty):
                                        # stockRate_instance.Qty = float(
                                        #     stockRate_instance.Qty) - float(changQty)
                                        # changQty = float(stockRate_instance.Qty) - float(changQty)
                                        lastQty = float(
                                            stockRate_instance.Qty) - float(changQty)
                                        chqy = changQty
                                        changQty = 0
                                        stockRate_instance.Qty = lastQty
                                        stockRate_instance.save()

                                        if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                       VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit).exists():
                                            stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                                          VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit)
                                            QtyOut = stockPost_instance.QtyOut
                                            newQty = float(
                                                QtyOut) + float(chqy)

                                            stockPost_instance.QtyOut = newQty
                                            stockPost_instance.save()
                                        else:
                                            StockPostingID = get_auto_stockPostid(
                                                StockPosting, BranchID, CompanyID)
                                            StockPosting.objects.create(
                                                StockPostingID=StockPostingID,
                                                BranchID=BranchID,
                                                Action=Action,
                                                Date=Date,
                                                VoucherMasterID=SalesMasterID,
                                                VoucherType=VoucherType,
                                                ProductID=ProductID,
                                                BatchID=BatchID,
                                                WareHouseID=WarehouseID,
                                                QtyOut=chqy,
                                                Rate=stock_post_cost,
                                                PriceListID=PriceListID_DefUnit,
                                                IsActive=IsActive,
                                                CreatedDate=today,
                                                UpdatedDate=today,
                                                CreatedUserID=CreatedUserID,
                                                CompanyID=CompanyID,
                                            )

                                            StockPosting_Log.objects.create(
                                                TransactionID=StockPostingID,
                                                BranchID=BranchID,
                                                Action=Action,
                                                Date=Date,
                                                VoucherMasterID=SalesMasterID,
                                                VoucherType=VoucherType,
                                                ProductID=ProductID,
                                                BatchID=BatchID,
                                                WareHouseID=WarehouseID,
                                                QtyOut=chqy,
                                                Rate=stock_post_cost,
                                                PriceListID=PriceListID_DefUnit,
                                                IsActive=IsActive,
                                                CreatedDate=today,
                                                UpdatedDate=today,
                                                CreatedUserID=CreatedUserID,
                                                CompanyID=CompanyID,
                                            )

                                        if StockTrans.objects.filter(StockRateID=StockRateID, DetailID=SalesDetailsID, MasterID=SalesMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                                            stockTra_in = StockTrans.objects.filter(
                                                StockRateID=StockRateID, DetailID=SalesDetailsID, MasterID=SalesMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                                            stockTra_in.Qty = float(
                                                stockTra_in.Qty) + float(chqy)
                                            stockTra_in.save()
                                        else:
                                            StockTransID = get_auto_StockTransID(
                                                StockTrans, BranchID, CompanyID)
                                            StockTrans.objects.create(
                                                StockTransID=StockTransID,
                                                BranchID=BranchID,
                                                VoucherType=VoucherType,
                                                StockRateID=StockRateID,
                                                DetailID=SalesDetailsID,
                                                MasterID=SalesMasterID,
                                                Qty=chqy,
                                                IsActive=IsActive,
                                                CompanyID=CompanyID,
                                            )
                                        break
                                    elif float(stockRate_instance.Qty) < float(changQty):
                                        if float(changQty) > float(stockRate_instance.Qty):
                                            changQty = float(changQty) - \
                                                float(stockRate_instance.Qty)
                                            stckQty = stockRate_instance.Qty
                                            stockRate_instance.Qty = 0
                                            stockRate_instance.save()

                                            if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                           VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit).exists():
                                                stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                                              VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit)
                                                QtyOut = stockPost_instance.QtyOut
                                                newQty = float(QtyOut) + \
                                                    float(stckQty)
                                                stockPost_instance.QtyOut = newQty
                                                stockPost_instance.save()
                                            else:
                                                StockPostingID = get_auto_stockPostid(
                                                    StockPosting, BranchID, CompanyID)
                                                StockPosting.objects.create(
                                                    StockPostingID=StockPostingID,
                                                    BranchID=BranchID,
                                                    Action=Action,
                                                    Date=Date,
                                                    VoucherMasterID=SalesMasterID,
                                                    VoucherType=VoucherType,
                                                    ProductID=ProductID,
                                                    BatchID=BatchID,
                                                    WareHouseID=WarehouseID,
                                                    QtyOut=stckQty,
                                                    Rate=stock_post_cost,
                                                    PriceListID=PriceListID_DefUnit,
                                                    IsActive=IsActive,
                                                    CreatedDate=today,
                                                    UpdatedDate=today,
                                                    CreatedUserID=CreatedUserID,
                                                    CompanyID=CompanyID,
                                                )

                                                StockPosting_Log.objects.create(
                                                    TransactionID=StockPostingID,
                                                    BranchID=BranchID,
                                                    Action=Action,
                                                    Date=Date,
                                                    VoucherMasterID=SalesMasterID,
                                                    VoucherType=VoucherType,
                                                    ProductID=ProductID,
                                                    BatchID=BatchID,
                                                    WareHouseID=WarehouseID,
                                                    QtyOut=stckQty,
                                                    Rate=stock_post_cost,
                                                    PriceListID=PriceListID_DefUnit,
                                                    IsActive=IsActive,
                                                    CreatedDate=today,
                                                    UpdatedDate=today,
                                                    CreatedUserID=CreatedUserID,
                                                    CompanyID=CompanyID,
                                                )
                                            if StockTrans.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, DetailID=SalesDetailsID, MasterID=SalesMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                                                stockTra_in = StockTrans.objects.filter(
                                                    CompanyID=CompanyID, StockRateID=StockRateID, DetailID=SalesDetailsID, MasterID=SalesMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                                                stockTra_in.Qty = float(
                                                    stockTra_in.Qty) + float(stckQty)
                                                stockTra_in.save()
                                            else:
                                                StockTransID = get_auto_StockTransID(
                                                    StockTrans, BranchID, CompanyID)
                                                StockTrans.objects.create(
                                                    StockTransID=StockTransID,
                                                    BranchID=BranchID,
                                                    VoucherType=VoucherType,
                                                    StockRateID=StockRateID,
                                                    DetailID=SalesDetailsID,
                                                    MasterID=SalesMasterID,
                                                    Qty=stckQty,
                                                    IsActive=IsActive,
                                                    CompanyID=CompanyID,
                                                )
                                        else:
                                            if changQty < 0:
                                                changQty = 0
                                            # chqty = changQty
                                            changQty = float(
                                                stockRate_instance.Qty) - float(changQty)
                                            chqty = changQty
                                            stockRate_instance.Qty = changQty
                                            changQty = 0
                                            stockRate_instance.save()

                                            if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                           VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit).exists():
                                                stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                                              VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit)
                                                QtyOut = stockPost_instance.QtyOut
                                                newQty = float(
                                                    QtyOut) + float(chqty)
                                                stockPost_instance.QtyOut = newQty
                                                stockPost_instance.save()
                                            else:
                                                StockPostingID = get_auto_stockPostid(
                                                    StockPosting, BranchID, CompanyID)
                                                StockPosting.objects.create(
                                                    StockPostingID=StockPostingID,
                                                    BranchID=BranchID,
                                                    Action=Action,
                                                    Date=Date,
                                                    VoucherMasterID=SalesMasterID,
                                                    VoucherType=VoucherType,
                                                    ProductID=ProductID,
                                                    BatchID=BatchID,
                                                    WareHouseID=WarehouseID,
                                                    QtyOut=chqty,
                                                    Rate=stock_post_cost,
                                                    PriceListID=PriceListID_DefUnit,
                                                    IsActive=IsActive,
                                                    CreatedDate=today,
                                                    UpdatedDate=today,
                                                    CreatedUserID=CreatedUserID,
                                                    CompanyID=CompanyID,
                                                )

                                                StockPosting_Log.objects.create(
                                                    TransactionID=StockPostingID,
                                                    BranchID=BranchID,
                                                    Action=Action,
                                                    Date=Date,
                                                    VoucherMasterID=SalesMasterID,
                                                    VoucherType=VoucherType,
                                                    ProductID=ProductID,
                                                    BatchID=BatchID,
                                                    WareHouseID=WarehouseID,
                                                    QtyOut=chqty,
                                                    Rate=stock_post_cost,
                                                    PriceListID=PriceListID_DefUnit,
                                                    IsActive=IsActive,
                                                    CreatedDate=today,
                                                    UpdatedDate=today,
                                                    CreatedUserID=CreatedUserID,
                                                    CompanyID=CompanyID,
                                                )

                                            if StockTrans.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, DetailID=SalesDetailsID, MasterID=SalesMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                                                stockTra_in = StockTrans.objects.filter(
                                                    CompanyID=CompanyID, StockRateID=StockRateID, DetailID=SalesDetailsID, MasterID=SalesMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                                                stockTra_in.Qty = float(
                                                    stockTra_in.Qty) + float(chqty)
                                                stockTra_in.save()
                                            else:
                                                StockTransID = get_auto_StockTransID(
                                                    StockTrans, BranchID, CompanyID)
                                                StockTrans.objects.create(
                                                    StockTransID=StockTransID,
                                                    BranchID=BranchID,
                                                    VoucherType=VoucherType,
                                                    StockRateID=StockRateID,
                                                    DetailID=SalesDetailsID,
                                                    MasterID=SalesMasterID,
                                                    Qty=chqty,
                                                    IsActive=IsActive,
                                                    CompanyID=CompanyID,
                                                )

                                    elif float(stockRate_instance.Qty) == float(changQty):
                                        chty = stockRate_instance.Qty
                                        stockRate_instance.Qty = 0
                                        changQty = 0
                                        stockRate_instance.save()

                                        if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                       VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit).exists():
                                            stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                                          VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit)
                                            QtyOut = stockPost_instance.QtyOut
                                            newQty = float(QtyOut) + \
                                                float(chty)
                                            stockPost_instance.QtyOut = newQty
                                            stockPost_instance.save()
                                        else:
                                            StockPostingID = get_auto_stockPostid(
                                                StockPosting, BranchID, CompanyID)
                                            StockPosting.objects.create(
                                                StockPostingID=StockPostingID,
                                                BranchID=BranchID,
                                                Action=Action,
                                                Date=Date,
                                                VoucherMasterID=SalesMasterID,
                                                VoucherType=VoucherType,
                                                ProductID=ProductID,
                                                BatchID=BatchID,
                                                WareHouseID=WarehouseID,
                                                QtyOut=chty,
                                                Rate=stock_post_cost,
                                                PriceListID=PriceListID_DefUnit,
                                                IsActive=IsActive,
                                                CreatedDate=today,
                                                UpdatedDate=today,
                                                CreatedUserID=CreatedUserID,
                                                CompanyID=CompanyID,
                                            )

                                            StockPosting_Log.objects.create(
                                                TransactionID=StockPostingID,
                                                BranchID=BranchID,
                                                Action=Action,
                                                Date=Date,
                                                VoucherMasterID=SalesMasterID,
                                                VoucherType=VoucherType,
                                                ProductID=ProductID,
                                                BatchID=BatchID,
                                                WareHouseID=WarehouseID,
                                                QtyOut=chty,
                                                Rate=stock_post_cost,
                                                PriceListID=PriceListID_DefUnit,
                                                IsActive=IsActive,
                                                CreatedDate=today,
                                                UpdatedDate=today,
                                                CreatedUserID=CreatedUserID,
                                                CompanyID=CompanyID,
                                            )

                                        if StockTrans.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, DetailID=SalesDetailsID, MasterID=SalesMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                                            stockTra_in = StockTrans.objects.filter(
                                                CompanyID=CompanyID, StockRateID=StockRateID, DetailID=SalesDetailsID, MasterID=SalesMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                                            stockTra_in.Qty = float(
                                                stockTra_in.Qty) + float(chty)
                                            stockTra_in.save()
                                        else:
                                            StockTransID = get_auto_StockTransID(
                                                StockTrans, BranchID, CompanyID)
                                            StockTrans.objects.create(
                                                StockTransID=StockTransID,
                                                BranchID=BranchID,
                                                VoucherType=VoucherType,
                                                StockRateID=StockRateID,
                                                DetailID=SalesDetailsID,
                                                MasterID=SalesMasterID,
                                                Qty=chty,
                                                IsActive=IsActive,
                                                CompanyID=CompanyID,
                                            )
                                        break

                            if float(changQty) > 0:
                                if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID, Qty__lte=0, PriceListID=PriceListID_DefUnit).exists():
                                    stockRate_instance = StockRate.objects.filter(
                                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID, Qty__lte=0, PriceListID=PriceListID_DefUnit).first()
                                    stock_post_cost = stockRate_instance.Cost
                                    if float(changQty) > 0:
                                        stockRate_instance.Qty = float(
                                            stockRate_instance.Qty) - float(changQty)
                                        stockRate_instance.save()

                                        if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                       VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit).exists():
                                            stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                                          VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit)
                                            QtyOut = stockPost_instance.QtyOut
                                            newQty = float(
                                                QtyOut) + float(changQty)
                                            stockPost_instance.QtyOut = newQty
                                            stockPost_instance.save()
                                        else:
                                            StockPostingID = get_auto_stockPostid(
                                                StockPosting, BranchID, CompanyID)
                                            StockPosting.objects.create(
                                                StockPostingID=StockPostingID,
                                                BranchID=BranchID,
                                                Action=Action,
                                                Date=Date,
                                                VoucherMasterID=SalesMasterID,
                                                VoucherType=VoucherType,
                                                ProductID=ProductID,
                                                BatchID=BatchID,
                                                WareHouseID=WarehouseID,
                                                QtyOut=changQty,
                                                Rate=stock_post_cost,
                                                PriceListID=PriceListID_DefUnit,
                                                IsActive=IsActive,
                                                CreatedDate=today,
                                                UpdatedDate=today,
                                                CreatedUserID=CreatedUserID,
                                                CompanyID=CompanyID,
                                            )

                                            StockPosting_Log.objects.create(
                                                TransactionID=StockPostingID,
                                                BranchID=BranchID,
                                                Action=Action,
                                                Date=Date,
                                                VoucherMasterID=SalesMasterID,
                                                VoucherType=VoucherType,
                                                ProductID=ProductID,
                                                BatchID=BatchID,
                                                WareHouseID=WarehouseID,
                                                QtyOut=changQty,
                                                Rate=stock_post_cost,
                                                PriceListID=PriceListID_DefUnit,
                                                IsActive=IsActive,
                                                CreatedDate=today,
                                                UpdatedDate=today,
                                                CreatedUserID=CreatedUserID,
                                                CompanyID=CompanyID,
                                            )

                                        if not StockTrans.objects.filter(CompanyID=CompanyID,
                                                                         StockRateID=stockRate_instance.StockRateID,
                                                                         DetailID=SalesDetailsID,
                                                                         MasterID=SalesMasterID,
                                                                         VoucherType=VoucherType,
                                                                         BranchID=BranchID).exists():

                                            StockTransID = get_auto_StockTransID(
                                                StockTrans, BranchID, CompanyID)
                                            StockTrans.objects.create(
                                                CompanyID=CompanyID,
                                                StockTransID=StockTransID,
                                                BranchID=BranchID,
                                                VoucherType=VoucherType,
                                                StockRateID=stockRate_instance.StockRateID,
                                                DetailID=SalesDetailsID,
                                                MasterID=SalesMasterID,
                                                Qty=changQty,
                                                IsActive=IsActive
                                            )
                        else:
                            # if float(changQty) > 0:
                            #     qty = float(Qty) * -1
                            StockRateID = get_auto_StockRateID(
                                StockRate, BranchID, CompanyID)
                            StockRate.objects.create(
                                StockRateID=StockRateID,
                                BranchID=BranchID,
                                BatchID=BatchID,
                                PurchasePrice=PurchasePrice,
                                SalesPrice=SalesPrice,
                                Qty=qty,
                                Cost=Cost,
                                ProductID=ProductID,
                                WareHouseID=WarehouseID,
                                Date=Date,
                                PriceListID=PriceListID_DefUnit,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CompanyID=CompanyID,
                            )

                            StockPostingID = get_auto_stockPostid(
                                StockPosting, BranchID, CompanyID)
                            StockPosting.objects.create(
                                StockPostingID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=Date,
                                VoucherMasterID=SalesMasterID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchID,
                                WareHouseID=WarehouseID,
                                QtyOut=Qty,
                                Rate=Cost,
                                PriceListID=PriceListID_DefUnit,
                                IsActive=IsActive,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )

                            StockPosting_Log.objects.create(
                                TransactionID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=Date,
                                VoucherMasterID=SalesMasterID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchID,
                                WareHouseID=WarehouseID,
                                QtyOut=Qty,
                                Rate=Cost,
                                PriceListID=PriceListID_DefUnit,
                                IsActive=IsActive,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )
                            StockTransID = get_auto_StockTransID(
                                StockTrans, BranchID, CompanyID)
                            StockTrans.objects.create(
                                StockTransID=StockTransID,
                                BranchID=BranchID,
                                VoucherType=VoucherType,
                                StockRateID=StockRateID,
                                DetailID=SalesDetailsID,
                                MasterID=SalesMasterID,
                                Qty=Qty,
                                IsActive=IsActive,
                                CompanyID=CompanyID,
                            )
                # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sales Invoice',
            #              'Edit', 'Sales Invoice Updated successfully.', 'Sales Invoice Updated successfully.')

            response_data = {
                "StatusCode": 6000,
                "message": "Sales Updated Successfully!!!",
            }

            return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again"
        }

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Sales',
                     'Edit', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def list_salesMaster(request):
    data = request.data
    CompanyID = data['CompanyID']
    PriceRounding = data['PriceRounding']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():

            instances = SalesMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

            serialized = SalesMasterRestSerializer(instances, many=True, context={"CompanyID": CompanyID,
                                                                                  "PriceRounding": PriceRounding})

            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sales Invoice', 'List',
            #              'Sales Invoice List Viewed successfully.', 'Sales Invoice List Viewed successfully.')

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Sales Invoice',
            #              'List', 'Sales Invoice List Viewed Failed.', 'Sales Invoice not found in this branch')
            response_data = {
                "StatusCode": 6001,
                "message": "Sales Master not found in this branch."
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch you enterd is not valid."
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def sale_pagination(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']

    page_number = data['page_no']
    items_per_page = data['items_per_page']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']

        if page_number and items_per_page:
            sale_object = SalesMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

            sale_sort_pagination = list_pagination(
                sale_object,
                items_per_page,
                page_number
            )
            sale_serializer = SalesMasterRest1Serializer(
                sale_sort_pagination,
                many=True,
                context={"request": request, "CompanyID": CompanyID,
                         "PriceRounding": PriceRounding}
            )
            data = sale_serializer.data
            if not data == None:
                response_data = {
                    "StatusCode": 6000,
                    "data": data,
                    "count": len(sale_object)
                }
            else:
                response_data = {
                    "StatusCode": 6001
                }

            return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def salesMaster(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    instance = None
    if SalesMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = SalesMaster.objects.get(CompanyID=CompanyID, pk=pk)
        serialized = SalesMasterRestSerializer(
            instance, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding, })

        # request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sales Invoice', 'View',
        #              'Sales Invoice Single Viewed successfully.', 'Sales Invoice Single Viewed successfully.')
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Sales Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def salesInvoice_for_SalesReturn(request):
    data = request.data
    CompanyID = data['CompanyID']
    PriceRounding = data['PriceRounding']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    VoucherNo = data['VoucherNo']
    if SalesMaster.objects.filter(CompanyID=CompanyID, VoucherNo=VoucherNo, BranchID=BranchID).exists():
        instance = SalesMaster.objects.get(
            CompanyID=CompanyID, VoucherNo=VoucherNo, BranchID=BranchID)
        serialized = SalesMasterForReturnSerializer(instance, context={"CompanyID": CompanyID,
                                                                       "PriceRounding": PriceRounding})

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Sales Invoice Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def salesInvoice_for_SalesEstimate(request):
    data = request.data
    CompanyID = data['CompanyID']
    PriceRounding = data['PriceRounding']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    VoucherNo = data['VoucherNo']
    if SalesEstimateMaster.objects.filter(CompanyID=CompanyID, VoucherNo=VoucherNo, BranchID=BranchID).exists():
        instance = SalesEstimateMaster.objects.get(
            CompanyID=CompanyID, VoucherNo=VoucherNo, BranchID=BranchID)
        serialized = SalesEstimateForOrderSerializer(instance, context={"CompanyID": CompanyID,
                                                                        "PriceRounding": PriceRounding})

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Sales Estimate Invoice Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_salesMaster(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if SalesMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = SalesMaster.objects.get(pk=pk)
        SalesMasterID = instance.SalesMasterID
        LoyaltyCustomerID = instance.LoyaltyCustomerID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        Date = instance.Date
        CreditPeriod = instance.CreditPeriod
        LedgerID = instance.LedgerID
        PriceCategoryID = instance.PriceCategoryID
        EmployeeID = instance.EmployeeID
        SalesAccount = instance.SalesAccount
        CustomerName = instance.CustomerName
        Address1 = instance.Address1
        Address2 = instance.Address2
        Address3 = instance.Address3
        Notes = instance.Notes
        FinacialYearID = instance.FinacialYearID
        TotalGrossAmt = instance.TotalGrossAmt
        AddlDiscPercent = instance.AddlDiscPercent
        AddlDiscAmt = instance.AddlDiscAmt
        TotalDiscount = instance.TotalDiscount
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
        CardTypeID = instance.CardTypeID
        CardNumber = instance.CardNumber
        IsActive = instance.IsActive
        IsPosted = instance.IsPosted
        SalesType = instance.SalesType
        TaxID = instance.TaxID
        TaxType = instance.TaxType
        BillDiscPercent = instance.BillDiscPercent
        BillDiscAmt = instance.BillDiscAmt
        VATAmount = instance.VATAmount
        SGSTAmount = instance.SGSTAmount
        CGSTAmount = instance.CGSTAmount
        IGSTAmount = instance.IGSTAmount
        TAX1Amount = instance.TAX1Amount
        TAX2Amount = instance.TAX2Amount
        TAX3Amount = instance.TAX3Amount
        Balance = instance.Balance
        TransactionTypeID = instance.TransactionTypeID
        CashID = instance.CashID
        BankID = instance.BankID
        KFCAmount = instance.KFCAmount

        Action = "D"

        SalesMaster_Log.objects.create(
            TransactionID=SalesMasterID,
            LoyaltyCustomerID=LoyaltyCustomerID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            Date=Date,
            CreditPeriod=CreditPeriod,
            LedgerID=LedgerID,
            PriceCategoryID=PriceCategoryID,
            EmployeeID=EmployeeID,
            SalesAccount=SalesAccount,
            CustomerName=CustomerName,
            Address1=Address1,
            Address2=Address2,
            Address3=Address3,
            Notes=Notes,
            FinacialYearID=FinacialYearID,
            TotalGrossAmt=TotalGrossAmt,
            AddlDiscPercent=AddlDiscPercent,
            AddlDiscAmt=AddlDiscAmt,
            TotalDiscount=TotalDiscount,
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
            CardTypeID=CardTypeID,
            CardNumber=CardNumber,
            IsActive=IsActive,
            IsPosted=IsPosted,
            SalesType=SalesType,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            TaxID=TaxID,
            TaxType=TaxType,
            BillDiscPercent=BillDiscPercent,
            BillDiscAmt=BillDiscAmt,
            VATAmount=VATAmount,
            SGSTAmount=SGSTAmount,
            CGSTAmount=CGSTAmount,
            IGSTAmount=IGSTAmount,
            TAX1Amount=TAX1Amount,
            TAX2Amount=TAX2Amount,
            TAX3Amount=TAX3Amount,
            Balance=Balance,
            TransactionTypeID=TransactionTypeID,
            CompanyID=CompanyID,
            Action=Action,
            CashID=CashID,
            BankID=BankID,
            KFCAmount=KFCAmount,
        )

        if LedgerPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=SalesMasterID, BranchID=BranchID, VoucherType="SI").exists():

            ledgerPostInstances = LedgerPosting.objects.filter(
                CompanyID=CompanyID, VoucherMasterID=SalesMasterID, BranchID=BranchID, VoucherType="SI")

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
                    VoucherMasterID=SalesMasterID,
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

        if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=SalesMasterID, BranchID=BranchID, VoucherType="SI").exists():

            stockPostingInstances = StockPosting.objects.filter(
                CompanyID=CompanyID, VoucherMasterID=SalesMasterID, BranchID=BranchID, VoucherType="SI")

            for stockPostingInstance in stockPostingInstances:

                StockPostingID = stockPostingInstance.StockPostingID
                BranchID = stockPostingInstance.BranchID
                Date = stockPostingInstance.Date
                VoucherMasterID = stockPostingInstance.VoucherMasterID
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
                    VoucherMasterID=SalesMasterID,
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

        detail_instances = SalesDetails.objects.filter(
            CompanyID=CompanyID, SalesMasterID=SalesMasterID, BranchID=BranchID)

        for detail_instance in detail_instances:

            SalesDetailsID = detail_instance.SalesDetailsID
            BranchID = detail_instance.BranchID
            SalesMasterID = detail_instance.SalesMasterID
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
            AddlDiscPerc = detail_instance.AddlDiscPerc
            AddlDiscAmt = detail_instance.AddlDiscAmt
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
            TAX1Perc = detail_instance.TAX1Perc
            TAX1Amount = detail_instance.TAX1Amount
            TAX2Perc = detail_instance.TAX2Perc
            TAX2Amount = detail_instance.TAX2Amount
            TAX3Perc = detail_instance.TAX3Perc
            TAX3Amount = detail_instance.TAX3Amount
            BatchCode = detail_instance.BatchCode
            Description = detail_instance.Description
            KFCAmount = detail_instance.KFCAmount
            KFCPerc = detail_instance.KFCPerc

            if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
                batch_ins = Batch.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                StockOut = batch_ins.StockOut
                batch_ins.StockOut = float(StockOut) - float(Qty)
                batch_ins.save()

            if SerialNumbers.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SalesMasterID=SalesMasterID, SalesDetailsID=SalesDetailsID, VoucherType="SI").exists():
                serial_instances = SerialNumbers.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, SalesMasterID=SalesMasterID, SalesDetailsID=SalesDetailsID, VoucherType="SI")
                for sir in serial_instances:
                    sir.delete()

            SalesDetails_Log.objects.create(
                TransactionID=SalesDetailsID,
                BranchID=BranchID,
                Action=Action,
                SalesMasterID=SalesMasterID,
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
                AddlDiscPerc=AddlDiscPerc,
                AddlDiscAmt=AddlDiscAmt,
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
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Flavour=Flavour,
                TAX1Perc=TAX1Perc,
                TAX1Amount=TAX1Amount,
                TAX2Perc=TAX2Perc,
                TAX2Amount=TAX2Amount,
                TAX3Perc=TAX3Perc,
                TAX3Amount=TAX3Amount,
                CompanyID=CompanyID,
                BatchCode=BatchCode,
                Description=Description,
                KFCAmount=KFCAmount,
                KFCPerc=KFCPerc,
            )
            # =========Loyalty Point ==========
            tot_Points = 0
            if LoyaltyPoint.objects.filter(LoyaltyCustomerID=LoyaltyCustomerID, VoucherMasterID=SalesMasterID, VoucherType="SI", BranchID=BranchID, CompanyID=CompanyID).exists():
                instances = LoyaltyPoint.objects.filter(
                    LoyaltyCustomerID=LoyaltyCustomerID, VoucherMasterID=SalesMasterID, VoucherType="SI", BranchID=BranchID, CompanyID=CompanyID)
                for i in instances:
                    if i.is_Radeem == False:
                        tot_Points += float(i.Point)
                    print(i.Point, "TRRRRRRRRRRRRRRRRRRRRRRRREEEEEEEEEEEEEEEEEEEE")
                    i.delete()
                instances1 = LoyaltyPoint.objects.filter(
                    LoyaltyCustomerID=LoyaltyCustomerID, VoucherMasterID=SalesMasterID, VoucherType="SI", BranchID=BranchID, CompanyID=CompanyID, is_Radeem=False)
                # for i in instances1:
                #     i.Point =+ tot_Points
                #     if tot_Points == 0:
                #         break
                #     i.save()
            # =========Loyalty Point ==========

            if StockTrans.objects.filter(CompanyID=CompanyID, DetailID=SalesDetailsID, MasterID=SalesMasterID, BranchID=BranchID, VoucherType="SI", IsActive=True).exists():
                stockTrans_instances = StockTrans.objects.filter(
                    CompanyID=CompanyID, DetailID=SalesDetailsID, MasterID=SalesMasterID, BranchID=BranchID, VoucherType="SI", IsActive=True)

                for i in stockTrans_instances:
                    stockRateID = i.StockRateID
                    i.IsActive = False
                    i.save()

                    stockRate_instance = StockRate.objects.get(
                        CompanyID=CompanyID, StockRateID=stockRateID, BranchID=BranchID)
                    stockRate_instance.Qty = float(
                        stockRate_instance.Qty) + float(i.Qty)
                    stockRate_instance.save()

            detail_instance.delete()
        instance.delete()

        # request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sales Invoice',
                     'Deleted', 'Sales Invoice Deleted successfully.', 'Sales Invoice Deleted successfully')

        response_data = {
            "StatusCode": 6000,
            "title": "Success",
            "message": "Sales Master Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "title": "Failed",
            "message": "Sales Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def gst_sales_report(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    UserID = data['UserID']
    PriceRounding = data['PriceRounding']
    serialized1 = ListSerializerforReport(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']

        Total_TaxableValue = 0
        Total_TotalQty = 0

        Total_TotalTaxableAmount = 0
        Total_TotalTax = 0
        Total_SGSTAmount = 0
        Total_CGSTAmount = 0
        Total_IGSTAmount = 0
        Total_KFCAmount = 0
        print(UserID, "UserIDUserIDUserIDUserIDUserID")

        TaxType_Arr = ["GST Intra-state B2C","Export","GST Inter-state B2B","GST Intra-state B2C","GST Intra-state B2B","GST"]

        if UserID:
            UserID = UserTable.objects.get(id=UserID).customer.user.pk
            if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID,TaxType__in=TaxType_Arr).exists():
                instances = SalesMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID,TaxType__in=TaxType_Arr)
                return_instances = SalesReturnMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, CreatedUserID=UserID,TaxType__in=TaxType_Arr)
                serialized_sales = SalesGSTReportSerializer(instances, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
                                                                                           "FromDate": FromDate, "ToDate": ToDate})

                serialized_return = SalesReturnMasterRestSerializer(return_instances, many=True, context={"CompanyID": CompanyID,
                                                                                                          "PriceRounding": PriceRounding})

                sales_data = serialized_sales.data
                sales_return_data = serialized_return.data

                final_array = []
                # =======

                orderdDict = sales_data
                return_orderdDict = sales_return_data

                jsnDatas = convertOrderdDict(orderdDict)
                return_jsnDatas = convertOrderdDict(return_orderdDict)

                party_gstin = ""
                for i in jsnDatas:
                    LedgerID = i['LedgerID']
                    if AccountLedger.objects.filter(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID).exists():
                        Particulars = AccountLedger.objects.get(
                            LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID)
                        LedgerName = Particulars.LedgerName
                        if Particulars.AccountGroupUnder == 10:
                            party_gstin = Parties.objects.get(
                                LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID, PartyType="customer", PartyCode=Particulars.LedgerCode).GSTNumber

                    dic = {
                        "Date": i['Date'],
                        "VoucherNo": i['VoucherNo'],
                        "VoucherType": "SI",
                        "Particulars": LedgerName,
                        "party_gstin": party_gstin,
                        "TaxType": i['TaxType'],
                        "TotalTax": i['TotalTax'],
                        "SGSTAmount": i['SGSTAmount'],
                        "IGSTAmount": i['IGSTAmount'],
                        "CGSTAmount": i['CGSTAmount'],
                        "CESSAmount": 0,
                        "KFCAmount": i['KFCAmount'],
                        "TotalTaxableAmount": i['TotalTaxableAmount'],
                    }
                    if float(i['TotalTax']) > 0:
                        print("SALEMASTER", i['TotalTax'])
                        final_array.append(dic)

                party_gstin = ""
                for i in return_jsnDatas:
                    LedgerID = i['LedgerID']
                    if AccountLedger.objects.filter(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID).exists():
                        LedgerName = Particulars.LedgerName
                        Particulars = AccountLedger.objects.get(
                            LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID)
                        if Particulars.AccountGroupUnder == 10:
                            party_gstin = Parties.objects.get(
                                LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID, PartyType="customer", PartyCode=Particulars.LedgerCode).GSTNumber
                    try:
                        KFCAmount = int(i['KFCAmount'])
                    except:
                        KFCAmount = 0

                    TotalTaxableAmount = float(i['TotalTaxableAmount'])
                    if TotalTaxableAmount:
                        TotalTaxableAmount = float(i['TotalTaxableAmount'])
                    else:
                        TotalTaxableAmount = 0

                    dic = {
                        "Date": i['VoucherDate'],
                        "VoucherNo": i['VoucherNo'],
                        "VoucherType": "SR",
                        "Particulars": LedgerName,
                        "party_gstin": party_gstin,
                        "TaxType": i['TaxType'],
                        "TotalTax": int(i['TotalTax']*-1),
                        "SGSTAmount": int(i['SGSTAmount']*-1),
                        "IGSTAmount": int(i['IGSTAmount']*-1),
                        "CGSTAmount": int(i['CGSTAmount']*-1),
                        "CESSAmount": 0,
                        "KFCAmount": KFCAmount*-1,
                        "TotalTaxableAmount": TotalTaxableAmount*-1,
                    }
                    if float(i['TotalTax']) > 0:
                        final_array.append(dic)
                        print("SALERETURN.........", i['TotalTax'])

                for i in final_array:
                    Total_TotalTaxableAmount += float(i['TotalTaxableAmount'])
                    Total_TotalTax += float(i['TotalTax'])

                    Total_SGSTAmount += float(i['SGSTAmount'])
                    Total_CGSTAmount += float(i['CGSTAmount'])
                    Total_IGSTAmount += float(i['IGSTAmount'])
                    Total_KFCAmount += float(i['KFCAmount'])
                print(final_array, "IF>>>")
                response_data = {
                    "StatusCode": 6000,
                    "sales_data": final_array,
                    "Total_TaxableValue": Total_TaxableValue,
                    "Total_TotalQty": Total_TotalQty,

                    "Total_TotalTaxableAmount": Total_TotalTaxableAmount,
                    "Total_TotalTax": Total_TotalTax,
                    "Total_SGSTAmount": Total_SGSTAmount,
                    "Total_CGSTAmount": Total_CGSTAmount,
                    "Total_IGSTAmount": Total_IGSTAmount,
                    "Total_KFCAmount": Total_KFCAmount,
                }
                return Response(response_data, status=status.HTTP_200_OK)

        elif SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate,TaxType__in=TaxType_Arr).exists():
            # if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate,TaxType__in=TaxType_Arr).exists():
            instances = SalesMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate,TaxType__in=TaxType_Arr)
            serialized_sales = SalesGSTReportSerializer(instances, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
                                                                                       "FromDate": FromDate, "ToDate": ToDate})

            # ======
            return_instances = SalesReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate,TaxType__in=TaxType_Arr)
            serialized_return = SalesReturnMasterRestSerializer(return_instances, many=True, context={"CompanyID": CompanyID,
                                                                                                      "PriceRounding": PriceRounding})

            sales_data = serialized_sales.data
            sales_return_data = serialized_return.data
            final_array = []
            # =======

            orderdDict = sales_data
            return_orderdDict = sales_return_data

            jsnDatas = convertOrderdDict(orderdDict)
            return_jsnDatas = convertOrderdDict(return_orderdDict)

            for i in jsnDatas:
                LedgerID = i['LedgerID']
                LedgerName = ""
                party_gstin = ""

                if AccountLedger.objects.filter(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID).exists():
                    Particulars = AccountLedger.objects.get(
                        LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID)
                    LedgerName = Particulars.LedgerName
                    if Particulars.AccountGroupUnder == 10:
                        party_gstin = Parties.objects.get(
                            LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID, PartyType="customer", PartyCode=Particulars.LedgerCode).GSTNumber
                dic = {
                    "Date": i['Date'],
                    "VoucherNo": i['VoucherNo'],
                    "VoucherType": "SI",
                    "Particulars": LedgerName,
                    "party_gstin": party_gstin,
                    "TaxType": i['TaxType'],
                    "TotalTax": i['TotalTax'],
                    "SGSTAmount": i['SGSTAmount'],
                    "IGSTAmount": i['IGSTAmount'],
                    "CGSTAmount": i['CGSTAmount'],
                    "CESSAmount": 0,
                    "KFCAmount": i['KFCAmount'],
                    "TotalTaxableAmount": i['TotalTaxableAmount'],
                }
                if float(i['TotalTax']) > 0:
                    final_array.append(dic)

            for i in return_jsnDatas:
                LedgerID = i['LedgerID']

                LedgerName = ""
                party_gstin = ""
                if AccountLedger.objects.filter(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID).exists():
                    Particulars = AccountLedger.objects.get(
                        LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID)
                    LedgerName = Particulars.LedgerName
                    if Particulars.AccountGroupUnder == 10:
                        party_gstin = Parties.objects.get(
                            LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID, PartyType="customer", PartyCode=Particulars.LedgerCode).GSTNumber
                try:
                    KFCAmount = int(i['KFCAmount'])
                except:
                    KFCAmount = 0

                TotalTaxableAmount = float(i['TotalTaxableAmount'])
                if TotalTaxableAmount:
                    TotalTaxableAmount = float(i['TotalTaxableAmount'])
                else:
                    TotalTaxableAmount = 0

                dic = {
                    "Date": i['VoucherDate'],
                    "VoucherNo": i['VoucherNo'],
                    "VoucherType": "SR",
                    "Particulars": LedgerName,
                    "party_gstin": party_gstin,
                    "TaxType": i['TaxType'],
                    "TotalTax": int(i['TotalTax']*-1),
                    "SGSTAmount": int(i['SGSTAmount']*-1),
                    "IGSTAmount": int(i['IGSTAmount']*-1),
                    "CGSTAmount": int(i['CGSTAmount']*-1),
                    "CESSAmount": 0,
                    "KFCAmount": KFCAmount*-1,
                    "TotalTaxableAmount": TotalTaxableAmount*-1,
                }
                if float(i['TotalTax']) > 0:
                    final_array.append(dic)

            for i in final_array:
                Total_TotalTaxableAmount += float(i['TotalTaxableAmount'])
                Total_TotalTax += float(i['TotalTax'])

                Total_SGSTAmount += float(i['SGSTAmount'])
                Total_CGSTAmount += float(i['CGSTAmount'])
                Total_IGSTAmount += float(i['IGSTAmount'])
                Total_KFCAmount += float(i['KFCAmount'])
            print(final_array, 'final_array')
            response_data = {
                "StatusCode": 6000,
                "sales_data": final_array,
                "Total_TaxableValue": Total_TaxableValue,
                "Total_TotalQty": Total_TotalQty,
                "Total_TotalTaxableAmount": Total_TotalTaxableAmount,
                "Total_TotalTax": Total_TotalTax,
                "Total_SGSTAmount": Total_SGSTAmount,
                "Total_CGSTAmount": Total_CGSTAmount,
                "Total_IGSTAmount": Total_IGSTAmount,
                "Total_KFCAmount": Total_KFCAmount,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "datas not found!"
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "please provide valid datas!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def sales_report(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    UserID = data['UserID']
    PriceRounding = data['PriceRounding']
    try:
        page_number = data['page_no']
    except:
        page_number = ""

    try:
        items_per_page = data['items_per_page']
    except:
        items_per_page = ""
    serialized1 = ListSerializerforReport(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']

        sales_data = []
        salesReturn_data = []
        Total_netAmt_sale = 0
        Total_netAmt_saleRetn = 0
        Total_tax_sale = 0
        Total_tax_saleRetn = 0
        Total_billDiscount_sale = 0
        Total_billDiscount_saleRetn = 0
        Total_grandTotal_sale = 0
        Total_grandTotal_saleRetn = 0
        Total_cashSales = 0
        Total_bankSales = 0
        Total_creditSales = 0
        Total_cashSalesReturn = 0
        Total_bankSalesReturn = 0
        Total_creditSalesReturn = 0
        count_sales_return = 0
        instances_salesReturn = None

        if UserID:
            UserID = UserTable.objects.get(id=UserID).customer.user.pk
            if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID).exists():
                instances = SalesMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID)
                count_sales = instances.count()
                serialized_sales = SalesMasterReportSerializer(instances, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
                                                                                              "FromDate": FromDate, "ToDate": ToDate})
                sales_data = serialized_sales.data

                orderdDict = sales_data
                jsnDatas = convertOrderdDict(orderdDict)

                for i in jsnDatas:
                    CashSales = i['CashSales']
                    BankSales = i['BankSales']
                    CreditSales = i['CreditSales']

                    Total_cashSales += CashSales
                    Total_bankSales += BankSales
                    Total_creditSales += CreditSales

                for i_sale in instances:
                    Total_netAmt_sale += i_sale.NetTotal
                    Total_tax_sale += i_sale.TotalTax
                    Total_billDiscount_sale += i_sale.BillDiscAmt
                    Total_grandTotal_sale += i_sale.GrandTotal

            if SalesReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, CreatedUserID=UserID).exists():
                instances_salesReturn = SalesReturnMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, CreatedUserID=UserID)
                count_sales_return = instances_salesReturn.count()
                serialized_salesReturn = SalesReturnMasterReportSerializer(instances_salesReturn, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
                                                                                                                      "FromDate": FromDate, "ToDate": ToDate})
                salesReturn_data = serialized_salesReturn.data

                orderdDict = salesReturn_data
                jsnDatas = convertOrderdDict(orderdDict)

                for i in jsnDatas:
                    CashSalesReturn = i['CashSalesReturn']
                    BankSalesReturn = i['BankSalesReturn']
                    CreditSalesReturn = i['CreditSalesReturn']

                    Total_cashSalesReturn += CashSalesReturn
                    Total_bankSalesReturn += BankSalesReturn
                    Total_creditSalesReturn += CreditSalesReturn

                for i_saleReturn in instances_salesReturn:
                    Total_netAmt_saleRetn += i_saleReturn.NetTotal
                    Total_tax_saleRetn += i_saleReturn.TotalTax
                    Total_billDiscount_saleRetn += i_saleReturn.BillDiscAmt
                    Total_grandTotal_saleRetn += i_saleReturn.GrandTotal

        else:
            if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
                instances = SalesMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)

                count_sales = instances.count()

                sale_sort_pagination = list_pagination(
                    instances,
                    items_per_page,
                    page_number
                )
                serialized_sales = SalesMasterReportSerializer(sale_sort_pagination, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
                                                                                              "FromDate": FromDate, "ToDate": ToDate})
                sales_data = serialized_sales.data

                orderdDict = sales_data
                jsnDatas = convertOrderdDict(orderdDict)

                for i in jsnDatas:
                    CashSales = i['CashSales']
                    BankSales = i['BankSales']
                    CreditSales = i['CreditSales']

                    Total_cashSales += CashSales
                    Total_bankSales += BankSales
                    Total_creditSales += CreditSales

                for i_sale in instances:
                    Total_netAmt_sale += i_sale.NetTotal
                    Total_tax_sale += i_sale.TotalTax
                    Total_billDiscount_sale += i_sale.BillDiscAmt
                    Total_grandTotal_sale += i_sale.GrandTotal

            if SalesReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate).exists():
                instances_salesReturn = SalesReturnMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate)

                count_sales_return = instances_salesReturn.count()
                serialized_salesReturn = SalesReturnMasterReportSerializer(instances_salesReturn, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
                                                                                                                      "FromDate": FromDate, "ToDate": ToDate})
                salesReturn_data = serialized_salesReturn.data

                orderdDict = salesReturn_data
                jsnDatas = convertOrderdDict(orderdDict)

                for i in jsnDatas:
                    CashSalesReturn = i['CashSalesReturn']
                    BankSalesReturn = i['BankSalesReturn']
                    CreditSalesReturn = i['CreditSalesReturn']

                    Total_cashSalesReturn += CashSalesReturn
                    Total_bankSalesReturn += BankSalesReturn
                    Total_creditSalesReturn += CreditSalesReturn

                for i_saleReturn in instances_salesReturn:
                    Total_netAmt_saleRetn += i_saleReturn.NetTotal
                    Total_tax_saleRetn += i_saleReturn.TotalTax
                    Total_billDiscount_saleRetn += i_saleReturn.BillDiscAmt
                    Total_grandTotal_saleRetn += i_saleReturn.GrandTotal

        #request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sales Report', 'Report', 'Sales Report Viewed successfully.', 'Sales Report Viewed successfully.')
        sales_data_code = 6001
        salesReturn_data_code = 6001
        if sales_data:
            sales_data_code = 6000
        if salesReturn_data:
            salesReturn_data_code = 6000
        if sales_data or salesReturn_data:
            count_divided_sales = math.ceil(float(count_sales)/ 10)
            count_divided_sales_return = math.ceil(float(count_sales_return)/ 10)
            response_data = {
                "StatusCode": 6000,
                "count": len(instances),
                "return_count": count_sales_return,
                "count_divided_sales": count_divided_sales,
                "count_divided_sales_return": count_divided_sales_return,
                "sales_data_code": sales_data_code,
                "salesReturn_data_code": salesReturn_data_code,
                "sales_data": sales_data,
                "salesReturn_data": salesReturn_data,
                "Total_netAmt_sale": round(Total_netAmt_sale, PriceRounding),
                "Total_netAmt_saleRetn": round(Total_netAmt_saleRetn, PriceRounding),
                "Total_tax_sale": round(Total_tax_sale, PriceRounding),
                "Total_tax_saleRetn": round(Total_tax_saleRetn, PriceRounding),
                "Total_billDiscount_sale": round(Total_billDiscount_sale, PriceRounding),
                "Total_billDiscount_saleRetn": round(Total_billDiscount_saleRetn, PriceRounding),
                "Total_grandTotal_sale": round(Total_grandTotal_sale, PriceRounding),
                "Total_grandTotal_saleRetn": round(Total_grandTotal_saleRetn, PriceRounding),
                "Total_cashSales": round(Total_cashSales, PriceRounding),
                "Total_bankSales": round(Total_bankSales, PriceRounding),
                "Total_creditSales": round(Total_creditSales, PriceRounding),
                "Total_cashSalesReturn": round(Total_cashSalesReturn, PriceRounding),
                "Total_bankSalesReturn": round(Total_bankSalesReturn, PriceRounding),
                "Total_creditSalesReturn": round(Total_creditSalesReturn, PriceRounding),
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "datas not found!",
                "sales_data_code": sales_data_code,
                "salesReturn_data_code": salesReturn_data_code,
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "please provide valid datas!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def searchLedger_sales_report(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    UserID = data['UserID']
    PriceRounding = data['PriceRounding']
    LedgerID = data['LedgerID']
    try:
        page_number = data['page_no']
    except:
        page_number = ""

    try:
        items_per_page = data['items_per_page']
    except:
        items_per_page = ""
    serialized1 = ListSerializerforReport(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']

        sales_data = []
        salesReturn_data = []
        Total_netAmt_sale = 0
        Total_netAmt_saleRetn = 0
        Total_tax_sale = 0
        Total_tax_saleRetn = 0
        Total_billDiscount_sale = 0
        Total_billDiscount_saleRetn = 0
        Total_grandTotal_sale = 0
        Total_grandTotal_saleRetn = 0
        Total_cashSales = 0
        Total_bankSales = 0
        Total_creditSales = 0
        Total_cashSalesReturn = 0
        Total_bankSalesReturn = 0
        Total_creditSalesReturn = 0

        if LedgerID:
            # ledger_ins = AccountLedger.objects.get(BranchID=BranchID,CompanyID=CompanyID,LedgerName=LedgerName)
            if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, LedgerID=LedgerID).exists():
                instances = SalesMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, LedgerID=LedgerID)
                serialized_sales = SalesMasterReportSerializer(instances, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
                                                                                              "FromDate": FromDate, "ToDate": ToDate})
                sales_data = serialized_sales.data

                orderdDict = sales_data
                jsnDatas = convertOrderdDict(orderdDict)

                for i in jsnDatas:
                    CashSales = i['CashSales']
                    BankSales = i['BankSales']
                    CreditSales = i['CreditSales']

                    Total_cashSales += CashSales
                    Total_bankSales += BankSales
                    Total_creditSales += CreditSales

                for i_sale in instances:
                    Total_netAmt_sale += i_sale.NetTotal
                    Total_tax_sale += i_sale.TotalTax
                    Total_billDiscount_sale += i_sale.BillDiscAmt
                    Total_grandTotal_sale += i_sale.GrandTotal

            if SalesReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, LedgerID=LedgerID).exists():
                instances_salesReturn = SalesReturnMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, LedgerID=LedgerID)
                serialized_salesReturn = SalesReturnMasterReportSerializer(instances_salesReturn, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
                                                                                                                      "FromDate": FromDate, "ToDate": ToDate})
                salesReturn_data = serialized_salesReturn.data

                orderdDict = salesReturn_data
                jsnDatas = convertOrderdDict(orderdDict)

                for i in jsnDatas:
                    CashSalesReturn = i['CashSalesReturn']
                    BankSalesReturn = i['BankSalesReturn']
                    CreditSalesReturn = i['CreditSalesReturn']

                    Total_cashSalesReturn += CashSalesReturn
                    Total_bankSalesReturn += BankSalesReturn
                    Total_creditSalesReturn += CreditSalesReturn

                for i_saleReturn in instances_salesReturn:
                    Total_netAmt_saleRetn += i_saleReturn.NetTotal
                    Total_tax_saleRetn += i_saleReturn.TotalTax
                    Total_billDiscount_saleRetn += i_saleReturn.BillDiscAmt
                    Total_grandTotal_saleRetn += i_saleReturn.GrandTotal

        elif UserID:
            UserID = UserTable.objects.get(id=UserID).customer.user.pk
            if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID).exists():
                instances = SalesMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID)
                serialized_sales = SalesMasterReportSerializer(instances, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
                                                                                              "FromDate": FromDate, "ToDate": ToDate})
                sales_data = serialized_sales.data

                orderdDict = sales_data
                jsnDatas = convertOrderdDict(orderdDict)

                for i in jsnDatas:
                    CashSales = i['CashSales']
                    BankSales = i['BankSales']
                    CreditSales = i['CreditSales']

                    Total_cashSales += CashSales
                    Total_bankSales += BankSales
                    Total_creditSales += CreditSales

                for i_sale in instances:
                    Total_netAmt_sale += i_sale.NetTotal
                    Total_tax_sale += i_sale.TotalTax
                    Total_billDiscount_sale += i_sale.BillDiscAmt
                    Total_grandTotal_sale += i_sale.GrandTotal

            if SalesReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, CreatedUserID=UserID).exists():
                instances_salesReturn = SalesReturnMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, CreatedUserID=UserID)
                serialized_salesReturn = SalesReturnMasterReportSerializer(instances_salesReturn, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
                                                                                                                      "FromDate": FromDate, "ToDate": ToDate})
                salesReturn_data = serialized_salesReturn.data

                orderdDict = salesReturn_data
                jsnDatas = convertOrderdDict(orderdDict)

                for i in jsnDatas:
                    CashSalesReturn = i['CashSalesReturn']
                    BankSalesReturn = i['BankSalesReturn']
                    CreditSalesReturn = i['CreditSalesReturn']

                    Total_cashSalesReturn += CashSalesReturn
                    Total_bankSalesReturn += BankSalesReturn
                    Total_creditSalesReturn += CreditSalesReturn

                for i_saleReturn in instances_salesReturn:
                    Total_netAmt_saleRetn += i_saleReturn.NetTotal
                    Total_tax_saleRetn += i_saleReturn.TotalTax
                    Total_billDiscount_saleRetn += i_saleReturn.BillDiscAmt
                    Total_grandTotal_saleRetn += i_saleReturn.GrandTotal

        else:
            if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
                instances = SalesMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)

                sale_sort_pagination = list_pagination(
                    instances,
                    items_per_page,
                    page_number
                )
                serialized_sales = SalesMasterReportSerializer(sale_sort_pagination, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
                                                                                                         "FromDate": FromDate, "ToDate": ToDate})
                sales_data = serialized_sales.data

                orderdDict = sales_data
                jsnDatas = convertOrderdDict(orderdDict)

                for i in jsnDatas:
                    CashSales = i['CashSales']
                    BankSales = i['BankSales']
                    CreditSales = i['CreditSales']

                    Total_cashSales += CashSales
                    Total_bankSales += BankSales
                    Total_creditSales += CreditSales

                for i_sale in instances:
                    Total_netAmt_sale += i_sale.NetTotal
                    Total_tax_sale += i_sale.TotalTax
                    Total_billDiscount_sale += i_sale.BillDiscAmt
                    Total_grandTotal_sale += i_sale.GrandTotal

            if SalesReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate).exists():
                instances_salesReturn = SalesReturnMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate)
                serialized_salesReturn = SalesReturnMasterReportSerializer(instances_salesReturn, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
                                                                                                                      "FromDate": FromDate, "ToDate": ToDate})
                salesReturn_data = serialized_salesReturn.data

                orderdDict = salesReturn_data
                jsnDatas = convertOrderdDict(orderdDict)

                for i in jsnDatas:
                    CashSalesReturn = i['CashSalesReturn']
                    BankSalesReturn = i['BankSalesReturn']
                    CreditSalesReturn = i['CreditSalesReturn']

                    Total_cashSalesReturn += CashSalesReturn
                    Total_bankSalesReturn += BankSalesReturn
                    Total_creditSalesReturn += CreditSalesReturn

                for i_saleReturn in instances_salesReturn:
                    Total_netAmt_saleRetn += i_saleReturn.NetTotal
                    Total_tax_saleRetn += i_saleReturn.TotalTax
                    Total_billDiscount_saleRetn += i_saleReturn.BillDiscAmt
                    Total_grandTotal_saleRetn += i_saleReturn.GrandTotal

        # request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sales Report', 'Report', 'Sales Report Viewed successfully.', 'Sales Report Viewed successfully.')
        print(sales_data, "PPPPPPPPPPPOOOOOOOOOOOOIIIIIIIIIIII")
        sales_data_code = 6001
        salesReturn_data_code = 6001
        if sales_data:
            sales_data_code = 6000
        if salesReturn_data:
            salesReturn_data_code = 6000
        if sales_data or salesReturn_data:
            response_data = {
                "StatusCode": 6000,
                "count": len(instances),
                "sales_data_code": sales_data_code,
                "salesReturn_data_code": salesReturn_data_code,
                "sales_data": sales_data,
                "salesReturn_data": salesReturn_data,
                "Total_netAmt_sale": round(Total_netAmt_sale, PriceRounding),
                "Total_netAmt_saleRetn": round(Total_netAmt_saleRetn, PriceRounding),
                "Total_tax_sale": round(Total_tax_sale, PriceRounding),
                "Total_tax_saleRetn": round(Total_tax_saleRetn, PriceRounding),
                "Total_billDiscount_sale": round(Total_billDiscount_sale, PriceRounding),
                "Total_billDiscount_saleRetn": round(Total_billDiscount_saleRetn, PriceRounding),
                "Total_grandTotal_sale": round(Total_grandTotal_sale, PriceRounding),
                "Total_grandTotal_saleRetn": round(Total_grandTotal_saleRetn, PriceRounding),
                "Total_cashSales": round(Total_cashSales, PriceRounding),
                "Total_bankSales": round(Total_bankSales, PriceRounding),
                "Total_creditSales": round(Total_creditSales, PriceRounding),
                "Total_cashSalesReturn": round(Total_cashSalesReturn, PriceRounding),
                "Total_bankSalesReturn": round(Total_bankSalesReturn, PriceRounding),
                "Total_creditSalesReturn": round(Total_creditSalesReturn, PriceRounding),
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "datas not found!"
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "please provide valid datas!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def sales_report1(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    UserID = data['UserID']
    PriceRounding = data['PriceRounding']
    serialized1 = ListSerializerforReport(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']

        sales_data = []
        salesReturn_data = []
        Total_netAmt_sale = 0
        Total_netAmt_saleRetn = 0
        Total_tax_sale = 0
        Total_tax_saleRetn = 0
        Total_billDiscount_sale = 0
        Total_billDiscount_saleRetn = 0
        Total_grandTotal_sale = 0
        Total_grandTotal_saleRetn = 0
        Total_cashSales = 0
        Total_bankSales = 0
        Total_creditSales = 0
        Total_cashSalesReturn = 0
        Total_bankSalesReturn = 0
        Total_creditSalesReturn = 0

        if UserID:
            UserID = UserTable.objects.get(id=UserID).customer.user.pk
            if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID).exists():
                instances = SalesMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID)
                serialized_sales = SalesMasterReportSerializer(instances, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
                                                                                              "FromDate": FromDate, "ToDate": ToDate})
                sales_data = serialized_sales.data

                orderdDict = sales_data
                jsnDatas = convertOrderdDict(orderdDict)

                for i in jsnDatas:
                    CashSales = i['CashSales']
                    BankSales = i['BankSales']
                    CreditSales = i['CreditSales']

                    Total_cashSales += CashSales
                    Total_bankSales += BankSales
                    Total_creditSales += CreditSales

                for i_sale in instances:
                    Total_netAmt_sale += i_sale.NetTotal
                    Total_tax_sale += i_sale.TotalTax
                    Total_billDiscount_sale += i_sale.BillDiscAmt
                    Total_grandTotal_sale += i_sale.GrandTotal

            if SalesReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, CreatedUserID=UserID).exists():
                instances_salesReturn = SalesReturnMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, CreatedUserID=UserID)
                serialized_salesReturn = SalesReturnMasterReportSerializer(instances_salesReturn, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
                                                                                                                      "FromDate": FromDate, "ToDate": ToDate})
                salesReturn_data = serialized_salesReturn.data

                orderdDict = salesReturn_data
                jsnDatas = convertOrderdDict(orderdDict)

                for i in jsnDatas:
                    CashSalesReturn = i['CashSalesReturn']
                    BankSalesReturn = i['BankSalesReturn']
                    CreditSalesReturn = i['CreditSalesReturn']

                    Total_cashSalesReturn += CashSalesReturn
                    Total_bankSalesReturn += BankSalesReturn
                    Total_creditSalesReturn += CreditSalesReturn

                for i_saleReturn in instances_salesReturn:
                    Total_netAmt_saleRetn += i_saleReturn.NetTotal
                    Total_tax_saleRetn += i_saleReturn.TotalTax
                    Total_billDiscount_saleRetn += i_saleReturn.BillDiscAmt
                    Total_grandTotal_saleRetn += i_saleReturn.GrandTotal

        else:
            if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
                instances = SalesMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)
                serialized_sales = SalesMasterReportSerializer(instances, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
                                                                                              "FromDate": FromDate, "ToDate": ToDate})
                sales_data = serialized_sales.data

                orderdDict = sales_data
                jsnDatas = convertOrderdDict(orderdDict)

                for i in jsnDatas:
                    CashSales = i['CashSales']
                    BankSales = i['BankSales']
                    CreditSales = i['CreditSales']

                    Total_cashSales += CashSales
                    Total_bankSales += BankSales
                    Total_creditSales += CreditSales

                for i_sale in instances:
                    Total_netAmt_sale += i_sale.NetTotal
                    Total_tax_sale += i_sale.TotalTax
                    Total_billDiscount_sale += i_sale.BillDiscAmt
                    Total_grandTotal_sale += i_sale.GrandTotal

            if SalesReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate).exists():
                instances_salesReturn = SalesReturnMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate)
                serialized_salesReturn = SalesReturnMasterReportSerializer(instances_salesReturn, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
                                                                                                                      "FromDate": FromDate, "ToDate": ToDate})
                salesReturn_data = serialized_salesReturn.data

                orderdDict = salesReturn_data
                jsnDatas = convertOrderdDict(orderdDict)

                for i in jsnDatas:
                    CashSalesReturn = i['CashSalesReturn']
                    BankSalesReturn = i['BankSalesReturn']
                    CreditSalesReturn = i['CreditSalesReturn']

                    Total_cashSalesReturn += CashSalesReturn
                    Total_bankSalesReturn += BankSalesReturn
                    Total_creditSalesReturn += CreditSalesReturn

                for i_saleReturn in instances_salesReturn:
                    Total_netAmt_saleRetn += i_saleReturn.NetTotal
                    Total_tax_saleRetn += i_saleReturn.TotalTax
                    Total_billDiscount_saleRetn += i_saleReturn.BillDiscAmt
                    Total_grandTotal_saleRetn += i_saleReturn.GrandTotal

        # request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sales Report', 'Report', 'Sales Report Viewed successfully.', 'Sales Report Viewed successfully.')
        print(sales_data, "PPPPPPPPPPPOOOOOOOOOOOOIIIIIIIIIIII")
        sales_data_code = 6001
        salesReturn_data_code = 6001
        if sales_data:
            sales_data_code = 6000
        if salesReturn_data:
            salesReturn_data_code = 6000
        if sales_data or salesReturn_data:
            response_data = {
                "StatusCode": 6000,
                "sales_data_code": sales_data_code,
                "salesReturn_data_code": salesReturn_data_code,
                "sales_data": sales_data,
                "salesReturn_data": salesReturn_data,
                "Total_netAmt_sale": round(Total_netAmt_sale, PriceRounding),
                "Total_netAmt_saleRetn": round(Total_netAmt_saleRetn, PriceRounding),
                "Total_tax_sale": round(Total_tax_sale, PriceRounding),
                "Total_tax_saleRetn": round(Total_tax_saleRetn, PriceRounding),
                "Total_billDiscount_sale": round(Total_billDiscount_sale, PriceRounding),
                "Total_billDiscount_saleRetn": round(Total_billDiscount_saleRetn, PriceRounding),
                "Total_grandTotal_sale": round(Total_grandTotal_sale, PriceRounding),
                "Total_grandTotal_saleRetn": round(Total_grandTotal_saleRetn, PriceRounding),
                "Total_cashSales": round(Total_cashSales, PriceRounding),
                "Total_bankSales": round(Total_bankSales, PriceRounding),
                "Total_creditSales": round(Total_creditSales, PriceRounding),
                "Total_cashSalesReturn": round(Total_cashSalesReturn, PriceRounding),
                "Total_bankSalesReturn": round(Total_bankSalesReturn, PriceRounding),
                "Total_creditSalesReturn": round(Total_creditSalesReturn, PriceRounding),
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "datas not found!"
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "please provide valid datas!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def sales_integrated_report(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    UserID = data['UserID']
    PriceRounding = data['PriceRounding']
    serialized1 = ListSerializerforReport(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']

        date_array = []
        final_array = []
        cash_ledgers = []
        bank_ledgers = []
        credit_ledgers = []

        UserID = str(UserID)

        if not UserID == "0":
            user_name = UserTable.objects.get(
                CompanyID=CompanyID, id=UserID).customer.user.username
            UserID = UserTable.objects.get(
                CompanyID=CompanyID, id=UserID).customer.user.id
            if AccountLedger.objects.filter(CompanyID=CompanyID, BranchID=BranchID, AccountGroupUnder=9).exists():
                account_ledgers_cash = AccountLedger.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, AccountGroupUnder=9)
                for al in account_ledgers_cash:
                    cash_ledgers.append(al.LedgerID)

            if AccountLedger.objects.filter(CompanyID=CompanyID, BranchID=BranchID, AccountGroupUnder=8).exists():
                account_ledgers_bank = AccountLedger.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, AccountGroupUnder=8)
                for al in account_ledgers_bank:
                    bank_ledgers.append(al.LedgerID)

            if AccountLedger.objects.filter(CompanyID=CompanyID, BranchID=BranchID, AccountGroupUnder__in=[10, 29]).exists():
                account_ledgers_credit = AccountLedger.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, AccountGroupUnder__in=[10, 29])
                for al in account_ledgers_credit:
                    credit_ledgers.append(al.LedgerID)

            if LedgerPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID).exists():
                instances = LedgerPosting.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID)

                for i in instances:
                    Date = i.Date
                    if not i.Date in date_array:
                        CashSales = 0
                        BankSales = 0
                        CreditSales = 0
                        CashSalesRetrn = 0
                        BankSalesRetrn = 0
                        DebitSalesRetrn = 0

                        if instances.filter(Date=Date, VoucherType="SI", LedgerID__in=cash_ledgers).exists():
                            ledgers = instances.filter(
                                Date=Date, VoucherType="SI", LedgerID__in=cash_ledgers)
                            TotalCashDebit = 0
                            TotalCashCredit = 0
                            for i in ledgers:
                                TotalCashDebit += float(i.Debit)
                                TotalCashCredit += float(i.Credit)
                            CashSales = float(TotalCashDebit) - \
                                float(TotalCashCredit)

                        if instances.filter(Date=Date, VoucherType="SI", LedgerID__in=bank_ledgers).exists():
                            ledgers = instances.filter(
                                Date=Date, VoucherType="SI", LedgerID__in=bank_ledgers)
                            TotalBankDebit = 0
                            TotalBankCredit = 0
                            for i in ledgers:
                                TotalBankDebit += float(i.Debit)
                                TotalBankCredit += float(i.Credit)
                            BankSales = float(TotalBankDebit) - \
                                float(TotalBankCredit)

                        if instances.filter(Date=Date, VoucherType="SI", LedgerID__in=credit_ledgers).exists():
                            ledgers = instances.filter(
                                Date=Date, VoucherType="SI", LedgerID__in=credit_ledgers)
                            TotalCreditDebit = 0
                            TotalCreditCredit = 0
                            for i in ledgers:
                                TotalCreditDebit += float(i.Debit)
                                TotalCreditCredit += float(i.Credit)
                            CreditSales = float(
                                TotalCreditDebit) - float(TotalCreditCredit)

                        if instances.filter(Date=Date, VoucherType="SR", LedgerID__in=cash_ledgers).exists():
                            ledgers = instances.filter(
                                Date=Date, VoucherType="SR", LedgerID__in=cash_ledgers)
                            TotalCashDebit = 0
                            TotalCashCredit = 0
                            for i in ledgers:
                                TotalCashDebit += float(i.Debit)
                                TotalCashCredit += float(i.Credit)
                            CashSalesRetrn = float(
                                TotalCashDebit) - float(TotalCashCredit)

                        if instances.filter(Date=Date, VoucherType="SR", LedgerID__in=bank_ledgers).exists():
                            ledgers = instances.filter(
                                Date=Date, VoucherType="SR", LedgerID__in=bank_ledgers)
                            TotalBankDebit = 0
                            TotalBankCredit = 0
                            for i in ledgers:
                                TotalBankDebit += float(i.Debit)
                                TotalBankCredit += float(i.Credit)
                            BankSalesRetrn = float(
                                TotalBankDebit) - float(TotalBankCredit)

                        if instances.filter(Date=Date, VoucherType="SR", LedgerID__in=credit_ledgers).exists():
                            ledgers = instances.filter(
                                Date=Date, VoucherType="SR", LedgerID__in=credit_ledgers)
                            TotalCreditDebit = 0
                            TotalCreditCredit = 0
                            for i in ledgers:
                                TotalCreditDebit += float(i.Debit)
                                TotalCreditCredit += float(i.Credit)
                            DebitSalesRetrn = float(
                                TotalCreditDebit) - float(TotalCreditCredit)

                        NetSales = float(CashSales) + \
                            float(CreditSales) + float(BankSales)
                        NetSalesReturn = float(
                            CashSalesRetrn) + float(DebitSalesRetrn) + float(BankSalesRetrn)

                        ActualSales = float(NetSales) - float(NetSalesReturn)

                        print(CashSales, "1nd",
                              CreditSales, "1nd",
                              BankSales, "1nd",
                              NetSales, "1nd",
                              CashSalesRetrn, "1nd",
                              DebitSalesRetrn, "1nd",
                              BankSalesRetrn, "1nd",
                              NetSalesReturn, "1nd",
                              ActualSales)

                        if CashSales == 0 and CreditSales == 0 and BankSales == 0 and NetSales == 0 and CashSalesRetrn == 0 and DebitSalesRetrn == 0 and BankSalesRetrn == 0 and NetSalesReturn == 0 and ActualSales == 0:
                            print("==============")
                        else:
                            final_array.append(
                                {
                                    "Date": Date,
                                    "User": user_name,
                                    "CashSales": CashSales,
                                    "CreditSales": CreditSales,
                                    "BankSales": BankSales,
                                    "NetSales": NetSales,
                                    "CashSalesReturn": CashSalesRetrn,
                                    "DebitSalesRetrn": DebitSalesRetrn,
                                    "BankSalesReturn": BankSalesRetrn,
                                    "NetSalesReturn": NetSalesReturn,
                                    "ActualSales": ActualSales,
                                })

                        date_array.append(i.Date)

        else:
            if AccountLedger.objects.filter(CompanyID=CompanyID, BranchID=BranchID, AccountGroupUnder=9).exists():
                account_ledgers_cash = AccountLedger.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, AccountGroupUnder=9)
                for al in account_ledgers_cash:
                    cash_ledgers.append(al.LedgerID)

            if AccountLedger.objects.filter(CompanyID=CompanyID, BranchID=BranchID, AccountGroupUnder=8).exists():
                account_ledgers_bank = AccountLedger.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, AccountGroupUnder=8)
                for al in account_ledgers_bank:
                    bank_ledgers.append(al.LedgerID)

            if AccountLedger.objects.filter(CompanyID=CompanyID, BranchID=BranchID, AccountGroupUnder__in=[10, 29]).exists():
                account_ledgers_credit = AccountLedger.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, AccountGroupUnder__in=[10, 29])
                for al in account_ledgers_credit:
                    credit_ledgers.append(al.LedgerID)

            if LedgerPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
                instances = LedgerPosting.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)

                for i in instances:
                    Date = i.Date
                    if not i.Date in date_array:
                        CashSales = 0
                        BankSales = 0
                        CreditSales = 0
                        CashSalesRetrn = 0
                        BankSalesRetrn = 0
                        DebitSalesRetrn = 0

                        if instances.filter(Date=Date, VoucherType="SI", LedgerID__in=cash_ledgers).exists():
                            ledgers = instances.filter(
                                Date=Date, VoucherType="SI", LedgerID__in=cash_ledgers)
                            TotalCashDebit = 0
                            TotalCashCredit = 0
                            for i in ledgers:
                                TotalCashDebit += float(i.Debit)
                                TotalCashCredit += float(i.Credit)
                            CashSales = float(TotalCashDebit) - \
                                float(TotalCashCredit)

                        if instances.filter(Date=Date, VoucherType="SI", LedgerID__in=bank_ledgers).exists():
                            ledgers = instances.filter(
                                Date=Date, VoucherType="SI", LedgerID__in=bank_ledgers)
                            TotalBankDebit = 0
                            TotalBankCredit = 0
                            for i in ledgers:
                                TotalBankDebit += float(i.Debit)
                                TotalBankCredit += float(i.Credit)
                            BankSales = float(TotalBankDebit) - \
                                float(TotalBankCredit)

                        if instances.filter(Date=Date, VoucherType="SI", LedgerID__in=credit_ledgers).exists():
                            ledgers = instances.filter(
                                Date=Date, VoucherType="SI", LedgerID__in=credit_ledgers)
                            TotalCreditDebit = 0
                            TotalCreditCredit = 0
                            for i in ledgers:
                                TotalCreditDebit += float(i.Debit)
                                TotalCreditCredit += float(i.Credit)
                            CreditSales = float(
                                TotalCreditDebit) - float(TotalCreditCredit)

                        if instances.filter(Date=Date, VoucherType="SR", LedgerID__in=cash_ledgers).exists():
                            ledgers = instances.filter(
                                Date=Date, VoucherType="SR", LedgerID__in=cash_ledgers)
                            TotalCashDebit = 0
                            TotalCashCredit = 0
                            for i in ledgers:
                                TotalCashDebit += float(i.Debit)
                                TotalCashCredit += float(i.Credit)
                            CashSalesRetrn = float(
                                TotalCashDebit) - float(TotalCashCredit)

                        if instances.filter(Date=Date, VoucherType="SR", LedgerID__in=bank_ledgers).exists():
                            ledgers = instances.filter(
                                Date=Date, VoucherType="SR", LedgerID__in=bank_ledgers)
                            TotalBankDebit = 0
                            TotalBankCredit = 0
                            for i in ledgers:
                                TotalBankDebit += float(i.Debit)
                                TotalBankCredit += float(i.Credit)
                            BankSalesRetrn = float(
                                TotalBankDebit) - float(TotalBankCredit)

                        if instances.filter(Date=Date, VoucherType="SR", LedgerID__in=credit_ledgers).exists():
                            ledgers = instances.filter(
                                Date=Date, VoucherType="SR", LedgerID__in=credit_ledgers)
                            TotalCreditDebit = 0
                            TotalCreditCredit = 0
                            for i in ledgers:
                                TotalCreditDebit += float(i.Debit)
                                TotalCreditCredit += float(i.Credit)
                            DebitSalesRetrn = float(
                                TotalCreditDebit) - float(TotalCreditCredit)

                        NetSales = float(CashSales) + \
                            float(CreditSales) + float(BankSales)
                        NetSalesReturn = float(
                            CashSalesRetrn) + float(DebitSalesRetrn) + float(BankSalesRetrn)

                        ActualSales = float(NetSales) - float(NetSalesReturn)

                        print(CashSales, "2nd",
                              CreditSales, "2nd",
                              BankSales, "2nd",
                              NetSales, "2nd",
                              CashSalesRetrn, "2nd",
                              DebitSalesRetrn, "2nd",
                              BankSalesRetrn, "2nd",
                              NetSalesReturn, "2nd",
                              ActualSales)

                        if CashSales == 0 and CreditSales == 0 and BankSales == 0 and NetSales == 0 and CashSalesRetrn == 0 and DebitSalesRetrn == 0 and BankSalesRetrn == 0 and NetSalesReturn == 0 and ActualSales == 0:
                            print(
                                "2ndSUCESSSSSSSSSSS)))))))))))))))))))))))))((((((((((((((((((((")
                        else:
                            print("ELSE>>>>>>>>>>>>>>>>>>>>>>>.")
                            final_array.append(
                                {
                                    "Date": Date,
                                    "User": "-",
                                    "CashSales": CashSales,
                                    "CreditSales": CreditSales,
                                    "BankSales": BankSales,
                                    "NetSales": NetSales,
                                    "CashSalesReturn": CashSalesRetrn,
                                    "DebitSalesRetrn": DebitSalesRetrn,
                                    "BankSalesReturn": BankSalesRetrn,
                                    "NetSalesReturn": NetSalesReturn,
                                    "ActualSales": ActualSales,
                                })

                        date_array.append(i.Date)

        TotalCashSales = 0
        TotalCreditSales = 0
        TotalBankSales = 0
        TotalNetSales = 0
        TotalCashSalesReturn = 0
        TotalDebitSalesRetrn = 0
        TotalBankSalesReturn = 0
        TotalNetSalesReturn = 0
        TotalActualSales = 0
        for f in final_array:
            print(f, "**************")
            TotalCashSales += float(f['CashSales'])
            TotalCreditSales += float(f['CreditSales'])
            TotalBankSales += float(f['BankSales'])
            TotalNetSales += float(f['NetSales'])
            TotalCashSalesReturn += float(f['CashSalesReturn'])
            TotalDebitSalesRetrn += float(f['DebitSalesRetrn'])
            TotalBankSalesReturn += float(f['BankSalesReturn'])
            TotalNetSalesReturn += float(f['NetSalesReturn'])
            TotalActualSales += float(f['ActualSales'])

        # request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sales Integrated Report', 'Report',
        #              'Sales Integrated Report Viewed successfully.', 'Sales Integrated Report Viewed successfully.')

        print(final_array, "final_array====================")
        if final_array:
            response_data = {
                "StatusCode": 6000,
                "data": final_array,
                "TotalCashSales": TotalCashSales,
                "TotalCreditSales": TotalCreditSales,
                "TotalBankSales": TotalBankSales,
                "TotalNetSales": TotalNetSales,
                "TotalCashSalesReturn": TotalCashSalesReturn,
                "TotalDebitSalesRetrn": TotalDebitSalesRetrn,
                "TotalBankSalesReturn": TotalBankSalesReturn,
                "TotalNetSalesReturn": TotalNetSalesReturn,
                "TotalActualSales": TotalActualSales,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Datas Not Found!"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "please provide valid datas!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def generateVoucherNo(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    VoucherType = data['VoucherType']
    BranchID = data['BranchID']
    if VoucherType == "SI":
        ShowTotalTax = False
        if GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowTotalTax").exists():
            general_ins = GeneralSettings.objects.filter(
                CompanyID=CompanyID, SettingsType="ShowTotalTax").first()
            ShowTotalTax = general_ins.SettingsValue

        if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instance = SalesMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            if not OldVoucherNo.isdecimal():
                res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
                num = res.group(0)
                new_num = int(num) + 1
                new_VoucherNo = "SI" + str(new_num)
            else:
                # new_VoucherNo = float(OldVoucherNo) + 1
                new_VoucherNo = str(int(OldVoucherNo) +
                                    1).zfill(len(OldVoucherNo))
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": new_VoucherNo,
                "ShowTotalTax": ShowTotalTax
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": "SI1",
                "ShowTotalTax": ShowTotalTax
            }

            return Response(response_data, status=status.HTTP_200_OK)

    elif VoucherType == "PI":
        if PurchaseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instance = PurchaseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            if not OldVoucherNo.isdecimal():
                res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
                num = res.group(0)
                new_num = int(num) + 1
                new_VoucherNo = "PI" + str(new_num)
            else:
                # new_VoucherNo = float(OldVoucherNo) + 1
                new_VoucherNo = str(int(OldVoucherNo) +
                                    1).zfill(len(OldVoucherNo))
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": new_VoucherNo
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": "PI1"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    elif VoucherType == "SO":
        if SalesOrderMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instance = SalesOrderMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            if not OldVoucherNo.isdecimal():
                res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
                num = res.group(0)
                new_num = int(num) + 1
                new_VoucherNo = "SO" + str(new_num)
            else:
                # new_VoucherNo = float(OldVoucherNo) + 1
                new_VoucherNo = str(int(OldVoucherNo) +
                                    1).zfill(len(OldVoucherNo))
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": new_VoucherNo
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": "SO1"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    elif VoucherType == "SE":
        if SalesEstimateMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instance = SalesEstimateMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            if not OldVoucherNo.isdecimal():
                res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
                num = res.group(0)
                new_num = int(num) + 1
                new_VoucherNo = "SE" + str(new_num)
            else:
                # new_VoucherNo = float(OldVoucherNo) + 1
                new_VoucherNo = str(int(OldVoucherNo) +
                                    1).zfill(len(OldVoucherNo))
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": new_VoucherNo
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": "SE1"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    elif VoucherType == "PO":
        if PurchaseOrderMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instance = PurchaseOrderMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            if not OldVoucherNo.isdecimal():
                res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
                num = res.group(0)
                new_num = int(num) + 1
                new_VoucherNo = "PO" + str(new_num)
            else:
                # new_VoucherNo = float(OldVoucherNo) + 1
                new_VoucherNo = str(int(OldVoucherNo) +
                                    1).zfill(len(OldVoucherNo))
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": new_VoucherNo
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": "PO1"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    elif VoucherType == "SR":
        if SalesReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instance = SalesReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            if not OldVoucherNo.isdecimal():
                res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
                num = res.group(0)
                new_num = int(num) + 1
                new_VoucherNo = "SR" + str(new_num)
            else:
                # new_VoucherNo = float(OldVoucherNo) + 1
                new_VoucherNo = str(int(OldVoucherNo) +
                                    1).zfill(len(OldVoucherNo))
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": new_VoucherNo
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": "SR1"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    elif VoucherType == "PR":
        if PurchaseReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instance = PurchaseReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            if not OldVoucherNo.isdecimal():
                res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
                num = res.group(0)
                new_num = int(num) + 1
                new_VoucherNo = "PR" + str(new_num)
            else:
                # new_VoucherNo = float(OldVoucherNo) + 1
                new_VoucherNo = str(int(OldVoucherNo) +
                                    1).zfill(len(OldVoucherNo))
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": new_VoucherNo
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": "PR1"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    elif VoucherType == "OS":
        if OpeningStockMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instance = OpeningStockMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            if not OldVoucherNo.isdecimal():
                res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
                num = res.group(0)
                new_num = int(num) + 1
                new_VoucherNo = "OS" + str(new_num)
            else:
                # new_VoucherNo = float(OldVoucherNo) + 1
                new_VoucherNo = str(int(OldVoucherNo) +
                                    1).zfill(len(OldVoucherNo))
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": new_VoucherNo
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": "OS1"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    elif VoucherType == "JL":
        if JournalMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instance = JournalMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            if not OldVoucherNo.isdecimal():
                res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
                num = res.group(0)
                new_num = int(num) + 1
                new_VoucherNo = "JL" + str(new_num)
            else:
                # new_VoucherNo = float(OldVoucherNo) + 1
                new_VoucherNo = str(int(OldVoucherNo) +
                                    1).zfill(len(OldVoucherNo))
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": new_VoucherNo
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": "JL1"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    elif VoucherType == "CP":
        if PaymentMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType="CP").exists():
            instance = PaymentMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherType="CP").first()
            OldVoucherNo = instance.VoucherNo
            if not OldVoucherNo.isdecimal():
                res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
                num = res.group(0)
                new_num = int(num) + 1
                new_VoucherNo = "CP" + str(new_num)
            else:
                # new_VoucherNo = float(OldVoucherNo) + 1
                new_VoucherNo = str(int(OldVoucherNo) +
                                    1).zfill(len(OldVoucherNo))
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": new_VoucherNo
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": "CP1"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    elif VoucherType == "BP":
        if PaymentMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType="BP").exists():
            instance = PaymentMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherType="BP").first()
            OldVoucherNo = instance.VoucherNo
            if not OldVoucherNo.isdecimal():
                res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
                num = res.group(0)
                new_num = int(num) + 1
                new_VoucherNo = "BP" + str(new_num)
            else:
                # new_VoucherNo = float(OldVoucherNo) + 1
                new_VoucherNo = str(int(OldVoucherNo) +
                                    1).zfill(len(OldVoucherNo))
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": new_VoucherNo
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": "BP1"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    elif VoucherType == "CR":
        if ReceiptMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType="CR").exists():
            instance = ReceiptMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherType="CR").first()
            OldVoucherNo = instance.VoucherNo
            if not OldVoucherNo.isdecimal():
                res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
                num = res.group(0)
                new_num = int(num) + 1
                new_VoucherNo = "CR" + str(new_num)
            else:
                # new_VoucherNo = float(OldVoucherNo) + 1
                new_VoucherNo = str(int(OldVoucherNo) +
                                    1).zfill(len(OldVoucherNo))
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": new_VoucherNo
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": "CR1"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    elif VoucherType == "BR":
        if ReceiptMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType="BR").exists():
            instance = ReceiptMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherType="BR").first()
            OldVoucherNo = instance.VoucherNo
            if not OldVoucherNo.isdecimal():
                res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
                num = res.group(0)
                new_num = int(num) + 1
                new_VoucherNo = "BR" + str(new_num)
            else:
                # new_VoucherNo = float(OldVoucherNo) + 1
                new_VoucherNo = str(int(OldVoucherNo) +
                                    1).zfill(len(OldVoucherNo))
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": new_VoucherNo
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": "BR1"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    elif VoucherType == "ST":
        if StockTransferMaster_ID.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instance = StockTransferMaster_ID.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            if not OldVoucherNo.isdecimal():
                res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
                num = res.group(0)
                new_num = int(num) + 1
                new_VoucherNo = "ST" + str(new_num)
            else:
                # new_VoucherNo = float(OldVoucherNo) + 1
                new_VoucherNo = str(int(OldVoucherNo) +
                                    1).zfill(len(OldVoucherNo))

            response_data = {
                "StatusCode": 6000,
                "VoucherNo": new_VoucherNo
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": "ST1"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    elif VoucherType == "AG":
        if AccountGroup.objects.filter(CompanyID=CompanyID).exists():
            instance = AccountGroup.objects.filter(
                CompanyID=CompanyID).order_by("AccountGroupID").last()
            OldGroupCode = instance.GroupCode
            if not OldGroupCode.isdecimal():
                res = re.search(r"\d+(\.\d+)?", OldGroupCode)
                num = res.group(0)
                new_num = int(num) + 1
                new_GroupCode = "GP" + str(new_num)
            else:
                # new_GroupCode = float(OldGroupCode) + 1
                new_GroupCode = str(int(OldGroupCode) +
                                    1).zfill(len(OldGroupCode))

            response_data = {
                "StatusCode": 6000,
                "GroupCode": new_GroupCode
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6000,
                "GroupCode": "GP1"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    elif VoucherType == "ES":
        if ExcessStockMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instance = ExcessStockMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            if not OldVoucherNo.isdecimal():
                res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
                num = res.group(0)
                new_num = int(num) + 1
                new_VoucherNo = "ES" + str(new_num)
            else:
                # new_VoucherNo = float(OldVoucherNo) + 1
                new_VoucherNo = str(int(OldVoucherNo) +
                                    1).zfill(len(OldVoucherNo))

            response_data = {
                "StatusCode": 6000,
                "VoucherNo": new_VoucherNo
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": "ES1"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    elif VoucherType == "SS":
        if ShortageStockMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instance = ShortageStockMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            if not OldVoucherNo.isdecimal():
                res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
                num = res.group(0)
                new_num = int(num) + 1
                new_VoucherNo = "SS" + str(new_num)
            else:
                # new_VoucherNo = float(OldVoucherNo) + 1
                new_VoucherNo = str(int(OldVoucherNo) +
                                    1).zfill(len(OldVoucherNo))
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": new_VoucherNo
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": "SS1"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    elif VoucherType == "DS":
        if DamageStockMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instance = DamageStockMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            if not OldVoucherNo.isdecimal():
                res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
                num = res.group(0)
                new_num = int(num) + 1
                new_VoucherNo = "DS" + str(new_num)
            else:
                # new_VoucherNo = float(OldVoucherNo) + 1
                new_VoucherNo = str(int(OldVoucherNo) +
                                    1).zfill(len(OldVoucherNo))

            response_data = {
                "StatusCode": 6000,
                "VoucherNo": new_VoucherNo
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": "DS1"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    elif VoucherType == "US":
        if UsedStockMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instance = UsedStockMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            if not OldVoucherNo.isdecimal():
                res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
                num = res.group(0)
                new_num = int(num) + 1
                new_VoucherNo = "US" + str(new_num)
            else:
                # new_VoucherNo = float(OldVoucherNo) + 1
                new_VoucherNo = str(int(OldVoucherNo) +
                                    1).zfill(len(OldVoucherNo))

            response_data = {
                "StatusCode": 6000,
                "VoucherNo": new_VoucherNo
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": "US1"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    elif VoucherType == "WO":
        if WorkOrderMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instance = WorkOrderMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            if not OldVoucherNo.isdecimal():
                res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
                num = res.group(0)
                new_num = int(num) + 1
                new_VoucherNo = "WO" + str(new_num)
            else:
                # new_VoucherNo = float(OldVoucherNo) + 1
                new_VoucherNo = str(int(OldVoucherNo) +
                                    1).zfill(len(OldVoucherNo))
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": new_VoucherNo
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": "WO1"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    elif VoucherType == "PC":
        ProductCode = "PC1000"

        if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():

            latest_ProductCode = Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID).order_by("ProductID").last()

            ProductCode = latest_ProductCode.ProductCode
            print("##################")
            print(ProductCode)
            print(type(ProductCode))
            if not ProductCode.isdecimal():
                temp = re.compile("([a-zA-Z]+)([0-9]+)")
                if temp.match(ProductCode):
                    res = temp.match(ProductCode).groups()

                    code, number = res

                    number = int(number) + 1
                    print(number)
                    ProductCode = str(code) + str(number)
                else:
                    ProductCode = str(float(ProductCode) +
                                      1).zfill(len(ProductCode))
            else:
                code = str(float(ProductCode) + 1)
                code = code.rstrip('0').rstrip('.') if '.' in code else code
                ProductCode = code.zfill(len(ProductCode))

        response_data = {
            "StatusCode": 6000,
            "ProductCode": ProductCode
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "can't get voucher number please call admin!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def generate_printReport(request):
    from api.v5.sales.serializers import SalesPrintSerializer
    from api.v5.salesReturns.serializers import SalesReturnMasterPrintSerializer
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']

    VoucherType = data['VoucherType']
    unq_id = data['id']
    company_instance = CompanySettings.objects.get(pk=CompanyID.id)
    company_serialized = CompanySettingsRestSerializer(
        company_instance, context={"request": request})
    if VoucherType == "SI":
        if SalesMaster.objects.filter(CompanyID=CompanyID, id=unq_id).exists():
            instance = SalesMaster.objects.get(CompanyID=CompanyID, id=unq_id)

            serialized = SalesPrintSerializer(instance, context={"CompanyID": CompanyID,
                                                                 "PriceRounding": PriceRounding})
            orderdDict = serialized.data
            jsnDatas = convertOrderdDict(orderdDict)

            # final_array = []
            # SalesDetails = []

            Details = jsnDatas['Details']
            count = 1
            for i in Details:
                UnitPrice = i['UnitPrice']
                Qty = i['Qty']
                ProductName = i['ProductName']
                NetAmount = i['NetAmount']
                i['id'] = count

                count = count + 1

            response_data = {
                "StatusCode": 6000,
                "data": jsnDatas,
                "company_data": company_serialized.data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Sales Invoice not Found!"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    elif VoucherType == "PI":
        if PurchaseMaster.objects.filter(CompanyID=CompanyID, id=unq_id).exists():
            instance = PurchaseMaster.objects.get(
                CompanyID=CompanyID, id=unq_id)

            serialized = PurchasePrintSerializer(instance, context={"CompanyID": CompanyID,
                                                                    "PriceRounding": PriceRounding})

            orderdDict = serialized.data
            jsnDatas = convertOrderdDict(orderdDict)

            # final_array = []
            # SalesDetails = []

            Details = jsnDatas['Details']
            count = 1
            for i in Details:
                UnitPrice = i['UnitPrice']
                Qty = i['Qty']
                ProductName = i['ProductName']
                NetAmount = i['NetAmount']
                i['id'] = count

                count = count + 1

            response_data = {
                "StatusCode": 6000,
                "data": jsnDatas,
                "company_data": company_serialized.data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Purchase invoice not Found!"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    elif VoucherType == "SR":
        if SalesReturnMaster.objects.filter(CompanyID=CompanyID, id=unq_id).exists():
            instance = SalesReturnMaster.objects.get(
                CompanyID=CompanyID, id=unq_id)

            serialized = SalesReturnMasterPrintSerializer(instance, context={"CompanyID": CompanyID,
                                                                             "PriceRounding": PriceRounding})

            orderdDict = serialized.data
            jsnDatas = convertOrderdDict(orderdDict)

            # final_array = []
            # SalesDetails = []

            Details = jsnDatas['Details']
            count = 1
            for i in Details:
                UnitPrice = i['UnitPrice']
                Qty = i['Qty']
                ProductName = i['ProductName']
                NetAmount = i['NetAmount']
                i['id'] = count

                count = count + 1

            response_data = {
                "StatusCode": 6000,
                "data": jsnDatas,
                "company_data": company_serialized.data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Sales Return not Found!"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    elif VoucherType == "PR":
        if PurchaseReturnMaster.objects.filter(CompanyID=CompanyID, id=unq_id).exists():
            instance = PurchaseReturnMaster.objects.get(
                CompanyID=CompanyID, id=unq_id)

            serialized = PurchaseReturnPrintSerializer(instance, context={"CompanyID": CompanyID,
                                                                          "PriceRounding": PriceRounding})

            orderdDict = serialized.data
            jsnDatas = convertOrderdDict(orderdDict)

            # final_array = []
            # SalesDetails = []

            Details = jsnDatas['Details']
            count = 1
            for i in Details:
                UnitPrice = i['UnitPrice']
                Qty = i['Qty']
                ProductName = i['ProductName']
                NetAmount = i['NetAmount']
                i['id'] = count

                count = count + 1

            response_data = {
                "StatusCode": 6000,
                "data": jsnDatas,
                "company_data": company_serialized.data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Purchase Return not Found!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    elif VoucherType == "PO":
        if PurchaseOrderMaster.objects.filter(CompanyID=CompanyID, id=unq_id).exists():
            instance = PurchaseOrderMaster.objects.get(
                CompanyID=CompanyID, id=unq_id)

            serialized = PurchaseOrderPrintSerializer(instance, context={"CompanyID": CompanyID,
                                                                         "PriceRounding": PriceRounding})
            orderdDict = serialized.data
            jsnDatas = convertOrderdDict(orderdDict)

            # final_array = []
            # SalesDetails = []

            Details = jsnDatas['PurchaseOrderDetails']
            count = 1
            for i in Details:
                UnitPrice = i['UnitPrice']
                Qty = i['Qty']
                ProductName = i['ProductName']
                NetAmount = i['NetAmount']
                i['id'] = count

                count = count + 1

            response_data = {
                "StatusCode": 6000,
                "data": jsnDatas,
                "company_data": company_serialized.data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Sales Invoice not Found!"
            }

            return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def vat_report(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    serialized1 = ListSerializerforReport(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']

        sale_data_cons = []
        saleRetrn_data_cons = []
        purchase_data_cons = []
        purchaseRetrn_data_cons = []

        Total_taxbleAmt_sale = 0
        Total_taxbleAmt_saleRetrn = 0
        Total_taxbleAmt_purchase = 0
        Total_taxbleAmt_purchaseRetrn = 0

        Total_taxAmt_sale = 0
        Total_taxAmt_saleRetrn = 0
        Total_taxAmt_purchase = 0
        Total_taxAmt_purchaseRetrn = 0

        Total_netAmt_sale = 0
        Total_netAmt_saleRetrn = 0
        Total_netAmt_purchase = 0
        Total_netAmt_purchaseRetrn = 0

        Total_payable = 0

        if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, TaxType='VAT').exists():
            sales_instances = SalesMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, TaxType='VAT')

            for i_sale in sales_instances:
                sale_details = SalesDetails.objects.filter(
                    SalesMasterID=i_sale.SalesMasterID, CompanyID=CompanyID, BranchID=BranchID)
                total_taxable_sale = 0
                for i_saleDet in sale_details:
                    total_taxable_sale += i_saleDet.TaxableAmount

                LedgerName_sale = AccountLedger.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=i_sale.LedgerID).LedgerName

                sales_dic = {
                    'VoucherNo': i_sale.VoucherNo,
                    'VoucherDate': i_sale.Date,
                    'LedgerName': LedgerName_sale,
                    'TaxType': i_sale.TaxType,
                    'TaxableAmount': total_taxable_sale,
                    'TaxAmount': i_sale.TotalTax,
                    'NetAmount': i_sale.NetTotal,
                }

                sale_data_cons.append(sales_dic)

                Total_taxbleAmt_sale += total_taxable_sale
                Total_taxAmt_sale += i_sale.TotalTax
                Total_netAmt_sale += i_sale.NetTotal

        if SalesReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, TaxType='VAT').exists():
            salesRetrn_instances = SalesReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, TaxType='VAT')

            for i_saleRetn in salesRetrn_instances:
                saleRetn_details = SalesReturnDetails.objects.filter(
                    SalesReturnMasterID=i_saleRetn.SalesReturnMasterID, CompanyID=CompanyID, BranchID=BranchID)
                total_taxable_saleRetn = 0
                for i_saleRetnDet in saleRetn_details:
                    total_taxable_saleRetn += i_saleRetnDet.TaxableAmount

                LedgerName_sale = AccountLedger.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=i_saleRetn.LedgerID).LedgerName

                salesRetn_dic = {
                    'VoucherNo': i_saleRetn.VoucherNo,
                    'VoucherDate': i_saleRetn.VoucherDate,
                    'LedgerName': LedgerName_sale,
                    'TaxType': i_saleRetn.TaxType,
                    'TaxableAmount': total_taxable_saleRetn,
                    'TaxAmount': i_saleRetn.TotalTax,
                    'NetAmount': i_saleRetn.NetTotal,
                }

                saleRetrn_data_cons.append(salesRetn_dic)

                Total_taxbleAmt_saleRetrn += total_taxable_saleRetn
                Total_taxAmt_saleRetrn += i_saleRetn.TotalTax
                Total_netAmt_saleRetrn += i_saleRetn.NetTotal

        if PurchaseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, TaxType='VAT').exists():
            purchase_instances = PurchaseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, TaxType='VAT')

            for i_purchase in purchase_instances:
                purchase_details = PurchaseDetails.objects.filter(
                    PurchaseMasterID=i_purchase.PurchaseMasterID, CompanyID=CompanyID, BranchID=BranchID)
                total_taxable_purchase = 0
                for i_purchaseDet in purchase_details:
                    total_taxable_purchase += i_purchaseDet.TaxableAmount

                LedgerName_purchase = AccountLedger.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=i_purchase.LedgerID).LedgerName

                purchase_dic = {
                    'VoucherNo': i_purchase.VoucherNo,
                    'VoucherDate': i_purchase.Date,
                    'LedgerName': LedgerName_purchase,
                    'TaxType': i_purchase.TaxType,
                    'TaxableAmount': total_taxable_purchase,
                    'TaxAmount': i_purchase.TotalTax,
                    'NetAmount': i_purchase.NetTotal,
                }

                purchase_data_cons.append(purchase_dic)

                Total_taxbleAmt_purchase += total_taxable_purchase
                Total_taxAmt_purchase += i_purchase.TotalTax
                Total_netAmt_purchase += i_purchase.NetTotal

        if PurchaseReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, TaxType='VAT').exists():
            purchaseRetn_instances = PurchaseReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, TaxType='VAT')

            for i_purchaseRetn in purchaseRetn_instances:
                purchase_details = PurchaseReturnDetails.objects.filter(
                    PurchaseReturnMasterID=i_purchaseRetn.PurchaseReturnMasterID, CompanyID=CompanyID, BranchID=BranchID)
                total_taxable_purchase = 0
                for i_purchaseRetnDet in purchase_details:
                    total_taxable_purchase += i_purchaseRetnDet.TaxableAmount

                LedgerName_purchaseRetn = AccountLedger.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=i_purchaseRetn.LedgerID).LedgerName

                purchaseRetn_dic = {
                    'VoucherNo': i_purchaseRetn.VoucherNo,
                    'VoucherDate': i_purchaseRetn.VoucherDate,
                    'LedgerName': LedgerName_purchaseRetn,
                    'TaxType': i_purchaseRetn.TaxType,
                    'TaxableAmount': total_taxable_purchase,
                    'TaxAmount': i_purchaseRetn.TotalTax,
                    'NetAmount': i_purchaseRetn.NetTotal,
                }

                purchaseRetrn_data_cons.append(purchaseRetn_dic)

                Total_taxbleAmt_purchaseRetrn += total_taxable_purchase
                Total_taxAmt_purchaseRetrn += i_purchaseRetn.TotalTax
                Total_netAmt_purchaseRetrn += i_purchaseRetn.NetTotal

        total_received_taxbleAmt = float(
            Total_taxbleAmt_sale) + float(Total_taxbleAmt_purchaseRetrn)
        total_received_taxAmt = float(
            Total_taxAmt_sale) + float(Total_taxAmt_purchaseRetrn)
        total_received_netAmt = float(
            Total_netAmt_sale) + float(Total_netAmt_purchaseRetrn)

        total_paid_taxbleAmt = float(
            Total_taxbleAmt_saleRetrn) + float(Total_taxbleAmt_purchase)
        total_paid_taxAmt = float(
            Total_taxAmt_saleRetrn) + float(Total_taxAmt_purchase)
        total_paid_netAmt = float(
            Total_netAmt_saleRetrn) + float(Total_netAmt_purchase)

        grandTotal_received = total_received_taxAmt
        grandTotal_paid = total_paid_taxAmt

        total_payable = float(grandTotal_received) - float(total_paid_taxAmt)

        # request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Vat Report', 'Report', 'Vat Report Viewed successfully.', 'Vat Report Viewed successfully.')

        if sale_data_cons or saleRetrn_data_cons or purchase_data_cons or purchaseRetrn_data_cons:
            response_data = {
                "StatusCode": 6000,
                "sale_data_cons": sale_data_cons,
                "saleRetrn_data_cons": saleRetrn_data_cons,
                "purchase_data_cons": purchase_data_cons,
                "purchaseRetrn_data_cons": purchaseRetrn_data_cons,
                'Total_taxbleAmt_sale': Total_taxbleAmt_sale,
                'Total_taxbleAmt_saleRetrn': Total_taxbleAmt_saleRetrn,
                'Total_taxbleAmt_purchase': Total_taxbleAmt_purchase,
                'Total_taxbleAmt_purchaseRetrn': Total_taxbleAmt_purchaseRetrn,
                'Total_taxAmt_sale': Total_taxAmt_sale,
                'Total_taxAmt_saleRetrn': Total_taxAmt_saleRetrn,
                'Total_taxAmt_purchase': Total_taxAmt_purchase,
                'Total_taxAmt_purchaseRetrn': Total_taxAmt_purchaseRetrn,
                'Total_netAmt_sale': Total_netAmt_sale,
                'Total_netAmt_saleRetrn': Total_netAmt_saleRetrn,
                'Total_netAmt_purchase': Total_netAmt_purchase,
                'Total_netAmt_purchaseRetrn': Total_netAmt_purchaseRetrn,
                'total_received_taxbleAmt': total_received_taxbleAmt,
                'total_received_taxAmt': total_received_taxAmt,
                'total_received_netAmt': total_received_netAmt,
                'total_paid_taxbleAmt': total_paid_taxbleAmt,
                'total_paid_taxAmt': total_paid_taxAmt,
                'total_paid_netAmt': total_paid_netAmt,
                'grandTotal_received': grandTotal_received,
                'grandTotal_paid': grandTotal_paid,
                'total_payable': total_payable,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Data Not Found!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "please provide valid datas!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def stock_report(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    ProductFilter = data['ProductFilter']
    StockFilter = data['StockFilter']
    ProductID = data['ProductID']
    CategoryID = data['CategoryID']
    GroupID = data['GroupID']
    WareHouseID = data['WareHouseID']
    Barcode = data['Barcode']
    try:
        page_number = data['page_no']
    except:
        page_number = ""

    try:
        items_per_page = data['items_per_page']
    except:
        items_per_page = ""

    serialized1 = ListSerializerforReport(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']

        stockDatas = []
        stockPosting_instances = None
        StatusCode = 6000
        if WareHouseID > 0:
            if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, WareHouseID=WareHouseID, Date__gte=FromDate, Date__lte=ToDate).exists():
                stockPosting_instances = StockPosting.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, WareHouseID=WareHouseID, Date__gte=FromDate, Date__lte=ToDate)
        else:
            if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
                stockPosting_instances = StockPosting.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)

        # total_QtyIn = 0
        # total_QtyOut = 0
        # for Curt_stk in stockPosting_instances:
        #     total_QtyIn += Curt_stk.QtyIn
        #     total_QtyOut += Curt_stk.QtyOut

        # current_Stock = float(total_QtyIn) - float(total_QtyOut)
        if stockPosting_instances:
            if ProductID > 0:
                stockPosting_instances = stockPosting_instances.filter(
                    ProductID=ProductID)
            elif CategoryID > 0:
                if ProductGroup.objects.filter(CategoryID=CategoryID, CompanyID=CompanyID, BranchID=BranchID).exists():
                    group_instances = ProductGroup.objects.filter(
                        CategoryID=CategoryID, CompanyID=CompanyID, BranchID=BranchID)
                    cat_prdids = []
                    for group_i in group_instances:
                        ProductGroupID = group_i.ProductGroupID
                        if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=ProductGroupID).exists():
                            product_instances = Product.objects.filter(
                                CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=ProductGroupID)

                            for product_i in product_instances:
                                ProductID = product_i.ProductID
                                cat_prdids.append(ProductID)
                            print(cat_prdids)
                    stockPosting_instances = stockPosting_instances.filter(
                        ProductID__in=cat_prdids)
                else:
                    StatusCode = 6001

            elif GroupID > 0:
                if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=GroupID).exists():
                    product_instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=GroupID)
                    grp_prdids = []
                    for product_i in product_instances:
                        ProductID = product_i.ProductID
                        grp_prdids.append(ProductID)
                    stockPosting_instances = stockPosting_instances.filter(
                        ProductID__in=grp_prdids)
                else:
                    StatusCode = 6001
            elif Barcode:
                if PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, AutoBarcode=Barcode).exists():
                    ProductID = PriceList.objects.get(
                        CompanyID=CompanyID, BranchID=BranchID, AutoBarcode=Barcode).ProductID

                    stockPosting_instances = stockPosting_instances.filter(
                        ProductID=ProductID)
                elif PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Barcode=Barcode).exists():
                    ProductID = PriceList.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, Barcode=Barcode).first().ProductID
                    stockPosting_instances = stockPosting_instances.filter(
                        ProductID=ProductID)
                elif Product.objects.filter(CompanyID=CompanyID, ProductCode=Barcode, BranchID=BranchID).exists():
                    ProductID = Product.objects.get(
                        CompanyID=CompanyID, BranchID=BranchID, ProductCode=Barcode).ProductID
                    stockPosting_instances = stockPosting_instances.filter(
                        ProductID=ProductID)
                else:
                    StatusCode = 6001

            product_arry = []
            product_ids = stockPosting_instances.values_list('ProductID')

            # for product_id in product_ids:
            #     if product_id[0] not in product_arry:
            #         product_arry.append(product_id[0])

            final_pro_arry = []
            check_array_for_totalStock = []

            qurried_instances = stockPosting_instances.values('ProductID').annotate(
                in_stock_quantity=Sum('QtyIn') - Sum('QtyOut')).order_by('ProductID')
            for q in qurried_instances:
                pro = q['ProductID']
                TotalStock = q['in_stock_quantity']

                check_stock_dic = {
                    "ProductID": pro,
                    "TotalStock": TotalStock
                }
                check_array_for_totalStock.append(check_stock_dic)

                if StockFilter == 1:
                    final_pro_arry.append(pro)
                elif StockFilter == 2:
                    if TotalStock > 0:
                        final_pro_arry.append(pro)
                elif StockFilter == 3:
                    if TotalStock < 0:
                        final_pro_arry.append(pro)
                elif StockFilter == 4:
                    if TotalStock == 0:
                        final_pro_arry.append(pro)
                elif StockFilter == 5:
                    StockReOrder = Product.objects.get(
                        ProductID=pro, BranchID=BranchID, CompanyID=CompanyID).StockReOrder
                    if TotalStock < StockReOrder:
                        final_pro_arry.append(pro)
                elif StockFilter == 6:
                    StockMaximum = Product.objects.get(
                        ProductID=pro, BranchID=BranchID, CompanyID=CompanyID).StockMaximum
                    if TotalStock > StockMaximum:
                        final_pro_arry.append(pro)
                elif StockFilter == 7:
                    StockMinimum = Product.objects.get(
                        ProductID=pro, BranchID=BranchID, CompanyID=CompanyID).StockMinimum
                    if TotalStock < StockMinimum:
                        final_pro_arry.append(pro)
            # final_instances = StockPosting.objects.filter(pk__in=[x.pk for x in stockDatas])
            if page_number and items_per_page:
                product_instances = Product.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID__in=final_pro_arry)
                product_sort_pagination = list_pagination(
                    product_instances,
                    items_per_page,
                    page_number
                )
            # else:
            #     product_sort_pagination = Product.objects.filter(
            #         CompanyID=CompanyID, BranchID=BranchID, ProductID__in=final_pro_arry)

            stockSerializer = StockSerializer(product_sort_pagination, many=True, context={
                                              "CompanyID": CompanyID, "PriceRounding": PriceRounding, "ToDate": ToDate})

            orderdDict = stockSerializer.data
            jsnDatas = convertOrderdDict(orderdDict)

            for i in jsnDatas:
                AutoBarcode = i['AutoBarcode']
                ProductID = i['ProductID']
                ProductName = i['ProductName']
                PurchasePrice = i['PurchasePrice']
                SalesPrice = i['SalesPrice']
                UnitName = i['UnitName']
                BaseUnitName = i['BaseUnitName']
                is_BasicUnit = i['is_BasicUnit']
                MultiFactor = i['MultiFactor']

                for t in check_array_for_totalStock:
                    ProductID_inArr = t['ProductID']

                    CurrentBaseStock = t['TotalStock']
                    total_stock = CurrentBaseStock

                    if is_BasicUnit == False:
                        if MultiFactor:
                            total_stock = float(
                                CurrentBaseStock) / float(MultiFactor)

                    if ProductID == ProductID_inArr:
                        i['CurrentStock'] = total_stock
                        i['CurrentBaseStock'] = CurrentBaseStock

            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Stock Report', 'Report', 'Stock Report Viewed successfully.', 'Stock Report Viewed successfully.')
            if jsnDatas:
                msg = ""
                if StatusCode == 6001:
                    msg = "Stock Not Available"
                response_data = {
                    "StatusCode": StatusCode,
                    "data": jsnDatas,
                    "count": len(product_instances),
                    "message": msg
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "Stock Not Available"
                }

                return Response(response_data, status=status.HTTP_200_OK)
        else:
            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Stock Report',
            #              'Report', 'Stock Report Viewed Failed.', 'No data During This Time Periods.')
            response_data = {
                "StatusCode": 6001,
                "message": "No data During This Time Periods!"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "please provide valid datas!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def stock_ledger_report(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    ProductID = data['ProductID']
    WareHouseID = data['WareHouseID']
    try:
        page_number = data['page_no']
    except:
        page_number = ""

    try:
        items_per_page = data['items_per_page']
    except:
        items_per_page = ""

    serialized1 = ListSerializerforReport(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']

        stockDatas = []
        stockPosting_instances = None
        StatusCode = 6000
        virtual_array = []
        last_data = []
        ob_array = []
        Balance = 0
        OpeningBalance = 0

        if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
            stockPosting_instances = StockPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).order_by('Date', 'StockPostingID')
            if WareHouseID > 0:
                stockPosting_instances = stockPosting_instances.filter(
                    WareHouseID=WareHouseID).order_by('Date', 'StockPostingID')
            # if page_number and items_per_page:
            #     stockPosting_instances = StockPosting.objects.filter(
            #     CompanyID=CompanyID, BranchID=BranchID, WareHouseID=WareHouseID,ProductID=ProductID).order_by('Date','StockPostingID')
            #     product_sort_pagination = list_pagination(
            #         stockPosting_instances,
            #         items_per_page,
            #         page_number
            #     )

            stockSerializer = StockPostingRestSerializer(stockPosting_instances, many=True, context={
                "CompanyID": CompanyID, "PriceRounding": PriceRounding})

            orderdDict = stockSerializer.data
            jsnDatas = convertOrderdDict(orderdDict)

            for i in jsnDatas:
                Date = i['Date']
                VoucherType = i['VoucherType']
                WareHouseName = i['WareHouseName']
                UnitName = i['UnitName']
                QtyIn = i['QtyIn']
                QtyOut = i['QtyOut']
                UserName = i['UserName']

                Balance = (float(Balance) + float(QtyIn)) - \
                    float(QtyOut)

                i['Balance'] = round(Balance, PriceRounding)
                QtyIn = float(QtyIn)
                QtyOut = float(QtyOut)

                virtual_dictionary = {"Date": Date, "VoucherType": VoucherType, "WareHouseName": WareHouseName, "UnitName": UnitName, "UserName": UserName,
                                      "QtyIn": round(QtyIn, PriceRounding), "QtyOut": round(QtyOut, PriceRounding), "Balance": round(Balance, PriceRounding)}

                virtual_array.append(virtual_dictionary)

            for i in virtual_array:
                date = i["Date"]
                if FromDate > date:
                    ob_array.append(i)
                if FromDate <= date and ToDate >= date:
                    last_data.append(i)

            if ob_array:
                last_dict = ob_array[-1]
                OpeningBalance = last_dict['Balance']

            if jsnDatas:
                response_data = {
                    "StatusCode": StatusCode,
                    "data": last_data,
                    "OpeningBalance": OpeningBalance,
                    "count": len(stockPosting_instances)

                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "No data!"
                }

                return Response(response_data, status=status.HTTP_200_OK)
        else:
            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Stock Report',
            #              'Report', 'Stock Report Viewed Failed.', 'No data During This Time Periods.')
            if not ProductID:
                msg = "please select a product"
            else:
                msg = "No data During This Time Periods!"
            response_data = {
                "StatusCode": 6001,
                "message": msg
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "please provide valid datas!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def stock_report_print(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    ProductFilter = data['ProductFilter']
    StockFilter = data['StockFilter']
    ProductID = data['ProductID']
    CategoryID = data['CategoryID']
    GroupID = data['GroupID']
    WareHouseID = data['WareHouseID']
    Barcode = data['Barcode']

    FromVal = data['FromVal']
    ToVal = data['ToVal']
    # FromVal = 1
    # ToVal = 50
    if FromVal and ToVal:
        FromVal = float(FromVal)
        ToVal = float(ToVal) + 1

    serialized1 = ListSerializerforReport(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']

        stockDatas = []
        stockPosting_instances = None
        StatusCode = 6000
        if WareHouseID > 0:
            if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, WareHouseID=WareHouseID, Date__gte=FromDate, Date__lte=ToDate).exists():
                stockPosting_instances = StockPosting.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, WareHouseID=WareHouseID, Date__gte=FromDate, Date__lte=ToDate)
        else:
            if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
                stockPosting_instances = StockPosting.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)

        if stockPosting_instances:
            if ProductID > 0:
                stockPosting_instances = stockPosting_instances.filter(
                    ProductID=ProductID)
            elif CategoryID > 0:
                if ProductGroup.objects.filter(CategoryID=CategoryID, CompanyID=CompanyID, BranchID=BranchID).exists():
                    group_instances = ProductGroup.objects.filter(
                        CategoryID=CategoryID, CompanyID=CompanyID, BranchID=BranchID)
                    for group_i in group_instances:
                        ProductGroupID = group_i.ProductGroupID
                        if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=ProductGroupID).exists():
                            product_instances = Product.objects.filter(
                                CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=ProductGroupID)
                            cat_prdids = []
                            for product_i in product_instances:
                                ProductID = product_i.ProductID
                                cat_prdids.append(ProductID)
                            stockPosting_instances = stockPosting_instances.filter(
                                ProductID__in=cat_prdids)

            elif GroupID > 0:
                if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=GroupID).exists():
                    product_instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=GroupID)
                    grp_prdids = []
                    for product_i in product_instances:
                        ProductID = product_i.ProductID
                        grp_prdids.append(ProductID)
                    stockPosting_instances = stockPosting_instances.filter(
                        ProductID__in=grp_prdids)
            elif Barcode:
                if PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, AutoBarcode=Barcode).exists():
                    ProductID = PriceList.objects.get(
                        CompanyID=CompanyID, BranchID=BranchID, AutoBarcode=Barcode).ProductID

                    stockPosting_instances = stockPosting_instances.filter(
                        ProductID=ProductID)
                elif PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Barcode=Barcode).exists():
                    ProductID = PriceList.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, Barcode=Barcode).first().ProductID
                    stockPosting_instances = stockPosting_instances.filter(
                        ProductID=ProductID)
                elif Product.objects.filter(CompanyID=CompanyID, ProductCode=Barcode, BranchID=BranchID).exists():
                    ProductID = Product.objects.get(
                        CompanyID=CompanyID, BranchID=BranchID, ProductCode=Barcode).ProductID
                    stockPosting_instances = stockPosting_instances.filter(
                        ProductID=ProductID)
                else:
                    StatusCode = 6001

            product_arry = []
            product_ids = stockPosting_instances.values_list('ProductID')

            for product_id in product_ids:
                if product_id[0] not in product_arry:
                    product_arry.append(product_id[0])

            final_pro_arry = []
            check_array_for_totalStock = []
            for pro in product_arry:
                tot_QtyIn = 0
                tot_QtyOut = 0
                stockPosting_instances_pro = stockPosting_instances.filter(
                    ProductID=pro)
                for stk_ins in stockPosting_instances_pro:
                    tot_QtyIn += stk_ins.QtyIn
                    tot_QtyOut += stk_ins.QtyOut

                TotalStock = float(tot_QtyIn) - float(tot_QtyOut)

                check_stock_dic = {
                    "ProductID": pro,
                    "TotalStock": TotalStock
                }
                check_array_for_totalStock.append(check_stock_dic)

                if StockFilter == 1:
                    final_pro_arry.append(pro)
                elif StockFilter == 2:
                    if TotalStock > 0:
                        final_pro_arry.append(pro)
                elif StockFilter == 3:
                    if TotalStock < 0:
                        final_pro_arry.append(pro)
                elif StockFilter == 4:
                    if TotalStock == 0:
                        final_pro_arry.append(pro)
                elif StockFilter == 5:
                    StockReOrder = Product.objects.get(
                        ProductID=pro, BranchID=BranchID, CompanyID=CompanyID).StockReOrder
                    if TotalStock < StockReOrder:
                        final_pro_arry.append(pro)
                elif StockFilter == 6:
                    StockMaximum = Product.objects.get(
                        ProductID=pro, BranchID=BranchID, CompanyID=CompanyID).StockMaximum
                    if TotalStock > StockMaximum:
                        final_pro_arry.append(pro)
                elif StockFilter == 7:
                    StockMinimum = Product.objects.get(
                        ProductID=pro, BranchID=BranchID, CompanyID=CompanyID).StockMinimum
                    if TotalStock < StockMinimum:
                        final_pro_arry.append(pro)

            if not FromVal == "" and not ToVal == "":
                product_sort_pagination = Product.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID__in=final_pro_arry)[FromVal:ToVal]
            else:
                product_sort_pagination = Product.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID__in=final_pro_arry)

            stockSerializer = StockSerializer(product_sort_pagination, many=True, context={
                                              "CompanyID": CompanyID, "PriceRounding": PriceRounding, "ToDate": ToDate})

            orderdDict = stockSerializer.data
            jsnDatas = convertOrderdDict(orderdDict)

            for i in jsnDatas:
                AutoBarcode = i['AutoBarcode']
                ProductID = i['ProductID']
                ProductName = i['ProductName']
                PurchasePrice = i['PurchasePrice']
                SalesPrice = i['SalesPrice']
                UnitName = i['UnitName']
                BaseUnitName = i['BaseUnitName']
                is_BasicUnit = i['is_BasicUnit']
                MultiFactor = i['MultiFactor']

                for t in check_array_for_totalStock:
                    ProductID_inArr = t['ProductID']

                    CurrentBaseStock = t['TotalStock']
                    total_stock = CurrentBaseStock
                    if is_BasicUnit == False:
                        if MultiFactor:
                            total_stock = float(
                                CurrentBaseStock) / float(MultiFactor)

                    if ProductID == ProductID_inArr:
                        i['CurrentStock'] = total_stock
                        i['CurrentBaseStock'] = CurrentBaseStock

            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Stock Report', 'Report', 'Stock Report Viewed successfully.', 'Stock Report Viewed successfully.')
            # print("page_number/................")
            # print(jsnDatas)
            if jsnDatas:
                response_data = {
                    "StatusCode": StatusCode,
                    "data": jsnDatas,
                    "count": len(product_sort_pagination),
                    "message": "Product Not Found With this Barcode"
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "No data!"
                }

                return Response(response_data, status=status.HTTP_200_OK)
        else:
            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Stock Report',
            #              'Report', 'Stock Report Viewed Failed.', 'No data During This Time Periods.')
            response_data = {
                "StatusCode": 6001,
                "message": "No data During This Time Periods!"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "please provide valid datas!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def batchwise_report(request):
    today = date.today()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    ProductID = data['ProductID']
    WareHouseID = data['WareHouseID']
    BranchID = data['BranchID']

    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, WareHouseID=WareHouseID).exists():
        instances = Batch.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, WareHouseID=WareHouseID)

        if not ProductID == 0:
            instances = instances.filter(ProductID=ProductID)

        batchSerializer = BatchSerializer(instances, many=True, context={
                                          "CompanyID": CompanyID, "PriceRounding": PriceRounding, "WareHouseID": WareHouseID})
        response_data = {
            "StatusCode": 6000,
            "data": batchSerializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        # request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Stock Value Report', 'Report', 'Stock Value Report Viewed Failed.', 'No data Under This Warehouse.')
        response_data = {
            "StatusCode": 6001,
            "message": "No data Under This Warehouse!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def stockValue_report(request):
    try:
        with transaction.atomic():
            today = date.today()
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            PriceRounding = data['PriceRounding']
            ProductID = data['ProductID']
            WareHouseID = data['WareHouseID']
            BranchID = data['BranchID']
            ToDate = data['ToDate']

            try:
                CreatedUserID = data['CreatedUserID']
            except:
                CreatedUserID = 1

            try:
                page_number = data['page_no']
            except:
                page_number = ""

            try:
                items_per_page = data['items_per_page']
            except:
                items_per_page = ""

            print("items_per_page================")
            print(items_per_page)
            if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, WareHouseID=WareHouseID, Date__lte=ToDate).exists():
                stock_instances = StockPosting.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, WareHouseID=WareHouseID, Date__lte=ToDate)

                if ProductID > 0:
                    stock_instances = stock_instances.filter(
                        ProductID=ProductID)

                product_arry = []
                product_ids = stock_instances.values_list('ProductID')

                for product_id in product_ids:
                    if product_id[0] not in product_arry:
                        product_arry.append(product_id[0])

                qurried_instances = stock_instances.values('ProductID').annotate(
                    in_stock_quantity=Sum('QtyIn') - Sum('QtyOut')).order_by('ProductID')

                stock_total = 0
                for q in qurried_instances:
                    stock_total += q['in_stock_quantity']

                if page_number and items_per_page:
                    product_instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_arry)
                    product_sort_pagination = list_pagination(
                        product_instances,
                        items_per_page,
                        page_number
                    )

                # product_instances = Product.objects.filter(
                #     CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_arry)

                stockSerializer = StockSerializer(product_sort_pagination, many=True, context={
                                                  "CompanyID": CompanyID, "PriceRounding": PriceRounding, "WareHouseID": WareHouseID, "ToDate": ToDate})

                orderdDict = stockSerializer.data
                jsnDatas = convertOrderdDict(orderdDict)
                TotalQty = 0

                GrandTotalCost = 0
                final_array = []
                count = 0
                for i in jsnDatas:
                    if not float(i['Qty']) == 0:
                        cost = i['Cost']
                        qty = i['Qty']
                        TotalCost = float(cost) * float(qty)
                        items = {
                            "id": i['id'],
                            "Cost": cost,
                            "Date": ToDate,
                            "ProductName": i['ProductName'],
                            "PurchasePrice": i['PurchasePrice'],
                            "Qty": qty,
                            "SalesPrice": i['SalesPrice'],
                            "TotalCost": TotalCost,
                            "UnitName": i['UnitName'],
                            "WareHouseID": WareHouseID,
                            "WareHouseName": i['WareHouseName'],
                        }
                        count = count + 1
                        final_array.append(items)

                        # TotalQty += float(i['Qty'])
                        # GrandTotalCost += TotalCost

                # product_instances = Product.objects.filter(
                #     CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_arry)

                # stockAllSerializer = StockSerializer(product_instances, many=True, context={
                #                                   "CompanyID": CompanyID, "PriceRounding": PriceRounding, "WareHouseID": WareHouseID, "ToDate": ToDate})

                # orderdDict = stockAllSerializer.data
                # jsnDatas = convertOrderdDict(orderdDict)
                # TotalQty = 0
                # GrandTotalCost = 0

                # for i in jsnDatas:
                #     if not float(i['Qty']) == 0:
                #         cost = i['Cost']
                #         qty = i['Qty']
                #         TotalCost = float(cost) * float(qty)

                #         TotalQty += float(i['Qty'])
                #         GrandTotalCost += TotalCost

                # request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Stock Value Report', 'Report', 'Stock Value Report Viewed successfully.', 'Stock Value Report Viewed successfully.')
                pro_count = product_instances.filter()
                response_data = {
                    "StatusCode": 6000,
                    "data": final_array,
                    "count": len(product_instances),
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                # request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Stock Value Report', 'Report', 'Stock Value Report Viewed Failed.', 'No data Under This Warehouse.')
                response_data = {
                    "StatusCode": 6001,
                    "message": "No data During this periods!!!"
                }

                return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        print(page_number)
        print(items_per_page)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("======================exception test")
        print(exc_type, fname, exc_tb.tb_lineno)
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again"
        }

        # transaction.rollback()
        # transaction.set_rollback(True)
        # transaction.set_rollback(False)
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Stock Value',
                     'Report', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def stockValue_report_print(request):
    today = date.today()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    ProductID = data['ProductID']
    WareHouseID = data['WareHouseID']
    BranchID = data['BranchID']
    ToDate = data['ToDate']

    FromVal = data['FromVal']
    ToVal = data['ToVal']
    # FromVal = 1
    # ToVal = 50
    if FromVal and ToVal:
        FromVal = float(FromVal)
        ToVal = float(ToVal) + 1

    if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, WareHouseID=WareHouseID, Date__lte=ToDate).exists():
        stock_instances = StockPosting.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, WareHouseID=WareHouseID, Date__lte=ToDate)

        if ProductID > 0:
            stock_instances = stock_instances.filter(ProductID=ProductID)

        product_arry = []
        product_ids = stock_instances.values_list('ProductID')

        for product_id in product_ids:
            if product_id[0] not in product_arry:
                product_arry.append(product_id[0])

        if not FromVal == "" and not ToVal == "":
            product_instances = Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_arry)[FromVal:ToVal]
        else:
            product_instances = Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_arry)

        stockSerializer = StockSerializer(product_instances, many=True, context={
                                          "CompanyID": CompanyID, "PriceRounding": PriceRounding, "WareHouseID": WareHouseID, "ToDate": ToDate})

        orderdDict = stockSerializer.data
        jsnDatas = convertOrderdDict(orderdDict)
        TotalQty = 0

        GrandTotalCost = 0
        final_array = []
        count = 0
        for i in jsnDatas:
            if not float(i['Qty']) == 0:
                cost = i['Cost']
                qty = i['Qty']
                TotalCost = float(cost) * float(qty)
                items = {
                    "id": i['id'],
                    "Cost": cost,
                    "Date": ToDate,
                    "ProductName": i['ProductName'],
                    "PurchasePrice": i['PurchasePrice'],
                    "Qty": qty,
                    "SalesPrice": i['SalesPrice'],
                    "TotalCost": TotalCost,
                    "UnitName": i['UnitName'],
                    "WareHouseID": WareHouseID,
                    "WareHouseName": i['WareHouseName'],
                }
                count = count + 1
                final_array.append(items)
                TotalQty += float(i['Qty'])
                GrandTotalCost += TotalCost

        # request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Stock Value Report', 'Report', 'Stock Value Report Viewed successfully.', 'Stock Value Report Viewed successfully.')

        response_data = {
            "StatusCode": 6000,
            "data": final_array,
            "count": len(product_instances),
            "TotalQty": TotalQty,
            "GrandTotalCost": GrandTotalCost,
        }
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        # request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Stock Value Report', 'Report', 'Stock Value Report Viewed Failed.', 'No data Under This Warehouse.')
        response_data = {
            "StatusCode": 6001,
            "message": "No data During this periods!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def salesRegister_report(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    ProductFilter = data['ProductFilter']
    ProductID = data['ProductID']
    CategoryID = data['CategoryID']
    GroupID = data['GroupID']
    WareHouseID = data['WareHouseID']
    UserID = data['UserID']
    LedgerID = data['LedgerID']
    ProductCode = data['ProductCode']
    BarCode = data['BarCode']
    serialized1 = ListSerializerforReport(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']

        produtVal = ProductID
        groupVal = GroupID
        categoryVal = CategoryID
        wareHouseVal = WareHouseID
        userVal = str(UserID)
        branchVal = BranchID
        ledgerVal = LedgerID
        productCodeVal = ProductCode
        barCodeVal = BarCode

        if SalesMaster.objects.filter(CompanyID=CompanyID, Date__gte=FromDate, Date__lte=ToDate).exists():
            saleMaster_instances = SalesMaster.objects.filter(
                CompanyID=CompanyID, Date__gte=FromDate, Date__lte=ToDate)

            if wareHouseVal > 0:
                if saleMaster_instances.filter(WarehouseID=wareHouseVal).exists():
                    saleMaster_instances = saleMaster_instances.filter(
                        WarehouseID=wareHouseVal)
                else:
                    # request , company, log_type, user, source, action, message, description
                    activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'sales Register Report',
                                 'Report', 'sales Register Report Viewed Failed.', 'Sales is not Found in this Warehouse')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Sales is not Found in this Warehouse!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
            if userVal > "0":
                UserID = UserTable.objects.get(pk=userVal).customer.user.id
                if saleMaster_instances.filter(CreatedUserID=UserID).exists():
                    saleMaster_instances = saleMaster_instances.filter(
                        CreatedUserID=UserID)
                else:
                    # request , company, log_type, user, source, action, message, description
                    activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'sales Register Report',
                                 'Report', 'sales Register Report Viewed Failed.', 'Sales is not Found by this user')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Sales is not Found by this user!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
            if branchVal > 0:
                if saleMaster_instances.filter(BranchID=branchVal).exists():
                    saleMaster_instances = saleMaster_instances.filter(
                        BranchID=branchVal)
                else:
                    # request , company, log_type, user, source, action, message, description
                    activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'sales Register Report',
                                 'Report', 'sales Register Report Viewed Failed.', 'Sales is not Found under this Branch')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Sales is not Found under this Branch!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
            if ledgerVal > 0:
                if saleMaster_instances.filter(LedgerID=ledgerVal).exists():
                    saleMaster_instances = saleMaster_instances.filter(
                        LedgerID=ledgerVal)
                else:
                    # request , company, log_type, user, source, action, message, description
                    activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'sales Register Report',
                                 'Report', 'sales Register Report Viewed Failed.', 'Sales is not Found under this Ledger')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Sales is not Found under this Ledger!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)

            masterList = []
            final_array = []
            for i in saleMaster_instances:
                SalesMasterID = i.SalesMasterID
                BranchID = i.BranchID
                Date = i.Date
                InvoiceNo = i.VoucherNo

                salesDetail_instances = SalesDetails.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, SalesMasterID=SalesMasterID)
                if produtVal > 0:
                    salesDetail_instances = salesDetail_instances.filter(
                        ProductID=produtVal)
                elif categoryVal > 0:
                    if ProductGroup.objects.filter(CategoryID=categoryVal, CompanyID=CompanyID, BranchID=BranchID).exists():
                        group_instances = ProductGroup.objects.filter(
                            CategoryID=categoryVal, CompanyID=CompanyID, BranchID=BranchID)
                        pro_ids = []
                        for group_i in group_instances:
                            ProductGroupID = group_i.ProductGroupID
                            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=ProductGroupID).exists():
                                product_instances = Product.objects.filter(
                                    CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=ProductGroupID)
                                
                                for product_i in product_instances:
                                    ProductID = product_i.ProductID
                                    pro_ids.append(ProductID)
                        salesDetail_instances = salesDetail_instances.filter(
                            ProductID__in=pro_ids)
                    else:
                        # request , company, log_type, user, source, action, message, description
                        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'sales Register Report',
                                     'Report', 'sales Register Report Viewed Failed.', 'Sales is not Found under this Category')
                        response_data = {
                            "StatusCode": 6001,
                            "message": "Sales is not Found under this Category!"
                        }

                        return Response(response_data, status=status.HTTP_200_OK)

                elif groupVal > 0:
                    if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=groupVal).exists():
                        product_instances = Product.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=groupVal)
                        pro_ids = []
                        for product_i in product_instances:
                            ProductID = product_i.ProductID
                            pro_ids.append(ProductID)
                        salesDetail_instances = salesDetail_instances.filter(
                            ProductID__in=pro_ids)
                    else:
                        # request , company, log_type, user, source, action, message, description
                        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'sales Register Report',
                                     'Report', 'sales Register Report Viewed Failed.', 'Sales is not Found under this Group')
                        response_data = {
                            "StatusCode": 6001,
                            "message": "Sales is not Found under this Group!"
                        }

                        return Response(response_data, status=status.HTTP_200_OK)

                elif productCodeVal:
                    if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductCode=productCodeVal).exists():
                        product_instances = Product.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, ProductCode=productCodeVal)
                        pro_ids = []
                        for product_i in product_instances:
                            ProductID = product_i.ProductID
                            pro_ids.append(ProductID)
                        salesDetail_instances = salesDetail_instances.filter(
                            ProductID__in=pro_ids)
                    else:
                        # request , company, log_type, user, source, action, message, description
                        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'sales Register Report',
                                     'Report', 'sales Register Report Viewed Failed.', 'Sales is not Found under this ProductCode')
                        response_data = {
                            "StatusCode": 6001,
                            "message": "Sales is not Found under this ProductCode!"
                        }

                        return Response(response_data, status=status.HTTP_200_OK)

                elif barCodeVal:
                    if PriceList.objects.filter(Barcode=barCodeVal, CompanyID=CompanyID, BranchID=BranchID).exists():
                        ProductID = PriceList.objects.filter(
                            Barcode=barCodeVal, CompanyID=CompanyID, BranchID=BranchID).first().ProductID
                        salesDetail_instances = salesDetail_instances.filter(
                            ProductID=ProductID)
                    else:
                        # request , company, log_type, user, source, action, message, description
                        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'sales Register Report',
                                     'Report', 'sales Register Report Viewed Failed.', 'Sales is not Found under this Bracode')
                        response_data = {
                            "StatusCode": 6001,
                            "message": "Sales is not Found under this Bracode!"
                        }

                        return Response(response_data, status=status.HTTP_200_OK)
                print("salesDetail_instances---=============")
                print(salesDetail_instances)
                for s in salesDetail_instances:
                    if s.SalesMasterID == SalesMasterID:
                        if not SalesMasterID in masterList:
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
                            if s.InclusivePrice == 0 and s.GrossAmount == 0 and s.VATAmount == 0 and s.NetAmount == 0 and s.CostPerPrice == 0:
                                print("IF CONDI@@@@@@@@@@TION")
                            else:
                                final_array.append(myDict)
                            masterList.append(SalesMasterID)
                    ProductID = s.ProductID
                    PriceListID = s.PriceListID
                    BranchID = s.BranchID
                    product_instance = Product.objects.get(
                        ProductID=ProductID, BranchID=BranchID, CompanyID=CompanyID)
                    ProductCode = product_instance.ProductCode
                    ProductName = product_instance.ProductName
                    ProductGroupID = product_instance.ProductGroupID
                    ProductGroupName = ProductGroup.objects.get(
                        ProductGroupID=ProductGroupID, BranchID=BranchID, CompanyID=CompanyID).GroupName
                    Barcode = PriceList.objects.get(
                        PriceListID=PriceListID, BranchID=BranchID, CompanyID=CompanyID).Barcode
                    Qty = s.Qty
                    SalesPrice = s.InclusivePrice
                    GrossAmount = s.GrossAmount
                    VATAmount = s.VATAmount
                    NetAmount = s.NetAmount
                    Cost = s.CostPerPrice
                    Profit = float(NetAmount) - (float(Qty) * float(Cost))

                    if SalesMasterID in masterList:
                        myDict = {
                            "id": i.id,
                            "Date": "-",
                            "InvoiceNo": "-",
                            "ProductCode": ProductCode,
                            "ProductName": ProductName,
                            "ProductGroup": ProductGroupName,
                            "Barcode": Barcode,
                            "Qty": Qty,
                            "SalesPrice": round(SalesPrice, PriceRounding),
                            "GrossAmount": round(GrossAmount, PriceRounding),
                            "VATAmount": round(VATAmount, PriceRounding),
                            "NetAmount": round(NetAmount, PriceRounding),
                            "Cost": round(Cost, PriceRounding),
                            "Profit": round(Profit, PriceRounding),
                        }

                    if SalesPrice == 0 and GrossAmount == 0 and VATAmount == 0 and NetAmount == 0 and Cost == 0 and Profit == 0:
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
                TotalProfit += f['Profit']
                TotalCost += f['Cost']
                TotalNetAmt += f['NetAmount']
                TotalVatAmt += f['VATAmount']
                TotalGrossAmt += f['GrossAmount']

            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'sales Register Report',
            #              'Report', 'Sales Register Report Viewed Successfully.', 'sales Register Report Viewed Successfully.')
            if final_array:
                response_data = {
                    "StatusCode": 6000,
                    "data": final_array,
                    "TotalProfit": TotalProfit,
                    "TotalCost": TotalCost,
                    "TotalNetAmt": TotalNetAmt,
                    "TotalVatAmt": TotalVatAmt,
                    "TotalGrossAmt": TotalGrossAmt,
                }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "No data"
                }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'sales Register Report',
            #              'Report', 'Sales Register Report Viewed Failed.', 'No data During This Time Periods')
            response_data = {
                "StatusCode": 6001,
                "message": "No data During This Time Periods!!!"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "please provide valid datas!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def billWise_report(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    WareHouseID = data['WareHouseID']
    RouteID = data['RouteID']
    UserID = data['UserID']
    CustomerID = data['CustomerID']
    page_number = data['page_no']
    items_per_page = data['items_per_page']

    serialized1 = ListSerializerforReport(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']

        wareHouseVal = WareHouseID
        routeVal = RouteID
        userVal = str(UserID)
        customerVal = CustomerID

        if SalesMaster.objects.filter(CompanyID=CompanyID, Date__gte=FromDate, Date__lte=ToDate).exists():
            saleMaster_instances = SalesMaster.objects.filter(
                CompanyID=CompanyID, Date__gte=FromDate, Date__lte=ToDate)

            if wareHouseVal > 0:
                if saleMaster_instances.filter(WarehouseID=wareHouseVal).exists():
                    saleMaster_instances = saleMaster_instances.filter(
                        WarehouseID=wareHouseVal)
                else:
                    # request , company, log_type, user, source, action, message, description
                    # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Bill Wise Report',
                    #              'Report', 'Bill Wise Report Viewed Failed.', 'Sales is not Found in this Warehouse')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Sales is not Found in this Warehouse!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)

            if not userVal == '0':
                UserID = UserTable.objects.get(pk=userVal).customer.user.id
                if saleMaster_instances.filter(CreatedUserID=UserID).exists():
                    saleMaster_instances = saleMaster_instances.filter(
                        CreatedUserID=UserID)
                else:
                    # request , company, log_type, user, source, action, message, description
                    # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Bill Wise Report',
                    #              'Report', 'Bill Wise Report Viewed Failed.', 'Sales is not Found by this user')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Sales is not Found by this user!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
            if customerVal > 0:
                LedgerID = Parties.objects.get(CompanyID=CompanyID,
                                               BranchID=BranchID, PartyID=customerVal).LedgerID
                if saleMaster_instances.filter(LedgerID=LedgerID).exists():
                    saleMaster_instances = saleMaster_instances.filter(
                        LedgerID=LedgerID)
                else:
                    # request , company, log_type, user, source, action, message, description
                    # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Bill Wise Report',
                    #              'Report', 'Bill Wise Report Viewed Failed.', 'Sales is not Found under this Customer')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Sales is not Found under this Customer!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)

            if routeVal > 0:
                party_ins = Parties.objects.filter(CompanyID=CompanyID,
                                                   BranchID=BranchID, RouteID=routeVal)

                party_ledgers = []
                for i in party_ins:
                    party_ledgers.append(i.LedgerID)

                if saleMaster_instances.filter(LedgerID__in=party_ledgers).exists():
                    saleMaster_instances = saleMaster_instances.filter(
                        LedgerID__in=party_ledgers)
                else:
                    # request , company, log_type, user, source, action, message, description
                    # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Bill Wise Report',
                    #              'Report', 'Bill Wise Report Viewed Failed.', 'Sales is not Found in this Warehouse')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Sales is not Found under this Route!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)

            final_array = []
            data = []
            count = 0
            if page_number and items_per_page:
                saleMaster_instances = saleMaster_instances
                count = saleMaster_instances.count()
                billWise_sort_pagination = list_pagination(
                    saleMaster_instances,
                    items_per_page,
                    page_number
                )

                billWiseSerializer = BillWiseSerializer(billWise_sort_pagination, many=True, context={
                                          "CompanyID": CompanyID})

                data = billWiseSerializer.data
            # for sm in saleMaster_instances:
            #     Date = sm.Date
            #     VoucherNo = sm.VoucherNo
            #     TotalGrossAmt = sm.TotalGrossAmt
            #     TotalDiscount = sm.TotalDiscount
            #     VATAmount = sm.VATAmount
            #     NetTotal = sm.NetTotal
            #     GrandTotal = sm.GrandTotal
            #     SalesMasterID = sm.SalesMasterID

            #     NetAmount = float(TotalGrossAmt) - float(TotalDiscount)
            #     # stock_ins = StockPosting.objects.filter(CompanyID=CompanyID,BranchID=BranchID,VoucherMasterID=SalesMasterID,VoucherType="SI",Date__gte=FromDate,Date__lte=ToDate)
            #     # NetCost = 0
            #     # for i in stock_ins:
            #     #     cost = float(i.Rate) * float(i.QtyOut)
            #     #     NetCost += cost

            #     salesdetail_ins = SalesDetails.objects.filter(
            #         CompanyID=CompanyID, BranchID=BranchID, SalesMasterID=SalesMasterID)

            #     NetCost = 0
            #     # TotalQty = 0
            #     for sd in salesdetail_ins:
            #         CostPerItem = sd.CostPerPrice
            #         Qty_item = sd.Qty
            #         NetCost += (float(CostPerItem) * float(Qty_item))

            #         # TotalQty += sd.Qty

            #     # Profit = float(NetTotal) - (float(TotalQty) * float(NetCost))
            #     Profit = float(NetAmount) - float(NetCost)

            #     final_array.append({
            #         "id": sm.id,
            #         "Date": Date,
            #         "InvoiceNo": VoucherNo,
            #         "GrossAmount": TotalGrossAmt,
            #         "VATAmount": VATAmount,
            #         "NetAmount": NetAmount,
            #         "NetCost": NetCost,
            #         "Profit": Profit,
            #         "GrandTotal": GrandTotal
            #     })

            TotalProfit = 0
            TotalCost = 0
            TotalNetAmt = 0
            TotalVatAmt = 0
            TotalGrossAmt = 0

            # for f in final_array:
            #     TotalProfit += f['Profit']
            #     TotalCost += f['NetCost']
            #     TotalNetAmt += f['NetAmount']
            #     TotalVatAmt += f['VATAmount']
            #     TotalGrossAmt += f['GrossAmount']

            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Bill Wise Report',
            #              'Report', 'Bill Wise Report Viewed Successfully.', 'Bill Wise Report Viewed Successfully.')
            count_divided = math.ceil(float(count)/ 10)
            response_data = {
                "StatusCode": 6000,
                "data": data,
                "count": count,
                "count_divided":count_divided,
                "TotalProfit": TotalProfit,
                "TotalCost": TotalCost,
                "TotalNetAmt": TotalNetAmt,
                "TotalVatAmt": TotalVatAmt,
                "TotalGrossAmt": TotalGrossAmt,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Bill Wise Report',
            #              'Report', 'Bill Wise Report Viewed Failed.', 'No data During This Time Periods')
            response_data = {
                "StatusCode": 6001,
                "message": "No data During This Time Periods!!!"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "please provide valid datas!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def excessStock_report(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    WareHouseID = data['WareHouseID']
    CreatedUserID = data['CreatedUserID']
    serialized1 = ListSerializerforReport(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']

        if ExcessStockMaster.objects.filter(CompanyID=CompanyID, Date__gte=FromDate, Date__lte=ToDate).exists():
            excess_instances = ExcessStockMaster.objects.filter(
                CompanyID=CompanyID, Date__gte=FromDate, Date__lte=ToDate)

            if WareHouseID > 0:
                if excess_instances.filter(WarehouseID=WareHouseID).exists():
                    excess_instances = excess_instances.filter(
                        WarehouseID=WareHouseID)
                else:
                    # request , company, log_type, user, source, action, message, description
                    activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Excess Stock Report',
                                 'Report', 'Excess Stock Report Viewed Successfully.', 'Excess Stock Report Viewed Successfully')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Excess Stock is not Found in this Warehouse!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)

            serialized = ExcessStockMasterSerializer(excess_instances, many=True, context={"CompanyID": CompanyID,
                                                                                           "PriceRounding": PriceRounding})

            # request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Excess Stock Report',
                         'Report', 'Excess Stock Report Viewed Failed.', 'Excess Stock is not Found in this Warehouse')

            orderdDict = serialized.data
            jsnDatas = convertOrderdDict(orderdDict)

            GrandTotalQty = 0
            GrandTotalCost = 0
            for i in jsnDatas:
                GrandTotalQty += i['TotalQty']
                GrandTotalCost += i['GrandTotal']

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "GrandTotalQty": GrandTotalQty,
                "GrandTotalCost": GrandTotalCost
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Excess Stock Report',
                         'Report', 'Excess Stock Report Viewed Failed.', 'No data During This Time Periods')
            response_data = {
                "StatusCode": 6001,
                "message": "No data During This Time Periods!!!"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "please provide valid datas!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def shortageStock_report(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    WareHouseID = data['WareHouseID']
    CreatedUserID = data['CreatedUserID']
    serialized1 = ListSerializerforReport(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']

        if ShortageStockMaster.objects.filter(CompanyID=CompanyID, Date__gte=FromDate, Date__lte=ToDate).exists():
            shortage_instances = ShortageStockMaster.objects.filter(
                CompanyID=CompanyID, Date__gte=FromDate, Date__lte=ToDate)

            if WareHouseID > 0:
                if shortage_instances.filter(WarehouseID=WareHouseID).exists():
                    shortage_instances = shortage_instances.filter(
                        WarehouseID=WareHouseID)
                else:
                    # request , company, log_type, user, source, action, message, description
                    activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Shortage Stock Report',
                                 'Report', 'Shortage Stock Report Viewed Successfully.', 'Shortage Stock Report Viewed Successfully')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Shortage Stock is not Found in this Warehouse!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)

            serialized = ShortageStockMasterSerializer(shortage_instances, many=True, context={"CompanyID": CompanyID,
                                                                                               "PriceRounding": PriceRounding})

            # request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Shortage Stock Report',
                         'Report', 'Shortage Stock Report Viewed Failed.', 'Shortage Stock is not Found in this Warehouse')

            orderdDict = serialized.data
            jsnDatas = convertOrderdDict(orderdDict)

            GrandTotalQty = 0
            GrandTotalCost = 0
            for i in jsnDatas:
                GrandTotalQty += i['TotalQty']
                GrandTotalCost += i['GrandTotal']

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "GrandTotalQty": GrandTotalQty,
                "GrandTotalCost": GrandTotalCost
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Shortage Stock Report',
                         'Report', 'Shortage Stock Report Viewed Failed.', 'No data During This Time Periods')
            response_data = {
                "StatusCode": 6001,
                "message": "No data During This Time Periods!!!"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "please provide valid datas!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def damageStock_report(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    WareHouseID = data['WareHouseID']
    CreatedUserID = data['CreatedUserID']
    serialized1 = ListSerializerforReport(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']

        if DamageStockMaster.objects.filter(CompanyID=CompanyID, Date__gte=FromDate, Date__lte=ToDate).exists():
            damage_instances = DamageStockMaster.objects.filter(
                CompanyID=CompanyID, Date__gte=FromDate, Date__lte=ToDate)

            if WareHouseID > 0:
                if damage_instances.filter(WarehouseID=WareHouseID).exists():
                    damage_instances = damage_instances.filter(
                        WarehouseID=WareHouseID)
                else:
                    # request , company, log_type, user, source, action, message, description
                    activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Damage Stock Report',
                                 'Report', 'Damage Stock Report Viewed Successfully.', 'Damage Stock Report Viewed Successfully')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Damage Stock is not Found in this Warehouse!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)

            serialized = DamageStockMasterSerializer(damage_instances, many=True, context={"CompanyID": CompanyID,
                                                                                           "PriceRounding": PriceRounding})

            # request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Damage Stock Report',
                         'Report', 'Damage Stock Report Viewed Failed.', 'Damage Stock is not Found in this Warehouse')

            orderdDict = serialized.data
            jsnDatas = convertOrderdDict(orderdDict)

            GrandTotalQty = 0
            GrandTotalCost = 0
            for i in jsnDatas:
                GrandTotalQty += i['TotalQty']
                GrandTotalCost += i['GrandTotal']

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "GrandTotalQty": GrandTotalQty,
                "GrandTotalCost": GrandTotalCost
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Damage Stock Report',
                         'Report', 'Damage Stock Report Viewed Failed.', 'No data During This Time Periods')
            response_data = {
                "StatusCode": 6001,
                "message": "No data During This Time Periods!!!"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "please provide valid datas!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def usedStock_report(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    WareHouseID = data['WareHouseID']
    CreatedUserID = data['CreatedUserID']
    serialized1 = ListSerializerforReport(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']

        if UsedStockMaster.objects.filter(CompanyID=CompanyID, Date__gte=FromDate, Date__lte=ToDate).exists():
            used_instances = UsedStockMaster.objects.filter(
                CompanyID=CompanyID, Date__gte=FromDate, Date__lte=ToDate)

            if WareHouseID > 0:
                if used_instances.filter(WarehouseID=WareHouseID).exists():
                    used_instances = used_instances.filter(
                        WarehouseID=WareHouseID)
                else:
                    # request , company, log_type, user, source, action, message, description
                    activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Used Stock Report',
                                 'Report', 'Used Stock Report Viewed Successfully.', 'Used Stock Report Viewed Successfully')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Used Stock is not Found in this Warehouse!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)

            serialized = UsedStockMasterSerializer(used_instances, many=True, context={"CompanyID": CompanyID,
                                                                                       "PriceRounding": PriceRounding})

            # request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Used Stock Report',
                         'Report', 'Used Stock Report Viewed Failed.', 'Used Stock is not Found in this Warehouse')

            orderdDict = serialized.data
            jsnDatas = convertOrderdDict(orderdDict)

            GrandTotalQty = 0
            GrandTotalCost = 0
            for i in jsnDatas:
                GrandTotalQty += i['TotalQty']
                GrandTotalCost += i['GrandTotal']

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "GrandTotalQty": GrandTotalQty,
                "GrandTotalCost": GrandTotalCost
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Used Stock Report',
                         'Report', 'Used Stock Report Viewed Failed.', 'No data During This Time Periods')
            response_data = {
                "StatusCode": 6001,
                "message": "No data During This Time Periods!!!"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "please provide valid datas!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def salesOrder_for_salesInvoice(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    OrderNo = data['OrderNo']
    BranchID = data['BranchID']
    instance = None
    if SalesOrderMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherNo=OrderNo, IsInvoiced="N").exists():
        instance = SalesOrderMaster.objects.get(
            CompanyID=CompanyID, BranchID=BranchID, VoucherNo=OrderNo, IsInvoiced="N")
        serialized = SalesOrderMasterRestSerializer(
            instance, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding, })

        print(serialized.data)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Sales Order Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def search_sales(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    product_name = data['product_name']
    length = data['length']
    param = data['param']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instances = SalesMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

            if length < 3:
                if param == "VoucherNo":
                    instances = instances.filter(
                        (Q(VoucherNo__icontains=product_name)))[:10]
                elif param == "Date":
                    instances = instances.filter(
                        (Q(Date__icontains=product_name)))[:10]
                elif param == "CustomerName":
                    instances = instances.filter(
                        (Q(CustomerName__icontains=product_name)))[:10]
                else:
                    ledger_ids = []
                    if AccountLedger.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerName__icontains=product_name).exists():
                        ledger_ins = AccountLedger.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, LedgerName__icontains=product_name)
                        for l in ledger_ins:
                            ledger_ids.append(l.LedgerID)
                    instances = instances.filter(
                        (Q(LedgerID__in=ledger_ids)))[:10]
            else:
                if param == "VoucherNo":
                    instances = instances.filter(
                        (Q(VoucherNo__icontains=product_name)))
                elif param == "Date":
                    instances = instances.filter(
                        (Q(Date__icontains=product_name)))
                elif param == "CustomerName":
                    instances = instances.filter(
                        (Q(CustomerName__icontains=product_name)))
                else:
                    ledger_ids = []
                    if AccountLedger.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerName__icontains=product_name).exists():
                        ledger_ins = AccountLedger.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, LedgerName__icontains=product_name)
                        for l in ledger_ins:
                            ledger_ids.append(l.LedgerID)
                    instances = instances.filter((Q(LedgerID__in=ledger_ids)))

            serialized = SalesMasterRestSerializer(instances, many=True, context={
                "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding, "product_name": "product_name"})

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def product_report(request):
    from datetime import datetime
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    ProductFilter = data['ProductFilter']
    ProductID = data['ProductID']
    CategoryID = data['CategoryID']
    GroupID = data['GroupID']
    WareHouseID = data['WareHouseID']
    with_voucher = data['with_voucher']
    report_type = data['report_type']
    try:
        page_number = data['page_no']
    except:
        page_number = ""

    try:
        items_per_page = data['items_per_page']
    except:
        items_per_page = ""

    serialized1 = ListSerializerforReport(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']

        stockDatas = []
        stockPosting_instances = None
        StatusCode = 6000

        if WareHouseID > 0:
            if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, WareHouseID=WareHouseID, Date__gte=FromDate, Date__lte=ToDate).exists():
                stockPosting_instances = StockPosting.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, WareHouseID=WareHouseID, Date__gte=FromDate, Date__lte=ToDate)
        else:
            if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
                stockPosting_instances = StockPosting.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)

        if stockPosting_instances:

            if ProductID > 0:
                stockPosting_instances = stockPosting_instances.filter(
                    ProductID=ProductID)
            elif CategoryID > 0:

                print(CategoryID)
                if ProductGroup.objects.filter(CategoryID=CategoryID, CompanyID=CompanyID, BranchID=BranchID).exists():
                    group_instances = ProductGroup.objects.filter(
                        CategoryID=CategoryID, CompanyID=CompanyID, BranchID=BranchID)
                    cat_prdids = []
                    print(cat_prdids)
                    for group_i in group_instances:
                        ProductGroupID = group_i.ProductGroupID
                        print(ProductGroupID)
                        if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=ProductGroupID).exists():
                            product_instances = Product.objects.filter(
                                CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=ProductGroupID)

                            for product_i in product_instances:
                                ProductID = product_i.ProductID
                                cat_prdids.append(ProductID)
                    stockPosting_instances = stockPosting_instances.filter(
                        ProductID__in=cat_prdids)
                else:
                    StatusCode = 6001

            elif GroupID > 0:
                if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=GroupID).exists():
                    product_instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=GroupID)
                    grp_prdids = []
                    for product_i in product_instances:
                        ProductID = product_i.ProductID
                        grp_prdids.append(ProductID)
                    stockPosting_instances = stockPosting_instances.filter(
                        ProductID__in=grp_prdids)

                else:
                    StatusCode = 6001

            if report_type == 11:
                dates_array = []

                stock_dates = stockPosting_instances.values_list('Date')

                for dt in stock_dates:
                    if str(dt[0]) not in dates_array:
                        dates_array.append(str(dt[0]))

                final_data = []

                for d in dates_array:
                    stock_datas = stockPosting_instances.filter(Date=d)
                    stockPost_arry = []
                    product_arry = []

                    for s in stock_datas:
                        product_ids = stock_datas.values_list('ProductID')

                        for product_id in product_ids:
                            if product_id[0] not in product_arry:
                                product_arry.append(product_id[0])
                    for p in product_arry:
                        product_name = Product.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, ProductID=p).ProductName

                        if with_voucher:
                            for s in stock_datas:
                                if s.VoucherType not in stockPost_arry:
                                    stockPost_arry.append(s.VoucherType)

                            last_datass = []
                            for std in stockPost_arry:
                                datas = stock_datas.filter(
                                    ProductID=p, VoucherType=std)
                                totalIn = 0
                                totalOut = 0
                                total_rate = 0
                                avg_in_price = 0
                                avg_out_price = 0
                                for dw in datas:
                                    totalIn += float(dw.QtyIn)
                                    totalOut += float(dw.QtyOut)
                                    total_rate += float(dw.Rate)
                                # last_datass.append(dw)

                                if not float(totalIn) == 0:
                                    avg_in_price = float(
                                        total_rate) / float(totalIn)
                                in_total = float(avg_in_price) * float(totalIn)

                                if not float(totalOut) == 0:
                                    avg_out_price = float(
                                        total_rate) / float(totalOut)
                                out_total = float(
                                    avg_out_price) * float(totalOut)
                                if not totalIn == 0 or not totalOut == 0:
                                    final_data.append({
                                        "VoucherDate": d,
                                        "Product": product_name,
                                        "VoucherType": std,
                                        "In": totalIn,
                                        "avg_in_price": avg_in_price,
                                        "in_total": in_total,
                                        "Out": totalOut,
                                        "avg_out_price": avg_out_price,
                                        "out_total": out_total,
                                    })

                        else:
                            last_datass = stock_datas.filter(ProductID=p)
                            totalIn = 0
                            totalOut = 0
                            total_rate = 0
                            avg_in_price = 0
                            avg_out_price = 0
                            for c in last_datass:
                                totalIn += float(c.QtyIn)
                                totalOut += float(c.QtyOut)
                                total_rate += float(c.Rate)

                            if not float(totalIn) == 0:
                                avg_in_price = float(
                                    total_rate) / float(totalIn)
                            in_total = float(avg_in_price) * float(totalIn)

                            if not float(totalOut) == 0:
                                avg_out_price = float(
                                    total_rate) / float(totalOut)
                            out_total = float(avg_out_price) * float(totalOut)

                            final_data.append({
                                "VoucherDate": d,
                                "Product": product_name,
                                "VoucherType": "-",
                                "In": totalIn,
                                "avg_in_price": avg_in_price,
                                "in_total": in_total,
                                "Out": totalOut,
                                "avg_out_price": avg_out_price,
                                "out_total": out_total,
                            })

            elif report_type == 12:
                dates_array = []

                stock_dates = stockPosting_instances.values_list('Date')

                for dt in stock_dates:
                    if str(dt[0]) not in dates_array:
                        dates_array.append(str(dt[0]))
                dates_array.sort(
                    key=lambda date: datetime.strptime(date, "%Y-%m-%d"))
                start = dates_array[0].split("-")
                end = dates_array[-1].split("-")
                yr = start[0]
                mth = start[1]
                dy = start[2]
                if int(mth) < 10:
                    mth = start[1][1]

                yre = end[0]
                mthe = end[1]
                dye = end[2]
                if int(mthe) < 10:
                    mthe = end[1][1]

                # start = datetym.date(2021, 05, 28)
                import datetime
                import pandas as pd
                import numpy as np
                start = datetime.date(int(yr), int(mth), int(dy))
                end = datetime.date(int(yre), int(mthe), int(dye))

                daterange = [
                    start + datetime.timedelta(days=x)
                    for x in range(0, (end-start).days)
                ]

                df = pd.DataFrame(
                    daterange,
                    columns=["Date"]
                )
                df['Date'] = pd.to_datetime(
                    df['Date']) + pd.to_timedelta(0, unit='d')
                df = df.groupby(
                    [pd.Grouper(key='Date', freq='W-SAT')]
                ).sum().reset_index().sort_values('Date')

                arr = df.to_numpy()

                new_arr = []
                for i in arr:
                    i = str(i).replace("[", '')
                    i = str(i).replace("\'", '')
                    i = str(i).replace("\'", '')
                    i = str(i).replace("]", '')
                    new_arr.append(i)

                end_dates = []
                for na in new_arr:
                    va = na.split("T")
                    end_dates.append(va[0])

                from datetime import datetime
                date_arrays = []
                for dar in dates_array:
                    date_object_d = datetime.strptime(dar, '%Y-%m-%d').date()
                    date_arrays.append(date_object_d)
                end_date_arrays = []
                for edt in end_dates:
                    date_object_e = datetime.strptime(edt, '%Y-%m-%d').date()
                    end_date_arrays.append(date_object_e)

                startin_date = date_arrays[0]
                date_weeks = []
                import datetime
                for ed in end_date_arrays:
                    date_object_ss = datetime.datetime.strptime(
                        str(ed), '%Y-%m-%d').date()
                    for i in range(7):
                        date_weeks.append(str(date_object_ss))
                        date_object_ss = date_object_ss - \
                            datetime.timedelta(days=1)
                N = 7
                date_week_group = [date_weeks[n:n+N]
                                   for n in range(0, len(date_weeks), N)]

                list_list_from_date = []
                for week_group in date_week_group:
                    list_from_date = []
                    # print(week_group)
                    for fr_date in dates_array:
                        if fr_date in week_group:
                            list_from_date.append(fr_date)

                    list_list_from_date.append(list_from_date)

                final_data = []
                print("----------------------////")
                print(list_list_from_date)
                for d in list_list_from_date:
                    if d:
                        if d[0] == d[-1]:
                            final_data.append({
                                # "VoucherDate" : d,
                                "Product": d[0],
                                "VoucherType": "",
                                "In": "",
                                "avg_in_price": "",
                                "in_total": "",
                                "Out": "",
                                "avg_out_price": "",
                                "out_total": "",
                                "heading": True
                            })
                        else:
                            final_data.append({
                                # "VoucherDate" : d,
                                "Product": d[0] + " To " + d[-1],
                                "VoucherType": "",
                                "In": "",
                                "avg_in_price": "",
                                "in_total": "",
                                "Out": "",
                                "avg_out_price": "",
                                "out_total": "",
                                "heading": True
                            })

                    stock_datas = stockPosting_instances.filter(Date__in=d)
                    stockPost_arry = []
                    product_arry = []

                    for s in stock_datas:
                        product_ids = stock_datas.values_list('ProductID')

                        for product_id in product_ids:
                            if product_id[0] not in product_arry:
                                product_arry.append(product_id[0])
                    for p in product_arry:
                        product_name = Product.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, ProductID=p).ProductName

                        if with_voucher:
                            for s in stock_datas:
                                if s.VoucherType not in stockPost_arry:
                                    stockPost_arry.append(s.VoucherType)

                            last_datass = []
                            for std in stockPost_arry:
                                datas = stock_datas.filter(
                                    ProductID=p, VoucherType=std)
                                totalIn = 0
                                totalOut = 0
                                total_rate = 0
                                avg_in_price = 0
                                avg_out_price = 0
                                for dw in datas:
                                    totalIn += float(dw.QtyIn)
                                    totalOut += float(dw.QtyOut)
                                    total_rate += float(dw.Rate)
                                # last_datass.append(dw)

                                if not float(totalIn) == 0:
                                    avg_in_price = float(
                                        total_rate) / float(totalIn)
                                in_total = float(avg_in_price) * float(totalIn)

                                if not float(totalOut) == 0:
                                    avg_out_price = float(
                                        total_rate) / float(totalOut)
                                out_total = float(
                                    avg_out_price) * float(totalOut)
                                if not totalIn == 0 or not totalOut == 0:
                                    final_data.append({
                                        # "VoucherDate" : d,
                                        "Product": product_name,
                                        "VoucherType": std,
                                        "In": totalIn,
                                        "avg_in_price": avg_in_price,
                                        "in_total": in_total,
                                        "Out": totalOut,
                                        "avg_out_price": avg_out_price,
                                        "out_total": out_total,
                                    })

                        else:
                            last_datass = stock_datas.filter(ProductID=p)
                            totalIn = 0
                            totalOut = 0
                            total_rate = 0
                            avg_in_price = 0
                            avg_out_price = 0
                            for c in last_datass:
                                totalIn += float(c.QtyIn)
                                totalOut += float(c.QtyOut)
                                total_rate += float(c.Rate)

                            if not float(totalIn) == 0:
                                avg_in_price = float(
                                    total_rate) / float(totalIn)
                            in_total = float(avg_in_price) * float(totalIn)

                            if not float(totalOut) == 0:
                                avg_out_price = float(
                                    total_rate) / float(totalOut)
                            out_total = float(avg_out_price) * float(totalOut)

                            final_data.append({
                                # "VoucherDate" : d,
                                "Product": product_name,
                                "VoucherType": "-",
                                "In": totalIn,
                                "avg_in_price": avg_in_price,
                                "in_total": in_total,
                                "Out": totalOut,
                                "avg_out_price": avg_out_price,
                                "out_total": out_total,
                            })

            else:
                print("----------------------")
                dates_array = []

                stock_dates = stockPosting_instances.values_list('Date')

                for dt in stock_dates:
                    if str(dt[0]) not in dates_array:
                        dates_array.append(str(dt[0]))
                print(dates_array)
                monthly_dates = []
                jan = []
                feb = []
                mar = []
                apr = []
                may = []
                jun = []
                july = []
                aug = []
                sep = []
                octb = []
                nov = []
                dec = []

                for dta in dates_array:
                    if dta[5:7] == "01":
                        jan.append(dta)
                    elif dta[5:7] == "02":
                        feb.append(dta)
                    elif dta[5:7] == "03":
                        mar.append(dta)
                    elif dta[5:7] == "04":
                        apr.append(dta)
                    elif dta[5:7] == "05":
                        may.append(dta)
                    elif dta[5:7] == "06":
                        jun.append(dta)
                    elif dta[5:7] == "07":
                        july.append(dta)
                    elif dta[5:7] == "08":
                        aug.append(dta)
                    elif dta[5:7] == "09":
                        sep.append(dta)
                    elif dta[5:7] == "10":
                        octb.append(dta)
                    elif dta[5:7] == "11":
                        nov.append(dta)
                    elif dta[5:7] == "12":
                        dec.append(dta)

                monthly_dates.append(jan)
                monthly_dates.append(feb)
                monthly_dates.append(mar)
                monthly_dates.append(apr)
                monthly_dates.append(may)
                monthly_dates.append(jun)
                monthly_dates.append(july)
                monthly_dates.append(aug)
                monthly_dates.append(sep)
                monthly_dates.append(octb)
                monthly_dates.append(nov)
                monthly_dates.append(dec)
                final_data = []
                mnth_array = []
                for monthly in monthly_dates:
                    for m in monthly:
                        if m and m[5:7] not in mnth_array:
                            mnth = m[5:7]
                            mnth_array.append(mnth)
                            month_name = get_month(mnth)
                            final_data.append({
                                "Product": month_name,
                                "VoucherType": "",
                                "In": "",
                                "avg_in_price": "",
                                "in_total": "",
                                "Out": "",
                                "avg_out_price": "",
                                "out_total": "",
                                "heading": True
                            })

                    stock_datas = stockPosting_instances.filter(
                        Date__in=monthly)
                    stockPost_arry = []
                    product_arry = []

                    for s in stock_datas:
                        product_ids = stock_datas.values_list('ProductID')

                        for product_id in product_ids:
                            if product_id[0] not in product_arry:
                                product_arry.append(product_id[0])
                    for p in product_arry:
                        product_name = Product.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, ProductID=p).ProductName

                        if with_voucher:
                            for s in stock_datas:
                                if s.VoucherType not in stockPost_arry:
                                    stockPost_arry.append(s.VoucherType)

                            last_datass = []
                            for std in stockPost_arry:
                                datas = stock_datas.filter(
                                    ProductID=p, VoucherType=std)
                                totalIn = 0
                                totalOut = 0
                                total_rate = 0
                                avg_in_price = 0
                                avg_out_price = 0
                                for dw in datas:
                                    totalIn += float(dw.QtyIn)
                                    totalOut += float(dw.QtyOut)
                                    total_rate += float(dw.Rate)
                                # last_datass.append(dw)

                                if not float(totalIn) == 0:
                                    avg_in_price = float(
                                        total_rate) / float(totalIn)
                                in_total = float(avg_in_price) * float(totalIn)

                                if not float(totalOut) == 0:
                                    avg_out_price = float(
                                        total_rate) / float(totalOut)
                                out_total = float(
                                    avg_out_price) * float(totalOut)
                                if not totalIn == 0 or not totalOut == 0:
                                    final_data.append({
                                        # "VoucherDate" : d,
                                        "Product": product_name,
                                        "VoucherType": std,
                                        "In": totalIn,
                                        "avg_in_price": avg_in_price,
                                        "in_total": in_total,
                                        "Out": totalOut,
                                        "avg_out_price": avg_out_price,
                                        "out_total": out_total,
                                    })

                        else:
                            last_datass = stock_datas.filter(ProductID=p)
                            totalIn = 0
                            totalOut = 0
                            total_rate = 0
                            avg_in_price = 0
                            avg_out_price = 0
                            for c in last_datass:
                                totalIn += float(c.QtyIn)
                                totalOut += float(c.QtyOut)
                                total_rate += float(c.Rate)

                            if not float(totalIn) == 0:
                                avg_in_price = float(
                                    total_rate) / float(totalIn)
                            in_total = float(avg_in_price) * float(totalIn)

                            if not float(totalOut) == 0:
                                avg_out_price = float(
                                    total_rate) / float(totalOut)
                            out_total = float(avg_out_price) * float(totalOut)

                            final_data.append({
                                # "VoucherDate" : d,
                                "Product": product_name,
                                "VoucherType": "-",
                                "In": totalIn,
                                "avg_in_price": avg_in_price,
                                "in_total": in_total,
                                "Out": totalOut,
                                "avg_out_price": avg_out_price,
                                "out_total": out_total,
                            })

            # if page_number and items_per_page:
            #     product_instances = Product.objects.filter(
            #         CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_arry)
            #     product_sort_pagination = list_pagination(
            #         product_instances,
            #         items_per_page,
            #         page_number
            #     )
            # else:
            #     product_sort_pagination = Product.objects.filter(
            #         CompanyID=CompanyID, BranchID=BranchID, ProductID__in=final_pro_arry)

            if final_data:
                print("===========-------------============")
                # print(final_data)
                response_data = {
                    "StatusCode": StatusCode,
                    "data": final_data,
                    # "count": len(product_instances),
                    "message": "Success"
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "No data!"
                }

                return Response(response_data, status=status.HTTP_200_OK)
        else:
            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Stock Report',
            #              'Report', 'Stock Report Viewed Failed.', 'No data During This Time Periods.')
            response_data = {
                "StatusCode": 6001,
                "message": "No data During This Time Periods!"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "please provide valid datas!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def sales_summary_report(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    UserID = data['UserID']
    LedgerID = data['LedgerID']
    WarehouseID = data['WarehouseID']
    serialized1 = ListSerializerforReport(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']

        if SalesMaster.objects.filter(CompanyID=CompanyID, Date__gte=FromDate, Date__lte=ToDate).exists():
            saleMaster_instances = SalesMaster.objects.filter(
                CompanyID=CompanyID, Date__gte=FromDate, Date__lte=ToDate)

            if not WarehouseID == 0:
                if saleMaster_instances.filter(WarehouseID=WarehouseID).exists():
                    saleMaster_instances = saleMaster_instances.filter(
                        WarehouseID=WarehouseID)
                else:
                    # request , company, log_type, user, source, action, message, description
                    # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Bill Wise Report',
                    #              'Report', 'Bill Wise Report Viewed Failed.', 'Sales is not Found in this Warehouse')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Sales is not Found in this Warehouse!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)

            if not UserID == '0':
                UserID = UserTable.objects.get(pk=UserID).customer.user.id
                if saleMaster_instances.filter(CreatedUserID=UserID).exists():
                    saleMaster_instances = saleMaster_instances.filter(
                        CreatedUserID=UserID)
                else:
                    # request , company, log_type, user, source, action, message, description
                    # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Bill Wise Report',
                    #              'Report', 'Bill Wise Report Viewed Failed.', 'Sales is not Found by this user')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Sales is not Found by this user!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
            if not LedgerID == 0:
                if saleMaster_instances.filter(LedgerID=LedgerID).exists():
                    saleMaster_instances = saleMaster_instances.filter(
                        LedgerID=LedgerID)
                else:
                    # request , company, log_type, user, source, action, message, description
                    # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Bill Wise Report',
                    #              'Report', 'Bill Wise Report Viewed Failed.', 'Sales is not Found under this Customer')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Sales is not Found under this Customer!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)

            serialized = SalesSummaryReportSerializer(saleMaster_instances, many=True, context={
                "CompanyID": CompanyID, "PriceRounding": PriceRounding, "FromDate": FromDate, "ToDate": ToDate})

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Bill Wise Report',
            #              'Report', 'Bill Wise Report Viewed Failed.', 'No data During This Time Periods')
            response_data = {
                "StatusCode": 6001,
                "message": "No data During This Time Periods!!!"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "please provide valid datas!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def supplier_vs_product_report(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    ProductID = data['ProductID']
    PartyID = data['PartyID']
    filterValue = data['filterValue']

    try:
        page_number = data['page_no']
    except:
        page_number = ""

    try:
        items_per_page = data['items_per_page']
    except:
        items_per_page = ""
    serialized1 = ListSerializerforReport(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']

        if filterValue == 1:
            if Parties.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PartyID=PartyID).exists():
                party_LedgerID = Parties.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, PartyID=PartyID).LedgerID

                productids = []
                if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, LedgerID=party_LedgerID).exists():
                    salesMaster_instance = SalesMaster.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, LedgerID=party_LedgerID)
                    sales_master_ids = salesMaster_instance.values_list(
                        'SalesMasterID', flat=True)
                    if SalesDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SalesMasterID__in=sales_master_ids).exists():
                        salesDetail_instances = SalesDetails.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, SalesMasterID__in=sales_master_ids)
                        sales_productids = salesDetail_instances.values_list(
                            'ProductID', flat=True)
                        sales_diff_ids = list(
                            set(sales_productids) - set(productids))
                        productids.extend(sales_diff_ids)

                if PurchaseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, LedgerID=party_LedgerID).exists():
                    purchaseMaster_instance = PurchaseMaster.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, LedgerID=party_LedgerID)
                    purchase_master_ids = purchaseMaster_instance.values_list(
                        'PurchaseMasterID', flat=True)
                    if PurchaseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PurchaseMasterID__in=purchase_master_ids).exists():
                        purchaseDetail_instances = PurchaseDetails.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, PurchaseMasterID__in=purchase_master_ids)
                        purchase_productids = purchaseDetail_instances.values_list(
                            'ProductID', flat=True)
                        purchase_diff_ids = list(
                            set(purchase_productids) - set(productids))
                        productids.extend(purchase_diff_ids)

                if SalesReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, LedgerID=party_LedgerID).exists():
                    salesReturnMaster_instance = SalesReturnMaster.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, LedgerID=party_LedgerID)
                    salesReturn_master_ids = salesReturnMaster_instance.values_list(
                        'SalesReturnMasterID', flat=True)
                    if SalesReturnDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SalesReturnMasterID__in=salesReturn_master_ids).exists():
                        salesReturnDetail_instances = SalesReturnDetails.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, SalesReturnMasterID__in=salesReturn_master_ids)
                        salesReturn_productids = salesReturnDetail_instances.values_list(
                            'ProductID', flat=True)
                        salesReturn_diff_ids = list(
                            set(salesReturn_productids) - set(productids))
                        productids.extend(salesReturn_diff_ids)

                if PurchaseReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, LedgerID=party_LedgerID).exists():
                    purchaseReturnMaster_instance = PurchaseReturnMaster.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, LedgerID=party_LedgerID)
                    purchaseReturn_master_ids = purchaseReturnMaster_instance.values_list(
                        'PurchaseReturnMasterID', flat=True)
                    if PurchaseReturnDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PurchaseReturnMasterID__in=purchaseReturn_master_ids).exists():
                        purchaseReturnDetail_instances = PurchaseReturnDetails.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, PurchaseReturnMasterID__in=purchaseReturn_master_ids)
                        purchaseReturn_productids = purchaseReturnDetail_instances.values_list(
                            'ProductID', flat=True)
                        purchaseReturn_diff_ids = list(
                            set(purchaseReturn_productids) - set(productids))
                        productids.extend(purchaseReturn_diff_ids)

                if page_number and items_per_page:
                    prodct_ins = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID__in=productids)
                    party_sort_pagination = list_pagination(
                        prodct_ins,
                        items_per_page,
                        page_number
                    )
                serialized = SupplierVsProductReportSerializer(party_sort_pagination, many=True, context={
                                                               "CompanyID": CompanyID, "PriceRounding": PriceRounding, "FromDate": FromDate, "ToDate": ToDate})
                response_data = {
                    "StatusCode": 6000,
                    "data": serialized.data,
                    "count": len(prodct_ins),
                }

        else:
            ledger_ids = []
            party_ids = []
            if SalesDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
                salesDetail_instances = SalesDetails.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                sales_master_ids = salesDetail_instances.values_list(
                    'SalesMasterID', flat=True)
                sales_masterIns = SalesMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, SalesMasterID__in=sales_master_ids)
                sales_partyIds = sales_masterIns.values_list(
                    'LedgerID', flat=True)
                sales_diff_ids = list(set(sales_partyIds) - set(ledger_ids))
                ledger_ids.extend(sales_diff_ids)

            if PurchaseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
                purchaseDetail_instances = PurchaseDetails.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                purchase_master_ids = purchaseDetail_instances.values_list(
                    'PurchaseMasterID', flat=True)
                purchase_masterIns = PurchaseMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, PurchaseMasterID__in=purchase_master_ids)
                purchase_partyIds = purchase_masterIns.values_list(
                    'LedgerID', flat=True)
                purchase_diff_ids = list(
                    set(purchase_partyIds) - set(ledger_ids))
                ledger_ids.extend(purchase_diff_ids)

            if SalesReturnDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
                salesReturnDetail_instances = SalesReturnDetails.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                salesReturn_master_ids = salesReturnDetail_instances.values_list(
                    'SalesReturnMasterID', flat=True)
                salesReturn_masterIns = SalesReturnMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, SalesReturnMasterID__in=salesReturn_master_ids)
                salesReturn_partyIds = salesReturn_masterIns.values_list(
                    'LedgerID', flat=True)
                salesReturn_diff_ids = list(
                    set(salesReturn_partyIds) - set(ledger_ids))
                ledger_ids.extend(salesReturn_diff_ids)

            if PurchaseReturnDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
                purchaseReturnDetail_instances = PurchaseReturnDetails.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                purchaseReturn_master_ids = purchaseReturnDetail_instances.values_list(
                    'PurchaseReturnMasterID', flat=True)
                purchaseReturn_masterIns = PurchaseReturnMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, PurchaseReturnMasterID__in=purchaseReturn_master_ids)
                purchaseReturn_partyIds = purchaseReturn_masterIns.values_list(
                    'LedgerID', flat=True)
                purchaseReturn_diff_ids = list(
                    set(purchaseReturn_partyIds) - set(ledger_ids))
                ledger_ids.extend(purchaseReturn_diff_ids)

            if AccountLedger.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID__in=ledger_ids, AccountGroupUnder=29).exists():
                party_ledger_ins = AccountLedger.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID__in=ledger_ids, AccountGroupUnder=29)
                party_ids = party_ledger_ins.values_list('LedgerID', flat=True)

            if Parties.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID__in=party_ids).exists():
                if page_number and items_per_page:
                    party_ins = Parties.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, LedgerID__in=party_ids)
                    party_sort_pagination = list_pagination(
                        party_ins,
                        items_per_page,
                        page_number
                    )
                serialized = ProductVsSuppliersReportSerializer(party_sort_pagination, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding,
                                                                                                           "FromDate": FromDate, "ToDate": ToDate, "ProductID": ProductID})

                response_data = {
                    "StatusCode": 6000,
                    "data": serialized.data,
                    "count": len(party_ins),
                }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "no Datas"
                }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "please provide valid datas!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def inventory_flow_report(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    WarehouseID = data['WarehouseID']
    serialized1 = ListSerializerforReport(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']

        final_data = []
        if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__lt=FromDate).exists():
            stockPostInstance = StockPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Date__lt=FromDate)
            if not WarehouseID == 0:
                stockPostInstance = stockPostInstance.filter(
                    WareHouseID=WarehouseID)
            opening_stock_qtyinSum = stockPostInstance.aggregate(Sum('QtyIn'))
            opening_stock_qtyoutSum = stockPostInstance.aggregate(
                Sum('QtyOut'))
            opening_stock_qtyinSum = opening_stock_qtyinSum['QtyIn__sum']
            opening_stock_qtyoutSum = opening_stock_qtyoutSum['QtyOut__sum']
            opening_stock = float(opening_stock_qtyinSum) - \
                float(opening_stock_qtyoutSum)
            my_dict = {
                "particular": "Opening Stock",
                "amount": round(opening_stock, PriceRounding),
            }
            final_data.append(my_dict)

        else:
            my_dict = {
                "particular": "Opening Stock",
                "amount": 0,
            }
            final_data.append(my_dict)

        if LedgerPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID=69, VoucherType="PI", Date__gte=FromDate, Date__lte=ToDate).exists():
            ledgerPostInstance = LedgerPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=69, VoucherType="PI", Date__gte=FromDate, Date__lte=ToDate)
            purchase_sm = ledgerPostInstance.aggregate(Sum('Debit'))
            purchase_sm = purchase_sm['Debit__sum']
            my_dict = {
                "particular": "Purchase",
                "amount": round(purchase_sm, PriceRounding),
            }
            final_data.append(my_dict)
        else:
            my_dict = {
                "particular": "Purchase",
                "amount": 0,
            }
            final_data.append(my_dict)

        if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, VoucherType="ST").exists():
            stock_ins = StockPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, VoucherType="ST")
            if not WarehouseID == 0:
                stock_ins = stock_ins.filter(WareHouseID=WarehouseID)
            stock_transfer_qtyinSum = stock_ins.aggregate(Sum('QtyIn'))
            stock_transfer_qtyoutSum = stock_ins.aggregate(Sum('QtyOut'))
            stock_transfer_qtyinSum = stock_transfer_qtyinSum['QtyIn__sum']
            stock_transfer_qtyoutSum = stock_transfer_qtyoutSum['QtyOut__sum']
            stock_transfr_sum = float(
                stock_transfer_qtyinSum) - float(stock_transfer_qtyoutSum)

            my_dict = {
                "particular": "Stock Transfer",
                "amount": round(stock_transfr_sum, PriceRounding),
            }
            final_data.append(my_dict)
        else:
            my_dict = {
                "particular": "Stock Transfer",
                "amount": 0,
            }
            final_data.append(my_dict)

        # stock value
        stock_value = get_stock_value(
            CompanyID, BranchID, FromDate, ToDate, WarehouseID, PriceRounding)
        my_dict = {
            "particular": "Stock Value",
            "amount": round(stock_value, PriceRounding),
        }
        final_data.append(my_dict)

        Voucher_types = ["ES", "SS"]
        if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, VoucherType__in=Voucher_types).exists():
            stock_ins = StockPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, VoucherType__in=Voucher_types)
            if not WarehouseID == 0:
                stock_ins = stock_ins.filter(WareHouseID=WarehouseID)
            stock_adjust_qtyinSum = stock_ins.aggregate(Sum('QtyIn'))
            stock_transfer_qtyoutSum = stock_ins.aggregate(Sum('QtyOut'))
            stock_adjust_qtyinSum = stock_adjust_qtyinSum['QtyIn__sum']
            stock_transfer_qtyoutSum = stock_transfer_qtyoutSum['QtyOut__sum']
            stock_adjust_sum = float(
                stock_adjust_qtyinSum) - float(stock_transfer_qtyoutSum)

            my_dict = {
                "particular": "Stock Adjustment",
                "amount": round(stock_adjust_sum, PriceRounding),
            }
            final_data.append(my_dict)
        else:
            my_dict = {
                "particular": "Stock Adjustment",
                "amount": 0,
            }
            final_data.append(my_dict)

        account_ledgers_supp = AccountLedger.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, AccountGroupUnder=29, IsActive=True)
        supplier_ids = account_ledgers_supp.values_list('LedgerID', flat=True)
        account_ledgers_cust = AccountLedger.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, AccountGroupUnder=10, IsActive=True)
        customer_ids = account_ledgers_cust.values_list('LedgerID', flat=True)
        if LedgerPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__lt=ToDate, LedgerID__in=supplier_ids).exists():
            ledger_supp_ins = LedgerPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Date__lt=ToDate, LedgerID__in=supplier_ids)
            ledger_supp_Debit_sum = ledger_supp_ins.aggregate(Sum('Debit'))
            ledger_supp_Credit_sum = ledger_supp_ins.aggregate(Sum('Credit'))
            ledger_supp_Debit_sum = ledger_supp_Debit_sum['Debit__sum']
            ledger_supp_Credit_sum = ledger_supp_Credit_sum['Credit__sum']
            supp_balance = float(ledger_supp_Debit_sum) - \
                float(ledger_supp_Credit_sum)

            my_dict = {
                "particular": "Supplier Balance",
                "amount": round(supp_balance, PriceRounding),
            }
            final_data.append(my_dict)
        else:
            my_dict = {
                "particular": "Supplier Balance",
                "amount": 0,
            }
            final_data.append(my_dict)

        if LedgerPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__lt=ToDate, LedgerID__in=customer_ids).exists():
            ledger_cust_ins = LedgerPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Date__lt=ToDate, LedgerID__in=customer_ids)
            ledger_cust_Debit_sum = ledger_cust_ins.aggregate(Sum('Debit'))
            ledger_cust_Credit_sum = ledger_cust_ins.aggregate(Sum('Credit'))
            ledger_cust_Debit_sum = ledger_cust_Debit_sum['Debit__sum']
            ledger_cust_Credit_sum = ledger_cust_Credit_sum['Credit__sum']
            cust_balance = float(ledger_cust_Debit_sum) - \
                float(ledger_cust_Credit_sum)

            my_dict = {
                "particular": "Customer Balance",
                "amount": round(cust_balance, PriceRounding),
            }
            final_data.append(my_dict)
        else:
            my_dict = {
                "particular": "Customer Balance",
                "amount": 0,
            }
            final_data.append(my_dict)

        Pay_voucherTypes = ["CP", "CR"]
        if LedgerPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, LedgerID__in=supplier_ids, VoucherType__in=Pay_voucherTypes).exists():
            ledger_supp_pay_ins = LedgerPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lt=ToDate, LedgerID__in=supplier_ids, VoucherType__in=Pay_voucherTypes)
            ledger_supp_pay_Debit_sum = ledger_supp_pay_ins.aggregate(
                Sum('Debit'))
            supp_payment = ledger_supp_pay_Debit_sum['Debit__sum']

            my_dict = {
                "particular": "Supplier Payment",
                "amount": round(supp_payment, PriceRounding),
            }
            final_data.append(my_dict)
        else:
            my_dict = {
                "particular": "Supplier Payment",
                "amount": 0,
            }
            final_data.append(my_dict)

        if LedgerPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, LedgerID__in=customer_ids, VoucherType__in=Pay_voucherTypes).exists():
            ledger_cust_pay_ins = LedgerPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lt=ToDate, LedgerID__in=customer_ids, VoucherType__in=Pay_voucherTypes)
            ledger_supp_pay_Credit_sum = ledger_cust_pay_ins.aggregate(
                Sum('Credit'))
            cust_payment = ledger_supp_pay_Credit_sum['Credit__sum']

            my_dict = {
                "particular": "Customer Payment",
                "amount": round(cust_payment, PriceRounding),
            }
            final_data.append(my_dict)
        else:
            my_dict = {
                "particular": "Customer Payment",
                "amount": 0,
            }
            final_data.append(my_dict)

        if final_data:
            response_data = {
                "StatusCode": 6000,
                "data": final_data
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "no datas!!!"
            }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "please provide valid datas!!!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def sales_grand_totals(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    BranchID = data['BranchID']
    ToDate = data['ToDate']
    date_time_obj = datetime.datetime.strptime(ToDate, '%Y-%m-%d')
    dates_list = get_date_list(date_time_obj)
    print("================================")
    print(dates_list)
    final_data = []
    for d in dates_list:
        year = d.year
        month = d.month
        print(year)
        print(month)
        month_name = d.strftime("%B")
        if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__month=month, Date__year=year).exists():
            sales_instances = SalesMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Date__month=month, Date__year=year)
            sum_grand_totals = sales_instances.aggregate(Sum('GrandTotal'))
            sum_grand_totals = sum_grand_totals['GrandTotal__sum']
            myDict = {
                "Month": month_name,
                "Total": round(sum_grand_totals, 2),
            }
            final_data.append(myDict)
        else:
            myDict = {
                "Month": month_name,
                "Total": 0.0,
            }
            final_data.append(myDict)

    print(final_data)
    if final_data:
        response_data = {
            "StatusCode": 6000,
            "data": final_data
        }
    else:
        response_data = {
            "StatusCode": 6001,
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def sales_filterd_sales_order(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    BranchID = data['BranchID']
    OrderCustomerID = data['OrderCustomerID']
    OrderFromDate = data['OrderFromDate']
    OrderToDate = data['OrderToDate']
    if SalesOrderMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID=OrderCustomerID, IsInvoiced="N").exists():
        sales_order_instances = SalesOrderMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=OrderCustomerID, IsInvoiced="N")
        if OrderFromDate and OrderToDate:
            sales_order_instances = sales_order_instances.filter(
                Date__gte=OrderFromDate, Date__lte=OrderToDate)
        if sales_order_instances:
            serialized = FilterOrderSerializer(
                sales_order_instances, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "no datas"
            }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "no datas---"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def get_order_details(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    BranchID = data['BranchID']
    order_vouchers = data['order_vouchers']

    if SalesOrderMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherNo__in=order_vouchers, IsInvoiced="N").exists():
        sales_order_instances = SalesOrderMaster.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, VoucherNo__in=order_vouchers, IsInvoiced="N")
        master_ids = sales_order_instances.values_list(
            'SalesOrderMasterID', flat=True)
        sales_order_details = SalesOrderDetails.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, SalesOrderMasterID__in=master_ids)

        serialized = SalesOrderDetailsRestSerializer(sales_order_details, many=True, context={
                                                     "CompanyID": CompanyID, "PriceRounding": PriceRounding})

        orderdDict = serialized.data
        jsnDatas = convertOrderdDict(orderdDict)
        final_data = []
        pro_ids = []
        pro_dict = []
        for i in jsnDatas:
            ProductID = i['ProductID']
            Qty = i['Qty']
            if not ProductID in pro_ids:
                final_data.append(i)
                pro_ids.append(ProductID)
                pro_dict.append({
                    "ProductID": ProductID,
                    "ProductName": i['ProductName']
                })
            else:
                for f in final_data:
                    if f['ProductID'] == ProductID:
                        qty = f['Qty']
                        f['Qty'] = float(qty) + float(Qty)

        response_data = {
            "StatusCode": 6000,
            "data": final_data,
            "pro_dict": pro_dict
        }

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "no datas---"
        }

    return Response(response_data, status=status.HTTP_200_OK)
