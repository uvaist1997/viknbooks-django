from brands.models import SalesMaster, SalesMaster_Log, SalesDetails, SalesDetails_Log, StockPosting, LedgerPosting,\
    StockPosting_Log, LedgerPosting_Log, Parties, SalesDetailsDummy, StockRate, StockTrans, PriceList, DamageStockMaster, JournalMaster,\
    OpeningStockMaster, PaymentMaster, PurchaseMaster, PurchaseOrderMaster, PurchaseReturnMaster, ReceiptMaster, SalesOrderMaster,\
    SalesReturnMaster, StockReceiptMaster_ID, DamageStockMaster, StockTransferMaster_ID, AccountGroup, SalesReturnDetails,\
    AccountLedger, PurchaseDetails, PurchaseReturnDetails, Product, UserTable, ProductGroup, ExcessStockMaster, ShortageStockMaster, DamageStockMaster,\
    UsedStockMaster, GeneralSettings, CompanySettings
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v1.sales.serializers import SalesMasterSerializer, SalesMasterRestSerializer, SalesDetailsSerializer, SalesDetailsRestSerializer,\
    ListSerializerforReport, SalesMasterReportSerializer, SalesMasterForReturnSerializer, StockSerializer, StockRateSerializer, SalesIntegratedSerializer
