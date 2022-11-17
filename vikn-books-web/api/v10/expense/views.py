from brands import models as model
from api.v10.expense import serializers as serializer
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes,authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from api.v10.brands.serializers import ListSerializer
from api.v10.purchases.functions import generate_serializer_errors
from rest_framework import status
from api.v10.accountLedgers.functions import get_auto_LedgerPostid
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from main.functions import converted_float, get_BranchLedgerId_for_LedgerPosting, get_GeneralSettings, get_company, activity_log
import os
import re
import sys
from api.v10.ledgerPosting.functions import convertOrderdDict
from django.db.models import Q, Prefetch, Max
from django.db import transaction, IntegrityError
from api.v10.accountLedgers.functions import get_LedgerCode, get_auto_id as generated_ledgerID, UpdateLedgerBalance
import math
from main.functions import update_voucher_table
from django.http import HttpResponse
import xlwt
from xlwt import Workbook, XFStyle, Borders, Pattern, Font, easyxf, Alignment
from api.v10.expense.functions import get_masterID, get_detailID
from api.v10.sales.functions import get_Genrate_VoucherNo


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
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def create_expense(request):
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
            Date = data['Date']
            Supplier = data['Supplier']
            GST_Treatment = data['GST_Treatment']
            PlaceOfSupply = data['PlaceOfSupply']
            MasterInvoiceNo = data['MasterInvoiceNo']
            Notes = data['Notes']
            PaymentMode = data['PaymentMode']
            PaymentID = data['PaymentID']
            Amount = data['Amount']
            BillDiscPercent = data['BillDiscountPerc']
            BillDiscAmount = data['BillDiscountAmt']
            TotalGrossAmt = data['TotalGrossAmt']
            TotalTaxableAmount = data['TotalTaxableAmount']
            TotalDiscount = data['TotalDiscount']
            TotalTaxAmount = data['TotalTaxAmount']
            TotalNetAmount = data['TotalNetAmount']
            RoundOff = data['RoundOff']
            if not RoundOff:
                RoundOff = 0
            GrandTotal = data['GrandTotal']
            TaxInclusive = data['TaxInclusive']
            TaxType = data['TaxType']
            TaxTypeID = data['TaxTypeID']
            if TaxTypeID == "":
                TaxTypeID = 1
            TotalVATAmount = data['TotalVATAmount']
            TotalIGSTAmount = data['TotalIGSTAmount']
            TotalSGSTAmount = data['TotalSGSTAmount']
            TotalCGSTAmount = data['TotalCGSTAmount']
            TaxNo = data['TaxNo']

            IsActive = True

            VoucherType = "EX"
            # VoucherNo Updated
            try:
                PreFix = data['PreFix']
            except:
                PreFix = "EX"

            try:
                Seperator = data['Seperator']
            except:
                Seperator = ""

            try:
                InvoiceNo = data['InvoiceNo']
            except:
                InvoiceNo = 1

            Action = "A"

            Supplier = model.AccountLedger.objects.get(id=Supplier)
            Payment = None
            PaymentLedgerID = None
            if PaymentID:
                Payment = model.AccountLedger.objects.get(id=PaymentID)
                PaymentLedgerID = Payment.LedgerID
            if PlaceOfSupply:
                PlaceOfSupply = model.State.objects.get(id=PlaceOfSupply)
            else:
                PlaceOfSupply = None

            # checking voucher number already exist
            VoucherNoLow = VoucherNo.lower()
            is_voucherExist = False
            insts = model.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True

            check_VoucherNoAutoGenerate = False
            is_ExpenseOK = True

            if model.GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="VoucherNoAutoGenerate").exists():
                check_VoucherNoAutoGenerate = model.GeneralSettings.objects.get(
                    BranchID=BranchID, CompanyID=CompanyID, SettingsType="VoucherNoAutoGenerate").SettingsValue

            if is_voucherExist == True and check_VoucherNoAutoGenerate == "True":
                VoucherNo = get_Genrate_VoucherNo(
                    model.ExpenseMaster, BranchID, CompanyID, "EX")
                is_ExpenseOK = True
            elif is_voucherExist == False:
                is_ExpenseOK = True
            else:
                is_ExpenseOK = False

            if is_ExpenseOK:
                ExpenseMasterID = get_masterID(
                    model.ExpenseMaster, BranchID, CompanyID)

                update_voucher_table(
                    CompanyID, CreatedUserID, VoucherType, PreFix, Seperator, InvoiceNo)

                check_vat = get_GeneralSettings(
                    CompanyID, BranchID, "VAT"
                )
                check_vgst = get_GeneralSettings(
                    CompanyID, BranchID, "GST"
                )
                if CompanyID.is_gst:
                    GST_Treatment = model.Parties.objects.get(CompanyID=CompanyID,BranchID=BranchID,LedgerID=Supplier.LedgerID).GST_Treatment
                elif CompanyID.is_vat:
                    GST_Treatment = model.Parties.objects.get(CompanyID=CompanyID,BranchID=BranchID,LedgerID=Supplier.LedgerID).VAT_Treatment

                model.ExpenseMaster_Log.objects.create(
                    TransactionID=ExpenseMasterID,
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    Supplier=Supplier,
                    GST_Treatment=GST_Treatment,
                    PlaceOfSupply=PlaceOfSupply,
                    InvoiceNo=MasterInvoiceNo,
                    Notes=Notes,
                    PaymentMode=PaymentMode,
                    PaymentID=Payment,
                    Amount=Amount,
                    BillDiscPercent=BillDiscPercent,
                    BillDiscAmount=BillDiscAmount,
                    TotalGrossAmt=TotalGrossAmt,
                    TotalTaxableAmount=TotalTaxableAmount,
                    TotalDiscount=TotalDiscount,
                    TotalTaxAmount=TotalTaxAmount,
                    TotalNetAmount=TotalNetAmount,
                    RoundOff=RoundOff,
                    GrandTotal=GrandTotal,
                    TaxInclusive=TaxInclusive,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    TaxType=TaxType,
                    TaxTypeID=TaxTypeID,
                    TotalVATAmount=TotalVATAmount,
                    TotalIGSTAmount=TotalIGSTAmount,
                    TotalSGSTAmount=TotalSGSTAmount,
                    TotalCGSTAmount=TotalCGSTAmount,
                    TaxNo=TaxNo,
                )

                instance = model.ExpenseMaster.objects.create(
                    ExpenseMasterID=ExpenseMasterID,
                    CompanyID=CompanyID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    Date=Date,
                    Supplier=Supplier,
                    GST_Treatment=GST_Treatment,
                    PlaceOfSupply=PlaceOfSupply,
                    InvoiceNo=MasterInvoiceNo,
                    Notes=Notes,
                    PaymentMode=PaymentMode,
                    PaymentID=Payment,
                    Amount=Amount,
                    BillDiscPercent=BillDiscPercent,
                    BillDiscAmount=BillDiscAmount,
                    TotalGrossAmt=TotalGrossAmt,
                    TotalTaxableAmount=TotalTaxableAmount,
                    TotalDiscount=TotalDiscount,
                    TotalTaxAmount=TotalTaxAmount,
                    TotalNetAmount=TotalNetAmount,
                    RoundOff=RoundOff,
                    GrandTotal=GrandTotal,
                    TaxInclusive=TaxInclusive,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    TaxType=TaxType,
                    TaxTypeID=TaxTypeID,
                    TotalVATAmount=TotalVATAmount,
                    TotalIGSTAmount=TotalIGSTAmount,
                    TotalSGSTAmount=TotalSGSTAmount,
                    TotalCGSTAmount=TotalCGSTAmount,
                    TaxNo=TaxNo
                )

                if TaxType == 'VAT':
                    if converted_float(TotalVATAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            model.LedgerPosting, BranchID, CompanyID)

                        # VAT on Expense
                        vat_on_expense = get_BranchLedgerId_for_LedgerPosting(
                            BranchID, CompanyID, 'vat_on_expense')

                        model.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=vat_on_expense,
                            RelatedLedgerID=Supplier.LedgerID,
                            Debit=TotalVATAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        model.LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=vat_on_expense,
                            RelatedLedgerID=Supplier.LedgerID,
                            Debit=TotalVATAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, vat_on_expense, ExpenseMasterID, VoucherType, TotalVATAmount, "Dr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            model.LedgerPosting, BranchID, CompanyID)

                        model.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=Supplier.LedgerID,
                            RelatedLedgerID=vat_on_expense,
                            Credit=TotalVATAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        model.LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=Supplier.LedgerID,
                            RelatedLedgerID=vat_on_expense,
                            Credit=TotalVATAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, TotalVATAmount, "Cr", "create")

                elif TaxType == 'GST Intra-state B2B':
                    if converted_float(TotalCGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            model.LedgerPosting, BranchID, CompanyID)
                        # Central GST on Expense
                        central_gst_on_expense = get_BranchLedgerId_for_LedgerPosting(
                            BranchID, CompanyID, 'central_gst_on_expense')

                        model.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=central_gst_on_expense,
                            RelatedLedgerID=Supplier.LedgerID,
                            Debit=TotalCGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                        model.LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=central_gst_on_expense,
                            RelatedLedgerID=Supplier.LedgerID,
                            Debit=TotalCGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, central_gst_on_expense, ExpenseMasterID, VoucherType, TotalCGSTAmount, "Dr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            model.LedgerPosting, BranchID, CompanyID)

                        model.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=Supplier.LedgerID,
                            RelatedLedgerID=central_gst_on_expense,
                            Credit=TotalCGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        model.LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=Supplier.LedgerID,
                            RelatedLedgerID=central_gst_on_expense,
                            Credit=TotalCGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, TotalCGSTAmount, "Cr", "create")

                    if converted_float(TotalSGSTAmount) > 0:

                        LedgerPostingID = get_auto_LedgerPostid(
                            model.LedgerPosting, BranchID, CompanyID)
                        # State GST on Payment
                        state_gst_on_payment = get_BranchLedgerId_for_LedgerPosting(
                            BranchID, CompanyID, 'state_gst_on_payment')

                        model.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=state_gst_on_payment,
                            RelatedLedgerID=Supplier.LedgerID,
                            Debit=TotalSGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                        model.LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=state_gst_on_payment,
                            RelatedLedgerID=Supplier.LedgerID,
                            Debit=TotalSGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, state_gst_on_payment, ExpenseMasterID, VoucherType, TotalSGSTAmount, "Dr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            model.LedgerPosting, BranchID, CompanyID)

                        model.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=Supplier.LedgerID,
                            RelatedLedgerID=state_gst_on_payment,
                            Credit=TotalSGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        model.LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=Supplier.LedgerID,
                            RelatedLedgerID=state_gst_on_payment,
                            Credit=TotalSGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, TotalSGSTAmount, "Cr", "create")

                elif TaxType == 'GST Inter-state B2B':
                    if converted_float(TotalIGSTAmount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            model.LedgerPosting, BranchID, CompanyID)
                        # Central GST on Expense
                        central_gst_on_expense = get_BranchLedgerId_for_LedgerPosting(
                            BranchID, CompanyID, 'central_gst_on_expense')

                        model.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=central_gst_on_expense,
                            RelatedLedgerID=Supplier.LedgerID,
                            Debit=TotalIGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        model.LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=central_gst_on_expense,
                            RelatedLedgerID=Supplier.LedgerID,
                            Debit=TotalIGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, central_gst_on_expense, ExpenseMasterID, VoucherType, TotalIGSTAmount, "Dr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            model.LedgerPosting, BranchID, CompanyID)

                        model.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=Supplier.LedgerID,
                            RelatedLedgerID=central_gst_on_expense,
                            Credit=TotalIGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        model.LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ExpenseMasterID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=Supplier.LedgerID,
                            RelatedLedgerID=central_gst_on_expense,
                            Credit=TotalIGSTAmount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, TotalIGSTAmount, "Cr", "create")

                if converted_float(RoundOff) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        model.LedgerPosting, BranchID, CompanyID)
                    # Round off Purchase
                    round_off_purchase = get_BranchLedgerId_for_LedgerPosting(
                        BranchID, CompanyID, 'round_off_purchase')

                    model.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=round_off_purchase,
                        RelatedLedgerID=Supplier.LedgerID,
                        Debit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    model.LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=round_off_purchase,
                        RelatedLedgerID=Supplier.LedgerID,
                        Debit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, round_off_purchase, ExpenseMasterID, VoucherType, RoundOff, "Dr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        model.LedgerPosting, BranchID, CompanyID)

                    model.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=round_off_purchase,
                        Credit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    model.LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=round_off_purchase,
                        Credit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, RoundOff, "Cr", "create")

                if converted_float(RoundOff) < 0:
                    # Round off Purchase
                    round_off_purchase = get_BranchLedgerId_for_LedgerPosting(
                        BranchID, CompanyID, 'round_off_purchase')

                    LedgerPostingID = get_auto_LedgerPostid(
                        model.LedgerPosting, BranchID, CompanyID)

                    RoundOff = abs(converted_float(RoundOff))

                    model.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=round_off_purchase,
                        RelatedLedgerID=Supplier.LedgerID,
                        Credit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    model.LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=round_off_purchase,
                        RelatedLedgerID=Supplier.LedgerID,
                        Credit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, round_off_purchase, ExpenseMasterID, VoucherType, RoundOff, "Cr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        model.LedgerPosting, BranchID, CompanyID)

                    model.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=round_off_purchase,
                        Debit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    model.LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=round_off_purchase,
                        Debit=RoundOff,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, RoundOff, "Dr", "create")

                if converted_float(TotalDiscount) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        model.LedgerPosting, BranchID, CompanyID)
                    # Discount on Purchase
                    discount_on_purchase = get_BranchLedgerId_for_LedgerPosting(
                        BranchID, CompanyID, 'discount_on_purchase')

                    model.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=discount_on_purchase,
                        RelatedLedgerID=Supplier.LedgerID,
                        Credit=TotalDiscount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    model.LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=discount_on_purchase,
                        RelatedLedgerID=Supplier.LedgerID,
                        Credit=TotalDiscount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, discount_on_purchase, ExpenseMasterID, VoucherType, TotalDiscount, "Cr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        model.LedgerPosting, BranchID, CompanyID)

                    model.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=discount_on_purchase,
                        Debit=TotalDiscount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    model.LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=discount_on_purchase,
                        Debit=TotalDiscount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, TotalDiscount, "Dr", "create")

                if converted_float(Amount) > 0:
                    # payment LedgerPosting
                    LedgerPostingID = get_auto_LedgerPostid(
                        model.LedgerPosting, BranchID, CompanyID)

                    model.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PaymentLedgerID,
                        RelatedLedgerID=Supplier.LedgerID,
                        Credit=Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    model.LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=PaymentLedgerID,
                        RelatedLedgerID=Supplier.LedgerID,
                        Credit=Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, PaymentLedgerID, ExpenseMasterID, VoucherType, Amount, "Cr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        model.LedgerPosting, BranchID, CompanyID)

                    model.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=PaymentLedgerID,
                        Debit=Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    model.LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=PaymentLedgerID,
                        Debit=Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, Amount, "Dr", "create")

                expenseDetails = data["ExpenseDetails"]

                for expenseDetail in expenseDetails:
                    LedgerID = expenseDetail['LedgerID']
                    if LedgerID:
                        Amount = expenseDetail['Amount']
                        TaxID = expenseDetail['TaxID']
                        DiscountAmount = converted_float(expenseDetail['DiscountAmount'])
                        TaxableAmount = converted_float(expenseDetail['TaxableAmount'])
                        TaxPerc = converted_float(expenseDetail['TaxPerc'])
                        TaxAmount = converted_float(expenseDetail['TaxAmount'])
                        NetTotal = converted_float(expenseDetail['Total'])
                        VATPerc = converted_float(expenseDetail['VATPerc'])
                        VATAmount = converted_float(expenseDetail['VATAmount'])
                        IGSTPerc = converted_float(expenseDetail['IGSTPerc'])
                        IGSTAmount = converted_float(expenseDetail['IGSTAmount'])
                        SGSTPerc = converted_float(expenseDetail['SGSTPerc'])
                        SGSTAmount = converted_float(expenseDetail['SGSTAmount'])
                        CGSTPerc = converted_float(expenseDetail['CGSTPerc'])
                        CGSTAmount = converted_float(expenseDetail['CGSTAmount'])

                        Ledger = model.AccountLedger.objects.get(id=LedgerID)
                        if not TaxID:
                            TaxID = None

                        ExpenseDetailsID = get_detailID(
                            model.ExpenseDetails, BranchID, CompanyID)

                        log_instance = model.ExpenseDetails_Log.objects.create(
                            CompanyID=CompanyID,
                            TransactionID=ExpenseDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            ExpenseMasterID=ExpenseMasterID,
                            Ledger=Ledger,
                            Amount=Amount,
                            TaxID=TaxID,
                            TaxableAmount=TaxableAmount,
                            DiscountAmount=DiscountAmount,
                            TaxPerc=TaxPerc,
                            TaxAmount=TaxAmount,
                            NetTotal=NetTotal,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            VATPerc=VATPerc,
                            VATAmount=VATAmount,
                            IGSTPerc=IGSTPerc,
                            IGSTAmount=IGSTAmount,
                            SGSTPerc=SGSTPerc,
                            SGSTAmount=SGSTAmount,
                            CGSTPerc=CGSTPerc,
                            CGSTAmount=CGSTAmount,
                        )
                        model.ExpenseDetails.objects.create(
                            CompanyID=CompanyID,
                            ExpenseDetailsID=ExpenseDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            ExpenseMasterID=ExpenseMasterID,
                            Ledger=Ledger,
                            Amount=Amount,
                            TaxID=TaxID,
                            TaxableAmount=TaxableAmount,
                            DiscountAmount=DiscountAmount,
                            TaxPerc=TaxPerc,
                            TaxAmount=TaxAmount,
                            NetTotal=NetTotal,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            VATPerc=VATPerc,
                            VATAmount=VATAmount,
                            IGSTPerc=IGSTPerc,
                            IGSTAmount=IGSTAmount,
                            SGSTPerc=SGSTPerc,
                            SGSTAmount=SGSTAmount,
                            CGSTPerc=CGSTPerc,
                            CGSTAmount=CGSTAmount,
                        )

                        LedgerPostingID = get_auto_LedgerPostid(
                            model.LedgerPosting, BranchID, CompanyID)

                        model.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ExpenseMasterID,
                            VoucherDetailID=ExpenseDetailsID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=Ledger.LedgerID,
                            RelatedLedgerID=Supplier.LedgerID,
                            Debit=Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        model.LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ExpenseMasterID,
                            VoucherDetailID=ExpenseDetailsID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=Ledger.LedgerID,
                            RelatedLedgerID=Supplier.LedgerID,
                            Debit=Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, Ledger.LedgerID, ExpenseMasterID, VoucherType, Amount, "Dr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            model.LedgerPosting, BranchID, CompanyID)

                        model.LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ExpenseMasterID,
                            VoucherDetailID=ExpenseDetailsID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=Supplier.LedgerID,
                            RelatedLedgerID=Ledger.LedgerID,
                            Credit=Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        model.LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ExpenseMasterID,
                            VoucherDetailID=ExpenseDetailsID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=Supplier.LedgerID,
                            RelatedLedgerID=Ledger.LedgerID,
                            Credit=Amount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, Amount, "Cr", "create")

                response_data = {
                    "StatusCode": 6000,
                    "id": instance.id,
                    "message": "Expense created Successfully!!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Expense',
                             'Create', 'Expense created Failed.', 'VoucherNo already exist')
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
        activity_id = activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Expense',
                     'Create', str(e), err_descrb)
        body_params = str(request.data)
        model.Activity_Log.objects.filter(
            id=activity_id).update(body_params=body_params)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def list_expense(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']

    try:
        page_number = data['page_no']
    except:
        page_number = ""

    try:
        items_per_page = data['items_per_page']
    except:
        items_per_page = ""

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']

        if model.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            if page_number and items_per_page:
                instances = model.ExpenseMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                count = len(instances)
                expense_sort_pagination = list_pagination(
                    instances,
                    items_per_page,
                    page_number
                )
            else:
                expense_sort_pagination = model.ExpenseMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                count = len(expense_sort_pagination)
            serialized = serializer.ExpenseMasterSerializer(expense_sort_pagination, many=True, context={
                "CompanyID": CompanyID, "PriceRounding": PriceRounding})

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "count": count,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "No Expenses"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch not valid."
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def expense(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    CreatedUserID = data['CreatedUserID']

    if model.ExpenseMaster.objects.filter(pk=pk).exists():
        instance = model.ExpenseMaster.objects.get(pk=pk)
        serialized = serializer.ExpenseMasterSerializer(
            instance, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding})

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data,
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Expense Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def edit_expense(request, pk):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CreatedUserID = data['CreatedUserID']
            PriceRounding = data['PriceRounding']
            CompanyID = get_company(CompanyID)

            today = datetime.datetime.now()
            expense_instance = model.ExpenseMaster.objects.get(pk=pk)
            ExpenseMasterID = expense_instance.ExpenseMasterID
            VoucherNo = expense_instance.VoucherNo
            BranchID = expense_instance.BranchID

            Date = data['Date']
            Supplier = data['Supplier']
            GST_Treatment = data['GST_Treatment']
            PlaceOfSupply = data['PlaceOfSupply']
            MasterInvoiceNo = data['MasterInvoiceNo']
            Notes = data['Notes']
            PaymentMode = data['PaymentMode']
            PaymentID = data['PaymentID']
            Amount = data['Amount']
            BillDiscPercent = data['BillDiscountPerc']
            BillDiscAmount = data['BillDiscountAmt']
            TotalGrossAmt = data['TotalGrossAmt']
            TotalTaxableAmount = data['TotalTaxableAmount']
            TotalDiscount = data['TotalDiscount']
            TotalTaxAmount = data['TotalTaxAmount']
            TotalNetAmount = data['TotalNetAmount']
            RoundOff = data['RoundOff']
            GrandTotal = data['GrandTotal']
            TaxInclusive = data['TaxInclusive']
            TaxType = data['TaxType']
            TaxTypeID = data['TaxTypeID']
            if TaxTypeID == "":
                TaxTypeID = 1
            TotalVATAmount = data['TotalVATAmount']
            TotalIGSTAmount = data['TotalIGSTAmount']
            TotalSGSTAmount = data['TotalSGSTAmount']
            TotalCGSTAmount = data['TotalCGSTAmount']
            TaxNo = data['TaxNo']

            IsActive = True

            VoucherType = "EX"
            # VoucherNo Updated
            try:
                PreFix = data['PreFix']
            except:
                PreFix = "EX"

            try:
                Seperator = data['Seperator']
            except:
                Seperator = ""

            try:
                InvoiceNo = data['InvoiceNo']
            except:
                InvoiceNo = 1

            Action = "M"

            Supplier = model.AccountLedger.objects.get(id=Supplier)
            Payment = None
            PaymentLedgerID = None
            if PaymentID:
                Payment = model.AccountLedger.objects.get(id=PaymentID)
                PaymentLedgerID = Payment.LedgerID
            if PlaceOfSupply:
                PlaceOfSupply = model.State.objects.get(id=PlaceOfSupply)
            else:
                PlaceOfSupply = None
                
            if not RoundOff:
                RoundOff = 0

            # checking voucher number already exist

            # ExpenseMasterID = get_masterID(
            #     model.ExpenseMaster, BranchID, CompanyID)

            # update_voucher_table(CompanyID,CreatedUserID,VoucherType,PreFix,Seperator, InvoiceNo)
            if CompanyID.is_gst:
                GST_Treatment = model.Parties.objects.get(CompanyID=CompanyID,BranchID=BranchID,LedgerID=Supplier.LedgerID).GST_Treatment
            elif CompanyID.is_vat:
                GST_Treatment = model.Parties.objects.get(CompanyID=CompanyID,BranchID=BranchID,LedgerID=Supplier.LedgerID).VAT_Treatment

            model.ExpenseMaster_Log.objects.create(
                TransactionID=ExpenseMasterID,
                CompanyID=CompanyID,
                BranchID=BranchID,
                Action=Action,
                VoucherNo=VoucherNo,
                Date=Date,
                Supplier=Supplier,
                GST_Treatment=GST_Treatment,
                PlaceOfSupply=PlaceOfSupply,
                InvoiceNo=MasterInvoiceNo,
                Notes=Notes,
                PaymentMode=PaymentMode,
                PaymentID=Payment,
                Amount=Amount,
                BillDiscPercent=BillDiscPercent,
                BillDiscAmount=BillDiscAmount,
                TotalGrossAmt=TotalGrossAmt,
                TotalTaxableAmount=TotalTaxableAmount,
                TotalDiscount=TotalDiscount,
                TotalTaxAmount=TotalTaxAmount,
                TotalNetAmount=TotalNetAmount,
                RoundOff=RoundOff,
                GrandTotal=GrandTotal,
                TaxInclusive=TaxInclusive,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                TaxType=TaxType,
                TaxTypeID=TaxTypeID,
                TotalVATAmount=TotalVATAmount,
                TotalIGSTAmount=TotalIGSTAmount,
                TotalSGSTAmount=TotalSGSTAmount,
                TotalCGSTAmount=TotalCGSTAmount,
                TaxNo=TaxNo
            )

            update_ledger = UpdateLedgerBalance(
                CompanyID, BranchID, 0, ExpenseMasterID, "EX", 0, "Cr", "update")

            if model.LedgerPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=ExpenseMasterID, BranchID=BranchID, VoucherType="EX").exists():
                ledgerPostInstances = model.LedgerPosting.objects.filter(
                    CompanyID=CompanyID, VoucherMasterID=ExpenseMasterID, BranchID=BranchID, VoucherType="EX").delete()

            expense_instance.Action = Action
            expense_instance.Date = Date
            expense_instance.Supplier = Supplier
            expense_instance.GST_Treatment = GST_Treatment
            expense_instance.PlaceOfSupply = PlaceOfSupply
            expense_instance.MasterInvoiceNo = MasterInvoiceNo
            expense_instance.Notes = Notes
            expense_instance.PaymentMode = PaymentMode
            expense_instance.PaymentID = Payment
            expense_instance.Amount = Amount
            expense_instance.BillDiscPercent = BillDiscPercent
            expense_instance.BillDiscAmount = BillDiscAmount
            expense_instance.TotalGrossAmt = TotalGrossAmt
            expense_instance.TotalTaxableAmount = TotalTaxableAmount
            expense_instance.TotalDiscount = TotalDiscount
            expense_instance.TotalTaxAmount = TotalTaxAmount
            expense_instance.TotalNetAmount = TotalNetAmount
            expense_instance.RoundOff = RoundOff
            expense_instance.GrandTotal = GrandTotal
            expense_instance.TaxInclusive = TaxInclusive
            expense_instance.UpdatedDate = today
            expense_instance.CreatedUserID = CreatedUserID
            expense_instance.TaxType = TaxType
            expense_instance.TaxTypeID = TaxTypeID
            expense_instance.TotalVATAmount = TotalVATAmount
            expense_instance.TotalIGSTAmount = TotalIGSTAmount
            expense_instance.TotalSGSTAmount = TotalSGSTAmount
            expense_instance.TotalCGSTAmount = TotalCGSTAmount
            expense_instance.TaxNo = TaxNo

            expense_instance.save()

            if TaxType == 'VAT':
                if converted_float(TotalVATAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        model.LedgerPosting, BranchID, CompanyID)
                    # VAT on Expense
                    vat_on_expense = get_BranchLedgerId_for_LedgerPosting(
                        BranchID, CompanyID, 'vat_on_expense')

                    model.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=vat_on_expense,
                        RelatedLedgerID=Supplier.LedgerID,
                        Debit=TotalVATAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    model.LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=vat_on_expense,
                        RelatedLedgerID=Supplier.LedgerID,
                        Debit=TotalVATAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, vat_on_expense, ExpenseMasterID, VoucherType, TotalVATAmount, "Dr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        model.LedgerPosting, BranchID, CompanyID)

                    model.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=vat_on_expense,
                        Credit=TotalVATAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    model.LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=vat_on_expense,
                        Credit=TotalVATAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, TotalVATAmount, "Cr", "create")

            elif TaxType == 'GST Intra-state B2B':
                if converted_float(TotalCGSTAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        model.LedgerPosting, BranchID, CompanyID)

                    # Central GST on Expense
                    central_gst_on_expense = get_BranchLedgerId_for_LedgerPosting(
                        BranchID, CompanyID, 'central_gst_on_expense')

                    model.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=central_gst_on_expense,
                        RelatedLedgerID=Supplier.LedgerID,
                        Debit=TotalCGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )
                    model.LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=central_gst_on_expense,
                        RelatedLedgerID=Supplier.LedgerID,
                        Debit=TotalCGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, central_gst_on_expense, ExpenseMasterID, VoucherType, TotalCGSTAmount, "Dr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        model.LedgerPosting, BranchID, CompanyID)

                    model.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=central_gst_on_expense,
                        Credit=TotalCGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    model.LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=central_gst_on_expense,
                        Credit=TotalCGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, TotalCGSTAmount, "Cr", "create")

                if converted_float(TotalSGSTAmount) > 0:

                    LedgerPostingID = get_auto_LedgerPostid(
                        model.LedgerPosting, BranchID, CompanyID)
                    # State GST on Payment
                    state_gst_on_payment = get_BranchLedgerId_for_LedgerPosting(
                        BranchID, CompanyID, 'state_gst_on_payment')

                    model.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=state_gst_on_payment,
                        RelatedLedgerID=Supplier.LedgerID,
                        Debit=TotalSGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )
                    model.LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=state_gst_on_payment,
                        RelatedLedgerID=Supplier.LedgerID,
                        Debit=TotalSGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, state_gst_on_payment, ExpenseMasterID, VoucherType, TotalSGSTAmount, "Dr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        model.LedgerPosting, BranchID, CompanyID)

                    model.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=state_gst_on_payment,
                        Credit=TotalSGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    model.LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=state_gst_on_payment,
                        Credit=TotalSGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, TotalSGSTAmount, "Cr", "create")

            elif TaxType == 'GST Inter-state B2B':
                if converted_float(TotalIGSTAmount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        model.LedgerPosting, BranchID, CompanyID)
                    # Central GST on Expense
                    central_gst_on_expense = get_BranchLedgerId_for_LedgerPosting(
                        BranchID, CompanyID, 'central_gst_on_expense')

                    model.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=central_gst_on_expense,
                        RelatedLedgerID=Supplier.LedgerID,
                        Debit=TotalIGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    model.LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=central_gst_on_expense,
                        RelatedLedgerID=Supplier.LedgerID,
                        Debit=TotalIGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, central_gst_on_expense, ExpenseMasterID, VoucherType, TotalIGSTAmount, "Dr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        model.LedgerPosting, BranchID, CompanyID)

                    model.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=central_gst_on_expense,
                        Credit=TotalIGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    model.LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=central_gst_on_expense,
                        Credit=TotalIGSTAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, TotalIGSTAmount, "Cr", "create")

            if converted_float(RoundOff) > 0:

                LedgerPostingID = get_auto_LedgerPostid(
                    model.LedgerPosting, BranchID, CompanyID)
                # Round off Purchase
                round_off_purchase = get_BranchLedgerId_for_LedgerPosting(
                    BranchID, CompanyID, 'round_off_purchase')

                model.LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=round_off_purchase,
                    RelatedLedgerID=Supplier.LedgerID,
                    Debit=RoundOff,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                model.LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=round_off_purchase,
                    RelatedLedgerID=Supplier.LedgerID,
                    Debit=RoundOff,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, round_off_purchase, ExpenseMasterID, VoucherType, RoundOff, "Dr", "create")

                LedgerPostingID = get_auto_LedgerPostid(
                    model.LedgerPosting, BranchID, CompanyID)

                model.LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=Supplier.LedgerID,
                    RelatedLedgerID=round_off_purchase,
                    Credit=RoundOff,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                model.LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=Supplier.LedgerID,
                    RelatedLedgerID=round_off_purchase,
                    Credit=RoundOff,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, RoundOff, "Cr", "create")

            if converted_float(RoundOff) < 0:
                # Round off Purchase
                round_off_purchase = get_BranchLedgerId_for_LedgerPosting(
                    BranchID, CompanyID, 'round_off_purchase')
                LedgerPostingID = get_auto_LedgerPostid(
                    model.LedgerPosting, BranchID, CompanyID)

                RoundOff = abs(converted_float(RoundOff))

                model.LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=round_off_purchase,
                    RelatedLedgerID=Supplier.LedgerID,
                    Credit=RoundOff,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                model.LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=round_off_purchase,
                    RelatedLedgerID=Supplier.LedgerID,
                    Credit=RoundOff,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, round_off_purchase, ExpenseMasterID, VoucherType, RoundOff, "Cr", "create")

                LedgerPostingID = get_auto_LedgerPostid(
                    model.LedgerPosting, BranchID, CompanyID)

                model.LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=Supplier.LedgerID,
                    RelatedLedgerID=round_off_purchase,
                    Debit=RoundOff,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                model.LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=Supplier.LedgerID,
                    RelatedLedgerID=round_off_purchase,
                    Debit=RoundOff,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, RoundOff, "Dr", "create")

            if converted_float(TotalDiscount) > 0:

                LedgerPostingID = get_auto_LedgerPostid(
                    model.LedgerPosting, BranchID, CompanyID)
                # Discount on Purchase
                discount_on_purchase = get_BranchLedgerId_for_LedgerPosting(
                    BranchID, CompanyID, 'discount_on_purchase')

                model.LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=discount_on_purchase,
                    RelatedLedgerID=Supplier.LedgerID,
                    Credit=TotalDiscount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                model.LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=discount_on_purchase,
                    RelatedLedgerID=Supplier.LedgerID,
                    Credit=TotalDiscount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, discount_on_purchase, ExpenseMasterID, VoucherType, TotalDiscount, "Cr", "create")

                LedgerPostingID = get_auto_LedgerPostid(
                    model.LedgerPosting, BranchID, CompanyID)

                model.LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=Supplier.LedgerID,
                    RelatedLedgerID=discount_on_purchase,
                    Debit=TotalDiscount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                model.LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=Supplier.LedgerID,
                    RelatedLedgerID=discount_on_purchase,
                    Debit=TotalDiscount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, TotalDiscount, "Dr", "create")

            # payment LedgerPosting
            if converted_float(Amount) > 0:
                LedgerPostingID = get_auto_LedgerPostid(
                    model.LedgerPosting, BranchID, CompanyID)

                model.LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PaymentLedgerID,
                    RelatedLedgerID=Supplier.LedgerID,
                    Credit=Amount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                model.LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=PaymentLedgerID,
                    RelatedLedgerID=Supplier.LedgerID,
                    Credit=Amount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, PaymentLedgerID, ExpenseMasterID, VoucherType, Amount, "Cr", "create")

                LedgerPostingID = get_auto_LedgerPostid(
                    model.LedgerPosting, BranchID, CompanyID)

                model.LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=Supplier.LedgerID,
                    RelatedLedgerID=PaymentLedgerID,
                    Debit=Amount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                model.LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ExpenseMasterID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=Supplier.LedgerID,
                    RelatedLedgerID=PaymentLedgerID,
                    Debit=Amount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

            update_ledger = UpdateLedgerBalance(
                CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, Amount, "Dr", "create")

            deleted_datas = data["deleted_data"]
            if deleted_datas:
                for deleted_Data in deleted_datas:
                    deleted_pk = deleted_Data['unq_id']

                    if not deleted_pk == '' or not deleted_pk == 0:
                        if model.ExpenseDetails.objects.filter(pk=deleted_pk).exists():
                            deleted_detail = model.ExpenseDetails.objects.filter(
                                pk=deleted_pk).delete()

            expenseDetails = data["ExpenseDetails"]

            for expenseDetail in expenseDetails:
                LedgerID = expenseDetail['LedgerID']
                if LedgerID:
                    pk = expenseDetail['unq_id']
                    detailID = expenseDetail['detailID']
                    Amount = expenseDetail['Amount']
                    TaxID = expenseDetail['TaxID']
                    DiscountAmount = converted_float(expenseDetail['DiscountAmount'])
                    TaxableAmount = converted_float(expenseDetail['TaxableAmount'])
                    TaxPerc = converted_float(expenseDetail['TaxPerc'])
                    TaxAmount = converted_float(expenseDetail['TaxAmount'])
                    NetTotal = converted_float(expenseDetail['Total'])
                    VATPerc = converted_float(expenseDetail['VATPerc'])
                    VATAmount = converted_float(expenseDetail['VATAmount'])
                    IGSTPerc = converted_float(expenseDetail['IGSTPerc'])
                    IGSTAmount = converted_float(expenseDetail['IGSTAmount'])
                    SGSTPerc = converted_float(expenseDetail['SGSTPerc'])
                    SGSTAmount = converted_float(expenseDetail['SGSTAmount'])
                    CGSTPerc = converted_float(expenseDetail['CGSTPerc'])
                    CGSTAmount = converted_float(expenseDetail['CGSTAmount'])

                    Ledger = model.AccountLedger.objects.get(id=LedgerID)
                    if not TaxID:
                        TaxID = None

                    if detailID == 0:
                        Detail_instance = model.ExpenseDetails.objects.get(
                            pk=pk)
                        ExpenseDetailsID = Detail_instance.ExpenseDetailsID

                        log_instance = model.ExpenseDetails_Log.objects.create(
                            CompanyID=CompanyID,
                            TransactionID=ExpenseDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            ExpenseMasterID=ExpenseMasterID,
                            Ledger=Ledger,
                            Amount=Amount,
                            TaxID=TaxID,
                            TaxableAmount=TaxableAmount,
                            DiscountAmount=DiscountAmount,
                            TaxPerc=TaxPerc,
                            TaxAmount=TaxAmount,
                            NetTotal=NetTotal,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            VATPerc=VATPerc,
                            VATAmount=VATAmount,
                            IGSTPerc=IGSTPerc,
                            IGSTAmount=IGSTAmount,
                            SGSTPerc=SGSTPerc,
                            SGSTAmount=SGSTAmount,
                            CGSTPerc=CGSTPerc,
                            CGSTAmount=CGSTAmount,
                        )

                        Detail_instance.Action = Action
                        Detail_instance.Ledger = Ledger
                        Detail_instance.Amount = Amount
                        Detail_instance.TaxID = TaxID
                        Detail_instance.TaxableAmount = TaxableAmount
                        Detail_instance.DiscountAmount = DiscountAmount
                        Detail_instance.TaxPerc = TaxPerc
                        Detail_instance.TaxAmount = TaxAmount
                        Detail_instance.NetTotal = NetTotal
                        Detail_instance.UpdatedDate = today
                        Detail_instance.CreatedUserID = CreatedUserID
                        Detail_instance.VATPerc = VATPerc
                        Detail_instance.VATAmount = VATAmount
                        Detail_instance.IGSTPerc = IGSTPerc
                        Detail_instance.IGSTAmount = IGSTAmount
                        Detail_instance.SGSTPerc = SGSTPerc
                        Detail_instance.SGSTAmount = SGSTAmount
                        Detail_instance.CGSTPerc = CGSTPerc
                        Detail_instance.CGSTAmount = CGSTAmount

                        Detail_instance.save()

                    if detailID == 1:
                        Action = "A"
                        ExpenseDetailsID = get_detailID(
                            model.ExpenseDetails, BranchID, CompanyID)

                        log_instance = model.ExpenseDetails_Log.objects.create(
                            CompanyID=CompanyID,
                            TransactionID=ExpenseDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            ExpenseMasterID=ExpenseMasterID,
                            Ledger=Ledger,
                            Amount=Amount,
                            TaxID=TaxID,
                            TaxableAmount=TaxableAmount,
                            DiscountAmount=DiscountAmount,
                            TaxPerc=TaxPerc,
                            TaxAmount=TaxAmount,
                            NetTotal=NetTotal,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            VATPerc=VATPerc,
                            VATAmount=VATAmount,
                            IGSTPerc=IGSTPerc,
                            IGSTAmount=IGSTAmount,
                            SGSTPerc=SGSTPerc,
                            SGSTAmount=SGSTAmount,
                            CGSTPerc=CGSTPerc,
                            CGSTAmount=CGSTAmount,
                        )

                        model.ExpenseDetails.objects.create(
                            CompanyID=CompanyID,
                            ExpenseDetailsID=ExpenseDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            ExpenseMasterID=ExpenseMasterID,
                            Ledger=Ledger,
                            Amount=Amount,
                            TaxID=TaxID,
                            TaxableAmount=TaxableAmount,
                            DiscountAmount=DiscountAmount,
                            TaxPerc=TaxPerc,
                            TaxAmount=TaxAmount,
                            NetTotal=NetTotal,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            VATPerc=VATPerc,
                            VATAmount=VATAmount,
                            IGSTPerc=IGSTPerc,
                            IGSTAmount=IGSTAmount,
                            SGSTPerc=SGSTPerc,
                            SGSTAmount=SGSTAmount,
                            CGSTPerc=CGSTPerc,
                            CGSTAmount=CGSTAmount,
                        )

                    LedgerPostingID = get_auto_LedgerPostid(
                        model.LedgerPosting, BranchID, CompanyID)

                    model.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherDetailID=ExpenseDetailsID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Ledger.LedgerID,
                        RelatedLedgerID=Supplier.LedgerID,
                        Debit=Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    model.LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherDetailID=ExpenseDetailsID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Ledger.LedgerID,
                        RelatedLedgerID=Supplier.LedgerID,
                        Debit=Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, Ledger.LedgerID, ExpenseMasterID, VoucherType, Amount, "Dr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        model.LedgerPosting, BranchID, CompanyID)

                    model.LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherDetailID=ExpenseDetailsID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=Ledger.LedgerID,
                        Credit=Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    model.LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherDetailID=ExpenseDetailsID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=Supplier.LedgerID,
                        RelatedLedgerID=Ledger.LedgerID,
                        Credit=Amount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, Supplier.LedgerID, ExpenseMasterID, VoucherType, Amount, "Cr", "edit")

            response_data = {
                "StatusCode": 6000,
                "message": "Expense Updated Successfully!!!",
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
            "message": "some error occured..please try again",
            "err_descrb": err_descrb
        }

        # transaction.rollback()
        # transaction.set_rollback(True)
        # transaction.set_rollback(False)
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Expense',
                     'Edit', str(e), err_descrb)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def delete_expense(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    try:
        selecte_ids = data['selecte_ids']
    except:
        selecte_ids = []

    today = datetime.datetime.now()
    instances = None
    ledgerPostInstances = None

    if selecte_ids:
        if model.ExpenseMaster.objects.filter(CompanyID=CompanyID, pk__in=selecte_ids).exists():
            instances = model.ExpenseMaster.objects.filter(pk__in=selecte_ids)
    else:
        if model.ExpenseMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instances = model.ExpenseMaster.objects.filter(pk=pk)

    # if model.ExpenseMaster.objects.filter(pk=pk).exists():
    #     instance = model.ExpenseMaster.objects.get(pk=pk)
    if instances:
        for instance in instances:
            ExpenseMasterID = instance.ExpenseMasterID
            BranchID = instance.BranchID
            VoucherNo = instance.VoucherNo
            VoucherType = "EX"
            Date = instance.Date
            Supplier = instance.Supplier
            GST_Treatment = instance.GST_Treatment
            PlaceOfSupply = instance.PlaceOfSupply
            MasterInvoiceNo = instance.InvoiceNo
            Notes = instance.Notes
            PaymentMode = instance.PaymentMode
            Payment = instance.PaymentID
            Amount = instance.Amount
            BillDiscPercent = instance.BillDiscPercent
            BillDiscAmount = instance.BillDiscAmount
            TotalGrossAmt = instance.TotalGrossAmt
            TotalTaxableAmount = instance.TotalTaxableAmount
            TotalDiscount = instance.TotalDiscount
            TotalTaxAmount = instance.TotalTaxAmount
            TotalNetAmount = instance.TotalNetAmount
            RoundOff = instance.RoundOff
            GrandTotal = instance.GrandTotal
            TaxInclusive = instance.TaxInclusive
            CreatedUserID = instance.CreatedUserID
            TaxType = instance.TaxType
            TaxTypeID = instance.TaxTypeID
            TotalVATAmount = instance.TotalVATAmount
            TotalIGSTAmount = instance.TotalIGSTAmount
            TotalSGSTAmount = instance.TotalSGSTAmount
            TotalCGSTAmount = instance.TotalCGSTAmount
            Action = "D"

            model.ExpenseMaster_Log.objects.create(
                TransactionID=ExpenseMasterID,
                CompanyID=CompanyID,
                BranchID=BranchID,
                Action=Action,
                VoucherNo=VoucherNo,
                Date=Date,
                Supplier=Supplier,
                GST_Treatment=GST_Treatment,
                PlaceOfSupply=PlaceOfSupply,
                InvoiceNo=MasterInvoiceNo,
                Notes=Notes,
                PaymentMode=PaymentMode,
                PaymentID=Payment,
                Amount=Amount,
                BillDiscPercent=BillDiscPercent,
                BillDiscAmount=BillDiscAmount,
                TotalGrossAmt=TotalGrossAmt,
                TotalTaxableAmount=TotalTaxableAmount,
                TotalDiscount=TotalDiscount,
                TotalTaxAmount=TotalTaxAmount,
                TotalNetAmount=TotalNetAmount,
                RoundOff=RoundOff,
                GrandTotal=GrandTotal,
                TaxInclusive=TaxInclusive,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                TaxType=TaxType,
                TaxTypeID=TaxTypeID,
                TotalVATAmount=TotalVATAmount,
                TotalIGSTAmount=TotalIGSTAmount,
                TotalSGSTAmount=TotalSGSTAmount,
                TotalCGSTAmount=TotalCGSTAmount,
            )

            detail_instances = model.ExpenseDetails.objects.filter(
                CompanyID=CompanyID, ExpenseMasterID=ExpenseMasterID, BranchID=BranchID)

            for detail_instance in detail_instances:

                ExpenseDetailsID = detail_instance.ExpenseDetailsID
                BranchID = detail_instance.BranchID
                ExpenseMasterID = detail_instance.ExpenseMasterID
                Ledger = detail_instance.Ledger
                Amount = detail_instance.Amount
                TaxID = detail_instance.TaxID
                TaxableAmount = detail_instance.TaxableAmount
                DiscountAmount = detail_instance.DiscountAmount
                TaxPerc = detail_instance.TaxPerc
                TaxAmount = detail_instance.TaxAmount
                NetTotal = detail_instance.NetTotal
                CreatedDate = detail_instance.CreatedDate
                UpdatedDate = detail_instance.UpdatedDate
                CreatedUserID = detail_instance.CreatedUserID
                VATPerc = detail_instance.VATPerc
                VATAmount = detail_instance.VATAmount
                IGSTPerc = detail_instance.IGSTPerc
                IGSTAmount = detail_instance.IGSTAmount
                SGSTPerc = detail_instance.SGSTPerc
                SGSTAmount = detail_instance.SGSTAmount
                CGSTPerc = detail_instance.CGSTPerc
                CGSTAmount = detail_instance.CGSTAmount

                log_instance = model.ExpenseDetails_Log.objects.create(
                    CompanyID=CompanyID,
                    TransactionID=ExpenseDetailsID,
                    BranchID=BranchID,
                    Action=Action,
                    ExpenseMasterID=ExpenseMasterID,
                    Ledger=Ledger,
                    Amount=Amount,
                    TaxID=TaxID,
                    TaxableAmount=TaxableAmount,
                    DiscountAmount=DiscountAmount,
                    TaxPerc=TaxPerc,
                    TaxAmount=TaxAmount,
                    NetTotal=NetTotal,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    VATPerc=VATPerc,
                    VATAmount=VATAmount,
                    IGSTPerc=IGSTPerc,
                    IGSTAmount=IGSTAmount,
                    SGSTPerc=SGSTPerc,
                    SGSTAmount=SGSTAmount,
                    CGSTPerc=CGSTPerc,
                    CGSTAmount=CGSTAmount,
                )

                detail_instance.delete()

            if model.LedgerPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=ExpenseMasterID, BranchID=BranchID, VoucherType=VoucherType).exists():
                ledgerPostInstances = model.LedgerPosting.objects.filter(
                    CompanyID=CompanyID, VoucherMasterID=ExpenseMasterID, BranchID=BranchID, VoucherType=VoucherType)

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, 0, ExpenseMasterID, VoucherType, 0, "Cr", "update")
                for ledgerPostInstance in ledgerPostInstances:

                    LedgerPostingID = ledgerPostInstance.LedgerPostingID
                    VoucherType = ledgerPostInstance.VoucherType
                    Debit = ledgerPostInstance.Debit
                    Credit = ledgerPostInstance.Credit
                    IsActive = ledgerPostInstance.IsActive
                    Date = ledgerPostInstance.Date
                    LedgerID = ledgerPostInstance.LedgerID
                    CreatedUserID = ledgerPostInstance.CreatedUserID

                    model.LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ExpenseMasterID,
                        VoucherNo=VoucherNo,
                        VoucherType=VoucherType,
                        LedgerID=LedgerID,
                        Debit=Debit,
                        Credit=Credit,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    ledgerPostInstance.delete()

            instance.delete()
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Expense',
                         'Delete', 'Expense Deleted Successfully.', 'Expense Deleted Successfully.')

            response_data = {
                "StatusCode": 6000,
                "message": "Expense Master Deleted Successfully!",
                "title": "Success",
            }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID,
                     'Expense', 'Delete', 'Expense Deleted Failed.', 'Expense Not Found!')
        response_data = {
            "StatusCode": 6001,
            "message": "Expense Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def expense_report(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    VoucherType = data['VoucherType']
    LedgerList = data['CashLedgers']
    FromDate = data['FromDate']
    ToDate = data['ToDate']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']

        if model.ExpenseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
            instances = model.ExpenseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)
            final_data = []
            new_final_data = []
            tot_IGSTAmount = 0
            tot_SGSTAmount = 0
            tot_CGSTAmount = 0
            tot_Discount = 0
            tot_Amount = 0
            tot_NetAmount = 0
            tot_VatAmount = 0
            for i in instances:
                ExpenseMasterID = i.ExpenseMasterID
                Particulars = i.Supplier.LedgerName
                if model.ExpenseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID).exists():
                    if LedgerList:
                        detail_ins = model.ExpenseDetails.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID, Ledger__LedgerID__in=LedgerList)
                    else:
                        detail_ins = model.ExpenseDetails.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, ExpenseMasterID=ExpenseMasterID)
                    for l in detail_ins:
                        TaxType = "-"
                        if model.TaxCategory.objects.filter(CompanyID=CompanyID,TaxID=l.TaxID).exists():
                            TaxType = model.TaxCategory.objects.get(CompanyID=CompanyID,TaxID=l.TaxID).TaxName
                        LedgerName = l.Ledger.LedgerName
                        
                        
                        
                        virtual_dictionary = {"id": i.id,"VoucherNo": i.VoucherNo, "Date": i.Date, "LedgerName": LedgerName,
                                               "VATAmount": l.VATAmount,"IGSTAmount": l.IGSTAmount,"SGSTAmount": l.SGSTAmount,"CGSTAmount": l.CGSTAmount,"TaxType": TaxType,"Particulars": Particulars,"Amount": l.Amount, "Discount": l.DiscountAmount, "NetAmount": l.NetTotal}
                        tot_Discount += l.DiscountAmount
                        tot_Amount += l.Amount
                        tot_NetAmount += l.NetTotal
                        tot_IGSTAmount += l.IGSTAmount
                        tot_SGSTAmount += l.SGSTAmount
                        tot_CGSTAmount += l.CGSTAmount
                        tot_VatAmount += l.VATAmount
                        final_data.append(virtual_dictionary)
                        new_final_data.append(virtual_dictionary)

            # append Total new New array
            tot_dictionary = {"VoucherNo": "Total", "Date": "", "LedgerName": "",
                              "TaxType": "", "IGSTAmount": tot_IGSTAmount, "SGSTAmount": tot_SGSTAmount, "CGSTAmount": tot_CGSTAmount, "Amount": tot_Amount, "Discount": tot_Discount, "NetAmount": tot_NetAmount, "Narration": "", "VATAmount": tot_VatAmount}
            new_final_data.append(tot_dictionary)
            if final_data and new_final_data:
                response_data = {
                    "StatusCode": 6000,
                    "data": final_data,
                    "new_data": new_final_data,
                    "total": tot_dictionary,
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "Expense details not found!"
                }
                return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Expense details not found!"
            }
            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)

