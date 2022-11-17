from brands.models import PurchaseReturnMaster, PurchaseReturnMaster_Log, PurchaseReturnDetails, PurchaseReturnDetails_Log,\
    StockPosting, LedgerPosting, StockPosting_Log, LedgerPosting_Log, PurchaseReturnDetailsDummy, PriceList, StockRate, StockTrans,\
    PurchaseMaster, PurchaseDetails, GeneralSettings, Batch, Product, ProductGroup
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v5.purchaseReturns.serializers import PurchaseReturnMasterSerializer, PurchaseReturn1MasterRestSerializer, PurchaseReturnMasterRestSerializer, PurchaseReturnDetailsSerializer, PurchaseReturnDetailsRestSerializer
from api.v5.brands.serializers import ListSerializer
from api.v5.purchaseReturns.functions import generate_serializer_errors
from rest_framework import status
from api.v5.sales.serializers import ListSerializerforReport
from api.v5.purchaseReturns.functions import get_auto_id, get_auto_idMaster
from api.v5.sales.functions import get_auto_stockPostid
from api.v5.accountLedgers.functions import get_auto_LedgerPostid
from api.v5.purchases.functions import get_auto_StockRateID, get_auto_StockTransID
import datetime
from main.functions import get_company, activity_log, list_pagination
from api.v5.products.functions import get_auto_AutoBatchCode
from api.v5.sales.functions import get_Genrate_VoucherNo
from django.db.models import Q, Prefetch
from django.db import transaction, IntegrityError
import re
import sys
import os


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def create_purchaseReturn(request):
    try:
        with transaction.atomic():
            today = datetime.datetime.now()
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            PriceRounding = data['PriceRounding']
            CreatedUserID = data['CreatedUserID']

            BranchID = data['BranchID']
            VoucherDate = data['VoucherDate']
            VoucherNo = data['VoucherNo']
            RefferenceBillNo = data['RefferenceBillNo']
            RefferenceBillDate = data['RefferenceBillDate']
            VenderInvoiceDate = data['VenderInvoiceDate']
            CreditPeriod = data['CreditPeriod']
            LedgerID = data['LedgerID']
            PriceCategoryID = data['PriceCategoryID']
            EmployeeID = data['EmployeeID']
            PurchaseAccount = data['PurchaseAccount']
            DeliveryMasterID = data['DeliveryMasterID']
            OrderMasterID = data['OrderMasterID']
            CustomerName = data['CustomerName']
            Address1 = data['Address1']
            Address2 = data['Address2']
            Address3 = data['Address3']
            Notes = data['Notes']
            FinacialYearID = data['FinacialYearID']
            IsActive = data['IsActive']
            WarehouseID = data['WarehouseID']
            BatchID = data['BatchID']
            TaxID = data['TaxID']
            TaxType = data['TaxType']

            TotalTax = float(data['TotalTax'])
            NetTotal = float(data['NetTotal'])
            AdditionalCost = float(data['AdditionalCost'])
            GrandTotal = float(data['GrandTotal'])
            RoundOff = float(data['RoundOff'])
            TotalGrossAmt = float(data['TotalGrossAmt'])
            VATAmount = float(data['VATAmount'])
            SGSTAmount = float(data['SGSTAmount'])
            CGSTAmount = float(data['CGSTAmount'])
            IGSTAmount = float(data['IGSTAmount'])
            TAX1Amount = float(data['TAX1Amount'])
            TAX2Amount = float(data['TAX2Amount'])
            TAX3Amount = float(data['TAX3Amount'])
            AddlDiscPercent = float(data['AddlDiscPercent'])
            AddlDiscAmt = float(data['AddlDiscAmt'])
            TotalDiscount = float(data['TotalDiscount'])
            BillDiscPercent = float(data['BillDiscPercent'])
            BillDiscAmt = float(data['BillDiscAmt'])

            # TotalTax = round(TotalTax, PriceRounding)
            # NetTotal = round(NetTotal, PriceRounding)
            # AdditionalCost = round(AdditionalCost, PriceRounding)
            # GrandTotal = round(GrandTotal, PriceRounding)
            # RoundOff = round(RoundOff, PriceRounding)

            # TotalGrossAmt = round(TotalGrossAmt, PriceRounding)
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

            Action = "A"

            purchaseReturnDetails = data["PurchaseReturnDetails"]
            TotalTaxableAmount = 0
            for i in purchaseReturnDetails:
                TotalTaxableAmount += float(i['TaxableAmount'])

            # checking voucher number already exist
            VoucherNoLow = VoucherNo.lower()
            is_voucherExist = False
            insts = PurchaseReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True

            check_VoucherNoAutoGenerate = False
            is_PurchaseReturnOK = True

            if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="VoucherNoAutoGenerate").exists():
                check_VoucherNoAutoGenerate = GeneralSettings.objects.get(
                    CompanyID=CompanyID, SettingsType="VoucherNoAutoGenerate").SettingsValue

            if is_voucherExist == True and check_VoucherNoAutoGenerate == "True":
                VoucherNo = get_Genrate_VoucherNo(
                    PurchaseReturnMaster, BranchID, CompanyID, "PR")
                is_PurchaseReturnOK = True
            elif is_voucherExist == False:
                is_PurchaseReturnOK = True
            else:
                is_PurchaseReturnOK = False

            if is_PurchaseReturnOK:

                PurchaseReturnMasterID = get_auto_idMaster(
                    PurchaseReturnMaster, BranchID, CompanyID)

                PurchaseReturnMaster_Log.objects.create(
                    TransactionID=PurchaseReturnMasterID,
                    TotalTaxableAmount=TotalTaxableAmount,
                    BranchID=BranchID,
                    VoucherNo=VoucherNo,
                    VoucherDate=VoucherDate,
                    RefferenceBillNo=RefferenceBillNo,
                    RefferenceBillDate=RefferenceBillDate,
                    VenderInvoiceDate=VenderInvoiceDate,
                    CreditPeriod=CreditPeriod,
                    LedgerID=LedgerID,
                    PriceCategoryID=PriceCategoryID,
                    EmployeeID=EmployeeID,
                    PurchaseAccount=PurchaseAccount,
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
                    WarehouseID=WarehouseID,
                    IsActive=IsActive,
                    CreatedUserID=CreatedUserID,
                    Action=Action,
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
                )

                PurchaseReturnMaster.objects.create(
                    PurchaseReturnMasterID=PurchaseReturnMasterID,
                    TotalTaxableAmount=TotalTaxableAmount,
                    BranchID=BranchID,
                    VoucherNo=VoucherNo,
                    VoucherDate=VoucherDate,
                    RefferenceBillNo=RefferenceBillNo,
                    RefferenceBillDate=RefferenceBillDate,
                    VenderInvoiceDate=VenderInvoiceDate,
                    CreditPeriod=CreditPeriod,
                    LedgerID=LedgerID,
                    PriceCategoryID=PriceCategoryID,
                    EmployeeID=EmployeeID,
                    PurchaseAccount=PurchaseAccount,
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
                    WarehouseID=WarehouseID,
                    IsActive=IsActive,
                    CreatedUserID=CreatedUserID,
                    Action=Action,
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
                )

                VoucherType = "PR"

                # new posting starting from here
                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=PurchaseReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
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
                    Date=VoucherDate,
                    VoucherMasterID=PurchaseReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
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
                    Date=VoucherDate,
                    VoucherMasterID=PurchaseReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=PurchaseAccount,
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
                    VoucherMasterID=PurchaseReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=PurchaseAccount,
                    Debit=GrandTotal,
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
                            Date=VoucherDate,
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=54,
                            RelatedLedgerID=PurchaseAccount,
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
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=54,
                            RelatedLedgerID=PurchaseAccount,
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
                            Date=VoucherDate,
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=54,
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
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=54,
                            Debit=VATAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                elif TaxType == 'GST Intra-state B2B':
                    if float(CGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=36,
                            RelatedLedgerID=PurchaseAccount,
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
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=36,
                            RelatedLedgerID=PurchaseAccount,
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
                            Date=VoucherDate,
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=36,
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
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=36,
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
                            Date=VoucherDate,
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=42,
                            RelatedLedgerID=PurchaseAccount,
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
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=42,
                            RelatedLedgerID=PurchaseAccount,
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
                            Date=VoucherDate,
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=42,
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
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=42,
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
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=39,
                            RelatedLedgerID=PurchaseAccount,
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
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=39,
                            RelatedLedgerID=PurchaseAccount,
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
                            Date=VoucherDate,
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=39,
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
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=39,
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
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=VoucherDate,
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=45,
                            RelatedLedgerID=PurchaseAccount,
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
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=45,
                            RelatedLedgerID=PurchaseAccount,
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
                            Date=VoucherDate,
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=45,
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
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=45,
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
                            Date=VoucherDate,
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=48,
                            RelatedLedgerID=PurchaseAccount,
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
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=48,
                            RelatedLedgerID=PurchaseAccount,
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
                            Date=VoucherDate,
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=48,
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
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=48,
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
                            Date=VoucherDate,
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=51,
                            RelatedLedgerID=PurchaseAccount,
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
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=51,
                            RelatedLedgerID=PurchaseAccount,
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
                            Date=VoucherDate,
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=51,
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
                            VoucherMasterID=PurchaseReturnMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=PurchaseAccount,
                            RelatedLedgerID=51,
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
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
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
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
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

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
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
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
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

                if float(RoundOff) < 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    RoundOff = abs(float(RoundOff))

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
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
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
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

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
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
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
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

                if float(TotalDiscount) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=83,
                        RelatedLedgerID=PurchaseAccount,
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
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=83,
                        RelatedLedgerID=PurchaseAccount,
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
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=83,
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
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=83,
                        Credit=TotalDiscount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                # new posting end here

                purchaseReturnDetails = data["PurchaseReturnDetails"]

                for purchaseReturnDetail in purchaseReturnDetails:

                    ProductID = purchaseReturnDetail['ProductID']
                    if ProductID:
                        # PurchaseReturnMasterID = serialized.data['PurchaseReturnMasterID']
                        DeliveryDetailsID = purchaseReturnDetail['DeliveryDetailsID']
                        OrderDetailsID = purchaseReturnDetail['OrderDetailsID']
                        Qty = purchaseReturnDetail['Qty']
                        FreeQty = purchaseReturnDetail['FreeQty']
                        PriceListID = purchaseReturnDetail['PriceListID']

                        DiscountPerc = float(
                            purchaseReturnDetail['DiscountPerc'])
                        DiscountAmount = float(
                            purchaseReturnDetail['DiscountAmount'])
                        GrossAmount = float(
                            purchaseReturnDetail['GrossAmount'])
                        TaxableAmount = float(
                            purchaseReturnDetail['TaxableAmount'])
                        VATPerc = float(purchaseReturnDetail['VATPerc'])
                        VATAmount = float(purchaseReturnDetail['VATAmount'])
                        SGSTPerc = float(purchaseReturnDetail['SGSTPerc'])
                        SGSTAmount = float(purchaseReturnDetail['SGSTAmount'])
                        CGSTPerc = float(purchaseReturnDetail['CGSTPerc'])
                        CGSTAmount = float(purchaseReturnDetail['CGSTAmount'])
                        IGSTPerc = float(purchaseReturnDetail['IGSTPerc'])
                        IGSTAmount = float(purchaseReturnDetail['IGSTAmount'])
                        NetAmount = float(purchaseReturnDetail['NetAmount'])
                        RateWithTax = float(
                            purchaseReturnDetail['RateWithTax'])
                        # CostPerPrice = float(purchaseReturnDetail['CostPerPrice'])
                        UnitPrice = float(purchaseReturnDetail['UnitPrice'])
                        InclusivePrice = float(
                            purchaseReturnDetail['InclusivePrice'])
                        AddlDiscPerc = float(
                            purchaseReturnDetail['AddlDiscPerc'])
                        AddlDiscAmt = float(
                            purchaseReturnDetail['AddlDiscAmt'])
                        TAX1Perc = float(purchaseReturnDetail['TAX1Perc'])
                        TAX1Amount = float(purchaseReturnDetail['TAX1Amount'])
                        TAX2Perc = float(purchaseReturnDetail['TAX2Perc'])
                        TAX2Amount = float(purchaseReturnDetail['TAX2Amount'])
                        TAX3Perc = float(purchaseReturnDetail['TAX3Perc'])
                        TAX3Amount = float(purchaseReturnDetail['TAX3Amount'])

                        CostPerPrice = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).PurchasePrice

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
                        # RateWithTax = round(RateWithTax, PriceRounding)
                        # CostPerPrice = round(CostPerPrice, PriceRounding)

                        # UnitPrice = round(UnitPrice, PriceRounding)
                        # InclusivePrice = round(InclusivePrice, PriceRounding)
                        # AddlDiscPerc = round(AddlDiscPerc, PriceRounding)
                        # AddlDiscAmt = round(AddlDiscAmt, PriceRounding)
                        # TAX1Perc = round(TAX1Perc, PriceRounding)

                        # TAX1Amount = round(TAX1Amount, PriceRounding)
                        # TAX2Perc = round(TAX2Perc, PriceRounding)
                        # TAX2Amount = round(TAX2Amount, PriceRounding)
                        # TAX3Perc = round(TAX3Perc, PriceRounding)
                        # TAX3Amount = round(TAX3Amount, PriceRounding)

                        try:
                            BatchCode = purchaseReturnDetail['BatchCode']
                        except:
                            BatchCode = 0
                        try:
                            is_inclusive = purchaseReturnDetail['is_inclusive']
                        except:
                            is_inclusive = False

                        if is_inclusive == True:
                            Batch_purchasePrice = InclusivePrice
                        else:
                            Batch_purchasePrice = UnitPrice

                        product_is_Service = Product.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).is_Service

                        MultiFactor = PriceList.objects.get(
                            CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor

                        qty_batch = float(FreeQty) + float(Qty)
                        Qty_batch = float(MultiFactor) * float(qty_batch)
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
                                SalesPrice = pri_ins.SalesPrice

                                if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                                    if check_BatchCriteria == "PurchasePrice":
                                        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PurchasePrice=Batch_purchasePrice).exists():
                                            batch_ins = Batch.objects.filter(
                                                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PurchasePrice=Batch_purchasePrice).last()
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
                                                PurchasePrice=Batch_purchasePrice,
                                                SalesPrice=SalesPrice,
                                                PriceListID=PriceListID,
                                                ProductID=ProductID,
                                                WareHouseID=WarehouseID,
                                                CreatedDate=today,
                                                UpdatedDate=today,
                                                CreatedUserID=CreatedUserID,
                                            )
                                    elif check_BatchCriteria == "PurchasePriceAndExpiryDate":
                                        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PurchasePrice=Batch_purchasePrice, ExpiryDate=ExpiryDate).exists():
                                            batch_ins = Batch.objects.filter(
                                                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PurchasePrice=Batch_purchasePrice, ExpiryDate=ExpiryDate).last()
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
                                                PurchasePrice=Batch_purchasePrice,
                                                SalesPrice=SalesPrice,
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
                                            PurchasePrice=Batch_purchasePrice,
                                            SalesPrice=SalesPrice,
                                            PriceListID=PriceListID,
                                            ProductID=ProductID,
                                            WareHouseID=WarehouseID,
                                            CreatedDate=today,
                                            UpdatedDate=today,
                                            CreatedUserID=CreatedUserID,
                                        )

                        PurchaseReturnQty = Qty
                        PurchaseReturnDetailsID = get_auto_id(
                            PurchaseReturnDetails, BranchID, CompanyID)

                        log_instance = PurchaseReturnDetails_Log.objects.create(
                            TransactionID=PurchaseReturnDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            PurchaseReturnMasterID=PurchaseReturnMasterID,
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
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            AddlDiscPerc=AddlDiscPerc,
                            AddlDiscAmt=AddlDiscAmt,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            CompanyID=CompanyID,
                            BatchCode=BatchCode
                        )

                        PurchaseReturnDetails.objects.create(
                            PurchaseReturnDetailsID=PurchaseReturnDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            PurchaseReturnMasterID=PurchaseReturnMasterID,
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
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            AddlDiscPerc=AddlDiscPerc,
                            AddlDiscAmt=AddlDiscAmt,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            CompanyID=CompanyID,
                            BatchCode=BatchCode,
                            LogID=log_instance.ID
                        )

                        # priceList = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,DefaultUnit=True,BranchID=BranchID)

                        # PriceListID_DefUnit = priceList.PriceListID
                        # MultiFactor = priceList.MultiFactor

                        # MultiFactor = PriceList.objects.get(
                        #     CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor
                        PriceListID_DefUnit = PriceList.objects.get(
                            CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

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
                                                                           VoucherMasterID=PurchaseReturnMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit).exists():
                                                stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                                              VoucherMasterID=PurchaseReturnMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit)
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
                                                    Date=VoucherDate,
                                                    VoucherMasterID=PurchaseReturnMasterID,
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
                                                    Date=VoucherDate,
                                                    VoucherMasterID=PurchaseReturnMasterID,
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

                                            if StockTrans.objects.filter(StockRateID=StockRateID, DetailID=PurchaseReturnDetailsID, MasterID=PurchaseReturnMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                                                stockTra_in = StockTrans.objects.filter(
                                                    StockRateID=StockRateID, DetailID=PurchaseReturnDetailsID, MasterID=PurchaseReturnMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
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
                                                    DetailID=PurchaseReturnDetailsID,
                                                    MasterID=PurchaseReturnMasterID,
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
                                                                               VoucherMasterID=PurchaseReturnMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit).exists():
                                                    stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                                                  VoucherMasterID=PurchaseReturnMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit)
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
                                                        Date=VoucherDate,
                                                        VoucherMasterID=PurchaseReturnMasterID,
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
                                                        Date=VoucherDate,
                                                        VoucherMasterID=PurchaseReturnMasterID,
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
                                                if StockTrans.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, DetailID=PurchaseReturnDetailsID, MasterID=PurchaseReturnMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                                                    stockTra_in = StockTrans.objects.filter(
                                                        CompanyID=CompanyID, StockRateID=StockRateID, DetailID=PurchaseReturnDetailsID, MasterID=PurchaseReturnMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
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
                                                        DetailID=PurchaseReturnDetailsID,
                                                        MasterID=PurchaseReturnMasterID,
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
                                                                               VoucherMasterID=PurchaseReturnMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit).exists():
                                                    stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                                                  VoucherMasterID=PurchaseReturnMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit)
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
                                                        Date=VoucherDate,
                                                        VoucherMasterID=PurchaseReturnMasterID,
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
                                                        Date=VoucherDate,
                                                        VoucherMasterID=PurchaseReturnMasterID,
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

                                                if StockTrans.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, DetailID=PurchaseReturnDetailsID, MasterID=PurchaseReturnMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                                                    stockTra_in = StockTrans.objects.filter(
                                                        CompanyID=CompanyID, StockRateID=StockRateID, DetailID=PurchaseReturnDetailsID, MasterID=PurchaseReturnMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
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
                                                        DetailID=PurchaseReturnDetailsID,
                                                        MasterID=PurchaseReturnMasterID,
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
                                                                           VoucherMasterID=PurchaseReturnMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit).exists():
                                                stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                                              VoucherMasterID=PurchaseReturnMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit)
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
                                                    Date=VoucherDate,
                                                    VoucherMasterID=PurchaseReturnMasterID,
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
                                                    Date=VoucherDate,
                                                    VoucherMasterID=PurchaseReturnMasterID,
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

                                            if StockTrans.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, DetailID=PurchaseReturnDetailsID, MasterID=PurchaseReturnMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                                                stockTra_in = StockTrans.objects.filter(
                                                    CompanyID=CompanyID, StockRateID=StockRateID, DetailID=PurchaseReturnDetailsID, MasterID=PurchaseReturnMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
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
                                                    DetailID=PurchaseReturnDetailsID,
                                                    MasterID=PurchaseReturnMasterID,
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
                                                                           VoucherMasterID=PurchaseReturnMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit).exists():
                                                stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                                              VoucherMasterID=PurchaseReturnMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit)
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
                                                    Date=VoucherDate,
                                                    VoucherMasterID=PurchaseReturnMasterID,
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
                                                    Date=VoucherDate,
                                                    VoucherMasterID=PurchaseReturnMasterID,
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
                                                                             DetailID=PurchaseReturnDetailsID,
                                                                             MasterID=PurchaseReturnMasterID,
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
                                                    DetailID=PurchaseReturnDetailsID,
                                                    MasterID=PurchaseReturnMasterID,
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
                                    Date=VoucherDate,
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
                                    Date=VoucherDate,
                                    VoucherMasterID=PurchaseReturnMasterID,
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
                                    Date=VoucherDate,
                                    VoucherMasterID=PurchaseReturnMasterID,
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
                                    DetailID=PurchaseReturnDetailsID,
                                    MasterID=PurchaseReturnMasterID,
                                    Qty=Qty,
                                    IsActive=IsActive,
                                    CompanyID=CompanyID,
                                )

                        if PurchaseMaster.objects.filter(CompanyID=CompanyID, VoucherNo=RefferenceBillNo, BranchID=BranchID).exists():

                            PurchaseMaster_instance = PurchaseMaster.objects.get(
                                CompanyID=CompanyID, VoucherNo=RefferenceBillNo, BranchID=BranchID)
                            PurchaseMasterID = PurchaseMaster_instance.PurchaseMasterID

                            if PurchaseDetails.objects.filter(CompanyID=CompanyID, PurchaseMasterID=PurchaseMasterID, BranchID=BranchID, ProductID=ProductID).exists():
                                PurchaseDetails_instances = PurchaseDetails.objects.filter(
                                    CompanyID=CompanyID, PurchaseMasterID=PurchaseMasterID, BranchID=BranchID, ProductID=ProductID)

                                for i in PurchaseDetails_instances:
                                    ReturnQty = i.ReturnQty
                                    PurchaseReturnQty = PurchaseReturnQty
                                    ReturnQty = float(ReturnQty) - \
                                        float(PurchaseReturnQty)
                                    i.ReturnQty = ReturnQty

                                    i.save()

                #request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'PurchaseReturns',
                #              'Create', 'Purchase Returns created Successfully.', 'Purchase Returns created Successfully.')
                response_data = {
                    "StatusCode": 6000,
                    "message": "Purchase Return created Successfully!!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'PurchaseReturns',
                             'Create', 'Purchase Returns created Failed.', 'VoucherNo already exist!')

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

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Purchase Return',
                     'Create', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def edit_purchaseReturn(request, pk):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            PriceRounding = data['PriceRounding']
            CreatedUserID = data['CreatedUserID']

            today = datetime.datetime.now()

            purchaseReturnMaster_instance = None
            purchaseReturnDetails = None

            purchaseReturnMaster_instance = PurchaseReturnMaster.objects.get(
                CompanyID=CompanyID, pk=pk)

            PurchaseReturnMasterID = purchaseReturnMaster_instance.PurchaseReturnMasterID
            BranchID = purchaseReturnMaster_instance.BranchID
            VoucherNo = purchaseReturnMaster_instance.VoucherNo

            Action = "M"

            VoucherDate = data['VoucherDate']
            RefferenceBillNo = data['RefferenceBillNo']
            RefferenceBillDate = data['RefferenceBillDate']
            VenderInvoiceDate = data['VenderInvoiceDate']
            CreditPeriod = data['CreditPeriod']
            LedgerID = data['LedgerID']
            PriceCategoryID = data['PriceCategoryID']
            EmployeeID = data['EmployeeID']
            PurchaseAccount = data['PurchaseAccount']
            DeliveryMasterID = data['DeliveryMasterID']
            OrderMasterID = data['OrderMasterID']
            CustomerName = data['CustomerName']
            Address1 = data['Address1']
            Address2 = data['Address2']
            Address3 = data['Address3']
            Notes = data['Notes']
            FinacialYearID = data['FinacialYearID']
            WarehouseID = data['WarehouseID']
            IsActive = data['IsActive']
            BatchID = data['BatchID']
            TaxID = data['TaxID']
            TaxType = data['TaxType']

            TotalTax = float(data['TotalTax'])
            NetTotal = float(data['NetTotal'])
            AdditionalCost = float(data['AdditionalCost'])
            GrandTotal = float(data['GrandTotal'])
            RoundOff = float(data['RoundOff'])
            TotalGrossAmt = float(data['TotalGrossAmt'])
            VATAmount = float(data['VATAmount'])
            SGSTAmount = float(data['SGSTAmount'])
            CGSTAmount = float(data['CGSTAmount'])
            IGSTAmount = float(data['IGSTAmount'])
            TAX1Amount = float(data['TAX1Amount'])
            TAX2Amount = float(data['TAX2Amount'])
            TAX3Amount = float(data['TAX3Amount'])
            AddlDiscPercent = float(data['AddlDiscPercent'])
            AddlDiscAmt = float(data['AddlDiscAmt'])
            TotalDiscount = float(data['TotalDiscount'])
            BillDiscPercent = float(data['BillDiscPercent'])
            BillDiscAmt = float(data['BillDiscAmt'])

            # TotalTax = round(TotalTax, PriceRounding)
            # NetTotal = round(NetTotal, PriceRounding)
            # AdditionalCost = round(AdditionalCost, PriceRounding)
            # GrandTotal = round(GrandTotal, PriceRounding)
            # RoundOff = round(RoundOff, PriceRounding)

            # TotalGrossAmt = round(TotalGrossAmt, PriceRounding)
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

            purchaseReturnDetails = data["PurchaseReturnDetails"]
            TotalTaxableAmount = 0
            for i in purchaseReturnDetails:
                TotalTaxableAmount += float(i['TaxableAmount'])

            PurchaseReturnMaster_Log.objects.create(
                TransactionID=PurchaseReturnMasterID,
                TotalTaxableAmount=TotalTaxableAmount,
                BranchID=BranchID,
                VoucherNo=VoucherNo,
                VoucherDate=VoucherDate,
                RefferenceBillNo=RefferenceBillNo,
                RefferenceBillDate=RefferenceBillDate,
                VenderInvoiceDate=VenderInvoiceDate,
                CreditPeriod=CreditPeriod,
                LedgerID=LedgerID,
                PriceCategoryID=PriceCategoryID,
                EmployeeID=EmployeeID,
                PurchaseAccount=PurchaseAccount,
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
                WarehouseID=WarehouseID,
                IsActive=IsActive,
                CreatedUserID=CreatedUserID,
                Action=Action,
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
            )

            if LedgerPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PurchaseReturnMasterID, BranchID=BranchID, VoucherType="PR").exists():

                ledgerPostInstances = LedgerPosting.objects.filter(
                    CompanyID=CompanyID, VoucherMasterID=PurchaseReturnMasterID, BranchID=BranchID, VoucherType="PR")

                for ledgerPostInstance in ledgerPostInstances:

                    ledgerPostInstance.delete()

            if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PurchaseReturnMasterID, BranchID=BranchID, VoucherType="PR").exists():
                stockPostingInstances = StockPosting.objects.filter(
                    CompanyID=CompanyID, VoucherMasterID=PurchaseReturnMasterID, BranchID=BranchID, VoucherType="PR")
                for stockPostingInstance in stockPostingInstances:
                    stockPostingInstance.delete()

            if StockTrans.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType="PR", MasterID=PurchaseReturnMasterID, IsActive=True).exists():
                trans_ins = StockTrans.objects.filter(
                    CompanyID=CompanyID, VoucherType="PR", MasterID=PurchaseReturnMasterID, IsActive=True)
                for s in trans_ins:
                    trans_StockRateID = s.StockRateID
                    trans_Qty = s.Qty
                    if StockRate.objects.filter(CompanyID=CompanyID, BranchID=BranchID, StockRateID=trans_StockRateID).exists():
                        rate_ins = StockRate.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, StockRateID=trans_StockRateID)
                        rate_ins.Qty = float(rate_ins.Qty) - float(trans_Qty)
                        rate_ins.save()
                    s.IsActive = False
                    s.save()

            if PurchaseReturnDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PurchaseReturnMasterID=PurchaseReturnMasterID).exists():
                sale_ins = PurchaseReturnDetails.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, PurchaseReturnMasterID=PurchaseReturnMasterID)
                for i in sale_ins:
                    BatchCode = i.BatchCode
                    Qty = i.Qty
                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
                        batch_ins = Batch.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                        StockOut = batch_ins.StockOut
                        batch_ins.StockOut = float(StockOut) - float(Qty)
                        batch_ins.save()

            purchaseReturnMaster_instance.VoucherDate = VoucherDate
            purchaseReturnMaster_instance.RefferenceBillNo = RefferenceBillNo
            purchaseReturnMaster_instance.RefferenceBillDate = RefferenceBillDate
            purchaseReturnMaster_instance.VenderInvoiceDate = VenderInvoiceDate
            purchaseReturnMaster_instance.CreditPeriod = CreditPeriod
            purchaseReturnMaster_instance.LedgerID = LedgerID
            purchaseReturnMaster_instance.PriceCategoryID = PriceCategoryID
            purchaseReturnMaster_instance.EmployeeID = EmployeeID
            purchaseReturnMaster_instance.PurchaseAccount = PurchaseAccount
            purchaseReturnMaster_instance.DeliveryMasterID = DeliveryMasterID
            purchaseReturnMaster_instance.OrderMasterID = OrderMasterID
            purchaseReturnMaster_instance.CustomerName = CustomerName
            purchaseReturnMaster_instance.Address1 = Address1
            purchaseReturnMaster_instance.Address2 = Address2
            purchaseReturnMaster_instance.Address3 = Address3
            purchaseReturnMaster_instance.Notes = Notes
            purchaseReturnMaster_instance.FinacialYearID = FinacialYearID
            purchaseReturnMaster_instance.TotalTax = TotalTax
            purchaseReturnMaster_instance.NetTotal = NetTotal
            purchaseReturnMaster_instance.AdditionalCost = AdditionalCost
            purchaseReturnMaster_instance.GrandTotal = GrandTotal
            purchaseReturnMaster_instance.RoundOff = RoundOff
            purchaseReturnMaster_instance.WarehouseID = WarehouseID
            purchaseReturnMaster_instance.IsActive = IsActive
            purchaseReturnMaster_instance.TotalGrossAmt = TotalGrossAmt
            purchaseReturnMaster_instance.Action = Action
            purchaseReturnMaster_instance.CreatedUserID = CreatedUserID
            purchaseReturnMaster_instance.UpdatedDate = today
            purchaseReturnMaster_instance.TaxID = TaxID
            purchaseReturnMaster_instance.TaxType = TaxType
            purchaseReturnMaster_instance.VATAmount = VATAmount
            purchaseReturnMaster_instance.SGSTAmount = SGSTAmount
            purchaseReturnMaster_instance.CGSTAmount = CGSTAmount
            purchaseReturnMaster_instance.IGSTAmount = IGSTAmount
            purchaseReturnMaster_instance.TAX1Amount = TAX1Amount
            purchaseReturnMaster_instance.TAX2Amount = TAX2Amount
            purchaseReturnMaster_instance.TAX3Amount = TAX3Amount
            purchaseReturnMaster_instance.AddlDiscPercent = AddlDiscPercent
            purchaseReturnMaster_instance.AddlDiscAmt = AddlDiscAmt
            purchaseReturnMaster_instance.TotalDiscount = TotalDiscount
            purchaseReturnMaster_instance.BillDiscPercent = BillDiscPercent
            purchaseReturnMaster_instance.BillDiscAmt = BillDiscAmt
            purchaseReturnMaster_instance.TotalTaxableAmount = TotalTaxableAmount
            purchaseReturnMaster_instance.save()

            VoucherType = "PR"

            # new posting starting from here
            LedgerPostingID = get_auto_LedgerPostid(
                LedgerPosting, BranchID, CompanyID)

            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=VoucherDate,
                VoucherMasterID=PurchaseReturnMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=PurchaseAccount,
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
                Date=VoucherDate,
                VoucherMasterID=PurchaseReturnMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=PurchaseAccount,
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
                Date=VoucherDate,
                VoucherMasterID=PurchaseReturnMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                RelatedLedgerID=PurchaseAccount,
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
                VoucherMasterID=PurchaseReturnMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                RelatedLedgerID=PurchaseAccount,
                Debit=GrandTotal,
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
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=54,
                        RelatedLedgerID=PurchaseAccount,
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
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=54,
                        RelatedLedgerID=PurchaseAccount,
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
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=54,
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
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=54,
                        Debit=VATAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

            elif TaxType == 'GST Intra-state B2B':
                if float(CGSTAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=36,
                        RelatedLedgerID=PurchaseAccount,
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
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=36,
                        RelatedLedgerID=PurchaseAccount,
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
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=36,
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
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=36,
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
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=42,
                        RelatedLedgerID=PurchaseAccount,
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
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=42,
                        RelatedLedgerID=PurchaseAccount,
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
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=42,
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
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=42,
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
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=39,
                        RelatedLedgerID=PurchaseAccount,
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
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=39,
                        RelatedLedgerID=PurchaseAccount,
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
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=39,
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
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=39,
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
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=45,
                        RelatedLedgerID=PurchaseAccount,
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
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=45,
                        RelatedLedgerID=PurchaseAccount,
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
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=45,
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
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=45,
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
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=48,
                        RelatedLedgerID=PurchaseAccount,
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
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=48,
                        RelatedLedgerID=PurchaseAccount,
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
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=48,
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
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=48,
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
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=51,
                        RelatedLedgerID=PurchaseAccount,
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
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=51,
                        RelatedLedgerID=PurchaseAccount,
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
                        Date=VoucherDate,
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=51,
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
                        VoucherMasterID=PurchaseReturnMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PurchaseAccount,
                        RelatedLedgerID=51,
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
                    Date=VoucherDate,
                    VoucherMasterID=PurchaseReturnMasterID,
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
                    Date=VoucherDate,
                    VoucherMasterID=PurchaseReturnMasterID,
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

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=PurchaseReturnMasterID,
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
                    Date=VoucherDate,
                    VoucherMasterID=PurchaseReturnMasterID,
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

            if float(RoundOff) < 0:

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                RoundOff = abs(float(RoundOff))

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=PurchaseReturnMasterID,
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
                    Date=VoucherDate,
                    VoucherMasterID=PurchaseReturnMasterID,
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

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=PurchaseReturnMasterID,
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
                    Date=VoucherDate,
                    VoucherMasterID=PurchaseReturnMasterID,
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

            if float(TotalDiscount) > 0:

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=VoucherDate,
                    VoucherMasterID=PurchaseReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=83,
                    RelatedLedgerID=PurchaseAccount,
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
                    VoucherMasterID=PurchaseReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=83,
                    RelatedLedgerID=PurchaseAccount,
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
                    Date=VoucherDate,
                    VoucherMasterID=PurchaseReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
                    RelatedLedgerID=83,
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
                    VoucherMasterID=PurchaseReturnMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PurchaseAccount,
                    RelatedLedgerID=83,
                    Credit=TotalDiscount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

            # new posting end here

            # deleted_datas = data["deleted_data"]
            # if deleted_datas:
            #     for deleted_Data in deleted_datas:
            #         PurchaseReturnDetailsID = deleted_Data['PurchaseReturnDetailsID']
            #         pk = deleted_Data['unq_id']

            #         if not pk == '':
            #             if PurchaseReturnDetails.objects.filter(CompanyID=CompanyID,pk=pk).exists():
            #                 deleted_detail = PurchaseReturnDetails.objects.filter(CompanyID=CompanyID,pk=pk)
            #                 deleted_detail.delete()

            #             stockTrans_instance = None
            #             if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=PurchaseReturnDetailsID,MasterID=PurchaseReturnMasterID,BranchID=BranchID,VoucherType=VoucherType,IsActive=True).exists():
            #                 stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID,DetailID=PurchaseReturnDetailsID,MasterID=PurchaseReturnMasterID,BranchID=BranchID,VoucherType=VoucherType,IsActive=True)
            #                 qty_in_stockTrans = stockTrans_instance.Qty
            #                 StockRateID = stockTrans_instance.StockRateID
            #                 stockTrans_instance.IsActive = False
            #                 stockTrans_instance.save()

            #                 stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,StockRateID=StockRateID,BranchID=BranchID,WareHouseID=WarehouseID)
            #                 stockRate_instance.Qty = float(stockRate_instance.Qty) - float(qty_in_stockTrans)
            #                 stockRate_instance.save()

            deleted_datas = data["deleted_data"]
            if deleted_datas:
                for deleted_Data in deleted_datas:
                    deleted_pk = deleted_Data['unq_id']
                    PurchaseReturnDetailsID_Deleted = deleted_Data['PurchaseReturnDetailsID']
                    ProductID_Deleted = deleted_Data['ProductID']
                    PriceListID_Deleted = deleted_Data['PriceListID']
                    Rate_Deleted = deleted_Data['Rate']
                    PurchaseReturnMasterID_Deleted = deleted_Data['PurchaseReturnMasterID']
                    WarehouseID_Deleted = deleted_Data['WarehouseID']

                    if PriceList.objects.filter(CompanyID=CompanyID, ProductID=ProductID_Deleted, DefaultUnit=True).exists():
                        priceList = PriceList.objects.get(
                            CompanyID=CompanyID, ProductID=ProductID_Deleted, DefaultUnit=True)
                        MultiFactor = priceList.MultiFactor
                        Cost = float(Rate_Deleted) / float(MultiFactor)
                        Ct = round(Cost, 4)
                        Cost_Deleted = str(Ct)

                        if not deleted_pk == '' or not deleted_pk == 0:
                            if PurchaseReturnDetails.objects.filter(CompanyID=CompanyID, pk=deleted_pk).exists():
                                deleted_detail = PurchaseReturnDetails.objects.filter(
                                    CompanyID=CompanyID, pk=deleted_pk)
                                deleted_detail.delete()

                                # if StockRate.objects.filter(CompanyID=CompanyID,ProductID=ProductID_Deleted,PriceListID=PriceListID_Deleted,Cost=Cost_Deleted,WareHouseID=WarehouseID).exists():
                                #     stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,ProductID=ProductID_Deleted,PriceListID=PriceListID_Deleted,Cost=Cost_Deleted,WareHouseID=WarehouseID)
                                #     StockRateID = stockRate_instance.StockRateID
                                #     if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=PurchaseReturnDetailsID_Deleted,MasterID=PurchaseReturnMasterID_Deleted,BranchID=BranchID,
                                #         VoucherType=VoucherType,IsActive=True,StockRateID=StockRateID).exists():
                                #         stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID,DetailID=PurchaseReturnDetailsID_Deleted,MasterID=PurchaseReturnMasterID_Deleted,BranchID=BranchID,
                                #             VoucherType=VoucherType,IsActive=True,StockRateID=StockRateID)
                                #         qty_in_stockTrans = stockTrans_instance.Qty
                                #         stockRate_instance.Qty = float(stockRate_instance.Qty) - float(qty_in_stockTrans)
                                #         stockRate_instance.save()
                                #         stockTrans_instance.IsActive = False
                                #         stockTrans_instance.save()

                                if StockTrans.objects.filter(CompanyID=CompanyID, DetailID=PurchaseReturnDetailsID_Deleted, MasterID=PurchaseReturnMasterID_Deleted, BranchID=BranchID, VoucherType=VoucherType, IsActive=True).exists():
                                    stockTrans_instance = StockTrans.objects.filter(
                                        CompanyID=CompanyID, DetailID=PurchaseReturnDetailsID_Deleted, MasterID=PurchaseReturnMasterID_Deleted, BranchID=BranchID, VoucherType=VoucherType, IsActive=True)
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

            purchaseReturnDetails = data["PurchaseReturnDetails"]

            for purchaseReturnDetail in purchaseReturnDetails:

                # PurchaseReturnMasterID = serialized.data['PurchaseReturnMasterID']
                ProductID = purchaseReturnDetail['ProductID']
                if ProductID:
                    pk = purchaseReturnDetail['unq_id']
                    detailID = purchaseReturnDetail['detailID']
                    DeliveryDetailsID = purchaseReturnDetail['DeliveryDetailsID']
                    OrderDetailsID = purchaseReturnDetail['OrderDetailsID']
                    Qty_detail = purchaseReturnDetail['Qty']
                    PriceListID = purchaseReturnDetail['PriceListID']
                    FreeQty = purchaseReturnDetail['FreeQty']

                    # UnitPrice = purchaseReturnDetail['UnitPrice']
                    # InclusivePrice = purchaseReturnDetail['InclusivePrice']
                    # RateWithTax = purchaseReturnDetail['RateWithTax']
                    # CostPerPrice = purchaseReturnDetail['CostPerPrice']
                    # DiscountPerc = purchaseReturnDetail['DiscountPerc']
                    # DiscountAmount = purchaseReturnDetail['DiscountAmount']
                    # GrossAmount = purchaseReturnDetail['GrossAmount']
                    # TaxableAmount = purchaseReturnDetail['TaxableAmount']
                    # VATPerc = purchaseReturnDetail['VATPerc']
                    # VATAmount = purchaseReturnDetail['VATAmount']
                    # SGSTPerc = purchaseReturnDetail['SGSTPerc']
                    # SGSTAmount = purchaseReturnDetail['SGSTAmount']
                    # CGSTPerc = purchaseReturnDetail['CGSTPerc']
                    # CGSTAmount = purchaseReturnDetail['CGSTAmount']
                    # IGSTPerc = purchaseReturnDetail['IGSTPerc']
                    # IGSTAmount = purchaseReturnDetail['IGSTAmount']
                    # NetAmount = purchaseReturnDetail['NetAmount']

                    # AddlDiscPerc = purchaseReturnDetail['AddlDiscPerc']
                    # AddlDiscAmt = purchaseReturnDetail['AddlDiscAmt']
                    # TAX1Perc = purchaseReturnDetail['TAX1Perc']
                    # TAX1Amount = purchaseReturnDetail['TAX1Amount']
                    # TAX2Perc = purchaseReturnDetail['TAX2Perc']
                    # TAX2Amount = purchaseReturnDetail['TAX2Amount']
                    # TAX3Perc = purchaseReturnDetail['TAX3Perc']
                    # TAX3Amount = purchaseReturnDetail['TAX3Amount']

                    DiscountPerc = float(purchaseReturnDetail['DiscountPerc'])
                    DiscountAmount = float(
                        purchaseReturnDetail['DiscountAmount'])
                    GrossAmount = float(purchaseReturnDetail['GrossAmount'])
                    TaxableAmount = float(
                        purchaseReturnDetail['TaxableAmount'])
                    VATPerc = float(purchaseReturnDetail['VATPerc'])
                    VATAmount = float(purchaseReturnDetail['VATAmount'])
                    SGSTPerc = float(purchaseReturnDetail['SGSTPerc'])
                    SGSTAmount = float(purchaseReturnDetail['SGSTAmount'])
                    CGSTPerc = float(purchaseReturnDetail['CGSTPerc'])
                    CGSTAmount = float(purchaseReturnDetail['CGSTAmount'])
                    IGSTPerc = float(purchaseReturnDetail['IGSTPerc'])
                    IGSTAmount = float(purchaseReturnDetail['IGSTAmount'])
                    NetAmount = float(purchaseReturnDetail['NetAmount'])
                    RateWithTax = float(purchaseReturnDetail['RateWithTax'])
                    CostPerPrice = float(purchaseReturnDetail['CostPerPrice'])

                    UnitPrice = float(purchaseReturnDetail['UnitPrice'])
                    InclusivePrice = float(
                        purchaseReturnDetail['InclusivePrice'])
                    AddlDiscPerc = float(purchaseReturnDetail['AddlDiscPerc'])
                    AddlDiscAmt = float(purchaseReturnDetail['AddlDiscAmt'])
                    TAX1Perc = float(purchaseReturnDetail['TAX1Perc'])
                    TAX1Amount = float(purchaseReturnDetail['TAX1Amount'])
                    TAX2Perc = float(purchaseReturnDetail['TAX2Perc'])
                    TAX2Amount = float(purchaseReturnDetail['TAX2Amount'])
                    TAX3Perc = float(purchaseReturnDetail['TAX3Perc'])
                    TAX3Amount = float(purchaseReturnDetail['TAX3Amount'])

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
                    # RateWithTax = round(RateWithTax, PriceRounding)
                    # CostPerPrice = round(CostPerPrice, PriceRounding)

                    # UnitPrice = round(UnitPrice, PriceRounding)
                    # InclusivePrice = round(InclusivePrice, PriceRounding)
                    # AddlDiscPerc = round(AddlDiscPerc, PriceRounding)
                    # AddlDiscAmt = round(AddlDiscAmt, PriceRounding)
                    # TAX1Perc = round(TAX1Perc, PriceRounding)

                    # TAX1Amount = round(TAX1Amount, PriceRounding)
                    # TAX2Perc = round(TAX2Perc, PriceRounding)
                    # TAX2Amount = round(TAX2Amount, PriceRounding)
                    # TAX3Perc = round(TAX3Perc, PriceRounding)
                    # TAX3Amount = round(TAX3Amount, PriceRounding)

                    try:
                        BatchCode = purchaseReturnDetail['BatchCode']
                    except:
                        BatchCode = 0
                    try:
                        is_inclusive = purchaseReturnDetail['is_inclusive']
                    except:
                        is_inclusive = False

                    if is_inclusive == True:
                        Batch_purchasePrice = InclusivePrice
                    else:
                        Batch_purchasePrice = UnitPrice

                    product_is_Service = Product.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID).is_Service

                    MultiFactor = PriceList.objects.get(
                        CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor

                    qty_batch = float(FreeQty) + float(Qty_detail)
                    Qty_batch = float(MultiFactor) * float(qty_batch)
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
                            SalesPrice = pri_ins.SalesPrice

                            if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                                if check_BatchCriteria == "PurchasePrice":
                                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PurchasePrice=Batch_purchasePrice).exists():
                                        batch_ins = Batch.objects.filter(
                                            CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PurchasePrice=Batch_purchasePrice).last()
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
                                            PurchasePrice=Batch_purchasePrice,
                                            SalesPrice=SalesPrice,
                                            PriceListID=PriceListID,
                                            ProductID=ProductID,
                                            WareHouseID=WarehouseID,
                                            CreatedDate=today,
                                            UpdatedDate=today,
                                            CreatedUserID=CreatedUserID,
                                        )
                                elif check_BatchCriteria == "PurchasePriceAndExpiryDate":
                                    if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PurchasePrice=Batch_purchasePrice, ExpiryDate=ExpiryDate).exists():
                                        batch_ins = Batch.objects.filter(
                                            CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID, PurchasePrice=Batch_purchasePrice, ExpiryDate=ExpiryDate).last()
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
                                            PurchasePrice=Batch_purchasePrice,
                                            SalesPrice=SalesPrice,
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
                                        PurchasePrice=Batch_purchasePrice,
                                        SalesPrice=SalesPrice,
                                        PriceListID=PriceListID,
                                        ProductID=ProductID,
                                        WareHouseID=WarehouseID,
                                        CreatedDate=today,
                                        UpdatedDate=today,
                                        CreatedUserID=CreatedUserID,
                                    )

                    # priceList = PriceList.objects.get(CompanyID=CompanyID,ProductID=ProductID,DefaultUnit=True)

                    # PriceListID_DefUnit = priceList.PriceListID
                    # MultiFactor = priceList.MultiFactor

                    # MultiFactor = PriceList.objects.get(
                    #     CompanyID=CompanyID, PriceListID=PriceListID, BranchID=BranchID).MultiFactor
                    PriceListID_DefUnit = PriceList.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID, DefaultUnit=True, BranchID=BranchID).PriceListID

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

                    PurchaseReturnDetailsID = get_auto_id(
                        PurchaseReturnDetails, BranchID, CompanyID)
                    StockPostingID = get_auto_stockPostid(
                        StockPosting, BranchID, CompanyID)

                    if detailID == 0:
                        purchaseReturnDetail_instance = PurchaseReturnDetails.objects.get(
                            CompanyID=CompanyID, pk=pk)

                        PurchaseReturnDetailsID = purchaseReturnDetail_instance.PurchaseReturnDetailsID

                        log_instance = PurchaseReturnDetails_Log.objects.create(
                            TransactionID=PurchaseReturnDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            PurchaseReturnMasterID=PurchaseReturnMasterID,
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
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            AddlDiscPerc=AddlDiscPerc,
                            AddlDiscAmt=AddlDiscAmt,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            CompanyID=CompanyID,
                            BatchCode=BatchCode
                        )

                        purchaseReturnDetail_instance.DeliveryDetailsID = DeliveryDetailsID
                        purchaseReturnDetail_instance.OrderDetailsID = OrderDetailsID
                        purchaseReturnDetail_instance.ProductID = ProductID
                        purchaseReturnDetail_instance.Qty = Qty_detail
                        purchaseReturnDetail_instance.FreeQty = FreeQty
                        purchaseReturnDetail_instance.UnitPrice = UnitPrice
                        purchaseReturnDetail_instance.InclusivePrice = InclusivePrice
                        purchaseReturnDetail_instance.RateWithTax = RateWithTax
                        purchaseReturnDetail_instance.CostPerPrice = CostPerPrice
                        purchaseReturnDetail_instance.PriceListID = PriceListID
                        purchaseReturnDetail_instance.DiscountPerc = DiscountPerc
                        purchaseReturnDetail_instance.DiscountAmount = DiscountAmount
                        purchaseReturnDetail_instance.GrossAmount = GrossAmount
                        purchaseReturnDetail_instance.TaxableAmount = TaxableAmount
                        purchaseReturnDetail_instance.VATPerc = VATPerc
                        purchaseReturnDetail_instance.VATAmount = VATAmount
                        purchaseReturnDetail_instance.SGSTPerc = SGSTPerc
                        purchaseReturnDetail_instance.SGSTAmount = SGSTAmount
                        purchaseReturnDetail_instance.CGSTPerc = CGSTPerc
                        purchaseReturnDetail_instance.CGSTAmount = CGSTAmount
                        purchaseReturnDetail_instance.IGSTPerc = IGSTPerc
                        purchaseReturnDetail_instance.IGSTAmount = IGSTAmount
                        purchaseReturnDetail_instance.NetAmount = NetAmount
                        purchaseReturnDetail_instance.Action = Action
                        purchaseReturnDetail_instance.UpdatedDate = today
                        purchaseReturnDetail_instance.CreatedUserID = CreatedUserID
                        purchaseReturnDetail_instance.AddlDiscPerc = AddlDiscPerc
                        purchaseReturnDetail_instance.AddlDiscAmt = AddlDiscAmt
                        purchaseReturnDetail_instance.TAX1Perc = TAX1Perc
                        purchaseReturnDetail_instance.TAX1Amount = TAX1Amount
                        purchaseReturnDetail_instance.TAX2Perc = TAX2Perc
                        purchaseReturnDetail_instance.TAX2Amount = TAX2Amount
                        purchaseReturnDetail_instance.TAX3Perc = TAX3Perc
                        purchaseReturnDetail_instance.TAX3Amount = TAX3Amount
                        purchaseReturnDetail_instance.BatchCode = BatchCode
                        purchaseReturnDetail_instance.LogID = log_instance.ID
                        purchaseReturnDetail_instance.save()

                        # StockPostingID = get_auto_stockPostid(
                        #     StockPosting, BranchID, CompanyID)
                        # StockPosting.objects.create(
                        #     StockPostingID=StockPostingID,
                        #     BranchID=BranchID,
                        #     Action=Action,
                        #     Date=VoucherDate,
                        #     VoucherMasterID=PurchaseReturnMasterID,
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
                        #     Date=VoucherDate,
                        #     VoucherMasterID=PurchaseReturnMasterID,
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

                        log_instance = PurchaseReturnDetails_Log.objects.create(
                            TransactionID=PurchaseReturnDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            PurchaseReturnMasterID=PurchaseReturnMasterID,
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
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            AddlDiscPerc=AddlDiscPerc,
                            AddlDiscAmt=AddlDiscAmt,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            CompanyID=CompanyID,
                            BatchCode=BatchCode
                        )

                        PurchaseReturnDetails.objects.create(
                            PurchaseReturnDetailsID=PurchaseReturnDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            PurchaseReturnMasterID=PurchaseReturnMasterID,
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
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            AddlDiscPerc=AddlDiscPerc,
                            AddlDiscAmt=AddlDiscAmt,
                            TAX1Perc=TAX1Perc,
                            TAX1Amount=TAX1Amount,
                            TAX2Perc=TAX2Perc,
                            TAX2Amount=TAX2Amount,
                            TAX3Perc=TAX3Perc,
                            TAX3Amount=TAX3Amount,
                            CompanyID=CompanyID,
                            BatchCode=BatchCode,
                            LogID=log_instance.ID
                        )

                        # StockPostingID = get_auto_stockPostid(
                        #     StockPosting, BranchID, CompanyID)
                        # StockPosting.objects.create(
                        #     StockPostingID=StockPostingID,
                        #     BranchID=BranchID,
                        #     Action=Action,
                        #     Date=VoucherDate,
                        #     VoucherMasterID=PurchaseReturnMasterID,
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
                        #     Date=VoucherDate,
                        #     VoucherMasterID=PurchaseReturnMasterID,
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
                                                                       VoucherMasterID=PurchaseReturnMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit).exists():
                                            stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                                          VoucherMasterID=PurchaseReturnMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit)
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
                                                Date=VoucherDate,
                                                VoucherMasterID=PurchaseReturnMasterID,
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
                                                Date=VoucherDate,
                                                VoucherMasterID=PurchaseReturnMasterID,
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

                                        if StockTrans.objects.filter(StockRateID=StockRateID, DetailID=PurchaseReturnDetailsID, MasterID=PurchaseReturnMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                                            stockTra_in = StockTrans.objects.filter(
                                                StockRateID=StockRateID, DetailID=PurchaseReturnDetailsID, MasterID=PurchaseReturnMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
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
                                                DetailID=PurchaseReturnDetailsID,
                                                MasterID=PurchaseReturnMasterID,
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
                                                                           VoucherMasterID=PurchaseReturnMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit).exists():
                                                stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                                              VoucherMasterID=PurchaseReturnMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit)
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
                                                    Date=VoucherDate,
                                                    VoucherMasterID=PurchaseReturnMasterID,
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
                                                    Date=VoucherDate,
                                                    VoucherMasterID=PurchaseReturnMasterID,
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
                                            if StockTrans.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, DetailID=PurchaseReturnDetailsID, MasterID=PurchaseReturnMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                                                stockTra_in = StockTrans.objects.filter(
                                                    CompanyID=CompanyID, StockRateID=StockRateID, DetailID=PurchaseReturnDetailsID, MasterID=PurchaseReturnMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
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
                                                    DetailID=PurchaseReturnDetailsID,
                                                    MasterID=PurchaseReturnMasterID,
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
                                                                           VoucherMasterID=PurchaseReturnMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit).exists():
                                                stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                                              VoucherMasterID=PurchaseReturnMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit)
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
                                                    Date=VoucherDate,
                                                    VoucherMasterID=PurchaseReturnMasterID,
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
                                                    Date=VoucherDate,
                                                    VoucherMasterID=PurchaseReturnMasterID,
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

                                            if StockTrans.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, DetailID=PurchaseReturnDetailsID, MasterID=PurchaseReturnMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                                                stockTra_in = StockTrans.objects.filter(
                                                    CompanyID=CompanyID, StockRateID=StockRateID, DetailID=PurchaseReturnDetailsID, MasterID=PurchaseReturnMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
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
                                                    DetailID=PurchaseReturnDetailsID,
                                                    MasterID=PurchaseReturnMasterID,
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
                                                                       VoucherMasterID=PurchaseReturnMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit).exists():
                                            stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                                          VoucherMasterID=PurchaseReturnMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit)
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
                                                Date=VoucherDate,
                                                VoucherMasterID=PurchaseReturnMasterID,
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
                                                Date=VoucherDate,
                                                VoucherMasterID=PurchaseReturnMasterID,
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

                                        if StockTrans.objects.filter(CompanyID=CompanyID, StockRateID=StockRateID, DetailID=PurchaseReturnDetailsID, MasterID=PurchaseReturnMasterID, VoucherType=VoucherType, BranchID=BranchID).exists():
                                            stockTra_in = StockTrans.objects.filter(
                                                CompanyID=CompanyID, StockRateID=StockRateID, DetailID=PurchaseReturnDetailsID, MasterID=PurchaseReturnMasterID, VoucherType=VoucherType, BranchID=BranchID).first()
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
                                                DetailID=PurchaseReturnDetailsID,
                                                MasterID=PurchaseReturnMasterID,
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
                                                                       VoucherMasterID=PurchaseReturnMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit).exists():
                                            stockPost_instance = StockPosting.objects.get(CompanyID=CompanyID, WareHouseID=WarehouseID, ProductID=ProductID, BranchID=BranchID,
                                                                                          VoucherMasterID=PurchaseReturnMasterID, VoucherType=VoucherType, Rate=stock_post_cost, PriceListID=PriceListID_DefUnit)
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
                                                Date=VoucherDate,
                                                VoucherMasterID=PurchaseReturnMasterID,
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
                                                Date=VoucherDate,
                                                VoucherMasterID=PurchaseReturnMasterID,
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
                                                                         DetailID=PurchaseReturnDetailsID,
                                                                         MasterID=PurchaseReturnMasterID,
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
                                                DetailID=PurchaseReturnDetailsID,
                                                MasterID=PurchaseReturnMasterID,
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
                                Date=VoucherDate,
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
                                Date=VoucherDate,
                                VoucherMasterID=PurchaseReturnMasterID,
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
                                Date=VoucherDate,
                                VoucherMasterID=PurchaseReturnMasterID,
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
                                DetailID=PurchaseReturnDetailsID,
                                MasterID=PurchaseReturnMasterID,
                                Qty=Qty,
                                IsActive=IsActive,
                                CompanyID=CompanyID,
                            )

            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'PurchaseReturns',
            #              'Edit', 'Purchase Returns Updated Successfully.', 'Purchase Returns Updated Successfully')

            response_data = {
                "StatusCode": 6000,
                "message": "Purchase Return Updated Successfully!!!",
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

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Purchase Return',
                     'Edit', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def list_purchaseReturnMaster(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']

        if PurchaseReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():

            instances = PurchaseReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

            serialized = PurchaseReturnMasterRestSerializer(instances, many=True, context={"CompanyID": CompanyID,
                                                                                           "PriceRounding": PriceRounding})

            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'PurchaseReturns', 'List',
            #              'Purchase Returns List Viewed Successfully.', 'Purchase Returns List Viewed Successfully.')
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'PurchaseReturns', 'List',
            #              'Purchase Returns List Viewed Failed.', 'Purchase Return not found under this branch.')

            response_data = {
                "StatusCode": 6001,
                "message": "Purchase Return Master not found in this branch."
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
def purchase_return_pagination(request):
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
            purchase_return_object = PurchaseReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

            purchase_return_sort_pagination = list_pagination(
                purchase_return_object,
                items_per_page,
                page_number
            )
            purchase_return_serializer = PurchaseReturn1MasterRestSerializer(
                purchase_return_sort_pagination,
                many=True,
                context={"request": request, "CompanyID": CompanyID,
                         "PriceRounding": PriceRounding}
            )
            data = purchase_return_serializer.data
            if not data == None:
                response_data = {
                    "StatusCode": 6000,
                    "data": data,
                    "count": len(purchase_return_object)
                }
            else:
                response_data = {
                    "StatusCode": 6001
                }

            return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def purchaseReturnMaster(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']

    if PurchaseReturnMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = PurchaseReturnMaster.objects.get(CompanyID=CompanyID, pk=pk)
        serialized = PurchaseReturnMasterRestSerializer(instance, context={"CompanyID": CompanyID,
                                                                           "PriceRounding": PriceRounding})

        #request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'PurchaseReturns', 'View',
        #              'Purchase Returns Single Viewed Successfully.', 'Purchase Returns Single Viewed Successfully.')
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        #request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'PurchaseReturns',
        #              'View', 'Purchase Returns Single Viewed Failed.', 'Purchase Return Not Found!')
        response_data = {
            "StatusCode": 6001,
            "message": "Purchase Return Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_purchaseReturnMaster(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    instance = None
    if PurchaseReturnMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = PurchaseReturnMaster.objects.get(CompanyID=CompanyID, pk=pk)

        PurchaseReturnMasterID = instance.PurchaseReturnMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        VoucherDate = instance.VoucherDate
        RefferenceBillNo = instance.RefferenceBillNo
        RefferenceBillDate = instance.RefferenceBillDate
        VenderInvoiceDate = instance.VenderInvoiceDate
        CreditPeriod = instance.CreditPeriod
        LedgerID = instance.LedgerID
        PriceCategoryID = instance.PriceCategoryID
        EmployeeID = instance.EmployeeID
        PurchaseAccount = instance.PurchaseAccount
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
        AddlDiscPercent = instance.AddlDiscPercent
        AddlDiscAmt = instance.AddlDiscAmt
        TotalDiscount = instance.TotalDiscount
        BillDiscPercent = instance.BillDiscPercent
        BillDiscAmt = instance.BillDiscAmt
        Action = "D"

        PurchaseReturnMaster_Log.objects.create(
            TransactionID=PurchaseReturnMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            VoucherDate=VoucherDate,
            RefferenceBillNo=RefferenceBillNo,
            RefferenceBillDate=RefferenceBillDate,
            VenderInvoiceDate=VenderInvoiceDate,
            CreditPeriod=CreditPeriod,
            LedgerID=LedgerID,
            PriceCategoryID=PriceCategoryID,
            EmployeeID=EmployeeID,
            PurchaseAccount=PurchaseAccount,
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
            WarehouseID=WarehouseID,
            IsActive=IsActive,
            CreatedUserID=CreatedUserID,
            Action=Action,
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
        )

        if LedgerPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PurchaseReturnMasterID, BranchID=BranchID, VoucherType="PR").exists():

            ledgerPostInstances = LedgerPosting.objects.filter(
                CompanyID=CompanyID, VoucherMasterID=PurchaseReturnMasterID, BranchID=BranchID, VoucherType="PR")

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
                    Date=VoucherDate,
                    VoucherMasterID=PurchaseReturnMasterID,
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

        if StockPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PurchaseReturnMasterID, BranchID=BranchID, VoucherType="PR").exists():

            stockPostingInstances = StockPosting.objects.filter(
                CompanyID=CompanyID, VoucherMasterID=PurchaseReturnMasterID, BranchID=BranchID, VoucherType="PR")

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
                    Date=VoucherDate,
                    VoucherMasterID=PurchaseReturnMasterID,
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

        detail_instances = PurchaseReturnDetails.objects.filter(
            CompanyID=CompanyID, PurchaseReturnMasterID=PurchaseReturnMasterID)

        for detail_instance in detail_instances:

            PurchaseReturnDetailsID = detail_instance.PurchaseReturnDetailsID
            BranchID = detail_instance.BranchID
            PurchaseReturnMasterID = detail_instance.PurchaseReturnMasterID
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

            AddlDiscPerc = detail_instance.AddlDiscPerc
            AddlDiscAmt = detail_instance.AddlDiscAmt
            TAX1Perc = detail_instance.TAX1Perc
            TAX1Amount = detail_instance.TAX1Amount
            TAX2Perc = detail_instance.TAX2Perc
            TAX2Amount = detail_instance.TAX2Amount
            TAX3Perc = detail_instance.TAX3Perc
            TAX3Amount = detail_instance.TAX3Amount

            BatchCode = detail_instance.BatchCode

            if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode).exists():
                batch_ins = Batch.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, BatchCode=BatchCode)
                StockOut = batch_ins.StockOut
                batch_ins.StockOut = float(StockOut) - float(Qty)
                batch_ins.save()

            PurchaseReturnDetails_Log.objects.create(
                TransactionID=PurchaseReturnDetailsID,
                BranchID=BranchID,
                Action=Action,
                PurchaseReturnMasterID=PurchaseReturnMasterID,
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
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                AddlDiscPerc=AddlDiscPerc,
                AddlDiscAmt=AddlDiscAmt,
                TAX1Perc=TAX1Perc,
                TAX1Amount=TAX1Amount,
                TAX2Perc=TAX2Perc,
                TAX2Amount=TAX2Amount,
                TAX3Perc=TAX3Perc,
                TAX3Amount=TAX3Amount,
                CompanyID=CompanyID,
                BatchCode=BatchCode
            )

            if StockTrans.objects.filter(CompanyID=CompanyID, DetailID=PurchaseReturnDetailsID, MasterID=PurchaseReturnMasterID, BranchID=BranchID, VoucherType="PR", IsActive=True).exists():
                stockTrans_instances = StockTrans.objects.filter(
                    CompanyID=CompanyID, DetailID=PurchaseReturnDetailsID, MasterID=PurchaseReturnMasterID, BranchID=BranchID, VoucherType="PR", IsActive=True)

                for i in stockTrans_instances:
                    stockRateID = i.StockRateID
                    i.IsActive = False
                    i.save()

                    stockRate_instance = StockRate.objects.get(
                        CompanyID=CompanyID, StockRateID=stockRateID, BranchID=BranchID)
                    stockRate_instance.Qty = float(
                        stockRate_instance.Qty) + float(i.Qty)
                    stockRate_instance.save()
            # if StockTrans.objects.filter(CompanyID=CompanyID,DetailID=PurchaseReturnDetailsID,MasterID=PurchaseReturnMasterID,BranchID=BranchID,VoucherType="PR").exists():
            #     stockTrans_instance = StockTrans.objects.get(CompanyID=CompanyID,DetailID=PurchaseReturnDetailsID,MasterID=PurchaseReturnMasterID,BranchID=BranchID,VoucherType="PR")

            #     stockRateID = stockTrans_instance.StockRateID
            #     stockTrans_instance.IsActive = False
            #     stockTrans_instance.save()

            #     stockRate_instance = StockRate.objects.get(CompanyID=CompanyID,StockRateID=stockRateID,BranchID=BranchID)
            #     stockRate_instance.Qty = stockTrans_instance.Qty
            #     stockRate_instance.save()

            detail_instance.delete()
        instance.delete()
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'PurchaseReturns',
                     'Delete', 'Purchase Returns Deleted Successfully.', 'Purchase Returns Deleted Successfully.')
        response_data = {
            "StatusCode": 6000,
            "title": "Success",
            "message": "Purchase Return Master Deleted Successfully!"
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'PurchaseReturns',
                     'Delete', 'Purchase Returns Deleted Failed.', 'Purchase Return Not Found.')
        response_data = {
            "StatusCode": 6001,
            "title": "Failed",
            "message": "Purchase Return Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def report_purchaseReturns(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    serialized1 = ListSerializerforReport(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']
        ToDate = serialized1.data['ToDate']

        if PurchaseReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherDate__lte=ToDate).exists():
            instances = PurchaseReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherDate__lte=ToDate)

            serialized = PurchaseReturnMasterRestSerializer(
                instances, many=True, context={"CompanyID": CompanyID})

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'PurchaseReturnsReports', 'Report',
                         'Purchase Returns Reports viewed Successfully.', 'Purchase Returns Reports viewed Successfully.')
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'PurchaseReturnsReports',
                         'Report', 'Purchase Returns Reports viewed Failed.', 'No datas under this date.')
            response_data = {
                "StatusCode": 6001,
                "message": "No data under this date!!!"
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
def search_purchaseReturns(request):
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
        if PurchaseReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instances = PurchaseReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

            if length < 3:
                if param == "VoucherNo":
                    instances = instances.filter(
                        (Q(VoucherNo__icontains=product_name)))[:10]
                elif param == "VoucherDate":
                    instances = instances.filter(
                        (Q(VoucherDate__icontains=product_name)))[:10]
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
                elif param == "VoucherDate":
                    instances = instances.filter(
                        (Q(VoucherDate__icontains=product_name)))
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

            serialized = PurchaseReturnMasterRestSerializer(instances, many=True, context={
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
def purchaseReturnRegister_report(request):
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

        if PurchaseReturnMaster.objects.filter(CompanyID=CompanyID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate).exists():
            purchaseReturnMaster_instances = PurchaseReturnMaster.objects.filter(
                CompanyID=CompanyID, VoucherDate__gte=FromDate, VoucherDate__lte=ToDate)

            if wareHouseVal > 0:
                if purchaseReturnMaster_instances.filter(WarehouseID=wareHouseVal).exists():
                    purchaseReturnMaster_instances = purchaseReturnMaster_instances.filter(
                        WarehouseID=wareHouseVal)
                else:
                    #request , company, log_type, user, source, action, message, description
                    activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Purchase Return Register Report',
                                 'Report', 'Purchase Return Register Report Viewed Failed.', 'Purchase Return is not Found in this Warehouse')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Purchase Return is not Found in this Warehouse!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
            if userVal > "0":
                UserID = UserTable.objects.get(pk=userVal).customer.user.id
                if purchaseReturnMaster_instances.filter(CreatedUserID=UserID).exists():
                    purchaseReturnMaster_instances = purchaseReturnMaster_instances.filter(
                        CreatedUserID=UserID)
                else:
                    #request , company, log_type, user, source, action, message, description
                    activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Purchase Return Register Report',
                                 'Report', 'Purchase Return Register Report Viewed Failed.', 'Purchase Return is not Found by this user')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Purchase Return is not Found by this user!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
            if branchVal > 0:
                if purchaseReturnMaster_instances.filter(BranchID=branchVal).exists():
                    purchaseReturnMaster_instances = purchaseReturnMaster_instances.filter(
                        BranchID=branchVal)
                else:
                    #request , company, log_type, user, source, action, message, description
                    activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Purchase Return Register Report',
                                 'Report', 'Purchase Return Register Report Viewed Failed.', 'Purchase Return is not Found under this Branch')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Purchase Return is not Found under this Branch!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
            if ledgerVal > 0:
                if purchaseReturnMaster_instances.filter(LedgerID=ledgerVal).exists():
                    purchaseReturnMaster_instances = purchaseReturnMaster_instances.filter(
                        LedgerID=ledgerVal)
                else:
                    #request , company, log_type, user, source, action, message, description
                    activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Purchase Return Register Report',
                                 'Report', 'Purchase Return Register Report Viewed Failed.', 'Purchase Return is not Found under this Ledger')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Purchase Return is not Found under this Ledger!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)

            masterList = []
            final_array = []
            for i in purchaseReturnMaster_instances:
                PurchaseReturnMasterID = i.PurchaseReturnMasterID
                BranchID = i.BranchID
                Date = i.VoucherDate
                InvoiceNo = i.VoucherNo

                PurchaseReturnDetail_instances = PurchaseReturnDetails.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, PurchaseReturnMasterID=PurchaseReturnMasterID)
                if produtVal > 0:
                    PurchaseReturnDetail_instances = PurchaseReturnDetail_instances.filter(
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
                                PurchaseReturnDetail_instances = PurchaseReturnDetail_instances.filter(
                                    ProductID__in=pro_ids)
                    else:
                        #request , company, log_type, user, source, action, message, description
                        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Purchase Return Register Report',
                                     'Report', 'Purchase Return Register Report Viewed Failed.', 'Purchase Return is not Found under this Category')
                        response_data = {
                            "StatusCode": 6001,
                            "message": "Purchase Return is not Found under this Category!"
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
                        PurchaseReturnDetail_instances = PurchaseReturnDetail_instances.filter(
                            ProductID__in=pro_ids)
                    else:
                        #request , company, log_type, user, source, action, message, description
                        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Purchase Return Register Report',
                                     'Report', 'Purchase Return Register Report Viewed Failed.', 'Purchase Return is not Found under this Group')
                        response_data = {
                            "StatusCode": 6001,
                            "message": "Purchase Return is not Found under this Group!"
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
                        PurchaseReturnDetail_instances = PurchaseReturnDetail_instances.filter(
                            ProductID__in=pro_ids)
                    else:
                        #request , company, log_type, user, source, action, message, description
                        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Purchase Return Register Report',
                                     'Report', 'Purchase Return Register Report Viewed Failed.', 'Purchase Return is not Found under this ProductCode')
                        response_data = {
                            "StatusCode": 6001,
                            "message": "Purchase Return is not Found under this ProductCode!"
                        }

                        return Response(response_data, status=status.HTTP_200_OK)

                elif barCodeVal:
                    if PriceList.objects.filter(Barcode=barCodeVal, CompanyID=CompanyID, BranchID=BranchID).exists():
                        ProductID = PriceList.objects.filter(
                            Barcode=barCodeVal, CompanyID=CompanyID, BranchID=BranchID).first().ProductID
                        PurchaseReturnDetail_instances = PurchaseReturnDetail_instances.filter(
                            ProductID=ProductID)
                    else:
                        #request , company, log_type, user, source, action, message, description
                        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Purchase Return Register Report',
                                     'Report', 'Purchase Return Register Report Viewed Failed.', 'Purchase Return is not Found under this Bracode')
                        response_data = {
                            "StatusCode": 6001,
                            "message": "Purchase Return is not Found under this Bracode!"
                        }

                        return Response(response_data, status=status.HTTP_200_OK)

                for s in PurchaseReturnDetail_instances:
                    print("------------------////------------------5044")
                    print(s.CostPerPrice)
                    if s.PurchaseReturnMasterID == PurchaseReturnMasterID:
                        if not PurchaseReturnMasterID in masterList:
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
                            masterList.append(PurchaseReturnMasterID)
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
                    Cost = s.CostPerPrice
                    Profit = float(NetAmount) - (float(Qty) * float(Cost))
                    print(NetAmount)
                    print(Qty)
                    print(Cost)
                    if PurchaseReturnMasterID in masterList:
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
