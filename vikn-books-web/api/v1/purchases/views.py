from brands.models import PurchaseMaster, PurchaseMaster_Log, PurchaseDetails, PurchaseDetails_Log, StockPosting, LedgerPosting, StockPosting_Log,\
LedgerPosting_Log, PurchaseDetailsDummy, StockRate, PriceList, StockTrans,ProductGroup,Brand,Unit,Warehouse,PurchaseReturnMaster,OpeningStockMaster
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v1.purchases.serializers import PurchaseMasterSerializer, PurchaseMasterRestSerializer, PurchaseDetailsSerializer,\
PurchaseDetailsRestSerializer, PurchaseMasterReportSerializer, PurchaseMasterForReturnSerializer
from api.v1.brands.serializers import ListSerializer
from api.v1.purchases.functions import generate_serializer_errors
from rest_framework import status
from api.v1.sales.serializers import ListSerializerforReport
from api.v1.purchases.functions import get_auto_id, get_auto_idMaster, get_auto_StockRateID, get_auto_StockTransID
from api.v1.sales.functions import get_auto_stockPostid 
from api.v1.accountLedgers.functions import get_auto_LedgerPostid
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from main.functions import get_company, activity_log
from api.v1.purchaseReturns.serializers import PurchaseReturnMasterRestSerializer
import re


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
def create_purchase(request):
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

    Action = "A"

    #checking voucher number already exist
    VoucherNoLow = VoucherNo.lower()
    is_voucherExist = False
    insts = PurchaseMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
    if insts:
        for i in insts:
            voucher_no = i.VoucherNo
            voucherNo = voucher_no.lower()
            if VoucherNoLow == voucherNo:
                is_voucherExist = True

    if not is_voucherExist:

        PurchaseMasterID = get_auto_idMaster(PurchaseMaster,BranchID,CompanyID)

        instance = PurchaseMaster.objects.create(
            PurchaseMasterID=PurchaseMasterID,
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
            )

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
            )

        VoucherType = "PI"

        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

        LedgerPosting.objects.create(
            LedgerPostingID=LedgerPostingID,
            BranchID=BranchID,
            Date=Date,
            VoucherMasterID=PurchaseMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=PurchaseAccount,
            Debit=TotalGrossAmt,
            IsActive=IsActive,
            Action=Action,
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
            Debit=TotalGrossAmt,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            CompanyID=CompanyID,
            )

        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

        LedgerPosting.objects.create(
            LedgerPostingID=LedgerPostingID,
            BranchID=BranchID,
            Date=Date,
            VoucherMasterID=PurchaseMasterID,
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
            VoucherMasterID=PurchaseMasterID,
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

        if TaxType == 'VAT':
            if float(VATAmount) > 0:
                LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)
                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=54,
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
                    Debit=VATAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                    )
        elif TaxType == 'GST Intra-state B2B':
            if float(SGSTAmount) > 0 or float(CGSTAmount) > 0:
                LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)
                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=36,
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
                    Debit=CGSTAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                    )

                LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)
                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=42,
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
                    Debit=SGSTAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                    )
        elif TaxType == 'GST Inter-state B2B':
            if float(IGSTAmount) > 0:
                LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)
                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=39,
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
                    Debit=IGSTAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                    )
        elif not TaxType == 'Import' and not TaxType == 'VAT':
            if float(TAX1Amount) > 0:
                LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)
                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PurchaseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=45,
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
                    Debit=TAX1Amount,
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
                    LedgerID=48,
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
                    Debit=TAX2Amount,
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
                    LedgerID=51,
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
                    Debit=TAX3Amount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                    )

        if float(TotalDiscount) > 0:

            LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)


            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=PurchaseMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=83,
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
                Credit=TotalDiscount,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
                )

        if float(RoundOff) > 0:

            LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=PurchaseMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=77,
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
                Debit=RoundOff,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
                )

        if float(RoundOff) < 0:

            LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

            RoundOff = abs(float(RoundOff))

            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=PurchaseMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=77,
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
                Credit=RoundOff,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
                )

        purchaseDetails = data["PurchaseDetails"]

        for purchaseDetail in purchaseDetails:  

            # PurchaseMasterID = serialized.data['PurchaseMasterID']
            ProductID = purchaseDetail['ProductID']
            Qty = purchaseDetail['Qty']
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

            UnitPrice = round(UnitPrice,PriceRounding)
            InclusivePrice = round(InclusivePrice,PriceRounding)
            RateWithTax = round(RateWithTax,PriceRounding)
            CostPerItem = round(CostPerItem,PriceRounding)
            DiscountPerc = round(DiscountPerc,PriceRounding)
            DiscountAmount = round(DiscountAmount,PriceRounding)
            AddlDiscPerc = round(AddlDiscPerc,PriceRounding)
            AddlDiscAmt = round(AddlDiscAmt,PriceRounding)
            GrossAmount = round(GrossAmount,PriceRounding)
            TaxableAmount = round(TaxableAmount,PriceRounding)
            VATPerc = round(VATPerc,PriceRounding)
            VATAmount = round(VATAmount,PriceRounding)
            SGSTPerc = round(SGSTPerc,PriceRounding)
            SGSTAmount = round(SGSTAmount,PriceRounding)
            CGSTPerc = round(CGSTPerc,PriceRounding)
            CGSTAmount = round(CGSTAmount,PriceRounding)
            IGSTPerc = round(IGSTPerc,PriceRounding)
            IGSTAmount = round(IGSTAmount,PriceRounding)
            NetAmount = round(NetAmount,PriceRounding)
            TAX1Perc = round(TAX1Perc,PriceRounding)
            TAX1Amount = round(TAX1Amount,PriceRounding)
            TAX2Perc = round(TAX2Perc,PriceRounding)
            TAX2Amount = round(TAX2Amount,PriceRounding)
            TAX3Perc = round(TAX3Perc,PriceRounding)
            TAX3Amount = round(TAX3Amount,PriceRounding)
            
            PurchaseDetailsID = get_auto_id(PurchaseDetails,BranchID,CompanyID)
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
                )

            PurchaseDetails_Log.objects.create(
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
                )


            MultiFactor = PriceList.objects.get(CompanyID=CompanyID,PriceListID=PriceListID,BranchID=BranchID).MultiFactor
            PriceListID = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,DefaultUnit=True,BranchID=BranchID).PriceListID

            # PurchasePrice = priceList.PurchasePrice
            # SalesPrice = priceList.SalesPrice

            qty = float(FreeQty) + float(Qty)

            Qty = float(MultiFactor) * float(qty)
            Cost = float(CostPerItem) /  float(MultiFactor)

            Qy = round(Qty,4)
            Qty = str(Qy)

            Ct = round(Cost,4)
            Cost = str(Ct)

            princeList_instance = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,PriceListID=PriceListID,BranchID=BranchID)
            PurchasePrice = princeList_instance.PurchasePrice
            SalesPrice = princeList_instance.SalesPrice

            StockPostingID = get_auto_stockPostid(StockPosting,BranchID,CompanyID)

            StockPosting.objects.create(
                StockPostingID=StockPostingID,
                BranchID=BranchID,
                Action=Action,
                Date=Date,
                VoucherMasterID=PurchaseMasterID,
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


            stockRateInstance = None

            if StockRate.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Cost=Cost,ProductID=ProductID,WareHouseID=WarehouseID,PriceListID=PriceListID).exists():
                stockRateInstance = StockRate.objects.get(CompanyID=CompanyID,BranchID=BranchID,Cost=Cost,ProductID=ProductID,WareHouseID=WarehouseID,PriceListID=PriceListID)
                
                StockRateID = stockRateInstance.StockRateID
                stockRateInstance.Qty = float(stockRateInstance.Qty) + float(Qty)
                stockRateInstance.save()

                if StockTrans.objects.filter(StockRateID=StockRateID,DetailID=PurchaseDetailsID,MasterID=PurchaseMasterID,VoucherType=VoucherType,BranchID=BranchID).exists():
                    stockTra_in = StockTrans.objects.filter(StockRateID=StockRateID,DetailID=PurchaseDetailsID,MasterID=PurchaseMasterID,VoucherType=VoucherType,BranchID=BranchID).first()
                    stockTra_in.Qty = float(stockTra_in.Qty) + float(Qty)
                    stockTra_in.save()
                else:
                    StockTransID = get_auto_StockTransID(StockTrans,BranchID,CompanyID)
                    StockTrans.objects.create(
                        StockTransID=StockTransID,
                        BranchID=BranchID,
                        VoucherType=VoucherType,
                        StockRateID=StockRateID,
                        DetailID=PurchaseDetailsID,
                        MasterID=PurchaseMasterID,
                        Qty=Qty,
                        IsActive=IsActive,
                        CompanyID=CompanyID,
                        )

                
            else:
                StockRateID = get_auto_StockRateID(StockRate,BranchID,CompanyID)
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
                    PriceListID=PriceListID,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                    )

                StockTransID = get_auto_StockTransID(StockTrans,BranchID,CompanyID)
                StockTrans.objects.create(
                    StockTransID=StockTransID,
                    BranchID=BranchID,
                    VoucherType=VoucherType,
                    StockRateID=StockRateID,
                    DetailID=PurchaseDetailsID,
                    MasterID=PurchaseMasterID,
                    Qty=Qty,
                    IsActive=IsActive,
                    CompanyID=CompanyID,
                    )

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Purchase', 'Create', 'Purchase created successfully.', 'Purchase saved successfully.')

        response_data = {
            "StatusCode" : 6000,
            "id": instance.id,
            "message" : "purchase created Successfully!!!",
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Purchase', 'Create', 'Purchase created Failed.', 'VoucherNo already exist')
        response_data = {
        "StatusCode" : 6001,
        "message" : "VoucherNo already exist!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_purchase(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    today = datetime.datetime.now()
    purchaseMaster_instance = None
    purchaseDetails = None
    purchaseMaster_instance = PurchaseMaster.objects.get(CompanyID=CompanyID,pk=pk)
    PurchaseMasterID = purchaseMaster_instance.PurchaseMasterID
    VoucherNo = purchaseMaster_instance.VoucherNo
    BranchID = purchaseMaster_instance.BranchID

    Action = "M"
    if LedgerPosting.objects.filter(CompanyID=CompanyID,VoucherMasterID=PurchaseMasterID,BranchID=BranchID,VoucherType="PI").exists():

        ledgerPostInstances = LedgerPosting.objects.filter(CompanyID=CompanyID,VoucherMasterID=PurchaseMasterID,BranchID=BranchID,VoucherType="PI")
        
        for ledgerPostInstance in ledgerPostInstances:
            
            ledgerPostInstance.delete()

    if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PurchaseMasterID,BranchID=BranchID,VoucherType="PI").exists():

        stockPostingInstances = StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PurchaseMasterID,BranchID=BranchID,VoucherType="PI")
        
        for stockPostingInstance in stockPostingInstances:
    
            stockPostingInstance.delete()

        
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
    Balance = data['Balance']

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

    purchaseMaster_instance.save()

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
        )

    VoucherType = "PI"

    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

    LedgerPosting.objects.create(
        LedgerPostingID=LedgerPostingID,
        BranchID=BranchID,
        Date=Date,
        VoucherMasterID=PurchaseMasterID,
        VoucherType=VoucherType,
        VoucherNo=VoucherNo,
        LedgerID=PurchaseAccount,
        Debit=TotalGrossAmt,
        IsActive=IsActive,
        Action=Action,
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
        Debit=TotalGrossAmt,
        IsActive=IsActive,
        Action=Action,
        CreatedUserID=CreatedUserID,
        CreatedDate=today,
        UpdatedDate=today,
        CompanyID=CompanyID,
        )

    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

    LedgerPosting.objects.create(
        LedgerPostingID=LedgerPostingID,
        BranchID=BranchID,
        Date=Date,
        VoucherMasterID=PurchaseMasterID,
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
        VoucherMasterID=PurchaseMasterID,
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

    if TaxType == 'VAT':
        if float(VATAmount) > 0:
            LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)
            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=PurchaseMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=54,
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
                Debit=VATAmount,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
                )
    elif TaxType == 'GST Intra-state B2B':
        if float(SGSTAmount) > 0 or float(CGSTAmount) > 0:
            LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)
            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=PurchaseMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=36,
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
                Debit=CGSTAmount,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
                )

            LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)
            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=PurchaseMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=42,
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
                Debit=SGSTAmount,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
                )
    elif TaxType == 'GST Inter-state B2B':
        if float(IGSTAmount) > 0:
            LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)
            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=PurchaseMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=39,
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
                Debit=IGSTAmount,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
                )
    if not TaxType == 'Import':
        if float(TAX1Amount) > 0:
            LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)
            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=PurchaseMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=45,
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
                Debit=TAX1Amount,
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
                LedgerID=48,
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
                Debit=TAX2Amount,
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
                LedgerID=51,
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
                Debit=TAX3Amount,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
                )

    if float(TotalDiscount) > 0:

        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)


        LedgerPosting.objects.create(
            LedgerPostingID=LedgerPostingID,
            BranchID=BranchID,
            Date=Date,
            VoucherMasterID=PurchaseMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=83,
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
            Credit=TotalDiscount,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            CompanyID=CompanyID,
            )

    if float(RoundOff) > 0:

        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

        LedgerPosting.objects.create(
            LedgerPostingID=LedgerPostingID,
            BranchID=BranchID,
            Date=Date,
            VoucherMasterID=PurchaseMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=77,
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
            Debit=RoundOff,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            CompanyID=CompanyID,
            )

    if float(RoundOff) < 0:

        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

        RoundOff = abs(float(RoundOff))

        LedgerPosting.objects.create(
            LedgerPostingID=LedgerPostingID,
            BranchID=BranchID,
            Date=Date,
            VoucherMasterID=PurchaseMasterID,
            VoucherType=VoucherType,
            VoucherNo=VoucherNo,
            LedgerID=77,
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
            Credit=RoundOff,
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

            if PriceList.objects.filter(CompanyID=CompanyID,ProductID=ProductID_Deleted,DefaultUnit=True).exists():
                priceList = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID_Deleted,DefaultUnit=True)
                MultiFactor = priceList.MultiFactor
                Cost = float(Rate_Deleted) /  float(MultiFactor)
                Ct = round(Cost,4)
                Cost_Deleted = str(Ct)

                if not deleted_pk == '' or not deleted_pk == 0:
                    if PurchaseDetails.objects.filter(CompanyID=CompanyID,pk=deleted_pk).exists():
                        deleted_detail = PurchaseDetails.objects.get(CompanyID=CompanyID,pk=deleted_pk)
                        deleted_detail.delete()

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

                        if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=PurchaseDetailsID_Deleted,MasterID=PurchaseMasterID_Deleted,BranchID=BranchID,VoucherType=VoucherType,IsActive=True).exists():
                            stockTrans_instance = StockTrans.objects.filter(CompanyID=CompanyID,DetailID=PurchaseDetailsID_Deleted,MasterID=PurchaseMasterID_Deleted,BranchID=BranchID,VoucherType=VoucherType,IsActive=True)
                            for stck in stockTrans_instance:
                                StockRateID = stck.StockRateID
                                stck.IsActive = False
                                qty_in_stockTrans = stck.Qty
                                if StockRate.objects.filter(CompanyID=CompanyID,StockRateID=StockRateID,BranchID=BranchID).exists():
                                    stockRateInstance = StockRate.objects.get(CompanyID=CompanyID,StockRateID=StockRateID,BranchID=BranchID)
                                    stockRateInstance.Qty = float(stockRateInstance.Qty) - float(qty_in_stockTrans)
                                    stockRateInstance.save()
                                stck.save()


    purchaseDetails = data["PurchaseDetails"]
    for purchaseDetail in purchaseDetails:
        pk = purchaseDetail['unq_id']
        detailID = purchaseDetail['detailID']
        ProductID = purchaseDetail['ProductID']
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


        UnitPrice = round(UnitPrice,PriceRounding)
        InclusivePrice = round(InclusivePrice,PriceRounding)
        RateWithTax = round(RateWithTax,PriceRounding)
        CostPerItem = round(CostPerItem,PriceRounding)
        DiscountPerc = round(DiscountPerc,PriceRounding)
        DiscountAmount = round(DiscountAmount,PriceRounding)
        AddlDiscPerc = round(AddlDiscPerc,PriceRounding)
        AddlDiscAmt = round(AddlDiscAmt,PriceRounding)
        GrossAmount = round(GrossAmount,PriceRounding)
        TaxableAmount = round(TaxableAmount,PriceRounding)
        VATPerc = round(VATPerc,PriceRounding)
        VATAmount = round(VATAmount,PriceRounding)
        SGSTPerc = round(SGSTPerc,PriceRounding)
        SGSTAmount = round(SGSTAmount,PriceRounding)
        CGSTPerc = round(CGSTPerc,PriceRounding)
        CGSTAmount = round(CGSTAmount,PriceRounding)
        IGSTPerc = round(IGSTPerc,PriceRounding)
        IGSTAmount = round(IGSTAmount,PriceRounding)
        NetAmount = round(NetAmount,PriceRounding)
        TAX1Perc = round(TAX1Perc,PriceRounding)
        TAX1Amount = round(TAX1Amount,PriceRounding)
        TAX2Perc = round(TAX2Perc,PriceRounding)
        TAX2Amount = round(TAX2Amount,PriceRounding)
        TAX3Perc = round(TAX3Perc,PriceRounding)
        TAX3Amount = round(TAX3Amount,PriceRounding)


        # priceList = PriceList.objects.get(CompanyID=CompanyID,PriceListID=PriceListID,BranchID=BranchID)

        MultiFactor = PriceList.objects.get(CompanyID=CompanyID,PriceListID=PriceListID,BranchID=BranchID).MultiFactor
        PriceListID_DefUnit = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,DefaultUnit=True,BranchID=BranchID).PriceListID


        # PriceListID_DefUnit = priceList.PriceListID
        # MultiFactor = priceList.MultiFactor

        # PurchasePrice = priceList.PurchasePrice
        # SalesPrice = priceList.SalesPrice
        qty = float(FreeQty) + float(Qty_detail)

        Qty = float(MultiFactor) * float(qty)
        Cost = float(CostPerItem) /  float(MultiFactor)

        Qy = round(Qty,4)
        Qty = str(Qy)


        Ct = round(Cost,4)
        Cost = str(Ct)

        # deleted_datas = data["deleted_data"]
        # if deleted_datas:
        #     for deleted_Data in deleted_datas:
        #         deleted_pk = deleted_Data['unq_id']
        #         PurchaseDetailsID = deleted_Data['PurchaseDetailsID']
        #         if not deleted_pk == '':
        #             if PurchaseDetails.objects.filter(CompanyID=CompanyID,pk=deleted_pk).exists():
        #                 deleted_detail = PurchaseDetails.objects.filter(CompanyID=CompanyID,pk=deleted_pk)
        #                 deleted_detail.delete()

        #                 if StockRate.objects.filter(CompanyID=CompanyID,ProductID=ProductID,PriceListID=PriceListID,Cost=Cost,WareHouseID=WarehouseID).exists():
        #                     stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,ProductID=ProductID,PriceListID=PriceListID,Cost=Cost,WareHouseID=WarehouseID)
        #                     StockRateID = stockRate_instance.StockRateID
                            
        #                     stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID,DetailID=PurchaseDetailsID,MasterID=PurchaseMasterID,BranchID=BranchID,
        #                         VoucherType=VoucherType,IsActive=True,StockRateID=StockRateID)
        #                     qty_in_stockTrans = stockTrans_instance.Qty
        #                     stockRate_instance.Qty = float(stockRate_instance.Qty) - float(qty_in_stockTrans)
        #                     stockRate_instance.save()
        #                     stockTrans_instance.IsActive = False
        #                     stockTrans_instance.save()


        princeList_instance = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,PriceListID=PriceListID_DefUnit,BranchID=BranchID)
        PurchasePrice = princeList_instance.PurchasePrice
        SalesPrice = princeList_instance.SalesPrice

        
        StockPostingID = get_auto_stockPostid(StockPosting,BranchID,CompanyID)

        if detailID == 0:

            purchaseDetail_instance = PurchaseDetails.objects.get(CompanyID=CompanyID,pk=pk)
            PurchaseDetailsID = purchaseDetail_instance.PurchaseDetailsID
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

            purchaseDetail_instance.save()

            PurchaseDetails_Log.objects.create(
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
                )

            StockPosting.objects.create(
                StockPostingID=StockPostingID,
                BranchID=BranchID,
                Action=Action,
                Date=Date,
                VoucherMasterID=PurchaseMasterID,
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

        if detailID == 1:

            Action = "A"

            PurchaseDetailsID = get_auto_id(PurchaseDetails,BranchID,CompanyID)

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
                )

            PurchaseDetails_Log.objects.create(
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
                )

            StockPosting.objects.create(
                StockPostingID=StockPostingID,
                BranchID=BranchID,
                Action=Action,
                Date=Date,
                VoucherMasterID=PurchaseMasterID,
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

        if detailID == 1:
            if StockRate.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Cost=Cost,ProductID=ProductID,WareHouseID=WarehouseID,PriceListID=PriceListID).exists():
                stockRateInstance = StockRate.objects.get(CompanyID=CompanyID,BranchID=BranchID,Cost=Cost,ProductID=ProductID,WareHouseID=WarehouseID,PriceListID=PriceListID)
                
                StockRateID = stockRateInstance.StockRateID
                stockRateInstance.Qty = float(stockRateInstance.Qty) + float(Qty)
                stockRateInstance.save()

                if StockTrans.objects.filter(StockRateID=StockRateID,DetailID=PurchaseDetailsID,MasterID=PurchaseMasterID,VoucherType=VoucherType,BranchID=BranchID).exists():
                    stockTra_in = StockTrans.objects.filter(StockRateID=StockRateID,DetailID=PurchaseDetailsID,MasterID=PurchaseMasterID,VoucherType=VoucherType,BranchID=BranchID).first()
                    stockTra_in.Qty = float(stockTra_in.Qty) + float(Qty)
                    stockTra_in.save()
                else:
                    StockTransID = get_auto_StockTransID(StockTrans,BranchID,CompanyID)
                    StockTrans.objects.create(
                        StockTransID=StockTransID,
                        BranchID=BranchID,
                        VoucherType=VoucherType,
                        StockRateID=StockRateID,
                        DetailID=PurchaseDetailsID,
                        MasterID=PurchaseMasterID,
                        Qty=Qty,
                        IsActive=IsActive,
                        CompanyID=CompanyID,
                        )

                
            else:
                StockRateID = get_auto_StockRateID(StockRate,BranchID,CompanyID)
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

                StockTransID = get_auto_StockTransID(StockTrans,BranchID,CompanyID)
                StockTrans.objects.create(
                    StockTransID=StockTransID,
                    BranchID=BranchID,
                    VoucherType=VoucherType,
                    StockRateID=StockRateID,
                    DetailID=PurchaseDetailsID,
                    MasterID=PurchaseMasterID,
                    Qty=Qty,
                    IsActive=IsActive,
                    CompanyID=CompanyID,
                    )
        else:
            if StockRate.objects.filter(CompanyID=CompanyID,ProductID=ProductID,PriceListID=PriceListID_DefUnit,Cost=Cost,WareHouseID=WarehouseID).exists():
                stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,ProductID=ProductID,PriceListID=PriceListID_DefUnit,Cost=Cost,WareHouseID=WarehouseID)
                StockRateID = stockRate_instance.StockRateID
                if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=PurchaseDetailsID,MasterID=PurchaseMasterID,BranchID=BranchID,
                        VoucherType=VoucherType,IsActive=True,StockRateID=StockRateID).exists():
                    stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID,DetailID=PurchaseDetailsID,MasterID=PurchaseMasterID,BranchID=BranchID,
                        VoucherType=VoucherType,IsActive=True,StockRateID=StockRateID)

                    if float(stockTrans_instance.Qty) < float(Qty):
                        deff = float(Qty) - float(stockTrans_instance.Qty)
                        stockTrans_instance.Qty = float(stockTrans_instance.Qty) + float(deff)
                        stockTrans_instance.save()

                        stockRate_instance.Qty = float(stockRate_instance.Qty) + float(deff)
                        stockRate_instance.save()

                    elif float(stockTrans_instance.Qty) > float(Qty):
                        deff = float(stockTrans_instance.Qty) - float(Qty)
                        stockTrans_instance.Qty = float(stockTrans_instance.Qty) - float(deff)
                        stockTrans_instance.save() 

                        stockRate_instance.Qty = float(stockRate_instance.Qty) - float(deff)
                        stockRate_instance.save()

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
    activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Purchase', 'Edit', 'Purchase Updated successfully.', 'Purchase Updated successfully.')
    response_data = {
    "StatusCode" : 6000,
    "message" : "purchase updated Successfully!!!",
    }

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

        if PurchaseMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():

            instances = PurchaseMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID)

            serialized = PurchaseMasterRestSerializer(instances,many=True,context = {"CompanyID": CompanyID, 
                "PriceRounding": PriceRounding, "QtyRounding" : QtyRounding })

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Purchase', 'List', 'Purchase List Viewed successfully.', 'Purchase List Viewed successfully.')
            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Purchase', 'List', 'Purchase List Viewed Failed.', 'Purchase not found in this branch')
            response_data = {
            "StatusCode" : 6001,
            "message" : "Purchase Master not found in this branch."
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Branch you enterd is not valid."
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
            purchase_object = PurchaseMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID)

            purchase_sort_pagination = list_pagination(
                purchase_object,
                items_per_page,
                page_number
            )
            purchase_serializer = PurchaseMasterRestSerializer(
                purchase_sort_pagination,
                many=True,
                context={"request":request,"CompanyID":CompanyID,"PriceRounding" : PriceRounding, "QtyRounding" : QtyRounding}
            )
            data = purchase_serializer.data
            if not data==None:
                response_data = {
                    "StatusCode" : 6000,
                    "data" : data,
                    "count": len(purchase_object)
                }
            else:
                response_data = {
                    "StatusCode" : 6001
                }

            return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def purchaseMaster(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    QtyRounding = data['QtyRounding']
    PriceRounding = data['PriceRounding']

    if PurchaseMaster.objects.filter(CompanyID=CompanyID,pk=pk).exists():
        instance = PurchaseMaster.objects.get(CompanyID=CompanyID,pk=pk)
        serialized = PurchaseMasterRestSerializer(instance,context = {"CompanyID": CompanyID, 
                "PriceRounding": PriceRounding, "QtyRounding" : QtyRounding })

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Purchase', 'View', 'Purchase single Viewed successfully.', 'Purchase single Viewed successfully.')

        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Purchase Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_purchaseMaster(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    instance = None
    if PurchaseMaster.objects.filter(CompanyID=CompanyID,pk=pk).exists():
        instance = PurchaseMaster.objects.get(CompanyID=CompanyID,pk=pk)
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
            )

        instance.delete()

        if LedgerPosting.objects.filter(CompanyID=CompanyID,VoucherMasterID=PurchaseMasterID,BranchID=BranchID,VoucherType="PI").exists():

            ledgerPostInstances = LedgerPosting.objects.filter(CompanyID=CompanyID,VoucherMasterID=PurchaseMasterID,BranchID=BranchID,VoucherType="PI")
            
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
                    VoucherMasterID=PurchaseMasterID,
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

        if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PurchaseMasterID,BranchID=BranchID,VoucherType="PI").exists():

            stockPostingInstances = StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PurchaseMasterID,BranchID=BranchID,VoucherType="PI")
            
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
                    VoucherMasterID=PurchaseMasterID,
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


        detail_instances = PurchaseDetails.objects.filter(CompanyID=CompanyID,PurchaseMasterID=PurchaseMasterID)

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
                )

            detail_instance.delete()

            # if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=PurchaseDetailsID,MasterID=PurchaseMasterID,BranchID=BranchID,VoucherType="PI").exists():
            #     stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID,DetailID=PurchaseDetailsID,MasterID=PurchaseMasterID,BranchID=BranchID,VoucherType="PI")

            #     stockRateID = stockTrans_instance.StockRateID
            #     stockTrans_instance.IsActive = False
            #     stockTrans_instance.save()

            #     stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,StockRateID=stockRateID,BranchID=BranchID)
            #     stockRate_instance.Qty = stockTrans_instance.Qty
            #     stockRate_instance.save()

            if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=PurchaseDetailsID,MasterID=PurchaseMasterID,BranchID=BranchID,VoucherType="PI",IsActive = True).exists():
                stockTrans_instances = StockTrans.objects.filter(CompanyID=CompanyID,DetailID=PurchaseDetailsID,MasterID=PurchaseMasterID,BranchID=BranchID,VoucherType="PI",IsActive = True)

                for i in stockTrans_instances:
                    stockRateID = i.StockRateID
                    i.IsActive = False
                    i.save()

                    stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,StockRateID=stockRateID,BranchID=BranchID)
                    stockRate_instance.Qty = float(stockRate_instance.Qty) - float(i.Qty)
                    stockRate_instance.save()

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Purchase', 'Delete', 'Purchase Deleted successfully.', 'Purchase Deleted successfully.')
        
        response_data = {
            "StatusCode" : 6000,
            "title" : "Success",
            "message" : "Purchase Master Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "title" : "Failed",
            "message" : "Purchase Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def report_purchases(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = int(data['PriceRounding'])
    serialized1 = ListSerializerforReport(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        FromDate = serialized1.data['FromDate']
        ToDate = serialized1.data['ToDate']

        purchase_data = []
        purchaseReturn_data = []
        Total_netAmt_purchase = 0
        Total_netAmt_purchaseRetn = 0
        Total_tax_purchase = 0
        Total_tax_purchaseRetn = 0
        Total_billDiscount_purchase = 0
        Total_billDiscount_purchaseRetn = 0
        Total_grandTotal_purchase = 0
        Total_grandTotal_purchaseRetn = 0

        PurchaseCode = 6001
        PurchaseReturnCode = 6001
        if PurchaseMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Date__gte=FromDate,Date__lte=ToDate).exists():
            instances = PurchaseMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Date__gte=FromDate,Date__lte=ToDate)
            serialized_purchase = PurchaseMasterRestSerializer(instances,many=True,context = {"CompanyID": CompanyID,"PriceRounding" : PriceRounding })
            purchase_data = serialized_purchase.data
            PurchaseCode = 6000

            for i_purchase in instances:
                Total_netAmt_purchase += i_purchase.NetTotal
                Total_tax_purchase += i_purchase.TotalTax
                Total_billDiscount_purchase += i_purchase.BillDiscAmt
                Total_grandTotal_purchase += i_purchase.GrandTotal

        if PurchaseReturnMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,VoucherDate__gte=FromDate,VoucherDate__lte=ToDate).exists():
            instances_purchaseReturn = PurchaseReturnMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,VoucherDate__gte=FromDate,VoucherDate__lte=ToDate)
            serialized_purchaseReturn = PurchaseReturnMasterRestSerializer(instances_purchaseReturn,many=True,context = {"CompanyID": CompanyID, "PriceRounding" : PriceRounding })
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
            response_data = {
                "StatusCode" : 6000,
                "PurchaseCode" : PurchaseCode,
                "PurchaseReturnCode" : PurchaseReturnCode,
                "purchase_data" : purchase_data,
                "purchaseReturn_data" : purchaseReturn_data,
                "Total_netAmt_purchase" : round(Total_netAmt_purchase,PriceRounding),
                "Total_netAmt_purchaseRetn" : round(Total_netAmt_purchaseRetn,PriceRounding),
                "Total_tax_purchase" : round(Total_tax_purchase,PriceRounding),
                "Total_tax_purchaseRetn" : round(Total_tax_purchaseRetn,PriceRounding),
                "Total_billDiscount_purchase" : round(Total_billDiscount_purchase,PriceRounding),
                "Total_billDiscount_purchaseRetn" : round(Total_billDiscount_purchaseRetn,PriceRounding),
                "Total_grandTotal_purchase" : round(Total_grandTotal_purchase,PriceRounding),
                "Total_grandTotal_purchaseRetn" : round(Total_grandTotal_purchaseRetn,PriceRounding),
                }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode" : 6001,
                "message" : "Datas Not Found!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "please provide valid datas!!!"
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
    if PurchaseMaster.objects.filter(CompanyID=CompanyID,VoucherNo=VoucherNo,BranchID=BranchID).exists():
        instance = PurchaseMaster.objects.get(CompanyID=CompanyID,VoucherNo=VoucherNo,BranchID=BranchID)

        serialized = PurchaseMasterForReturnSerializer(instance,context = {"CompanyID": CompanyID,
        "PriceRounding": PriceRounding, })

        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Purchase Master Not Found!"
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

    default_productGroup = ProductGroup.objects.get(CompanyID=CompanyID,ProductGroupID=1,BranchID=BranchID).GroupName
    default_brand = Brand.objects.get(CompanyID=CompanyID,BrandID=1,BranchID=BranchID).BrandName
    default_unit = Unit.objects.get(CompanyID=CompanyID,UnitID=1,BranchID=BranchID).UnitName
    default_warehouse = Warehouse.objects.get(CompanyID=CompanyID,WarehouseID=1,BranchID=BranchID).WarehouseName


    if default_productGroup and default_brand and default_unit:
        if OpeningStockMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
            instance = OpeningStockMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "OS" + str(new_num)


            response_data = {
                "StatusCode" : 6000,
                "default_productGroup" : default_productGroup,
                "default_brand" : default_brand,
                "default_unit" : default_unit,
                "default_warehouse" : default_warehouse,
                "VoucherNo" : new_VoucherNo
            }
        else:
            response_data = {
            "StatusCode" : 6000,
            "VoucherNo" : "OS1",
            "default_productGroup" : default_productGroup,
            "default_brand" : default_brand,
            "default_unit" : default_unit,
            "default_warehouse" : default_warehouse,
            }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "some error occured!",
        }

    return Response(response_data, status=status.HTTP_200_OK)