from api.v1.brands.serializers import ListSerializer
from api.v1.purchases.serializers import PurchaseMasterRestSerializer, PurchasePrintSerializer
from api.v1.salesReturns.serializers import SalesReturnMasterRestSerializer, SalesReturnMasterReportSerializer
from api.v1.purchaseReturns.serializers import PurchaseReturnMasterRestSerializer, PurchaseReturnPrintSerializer
from api.v1.sales.functions import generate_serializer_errors
from rest_framework import status
from api.v1.sales.functions import get_auto_id, get_auto_idMaster, get_auto_stockPostid
from api.v1.accountLedgers.functions import get_auto_LedgerPostid
from api.v1.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
import datetime
from datetime import date, timedelta
import re
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from api.v1.ledgerPosting.functions import convertOrderdDict
from main.functions import get_company, activity_log
from api.v1.stockPostings.serializers import StockPostingSerializer, StockPostingRestSerializer, ExcessStockMasterSerializer, ShortageStockMasterSerializer, DamageStockMasterSerializer, UsedStockMasterSerializer, UsedStockDetailSerializer
from api.v1.companySettings.serializers import CompanySettingsRestSerializer

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
def create_sale(request):
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
    GrandTotal = float(data['GrandTotal'])
    RoundOff = float(data['RoundOff'])
    AddlDiscPercent = float(data['AddlDiscPercent'])

    VATAmount = float(data['VATAmount'])
    SGSTAmount = float(data['SGSTAmount'])
    CGSTAmount = float(data['CGSTAmount'])
    IGSTAmount = float(data['IGSTAmount'])
    TAX1Amount = float(data['TAX1Amount'])
    TAX2Amount = float(data['TAX2Amount'])
    TAX3Amount = float(data['TAX3Amount'])
    BillDiscPercent = float(data['BillDiscPercent'])
    BankAmount = float(data['BankAmount'])
    BillDiscAmt = float(data['BillDiscAmt'])
    Balance = float(data['Balance'])
    OldLedgerBalance = float(data['OldLedgerBalance'])

    TotalGrossAmt = round(TotalGrossAmt, PriceRounding)
    TotalTax = round(TotalTax, PriceRounding)
    NetTotal = round(NetTotal, PriceRounding)
    AddlDiscPercent = round(AddlDiscPercent, PriceRounding)
    AddlDiscAmt = round(AddlDiscAmt, PriceRounding)
    AdditionalCost = round(AdditionalCost, PriceRounding)
    TotalDiscount = round(TotalDiscount, PriceRounding)
    GrandTotal = round(GrandTotal, PriceRounding)
    RoundOff = round(RoundOff, PriceRounding)

    VATAmount = round(VATAmount, PriceRounding)
    SGSTAmount = round(SGSTAmount, PriceRounding)
    CGSTAmount = round(CGSTAmount, PriceRounding)
    IGSTAmount = round(IGSTAmount, PriceRounding)
    TAX1Amount = round(TAX1Amount, PriceRounding)
    TAX2Amount = round(TAX2Amount, PriceRounding)
    TAX3Amount = round(TAX3Amount, PriceRounding)
    BillDiscPercent = round(BillDiscPercent, PriceRounding)
    BankAmount = round(BankAmount, PriceRounding)
    BillDiscAmt = round(BillDiscAmt, PriceRounding)
    Balance = round(Balance, PriceRounding)
    OldLedgerBalance = round(OldLedgerBalance, PriceRounding)

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

    AllowCashReceiptMoreSaleAmt = data['AllowCashReceiptMoreSaleAmt']

    Action = "A"

    # checking voucher number already exist
    VoucherNoLow = VoucherNo.lower()
    is_voucherExist = False
    insts = SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID)
    if insts:
        for i in insts:
            voucher_no = i.VoucherNo
            voucherNo = voucher_no.lower()
            if VoucherNoLow == voucherNo:
                is_voucherExist = True

    if not is_voucherExist:

        SalesMasterID = get_auto_idMaster(SalesMaster, BranchID, CompanyID)

        if Parties.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID).exists():

            party_instances = Parties.objects.filter(
                CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)

            for party_instance in party_instances:

                party_instance.PartyName = CustomerName

                party_instance.save()

      
        CashAmount = float(GrandTotal) - float(BankAmount)

        sales_instance = SalesMaster.objects.create(
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
            Balance=Balance,
            TransactionTypeID=TransactionTypeID,
            CompanyID=CompanyID,
            OldLedgerBalance=OldLedgerBalance
        )

        SalesMaster_Log.objects.create(
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
            OldLedgerBalance=OldLedgerBalance
        )

        VoucherType = "SI"

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
            Credit=TotalGrossAmt,
            IsActive=IsActive,
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
            Credit=TotalGrossAmt,
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
                    Credit=VATAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )
        elif TaxType == 'GST Intra-state B2B' or TaxType == 'GST Intra-state B2C':
            if float(SGSTAmount) > 0 or float(CGSTAmount) > 0:
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
                    LedgerID=10,
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
                    Credit=SGSTAmount,
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
                    Credit=IGSTAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )
        if not TaxType == 'Export':
            if float(TAX1Amount) > 0:
                LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)
                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=16,
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
                    LedgerID=16,
                    Credit=TAX1Amount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                    )
            if float(TAX2Amount) > 0:
                LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)
                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=19,
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
                    LedgerID=19,
                    Credit=TAX2Amount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                    )
            if float(TAX3Amount) > 0:
                LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)
                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=22,
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
                    LedgerID=22,
                    Credit=TAX3Amount,
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
                Debit=TotalDiscount,
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
                Credit=RoundOff,
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
                Debit=RoundOff,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

        account_group = AccountLedger.objects.get(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).AccountGroupUnder

        if UserTable.objects.filter(CompanyID=CompanyID, customer__user__pk=CreatedUserID).exists():
            DefaultAccountForUser = UserTable.objects.get(
                CompanyID=CompanyID, customer__user__pk=CreatedUserID).DefaultAccountForUser
            Cash_Account = UserTable.objects.get(
                CompanyID=CompanyID, customer__user__pk=CreatedUserID).Cash_Account
            Bank_Account = UserTable.objects.get(
                CompanyID=CompanyID, customer__user__pk=CreatedUserID).Bank_Account

            if DefaultAccountForUser:
                if account_group == 9 and float(CashReceived) > 0 and float(BankAmount) > 0:
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
                        LedgerID=LedgerID,
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
                        LedgerID=Bank_Account,
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
                        LedgerID=Bank_Account,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                elif account_group == 9 and float(CashReceived) == 0 and float(BankAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Bank_Account,
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
                        LedgerID=Bank_Account,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                elif account_group == 9 and float(CashReceived) > 0 and float(BankAmount) == 0:
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
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )
                elif account_group == 9 and float(CashReceived) == 0 and float(BankAmount) == 0:
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
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )
                elif account_group == 8 and float(CashReceived) > 0 and float(BankAmount) > 0:
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
                        LedgerID=LedgerID,
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
                        LedgerID=Cash_Account,
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
                        LedgerID=Cash_Account,
                        Debit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                elif account_group == 8 and float(CashReceived) == 0 and float(BankAmount) > 0:
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
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                elif account_group == 8 and float(CashReceived) > 0 and float(BankAmount) == 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Cash_Account,
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
                        LedgerID=Cash_Account,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                elif account_group == 8 and float(CashReceived) == 0 and float(BankAmount) == 0:

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
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )



                elif (account_group == 10 or account_group == 29) and float(CashReceived) > 0 and float(BankAmount) > 0 and float(Balance) <= 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Bank_Account,
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
                        LedgerID=Bank_Account,
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
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    

                    if AllowCashReceiptMoreSaleAmt == True or AllowCashReceiptMoreSaleAmt == "true":
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=Cash_Account,
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
                            LedgerID=Cash_Account,
                            Debit=CashReceived,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                        BankCash = float(BankAmount) + float(CashReceived)
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
                            Credit=BankCash,
                            IsActive=IsActive,
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
                            Credit=BankCash,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                    else:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=Cash_Account,
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
                            LedgerID=Cash_Account,
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
                            LedgerID=LedgerID,
                            Credit=GrandTotal,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                elif (account_group == 10 or account_group == 29) and float(CashReceived) == 0 and float(BankAmount) > 0 and float(Balance) <= 0:
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
                        LedgerID=Bank_Account,
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
                        LedgerID=Bank_Account,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    if AllowCashReceiptMoreSaleAmt == True or AllowCashReceiptMoreSaleAmt == "true":
                        BankCash = float(BankAmount) + float(CashReceived)
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
                            Credit=BankCash,
                            IsActive=IsActive,
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
                            Credit=BankCash,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                    else:
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
                            LedgerID=LedgerID,
                            Credit=GrandTotal,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                elif (account_group == 10 or account_group == 29) and float(CashReceived) > 0 and float(BankAmount) == 0 and float(Balance) <= 0:
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
                        LedgerID=Cash_Account,
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
                        LedgerID=Cash_Account,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    if AllowCashReceiptMoreSaleAmt == True or AllowCashReceiptMoreSaleAmt == "true":
                        BankCash = float(BankAmount) + float(CashReceived)
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
                            Credit=BankCash,
                            IsActive=IsActive,
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
                            Credit=BankCash,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                    else:
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
                            LedgerID=LedgerID,
                            Credit=GrandTotal,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                elif (account_group == 10 or account_group == 29) and float(CashReceived) == 0 and float(BankAmount) == 0:
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
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                elif (account_group == 10 or account_group == 29) and float(CashReceived) > 0 and float(BankAmount) == 0 and float(Balance) > 0:
                    cash = float(GrandTotal) - float(CashReceived)

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Cash_Account,
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
                        LedgerID=Cash_Account,
                        Debit=CashReceived,
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
                        Debit=cash,
                        IsActive=IsActive,
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
                        Debit=cash,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                elif (account_group == 10 or account_group == 29) and float(CashReceived) == 0 and float(BankAmount) > 0 and float(Balance) > 0:
                    bank = float(GrandTotal) - float(BankAmount)
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Bank_Account,
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
                        LedgerID=Bank_Account,
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
                        Debit=bank,
                        IsActive=IsActive,
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
                        Debit=bank,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )
            else:
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
                    Debit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

        salesdetails = data["SalesDetails"]

        for salesdetail in salesdetails:

            ProductID = salesdetail['ProductID']
            Qty = salesdetail['Qty']
            FreeQty = salesdetail['FreeQty']
            Flavour = salesdetail['Flavour']
            PriceListID = salesdetail['PriceListID']

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

            UnitPrice = round(UnitPrice, PriceRounding)
            InclusivePrice = round(InclusivePrice, PriceRounding)
            RateWithTax = round(RateWithTax, PriceRounding)
            CostPerPrice = round(CostPerPrice, PriceRounding)
            AddlDiscPerc = round(AddlDiscPerc, PriceRounding)

            AddlDiscAmt = round(AddlDiscAmt, PriceRounding)
            DiscountPerc = round(DiscountPerc, PriceRounding)
            DiscountAmount = round(DiscountAmount, PriceRounding)
            GrossAmount = round(GrossAmount, PriceRounding)
            TaxableAmount = round(TaxableAmount, PriceRounding)

            VATPerc = round(VATPerc, PriceRounding)
            VATAmount = round(VATAmount, PriceRounding)
            SGSTPerc = round(SGSTPerc, PriceRounding)
            SGSTAmount = round(SGSTAmount, PriceRounding)
            CGSTPerc = round(CGSTPerc, PriceRounding)

            CGSTAmount = round(CGSTAmount, PriceRounding)
            IGSTPerc = round(IGSTPerc, PriceRounding)
            IGSTAmount = round(IGSTAmount, PriceRounding)
            NetAmount = round(NetAmount, PriceRounding)
            TAX1Perc = round(TAX1Perc, PriceRounding)

            TAX1Amount = round(TAX1Amount, PriceRounding)
            TAX2Perc = round(TAX2Perc, PriceRounding)
            TAX2Amount = round(TAX2Amount, PriceRounding)
            TAX3Perc = round(TAX3Perc, PriceRounding)
            TAX3Amount = round(TAX3Amount, PriceRounding)

            SalesDetailsID = get_auto_id(SalesDetails, BranchID, CompanyID)

            CostPerPrice = PriceList.objects.get(CompanyID=CompanyID,PriceListID=PriceListID,BranchID=BranchID,ProductID=ProductID).PurchasePrice

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
                CompanyID=CompanyID,
            )

            SalesDetails_Log.objects.create(
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
                CompanyID=CompanyID,
            )

            if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="SalesPriceUpdate").exists():
                check_SalesPriceUpdate = GeneralSettings.objects.get(
                    CompanyID=CompanyID, SettingsType="SalesPriceUpdate").SettingsValue
                if check_SalesPriceUpdate == "True":
                    pri_ins = PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID)
                    pri_ins.SalesPrice = UnitPrice
                    pri_ins.save()

            # priceList = PriceList.objects.get(CompanyID=CompanyID,PriceListID=PriceListID,BranchID=BranchID)

            MultiFactor = PriceList.objects.get(
                CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor
            PriceListID_DefUnit = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

            # PriceListID_DefUnit = priceList.PriceListID
            # MultiFactor = priceList.MultiFactor

            # PurchasePrice = priceList.PurchasePrice
            # SalesPrice = priceList.SalesPrice

            qty = float(FreeQty) + float(Qty)

            Qty = float(MultiFactor) * float(qty)
            Cost = float(CostPerPrice) / float(MultiFactor)

            Qy = round(Qty, 4)
            Qty = str(Qy)

            Ct = round(Cost, 4)
            Cost = str(Ct)

            princeList_instance = PriceList.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit, BranchID=BranchID)
            PurchasePrice = princeList_instance.PurchasePrice
            SalesPrice = princeList_instance.SalesPrice

            changQty = Qty
            if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID, Qty__gt=0, PriceListID=PriceListID_DefUnit).exists():
                stockRate_instances = StockRate.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, WareHouseID=WarehouseID, Qty__gt=0, PriceListID=PriceListID_DefUnit)
                count = stockRate_instances.count()
                last = 0
                for stockRate_instance in stockRate_instances:
                    last = float(last) + float(1)
                    StockRateID = stockRate_instance.StockRateID
                    stock_post_cost = stockRate_instance.Cost
                    if float(stockRate_instance.Qty) > float(Qty):
                        stockRate_instance.Qty = float(
                            stockRate_instance.Qty) - float(Qty)
                        changQty = 0
                        stockRate_instance.save()

                        if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                       VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit).exists():
                            stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                          VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit)
                            QtyOut = stockPost_instance.QtyOut
                            newQty = float(QtyOut) + float(Qty)

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
                                QtyOut=Qty,
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
                                QtyOut=Qty,
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
                                stockTra_in.Qty) + float(Qty)
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
                                Qty=Qty,
                                IsActive=IsActive,
                                CompanyID=CompanyID,
                            )
                    elif float(stockRate_instance.Qty) < float(Qty):

                        if float(changQty) > float(stockRate_instance.Qty):
                            changQty = float(changQty) - \
                                float(stockRate_instance.Qty)
                            stckQty = stockRate_instance.Qty
                            stockRate_instance.Qty = 0
                            stockRate_instance.save()

                            if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                           VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit).exists():
                                stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                              VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit)
                                QtyOut = stockPost_instance.QtyOut
                                newQty = float(QtyOut) + \
                                    float(stockRate_instance.Qty)
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
                                    stockTra_in.Qty) + float(stockRate_instance.Qty)
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
                                    Qty=stockRate_instance.Qty,
                                    IsActive=IsActive,
                                    CompanyID=CompanyID,
                                )
                        else:
                            if changQty < 0:
                                changQty = 0
                            chqty = changQty
                            changQty = float(
                                stockRate_instance.Qty) - float(changQty)
                            stockRate_instance.Qty = changQty
                            changQty = 0
                            stockRate_instance.save()

                            if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                           VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit).exists():
                                stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                              VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit)
                                QtyOut = stockPost_instance.QtyOut
                                newQty = float(QtyOut) + float(chqty)
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

                    elif float(stockRate_instance.Qty) == float(Qty):
                        stockRate_instance.Qty = 0
                        changQty = 0
                        stockRate_instance.save()

                        if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                       VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit).exists():
                            stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                          VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit)
                            QtyOut = stockPost_instance.QtyOut
                            newQty = float(QtyOut) + \
                                float(Qty)
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
                                QtyOut=Qty,
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
                                QtyOut=Qty,
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
                                stockTra_in.Qty) + float(Qty)
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
                                Qty=Qty,
                                IsActive=IsActive,
                                CompanyID=CompanyID,
                            )

            if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, Cost=Cost, WareHouseID=WarehouseID, Qty__lte=0, PriceListID=PriceListID_DefUnit).exists():
                stockRate_instance = StockRate.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, Cost=Cost, WareHouseID=WarehouseID, Qty__lte=0, PriceListID=PriceListID_DefUnit).first()
                stock_post_cost = stockRate_instance.Cost
                if float(changQty) > 0:
                    stockRate_instance.Qty = float(
                        stockRate_instance.Qty) - float(changQty)
                    stockRate_instance.save()

                    if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                   VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit).exists():
                        stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                      VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit)
                        QtyOut = stockPost_instance.QtyOut
                        newQty = float(QtyOut) + float(changQty)
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
                if float(changQty) > 0:
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
                        Qty=Qty,
                        IsActive=IsActive,
                        CompanyID=CompanyID,
                    )

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sales Invoice',
                     'Create', 'Sales Invoice created successfully.', 'Sales Invoice saved successfully.')

        response_data = {
            "StatusCode": 6000,
            "id": sales_instance.id,
            "message": "Sales created Successfully!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Sales Invoice',
                     'Create', 'Sales Invoice created Failed.', 'VoucherNo already exist')

        response_data = {
            "StatusCode": 6001,
            "message": "VoucherNo already exist!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_sales(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']

    today = datetime.datetime.now()
    salesMaster_instance = None
    ledgerPostInstances = None
    salesDetails = None

    salesMaster_instance = SalesMaster.objects.get(CompanyID=CompanyID, pk=pk)

    SalesMasterID = salesMaster_instance.SalesMasterID
    VoucherNo = salesMaster_instance.VoucherNo
    BranchID = salesMaster_instance.BranchID
    OldLedgerBalance = salesMaster_instance.OldLedgerBalance

    Action = "M"

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
    Balance = float(data['Balance'])

    AllowCashReceiptMoreSaleAmt = data['AllowCashReceiptMoreSaleAmt']

    TotalGrossAmt = round(TotalGrossAmt, PriceRounding)
    AddlDiscPercent = round(AddlDiscPercent, PriceRounding)
    AddlDiscAmt = round(AddlDiscAmt, PriceRounding)
    TotalDiscount = round(TotalDiscount, PriceRounding)
    TotalTax = round(TotalTax, PriceRounding)
    NetTotal = round(NetTotal, PriceRounding)

    AdditionalCost = round(AdditionalCost, PriceRounding)
    GrandTotal = round(GrandTotal, PriceRounding)
    RoundOff = round(RoundOff, PriceRounding)
    CashReceived = round(CashReceived, PriceRounding)
    BankAmount = round(BankAmount, PriceRounding)

    BillDiscPercent = round(BillDiscPercent, PriceRounding)
    BillDiscAmt = round(BillDiscAmt, PriceRounding)
    VATAmount = round(VATAmount, PriceRounding)
    SGSTAmount = round(SGSTAmount, PriceRounding)
    CGSTAmount = round(CGSTAmount, PriceRounding)

    IGSTAmount = round(IGSTAmount, PriceRounding)
    TAX1Amount = round(TAX1Amount, PriceRounding)
    TAX2Amount = round(TAX2Amount, PriceRounding)
    TAX3Amount = round(TAX3Amount, PriceRounding)
    Balance = round(Balance, PriceRounding)

    TransactionTypeID = data['TransactionTypeID']

    
    CashAmount = float(GrandTotal) - float(BankAmount)

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
    salesMaster_instance.Balance = Balance
    salesMaster_instance.TransactionTypeID = TransactionTypeID
    salesMaster_instance.save()

    SalesMaster_Log.objects.create(
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
        OldLedgerBalance=OldLedgerBalance
    )

    VoucherType = "SI"

    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting, BranchID, CompanyID)

    LedgerPosting.objects.create(
        LedgerPostingID=LedgerPostingID,
        BranchID=BranchID,
        Date=Date,
        VoucherMasterID=SalesMasterID,
        VoucherType=VoucherType,
        VoucherNo=VoucherNo,
        LedgerID=SalesAccount,
        Credit=TotalGrossAmt,
        IsActive=IsActive,
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
        Credit=TotalGrossAmt,
        IsActive=IsActive,
        Action=Action,
        CreatedUserID=CreatedUserID,
        CreatedDate=today,
        UpdatedDate=today,
        CompanyID=CompanyID,
    )

    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting, BranchID, CompanyID)

    LedgerPosting.objects.create(
        LedgerPostingID=LedgerPostingID,
        BranchID=BranchID,
        Date=Date,
        VoucherMasterID=SalesMasterID,
        VoucherType=VoucherType,
        VoucherNo=VoucherNo,
        LedgerID=LedgerID,
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
        Debit=GrandTotal,
        IsActive=IsActive,
        Action=Action,
        CreatedUserID=CreatedUserID,
        CreatedDate=today,
        UpdatedDate=today,
        CompanyID=CompanyID,
    )

    if float(TotalTax) > 0:

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
            Credit=TotalTax,
            IsActive=IsActive,
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
            Credit=TotalTax,
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
            Debit=TotalDiscount,
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
            Credit=RoundOff,
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
            Debit=RoundOff,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            CompanyID=CompanyID,
        )

        account_group = AccountLedger.objects.get(
            CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).AccountGroupUnder

        if UserTable.objects.filter(CompanyID=CompanyID, customer__user__pk=CreatedUserID).exists():
            DefaultAccountForUser = UserTable.objects.get(
                CompanyID=CompanyID, customer__user__pk=CreatedUserID).DefaultAccountForUser
            Cash_Account = UserTable.objects.get(
                CompanyID=CompanyID, customer__user__pk=CreatedUserID).Cash_Account
            Bank_Account = UserTable.objects.get(
                CompanyID=CompanyID, customer__user__pk=CreatedUserID).Bank_Account

            if DefaultAccountForUser:
                if account_group == 9 and float(CashReceived) > 0 and float(BankAmount) > 0:
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
                        LedgerID=LedgerID,
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
                        LedgerID=Bank_Account,
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
                        LedgerID=Bank_Account,
                        Debit=BankAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                elif account_group == 9 and float(CashReceived) == 0 and float(BankAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Bank_Account,
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
                        LedgerID=Bank_Account,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                elif account_group == 9 and float(CashReceived) > 0 and float(BankAmount) == 0:
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
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                elif account_group == 9 and float(CashReceived) == 0 and float(BankAmount) == 0:
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
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )
                elif account_group == 8 and float(CashReceived) > 0 and float(BankAmount) > 0:
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
                        LedgerID=LedgerID,
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
                        LedgerID=Cash_Account,
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
                        LedgerID=Cash_Account,
                        Debit=CashAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                elif account_group == 8 and float(CashReceived) == 0 and float(BankAmount) > 0:
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
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                elif account_group == 8 and float(CashReceived) > 0 and float(BankAmount) == 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Cash_Account,
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
                        LedgerID=Cash_Account,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                elif account_group == 8 and float(CashReceived) == 0 and float(BankAmount) == 0:

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
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )



                elif (account_group == 10 or account_group == 29) and float(CashReceived) > 0 and float(BankAmount) > 0 and float(Balance) <= 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Bank_Account,
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
                        LedgerID=Bank_Account,
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
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    

                    if AllowCashReceiptMoreSaleAmt == True or AllowCashReceiptMoreSaleAmt == "true":
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=Cash_Account,
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
                            LedgerID=Cash_Account,
                            Debit=CashReceived,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                        BankCash = float(BankAmount) + float(CashReceived)
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
                            Credit=BankCash,
                            IsActive=IsActive,
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
                            Credit=BankCash,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                    else:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=SalesMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=Cash_Account,
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
                            LedgerID=Cash_Account,
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
                            LedgerID=LedgerID,
                            Credit=GrandTotal,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                elif (account_group == 10 or account_group == 29) and float(CashReceived) == 0 and float(BankAmount) > 0 and float(Balance) <= 0:
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
                        LedgerID=Bank_Account,
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
                        LedgerID=Bank_Account,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    if AllowCashReceiptMoreSaleAmt == True or AllowCashReceiptMoreSaleAmt == "true":
                        BankCash = float(BankAmount) + float(CashReceived)
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
                            Credit=BankCash,
                            IsActive=IsActive,
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
                            Credit=BankCash,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                    else:
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
                            LedgerID=LedgerID,
                            Credit=GrandTotal,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                elif (account_group == 10 or account_group == 29) and float(CashReceived) > 0 and float(BankAmount) == 0 and float(Balance) <= 0:
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
                        LedgerID=Cash_Account,
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
                        LedgerID=Cash_Account,
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    if AllowCashReceiptMoreSaleAmt == True or AllowCashReceiptMoreSaleAmt == "true":
                        BankCash = float(BankAmount) + float(CashReceived)
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
                            Credit=BankCash,
                            IsActive=IsActive,
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
                            Credit=BankCash,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                    else:
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
                            LedgerID=LedgerID,
                            Credit=GrandTotal,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                elif (account_group == 10 or account_group == 29) and float(CashReceived) == 0 and float(BankAmount) == 0:
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
                        Debit=GrandTotal,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                elif (account_group == 10 or account_group == 29) and float(CashReceived) > 0 and float(BankAmount) == 0 and float(Balance) > 0:
                    cash = float(GrandTotal) - float(CashReceived)

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Cash_Account,
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
                        LedgerID=Cash_Account,
                        Debit=CashReceived,
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
                        Debit=cash,
                        IsActive=IsActive,
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
                        Debit=cash,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                elif (account_group == 10 or account_group == 29) and float(CashReceived) == 0 and float(BankAmount) > 0 and float(Balance) > 0:
                    bank = float(GrandTotal) - float(BankAmount)
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=SalesMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Bank_Account,
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
                        LedgerID=Bank_Account,
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
                        Debit=bank,
                        IsActive=IsActive,
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
                        Debit=bank,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )
            else:
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
                    Debit=GrandTotal,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

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
        pk = salesdetail['unq_id']
        detailID = salesdetail['detailID']
        ProductID = salesdetail['ProductID']
        Qty_detail = salesdetail['Qty']
        FreeQty = salesdetail['FreeQty']
        PriceListID = salesdetail['PriceListID']
        Flavour = salesdetail['Flavour']

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

        UnitPrice = round(UnitPrice, PriceRounding)
        InclusivePrice = round(InclusivePrice, PriceRounding)
        RateWithTax = round(RateWithTax, PriceRounding)
        CostPerPrice = round(CostPerPrice, PriceRounding)
        AddlDiscPerc = round(AddlDiscPerc, PriceRounding)

        AddlDiscAmt = round(AddlDiscAmt, PriceRounding)
        DiscountPerc = round(DiscountPerc, PriceRounding)
        DiscountAmount = round(DiscountAmount, PriceRounding)
        GrossAmount = round(GrossAmount, PriceRounding)
        TaxableAmount = round(TaxableAmount, PriceRounding)

        VATPerc = round(VATPerc, PriceRounding)
        VATAmount = round(VATAmount, PriceRounding)
        SGSTPerc = round(SGSTPerc, PriceRounding)
        SGSTAmount = round(SGSTAmount, PriceRounding)
        CGSTPerc = round(CGSTPerc, PriceRounding)

        CGSTAmount = round(CGSTAmount, PriceRounding)
        IGSTPerc = round(IGSTPerc, PriceRounding)
        IGSTAmount = round(IGSTAmount, PriceRounding)
        NetAmount = round(NetAmount, PriceRounding)
        TAX1Perc = round(TAX1Perc, PriceRounding)

        TAX1Amount = round(TAX1Amount, PriceRounding)
        TAX2Perc = round(TAX2Perc, PriceRounding)
        TAX2Amount = round(TAX2Amount, PriceRounding)
        TAX3Perc = round(TAX3Perc, PriceRounding)
        TAX3Amount = round(TAX3Amount, PriceRounding)

        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID,SettingsType="SalesPriceUpdate").exists():
            check_SalesPriceUpdate = GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="SalesPriceUpdate",BranchID=BranchID).SettingsValue
            if check_SalesPriceUpdate == "True":
                pri_ins = PriceList.objects.get(
                    CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID)
                pri_ins.SalesPrice = UnitPrice
                pri_ins.save()

        CostPerPrice = PriceList.objects.get(CompanyID=CompanyID,PriceListID=PriceListID,BranchID=BranchID,ProductID=ProductID).PurchasePrice

        # priceList = PriceList.objects.get(CompanyID=CompanyID,PriceListID=PriceListID,BranchID=BranchID)

        MultiFactor = PriceList.objects.get(
            CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor
        PriceListID_DefUnit = PriceList.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

        # PriceListID_DefUnit = priceList.PriceListID
        # MultiFactor = priceList.MultiFactor

        # PurchasePrice = priceList.PurchasePrice
        # SalesPrice = priceList.SalesPrice

        qty = float(FreeQty) + float(Qty_detail)

        Qty = float(MultiFactor) * float(qty)
        Cost = float(CostPerPrice) / float(MultiFactor)

        Qy = round(Qty, 4)
        Qty = str(Qy)

        Ct = round(Cost, 4)
        Cost = str(Ct)

        princeList_instance = PriceList.objects.get(
            CompanyID=CompanyID, ProductID=ProductID, PriceListID=PriceListID_DefUnit, BranchID=BranchID)
        PurchasePrice = princeList_instance.PurchasePrice
        SalesPrice = princeList_instance.SalesPrice

        if detailID == 0:

            salesDetail_instance = SalesDetails.objects.get(
                CompanyID=CompanyID, pk=pk)
            SalesDetailsID = salesDetail_instance.SalesDetailsID
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

            salesDetail_instance.save()

            SalesDetails_Log.objects.create(
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

        if detailID == 1:

            Action = "A"

            SalesDetailsID = get_auto_id(SalesDetails, BranchID, CompanyID)

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
                CompanyID=CompanyID,
            )

            SalesDetails_Log.objects.create(
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

            if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID_DefUnit).exists():
                stockRateInstance = StockRate.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, Cost=Cost, ProductID=ProductID, WareHouseID=WarehouseID, PriceListID=PriceListID_DefUnit)
                StockRateID = stockRateInstance.StockRateID
                stockRateInstance.Qty = float(
                    stockRateInstance.Qty) - float(Qty)
                stockRateInstance.save()

                # if StockPosting.objects.filter(WareHouseID=WarehouseID,ProductID=ProductID,BranchID=BranchID,
                #     VoucherMasterID=SalesMasterID,VoucherType=VoucherType,Rate=Cost,PriceListID=PriceListID_DefUnit).exists():
                #     stockPost_instance = StockPosting.objects.get(WareHouseID=WarehouseID,ProductID=ProductID,BranchID=BranchID,
                #         VoucherMasterID=SalesMasterID,VoucherType=VoucherType,Rate=Cost,PriceListID=PriceListID_DefUnit)
                #     QtyOut = stockPost_instance.QtyOut
                #     newQty = float(QtyOut) + float(Qty)
                #     stockPost_instance.save()
                # else:
                #     StockPostingID = get_auto_stockPostid(StockPosting,BranchID,CompanyID)
                #     StockPosting.objects.create(
                #         StockPostingID=StockPostingID,
                #         BranchID=BranchID,
                #         Action=Action,
                #         Date=Date,
                #         VoucherMasterID=SalesMasterID,
                #         VoucherType=VoucherType,
                #         ProductID=ProductID,
                #         BatchID=BatchID,
                #         WareHouseID=WarehouseID,
                #         QtyOut=Qty,
                #         Rate=Cost,
                #         PriceListID=PriceListID_DefUnit,
                #         IsActive=IsActive,
                #         CreatedDate=today,
                #         UpdatedDate=today,
                #         CreatedUserID=CreatedUserID,
                #         CompanyID=CompanyID,
                #         )

                #     StockPosting_Log.objects.create(
                #         TransactionID=StockPostingID,
                #         BranchID=BranchID,
                #         Action=Action,
                #         Date=Date,
                #         VoucherMasterID=SalesMasterID,
                #         VoucherType=VoucherType,
                #         ProductID=ProductID,
                #         BatchID=BatchID,
                #         WareHouseID=WarehouseID,
                #         QtyOut=Qty,
                #         Rate=Cost,
                #         PriceListID=PriceListID_DefUnit,
                #         IsActive=IsActive,
                #         CreatedDate=today,
                #         UpdatedDate=today,
                #         CreatedUserID=CreatedUserID,
                #         CompanyID=CompanyID,
                #         )

                # StockTransID = get_auto_StockTransID(StockTrans,BranchID,CompanyID)
                # StockTrans.objects.create(
                #     StockTransID=StockTransID,
                #     BranchID=BranchID,
                #     VoucherType=VoucherType,
                #     StockRateID=StockRateID,
                #     DetailID=SalesDetailsID,
                #     MasterID=SalesMasterID,
                #     Qty=Qty,
                #     IsActive=IsActive,
                #     CompanyID=CompanyID,
                #     )

                if StockTrans.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, DetailID=SalesDetailsID, MasterID=SalesMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                    stockTra_in = StockTrans.objects.filter(
                        CompanyID=CompanyID, StockRateID=StockRateID, DetailID=SalesDetailsID, MasterID=SalesMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
                    stockTra_in.Qty = float(stockTra_in.Qty) + float(Qty)
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
                        Qty=Qty,
                        IsActive=IsActive,
                        CompanyID=CompanyID,
                    )
            else:
                StockRateID = get_auto_StockRateID(
                    StockRate, BranchID, CompanyID)
                StockRate.objects.create(
                    StockRateID=StockRateID,
                    BranchID=BranchID,
                    BatchID=BatchID,
                    PurchasePrice=PurchasePrice,
                    SalesPrice=SalesPrice,
                    Qty=Qty,
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

                # StockPostingID = get_auto_stockPostid(StockPosting,BranchID,CompanyID)
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
                #     QtyOut=qty,
                #     Rate=Cost,
                #     PriceListID=PriceListID_DefUnit,
                #     IsActive=IsActive,
                #     CreatedDate=today,
                #     UpdatedDate=today,
                #     CreatedUserID=CreatedUserID,
                #     CompanyID=CompanyID,
                #     )

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
                #     QtyOut=qty,
                #     Rate=Cost,
                #     PriceListID=PriceListID_DefUnit,
                #     IsActive=IsActive,
                #     CreatedDate=today,
                #     UpdatedDate=today,
                #     CreatedUserID=CreatedUserID,
                #     CompanyID=CompanyID,
                #     )

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
        else:
            if StockRate.objects.filter(CompanyID=CompanyID, ProductID=ProductID, Cost=Cost, PriceListID=PriceListID_DefUnit, WareHouseID=WarehouseID).exists():
                stockRate_instance = StockRate.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, Cost=Cost, PriceListID=PriceListID_DefUnit, WareHouseID=WarehouseID)
                StockRateID = stockRate_instance.StockRateID
                if StockTrans.objects.filter(CompanyID=CompanyID, DetailID=SalesDetailsID, MasterID=SalesMasterID, BranchID=BranchID,
                                             VoucherType=VoucherType, IsActive=True, StockRateID=StockRateID).exists():
                    stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID, DetailID=SalesDetailsID, MasterID=SalesMasterID, BranchID=BranchID,
                                                                 VoucherType=VoucherType, IsActive=True, StockRateID=StockRateID)

                    if float(stockTrans_instance.Qty) < float(Qty):
                        deff = float(Qty) - float(stockTrans_instance.Qty)
                        stockTrans_instance.Qty = float(
                            stockTrans_instance.Qty) + float(deff)
                        stockTrans_instance.save()

                        stockRate_instance.Qty = float(
                            stockRate_instance.Qty) - float(deff)
                        stockRate_instance.save()

                        if StockPosting.objects.filter(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                       VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit).exists():
                            stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                          VoucherMasterID=SalesMasterID, VoucherType=VoucherType, Rate=Cost, PriceListID=PriceListID_DefUnit)
                            QtyOut = stockPost_instance.QtyOut
                            newQty = float(QtyOut) + float(deff)
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
                                QtyOut=deff,
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
                                QtyOut=deff,
                                Rate=Cost,
                                PriceListID=PriceListID_DefUnit,
                                IsActive=IsActive,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                                CompanyID=CompanyID,
                            )

                    elif float(stockTrans_instance.Qty) > float(Qty):
                        deff = float(stockTrans_instance.Qty) - float(Qty)
                        stockTrans_instance.Qty = float(
                            stockTrans_instance.Qty) - float(deff)
                        stockTrans_instance.save()

                        stockRate_instance.Qty = float(
                            stockRate_instance.Qty) + float(deff)
                        stockRate_instance.save()

                        # if StockPosting.objects.filter(WareHouseID=WarehouseID,ProductID=ProductID,BranchID=BranchID,
                        #     VoucherMasterID=SalesMasterID,VoucherType=VoucherType,Rate=Cost,PriceListID=PriceListID_DefUnit).exists():
                        #     stockPost_instance = StockPosting.objects.get(WareHouseID=WarehouseID,ProductID=ProductID,BranchID=BranchID,
                        #         VoucherMasterID=SalesMasterID,VoucherType=VoucherType,Rate=Cost,PriceListID=PriceListID_DefUnit)
                        #     QtyOut = stockPost_instance.QtyOut
                        #     newQty = float(QtyOut) + float(deff)
                        #     stockPost_instance.save()
                        # else:
                        #     StockPostingID = get_auto_stockPostid(StockPosting,BranchID,CompanyID)
                        #     StockPosting.objects.create(
                        #         StockPostingID=StockPostingID,
                        #         BranchID=BranchID,
                        #         Action=Action,
                        #         Date=Date,
                        #         VoucherMasterID=SalesMasterID,
                        #         VoucherType=VoucherType,
                        #         ProductID=ProductID,
                        #         BatchID=BatchID,
                        #         WareHouseID=WarehouseID,
                        #         QtyOut=deff,
                        #         Rate=Cost,
                        #         PriceListID=PriceListID_DefUnit,
                        #         IsActive=IsActive,
                        #         CreatedDate=today,
                        #         UpdatedDate=today,
                        #         CreatedUserID=CreatedUserID,
                        #         CompanyID=CompanyID,
                        #         )

                        #     StockPosting_Log.objects.create(
                        #         TransactionID=StockPostingID,
                        #         BranchID=BranchID,
                        #         Action=Action,
                        #         Date=Date,
                        #         VoucherMasterID=SalesMasterID,
                        #         VoucherType=VoucherType,
                        #         ProductID=ProductID,
                        #         BatchID=BatchID,
                        #         WareHouseID=WarehouseID,
                        #         QtyOut=deff,
                        #         Rate=Cost,
                        #         PriceListID=PriceListID_DefUnit,
                        #         IsActive=IsActive,
                        #         CreatedDate=today,
                        #         UpdatedDate=today,
                        #         CreatedUserID=CreatedUserID,
                        #         CompanyID=CompanyID,
                        #         )

            # if StockTrans.objects.filter(MasterID=SalesMasterID,DetailID=SalesDetailsID,BranchID=BranchID,VoucherType=VoucherType,IsActive=True).exists():
            #     stockTrans_instance = StockTrans.objects.filter(MasterID=SalesMasterID,DetailID=SalesDetailsID,BranchID=BranchID,VoucherType=VoucherType,IsActive=True).first()

            #     stockRateID = stockTrans_instance.StockRateID
            #     stockRate_instance = StockRate.objects.get(StockRateID=stockRateID,BranchID=BranchID,WareHouseID=WarehouseID)

            #     if float(stockTrans_instance.Qty) < float(Qty):
            #         deff = float(Qty) - float(stockTrans_instance.Qty)
            #         stockTrans_instance.Qty = float(stockTrans_instance.Qty) + float(deff)
            #         stockTrans_instance.save()

            #         stockRate_instance.Qty = float(stockRate_instance.Qty) - float(deff)
            #         stockRate_instance.save()

            #     elif float(stockTrans_instance.Qty) > float(Qty):
            #         deff = float(stockTrans_instance.Qty) - float(Qty)
            #         stockTrans_instance.Qty = float(stockTrans_instance.Qty) - float(deff)
            #         stockTrans_instance.save()

            #         stockRate_instance.Qty = float(stockRate_instance.Qty) + float(deff)
            #         stockRate_instance.save()

    #request , company, log_type, user, source, action, message, description
    activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sales Invoice',
                 'Edit', 'Sales Invoice Updated successfully.', 'Sales Invoice Updated successfully.')

    response_data = {
        "StatusCode": 6000,
        "message": "Sales Updated Successfully!!!",
    }

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

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sales Invoice', 'List',
                         'Sales Invoice List Viewed successfully.', 'Sales Invoice List Viewed successfully.')

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Sales Invoice',
                         'List', 'Sales Invoice List Viewed Failed.', 'Sales Invoice not found in this branch')
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
            sale_serializer = SalesMasterRestSerializer(
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

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sales Invoice', 'View',
                     'Sales Invoice Single Viewed successfully.', 'Sales Invoice Single Viewed successfully.')
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
            "message": "Sales Master Not Found!"
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

        Action = "D"

        SalesMaster_Log.objects.create(
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
        )

        instance.delete()

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

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=SalesMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
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
            )

            detail_instance.delete()

            if StockTrans.objects.filter(CompanyID=CompanyID, DetailID=SalesDetailsID, MasterID=SalesMasterID, BranchID=BranchID, VoucherType="SI",IsActive = True).exists():
                stockTrans_instances = StockTrans.objects.filter(
                    CompanyID=CompanyID, DetailID=SalesDetailsID, MasterID=SalesMasterID, BranchID=BranchID, VoucherType="SI",IsActive = True)

                for i in stockTrans_instances:
                    stockRateID = i.StockRateID
                    i.IsActive = False
                    i.save()

                    stockRate_instance = StockRate.objects.get(
                        CompanyID=CompanyID, StockRateID=stockRateID, BranchID=BranchID)
                    stockRate_instance.Qty = float(stockRate_instance.Qty) - float(i.Qty)
                    stockRate_instance.save()

        #request , company, log_type, user, source, action, message, description
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
def sales_report(request):
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

        #request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sales Report', 'Report', 'Sales Report Viewed successfully.', 'Sales Report Viewed successfully.')
        if sales_data:
            response_data = {
                "StatusCode": 6000,
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

        if not UserID == 0:
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
            print(f)
            TotalCashSales += float(f['CashSales'])
            TotalCreditSales += float(f['CreditSales'])
            TotalBankSales += float(f['BankSales'])
            TotalNetSales += float(f['NetSales'])
            TotalCashSalesReturn += float(f['CashSalesReturn'])
            TotalDebitSalesRetrn += float(f['DebitSalesRetrn'])
            TotalBankSalesReturn += float(f['BankSalesReturn'])
            TotalNetSalesReturn += float(f['NetSalesReturn'])
            TotalActualSales += float(f['ActualSales'])

        #request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Sales Integrated Report', 'Report',
        #              'Sales Integrated Report Viewed successfully.', 'Sales Integrated Report Viewed successfully.')
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
        if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instance = SalesMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "SI" + str(new_num)

            response_data = {
                "StatusCode": 6000,
                "VoucherNo": new_VoucherNo
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode": 6000,
                "VoucherNo": "SI1"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    elif VoucherType == "PI":
        if PurchaseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instance = PurchaseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "PI" + str(new_num)

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
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "SO" + str(new_num)

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

    elif VoucherType == "PO":
        if PurchaseOrderMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instance = PurchaseOrderMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "PO" + str(new_num)

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
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "SR" + str(new_num)

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
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "PR" + str(new_num)

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
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "OS" + str(new_num)

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
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "JL" + str(new_num)

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
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "CP" + str(new_num)
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
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "BP" + str(new_num)

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
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "CR" + str(new_num)

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
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "BR" + str(new_num)

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
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "ST" + str(new_num)

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
            res = re.search(r"\d+(\.\d+)?", OldGroupCode)
            num = res.group(0)
            new_num = int(num) + 1
            new_GroupCode = "GP" + str(new_num)

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
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "ES" + str(new_num)

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
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "SS" + str(new_num)

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
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "DS" + str(new_num)

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
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "US" + str(new_num)

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
    elif VoucherType == "PC":
        ProductCode = "PC1000"

        if Product.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():

            latest_ProductCode =  Product.objects.filter(CompanyID=CompanyID,BranchID=BranchID).order_by("ProductID").last()

            ProductCode = latest_ProductCode.ProductCode

            temp = re.compile("([a-zA-Z]+)([0-9]+)") 
            res = temp.match(ProductCode).groups()

            code , number = res

            number = int(number) + 1

            ProductCode = str(code) + str(number)

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
    from api.v1.sales.serializers import SalesPrintSerializer
    from api.v1.salesReturns.serializers import SalesReturnMasterPrintSerializer
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']

    VoucherType = data['VoucherType']
    unq_id = data['id']
    company_instance = CompanySettings.objects.get(pk=CompanyID.id)
    company_serialized = CompanySettingsRestSerializer(company_instance, context={"request": request})
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

        #request , company, log_type, user, source, action, message, description
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
    serialized1 = ListSerializerforReport(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']

        stockDatas = []
        stockPosting_instances = None

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

            # final_instances = StockPosting.objects.filter(pk__in=[x.pk for x in stockDatas])

            product_instances = Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID__in=final_pro_arry)
            stockSerializer = StockSerializer(product_instances, many=True, context={
                                              "CompanyID": CompanyID, "PriceRounding": PriceRounding})

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
                            total_stock = float(CurrentBaseStock) / float(MultiFactor)

                    if ProductID == ProductID_inArr:
                        i['CurrentStock'] = total_stock
                        i['CurrentBaseStock'] = CurrentBaseStock

            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Stock Report', 'Report', 'Stock Report Viewed successfully.', 'Stock Report Viewed successfully.')
            if jsnDatas:
                response_data = {
                    "StatusCode": 6000,
                    "data": jsnDatas,
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "No data!"
                }

                return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
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
def stockValue_report(request):
    today = date.today()
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    ProductID = data['ProductID']
    WareHouseID = data['WareHouseID']
    BranchID = data['BranchID']

    if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, WareHouseID=WareHouseID).exists():
        stock_instances = StockPosting.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, WareHouseID=WareHouseID)

        if ProductID > 0:
            stock_instances = stock_instances.filter(ProductID=ProductID)

        product_arry = []
        product_ids = stock_instances.values_list('ProductID')

        for product_id in product_ids:
            if product_id[0] not in product_arry:
                product_arry.append(product_id[0])

        product_instances = Product.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_arry)

        stockSerializer = StockSerializer(product_instances, many=True, context={
                                          "CompanyID": CompanyID, "PriceRounding": PriceRounding, "WareHouseID" : WareHouseID})


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
                    "id" : i['id'],
                    "Cost" : cost,
                    "Date" : today,
                    "ProductName" : i['ProductName'],
                    "PurchasePrice" : i['PurchasePrice'],
                    "Qty" : qty,
                    "SalesPrice" : i['SalesPrice'],
                    "TotalCost" : TotalCost,
                    "UnitName" : i['UnitName'],
                    "WareHouseID" : WareHouseID,
                    "WareHouseName" : i['WareHouseName'],
                }
                count = count + 1
                final_array.append(items)
                TotalQty += float(i['Qty'])
                GrandTotalCost += TotalCost

        #request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Stock Value Report', 'Report', 'Stock Value Report Viewed successfully.', 'Stock Value Report Viewed successfully.')

        response_data = {
            "StatusCode": 6000,
            "data": final_array,
            "TotalQty": TotalQty,
            "GrandTotalCost": GrandTotalCost,
        }
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Stock Value Report', 'Report', 'Stock Value Report Viewed Failed.', 'No data Under This Warehouse.')
        response_data = {
            "StatusCode": 6001,
            "message": "No data Under This Warehouse!!!"
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
        userVal = UserID
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
                    #request , company, log_type, user, source, action, message, description
                    activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'sales Register Report',
                                 'Report', 'sales Register Report Viewed Failed.', 'Sales is not Found in this Warehouse')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Sales is not Found in this Warehouse!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
            if userVal > 0:
                UserID = UserTable.objects.filter(pk=userVal).customer.user.id
                if saleMaster_instances.filter(CreatedUserID=userVal).exists():
                    saleMaster_instances = saleMaster_instances.filter(
                        CreatedUserID=userVal)
                else:
                    #request , company, log_type, user, source, action, message, description
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
                    #request , company, log_type, user, source, action, message, description
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
                    #request , company, log_type, user, source, action, message, description
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
                        for group_i in group_instances:
                            ProductGroupID = group_i.ProductGroupID
                            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=ProductGroupID).exists():
                                product_instances = Product.objects.filter(
                                    CompanyID=CompanyID, BranchID=BranchID, ProductGroupID=ProductGroupID)
                                pro_ids = []
                                for product_i in product_instances:
                                    ProductID = product_i.ProductID
                                    pro_ids.append(ProductID)
                                salesDetail_instances = salesDetail_instances.filter(
                                    ProductID__in=pro_ids)
                    else:
                        #request , company, log_type, user, source, action, message, description
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
                        #request , company, log_type, user, source, action, message, description
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
                        #request , company, log_type, user, source, action, message, description
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
                        #request , company, log_type, user, source, action, message, description
                        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'sales Register Report',
                                     'Report', 'sales Register Report Viewed Failed.', 'Sales is not Found under this Bracode')
                        response_data = {
                            "StatusCode": 6001,
                            "message": "Sales is not Found under this Bracode!"
                        }

                        return Response(response_data, status=status.HTTP_200_OK)

                for s in salesDetail_instances:
                    if s.SalesMasterID == SalesMasterID:
                        if not SalesMasterID in masterList:
                            myDict = {
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
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'sales Register Report',
            #              'Report', 'Sales Register Report Viewed Successfully.', 'sales Register Report Viewed Successfully.')

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
                    #request , company, log_type, user, source, action, message, description
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
                    #request , company, log_type, user, source, action, message, description
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
                    #request , company, log_type, user, source, action, message, description
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
                    #request , company, log_type, user, source, action, message, description
                    # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Bill Wise Report',
                    #              'Report', 'Bill Wise Report Viewed Failed.', 'Sales is not Found in this Warehouse')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Sales is not Found under this Route!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)

            final_array = []
            
            for sm in saleMaster_instances:
                Date = sm.Date
                VoucherNo = sm.VoucherNo
                TotalGrossAmt = sm.TotalGrossAmt
                VATAmount = sm.VATAmount
                NetTotal = sm.NetTotal

                SalesMasterID = sm.SalesMasterID

                # stock_ins = StockPosting.objects.filter(CompanyID=CompanyID,BranchID=BranchID,VoucherMasterID=SalesMasterID,VoucherType="SI",Date__gte=FromDate,Date__lte=ToDate)
                # NetCost = 0
                # for i in stock_ins:
                #     cost = float(i.Rate) * float(i.QtyOut)
                #     NetCost += cost

                salesdetail_ins = SalesDetails.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, SalesMasterID=SalesMasterID)

                print(SalesMasterID)
                print(salesdetail_ins)

                NetCost = 0
                # TotalQty = 0
                for sd in salesdetail_ins:
                    CostPerItem = sd.CostPerPrice
                    Qty_item = sd.Qty
                    NetCost += (float(CostPerItem) * float(Qty_item))
                    
                    # TotalQty += sd.Qty

                # Profit = float(NetTotal) - (float(TotalQty) * float(NetCost))
                Profit = float(NetTotal) -  float(NetCost)

                final_array.append({
                    "Date": Date,
                    "InvoiceNo": VoucherNo,
                    "GrossAmount": TotalGrossAmt,
                    "VATAmount": VATAmount,
                    "NetAmount": NetTotal,
                    "NetCost": NetCost,
                    "Profit": Profit,
                })

            TotalProfit = 0
            TotalCost = 0
            TotalNetAmt = 0
            TotalVatAmt = 0
            TotalGrossAmt = 0

            for f in final_array:
                TotalProfit += f['Profit']
                TotalCost += f['NetCost']
                TotalNetAmt += f['NetAmount']
                TotalVatAmt += f['VATAmount']
                TotalGrossAmt += f['GrossAmount']

            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Bill Wise Report',
            #              'Report', 'Bill Wise Report Viewed Successfully.', 'Bill Wise Report Viewed Successfully.')

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
                    #request , company, log_type, user, source, action, message, description
                    activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Excess Stock Report',
                                 'Report', 'Excess Stock Report Viewed Successfully.', 'Excess Stock Report Viewed Successfully')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Excess Stock is not Found in this Warehouse!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)

            serialized = ExcessStockMasterSerializer(excess_instances, many=True, context={"CompanyID": CompanyID,
                                                                                           "PriceRounding": PriceRounding})

            #request , company, log_type, user, source, action, message, description
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
            #request , company, log_type, user, source, action, message, description
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
                    #request , company, log_type, user, source, action, message, description
                    activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Damage Stock Report',
                                 'Report', 'Damage Stock Report Viewed Successfully.', 'Damage Stock Report Viewed Successfully')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Damage Stock is not Found in this Warehouse!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)

            serialized = DamageStockMasterSerializer(damage_instances, many=True, context={"CompanyID": CompanyID,
                                                                                           "PriceRounding": PriceRounding})

            #request , company, log_type, user, source, action, message, description
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
            #request , company, log_type, user, source, action, message, description
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
                    #request , company, log_type, user, source, action, message, description
                    activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Used Stock Report',
                                 'Report', 'Used Stock Report Viewed Successfully.', 'Used Stock Report Viewed Successfully')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Used Stock is not Found in this Warehouse!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)

            serialized = UsedStockMasterSerializer(used_instances, many=True, context={"CompanyID": CompanyID,
                                                                                       "PriceRounding": PriceRounding})

            #request , company, log_type, user, source, action, message, description
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
            #request , company, log_type, user, source, action, message, description
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
