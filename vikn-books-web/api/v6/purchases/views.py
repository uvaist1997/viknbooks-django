from brands.models import VoucherNoTable,State,PurchaseMaster, AccountLedger_Log,PurchaseMaster_Log, PurchaseDetails, PurchaseDetails_Log, StockPosting, LedgerPosting, StockPosting_Log,\
    LedgerPosting_Log, PurchaseDetailsDummy, StockRate, PriceList, StockTrans, ProductGroup, Brand, Unit, Warehouse, PurchaseReturnMaster, OpeningStockMaster,\
    Product, Batch, AccountLedger, UserTable, GeneralSettings, PurchaseOrderMaster, Parties

from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v6.purchases.serializers import PurchaseMasterSerializer, PurchaseMasterRestSerializer, PurchaseMasterRest1Serializer, PurchaseDetailsSerializer,\
    PurchaseDetailsRestSerializer, PurchaseMasterReportSerializer, PurchaseMasterForReturnSerializer

from api.v6.brands.serializers import ListSerializer
from api.v6.purchases.functions import generate_serializer_errors,purchase_gst_excel_data,export_to_excel_purchase_gst
from rest_framework import status
from api.v6.sales.serializers import ListSerializerforReport
from api.v6.purchases.functions import purchase_taxgroup_excel_data,export_to_excel_purchase_taxgroup,get_auto_id, get_auto_idMaster, get_auto_StockRateID, get_auto_StockTransID
from api.v6.sales.functions import get_auto_stockPostid
from api.v6.accountLedgers.functions import get_auto_LedgerPostid
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from main.functions import get_company, activity_log
from api.v6.purchaseReturns.serializers import PurchaseReturnMasterRestSerializer
from api.v6.purchaseOrders.serializers import PurchaseOrderMasterRestSerializer
from api.v6.products.functions import get_auto_AutoBatchCode,update_stock
from api.v6.sales.functions import get_Genrate_VoucherNo
import os,re,sys
from api.v6.ledgerPosting.functions import convertOrderdDict
from django.db.models import Q, Prefetch, Max
from django.db import transaction, IntegrityError
from api.v6.accountLedgers.functions import get_LedgerCode, get_auto_id as generated_ledgerID,UpdateLedgerBalance
import math
from main.functions import update_voucher_table
from django.http import HttpResponse
import xlwt
from xlwt import Workbook,XFStyle,Borders, Pattern, Font, easyxf,Alignment

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
def create_purchase(request):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CreatedUserID = data['CreatedUserID']
            PriceRounding = data['PriceRounding']
            CompanyID = get_company(CompanyID)

            today = datetime.datetime.now()
            BranchID = data['BranchID']
            VoucherNo = data['VoucherNo']
            RefferenceBillNo = data['RefferenceBillNo']
            Date = data['Date']
            VenderInvoiceDate = data['VenderInvoiceDate']
            CreditPeriod = data['CreditPeriod']
            LedgerID = data['LedgerID']
            PriceCategoryID = data['PriceCategoryID']
            EmployeeID = data['EmployeeID']
            PurchaseAccount = data['PurchaseAccount']
            CustomerName = data['CustomerName']
            Address1 = data['Address1']
            Address2 = data['Address2']
            Address3 = data['Address3']
            Notes = data['Notes']
            FinacialYearID = data['FinacialYearID']
            TotalGrossAmt = data['TotalGrossAmt']
            TotalTax = data['TotalTax']
            NetTotal = data['NetTotal']
            AddlDiscPercent = data['AddlDiscPercent']
            AddlDiscAmt = data['AddlDiscAmt']
            AdditionalCost = data['AdditionalCost']
            TotalDiscount = data['TotalDiscount']
            GrandTotal = data['GrandTotal']
            RoundOff = data['RoundOff']
            TransactionTypeID = data['TransactionTypeID']
            WarehouseID = data['WarehouseID']
            IsActive = data['IsActive']
            TaxID = data['TaxID']
            TaxType = data['TaxType']
            VATAmount = data['VATAmount']
            SGSTAmount = data['SGSTAmount']
            CGSTAmount = data['CGSTAmount']
            IGSTAmount = data['IGSTAmount']
            TAX1Amount = data['TAX1Amount']
            TAX2Amount = data['TAX2Amount']
            TAX3Amount = data['TAX3Amount']
            BillDiscPercent = data['BillDiscPercent']
            BillDiscAmt = data['BillDiscAmt']
            Balance = data['Balance']

            BatchID = data['BatchID']

            try:
                BankAmount = float(data['BankAmount'])
            except:
                BankAmount = 0

            # BankAmount = round(BankAmount, PriceRounding)

            try:
                CashReceived = data['CashReceived']
            except:
                CashReceived = 0

            try:
                CardTypeID = data['CardTypeID']
            except:
                CardTypeID = 0

            try:
                CardNumber = data['CardNumber']
            except:
                CardNumber = 0

            VoucherType = "PI"
            # VoucherNo Updated
            try:
                PreFix = data['PreFix']
            except:
                PreFix = "PI"

            try:
                Seperator = data['Seperator']
            except:
                Seperator = ""

            try:
                InvoiceNo = data['InvoiceNo']
            except:
                InvoiceNo = 1

            Action = "A"

            try:
                OrderNo = data['OrderNo']
            except:
                OrderNo = "SO0"

            purchaseDetails = data["PurchaseDetails"]
            TotalTaxableAmount = 0
            for i in purchaseDetails:
                TotalTaxableAmount += float(i['TaxableAmount'])

            if PurchaseOrderMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherNo=OrderNo, IsInvoiced="N").exists():
                order_instance = PurchaseOrderMaster.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, VoucherNo=OrderNo, IsInvoiced="N")
                order_instance.IsInvoiced = "I"
                order_instance.save()

            def max_id():
                general_settings_id = GeneralSettings.objects.filter(
                    CompanyID=CompanyID).aggregate(Max('GeneralSettingsID'))
                general_settings_id = general_settings_id.get(
                    'GeneralSettingsID__max', 0)
                general_settings_id += 1
                return general_settings_id

            try:
                ShowTotalTaxInPurchase = data['ShowTotalTaxInPurchase']
                is_except = False
            except:
                ShowTotalTaxInPurchase = False
                is_except = True

            if is_except == False:
                if not GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowTotalTaxInPurchase").exists():
                    GeneralSettings.objects.create(
                        CompanyID=CompanyID,
                        GeneralSettingsID=max_id(),
                        SettingsType="ShowTotalTaxInPurchase",
                        SettingsValue=ShowTotalTaxInPurchase,
                        BranchID=1, GroupName="Inventory",
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        Action=Action
                    )
                else:
                    GeneralSettings.objects.filter(
                        CompanyID=CompanyID,
                        SettingsType="ShowTotalTaxInPurchase"
                    ).update(
                        SettingsValue=ShowTotalTaxInPurchase,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        Action=Action
                    )

            AllowCashReceiptMorePurchaseAmt = data['AllowCashReceiptMorePurchaseAmt']

            # checking voucher number already exist
            VoucherNoLow = VoucherNo.lower()
            is_voucherExist = False
            insts = PurchaseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True

            check_VoucherNoAutoGenerate = False
            is_PurchaseOK = True

            if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="VoucherNoAutoGenerate").exists():
                check_VoucherNoAutoGenerate = GeneralSettings.objects.get(
                    CompanyID=CompanyID, SettingsType="VoucherNoAutoGenerate").SettingsValue

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

            # ===================================
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
                PurchaseTax = data['PurchaseTax']
            except:
                PurchaseTax = 0

            try:
                Country_of_Supply = data['Country_of_Supply']
            except:
                Country_of_Supply = ""

            try:
                State_of_Supply = data['State_of_Supply']
            except:
                State_of_Supply = ""

            try:
                GST_Treatment = data['GST_Treatment']
            except:
                GST_Treatment = ""

            try:
                VAT_Treatment = data['VAT_Treatment']
            except:
                VAT_Treatment = ""

            # ===================================
            if is_voucherExist == True and check_VoucherNoAutoGenerate == "True":
                VoucherNo = get_Genrate_VoucherNo(
                    PurchaseMaster, BranchID, CompanyID, "PI")
                is_PurchaseOK = True
            elif is_voucherExist == False:
                is_PurchaseOK = True
            else:
                is_PurchaseOK = False

            if is_PurchaseOK:
                PurchaseMasterID = get_auto_idMaster(
                    PurchaseMaster, BranchID, CompanyID)

                if AllowCashReceiptMorePurchaseAmt == True or AllowCashReceiptMorePurchaseAmt == "true":
                    CashAmount = float(CashReceived)
                elif float(Balance) < 0:
                    CashAmount = float(GrandTotal) - float(BankAmount)
                else:
                    CashAmount = float(CashReceived)

                update_voucher_table(CompanyID,CreatedUserID,VoucherType,PreFix,Seperator, InvoiceNo)

                PurchaseMaster_Log.objects.create(
                    TransactionID=PurchaseMasterID,
                    TotalTaxableAmount=TotalTaxableAmount,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    RefferenceBillNo=RefferenceBillNo,
                    Date=Date,
                    VenderInvoiceDate=VenderInvoiceDate,
                    CreditPeriod=CreditPeriod,
                    LedgerID=LedgerID,
                    PriceCategoryID=PriceCategoryID,
                    EmployeeID=EmployeeID,
                    PurchaseAccount=PurchaseAccount,
                    CustomerName=CustomerName,
                    Address1=Address1,
                    Address2=Address2,
                    Address3=Address3,
                    Notes=Notes,
                    FinacialYearID=FinacialYearID,
                    TotalGrossAmt=TotalGrossAmt,
                    TotalTax=TotalTax,
                    NetTotal=NetTotal,
                    AddlDiscPercent=AddlDiscPercent,
                    AddlDiscAmt=AddlDiscAmt,
                    AdditionalCost=AdditionalCost,
                    TotalDiscount=TotalDiscount,
                    GrandTotal=GrandTotal,
                    RoundOff=RoundOff,
                    TransactionTypeID=TransactionTypeID,
                    WarehouseID=WarehouseID,
                    IsActive=IsActive,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    TaxID=TaxID,
                    TaxType=TaxType,
                    VATAmount=VATAmount,
                    SGSTAmount=SGSTAmount,
                    CGSTAmount=CGSTAmount,
                    IGSTAmount=IGSTAmount,
                    TAX1Amount=TAX1Amount,
                    TAX2Amount=TAX2Amount,
                    TAX3Amount=TAX3Amount,
                    BillDiscPercent=BillDiscPercent,
                    BillDiscAmt=BillDiscAmt,
                    Balance=Balance,
                    CompanyID=CompanyID,
                    CashReceived=CashReceived,
                    CashAmount=CashAmount,
                    BankAmount=BankAmount,
                    CardTypeID=CardTypeID,
                    CardNumber=CardNumber,
                    CashID=CashID,
                    BankID=BankID,
                    ShippingCharge=ShippingCharge,
                    shipping_tax_amount=shipping_tax_amount,
                    TaxTypeID=TaxTypeID,
                    SAC=SAC,
                    PurchaseTax=PurchaseTax,
                    Country_of_Supply=Country_of_Supply,
                    State_of_Supply=State_of_Supply,
                    GST_Treatment=GST_Treatment,
                    VAT_Treatment=VAT_Treatment,
                )

                instance = PurchaseMaster.objects.create(
                    PurchaseMasterID=PurchaseMasterID,
                    TotalTaxableAmount=TotalTaxableAmount,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    RefferenceBillNo=RefferenceBillNo,
                    Date=Date,
                    VenderInvoiceDate=VenderInvoiceDate,
                    CreditPeriod=CreditPeriod,
                    LedgerID=LedgerID,
                    PriceCategoryID=PriceCategoryID,
                    EmployeeID=EmployeeID,
                    PurchaseAccount=PurchaseAccount,
                    CustomerName=CustomerName,
                    Address1=Address1,
                    Address2=Address2,
                    Address3=Address3,
                    Notes=Notes,
                    FinacialYearID=FinacialYearID,
                    TotalGrossAmt=TotalGrossAmt,
                    TotalTax=TotalTax,
                    NetTotal=NetTotal,
                    AddlDiscPercent=AddlDiscPercent,
                    AddlDiscAmt=AddlDiscAmt,
                    AdditionalCost=AdditionalCost,
                    TotalDiscount=TotalDiscount,
                    GrandTotal=GrandTotal,
                    RoundOff=RoundOff,
                    TransactionTypeID=TransactionTypeID,
                    WarehouseID=WarehouseID,
                    IsActive=IsActive,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    TaxID=TaxID,
                    TaxType=TaxType,
                    VATAmount=VATAmount,
                    SGSTAmount=SGSTAmount,
                    CGSTAmount=CGSTAmount,
                    IGSTAmount=IGSTAmount,
                    TAX1Amount=TAX1Amount,
                    TAX2Amount=TAX2Amount,
                    TAX3Amount=TAX3Amount,
                    BillDiscPercent=BillDiscPercent,
                    BillDiscAmt=BillDiscAmt,
                    Balance=Balance,
                    CompanyID=CompanyID,
                    CashReceived=CashReceived,
                    CashAmount=CashAmount,
                    BankAmount=BankAmount,
                    CardTypeID=CardTypeID,
                    CardNumber=CardNumber,
                    CashID=CashID,
                    BankID=BankID,
                    ShippingCharge=ShippingCharge,
                    shipping_tax_amount=shipping_tax_amount,
                    TaxTypeID=TaxTypeID,
                    SAC=SAC,
                    PurchaseTax=PurchaseTax,
                    Country_of_Supply=Country_of_Supply,
                    State_of_Supply=State_of_Supply,
                    GST_Treatment=GST_Treatment,
                    VAT_Treatment=VAT_Treatment,
                )

                account_group = AccountLedger.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).AccountGroupUnder


                # new posting starting from here
                # if float(shipping_tax_amount) > 0:
                #     if AccountLedger.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerName="Shipping Charges Purchase").exists():
                #         RelativeLedgerID = AccountLedger.objects.get(
                #             CompanyID=CompanyID, BranchID=BranchID, LedgerName="Shipping Charges Purchase").LedgerID
                #     else:
                #         RelativeLedgerID = generated_ledgerID(
                #             AccountLedger, BranchID, CompanyID)
                #         ShippingChargeLedgerCode = get_LedgerCode(
                #             AccountLedger, BranchID, CompanyID)

                #         AccountLedger.objects.create(
                #             LedgerID=RelativeLedgerID,
                #             BranchID=BranchID,
                #             LedgerName="Shipping Charges Purchase",
                #             LedgerCode=ShippingChargeLedgerCode,
                #             AccountGroupUnder=49,
                #             OpeningBalance=0,
                #             CrOrDr="Cr",
                #             Notes=Notes,
                #             IsActive=True,
                #             IsDefault=True,
                #             CreatedDate=today,
                #             UpdatedDate=today,
                #             Action=Action,
                #             CreatedUserID=CreatedUserID,
                #             CompanyID=CompanyID,
                #         )

                #         AccountLedger_Log.objects.create(
                #             BranchID=BranchID,
                #             TransactionID=RelativeLedgerID,
                #             LedgerName="Shipping Charges Purchase",
                #             LedgerCode=ShippingChargeLedgerCode,
                #             AccountGroupUnder=49,
                #             OpeningBalance=0,
                #             CrOrDr="Cr",
                #             Notes=Notes,
                #             IsActive=True,
                #             IsDefault=True,
                #             CreatedDate=today,
                #             UpdatedDate=today,
                #             Action=Action,
                #             CreatedUserID=CreatedUserID,
                #             CompanyID=CompanyID,
                #         )
                #     LedgerPostingID = get_auto_LedgerPostid(
                #         LedgerPosting, BranchID, CompanyID)

                #     LedgerPosting.objects.create(
                #         LedgerPostingID=LedgerPostingID,
                #         BranchID=BranchID,
                #         Date=Date,
                #         VoucherMasterID=PurchaseMasterID,
                #         VoucherType=VoucherType,
                #         VoucherNo=VoucherNo,
                #         LedgerID=PurchaseAccount,
                #         RelatedLedgerID=RelativeLedgerID,
                #         Credit=shipping_tax_amount,
                #         IsActive=IsActive,
                #         Action=Action,
                #         CreatedUserID=CreatedUserID,
                #         CreatedDate=today,
                #         UpdatedDate=today,
                #         CompanyID=CompanyID,
                #     )

                #     LedgerPosting_Log.objects.create(
                #         TransactionID=LedgerPostingID,
                #         BranchID=BranchID,
                #         Date=Date,
                #         VoucherMasterID=PurchaseMasterID,
                #         VoucherType=VoucherType,
                #         VoucherNo=VoucherNo,
                #         LedgerID=PurchaseAccount,
                #         RelatedLedgerID=RelativeLedgerID,
                #         Credit=shipping_tax_amount,
                #         IsActive=IsActive,
                #         Action=Action,
                #         CreatedUserID=CreatedUserID,
                #         CreatedDate=today,
                #         UpdatedDate=today,
                #         CompanyID=CompanyID,
                #     )

                #     LedgerPostingID = get_auto_LedgerPostid(
                #         LedgerPosting, BranchID, CompanyID)

                #     LedgerPosting.objects.create(
                #         LedgerPostingID=LedgerPostingID,
                #         BranchID=BranchID,
                #         Date=Date,
                #         VoucherMasterID=PurchaseMasterID,
                #         VoucherType=VoucherType,
                #         VoucherNo=VoucherNo,
                #         LedgerID=RelativeLedgerID,
                #         RelatedLedgerID=PurchaseAccount,
                #         Debit=shipping_tax_amount,
                #         IsActive=IsActive,
                #         Action=Action,
                #         CreatedUserID=CreatedUserID,
                #         CreatedDate=today,
                #         UpdatedDate=today,
                #         CompanyID=CompanyID,
                #     )

                #     LedgerPosting_Log.objects.create(
                #         TransactionID=LedgerPostingID,
                #         BranchID=BranchID,
                #         Date=Date,
                #         VoucherMasterID=PurchaseMasterID,
                #         VoucherType=VoucherType,
                #         VoucherNo=VoucherNo,
                #         LedgerID=RelativeLedgerID,
                #         RelatedLedgerID=PurchaseAccount,
                #         Debit=shipping_tax_amount,
                #         IsActive=IsActive,
                #         Action=Action,
                #         CreatedUserID=CreatedUserID,
                #         CreatedDate=today,
                #         UpdatedDate=today,
                #         CompanyID=CompanyID,
                #     )


                # new posting starting from here
                if TaxType == 'VAT':
                    if float(VATAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=54,
                            RelatedLedgerID=PurchaseAccount,
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
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=54,
                            RelatedLedgerID=PurchaseAccount,
                            Debit=VATAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(CompanyID,BranchID,54,PurchaseMasterID,VoucherType,VATAmount,"Dr","create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=54,
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
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=54,
                            Credit=VATAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,VATAmount,"Cr","create")

                elif TaxType == 'GST Intra-state B2B':
                    if float(CGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=36,
                            RelatedLedgerID=PurchaseAccount,
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
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=36,
                            RelatedLedgerID=PurchaseAccount,
                            Debit=CGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(CompanyID,BranchID,36,PurchaseMasterID,VoucherType,CGSTAmount,"Dr","create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=36,
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
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=36,
                            Credit=CGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,CGSTAmount,"Cr","create")

                    if float(SGSTAmount) > 0:

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=42,
                            RelatedLedgerID=PurchaseAccount,
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
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=42,
                            RelatedLedgerID=PurchaseAccount,
                            Debit=SGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(CompanyID,BranchID,42,PurchaseMasterID,VoucherType,SGSTAmount,"Dr","create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=42,
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
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=42,
                            Credit=SGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,SGSTAmount,"Cr","create")

                elif TaxType == 'GST Inter-state B2B':
                    if float(IGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=39,
                            RelatedLedgerID=PurchaseAccount,
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
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=39,
                            RelatedLedgerID=PurchaseAccount,
                            Debit=IGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(CompanyID,BranchID,39,PurchaseMasterID,VoucherType,IGSTAmount,"Dr","create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=39,
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
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=39,
                            Credit=IGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,IGSTAmount,"Cr","create")

                if not TaxType == 'Import':
                    if float(TAX1Amount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=45,
                            RelatedLedgerID=PurchaseAccount,
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
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=45,
                            RelatedLedgerID=PurchaseAccount,
                            Debit=TAX1Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(CompanyID,BranchID,45,PurchaseMasterID,VoucherType,TAX1Amount,"Dr","create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=45,
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
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=45,
                            Credit=TAX1Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,TAX1Amount,"Cr","create")

                    if float(TAX2Amount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=48,
                            RelatedLedgerID=PurchaseAccount,
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
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=48,
                            RelatedLedgerID=PurchaseAccount,
                            Debit=TAX2Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(CompanyID,BranchID,48,PurchaseMasterID,VoucherType,TAX2Amount,"Dr","create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=48,
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
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=48,
                            Credit=TAX2Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,TAX2Amount,"Cr","create")

                    if float(TAX3Amount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=51,
                            RelatedLedgerID=PurchaseAccount,
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
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=51,
                            RelatedLedgerID=PurchaseAccount,
                            Debit=TAX3Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(CompanyID,BranchID,51,PurchaseMasterID,VoucherType,TAX3Amount,"Dr","create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=51,
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
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=51,
                            Credit=TAX3Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,TAX3Amount,"Cr","create")

                if float(RoundOff) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=77,
                        RelatedLedgerID=PurchaseAccount,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=77,
                        RelatedLedgerID=PurchaseAccount,
                        Debit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,77,PurchaseMasterID,VoucherType,RoundOff,"Dr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=77,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=77,
                        Credit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,RoundOff,"Cr","create")

                if float(RoundOff) < 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    RoundOff = abs(float(RoundOff))

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=77,
                        RelatedLedgerID=PurchaseAccount,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=77,
                        RelatedLedgerID=PurchaseAccount,
                        Credit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,77,PurchaseMasterID,VoucherType,RoundOff,"Cr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=77,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=77,
                        Debit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,RoundOff,"Dr","create")

                if float(TotalDiscount) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=83,
                        RelatedLedgerID=PurchaseAccount,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=83,
                        RelatedLedgerID=PurchaseAccount,
                        Credit=TotalDiscount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,83,PurchaseMasterID,VoucherType,TotalDiscount,"Cr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=83,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=83,
                        Debit=TotalDiscount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,TotalDiscount,"Dr","create")

                # credit sales start here
                if float(CashReceived) == 0 and float(BankAmount) == 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
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
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=LedgerID,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,GrandTotal,"Dr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=PurchaseAccount,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=PurchaseAccount,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,LedgerID,PurchaseMasterID,VoucherType,GrandTotal,"Cr","create")

                # credit sales end here

                # customer with cash and customer with partial cash start here
                elif (account_group == 10 or account_group == 29 or account_group == 32) and float(CashReceived) > 0 and float(BankAmount) == 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
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
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=LedgerID,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,GrandTotal,"Dr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=PurchaseAccount,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=PurchaseAccount,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,LedgerID,PurchaseMasterID,VoucherType,GrandTotal,"Cr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
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
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
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

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,CashID,PurchaseMasterID,VoucherType,CashAmount,"Cr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
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
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
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

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,LedgerID,PurchaseMasterID,VoucherType,CashAmount,"Dr","create")

                # customer with cash and customer with partial cash end here

                # customer with bank and customer with partial bank start here
                elif (account_group == 10 or account_group == 29 or account_group == 32) and float(CashReceived) == 0 and float(BankAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
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
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=LedgerID,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,GrandTotal,"Dr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=PurchaseAccount,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=PurchaseAccount,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,LedgerID,PurchaseMasterID,VoucherType,GrandTotal,"Cr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
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
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
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

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,BankID,PurchaseMasterID,VoucherType,BankAmount,"Cr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
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
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
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

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,LedgerID,PurchaseMasterID,VoucherType,BankAmount,"Dr","create")

                # customer with bank and customer with partial bank end here

                # bank with cash and cash with cash start here
                elif (account_group == 8 or account_group == 9) and float(CashReceived) > 0 and float(BankAmount) == 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
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
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=CashID,
                        Debit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,CashAmount,"Dr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=PurchaseAccount,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=PurchaseAccount,
                        Credit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,CashID,PurchaseMasterID,VoucherType,CashAmount,"Cr","create")

                    csh_value = float(GrandTotal) - float(CashReceived)
                    if not float(csh_value) == 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                                LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=LedgerID,
                            RelatedLedgerID=PurchaseAccount,
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
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=LedgerID,
                            RelatedLedgerID=PurchaseAccount,
                            Credit=csh_value,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(CompanyID,BranchID,LedgerID,PurchaseMasterID,VoucherType,csh_value,"Cr","create")

                        LedgerPostingID = get_auto_LedgerPostid(
                                LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
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
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=LedgerID,
                            Debit=csh_value,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,csh_value,"Dr","create")
                # bank with cash and cash with cash end here

                # bank with bank and cash with bank start here
                elif (account_group == 8 or account_group == 9) and float(CashReceived) == 0 and float(BankAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
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
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=BankID,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,BankAmount,"Dr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=PurchaseAccount,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=PurchaseAccount,
                        Credit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,BankID,PurchaseMasterID,VoucherType,BankAmount,"Cr","create")

                    bnk_value = float(GrandTotal) - float(BankAmount)
                    if not float(bnk_value) == 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                                LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=LedgerID,
                            RelatedLedgerID=PurchaseAccount,
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
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=LedgerID,
                            RelatedLedgerID=PurchaseAccount,
                            Credit=bnk_value,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(CompanyID,BranchID,LedgerID,PurchaseMasterID,VoucherType,bnk_value,"Cr","create")

                        LedgerPostingID = get_auto_LedgerPostid(
                                LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
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
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=LedgerID,
                            Debit=bnk_value,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,bnk_value,"Dr","create")
                # bank with bank and cash with bank end here

                # customer with partial cash /bank and customer with cash/bank
                elif (account_group == 10 or account_group == 29 or account_group == 32) and float(CashReceived) > 0 and float(BankAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
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
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=LedgerID,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,GrandTotal,"Dr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=PurchaseAccount,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=PurchaseAccount,
                        Credit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,LedgerID,PurchaseMasterID,VoucherType,GrandTotal,"Cr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
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
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
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

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,CashID,PurchaseMasterID,VoucherType,CashAmount,"Cr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
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
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
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

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,LedgerID,PurchaseMasterID,VoucherType,CashAmount,"Dr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
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
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
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

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,BankID,PurchaseMasterID,VoucherType,BankAmount,"Cr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
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
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
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

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,LedgerID,PurchaseMasterID,VoucherType,BankAmount,"Dr","create")
                # customer with partial cash /bank and customer with cash/bank

                # cash with cash/bank start here
                elif (account_group == 9 or account_group == 8) and float(CashReceived) > 0 and float(BankAmount) > 0:

                    total_received = float(CashReceived) + float(BankAmount)
                    Balance_amt = float(GrandTotal) - float(total_received)
                    if not float(Balance_amt) == 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
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
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=LedgerID,
                            Debit=Balance_amt,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,Balance_amt,"Dr","create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=LedgerID,
                            RelatedLedgerID=PurchaseAccount,
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
                            Date=Date,
                            VoucherMasterID=PurchaseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=LedgerID,
                            RelatedLedgerID=PurchaseAccount,
                            Credit=Balance_amt,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(CompanyID,BranchID,LedgerID,PurchaseMasterID,VoucherType,Balance_amt,"Cr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=PurchaseAccount,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=BankID,
                        RelatedLedgerID=PurchaseAccount,
                        Credit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,BankID,PurchaseMasterID,VoucherType,BankAmount,"Cr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
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
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=BankID,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,BankAmount,"Dr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
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
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=CashID,
                        Debit=CashReceived,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,CashReceived,"Dr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=PurchaseAccount,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=CashID,
                        RelatedLedgerID=PurchaseAccount,
                        Credit=CashReceived,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,CashID,PurchaseMasterID,VoucherType,CashReceived,"Cr","create")

                # cash with cash/bank end here
                # new posting ending here

                purchaseDetails = data["PurchaseDetails"]

                for purchaseDetail in purchaseDetails:

                    # PurchaseMasterID = serialized.data['PurchaseMasterID']
                    ProductID = purchaseDetail['ProductID']

                    if ProductID:
                        Qty = purchaseDetail['Qty']
                        FreeQty = purchaseDetail['FreeQty']
                        UnitPrice = float(purchaseDetail['UnitPrice'])
                        InclusivePrice = float(
                            purchaseDetail['InclusivePrice'])
                        RateWithTax = float(purchaseDetail['RateWithTax'])
                        CostPerItem = float(purchaseDetail['CostPerItem'])
                        PriceListID = purchaseDetail['PriceListID']
                        DiscountPerc = float(purchaseDetail['DiscountPerc'])
                        DiscountAmount = float(
                            purchaseDetail['DiscountAmount'])
                        AddlDiscPerc = float(purchaseDetail['AddlDiscPerc'])
                        AddlDiscAmt = float(purchaseDetail['AddlDiscAmt'])
                        GrossAmount = float(purchaseDetail['GrossAmount'])
                        TaxableAmount = float(purchaseDetail['TaxableAmount'])
                        VATPerc = float(purchaseDetail['VATPerc'])
                        VATAmount = float(purchaseDetail['VATAmount'])
                        SGSTPerc = float(purchaseDetail['SGSTPerc'])
                        SGSTAmount = float(purchaseDetail['SGSTAmount'])
                        CGSTPerc = float(purchaseDetail['CGSTPerc'])
                        CGSTAmount = float(purchaseDetail['CGSTAmount'])
                        IGSTPerc = float(purchaseDetail['IGSTPerc'])
                        IGSTAmount = float(purchaseDetail['IGSTAmount'])
                        NetAmount = float(purchaseDetail['NetAmount'])
                        TAX1Perc = float(purchaseDetail['TAX1Perc'])
                        TAX1Amount = float(purchaseDetail['TAX1Amount'])
                        TAX2Perc = float(purchaseDetail['TAX2Perc'])
                        TAX2Amount = float(purchaseDetail['TAX2Amount'])
                        TAX3Perc = float(purchaseDetail['TAX3Perc'])
                        TAX3Amount = float(purchaseDetail['TAX3Amount'])
                        BatchCode = purchaseDetail['BatchCode']
                        is_inclusive = purchaseDetail['is_inclusive']

                        try:
                            ManufactureDate = purchaseDetail['ManufactureDate']

                        except:
                            ManufactureDate = None

                        try:
                            ExpiryDate = purchaseDetail['ExpiryDate']
                        except:
                            ExpiryDate = None

                        try:
                            SalesPrice = purchaseDetail['SalesPrice']
                        except:
                            SalesPrice = None

                        if not SalesPrice == None:
                            SalesPrice = float(purchaseDetail['SalesPrice'])

                        try:
                            ProductTaxID = purchaseDetail['ProductTaxID']
                        except:
                            ProductTaxID = ""
                            # SalesPrice = round(SalesPrice, PriceRounding)

                        # UnitPrice = round(UnitPrice, PriceRounding)
                        # InclusivePrice = round(InclusivePrice, PriceRounding)
                        # RateWithTax = round(RateWithTax, PriceRounding)
                        # CostPerItem = round(CostPerItem, PriceRounding)
                        # DiscountPerc = round(DiscountPerc, PriceRounding)
                        # DiscountAmount = round(DiscountAmount, PriceRounding)
                        # AddlDiscPerc = round(AddlDiscPerc, PriceRounding)
                        # AddlDiscAmt = round(AddlDiscAmt, PriceRounding)
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

                        # BatchCode = 0
                        if is_inclusive == True:
                            Batch_purchasePrice = InclusivePrice
                        else:
                            Batch_purchasePrice = UnitPrice

                        if ManufactureDate == "":
                            ManufactureDate = None

                        if ExpiryDate == "":
                            ExpiryDate = None

                        product_is_Service = Product.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).is_Service

                        MultiFactor = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor

                        qty_batch = float(FreeQty) + float(Qty)
                        Qty_batch = float(MultiFactor) * float(qty_batch)

                        CostPerItem = float(TaxableAmount) / float(qty_batch)
                        
                        if product_is_Service == False:
                            if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                                check_EnableProductBatchWise = GeneralSettings.objects.get(
                                    CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
                                check_BatchCriteria = "PurchasePriceAndSalesPrice"
                                if GeneralSettings.objects.filter(
                                        CompanyID=CompanyID, SettingsType="BatchCriteria").exists():
                                    check_BatchCriteria = GeneralSettings.objects.get(
                                        CompanyID=CompanyID, SettingsType="BatchCriteria").SettingsValue
                                pri_ins = PriceList.objects.get(
                                    CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID)
                                # PurchasePrice = pri_ins.PurchasePrice

                                if SalesPrice == None:
                                    SalesPrice = pri_ins.SalesPrice
                                pri_ins.SalesPrice = SalesPrice
                                pri_ins.save()

                                if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                                    if check_BatchCriteria == "PurchasePrice":
                                        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PriceListID=PriceListID, PurchasePrice=Batch_purchasePrice).exists():
                                            batch_ins = Batch.objects.filter(
                                                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PriceListID=PriceListID, PurchasePrice=Batch_purchasePrice).last()
                                            StockIn = batch_ins.StockIn
                                            BatchCode = batch_ins.BatchCode
                                            SalesPrice = batch_ins.SalesPrice
                                            NewStock = float(
                                                StockIn) + float(Qty_batch)
                                            batch_ins.StockIn = NewStock
                                            if ExpiryDate:
                                                batch_ins.ExpiryDate = ExpiryDate
                                            if ManufactureDate:
                                                batch_ins.ManufactureDate = ManufactureDate
                                            batch_ins.save()
                                        else:
                                            BatchCode = get_auto_AutoBatchCode(
                                                Batch, BranchID, CompanyID)
                                            Batch.objects.create(
                                                CompanyID=CompanyID,
                                                BranchID=BranchID,
                                                BatchCode=BatchCode,
                                                StockIn=Qty_batch,
                                                PurchasePrice=Batch_purchasePrice,
                                                SalesPrice=SalesPrice,
                                                PriceListID=PriceListID,
                                                ProductID=ProductID,
                                                WareHouseID=WarehouseID,
                                                ManufactureDate=ManufactureDate,
                                                ExpiryDate=ExpiryDate,
                                                CreatedDate=today,
                                                UpdatedDate=today,
                                                CreatedUserID=CreatedUserID,
                                            )
                                    elif check_BatchCriteria == "PurchasePriceAndExpiryDate":
                                        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PriceListID=PriceListID, PurchasePrice=Batch_purchasePrice, ExpiryDate=ExpiryDate).exists():
                                            batch_ins = Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID,
                                                                             PriceListID=PriceListID, PurchasePrice=Batch_purchasePrice, ExpiryDate=ExpiryDate).last()
                                            StockIn = batch_ins.StockIn
                                            BatchCode = batch_ins.BatchCode
                                            SalesPrice = batch_ins.SalesPrice
                                            NewStock = float(
                                                StockIn) + float(Qty_batch)
                                            batch_ins.StockIn = NewStock
                                            batch_ins.save()
                                        else:
                                            BatchCode = get_auto_AutoBatchCode(
                                                Batch, BranchID, CompanyID)
                                            Batch.objects.create(
                                                CompanyID=CompanyID,
                                                BranchID=BranchID,
                                                BatchCode=BatchCode,
                                                StockIn=Qty_batch,
                                                PurchasePrice=Batch_purchasePrice,
                                                SalesPrice=SalesPrice,
                                                PriceListID=PriceListID,
                                                ProductID=ProductID,
                                                WareHouseID=WarehouseID,
                                                ManufactureDate=ManufactureDate,
                                                ExpiryDate=ExpiryDate,
                                                CreatedDate=today,
                                                UpdatedDate=today,
                                                CreatedUserID=CreatedUserID,
                                            )
                                    # else:
                                    #     if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=Batch_purchasePrice, SalesPrice=SalesPrice).exists():
                                    #         batch_ins = Batch.objects.get(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=Batch_purchasePrice, SalesPrice=SalesPrice)
                                    #         StockIn = batch_ins.StockIn
                                    #         BatchCode = batch_ins.BatchCode
                                    #         NewStock = float(StockIn) + float(Qty)
                                    #         batch_ins.StockIn = NewStock
                                    #         batch_ins.save()
                                    #     else:
                                    #         BatchCode = get_auto_AutoBatchCode(
                                    #             Batch, BranchID, CompanyID)
                                    #         Batch.objects.create(
                                    #             CompanyID=CompanyID,
                                    #             BranchID=BranchID,
                                    #             BatchCode=BatchCode,
                                    #             StockIn=Qty,
                                    #             PurchasePrice=Batch_purchasePrice,
                                    #             SalesPrice=SalesPrice,
                                    #             PriceListID=PriceListID,
                                    #             ProductID=ProductID,
                                    #             WareHouseID=WarehouseID,
                                    #             ManufactureDate=ManufactureDate,
                                    #             ExpiryDate=ExpiryDate,
                                    #             CreatedDate=today,
                                    #             UpdatedDate=today,
                                    #             CreatedUserID=CreatedUserID,
                                    #         )

                                else:
                                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PriceListID=PriceListID).exists():
                                        batch_ins = Batch.objects.get(
                                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PriceListID=PriceListID)
                                        StockIn = batch_ins.StockIn
                                        BatchCode = batch_ins.BatchCode
                                        SalesPrice = batch_ins.SalesPrice
                                        NewStock = float(
                                            StockIn) + float(Qty_batch)
                                        batch_ins.StockIn = NewStock
                                        batch_ins.save()
                                    else:
                                        BatchCode = get_auto_AutoBatchCode(
                                            Batch, BranchID, CompanyID)
                                        Batch.objects.create(
                                            CompanyID=CompanyID,
                                            BranchID=BranchID,
                                            BatchCode=BatchCode,
                                            StockIn=Qty_batch,
                                            PurchasePrice=Batch_purchasePrice,
                                            SalesPrice=SalesPrice,
                                            PriceListID=PriceListID,
                                            ProductID=ProductID,
                                            WareHouseID=WarehouseID,
                                            ManufactureDate=ManufactureDate,
                                            ExpiryDate=ExpiryDate,
                                            CreatedDate=today,
                                            UpdatedDate=today,
                                            CreatedUserID=CreatedUserID,
                                        )

                                # if check_BatchCriteria == "PurchasePrice":
                                #     if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PriceListID=PriceListID, WareHouseID=WarehouseID, PurchasePrice=PurchasePrice).exists():
                                #         batch_ins = Batch.objects.get(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID,
                                #                                          PriceListID=PriceListID, WareHouseID=WarehouseID, PurchasePrice=PurchasePrice)
                                #         StockIn = batch_ins.StockIn
                                #         NewStock = float(StockIn) + float(Qty)
                                #         batch_ins.StockIn = NewStock
                                #         batch_ins.save()
                                #     else:
                                #         if Batch.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ProductID=ProductID,PriceListID=PriceListID,WareHouseID=WarehouseID,PurchasePrice=PurchasePrice,).exists():
                                #             batch_ins = Batch.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ProductID=ProductID,PriceListID=PriceListID,WareHouseID=WarehouseID,PurchasePrice=PurchasePrice).first()
                                #             StockIn = batch_ins.StockIn
                                #             NewStock = float(StockIn) + float(Qty)
                                #             batch_ins.update(StockIn=NewStock)
                                # elif check_BatchCriteria == "SalesPrice":
                                #     if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PriceListID=PriceListID, WareHouseID=WarehouseID, SalesPrice=SalesPrice).exists():
                                #         batch_ins = Batch.objects.get(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID,
                                #                                          PriceListID=PriceListID, WareHouseID=WarehouseID, SalesPrice=SalesPrice)
                                #         StockIn = batch_ins.StockIn
                                #         NewStock = float(StockIn) + float(Qty)
                                #         batch_ins.StockIn = NewStock
                                #         batch_ins.save()
                                #     else:
                                #         if Batch.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ProductID=ProductID,PriceListID=PriceListID,WareHouseID=WarehouseID,SalesPrice=SalesPrice,).exists():
                                #             batch_ins = Batch.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ProductID=ProductID,PriceListID=PriceListID,WareHouseID=WarehouseID,SalesPrice=SalesPrice).first()
                                #             StockIn = batch_ins.StockIn
                                #             NewStock = float(StockIn) + float(Qty)
                                #             batch_ins.update(StockIn=NewStock)
                                # else:
                                #     if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PriceListID=PriceListID, WareHouseID=WarehouseID, SalesPrice=SalesPrice,PurchasePrice=PurchasePrice).exists():
                                #         batch_ins = Batch.objects.get(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID,
                                #                                          PriceListID=PriceListID, WareHouseID=WarehouseID, SalesPrice=SalesPrice,PurchasePrice=PurchasePrice)
                                #         StockIn = batch_ins.StockIn
                                #         NewStock = float(StockIn) + float(Qty)
                                #         batch_ins.StockIn = NewStock
                                #         batch_ins.save()
                                #     else:
                                #         if Batch.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ProductID=ProductID,PriceListID=PriceListID,WareHouseID=WarehouseID,SalesPrice=SalesPrice,PurchasePrice=PurchasePrice).exists():
                                #             batch_ins = Batch.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ProductID=ProductID,PriceListID=PriceListID,WareHouseID=WarehouseID,SalesPrice=SalesPrice,PurchasePrice=PurchasePrice).first()
                                #             StockIn = batch_ins.StockIn
                                #             NewStock = float(StockIn) + float(Qty)
                                #             batch_ins.update(StockIn=NewStock)

                        PurchaseDetailsID = get_auto_id(
                            PurchaseDetails, BranchID, CompanyID)

                        log_instance = PurchaseDetails_Log.objects.create(
                            TransactionID=PurchaseDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            PurchaseMasterID=PurchaseMasterID,
                            ProductID=ProductID,
                            Qty=Qty,
                            ReturnQty=Qty,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            InclusivePrice=InclusivePrice,
                            RateWithTax=RateWithTax,
                            CostPerItem=CostPerItem,
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
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            CompanyID=CompanyID,
                            BatchCode=BatchCode,
                            ManufactureDate=ManufactureDate,
                            ExpiryDate=ExpiryDate,
                            ProductTaxID=ProductTaxID
                        )
                        PurchaseDetails.objects.create(
                            PurchaseDetailsID=PurchaseDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            PurchaseMasterID=PurchaseMasterID,
                            purchase_master=instance,
                            ProductID=ProductID,
                            Qty=Qty,
                            ReturnQty=Qty,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            InclusivePrice=InclusivePrice,
                            RateWithTax=RateWithTax,
                            CostPerItem=CostPerItem,
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
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            CompanyID=CompanyID,
                            BatchCode=BatchCode,
                            ManufactureDate=ManufactureDate,
                            ExpiryDate=ExpiryDate,
                            LogID=log_instance.ID,
                            ProductTaxID=ProductTaxID
                        )


                        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="PurchasePriceUpdate").exists():
                            check_PurchasePriceUpdate = GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="PurchasePriceUpdate").SettingsValue
                            if check_PurchasePriceUpdate == "True":
                                pri_ins = PriceList.objects.get(
                                    CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID)
                                pri_ins.PurchasePrice = Batch_purchasePrice
                                pri_ins.save()

                        if product_is_Service == False:
                            # MultiFactor = PriceList.objects.get(
                            #     CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor
                            PriceListID = PriceList.objects.get(
                                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

                            # PurchasePrice = priceList.PurchasePrice
                            # SalesPrice = priceList.SalesPrice

                            qty = float(FreeQty) + float(Qty)

                            Qty = float(MultiFactor) * float(qty)
                            Cost = float(CostPerItem) / float(MultiFactor)

                            # Qy = round(Qty, 4)
                            # Qty = str(Qy)

                            # Ct = round(Cost, 4)
                            # Cost = str(Ct)

                            princeList_instance = PriceList.objects.get(
                                CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID, BranchID=BranchID)
                            PurchasePrice = princeList_instance.PurchasePrice
                            SalesPrice = princeList_instance.SalesPrice

                            StockPostingID = get_auto_stockPostid(
                                StockPosting, BranchID, CompanyID)

                            StockPosting.objects.create(
                                StockPostingID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=Date,
                                VoucherMasterID=PurchaseMasterID,
                                VoucherDetailID=PurchaseDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchID,
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

                            StockPosting_Log.objects.create(
                                TransactionID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=Date,
                                VoucherMasterID=PurchaseMasterID,
                                VoucherDetailID=PurchaseDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchID,
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

                            update_stock(CompanyID,BranchID,ProductID)

                            # stockRateInstance = None

                            # if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID).exists():
                            #     stockRateInstance = StockRate.objects.get(
                            #         CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID)

                            #     StockRateID = stockRateInstance.StockRateID
                            #     stockRateInstance.Qty = float(
                            #         stockRateInstance.Qty) + float(Qty)
                            #     stockRateInstance.save()

                            #     if StockTrans.objects.filter(StockRateID=StockRateID, DetailID=PurchaseDetailsID, MasterID=PurchaseMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                            #         stockTra_in = StockTrans.objects.filter(
                            #             StockRateID=StockRateID, DetailID=PurchaseDetailsID, MasterID=PurchaseMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                            #         stockTra_in.Qty = float(
                            #             stockTra_in.Qty) + float(Qty)
                            #         stockTra_in.save()
                            #     else:
                            #         StockTransID = get_auto_StockTransID(
                            #             StockTrans, BranchID, CompanyID)
                            #         StockTrans.objects.create(
                            #             StockTransID=StockTransID,
                            #             BranchID=BranchID,
                            #             VoucherType=VoucherType,
                            #             StockRateID=StockRateID,
                            #             DetailID=PurchaseDetailsID,
                            #             MasterID=PurchaseMasterID,
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
                            #         Date=Date,
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
                            #         DetailID=PurchaseDetailsID,
                            #         MasterID=PurchaseMasterID,
                            #         Qty=Qty,
                            #         IsActive=IsActive,
                            #         CompanyID=CompanyID,
                            #     )

                #request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Purchase',
                #              'Create', 'Purchase created successfully.', 'Purchase saved successfully.')
                response_data = {
                    "StatusCode": 6000,
                    "id": instance.id,
                    "message": "purchase created Successfully!!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Purchase',
                             'Create', 'Purchase created Failed.', 'VoucherNo already exist')
                response_data = {
                    "StatusCode": 6001,
                    "message": "VoucherNo already exist.Please Change Your Prefix!"
                }

                return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
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
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Purchase',
                     'Create', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def edit_purchase(request, pk):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            CreatedUserID = data['CreatedUserID']
            PriceRounding = data['PriceRounding']
            today = datetime.datetime.now()
            purchaseMaster_instance = None
            purchaseDetails = None
            purchaseMaster_instance = PurchaseMaster.objects.get(
                CompanyID=CompanyID, pk=pk)
            PurchaseMasterID = purchaseMaster_instance.PurchaseMasterID
            VoucherNo = purchaseMaster_instance.VoucherNo
            BranchID = purchaseMaster_instance.BranchID

            Action = "M"

            RefferenceBillNo = data['RefferenceBillNo']
            Date = data['Date']
            VenderInvoiceDate = data['VenderInvoiceDate']
            CreditPeriod = data['CreditPeriod']
            LedgerID = data['LedgerID']
            PriceCategoryID = data['PriceCategoryID']
            EmployeeID = data['EmployeeID']
            PurchaseAccount = data['PurchaseAccount']
            CustomerName = data['CustomerName']
            Address1 = data['Address1']
            Address2 = data['Address2']
            Address3 = data['Address3']
            Notes = data['Notes']
            FinacialYearID = data['FinacialYearID']
            TotalGrossAmt = data['TotalGrossAmt']
            TotalTax = data['TotalTax']
            NetTotal = data['NetTotal']
            AddlDiscPercent = data['AddlDiscPercent']
            AddlDiscAmt = data['AddlDiscAmt']
            AdditionalCost = data['AdditionalCost']
            TotalDiscount = data['TotalDiscount']
            GrandTotal = data['GrandTotal']
            RoundOff = data['RoundOff']
            TransactionTypeID = data['TransactionTypeID']
            WarehouseID = data['WarehouseID']
            IsActive = data['IsActive']
            BatchID = data['BatchID']

            TaxID = data['TaxID']
            TaxType = data['TaxType']
            VATAmount = data['VATAmount']
            SGSTAmount = data['SGSTAmount']
            CGSTAmount = data['CGSTAmount']
            IGSTAmount = data['IGSTAmount']
            TAX1Amount = data['TAX1Amount']
            TAX2Amount = data['TAX2Amount']
            TAX3Amount = data['TAX3Amount']
            BillDiscPercent = data['BillDiscPercent']
            BillDiscAmt = data['BillDiscAmt']

            try:
                Balance = data['Balance']
            except:
                Balance = 0

            if not Balance:
                Balance = 0

            try:
                BankAmount = float(data['BankAmount'])
            except:
                BankAmount = 0

            try:
                CashReceived = data['CashReceived']
            except:
                CashReceived = 0

            try:
                CardTypeID = data['CardTypeID']
            except:
                CardTypeID = 0

            try:
                CardNumber = data['CardNumber']
            except:
                CardNumber = 0
            # ================
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
                PurchaseTax = data['PurchaseTax']
            except:
                PurchaseTax = 0

            try:
                Country_of_Supply = data['Country_of_Supply']
            except:
                Country_of_Supply = ""

            try:
                State_of_Supply = data['State_of_Supply']
            except:
                State_of_Supply = ""

            try:
                GST_Treatment = data['GST_Treatment']
            except:
                GST_Treatment = ""

            try:
                VAT_Treatment = data['VAT_Treatment']
            except:
                VAT_Treatment = ""
            # ==========

            purchaseDetails = data["PurchaseDetails"]
            TotalTaxableAmount = 0
            for i in purchaseDetails:
                TotalTaxableAmount += float(i['TaxableAmount'])

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

            AllowCashReceiptMorePurchaseAmt = data['AllowCashReceiptMorePurchaseAmt']
            if AllowCashReceiptMorePurchaseAmt == True or AllowCashReceiptMorePurchaseAmt == "true":
                CashAmount = CashReceived
            elif float(Balance) < 0:
                CashAmount = float(GrandTotal) - float(BankAmount)
            else:
                CashAmount = CashReceived

            PurchaseMaster_Log.objects.create(
                TransactionID=PurchaseMasterID,
                TotalTaxableAmount=TotalTaxableAmount,
                BranchID=BranchID,
                Action=Action,
                VoucherNo=VoucherNo,
                RefferenceBillNo=RefferenceBillNo,
                Date=Date,
                VenderInvoiceDate=VenderInvoiceDate,
                CreditPeriod=CreditPeriod,
                LedgerID=LedgerID,
                PriceCategoryID=PriceCategoryID,
                EmployeeID=EmployeeID,
                PurchaseAccount=PurchaseAccount,
                CustomerName=CustomerName,
                Address1=Address1,
                Address2=Address2,
                Address3=Address3,
                Notes=Notes,
                FinacialYearID=FinacialYearID,
                TotalGrossAmt=TotalGrossAmt,
                TotalTax=TotalTax,
                NetTotal=NetTotal,
                AddlDiscPercent=AddlDiscPercent,
                AddlDiscAmt=AddlDiscAmt,
                AdditionalCost=AdditionalCost,
                TotalDiscount=TotalDiscount,
                GrandTotal=GrandTotal,
                RoundOff=RoundOff,
                TransactionTypeID=TransactionTypeID,
                WarehouseID=WarehouseID,
                IsActive=IsActive,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                TaxID=TaxID,
                TaxType=TaxType,
                VATAmount=VATAmount,
                SGSTAmount=SGSTAmount,
                CGSTAmount=CGSTAmount,
                IGSTAmount=IGSTAmount,
                TAX1Amount=TAX1Amount,
                TAX2Amount=TAX2Amount,
                TAX3Amount=TAX3Amount,
                BillDiscPercent=BillDiscPercent,
                BillDiscAmt=BillDiscAmt,
                Balance=Balance,
                CompanyID=CompanyID,
                CashReceived=CashReceived,
                CashAmount=CashAmount,
                BankAmount=BankAmount,
                CardTypeID=CardTypeID,
                CardNumber=CardNumber,
                CashID=CashID,
                BankID=BankID,
                ShippingCharge=ShippingCharge,
                shipping_tax_amount=shipping_tax_amount,
                TaxTypeID=TaxTypeID,
                SAC=SAC,
                PurchaseTax=PurchaseTax,
                Country_of_Supply=Country_of_Supply,
                State_of_Supply=State_of_Supply,
                GST_Treatment=GST_Treatment,
                VAT_Treatment=VAT_Treatment,
            )

            update_ledger = UpdateLedgerBalance(CompanyID,BranchID,0,PurchaseMasterID,"PI",0,"Cr","update")

            if LedgerPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PurchaseMasterID, BranchID=BranchID, VoucherType="PI").exists():
                ledgerPostInstances = LedgerPosting.objects.filter(
                    CompanyID=CompanyID, VoucherMasterID=PurchaseMasterID, BranchID=BranchID, VoucherType="PI").delete()

                # for ledgerPostInstance in ledgerPostInstances:
                #     ledgerPostInstance.delete()

            # if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PurchaseMasterID, BranchID=BranchID, VoucherType="PI").exists():
            #     stockPostingInstances = StockPosting.objects.filter(
            #         CompanyID=CompanyID, VoucherMasterID=PurchaseMasterID, BranchID=BranchID, VoucherType="PI").delete()

            if PurchaseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PurchaseMasterID=PurchaseMasterID).exists():
                purch_ins = PurchaseDetails.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, PurchaseMasterID=PurchaseMasterID)
                for i in purch_ins:
                    BatchCode = i.BatchCode
                    Qty = i.Qty
                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
                        batch_ins = Batch.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                        StockIn = batch_ins.StockIn
                        batch_ins.StockIn = float(StockIn) - float(Qty)
                        batch_ins.save()
                    if not StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PurchaseMasterID,VoucherDetailID=i.PurchaseDetailsID,BranchID=BranchID, VoucherType="PI").exists():
                        StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PurchaseMasterID,BranchID=BranchID, VoucherType="PI").delete()
                        update_stock(CompanyID,BranchID,i.ProductID)
                    instance_MultiFactor = PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=i.PriceListID, BranchID=BranchID).MultiFactor

                    instance_qty_sum = float(i.FreeQty) + float(i.Qty)
                    instance_Qty = float(instance_MultiFactor) * float(instance_qty_sum)
                    if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PurchaseMasterID,VoucherDetailID=i.PurchaseDetailsID,ProductID=i.ProductID,BranchID=BranchID, VoucherType="PI").exists():
                        stock_inst = StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PurchaseMasterID,VoucherDetailID=i.PurchaseDetailsID,ProductID=i.ProductID,BranchID=BranchID, VoucherType="PI").first()
                        stock_inst.QtyIn = float(stock_inst.QtyIn) - float(instance_Qty)
                        stock_inst.save()
                        update_stock(CompanyID,BranchID,i.ProductID)


            purchaseMaster_instance.RefferenceBillNo = RefferenceBillNo
            purchaseMaster_instance.Date = Date
            purchaseMaster_instance.VenderInvoiceDate = VenderInvoiceDate
            purchaseMaster_instance.CreditPeriod = CreditPeriod
            purchaseMaster_instance.LedgerID = LedgerID
            purchaseMaster_instance.PriceCategoryID = PriceCategoryID
            purchaseMaster_instance.EmployeeID = EmployeeID
            purchaseMaster_instance.PurchaseAccount = PurchaseAccount
            purchaseMaster_instance.CustomerName = CustomerName
            purchaseMaster_instance.Address1 = Address1
            purchaseMaster_instance.Address2 = Address2
            purchaseMaster_instance.Address3 = Address3
            purchaseMaster_instance.Notes = Notes
            purchaseMaster_instance.FinacialYearID = FinacialYearID
            purchaseMaster_instance.TotalGrossAmt = TotalGrossAmt
            purchaseMaster_instance.TotalTax = TotalTax
            purchaseMaster_instance.NetTotal = NetTotal
            purchaseMaster_instance.AddlDiscPercent = AddlDiscPercent
            purchaseMaster_instance.AddlDiscAmt = AddlDiscAmt
            purchaseMaster_instance.AdditionalCost = AdditionalCost
            purchaseMaster_instance.TotalDiscount = TotalDiscount
            purchaseMaster_instance.GrandTotal = GrandTotal
            purchaseMaster_instance.RoundOff = RoundOff
            purchaseMaster_instance.TransactionTypeID = TransactionTypeID
            purchaseMaster_instance.WarehouseID = WarehouseID
            purchaseMaster_instance.IsActive = IsActive
            purchaseMaster_instance.Action = Action
            purchaseMaster_instance.UpdatedDate = today
            purchaseMaster_instance.CreatedUserID = CreatedUserID

            purchaseMaster_instance.TaxID = TaxID
            purchaseMaster_instance.TaxType = TaxType
            purchaseMaster_instance.VATAmount = VATAmount
            purchaseMaster_instance.SGSTAmount = SGSTAmount
            purchaseMaster_instance.CGSTAmount = CGSTAmount
            purchaseMaster_instance.IGSTAmount = IGSTAmount
            purchaseMaster_instance.TAX1Amount = TAX1Amount
            purchaseMaster_instance.TAX2Amount = TAX2Amount
            purchaseMaster_instance.TAX3Amount = TAX3Amount
            purchaseMaster_instance.BillDiscPercent = BillDiscPercent
            purchaseMaster_instance.BillDiscAmt = BillDiscAmt
            purchaseMaster_instance.Balance = Balance
            purchaseMaster_instance.TotalTaxableAmount = TotalTaxableAmount
            purchaseMaster_instance.CashReceived = CashReceived
            purchaseMaster_instance.CashAmount = CashAmount
            purchaseMaster_instance.BankAmount = BankAmount
            purchaseMaster_instance.CardTypeID = CardTypeID
            purchaseMaster_instance.CardNumber = CardNumber
            purchaseMaster_instance.CashID = CashID
            purchaseMaster_instance.BankID = BankID
            purchaseMaster_instance.ShippingCharge = ShippingCharge
            purchaseMaster_instance.shipping_tax_amount = shipping_tax_amount
            purchaseMaster_instance.TaxTypeID = TaxTypeID
            purchaseMaster_instance.SAC = SAC
            purchaseMaster_instance.PurchaseTax = PurchaseTax
            purchaseMaster_instance.Country_of_Supply = Country_of_Supply
            purchaseMaster_instance.State_of_Supply = State_of_Supply
            purchaseMaster_instance.GST_Treatment = GST_Treatment
            purchaseMaster_instance.VAT_Treatment = VAT_Treatment

            purchaseMaster_instance.save()

            VoucherType = "PI"

            account_group = AccountLedger.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).AccountGroupUnder

            # new posting starting from here
            # if float(shipping_tax_amount) > 0:
            #     if AccountLedger.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerName="Shipping Charges").exists():
            #         RelativeLedgerID = AccountLedger.objects.get(
            #             CompanyID=CompanyID, BranchID=BranchID, LedgerName="Shipping Charges").LedgerID
            #     else:
            #         RelativeLedgerID = generated_ledgerID(
            #             AccountLedger, BranchID, CompanyID)
            #         ShippingChargeLedgerCode = get_LedgerCode(
            #             AccountLedger, BranchID, CompanyID)

            #         AccountLedger.objects.create(
            #             LedgerID=RelativeLedgerID,
            #             BranchID=BranchID,
            #             LedgerName="Shipping Charges Purchase",
            #             LedgerCode=ShippingChargeLedgerCode,
            #             AccountGroupUnder=49,
            #             OpeningBalance=0,
            #             CrOrDr="Cr",
            #             Notes=Notes,
            #             IsActive=True,
            #             IsDefault=True,
            #             CreatedDate=today,
            #             UpdatedDate=today,
            #             Action=Action,
            #             CreatedUserID=CreatedUserID,
            #             CompanyID=CompanyID,
            #         )

            #         AccountLedger_Log.objects.create(
            #             BranchID=BranchID,
            #             TransactionID=RelativeLedgerID,
            #             LedgerName="Shipping Charges Purchase",
            #             LedgerCode=ShippingChargeLedgerCode,
            #             AccountGroupUnder=49,
            #             OpeningBalance=0,
            #             CrOrDr="Cr",
            #             Notes=Notes,
            #             IsActive=True,
            #             IsDefault=True,
            #             CreatedDate=today,
            #             UpdatedDate=today,
            #             Action=Action,
            #             CreatedUserID=CreatedUserID,
            #             CompanyID=CompanyID,
            #         )
            #     LedgerPostingID = get_auto_LedgerPostid(
            #         LedgerPosting, BranchID, CompanyID)

            #     LedgerPosting.objects.create(
            #         LedgerPostingID=LedgerPostingID,
            #         BranchID=BranchID,
            #         Date=Date,
            #         VoucherMasterID=PurchaseMasterID,
            #         VoucherType=VoucherType,
            #         VoucherNo=VoucherNo,
            #         LedgerID=PurchaseAccount,
            #         RelatedLedgerID=RelativeLedgerID,
            #         Credit=shipping_tax_amount,
            #         IsActive=IsActive,
            #         Action=Action,
            #         CreatedUserID=CreatedUserID,
            #         CreatedDate=today,
            #         UpdatedDate=today,
            #         CompanyID=CompanyID,
            #     )

            #     LedgerPosting_Log.objects.create(
            #         TransactionID=LedgerPostingID,
            #         BranchID=BranchID,
            #         Date=Date,
            #         VoucherMasterID=PurchaseMasterID,
            #         VoucherType=VoucherType,
            #         VoucherNo=VoucherNo,
            #         LedgerID=PurchaseAccount,
            #         RelatedLedgerID=RelativeLedgerID,
            #         Credit=shipping_tax_amount,
            #         IsActive=IsActive,
            #         Action=Action,
            #         CreatedUserID=CreatedUserID,
            #         CreatedDate=today,
            #         UpdatedDate=today,
            #         CompanyID=CompanyID,
            #     )

            #     LedgerPostingID = get_auto_LedgerPostid(
            #         LedgerPosting, BranchID, CompanyID)

            #     LedgerPosting.objects.create(
            #         LedgerPostingID=LedgerPostingID,
            #         BranchID=BranchID,
            #         Date=Date,
            #         VoucherMasterID=PurchaseMasterID,
            #         VoucherType=VoucherType,
            #         VoucherNo=VoucherNo,
            #         LedgerID=RelativeLedgerID,
            #         RelatedLedgerID=PurchaseAccount,
            #         Debit=shipping_tax_amount,
            #         IsActive=IsActive,
            #         Action=Action,
            #         CreatedUserID=CreatedUserID,
            #         CreatedDate=today,
            #         UpdatedDate=today,
            #         CompanyID=CompanyID,
            #     )

            #     LedgerPosting_Log.objects.create(
            #         TransactionID=LedgerPostingID,
            #         BranchID=BranchID,
            #         Date=Date,
            #         VoucherMasterID=PurchaseMasterID,
            #         VoucherType=VoucherType,
            #         VoucherNo=VoucherNo,
            #         LedgerID=RelativeLedgerID,
            #         RelatedLedgerID=PurchaseAccount,
            #         Debit=shipping_tax_amount,
            #         IsActive=IsActive,
            #         Action=Action,
            #         CreatedUserID=CreatedUserID,
            #         CreatedDate=today,
            #         UpdatedDate=today,
            #         CompanyID=CompanyID,
            #     )

            # new posting starting from here
            if TaxType == 'VAT':
                if float(VATAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=54,
                        RelatedLedgerID=PurchaseAccount,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=54,
                        RelatedLedgerID=PurchaseAccount,
                        Debit=VATAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,54,PurchaseMasterID,VoucherType,VATAmount,"Dr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=54,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=54,
                        Credit=VATAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,VATAmount,"Cr","create")

            elif TaxType == 'GST Intra-state B2B':
                if float(CGSTAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=36,
                        RelatedLedgerID=PurchaseAccount,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=36,
                        RelatedLedgerID=PurchaseAccount,
                        Debit=CGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,36,PurchaseMasterID,VoucherType,CGSTAmount,"Dr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=36,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=36,
                        Credit=CGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,CGSTAmount,"Cr","create")

                if float(SGSTAmount) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=42,
                        RelatedLedgerID=PurchaseAccount,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=42,
                        RelatedLedgerID=PurchaseAccount,
                        Debit=SGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,42,PurchaseMasterID,VoucherType,SGSTAmount,"Dr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=42,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=42,
                        Credit=SGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,SGSTAmount,"Cr","create")

            elif TaxType == 'GST Inter-state B2B':
                if float(IGSTAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=39,
                        RelatedLedgerID=PurchaseAccount,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=39,
                        RelatedLedgerID=PurchaseAccount,
                        Debit=IGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,39,PurchaseMasterID,VoucherType,IGSTAmount,"Dr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=39,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=39,
                        Credit=IGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,IGSTAmount,"Cr","create")

            if not TaxType == 'Import':
                if float(TAX1Amount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=45,
                        RelatedLedgerID=PurchaseAccount,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=45,
                        RelatedLedgerID=PurchaseAccount,
                        Debit=TAX1Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,45,PurchaseMasterID,VoucherType,TAX1Amount,"Dr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=45,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=45,
                        Credit=TAX1Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,TAX1Amount,"Cr","create")

                if float(TAX2Amount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=48,
                        RelatedLedgerID=PurchaseAccount,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=48,
                        RelatedLedgerID=PurchaseAccount,
                        Debit=TAX2Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,48,PurchaseMasterID,VoucherType,TAX2Amount,"Dr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=48,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=48,
                        Credit=TAX2Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,TAX2Amount,"Cr","create")

                if float(TAX3Amount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=51,
                        RelatedLedgerID=PurchaseAccount,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=51,
                        RelatedLedgerID=PurchaseAccount,
                        Debit=TAX3Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,51,PurchaseMasterID,VoucherType,TAX3Amount,"Dr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=51,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=51,
                        Credit=TAX3Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,TAX3Amount,"Cr","create")

            if float(RoundOff) > 0:

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=77,
                    RelatedLedgerID=PurchaseAccount,
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
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=77,
                    RelatedLedgerID=PurchaseAccount,
                    Debit=RoundOff,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,77,PurchaseMasterID,VoucherType,RoundOff,"Dr","create")

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
                    RelatedLedgerID=77,
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
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
                    RelatedLedgerID=77,
                    Credit=RoundOff,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,RoundOff,"Cr","create")

            if float(RoundOff) < 0:

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                RoundOff = abs(float(RoundOff))

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=77,
                    RelatedLedgerID=PurchaseAccount,
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
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=77,
                    RelatedLedgerID=PurchaseAccount,
                    Credit=RoundOff,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,77,PurchaseMasterID,VoucherType,RoundOff,"Cr","create")

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
                    RelatedLedgerID=77,
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
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
                    RelatedLedgerID=77,
                    Debit=RoundOff,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,RoundOff,"Dr","create")

            if float(TotalDiscount) > 0:

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=83,
                    RelatedLedgerID=PurchaseAccount,
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
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=83,
                    RelatedLedgerID=PurchaseAccount,
                    Credit=TotalDiscount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,83,PurchaseMasterID,VoucherType,TotalDiscount,"Cr","create")

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
                    RelatedLedgerID=83,
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
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
                    RelatedLedgerID=83,
                    Debit=TotalDiscount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,TotalDiscount,"Dr","create")

            # credit sales start here
            if float(CashReceived) == 0 and float(BankAmount) == 0:
                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
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
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
                    RelatedLedgerID=LedgerID,
                    Debit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,GrandTotal,"Dr","create")

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=PurchaseAccount,
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
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=PurchaseAccount,
                    Credit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,LedgerID,PurchaseMasterID,VoucherType,GrandTotal,"Cr","create")

            # credit sales end here

            # customer with cash and customer with partial cash start here
            elif (account_group == 10 or account_group == 29 or account_group == 32) and float(CashReceived) > 0 and float(BankAmount) == 0:
                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
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
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
                    RelatedLedgerID=LedgerID,
                    Debit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,GrandTotal,"Dr","create")

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=PurchaseAccount,
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
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=PurchaseAccount,
                    Credit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,LedgerID,PurchaseMasterID,VoucherType,GrandTotal,"Cr","create")

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
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
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
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

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,CashID,PurchaseMasterID,VoucherType,CashAmount,"Cr","create")

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
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
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
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

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,LedgerID,PurchaseMasterID,VoucherType,CashAmount,"Dr","create")

            # customer with cash and customer with partial cash end here

            # customer with bank and customer with partial bank start here
            elif (account_group == 10 or account_group == 29 or account_group == 32) and float(CashReceived) == 0 and float(BankAmount) > 0:
                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
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
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
                    RelatedLedgerID=LedgerID,
                    Debit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,GrandTotal,"Dr","create")

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=PurchaseAccount,
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
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=PurchaseAccount,
                    Credit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,LedgerID,PurchaseMasterID,VoucherType,GrandTotal,"Cr","create")

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
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
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
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

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,BankID,PurchaseMasterID,VoucherType,BankAmount,"Cr","create")

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
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
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
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

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,LedgerID,PurchaseMasterID,VoucherType,BankAmount,"Dr","create")

            # customer with bank and customer with partial bank end here

            # bank with cash and cash with cash start here
            elif (account_group == 8 or account_group == 9) and float(CashReceived) > 0 and float(BankAmount) == 0:
                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
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
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
                    RelatedLedgerID=CashID,
                    Debit=CashAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,CashAmount,"Dr","create")

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=CashID,
                    RelatedLedgerID=PurchaseAccount,
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
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=CashID,
                    RelatedLedgerID=PurchaseAccount,
                    Credit=CashAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,CashID,PurchaseMasterID,VoucherType,CashAmount,"Cr","create")

                csh_value = float(GrandTotal) - float(CashReceived)
                if not float(csh_value) == 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=PurchaseAccount,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=PurchaseAccount,
                        Credit=csh_value,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,LedgerID,PurchaseMasterID,VoucherType,csh_value,"Cr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
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
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=LedgerID,
                        Debit=csh_value,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,csh_value,"Dr","create")
            # bank with cash and cash with cash end here

            # bank with bank and cash with bank start here
            elif (account_group == 8 or account_group == 9) and float(CashReceived) == 0 and float(BankAmount) > 0:
                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
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
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
                    RelatedLedgerID=BankID,
                    Debit=BankAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,BankAmount,"Dr","create")

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=BankID,
                    RelatedLedgerID=PurchaseAccount,
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
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=BankID,
                    RelatedLedgerID=PurchaseAccount,
                    Credit=BankAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,BankID,PurchaseMasterID,VoucherType,BankAmount,"Cr","create")

                bnk_value = float(GrandTotal) - float(BankAmount)
                if not float(bnk_value) == 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=PurchaseAccount,
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
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=PurchaseAccount,
                        Credit=bnk_value,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,LedgerID,PurchaseMasterID,VoucherType,bnk_value,"Cr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
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
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=LedgerID,
                        Debit=bnk_value,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,bnk_value,"Dr","create")
            # bank with bank and cash with bank end here

            # customer with partial cash /bank and customer with cash/bank
            elif (account_group == 10 or account_group == 29 or account_group == 32) and float(CashReceived) > 0 and float(BankAmount) > 0:
                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
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
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
                    RelatedLedgerID=LedgerID,
                    Debit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,GrandTotal,"Dr","create")

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=PurchaseAccount,
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
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=PurchaseAccount,
                    Credit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,LedgerID,PurchaseMasterID,VoucherType,GrandTotal,"Cr","create")

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
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
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
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

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,CashID,PurchaseMasterID,VoucherType,CashAmount,"Cr","create")

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
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
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
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

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,LedgerID,PurchaseMasterID,VoucherType,CashAmount,"Dr","create")

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
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
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
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

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,BankID,PurchaseMasterID,VoucherType,BankAmount,"Cr","create")

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
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
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
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

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,BankID,PurchaseMasterID,VoucherType,BankAmount,"Dr","create")
            # customer with partial cash /bank and customer with cash/bank

            # cash with cash/bank start here
            elif (account_group == 9 or account_group == 8) and float(CashReceived) > 0 and float(BankAmount) > 0:

                total_received = float(CashReceived) + float(BankAmount)
                Balance_amt = float(GrandTotal) - float(total_received)
                if not float(Balance_amt) == 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
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
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=LedgerID,
                        Debit=Balance_amt,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,Balance_amt,"Dr","create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=PurchaseAccount,
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
                        Date=Date,
                        VoucherMasterID=PurchaseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=PurchaseAccount,
                        Credit=Balance_amt,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(CompanyID,BranchID,LedgerID,PurchaseMasterID,VoucherType,Balance_amt,"Cr","create")

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=BankID,
                    RelatedLedgerID=PurchaseAccount,
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
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=BankID,
                    RelatedLedgerID=PurchaseAccount,
                    Credit=BankAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,BankID,PurchaseMasterID,VoucherType,BankAmount,"Cr","create")

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
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
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
                    RelatedLedgerID=BankID,
                    Debit=BankAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,BankAmount,"Dr","create")

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
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
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
                    RelatedLedgerID=CashID,
                    Debit=CashReceived,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,PurchaseAccount,PurchaseMasterID,VoucherType,CashReceived,"Dr","create")

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=CashID,
                    RelatedLedgerID=PurchaseAccount,
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
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=CashID,
                    RelatedLedgerID=PurchaseAccount,
                    Credit=CashReceived,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(CompanyID,BranchID,CashID,PurchaseMasterID,VoucherType,CashReceived,"Cr","create")

            # cash with cash/bank end here
            # new posting ending here

            # deleted_datas = data["deleted_data"]
            # if deleted_datas:
            #     for deleted_Data in deleted_datas:
            #         PurchaseDetailsID = deleted_Data['PurchaseDetailsID']
            #         pk = deleted_Data['unq_id']

            #         if not pk == '':
            #             if PurchaseDetails.objects.filter(CompanyID=CompanyID,pk=pk).exists():
            #                 deleted_detail = PurchaseDetails.objects.filter(CompanyID=CompanyID,pk=pk)
            #                 deleted_detail.delete()
            #                 stockTrans_instance = None
            #                 if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=PurchaseDetailsID,MasterID=PurchaseMasterID,BranchID=BranchID,VoucherType=VoucherType,IsActive=True).exists():
            #                     stockTrans_instance = StockTrans.objects.filter(CompanyID=CompanyID,DetailID=PurchaseDetailsID,MasterID=PurchaseMasterID,BranchID=BranchID,VoucherType=VoucherType,IsActive=True).first()
            #                     qty_in_stockTrans = stockTrans_instance.Qty
            #                     StockRateID = stockTrans_instance.StockRateID
            #                     stockTrans_instance.IsActive = False
            #                     stockTrans_instance.save()

            #                     stockRate_instance = get_object_or_404(StockRate.objects.filter(CompanyID=CompanyID,StockRateID=StockRateID,BranchID=BranchID,WareHouseID=WarehouseID))
            #                     stockRate_instance.Qty = float(stockRate_instance.Qty) - float(qty_in_stockTrans)
            #                     stockRate_instance.save()

            deleted_datas = data["deleted_data"]
            if deleted_datas:
                for deleted_Data in deleted_datas:
                    deleted_pk = deleted_Data['unq_id']
                    PurchaseDetailsID_Deleted = deleted_Data['PurchaseDetailsID']
                    ProductID_Deleted = deleted_Data['ProductID']
                    PriceListID_Deleted = deleted_Data['PriceListID']
                    Rate_Deleted = deleted_Data['Rate']
                    PurchaseMasterID_Deleted = deleted_Data['PurchaseMasterID']
                    WarehouseID_Deleted = deleted_Data['WarehouseID']
                    try:
                        BranchID = deleted_Data['BranchID']
                    except:
                        BranchID = 1

                    if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID_Deleted, DefaultUnit=True).exists():
                        priceList = PriceList.objects.get(
                            CompanyID=CompanyID, ProductID=ProductID_Deleted, DefaultUnit=True)
                        MultiFactor = priceList.MultiFactor
                        Cost = float(Rate_Deleted) / float(MultiFactor)
                        Ct = round(Cost, 4)
                        Cost_Deleted = str(Ct)

                        if not deleted_pk == '' or not deleted_pk == 0:
                            if PurchaseDetails.objects.filter(CompanyID=CompanyID, pk=deleted_pk).exists():
                                deleted_detail = PurchaseDetails.objects.filter(
                                    CompanyID=CompanyID, pk=deleted_pk).delete()

                                # if StockRate.objects.filter(CompanyID=CompanyID,ProductID=ProductID_Deleted,PriceListID=PriceListID_Deleted,Cost=Cost_Deleted,WareHouseID=WarehouseID_Deleted).exists():
                                #     stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,ProductID=ProductID_Deleted,PriceListID=PriceListID_Deleted,Cost=Cost_Deleted,WareHouseID=WarehouseID_Deleted)
                                #     StockRateID = stockRate_instance.StockRateID
                                #     if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=PurchaseDetailsID_Deleted,MasterID=PurchaseMasterID_Deleted,BranchID=BranchID,
                                #         VoucherType=VoucherType,IsActive=True,StockRateID=StockRateID).exists():
                                #         stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID,DetailID=PurchaseDetailsID_Deleted,MasterID=PurchaseMasterID_Deleted,BranchID=BranchID,
                                #             VoucherType=VoucherType,IsActive=True,StockRateID=StockRateID)
                                #         qty_in_stockTrans = stockTrans_instance.Qty
                                #         stockRate_instance.Qty = float(stockRate_instance.Qty) - float(qty_in_stockTrans)
                                #         stockRate_instance.save()
                                #         stockTrans_instance.IsActive = False
                                #         stockTrans_instance.save()

                                if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PurchaseMasterID_Deleted,VoucherDetailID=PurchaseDetailsID_Deleted,ProductID=ProductID_Deleted,BranchID=BranchID, VoucherType="PI").exists():
                                    stock_instances_delete = StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PurchaseMasterID_Deleted,VoucherDetailID=PurchaseDetailsID_Deleted,ProductID=ProductID_Deleted,BranchID=BranchID, VoucherType="PI")
                                    stock_instances_delete.delete()
                                    update_stock(CompanyID,BranchID,ProductID_Deleted)

                                # if StockTrans.objects.filter(CompanyID=CompanyID, DetailID=PurchaseDetailsID_Deleted, MasterID=PurchaseMasterID_Deleted, BranchID=BranchID, VoucherType=VoucherType, IsActive=True).exists():
                                #     stockTrans_instance = StockTrans.objects.filter(
                                #         CompanyID=CompanyID, DetailID=PurchaseDetailsID_Deleted, MasterID=PurchaseMasterID_Deleted, BranchID=BranchID, VoucherType=VoucherType, IsActive=True)
                                #     for stck in stockTrans_instance:
                                #         StockRateID = stck.StockRateID
                                #         stck.IsActive = False
                                #         qty_in_stockTrans = stck.Qty
                                #         if StockRate.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, BranchID=BranchID).exists():
                                #             stockRateInstance = StockRate.objects.get(
                                #                 CompanyID=CompanyID, StockRateID=StockRateID, BranchID=BranchID)
                                #             stockRateInstance.Qty = float(
                                #                 stockRateInstance.Qty) - float(qty_in_stockTrans)
                                #             stockRateInstance.save()
                                #         stck.save()

            # if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PurchaseMasterID, BranchID=BranchID, VoucherType="PI").exists():
            #         stockPostingInstances = StockPosting.objects.filter(
            #             CompanyID=CompanyID, VoucherMasterID=PurchaseMasterID, BranchID=BranchID, VoucherType="PI").delete()

            purchaseDetails = data["PurchaseDetails"]
            for purchaseDetail in purchaseDetails:
                ProductID = purchaseDetail['ProductID']
                if ProductID:
                    pk = purchaseDetail['unq_id']
                    detailID = purchaseDetail['detailID']
                    Qty_detail = purchaseDetail['Qty']
                    FreeQty = purchaseDetail['FreeQty']
                    UnitPrice = float(purchaseDetail['UnitPrice'])
                    InclusivePrice = float(purchaseDetail['InclusivePrice'])
                    RateWithTax = float(purchaseDetail['RateWithTax'])
                    CostPerItem = float(purchaseDetail['CostPerItem'])
                    PriceListID = purchaseDetail['PriceListID']
                    DiscountPerc = float(purchaseDetail['DiscountPerc'])
                    DiscountAmount = float(purchaseDetail['DiscountAmount'])
                    AddlDiscPerc = float(purchaseDetail['AddlDiscPerc'])
                    AddlDiscAmt = float(purchaseDetail['AddlDiscAmt'])
                    GrossAmount = float(purchaseDetail['GrossAmount'])
                    TaxableAmount = float(purchaseDetail['TaxableAmount'])
                    VATPerc = float(purchaseDetail['VATPerc'])
                    VATAmount = float(purchaseDetail['VATAmount'])
                    SGSTPerc = float(purchaseDetail['SGSTPerc'])
                    SGSTAmount = float(purchaseDetail['SGSTAmount'])
                    CGSTPerc = float(purchaseDetail['CGSTPerc'])
                    CGSTAmount = float(purchaseDetail['CGSTAmount'])
                    IGSTPerc = float(purchaseDetail['IGSTPerc'])
                    IGSTAmount = float(purchaseDetail['IGSTAmount'])
                    NetAmount = float(purchaseDetail['NetAmount'])
                    TAX1Perc = float(purchaseDetail['TAX1Perc'])
                    TAX1Amount = float(purchaseDetail['TAX1Amount'])
                    TAX2Perc = float(purchaseDetail['TAX2Perc'])
                    TAX2Amount = float(purchaseDetail['TAX2Amount'])
                    TAX3Perc = float(purchaseDetail['TAX3Perc'])
                    TAX3Amount = float(purchaseDetail['TAX3Amount'])
                    BatchCode = purchaseDetail['BatchCode']
                    is_inclusive = purchaseDetail['is_inclusive']

                    try:
                        ManufactureDate = purchaseDetail['ManufactureDate']

                    except:
                        ManufactureDate = None

                    try:
                        ExpiryDate = purchaseDetail['ExpiryDate']
                    except:
                        ExpiryDate = None

                    try:
                        SalesPrice = purchaseDetail['SalesPrice']
                    except:
                        SalesPrice = None

                    if not SalesPrice == None:
                        SalesPrice = float(purchaseDetail['SalesPrice'])

                    try:
                        ProductTaxID = purchaseDetail['ProductTaxID']
                    except:
                        ProductTaxID = ""
                        # SalesPrice = round(SalesPrice, PriceRounding)

                    # UnitPrice = round(UnitPrice, PriceRounding)
                    # InclusivePrice = round(InclusivePrice, PriceRounding)
                    # RateWithTax = round(RateWithTax, PriceRounding)
                    # CostPerItem = round(CostPerItem, PriceRounding)
                    # DiscountPerc = round(DiscountPerc, PriceRounding)
                    # DiscountAmount = round(DiscountAmount, PriceRounding)
                    # AddlDiscPerc = round(AddlDiscPerc, PriceRounding)
                    # AddlDiscAmt = round(AddlDiscAmt, PriceRounding)
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

                    if is_inclusive == True:
                        Batch_purchasePrice = InclusivePrice
                    else:
                        Batch_purchasePrice = UnitPrice

                    if ManufactureDate == "":
                        ManufactureDate = None

                    if ExpiryDate == "":
                        ExpiryDate = None

                    product_is_Service = Product.objects.get(
                        CompanyID=CompanyID,ProductID=ProductID).is_Service

                    MultiFactor = PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor

                    qty_batch = float(FreeQty) + float(Qty_detail)
                    Qty_batch = float(MultiFactor) * float(qty_batch)

                    CostPerItem = float(TaxableAmount) / float(qty_batch)

                    # priceList = PriceList.objects.get(CompanyID=CompanyID,PriceListID=PriceListID,BranchID=BranchID)

                    if product_is_Service == False:
                        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                            check_EnableProductBatchWise = GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
                            check_BatchCriteria = "PurchasePrice"
                            if GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="BatchCriteria").exists():
                                check_BatchCriteria = GeneralSettings.objects.get(
                                    CompanyID=CompanyID, SettingsType="BatchCriteria").SettingsValue
                                print(check_BatchCriteria)
                            pri_ins = PriceList.objects.get(
                                CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID)
                            # PurchasePrice = pri_ins.PurchasePrice
                            # SalesPrice = pri_ins.SalesPrice

                            if SalesPrice == None:
                                SalesPrice = pri_ins.SalesPrice
                            pri_ins.SalesPrice = SalesPrice
                            pri_ins.save()

                            if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                                if check_BatchCriteria == "PurchasePrice":
                                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PriceListID=PriceListID, PurchasePrice=Batch_purchasePrice).exists():
                                        batch_ins = Batch.objects.filter(
                                            CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PriceListID=PriceListID, PurchasePrice=Batch_purchasePrice).last()
                                        StockIn = batch_ins.StockIn
                                        print(StockIn)
                                        BatchCode = batch_ins.BatchCode
                                        SalesPrice = batch_ins.SalesPrice
                                        NewStock = float(
                                            StockIn) + float(qty_batch)
                                        if ExpiryDate:
                                            batch_ins.ExpiryDate = ExpiryDate
                                        if ManufactureDate:
                                            batch_ins.ManufactureDate = ManufactureDate
                                        batch_ins.StockIn = NewStock
                                        batch_ins.save()
                                    else:
                                        BatchCode = get_auto_AutoBatchCode(
                                            Batch, BranchID, CompanyID)
                                        Batch.objects.create(
                                            CompanyID=CompanyID,
                                            BranchID=BranchID,
                                            BatchCode=BatchCode,
                                            StockIn=qty_batch,
                                            PurchasePrice=Batch_purchasePrice,
                                            SalesPrice=SalesPrice,
                                            PriceListID=PriceListID,
                                            ProductID=ProductID,
                                            ManufactureDate=ManufactureDate,
                                            ExpiryDate=ExpiryDate,
                                            WareHouseID=WarehouseID,
                                            CreatedDate=today,
                                            UpdatedDate=today,
                                            CreatedUserID=CreatedUserID,
                                        )
                                elif check_BatchCriteria == "PurchasePriceAndExpiryDate":
                                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PriceListID=PriceListID, PurchasePrice=Batch_purchasePrice, ExpiryDate=ExpiryDate).exists():
                                        batch_ins = Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID,
                                                                         PriceListID=PriceListID, PurchasePrice=Batch_purchasePrice, ExpiryDate=ExpiryDate).last()
                                        StockIn = batch_ins.StockIn
                                        BatchCode = batch_ins.BatchCode
                                        SalesPrice = batch_ins.SalesPrice
                                        NewStock = float(
                                            StockIn) + float(qty_batch)
                                        batch_ins.StockIn = NewStock
                                        batch_ins.save()
                                    else:
                                        BatchCode = get_auto_AutoBatchCode(
                                            Batch, BranchID, CompanyID)
                                        Batch.objects.create(
                                            CompanyID=CompanyID,
                                            BranchID=BranchID,
                                            BatchCode=BatchCode,
                                            StockIn=qty_batch,
                                            PurchasePrice=Batch_purchasePrice,
                                            SalesPrice=SalesPrice,
                                            PriceListID=PriceListID,
                                            ProductID=ProductID,
                                            ManufactureDate=ManufactureDate,
                                            ExpiryDate=ExpiryDate,
                                            WareHouseID=WarehouseID,
                                            CreatedDate=today,
                                            UpdatedDate=today,
                                            CreatedUserID=CreatedUserID,
                                        )
                                # else:
                                #     if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=Batch_purchasePrice, SalesPrice=SalesPrice).exists():
                                #         batch_ins = Batch.objects.get(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PurchasePrice=Batch_purchasePrice, SalesPrice=SalesPrice)
                                #         StockIn = batch_ins.StockIn
                                #         BatchCode = batch_ins.BatchCode
                                #         NewStock = float(StockIn) + float(qty_batch)
                                #         batch_ins.StockIn = NewStock
                                #         batch_ins.save()
                                #     else:
                                #         BatchCode = get_auto_AutoBatchCode(
                                #             Batch, BranchID, CompanyID)
                                #         Batch.objects.create(
                                #             CompanyID=CompanyID,
                                #             BranchID=BranchID,
                                #             BatchCode=BatchCode,
                                #             StockIn=qty_batch,
                                #             PurchasePrice=Batch_purchasePrice,
                                #             SalesPrice=SalesPrice,
                                #             PriceListID=PriceListID,
                                #             ProductID=ProductID,
                                #             WareHouseID=WarehouseID,
                                #             CreatedDate=today,
                                #             UpdatedDate=today,
                                #             CreatedUserID=CreatedUserID,
                                #         )

                            else:
                                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PriceListID=PriceListID).exists():
                                    batch_ins = Batch.objects.get(
                                        CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode, PriceListID=PriceListID)
                                    StockIn = batch_ins.StockIn
                                    BatchCode = batch_ins.BatchCode
                                    SalesPrice = batch_ins.SalesPrice
                                    NewStock = float(
                                        StockIn) + float(qty_batch)
                                    batch_ins.StockIn = NewStock
                                    batch_ins.save()
                                else:
                                    BatchCode = get_auto_AutoBatchCode(
                                        Batch, BranchID, CompanyID)
                                    Batch.objects.create(
                                        CompanyID=CompanyID,
                                        BranchID=BranchID,
                                        BatchCode=BatchCode,
                                        StockIn=qty_batch,
                                        PurchasePrice=Batch_purchasePrice,
                                        SalesPrice=SalesPrice,
                                        PriceListID=PriceListID,
                                        ProductID=ProductID,
                                        ManufactureDate=ManufactureDate,
                                        ExpiryDate=ExpiryDate,
                                        WareHouseID=WarehouseID,
                                        CreatedDate=today,
                                        UpdatedDate=today,
                                        CreatedUserID=CreatedUserID,
                                    )

                    if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="PurchasePriceUpdate").exists():
                        check_PurchasePriceUpdate = GeneralSettings.objects.get(
                            CompanyID=CompanyID, SettingsType="PurchasePriceUpdate").SettingsValue
                        if check_PurchasePriceUpdate == "True" or check_PurchasePriceUpdate == "true":
                            pri_ins = PriceList.objects.get(
                                CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID)
                            pri_ins.PurchasePrice = Batch_purchasePrice
                            pri_ins.save()

                    # MultiFactor = PriceList.objects.get(
                    #     CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor
                    PriceListID_DefUnit = PriceList.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

                    qty = float(FreeQty) + float(Qty_detail)
                    Qty = float(MultiFactor) * float(qty)
                    Cost = float(CostPerItem) / float(MultiFactor)

                    princeList_instance = PriceList.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit, BranchID=BranchID)
                    PurchasePrice = princeList_instance.PurchasePrice
                    SalesPrice = princeList_instance.SalesPrice

                    

                    if detailID == 0:
                        purchaseDetail_instance = PurchaseDetails.objects.get(
                            CompanyID=CompanyID, pk=pk)
                        PurchaseDetailsID = purchaseDetail_instance.PurchaseDetailsID

                        log_instance = PurchaseDetails_Log.objects.create(
                            TransactionID=PurchaseDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            PurchaseMasterID=PurchaseMasterID,
                            ProductID=ProductID,
                            Qty=Qty_detail,
                            ReturnQty=Qty_detail,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            RateWithTax=RateWithTax,
                            CostPerItem=CostPerItem,
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
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            CompanyID=CompanyID,
                            BatchCode=BatchCode,
                            ManufactureDate=ManufactureDate,
                            ExpiryDate=ExpiryDate,
                            ProductTaxID=ProductTaxID
                        )

                        purchaseDetail_instance.ProductID = ProductID
                        purchaseDetail_instance.Qty = Qty_detail
                        purchaseDetail_instance.ReturnQty = Qty_detail
                        purchaseDetail_instance.FreeQty = FreeQty
                        purchaseDetail_instance.UnitPrice = UnitPrice
                        purchaseDetail_instance.InclusivePrice = InclusivePrice
                        purchaseDetail_instance.RateWithTax = RateWithTax
                        purchaseDetail_instance.CostPerItem = CostPerItem
                        purchaseDetail_instance.PriceListID = PriceListID
                        purchaseDetail_instance.DiscountPerc = DiscountPerc
                        purchaseDetail_instance.DiscountAmount = DiscountAmount
                        purchaseDetail_instance.AddlDiscPerc = AddlDiscPerc
                        purchaseDetail_instance.AddlDiscAmt = AddlDiscAmt
                        purchaseDetail_instance.GrossAmount = GrossAmount
                        purchaseDetail_instance.TaxableAmount = TaxableAmount
                        purchaseDetail_instance.VATPerc = VATPerc
                        purchaseDetail_instance.VATAmount = VATAmount
                        purchaseDetail_instance.SGSTPerc = SGSTPerc
                        purchaseDetail_instance.SGSTAmount = SGSTAmount
                        purchaseDetail_instance.CGSTPerc = CGSTPerc
                        purchaseDetail_instance.CGSTAmount = CGSTAmount
                        purchaseDetail_instance.IGSTPerc = IGSTPerc
                        purchaseDetail_instance.IGSTAmount = IGSTAmount
                        purchaseDetail_instance.NetAmount = NetAmount
                        purchaseDetail_instance.CreatedDate = today
                        purchaseDetail_instance.Action = Action
                        purchaseDetail_instance.UpdatedDate = today
                        purchaseDetail_instance.CreatedUserID = CreatedUserID
                        purchaseDetail_instance.TAX1Perc = TAX1Perc
                        purchaseDetail_instance.TAX1Amount = TAX1Amount
                        purchaseDetail_instance.TAX2Perc = TAX2Perc
                        purchaseDetail_instance.TAX2Amount = TAX2Amount
                        purchaseDetail_instance.TAX3Perc = TAX3Perc
                        purchaseDetail_instance.TAX3Amount = TAX3Amount
                        purchaseDetail_instance.BatchCode = BatchCode
                        purchaseDetail_instance.ManufactureDate = ManufactureDate
                        purchaseDetail_instance.ExpiryDate = ExpiryDate
                        purchaseDetail_instance.LogID = log_instance.ID
                        purchaseDetail_instance.ProductTaxID = log_instance.ProductTaxID

                        purchaseDetail_instance.save()

                        if product_is_Service == False:
                            if StockPosting.objects.filter(CompanyID=CompanyID,WareHouseID=WarehouseID, VoucherMasterID=PurchaseMasterID,VoucherDetailID=PurchaseDetailsID,BranchID=BranchID, VoucherType="PI",ProductID=ProductID).exists():
                                stock_instance = StockPosting.objects.filter(CompanyID=CompanyID,WareHouseID=WarehouseID, VoucherMasterID=PurchaseMasterID,VoucherDetailID=PurchaseDetailsID,BranchID=BranchID, VoucherType="PI",ProductID=ProductID).first()
                                stock_instance.QtyIn = Qty
                                stock_instance.Action = Action
                                stock_instance.save()
                            else:
                                StockPostingID = get_auto_stockPostid(
                                    StockPosting, BranchID, CompanyID)
                                StockPosting.objects.create(
                                    StockPostingID=StockPostingID,
                                    BranchID=BranchID,
                                    Action=Action,
                                    Date=Date,
                                    VoucherMasterID=PurchaseMasterID,
                                    VoucherDetailID=PurchaseDetailsID,
                                    VoucherType=VoucherType,
                                    ProductID=ProductID,
                                    BatchID=BatchID,
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

                                StockPosting_Log.objects.create(
                                    TransactionID=StockPostingID,
                                    BranchID=BranchID,
                                    Action=Action,
                                    Date=Date,
                                    VoucherMasterID=PurchaseMasterID,
                                    VoucherDetailID=PurchaseDetailsID,
                                    VoucherType=VoucherType,
                                    ProductID=ProductID,
                                    BatchID=BatchID,
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

                            update_stock(CompanyID,BranchID,ProductID)





                        # if product_is_Service == False:

                        #     StockPosting.objects.create(
                        #         StockPostingID=StockPostingID,
                        #         BranchID=BranchID,
                        #         Action=Action,
                        #         Date=Date,
                        #         VoucherMasterID=PurchaseMasterID,
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
                        #         Date=Date,
                        #         VoucherMasterID=PurchaseMasterID,
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
                        Action = "A"
                        PurchaseDetailsID = get_auto_id(
                            PurchaseDetails, BranchID, CompanyID)

                        log_instance = PurchaseDetails_Log.objects.create(
                            TransactionID=PurchaseDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            PurchaseMasterID=PurchaseMasterID,
                            ProductID=ProductID,
                            Qty=Qty_detail,
                            ReturnQty=Qty_detail,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            RateWithTax=RateWithTax,
                            CostPerItem=CostPerItem,
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
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            CompanyID=CompanyID,
                            BatchCode=BatchCode,
                            ProductTaxID=ProductTaxID
                        )

                        PurchaseDetails.objects.create(
                            PurchaseDetailsID=PurchaseDetailsID,
                            BranchID=BranchID,
                            purchase_master=purchaseMaster_instance,
                            Action=Action,
                            PurchaseMasterID=PurchaseMasterID,
                            ProductID=ProductID,
                            Qty=Qty_detail,
                            ReturnQty=Qty_detail,
                            FreeQty=FreeQty,
                            UnitPrice=UnitPrice,
                            InclusivePrice=InclusivePrice,
                            RateWithTax=RateWithTax,
                            CostPerItem=CostPerItem,
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
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            CompanyID=CompanyID,
                            BatchCode=BatchCode,
                            LogID=log_instance.ID,
                            ProductTaxID=ProductTaxID
                        )

                        if product_is_Service == False:
                            StockPostingID = get_auto_stockPostid(
                                StockPosting, BranchID, CompanyID)
                            StockPosting.objects.create(
                                StockPostingID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=Date,
                                VoucherMasterID=PurchaseMasterID,
                                VoucherDetailID=PurchaseDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchID,
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

                            StockPosting_Log.objects.create(
                                TransactionID=StockPostingID,
                                BranchID=BranchID,
                                Action=Action,
                                Date=Date,
                                VoucherMasterID=PurchaseMasterID,
                                VoucherDetailID=PurchaseDetailsID,
                                VoucherType=VoucherType,
                                ProductID=ProductID,
                                BatchID=BatchID,
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

                            update_stock(CompanyID,BranchID,ProductID)

                        # for stockPostingInstance in stockPostingInstances:
                        #     print("its beeen delete")
                        #     stockPostingInstance.delete()

                    

                    # if product_is_Service == False:
                    #     if detailID == 1:
                    #         if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID).exists():
                    #             stockRateInstance = StockRate.objects.get(
                    #                 CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID)

                    #             StockRateID = stockRateInstance.StockRateID
                    #             stockRateInstance.Qty = float(
                    #                 stockRateInstance.Qty) + float(Qty)
                    #             stockRateInstance.save()

                    #             if StockTrans.objects.filter(StockRateID=StockRateID, DetailID=PurchaseDetailsID, MasterID=PurchaseMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                    #                 stockTra_in = StockTrans.objects.filter(
                    #                     StockRateID=StockRateID, DetailID=PurchaseDetailsID, MasterID=PurchaseMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                    #                 stockTra_in.Qty = float(
                    #                     stockTra_in.Qty) + float(Qty)
                    #                 stockTra_in.save()
                    #             else:
                    #                 StockTransID = get_auto_StockTransID(
                    #                     StockTrans, BranchID, CompanyID)
                    #                 StockTrans.objects.create(
                    #                     StockTransID=StockTransID,
                    #                     BranchID=BranchID,
                    #                     VoucherType=VoucherType,
                    #                     StockRateID=StockRateID,
                    #                     DetailID=PurchaseDetailsID,
                    #                     MasterID=PurchaseMasterID,
                    #                     Qty=Qty,
                    #                     IsActive=IsActive,
                    #                     CompanyID=CompanyID,
                    #                 )

                    #         else:
                    #             StockRateID = get_auto_StockRateID(
                    #                 StockRate, BranchID, CompanyID)
                    #             StockRate.objects.create(
                    #                 StockRateID=StockRateID,
                    #                 BranchID=BranchID,
                    #                 BatchID=BatchID,
                    #                 PurchasePrice=PurchasePrice,
                    #                 SalesPrice=SalesPrice,
                    #                 Qty=Qty,
                    #                 Cost=Cost,
                    #                 ProductID=ProductID,
                    #                 WareHouseID=WarehouseID,
                    #                 Date=Date,
                    #                 PriceListID=PriceListID_DefUnit,
                    #                 CreatedUserID=CreatedUserID,
                    #                 CreatedDate=today,
                    #                 UpdatedDate=today,
                    #                 CompanyID=CompanyID,
                    #             )

                    #             StockTransID = get_auto_StockTransID(
                    #                 StockTrans, BranchID, CompanyID)
                    #             StockTrans.objects.create(
                    #                 StockTransID=StockTransID,
                    #                 BranchID=BranchID,
                    #                 VoucherType=VoucherType,
                    #                 StockRateID=StockRateID,
                    #                 DetailID=PurchaseDetailsID,
                    #                 MasterID=PurchaseMasterID,
                    #                 Qty=Qty,
                    #                 IsActive=IsActive,
                    #                 CompanyID=CompanyID,
                    #             )
                    #     else:
                    #         if StockRate.objects.filter(CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit, Cost=Cost, WareHouseID=WarehouseID).exists():
                    #             stockRate_instance = StockRate.objects.get(
                    #                 CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit, Cost=Cost, WareHouseID=WarehouseID)
                    #             print("==============>>>>>>>>>>>>>>>>>============")
                    #             print(ProductID)
                    #             print(PriceListID_DefUnit)
                    #             print(stockRate_instance)
                    #             StockRateID = stockRate_instance.StockRateID
                    #             if StockTrans.objects.filter(CompanyID=CompanyID, DetailID=PurchaseDetailsID, MasterID=PurchaseMasterID, BranchID=BranchID,
                    #                                          VoucherType=VoucherType, IsActive=True, StockRateID=StockRateID).exists():
                    #                 stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID, DetailID=PurchaseDetailsID, MasterID=PurchaseMasterID, BranchID=BranchID,
                    #                                                              VoucherType=VoucherType, IsActive=True, StockRateID=StockRateID)

                    #                 if float(stockTrans_instance.Qty) < float(Qty):
                    #                     deff = float(Qty) - \
                    #                         float(stockTrans_instance.Qty)
                    #                     stockTrans_instance.Qty = float(
                    #                         stockTrans_instance.Qty) + float(deff)
                    #                     stockTrans_instance.save()

                    #                     stockRate_instance.Qty = float(
                    #                         stockRate_instance.Qty) + float(deff)
                    #                     stockRate_instance.save()

                    #                 elif float(stockTrans_instance.Qty) > float(Qty):
                    #                     deff = float(
                    #                         stockTrans_instance.Qty) - float(Qty)
                    #                     stockTrans_instance.Qty = float(
                    #                         stockTrans_instance.Qty) - float(deff)
                    #                     stockTrans_instance.save()

                    #                     stockRate_instance.Qty = float(
                    #                         stockRate_instance.Qty) - float(deff)
                    #                     stockRate_instance.save()

                    # if StockTrans.objects.filter(CompanyID=CompanyID,MasterID=PurchaseMasterID,DetailID=PurchaseDetailsID,BranchID=BranchID,VoucherType=VoucherType,IsActive=True).exists():
                    #     stockTrans_instance = StockTrans.objects.filter(CompanyID=CompanyID,MasterID=PurchaseMasterID,DetailID=PurchaseDetailsID,BranchID=BranchID,VoucherType=VoucherType,IsActive=True).first()
                    #     stockRateID = stockTrans_instance.StockRateID
                    #     stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,StockRateID=stockRateID,BranchID=BranchID,WareHouseID=WarehouseID)

                    #     if float(stockTrans_instance.Qty) < float(Qty):
                    #         deff = float(Qty) - float(stockTrans_instance.Qty)
                    #         stockTrans_instance.Qty = float(stockTrans_instance.Qty) + float(deff)
                    #         stockTrans_instance.save()

                    #         stockRate_instance.Qty = float(stockRate_instance.Qty) + float(deff)
                    #         stockRate_instance.save()

                    #     elif float(stockTrans_instance.Qty) > float(Qty):
                    #         deff = float(stockTrans_instance.Qty) - float(Qty)
                    #         stockTrans_instance.Qty = float(stockTrans_instance.Qty) - float(deff)
                    #         stockTrans_instance.save()

                    #         stockRate_instance.Qty = float(stockRate_instance.Qty) - float(deff)
                    #         stockRate_instance.save()

            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Purchase',
            #              'Edit', 'Purchase Updated successfully.', 'Purchase Updated successfully.')
            response_data = {
                "StatusCode": 6000,
                "message": "purchase updated Successfully!!!",
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

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Purchase',
                     'Edit', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def list_purchaseMaster(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    QtyRounding = data['QtyRounding']
    PriceRounding = data['PriceRounding']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']

        if PurchaseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():

            instances = PurchaseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

            serialized = PurchaseMasterRestSerializer(instances, many=True, context={"CompanyID": CompanyID,
                                                                                     "PriceRounding": PriceRounding, "QtyRounding": QtyRounding})

            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Purchase',
            #              'List', 'Purchase List Viewed successfully.', 'Purchase List Viewed successfully.')
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Purchase',
            #              'List', 'Purchase List Viewed Failed.', 'Purchase not found in this branch')
            response_data = {
                "StatusCode": 6001,
                "message": "Purchase Master not found in this branch."
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
def purchase_pagination(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    QtyRounding = data['QtyRounding']
    PriceRounding = data['PriceRounding']

    page_number = data['page_no']
    items_per_page = data['items_per_page']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']

        if page_number and items_per_page:
            purchase_object = PurchaseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

            purchase_sort_pagination = list_pagination(
                purchase_object,
                items_per_page,
                page_number
            )
            purchase_serializer = PurchaseMasterRest1Serializer(
                purchase_sort_pagination,
                many=True,
                context={"request": request, "CompanyID": CompanyID,
                         "PriceRounding": PriceRounding, "QtyRounding": QtyRounding}
            )
            data = purchase_serializer.data
            if not data == None:
                response_data = {
                    "StatusCode": 6000,
                    "data": data,
                    "count": len(purchase_object)
                }
            else:
                response_data = {
                    "StatusCode": 6001
                }

            return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def purchaseMaster(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    QtyRounding = data['QtyRounding']
    PriceRounding = data['PriceRounding']

    if PurchaseMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = PurchaseMaster.objects.get(CompanyID=CompanyID, pk=pk)
        serialized = PurchaseMasterRestSerializer(instance, context={"CompanyID": CompanyID,
                                                                     "PriceRounding": PriceRounding, "QtyRounding": QtyRounding})

        #request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Purchase',
        #              'View', 'Purchase single Viewed successfully.', 'Purchase single Viewed successfully.')

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Purchase Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_purchaseMaster(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    instance = None
    if PurchaseMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = PurchaseMaster.objects.get(CompanyID=CompanyID, pk=pk)
        PurchaseMasterID = instance.PurchaseMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        RefferenceBillNo = instance.RefferenceBillNo
        Date = instance.Date
        VenderInvoiceDate = instance.VenderInvoiceDate
        CreditPeriod = instance.CreditPeriod
        LedgerID = instance.LedgerID
        PriceCategoryID = instance.PriceCategoryID
        EmployeeID = instance.EmployeeID
        PurchaseAccount = instance.PurchaseAccount
        CustomerName = instance.CustomerName
        Address1 = instance.Address1
        Address2 = instance.Address2
        Address3 = instance.Address3
        Notes = instance.Notes
        FinacialYearID = instance.FinacialYearID
        TotalGrossAmt = instance.TotalGrossAmt
        TotalTax = instance.TotalTax
        NetTotal = instance.NetTotal
        AddlDiscPercent = instance.AddlDiscPercent
        AddlDiscAmt = instance.AddlDiscAmt
        AdditionalCost = instance.AdditionalCost
        TotalDiscount = instance.TotalDiscount
        GrandTotal = instance.GrandTotal
        RoundOff = instance.RoundOff
        TransactionTypeID = instance.TransactionTypeID
        WarehouseID = instance.WarehouseID
        IsActive = instance.IsActive

        TaxID = instance.TaxID
        TaxType = instance.TaxType
        VATAmount = instance.VATAmount
        SGSTAmount = instance.SGSTAmount
        CGSTAmount = instance.CGSTAmount
        IGSTAmount = instance.IGSTAmount
        TAX1Amount = instance.TAX1Amount
        TAX2Amount = instance.TAX2Amount
        TAX3Amount = instance.TAX3Amount
        BillDiscPercent = instance.BillDiscPercent
        BillDiscAmt = instance.BillDiscAmt
        Balance = instance.Balance
        Country_of_Supply = instance.Country_of_Supply
        State_of_Supply = instance.State_of_Supply
        GST_Treatment = instance.GST_Treatment
        VAT_Treatment = instance.VAT_Treatment

        Action = "D"

        PurchaseMaster_Log.objects.create(
            TransactionID=PurchaseMasterID,
            BranchID=BranchID,
            Action=Action,
            VoucherNo=VoucherNo,
            RefferenceBillNo=RefferenceBillNo,
            Date=Date,
            VenderInvoiceDate=VenderInvoiceDate,
            CreditPeriod=CreditPeriod,
            LedgerID=LedgerID,
            PriceCategoryID=PriceCategoryID,
            EmployeeID=EmployeeID,
            PurchaseAccount=PurchaseAccount,
            CustomerName=CustomerName,
            Address1=Address1,
            Address2=Address2,
            Address3=Address3,
            Notes=Notes,
            FinacialYearID=FinacialYearID,
            TotalGrossAmt=TotalGrossAmt,
            TotalTax=TotalTax,
            NetTotal=NetTotal,
            AddlDiscPercent=AddlDiscPercent,
            AddlDiscAmt=AddlDiscAmt,
            AdditionalCost=AdditionalCost,
            TotalDiscount=TotalDiscount,
            GrandTotal=GrandTotal,
            RoundOff=RoundOff,
            TransactionTypeID=TransactionTypeID,
            WarehouseID=WarehouseID,
            IsActive=IsActive,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            TaxID=TaxID,
            TaxType=TaxType,
            VATAmount=VATAmount,
            SGSTAmount=SGSTAmount,
            CGSTAmount=CGSTAmount,
            IGSTAmount=IGSTAmount,
            TAX1Amount=TAX1Amount,
            TAX2Amount=TAX2Amount,
            TAX3Amount=TAX3Amount,
            BillDiscPercent=BillDiscPercent,
            BillDiscAmt=BillDiscAmt,
            Balance=Balance,
            CompanyID=CompanyID,
            Country_of_Supply=Country_of_Supply,
            State_of_Supply=State_of_Supply,
            GST_Treatment=GST_Treatment,
            VAT_Treatment=VAT_Treatment,
        )

        if LedgerPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PurchaseMasterID, BranchID=BranchID, VoucherType="PI").exists():
            update_ledger = UpdateLedgerBalance(CompanyID,BranchID,0,PurchaseMasterID,"PI",0,"Cr","update")
            ledgerPostInstances = LedgerPosting.objects.filter(
                CompanyID=CompanyID, VoucherMasterID=PurchaseMasterID, BranchID=BranchID, VoucherType="PI")
            for ledgerPostInstance in ledgerPostInstances:
                LedgerPostingID = ledgerPostInstance.LedgerPostingID
                VoucherType = ledgerPostInstance.VoucherType
                VoucherNo = ledgerPostInstance.VoucherNo
                RelatedLedgerID = ledgerPostInstance.RelatedLedgerID
                Debit = ledgerPostInstance.Debit
                Credit = ledgerPostInstance.Credit
                IsActive = ledgerPostInstance.IsActive
                Date = ledgerPostInstance.Date
                LedgerID = ledgerPostInstance.LedgerID

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
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
        if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PurchaseMasterID, BranchID=BranchID, VoucherType="PI").exists():
            stockPostingInstances = StockPosting.objects.filter(
                CompanyID=CompanyID, VoucherMasterID=PurchaseMasterID, BranchID=BranchID, VoucherType="PI")
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

                update_stock(CompanyID,BranchID,ProductID)

        detail_instances = PurchaseDetails.objects.filter(
            CompanyID=CompanyID, PurchaseMasterID=PurchaseMasterID)

        for detail_instance in detail_instances:

            PurchaseDetailsID = detail_instance.PurchaseDetailsID
            BranchID = detail_instance.BranchID
            PurchaseMasterID = detail_instance.PurchaseMasterID
            ProductID = detail_instance.ProductID
            Qty = detail_instance.Qty
            FreeQty = detail_instance.FreeQty
            UnitPrice = detail_instance.UnitPrice
            RateWithTax = detail_instance.RateWithTax
            CostPerItem = detail_instance.CostPerItem
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
            TAX1Perc = detail_instance.TAX1Perc
            TAX1Amount = detail_instance.TAX1Amount
            TAX2Perc = detail_instance.TAX2Perc
            TAX2Amount = detail_instance.TAX2Amount
            TAX3Perc = detail_instance.TAX3Perc
            TAX3Amount = detail_instance.TAX3Amount
            ProductTaxID = detail_instance.ProductTaxID

            update_stock(CompanyID,BranchID,ProductID)           

            BatchCode = detail_instance.BatchCode
            if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
                batch_ins = Batch.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                StockIn = batch_ins.StockIn
                print(StockIn)
                print(Qty)
                batch_ins.StockIn = float(StockIn) - float(Qty)
                print(batch_ins.StockIn)
                batch_ins.save()

            PurchaseDetails_Log.objects.create(
                TransactionID=PurchaseDetailsID,
                BranchID=BranchID,
                Action=Action,
                PurchaseMasterID=PurchaseMasterID,
                ProductID=ProductID,
                Qty=Qty,
                FreeQty=FreeQty,
                UnitPrice=UnitPrice,
                RateWithTax=RateWithTax,
                CostPerItem=CostPerItem,
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
                TAX1Perc=TAX1Perc,
                TAX1Amount=TAX1Amount,
                TAX2Perc=TAX2Perc,
                TAX2Amount=TAX2Amount,
                TAX3Perc=TAX3Perc,
                TAX3Amount=TAX3Amount,
                CompanyID=CompanyID,
                BatchCode=BatchCode,
                ProductTaxID=ProductTaxID
            )

            # if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=PurchaseDetailsID,MasterID=PurchaseMasterID,BranchID=BranchID,VoucherType="PI").exists():
            #     stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID,DetailID=PurchaseDetailsID,MasterID=PurchaseMasterID,BranchID=BranchID,VoucherType="PI")

            #     stockRateID = stockTrans_instance.StockRateID
            #     stockTrans_instance.IsActive = False
            #     stockTrans_instance.save()

            #     stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,StockRateID=stockRateID,BranchID=BranchID)
            #     stockRate_instance.Qty = stockTrans_instance.Qty
            #     stockRate_instance.save()

            if StockTrans.objects.filter(CompanyID=CompanyID, DetailID=PurchaseDetailsID, MasterID=PurchaseMasterID, BranchID=BranchID, VoucherType="PI", IsActive=True).exists():
                stockTrans_instances = StockTrans.objects.filter(
                    CompanyID=CompanyID, DetailID=PurchaseDetailsID, MasterID=PurchaseMasterID, BranchID=BranchID, VoucherType="PI", IsActive=True)

                for i in stockTrans_instances:
                    stockRateID = i.StockRateID
                    i.IsActive = False
                    i.save()

                    stockRate_instance = StockRate.objects.get(
                        CompanyID=CompanyID, StockRateID=stockRateID, BranchID=BranchID)
                    stockRate_instance.Qty = float(
                        stockRate_instance.Qty) - float(i.Qty)
                    stockRate_instance.save()
            detail_instance.delete()
        instance.delete()
        
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Purchase',
                     'Delete', 'Purchase Deleted successfully.', 'Purchase Deleted successfully.')

        response_data = {
            "StatusCode": 6000,
            "title": "Success",
            "message": "Purchase Master Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "title": "Failed",
            "message": "Purchase Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def report_purchases(request):
    data = request.data
    CompanyID = data['CompanyID']
    ReffNo = data['ReffNo']
    CompanyID = get_company(CompanyID)
    PriceRounding = int(data['PriceRounding'])
    serialized1 = ListSerializerforReport(data=request.data)
    try:
        page_number = data['page_no']
    except:
        page_number = ""

    try:
        items_per_page = data['items_per_page']
    except:
        items_per_page = ""

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']

        purchase_data = []
        purchaseReturn_data = []
        Total_netAmt_purchase = 0
        Total_GrossAmt_purchase = 0
        Total_netAmt_purchaseRetn = 0
        Total_tax_purchase = 0
        Total_tax_purchaseRetn = 0
        Total_billDiscount_purchase = 0
        Total_billDiscount_purchaseRetn = 0
        Total_grandTotal_purchase = 0
        Total_grandTotal_purchaseRetn = 0

        PurchaseCode = 6001
        PurchaseReturnCode = 6001

        count_purchase = 0
        count_purchase_return = 0
        count_divided_purchase = 0
        count_divided_purchase_return = 0

        if ReffNo:
            if PurchaseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, RefferenceBillNo=ReffNo).exists():
                instances = PurchaseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, RefferenceBillNo=ReffNo)
                count_purchase = instances.count()
                if page_number and items_per_page:
                    purchase_sort_pagination = list_pagination(
                        instances,
                        items_per_page,
                        page_number
                    )
                

                serialized_purchase = PurchaseMasterRest1Serializer(purchase_sort_pagination, many=True, context={
                                                                   "CompanyID": CompanyID, "PriceRounding": PriceRounding})
                purchase_data = serialized_purchase.data
                PurchaseCode = 6000

                for i_purchase in instances:
                    Total_GrossAmt_purchase += i_purchase.TotalGrossAmt
                    Total_netAmt_purchase += i_purchase.NetTotal
                    Total_tax_purchase += i_purchase.TotalTax
                    Total_billDiscount_purchase += i_purchase.BillDiscAmt
                    Total_grandTotal_purchase += i_purchase.GrandTotal

        else:
            if PurchaseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
                instances = PurchaseMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)
                count_purchase = instances.count()
                if page_number and items_per_page:
                    purchase_sort_pagination = list_pagination(
                        instances,
                        items_per_page,
                        page_number
                    )

                serialized_purchase = PurchaseMasterRest1Serializer(purchase_sort_pagination, many=True, context={
                                                                   "CompanyID": CompanyID, "PriceRounding": PriceRounding})
                purchase_data = serialized_purchase.data
                PurchaseCode = 6000

                for i_purchase in instances:
                    Total_GrossAmt_purchase += i_purchase.TotalGrossAmt
                    Total_netAmt_purchase += i_purchase.NetTotal
                    Total_tax_purchase += i_purchase.TotalTax
                    Total_billDiscount_purchase += i_purchase.BillDiscAmt
                    Total_grandTotal_purchase += i_purchase.GrandTotal

        if PurchaseReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate).exists():
            instances_purchaseReturn = PurchaseReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate)
            count_purchase_return = instances_purchaseReturn.count()
            serialized_purchaseReturn = PurchaseReturnMasterRestSerializer(
                instances_purchaseReturn, many=True, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding})
            purchaseReturn_data = serialized_purchaseReturn.data
            PurchaseReturnCode = 6000

            for i_purchaseReturn in instances_purchaseReturn:
                Total_netAmt_purchaseRetn += i_purchaseReturn.NetTotal
                Total_tax_purchaseRetn += i_purchaseReturn.TotalTax
                Total_billDiscount_purchaseRetn += i_purchaseReturn.BillDiscAmt
                Total_grandTotal_purchaseRetn += i_purchaseReturn.GrandTotal

        #request , company, log_type, user, source, action, message, description
        # activity_log(request, CompanyID, 'Information', CreatedUserID, 'PurchaseReport', 'Report', 'Purchase Report Viewed successfully.', 'Purchase Report Viewed successfully.')
        if purchase_data:
            PurchaseCode = 6000
        if purchaseReturn_data:
            PurchaseReturnCode = 6000
        if purchase_data or purchaseReturn_data:
            count_divided_purchase = math.ceil(float(count_purchase)/ 10)
            count_divided_purchase_return = math.ceil(float(count_purchase_return)/ 10)
            response_data = {
                "StatusCode": 6000,
                "count": len(instances),
                "count_divided_purchase": count_divided_purchase,
                "count_divided_purchase_return": count_divided_purchase_return,
                "PurchaseCode": PurchaseCode,
                "PurchaseReturnCode": PurchaseReturnCode,
                "purchase_data": purchase_data,
                "purchaseReturn_data": purchaseReturn_data,
                "Total_GrossAmt_purchase": round(Total_GrossAmt_purchase, PriceRounding),
                "Total_netAmt_purchase": round(Total_netAmt_purchase, PriceRounding),
                "Total_netAmt_purchaseRetn": round(Total_netAmt_purchaseRetn, PriceRounding),
                "Total_tax_purchase": round(Total_tax_purchase, PriceRounding),
                "Total_tax_purchaseRetn": round(Total_tax_purchaseRetn, PriceRounding),
                "Total_billDiscount_purchase": round(Total_billDiscount_purchase, PriceRounding),
                "Total_billDiscount_purchaseRetn": round(Total_billDiscount_purchaseRetn, PriceRounding),
                "Total_grandTotal_purchase": round(Total_grandTotal_purchase, PriceRounding),
                "Total_grandTotal_purchaseRetn": round(Total_grandTotal_purchaseRetn, PriceRounding),
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
def purchaseInvoice_for_PurchaseReturn(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    VoucherNo = data['VoucherNo']
    PriceRounding = data['PriceRounding']
    if PurchaseMaster.objects.filter(CompanyID=CompanyID, VoucherNo=VoucherNo, BranchID=BranchID).exists():
        instance = PurchaseMaster.objects.get(
            CompanyID=CompanyID, VoucherNo=VoucherNo, BranchID=BranchID)

        serialized = PurchaseMasterForReturnSerializer(instance, context={"CompanyID": CompanyID,
                                                                          "PriceRounding": PriceRounding, })

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Purchase Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def default_values(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']

    default_productGroup = ProductGroup.objects.get(
        CompanyID=CompanyID, ProductGroupID=1, BranchID=BranchID).GroupName
    default_brand = Brand.objects.get(
        CompanyID=CompanyID, BrandID=1, BranchID=BranchID).BrandName
    default_unit = Unit.objects.get(
        CompanyID=CompanyID, UnitID=1, BranchID=BranchID).UnitName
    default_warehouse = Warehouse.objects.get(
        CompanyID=CompanyID, WarehouseID=1, BranchID=BranchID).WarehouseName

    ProductCode = "PC1000"
    VoucherNo = "OS1"

    if default_productGroup and default_brand and default_unit:
        if OpeningStockMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instance = OpeningStockMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "OS" + str(new_num)

            VoucherNo = new_VoucherNo
            # response_data = {
            #     "StatusCode" : 6000,
            #     "default_productGroup" : default_productGroup,
            #     "default_brand" : default_brand,
            #     "default_unit" : default_unit,
            #     "default_warehouse" : default_warehouse,
            #     "VoucherNo" : new_VoucherNo
            # }

        product_count = 0

        # if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        #     product_count = Product.objects.filter(
        #         CompanyID=CompanyID, BranchID=BranchID).count()
        #     latest_ProductCode = Product.objects.filter(
        #         CompanyID=CompanyID, BranchID=BranchID).order_by("ProductID").last()

        #     ProductCode = latest_ProductCode.ProductCode
        #     if not ProductCode.isdecimal():
        #         temp = re.compile("([a-zA-Z]+)([0-9]+)")
        #         if temp.match(ProductCode):
        #             res = temp.match(ProductCode).groups()

        #             code, number = res

        #             number = int(number) + 1

        #             ProductCode = str(code) + str(number)
        #         else:
        #             ProductCode = str(float(ProductCode) +
        #                               1).zfill(len(ProductCode))
        #     else:
        #         # ProductCode = float(ProductCode) + 1
        #         ProductCode = str(float(ProductCode) +
        #                           1).zfill(len(ProductCode))

        #     ProductCode = "PC1000"

        if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            product_count = Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID).count()
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
            "VoucherNo": VoucherNo,
            "default_productGroup": default_productGroup,
            "default_brand": default_brand,
            "default_unit": default_unit,
            "default_warehouse": default_warehouse,
            "ProductCode": ProductCode,
            "product_count": product_count
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured!",
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def search_purchases(request):
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
        if PurchaseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instances = PurchaseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

            if length < 3:
                if param == "VoucherNo":
                    instances = instances.filter(
                        (Q(VoucherNo__icontains=product_name)))[:10]
                elif param == "Date":
                    instances = instances.filter(
                        (Q(Date__icontains=product_name)))[:10]
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
                else:
                    ledger_ids = []
                    if AccountLedger.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerName__icontains=product_name).exists():
                        ledger_ins = AccountLedger.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, LedgerName__icontains=product_name)
                        for l in ledger_ins:
                            ledger_ids.append(l.LedgerID)
                    instances = instances.filter((Q(LedgerID__in=ledger_ids)))

            serialized = PurchaseMasterRestSerializer(instances, many=True, context={
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
def purchaseOrder_for_purchaseInvoice(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    OrderNo = data['OrderNo']
    BranchID = data['BranchID']
    instance = None
    if PurchaseOrderMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherNo=OrderNo, IsInvoiced="N").exists():
        instance = PurchaseOrderMaster.objects.get(
            CompanyID=CompanyID, BranchID=BranchID, VoucherNo=OrderNo, IsInvoiced="N")
        serialized = PurchaseOrderMasterRestSerializer(
            instance, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding, })

        print(serialized.data)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Purchase Order Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def purchaseRegister_report(request):
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
    try:
        CreatedUserID = data['CreatedUserID']
    except:
        CreatedUserID = 1

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

        if PurchaseMaster.objects.filter(CompanyID=CompanyID, Date__gte=FromDate, Date__lte=ToDate).exists():
            purchaseMaster_instances = PurchaseMaster.objects.filter(
                CompanyID=CompanyID, Date__gte=FromDate, Date__lte=ToDate)

            if wareHouseVal > 0:
                if purchaseMaster_instances.filter(WarehouseID=wareHouseVal).exists():
                    purchaseMaster_instances = purchaseMaster_instances.filter(
                        WarehouseID=wareHouseVal)
                else:
                    #request , company, log_type, user, source, action, message, description
                    activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Purchase Register Report',
                                 'Report', 'Purchase Register Report Viewed Failed.', 'Purchase is not Found in this Warehouse')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Purchase is not Found in this Warehouse!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
            if userVal > "0":
                UserID = UserTable.objects.get(pk=userVal).customer.user.id
                if purchaseMaster_instances.filter(CreatedUserID=UserID).exists():
                    purchaseMaster_instances = purchaseMaster_instances.filter(
                        CreatedUserID=UserID)
                else:
                    #request , company, log_type, user, source, action, message, description
                    activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Purchase Register Report',
                                 'Report', 'Purchase Register Report Viewed Failed.', 'Purchase is not Found by this user')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Purchase is not Found by this user!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
            if branchVal > 0:
                if purchaseMaster_instances.filter(BranchID=branchVal).exists():
                    purchaseMaster_instances = purchaseMaster_instances.filter(
                        BranchID=branchVal)
                else:
                    #request , company, log_type, user, source, action, message, description
                    activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Purchase Register Report',
                                 'Report', 'Purchase Register Report Viewed Failed.', 'Purchase is not Found under this Branch')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Purchase is not Found under this Branch!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
            if ledgerVal > 0:
                if purchaseMaster_instances.filter(LedgerID=ledgerVal).exists():
                    purchaseMaster_instances = purchaseMaster_instances.filter(
                        LedgerID=ledgerVal)
                else:
                    #request , company, log_type, user, source, action, message, description
                    activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Purchase Register Report',
                                 'Report', 'Purchase Register Report Viewed Failed.', 'Purchase is not Found under this Ledger')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Purchase is not Found under this Ledger!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)

            masterList = []
            final_array = []
            for i in purchaseMaster_instances:
                PurchaseMasterID = i.PurchaseMasterID
                BranchID = i.BranchID
                Date = i.Date
                InvoiceNo = i.VoucherNo

                PurchaseDetail_instances = PurchaseDetails.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, PurchaseMasterID=PurchaseMasterID)
                if produtVal > 0:
                    PurchaseDetail_instances = PurchaseDetail_instances.filter(
                        ProductID=produtVal)
                elif categoryVal > 0:
                    if ProductGroup.objects.filter(CategoryID=categoryVal, CompanyID=CompanyID, BranchID=BranchID).exists():
                        group_instances = ProductGroup.objects.filter(
                            CategoryID=categoryVal, CompanyID=CompanyID, BranchID=BranchID)
                        for group_i in group_instances:
                            ProductGroupID = group_i.ProductGroupID
                            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=ProductGroupID).exists():
                                product_instances = Product.objects.filter(
                                    CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=ProductGroupID)
                                pro_ids = []
                                for product_i in product_instances:
                                    ProductID = product_i.ProductID
                                    pro_ids.append(ProductID)
                                PurchaseDetail_instances = PurchaseDetail_instances.filter(
                                    ProductID__in=pro_ids)
                    else:
                        #request , company, log_type, user, source, action, message, description
                        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Purchase Register Report',
                                     'Report', 'Purchase Register Report Viewed Failed.', 'Purchase is not Found under this Category')
                        response_data = {
                            "StatusCode": 6001,
                            "message": "Purchase is not Found under this Category!"
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
                        PurchaseDetail_instances = PurchaseDetail_instances.filter(
                            ProductID__in=pro_ids)
                    else:
                        #request , company, log_type, user, source, action, message, description
                        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Purchase Register Report',
                                     'Report', 'Purchase Register Report Viewed Failed.', 'Purchase is not Found under this Group')
                        response_data = {
                            "StatusCode": 6001,
                            "message": "Purchase is not Found under this Group!"
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
                        PurchaseDetail_instances = PurchaseDetail_instances.filter(
                            ProductID__in=pro_ids)
                    else:
                        #request , company, log_type, user, source, action, message, description
                        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Purchase Register Report',
                                     'Report', 'Purchase Register Report Viewed Failed.', 'Purchase is not Found under this ProductCode')
                        response_data = {
                            "StatusCode": 6001,
                            "message": "Purchase is not Found under this ProductCode!"
                        }

                        return Response(response_data, status=status.HTTP_200_OK)

                elif barCodeVal:
                    if PriceList.objects.filter(Barcode=barCodeVal, CompanyID=CompanyID, BranchID=BranchID).exists():
                        ProductID = PriceList.objects.filter(
                            Barcode=barCodeVal, CompanyID=CompanyID, BranchID=BranchID).first().ProductID
                        PurchaseDetail_instances = PurchaseDetail_instances.filter(
                            ProductID=ProductID)
                    else:
                        #request , company, log_type, user, source, action, message, description
                        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Purchase Register Report',
                                     'Report', 'Purchase Register Report Viewed Failed.', 'Purchase is not Found under this Bracode')
                        response_data = {
                            "StatusCode": 6001,
                            "message": "Purchase is not Found under this Bracode!"
                        }

                        return Response(response_data, status=status.HTTP_200_OK)

                for s in PurchaseDetail_instances:
                    print("------------------////------------------5044")
                    print(s.CostPerItem)
                    if s.PurchaseMasterID == PurchaseMasterID:
                        if not PurchaseMasterID in masterList:
                            myDict = {
                                "id": i.id,
                                "Date": Date,
                                "InvoiceNo": InvoiceNo,
                                "ProductCode": "",
                                "ProductName": "",
                                "ProductGroup": "",
                                "Barcode": "",
                                "Qty": "",
                                "PurchasePrice": "",
                                "GrossAmount": 0,
                                "VATAmount": 0,
                                "NetAmount": 0,
                                "Cost": 0,
                                "Profit": 0,
                            }
                            if s.InclusivePrice == 0 and s.GrossAmount == 0 and s.VATAmount == 0 and s.NetAmount == 0 and s.CostPerItem == 0:
                                print("IF CONDI@@@@@@@@@@TION")
                            else:
                                final_array.append(myDict)
                            masterList.append(PurchaseMasterID)
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
                    PurchasePrice = s.InclusivePrice
                    GrossAmount = s.GrossAmount
                    VATAmount = s.VATAmount
                    NetAmount = s.NetAmount
                    Cost = s.CostPerItem
                    Profit = float(NetAmount) - (float(Qty) * float(Cost))
                    print(NetAmount)
                    print(Qty)
                    print(Cost)
                    if PurchaseMasterID in masterList:
                        print("=====================//5089")
                        print(Profit)
                        myDict = {
                            "id": i.id,
                            "Date": "-",
                            "InvoiceNo": "-",
                            "ProductCode": ProductCode,
                            "ProductName": ProductName,
                            "ProductGroup": ProductGroupName,
                            "Barcode": Barcode,
                            "Qty": Qty,
                            "PurchasePrice": round(PurchasePrice, PriceRounding),
                            "GrossAmount": round(GrossAmount, PriceRounding),
                            "VATAmount": round(VATAmount, PriceRounding),
                            "NetAmount": round(NetAmount, PriceRounding),
                            "Cost": round(Cost, PriceRounding),
                            "Profit": round(Profit, PriceRounding),
                        }

                    if PurchasePrice == 0 and GrossAmount == 0 and VATAmount == 0 and NetAmount == 0 and Cost == 0 and Profit == 0:
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

            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Purchase Register Report',
            #              'Report', 'Purchase Register Report Viewed Successfully.', 'Purchase Register Report Viewed Successfully.')

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
            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Purchase Register Report',
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
def gst_purchase_report(request):
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
        party_gstin = None
        Total_GrandTotal = 0
       
        print(UserID, "UserIDUserIDUserIDUserIDUserID")

        if UserID:
            UserID = UserTable.objects.get(id=UserID).customer.user.pk
            # if PurchaseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID).exists():
            instances = PurchaseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate, CreatedUserID=UserID)
            return_instances = PurchaseReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate, CreatedUserID=UserID)
            final_array = []
            # =======
            for i in instances:
                LedgerID = i.LedgerID
                if AccountLedger.objects.filter(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID).exists():
                    Particulars = AccountLedger.objects.get(
                        LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID)
                    LedgerName = Particulars.LedgerName
                    if Particulars.AccountGroupUnder == 29:
                        party_gstin = Parties.objects.get(
                            LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID, PartyType="supplier", PartyCode=Particulars.LedgerCode).GSTNumber

                dic = {
                    "Date": i.Date,
                    "VoucherNo": i.VoucherNo,
                    "RefferenceBillNo": i.RefferenceBillNo,
                    "VenderInvoiceDate": i.VenderInvoiceDate,
                    "GrandTotal": i.GrandTotal,
                    "VoucherType": "PI",
                    "Particulars": LedgerName,
                    "party_gstin": party_gstin,
                    "TaxType": i.TaxType,
                    "TotalTax": i.TotalTax,
                    "SGSTAmount": i.SGSTAmount,
                    "IGSTAmount": i.IGSTAmount,
                    "CGSTAmount": i.CGSTAmount,
                    "CESSAmount": 0,
                    # "KFCAmount" : i.KFCAmount,
                    "TotalTaxableAmount": i.TotalTaxableAmount,
                }
                if float(i.TotalTax) > 0:
                    final_array.append(dic)

            for i in return_instances:
                LedgerID = i.LedgerID
                if AccountLedger.objects.filter(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID).exists():
                    Particulars = AccountLedger.objects.get(
                        LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID)
                    LedgerName = Particulars.LedgerName
                    if Particulars.AccountGroupUnder == 29:
                        party_gstin = Parties.objects.get(
                            LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID, PartyType="supplier", PartyCode=Particulars.LedgerCode).GSTNumber
                # try:
                #     KFCAmount = int(i.KFCAmount)
                # except:
                #     KFCAmount = 0

                TotalTaxableAmount = float(i.TotalTaxableAmount)
                if TotalTaxableAmount:
                    TotalTaxableAmount = float(i.TotalTaxableAmount)
                else:
                    TotalTaxableAmount = 0

                dic = {
                    "Date": i.VoucherDate,
                    "VoucherNo": i.VoucherNo,
                    "RefferenceBillNo": i.RefferenceBillNo,
                    "VenderInvoiceDate": i.VenderInvoiceDate,
                    "GrandTotal": i.GrandTotal,
                    "VoucherType": "PR",
                    "Particulars": LedgerName,
                    "party_gstin": party_gstin,
                    "TaxType": i.TaxType,
                    "TotalTax": int(i.TotalTax*-1),
                    "SGSTAmount": int(i.SGSTAmount*-1),
                    "IGSTAmount": int(i.IGSTAmount*-1),
                    "CGSTAmount": int(i.CGSTAmount*-1),
                    "CESSAmount": 0,
                    # "KFCAmount" : KFCAmount*-1,
                    "TotalTaxableAmount": TotalTaxableAmount*-1,
                }
                if float(i.TotalTax) > 0:
                    final_array.append(dic)

            for i in final_array:
                Total_TotalTaxableAmount += float(i['TotalTaxableAmount'])
                Total_TotalTax += float(i['TotalTax'])

                Total_SGSTAmount += float(i['SGSTAmount'])
                Total_CGSTAmount += float(i['CGSTAmount'])
                Total_IGSTAmount += float(i['IGSTAmount'])
                Total_GrandTotal += float(i['GrandTotal'])
                # Total_KFCAmount += float(i['KFCAmount'])
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
                "Total_GrandTotal" : Total_GrandTotal
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     response_data = {
            #         "StatusCode": 6001,
            #         "message": "datas not found!"
            #     }

            # return Response(response_data, status=status.HTTP_200_OK)

        else:
            # if PurchaseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
            instances = PurchaseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)
            # ======
            return_instances = PurchaseReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate)

            final_array = []
            # =======
            for i in instances:
                print(i.TotalTax,"OOOOOOOOOOOOOOOOOO")
                LedgerID = i.LedgerID
                if AccountLedger.objects.filter(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID).exists():
                    Particulars = AccountLedger.objects.get(
                        LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID)
                    LedgerName = Particulars.LedgerName
                    if Particulars.AccountGroupUnder == 29:
                        party_gstin = Parties.objects.get(
                            LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID, PartyType="supplier", PartyCode=Particulars.LedgerCode).GSTNumber

                dic = {
                    "Date": i.Date,
                    "VoucherNo": i.VoucherNo,
                    "RefferenceBillNo": i.RefferenceBillNo,
                    "VenderInvoiceDate": i.VenderInvoiceDate,
                    "GrandTotal": i.GrandTotal,
                    "VoucherType": "PI",
                    "Particulars": LedgerName,
                    "party_gstin": party_gstin,
                    "TaxType": i.TaxType,
                    "TotalTax": i.TotalTax,
                    "SGSTAmount": i.SGSTAmount,
                    "IGSTAmount": i.IGSTAmount,
                    "CGSTAmount": i.CGSTAmount,
                    "CESSAmount": 0,
                    # "KFCAmount" : i.KFCAmount,
                    "TotalTaxableAmount": i.TotalTaxableAmount,
                }
                if float(i.TotalTax) > 0:
                    final_array.append(dic)

            for i in return_instances:
                LedgerID = i.LedgerID
                if AccountLedger.objects.filter(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID).exists():
                    Particulars = AccountLedger.objects.get(
                        LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID)
                    LedgerName = Particulars.LedgerName
                    if Particulars.AccountGroupUnder == 29:
                        party_gstin = Parties.objects.get(
                            LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID, PartyType="supplier", PartyCode=Particulars.LedgerCode).GSTNumber

                # try:
                #     KFCAmount = int(i.KFCAmount)
                # except:
                #     KFCAmount = 0

                TotalTaxableAmount = float(i.TotalTaxableAmount)
                if TotalTaxableAmount:
                    TotalTaxableAmount = float(i.TotalTaxableAmount)
                else:
                    TotalTaxableAmount = 0

                dic = {
                    "Date": i.VoucherDate,
                    "VoucherNo": i.VoucherNo,
                    "RefferenceBillNo": i.RefferenceBillNo,
                    "VenderInvoiceDate": i.VenderInvoiceDate,
                    "GrandTotal": i.GrandTotal,
                    "VoucherType": "PR",
                    "Particulars": LedgerName,
                    "party_gstin": party_gstin,
                    "TaxType": i.TaxType,
                    "TotalTax": int(i.TotalTax*-1),
                    "SGSTAmount": int(i.SGSTAmount*-1),
                    "IGSTAmount": int(i.IGSTAmount*-1),
                    "CGSTAmount": int(i.CGSTAmount*-1),
                    "CESSAmount": 0,
                    # "KFCAmount" : KFCAmount*-1,
                    "TotalTaxableAmount": TotalTaxableAmount*-1,
                }
                if float(i.TotalTax) > 0:
                    final_array.append(dic)

            for i in final_array:
                Total_TotalTaxableAmount += float(i['TotalTaxableAmount'])
                Total_TotalTax += float(i['TotalTax'])

                Total_SGSTAmount += float(i['SGSTAmount'])
                Total_CGSTAmount += float(i['CGSTAmount'])
                Total_IGSTAmount += float(i['IGSTAmount'])
                Total_GrandTotal += float(i['GrandTotal'])
                # Total_KFCAmount += float(i['KFCAmount'])

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
                # "Total_KFCAmount": Total_KFCAmount,
                "Total_GrandTotal" : Total_GrandTotal
            }
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     response_data = {
            #         "StatusCode": 6001,
            #         "message": "datas not found!"
            #     }

            # return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "please provide valid datas!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def purchase_gstr_report(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    serialized1 = ListSerializerforReport(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']

        final_data = []
        final_data = []
        is_ok = False
        count = 0
        # interstate b2b
        tax_types = ["GST Inter-state B2B","GST Inter-state B2C","GST Intra-state B2B","GST Intra-state B2C","GST Intra-state B2B Unregistered"]
        for tx in tax_types:
            if PurchaseMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Date__gte=FromDate,Date__lte=ToDate,TaxType=tx).exists():
                purchase_instances = PurchaseMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Date__gte=FromDate,Date__lte=ToDate,TaxType=tx)
                purchase_ids = purchase_instances.values_list('PurchaseMasterID', flat=True)

                purchase_details = PurchaseDetails.objects.filter(CompanyID=CompanyID,BranchID=BranchID,PurchaseMasterID__in=purchase_ids).exclude(IGSTPerc=0)
                tax_list = purchase_details.values_list('IGSTPerc', flat=True)
                tax_list = set(tax_list)
                # count = 0
                for t in tax_list:
                    gouprd_details = purchase_details.filter(IGSTPerc=t)
                    if gouprd_details:
                        final_data.append({
                            "TaxType" : tx,
                            "TaxPerc" : t,
                            "total_Qty" : 0,
                            "total_amount" : 0,
                            "total_SGSTAmount" : 0,
                            "total_CGSTAmount" : 0,
                            "total_IGSTAmount" : 0,
                            "total_sum_Total" : 0,
                            "data" : [],
                            })
                        total_Qty = 0
                        total_amount = 0
                        total_SGSTAmount = 0
                        total_CGSTAmount = 0
                        total_IGSTAmount = 0
                        total_sum_Total = 0
                        for g in gouprd_details:
                            PurchaseMasterID = g.PurchaseMasterID
                            Date = purchase_instances.get(PurchaseMasterID=PurchaseMasterID).Date
                            InvoiceNo = purchase_instances.get(PurchaseMasterID=PurchaseMasterID).RefferenceBillNo
                            LedgerID = purchase_instances.get(PurchaseMasterID=PurchaseMasterID).LedgerID
                            ProductID = g.ProductID
                            party = ""
                            GSTN = ""
                            City = ""
                            State_id = ""
                            State_Code = ""
                            if AccountLedger.objects.filter(CompanyID=CompanyID,BranchID=BranchID,LedgerID=LedgerID,AccountGroupUnder__in=[10,29]).exists():
                                parties = Parties.objects.get(CompanyID=CompanyID,BranchID=BranchID,LedgerID=LedgerID)
                                party = parties.PartyName
                                GSTN = parties.GSTNumber
                                City = parties.City
                                State_id = parties.State
                                State_Code = parties.State_Code
                                state_name = "" 
                                if State_id:
                                    if State.objects.filter(pk=State_id).exists():
                                        state_name = State.objects.get(pk=State_id).Name

                            product = Product.objects.get(CompanyID=CompanyID,BranchID=BranchID,ProductID=ProductID)
                            item_name = product.ProductName
                            HSN = product.HSNCode

                            Qty = g.Qty
                            UnitID = PriceList.objects.get(CompanyID=CompanyID,BranchID=BranchID,PriceListID=g.PriceListID).UnitID
                            UnitName = Unit.objects.get(CompanyID=CompanyID,BranchID=BranchID,UnitID=UnitID).UnitName
                            Amount = g.TaxableAmount

                            SGSTPerc = g.SGSTPerc
                            CGSTPerc = g.CGSTPerc
                            IGSTPerc = g.IGSTPerc
                            SGSTAmount = g.SGSTAmount
                            if SGSTAmount == 0:
                                SGSTPerc = 0
                            CGSTAmount = g.CGSTAmount
                            if CGSTAmount == 0:
                                CGSTPerc = 0
                            IGSTAmount = g.IGSTAmount
                            if IGSTAmount == 0:
                                IGSTPerc = 0
                            Total = g.NetAmount

                            total_Qty += float(Qty)
                            total_amount += float(Amount)
                            total_SGSTAmount += float(SGSTAmount)
                            total_CGSTAmount += float(CGSTAmount)
                            total_IGSTAmount += float(IGSTAmount)
                            total_sum_Total += float(Total)

                            data = {
                                "Date" : Date,
                                "InvoiceDate" : Date,
                                "InvoiceNo" : InvoiceNo,
                                "party" : party,
                                "GSTN" : GSTN,
                                "City" : City,
                                "State" : state_name,
                                "State_Code" : State_Code,
                                "item_name" : item_name,
                                "HSN" : HSN,
                                "Qty" : Qty,
                                "UnitName" : UnitName,
                                "Amount" : Amount,
                                "SGSTPerc" : SGSTPerc,
                                "CGSTPerc" : CGSTPerc,
                                "IGSTPerc" : IGSTPerc,
                                "SGSTAmount" : SGSTAmount,
                                "CGSTAmount" : CGSTAmount,
                                "IGSTAmount" : IGSTAmount,                            
                                "Total" : '%.2f' % round(Total, 2),
                            }

                            is_ok = True
                            final_data[count]['data'].append(data)

                        final_data[count]['total_Qty'] = total_Qty
                        final_data[count]['total_amount'] = total_amount
                        final_data[count]['total_SGSTAmount'] = total_SGSTAmount
                        final_data[count]['total_CGSTAmount'] = total_CGSTAmount
                        final_data[count]['total_IGSTAmount'] = total_IGSTAmount
                        final_data[count]['total_sum_Total'] = total_sum_Total

                        count += 1


        if is_ok == True:
            response_data = {
                "StatusCode": 6000,
                "final_data" : final_data,
               
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


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def purchase_taxgroup_report_excel(request):
    # content-type of response
    CompanyID = request.GET.get("CompanyID")
    BranchID = request.GET.get("BranchID")
    FromDate = request.GET.get("FromDate")
    ToDate = request.GET.get("ToDate")
    PriceRounding = request.GET.get("PriceRounding")
    
    print('CompanyID,BranchID,FromDate,ToDate')
    response = HttpResponse(content_type='application/ms-excel')

    #decide file name
    response['Content-Disposition'] = 'attachment; filename="Purchase TaxGroup List.xls"'

    #creating workbook
    wb = xlwt.Workbook(encoding='utf-8')
    data = purchase_taxgroup_excel_data(CompanyID,BranchID,FromDate,ToDate,PriceRounding)

    # ===============  adding B2B Suppliers sheet ============
    header_style = xlwt.easyxf('pattern: pattern solid, fore_colour light_blue;'
                              'font: colour white, bold True;')

    export_to_excel_purchase_taxgroup(wb,data,FromDate,ToDate)
 
  
    wb.save(response)
    return response


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def purchase_gst_report_excel(request):
    # content-type of response
    CompanyID = request.GET.get("CompanyID")
    BranchID = request.GET.get("BranchID")
    FromDate = request.GET.get("FromDate")
    ToDate = request.GET.get("ToDate")
    UserID = request.GET.get("UserID")
    PriceRounding = request.GET.get("PriceRounding")
    
    print('CompanyID,BranchID,FromDate,ToDate')
    response = HttpResponse(content_type='application/ms-excel')

    #decide file name
    response['Content-Disposition'] = 'attachment; filename="Purchase GST Report.xls"'

    #creating workbook
    wb = xlwt.Workbook(encoding='utf-8')
    data = purchase_gst_excel_data(CompanyID,BranchID,FromDate,ToDate,PriceRounding,UserID)

    # ===============  adding B2B Suppliers sheet ============
    header_style = xlwt.easyxf('pattern: pattern solid, fore_colour light_blue;'
                              'font: colour white, bold True;')

    export_to_excel_purchase_gst(wb,data,FromDate,ToDate)
 
  
    wb.save(response)
    return response



