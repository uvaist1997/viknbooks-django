import numpy as np
from api.v9.reportQuerys.functions import query_receipt_report_data
from brands.models import Activity_Log, BillWiseDetails, BillWiseMaster, PaymentMaster, ReceiptMaster, ReceiptMaster_Log, ReceiptDetails, ReceiptDetails_Log,\
    LedgerPosting, LedgerPosting_Log, TransactionTypes, CompanySettings, GeneralSettings, AccountLedger
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v9.receipts.serializers import ReceiptDetailsListSerializer, ReceiptPrintSerializer, ReceiptMasterSerializer, ReceiptMasterRestSerializer, ReceiptDetailsSerializer, ReceiptDetailsRestSerializer
from api.v9.payments.serializers import ListSerializer, PaymentPrintSerializer
from api.v9.receipts.functions import export_to_excel_receiptReport, generate_serializer_errors, get_voucher_type, receiptReport_excel_data
from rest_framework import status
from api.v9.receipts.functions import get_auto_id, get_auto_idMaster
from api.v9.accountLedgers.functions import get_auto_LedgerPostid, UpdateLedgerBalance
import datetime
from main.functions import converted_float, get_BranchLedgerId_for_LedgerPosting, get_company, activity_log
from api.v9.companySettings.serializers import CompanySettingsRestSerializer
from api.v9.sales.functions import get_BillwiseDetailsID, get_Genrate_VoucherNo
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Prefetch
from django.db import transaction, IntegrityError
import re
import sys
import os
from main.functions import update_voucher_table
from django.http import HttpResponse, JsonResponse
import xlwt
from django.utils.translation import gettext_lazy as _


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
def create_receipt(request):
    data = request.data
    try:
        VoucherType = data['VoucherNo']
    except:
        VoucherType = ""
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']
    try:
        with transaction.atomic():
            CompanyID = get_company(CompanyID)

            today = datetime.datetime.now()
            BranchID = data['BranchID']
            VoucherNo = data['VoucherNo']
            VoucherType = data['VoucherType']
            MasterLedgerID = data['MasterLedgerID']
            EmployeeID = data['EmployeeID']
            FinancialYearID = data['FinancialYearID']
            Date = data['Date']
            TotalAmount = data['TotalAmount']
            Notes = data['Notes']
            IsActive = data['IsActive']

            Action = "A"

            # checking voucher number already exist
            VoucherNoLow = VoucherNo.lower()
            is_voucherExist = False
            insts = ReceiptMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType)
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True

            check_VoucherNoAutoGenerate = False
            is_ReceiptsOK = True

            if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="VoucherNoAutoGenerate").exists():
                check_VoucherNoAutoGenerate = GeneralSettings.objects.get(
                    BranchID=BranchID, CompanyID=CompanyID, SettingsType="VoucherNoAutoGenerate").SettingsValue

            if is_voucherExist == True and check_VoucherNoAutoGenerate == "True":
                VoucherNo = get_Genrate_VoucherNo(
                    ReceiptMaster, BranchID, CompanyID, "RT")
                is_ReceiptsOK = True
            elif is_voucherExist == False:
                is_ReceiptsOK = True
            else:
                is_ReceiptsOK = False

            # VoucherNo Updated
            try:
                PreFix = data['PreFix']
            except:
                PreFix = VoucherType

            try:
                Seperator = data['Seperator']
            except:
                Seperator = ""

            try:
                InvoiceNo = data['InvoiceNo']
            except:
                InvoiceNo = 1

            if is_ReceiptsOK:
                update_voucher_table(
                    CompanyID, CreatedUserID, "RT", PreFix, Seperator, InvoiceNo)
                ReceiptMasterID = get_auto_idMaster(
                    ReceiptMaster, BranchID, CompanyID)

                ReceiptNo = str(VoucherType) + str(VoucherNo)

                ReceiptMaster_Log.objects.create(
                    TransactionID=ReceiptMasterID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    VoucherType=VoucherType,
                    ReceiptNo=ReceiptNo,
                    LedgerID=MasterLedgerID,
                    EmployeeID=EmployeeID,
                    FinancialYearID=FinancialYearID,
                    Date=Date,
                    TotalAmount=TotalAmount,
                    Notes=Notes,
                    IsActive=IsActive,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    UpdatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                )

                instance = ReceiptMaster.objects.create(
                    ReceiptMasterID=ReceiptMasterID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    VoucherType=VoucherType,
                    ReceiptNo=ReceiptNo,
                    LedgerID=MasterLedgerID,
                    EmployeeID=EmployeeID,
                    FinancialYearID=FinancialYearID,
                    Date=Date,
                    TotalAmount=TotalAmount,
                    Notes=Notes,
                    IsActive=IsActive,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    UpdatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                )

                receiptDetailslogs = data["ReceiptDetails"]

                for receiptDetaillog in receiptDetailslogs:
                    PaymentGateway = receiptDetaillog['PaymentGateway']
                    RefferenceNo = receiptDetaillog['RefferenceNo']
                    CardNetwork = receiptDetaillog['CardNetwork']
                    PaymentStatus = receiptDetaillog['PaymentStatus']
                    LedgerID = receiptDetaillog['LedgerID']
                    DueDate = receiptDetaillog['DueDate']
                    Amount = receiptDetaillog['Amount']
                    NetAmount = receiptDetaillog['NetAmount']
                    Balance = receiptDetaillog['Balance']
                    Narration = receiptDetaillog['Narration']
                    Discount = receiptDetaillog['Discount']
                    if Discount == "" or Discount == None:
                        Discount = 0
                    if VoucherType == "CR":
                        transactionType = TransactionTypes.objects.get(
                            CompanyID=CompanyID, Name="Cash")
                        transactionTypeID = transactionType.TransactionTypesID
                        PaymentGateway = transactionTypeID

                        ReceiptDetailID = get_auto_id(
                            ReceiptDetails, BranchID, CompanyID)

                        log_instance = ReceiptDetails_Log.objects.create(
                            TransactionID=ReceiptDetailID,
                            BranchID=BranchID,
                            Action=Action,
                            ReceiptMasterID=ReceiptMasterID,
                            VoucherType=VoucherType,
                            PaymentGateway=PaymentGateway,
                            RefferenceNo=RefferenceNo,
                            CardNetwork=CardNetwork,
                            PaymentStatus=PaymentStatus,
                            LedgerID=LedgerID,
                            DueDate=DueDate,
                            Amount=Amount,
                            Discount=Discount,
                            NetAmount=NetAmount,
                            Balance=Balance,
                            Narration=Narration,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                        ReceiptDetails.objects.create(
                            ReceiptDetailID=ReceiptDetailID,
                            BranchID=BranchID,
                            Action=Action,
                            # receipt_master=instance,
                            ReceiptMasterID=ReceiptMasterID,
                            VoucherType=VoucherType,
                            PaymentGateway=PaymentGateway,
                            RefferenceNo=RefferenceNo,
                            CardNetwork=CardNetwork,
                            PaymentStatus=PaymentStatus,
                            LedgerID=LedgerID,
                            DueDate=DueDate,
                            Amount=Amount,
                            Discount=Discount,
                            NetAmount=NetAmount,
                            Balance=Balance,
                            Narration=Narration,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                            LogID=log_instance.ID
                        )

                    if VoucherType == "BR":

                        ReceiptDetailID = get_auto_id(
                            ReceiptDetails, BranchID, CompanyID)

                        log_instance = ReceiptDetails_Log.objects.create(
                            TransactionID=ReceiptDetailID,
                            BranchID=BranchID,
                            Action=Action,
                            ReceiptMasterID=ReceiptMasterID,
                            VoucherType=VoucherType,
                            PaymentGateway=PaymentGateway,
                            RefferenceNo=RefferenceNo,
                            CardNetwork=CardNetwork,
                            PaymentStatus=PaymentStatus,
                            LedgerID=LedgerID,
                            DueDate=DueDate,
                            Amount=Amount,
                            Discount=Discount,
                            NetAmount=NetAmount,
                            Balance=Balance,
                            Narration=Narration,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                        ReceiptDetails.objects.create(
                            # receipt_master=instance,
                            ReceiptDetailID=ReceiptDetailID,
                            BranchID=BranchID,
                            Action=Action,
                            ReceiptMasterID=ReceiptMasterID,
                            VoucherType=VoucherType,
                            PaymentGateway=PaymentGateway,
                            RefferenceNo=RefferenceNo,
                            CardNetwork=CardNetwork,
                            PaymentStatus=PaymentStatus,
                            LedgerID=LedgerID,
                            DueDate=DueDate,
                            Amount=Amount,
                            Discount=Discount,
                            NetAmount=NetAmount,
                            Balance=Balance,
                            Narration=Narration,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                            LogID=log_instance.ID
                        )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ReceiptMasterID,
                        VoucherDetailID=ReceiptDetailID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=MasterLedgerID,
                        Credit=NetAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ReceiptMasterID,
                        VoucherDetailID=ReceiptDetailID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=MasterLedgerID,
                        Credit=NetAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, LedgerID, ReceiptMasterID, VoucherType, NetAmount, "Cr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ReceiptMasterID,
                        VoucherDetailID=ReceiptDetailID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=MasterLedgerID,
                        RelatedLedgerID=LedgerID,
                        Debit=NetAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ReceiptMasterID,
                        VoucherDetailID=ReceiptDetailID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=MasterLedgerID,
                        RelatedLedgerID=LedgerID,
                        Debit=NetAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, MasterLedgerID, ReceiptMasterID, VoucherType, NetAmount, "Dr", "create")

                    if converted_float(Discount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        # Discount on Receipt
                        discount_on_receipt = get_BranchLedgerId_for_LedgerPosting(
                            BranchID, CompanyID, 'discount_on_receipt')

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ReceiptMasterID,
                            VoucherDetailID=ReceiptDetailID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=discount_on_receipt,
                            RelatedLedgerID=LedgerID,
                            Debit=Discount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ReceiptMasterID,
                            VoucherDetailID=ReceiptDetailID,
                            VoucherNo=VoucherNo,
                            VoucherType=VoucherType,
                            LedgerID=discount_on_receipt,
                            RelatedLedgerID=LedgerID,
                            Debit=Discount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, discount_on_receipt, ReceiptMasterID, VoucherType, Discount, "Dr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ReceiptMasterID,
                            VoucherDetailID=ReceiptDetailID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=LedgerID,
                            RelatedLedgerID=discount_on_receipt,
                            Credit=Discount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=ReceiptMasterID,
                            VoucherDetailID=ReceiptDetailID,
                            VoucherNo=VoucherNo,
                            VoucherType=VoucherType,
                            LedgerID=LedgerID,
                            RelatedLedgerID=discount_on_receipt,
                            Credit=Discount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, LedgerID, ReceiptMasterID, VoucherType, Discount, "Cr", "create")

                try:
                    billwiseDetails_datas = data['billwiseDetails_datas']
                except:
                    billwiseDetails_datas = []

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
                                PaymentDate=Date,
                                Payments=Amount,
                                PaymentVoucherType=VoucherType,
                                PaymentInvoiceNo=VoucherNo
                            )

                #request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Receipt',
                #              'Create', 'Receipt created successfully.', 'Receipt saved successfully.')

                response_data = {
                    "StatusCode": 6000,
                    "message": "Receipt created Successfully!!!",
                    "title": "Success",
                    "id": instance.id
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Receipt',
                            'Create', 'Receipt created Failed.', 'VoucherNo already exist')
                response_data = {
                    "StatusCode": 6001,
                    "message": str(_("VoucherNo already exist"))
                }

                return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        receipt_type = "Receipts" + str(VoucherType)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again"
        }

        activity_id = activity_log(request._request, CompanyID, 'Error', CreatedUserID, receipt_type,
                                   'Create', str(e), err_descrb)
        body_params = str(request.data)
        Activity_Log.objects.filter(
            id=activity_id).update(body_params=body_params)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def edit_receipt(request, pk):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            CreatedUserID = data['CreatedUserID']

            today = datetime.datetime.now()
            receiptMaster_instance = None
            receiptDetails_instance = None
            receiptDetails = None
            ledgerPostInstances = None

            receiptMaster_instance = ReceiptMaster.objects.get(
                CompanyID=CompanyID, pk=pk)

            ReceiptMasterID = receiptMaster_instance.ReceiptMasterID
            BranchID = receiptMaster_instance.BranchID
            VoucherNo = receiptMaster_instance.VoucherNo
            ReceiptNo = receiptMaster_instance.ReceiptNo
            instance_VoucherType = receiptMaster_instance.VoucherType

            VoucherType = data['VoucherType']
            MasterLedgerID = data['MasterLedgerID']
            EmployeeID = data['EmployeeID']
            FinancialYearID = data['FinancialYearID']
            Date = data['Date']
            TotalAmount = data['TotalAmount']
            Notes = data['Notes']
            IsActive = data['IsActive']

            Action = "M"

            ReceiptMaster_Log.objects.create(
                TransactionID=ReceiptMasterID,
                BranchID=BranchID,
                Action=Action,
                VoucherNo=VoucherNo,
                VoucherType=VoucherType,
                ReceiptNo=ReceiptNo,
                LedgerID=MasterLedgerID,
                EmployeeID=EmployeeID,
                FinancialYearID=FinancialYearID,
                Date=Date,
                TotalAmount=TotalAmount,
                Notes=Notes,
                IsActive=IsActive,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                UpdatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            update_ledger = UpdateLedgerBalance(
                CompanyID, BranchID, 0, ReceiptMasterID, instance_VoucherType, 0, "Cr", "update")

            if LedgerPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=ReceiptMasterID, BranchID=BranchID, VoucherType=instance_VoucherType).exists():
                ledgerPostInstances = LedgerPosting.objects.filter(
                    CompanyID=CompanyID, VoucherMasterID=ReceiptMasterID, BranchID=BranchID, VoucherType=instance_VoucherType).delete()
                # for ledgerPostInstance in ledgerPostInstances:
                #     ledgerPostInstance.delete()

            if ReceiptDetails.objects.filter(CompanyID=CompanyID, ReceiptMasterID=ReceiptMasterID, BranchID=BranchID, VoucherType=instance_VoucherType).exists():
                receiptDetailInstances = ReceiptDetails.objects.filter(
                    CompanyID=CompanyID, ReceiptMasterID=ReceiptMasterID, BranchID=BranchID, VoucherType=instance_VoucherType).delete()
                # for receiptDetailInstance in receiptDetailInstances:
                #     receiptDetailInstance.delete()

            receiptMaster_instance.VoucherType = VoucherType
            receiptMaster_instance.LedgerID = MasterLedgerID
            receiptMaster_instance.EmployeeID = EmployeeID
            receiptMaster_instance.FinancialYearID = FinancialYearID
            receiptMaster_instance.Date = Date
            receiptMaster_instance.TotalAmount = TotalAmount
            receiptMaster_instance.Notes = Notes
            receiptMaster_instance.IsActive = IsActive
            receiptMaster_instance.Action = Action
            receiptMaster_instance.UpdatedUserID = CreatedUserID
            receiptMaster_instance.UpdatedDate = today
            receiptMaster_instance.save()

            receiptDetails = data["ReceiptDetails"]

            for receiptDetail in receiptDetails:

                PaymentGateway = receiptDetail['PaymentGateway']
                RefferenceNo = receiptDetail['RefferenceNo']
                CardNetwork = receiptDetail['CardNetwork']
                PaymentStatus = receiptDetail['PaymentStatus']
                LedgerID = receiptDetail['LedgerID']
                DueDate = receiptDetail['DueDate']
                Amount = receiptDetail['Amount']
                NetAmount = receiptDetail['NetAmount']
                Balance = receiptDetail['Balance']
                Narration = receiptDetail['Narration']
                detailID = receiptDetail['detailID']
                Discount = receiptDetail['Discount']
                if Discount == "" or Discount == None:
                    Discount = 0
                if detailID == 0:
                    if VoucherType == "CR":
                        transactionType = TransactionTypes.objects.get(
                            CompanyID=CompanyID, Name="Cash")
                        transactionTypeID = transactionType.TransactionTypesID
                        PaymentGateway = transactionTypeID
                        ReceiptDetailID = get_auto_id(
                            ReceiptDetails, BranchID, CompanyID)

                        log_instance = ReceiptDetails_Log.objects.create(
                            TransactionID=ReceiptDetailID,
                            BranchID=BranchID,
                            Action=Action,
                            ReceiptMasterID=ReceiptMasterID,
                            VoucherType=VoucherType,
                            PaymentGateway=PaymentGateway,
                            RefferenceNo=RefferenceNo,
                            CardNetwork=CardNetwork,
                            PaymentStatus=PaymentStatus,
                            LedgerID=LedgerID,
                            DueDate=DueDate,
                            Amount=Amount,
                            Discount=Discount,
                            NetAmount=NetAmount,
                            Balance=Balance,
                            Narration=Narration,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                        ReceiptDetails.objects.create(
                            ReceiptDetailID=ReceiptDetailID,
                            BranchID=BranchID,
                            Action=Action,
                            ReceiptMasterID=ReceiptMasterID,
                            VoucherType=VoucherType,
                            PaymentGateway=PaymentGateway,
                            RefferenceNo=RefferenceNo,
                            CardNetwork=CardNetwork,
                            PaymentStatus=PaymentStatus,
                            LedgerID=LedgerID,
                            DueDate=DueDate,
                            Amount=Amount,
                            Discount=Discount,
                            NetAmount=NetAmount,
                            Balance=Balance,
                            Narration=Narration,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                            LogID=log_instance.ID
                            # receipt_master = receiptMaster_instance,
                        )

                    if VoucherType == "BR":

                        ReceiptDetailID = get_auto_id(
                            ReceiptDetails, BranchID, CompanyID)

                        log_instance = ReceiptDetails_Log.objects.create(
                            TransactionID=ReceiptDetailID,
                            BranchID=BranchID,
                            Action=Action,
                            ReceiptMasterID=ReceiptMasterID,
                            VoucherType=VoucherType,
                            PaymentGateway=PaymentGateway,
                            RefferenceNo=RefferenceNo,
                            CardNetwork=CardNetwork,
                            PaymentStatus=PaymentStatus,
                            LedgerID=LedgerID,
                            DueDate=DueDate,
                            Amount=Amount,
                            Discount=Discount,
                            NetAmount=NetAmount,
                            Balance=Balance,
                            Narration=Narration,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )
                        ReceiptDetails.objects.create(
                            # receipt_master = receiptMaster_instance,
                            ReceiptDetailID=ReceiptDetailID,
                            BranchID=BranchID,
                            Action=Action,
                            ReceiptMasterID=ReceiptMasterID,
                            VoucherType=VoucherType,
                            PaymentGateway=PaymentGateway,
                            RefferenceNo=RefferenceNo,
                            CardNetwork=CardNetwork,
                            PaymentStatus=PaymentStatus,
                            LedgerID=LedgerID,
                            DueDate=DueDate,
                            Amount=Amount,
                            Discount=Discount,
                            NetAmount=NetAmount,
                            Balance=Balance,
                            Narration=Narration,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                            LogID=log_instance.ID
                        )
                
                if detailID == 1:
                    Action = "A"
                    if VoucherType == "CR":
                        transactionType = TransactionTypes.objects.get(
                            CompanyID=CompanyID, Name="Cash")
                        transactionTypeID = transactionType.TransactionTypesID
                        PaymentGateway = transactionTypeID
                        ReceiptDetailID = get_auto_id(
                            ReceiptDetails, BranchID, CompanyID)

                        log_instance = ReceiptDetails_Log.objects.create(
                            TransactionID=ReceiptDetailID,
                            BranchID=BranchID,
                            Action=Action,
                            ReceiptMasterID=ReceiptMasterID,
                            VoucherType=VoucherType,
                            PaymentGateway=PaymentGateway,
                            RefferenceNo=RefferenceNo,
                            CardNetwork=CardNetwork,
                            PaymentStatus=PaymentStatus,
                            LedgerID=LedgerID,
                            DueDate=DueDate,
                            Amount=Amount,
                            Discount=Discount,
                            NetAmount=NetAmount,
                            Balance=Balance,
                            Narration=Narration,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )
                        ReceiptDetails.objects.create(
                            ReceiptDetailID=ReceiptDetailID,
                            BranchID=BranchID,
                            Action=Action,
                            ReceiptMasterID=ReceiptMasterID,
                            VoucherType=VoucherType,
                            PaymentGateway=PaymentGateway,
                            RefferenceNo=RefferenceNo,
                            CardNetwork=CardNetwork,
                            PaymentStatus=PaymentStatus,
                            LedgerID=LedgerID,
                            DueDate=DueDate,
                            Amount=Amount,
                            Discount=Discount,
                            NetAmount=NetAmount,
                            Balance=Balance,
                            Narration=Narration,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                            LogID=log_instance.ID
                        )

                    if VoucherType == "BR":

                        ReceiptDetailID = get_auto_id(
                            ReceiptDetails, BranchID, CompanyID)

                        log_instance = ReceiptDetails_Log.objects.create(
                            TransactionID=ReceiptDetailID,
                            BranchID=BranchID,
                            Action=Action,
                            ReceiptMasterID=ReceiptMasterID,
                            VoucherType=VoucherType,
                            PaymentGateway=PaymentGateway,
                            RefferenceNo=RefferenceNo,
                            CardNetwork=CardNetwork,
                            PaymentStatus=PaymentStatus,
                            LedgerID=LedgerID,
                            DueDate=DueDate,
                            Amount=Amount,
                            Discount=Discount,
                            NetAmount=NetAmount,
                            Balance=Balance,
                            Narration=Narration,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                        ReceiptDetails.objects.create(
                            ReceiptDetailID=ReceiptDetailID,
                            BranchID=BranchID,
                            Action=Action,
                            ReceiptMasterID=ReceiptMasterID,
                            VoucherType=VoucherType,
                            PaymentGateway=PaymentGateway,
                            RefferenceNo=RefferenceNo,
                            CardNetwork=CardNetwork,
                            PaymentStatus=PaymentStatus,
                            LedgerID=LedgerID,
                            DueDate=DueDate,
                            Amount=Amount,
                            Discount=Discount,
                            NetAmount=NetAmount,
                            Balance=Balance,
                            Narration=Narration,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                            LogID=log_instance.ID
                        )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ReceiptMasterID,
                    VoucherDetailID=ReceiptDetailID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=MasterLedgerID,
                    Credit=NetAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ReceiptMasterID,
                    VoucherDetailID=ReceiptDetailID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=MasterLedgerID,
                    Credit=NetAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, LedgerID, ReceiptMasterID, VoucherType, NetAmount, "Cr", "create")

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ReceiptMasterID,
                    VoucherDetailID=ReceiptDetailID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=MasterLedgerID,
                    RelatedLedgerID=LedgerID,
                    Debit=NetAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ReceiptMasterID,
                    VoucherDetailID=ReceiptDetailID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=MasterLedgerID,
                    RelatedLedgerID=LedgerID,
                    Debit=NetAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, MasterLedgerID, ReceiptMasterID, VoucherType, NetAmount, "Dr", "create")

                if converted_float(Discount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    # Discount on Receipt
                    discount_on_receipt = get_BranchLedgerId_for_LedgerPosting(
                        BranchID, CompanyID, 'discount_on_receipt')

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ReceiptMasterID,
                        VoucherDetailID=ReceiptDetailID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=discount_on_receipt,
                        RelatedLedgerID=LedgerID,
                        Debit=Discount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ReceiptMasterID,
                        VoucherDetailID=ReceiptDetailID,
                        VoucherNo=VoucherNo,
                        VoucherType=VoucherType,
                        LedgerID=discount_on_receipt,
                        RelatedLedgerID=LedgerID,
                        Debit=Discount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, discount_on_receipt, ReceiptMasterID, VoucherType, Discount, "Dr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ReceiptMasterID,
                        VoucherDetailID=ReceiptDetailID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=discount_on_receipt,
                        Credit=Discount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=ReceiptMasterID,
                        VoucherDetailID=ReceiptDetailID,
                        VoucherNo=VoucherNo,
                        VoucherType=VoucherType,
                        LedgerID=LedgerID,
                        RelatedLedgerID=discount_on_receipt,
                        Credit=Discount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, LedgerID, ReceiptMasterID, VoucherType, Discount, "Cr", "create")

                    
                    
            try:
                billwiseDetails_datas = data['billwiseDetails_datas']
            except:
                billwiseDetails_datas = []

            if billwiseDetails_datas:
                for b in billwiseDetails_datas:
                    BillwiseMasterID = b["BillwiseMasterID"]
                    Amount = b["Amount"]
                    
                    if BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID).exists():
                        bill_master_instance = BillWiseMaster.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID).first()
                        bill_master_instance.Payments = converted_float(Amount)
                        # bill_master_instance.Payments = converted_float(
                        #     bill_master_instance.Payments) + converted_float(Amount)
                        bill_master_instance.save()
                        if BillWiseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID,BillwiseMasterID=BillwiseMasterID, PaymentInvoiceNo=VoucherNo, PaymentVoucherType=VoucherType).exists():
                            bill_details_instance = BillWiseDetails.objects.filter(
                                CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID, PaymentInvoiceNo=VoucherNo, PaymentVoucherType=VoucherType).first()
                            bill_master_instance.Payments = converted_float(
                                bill_master_instance.Payments) + converted_float(Amount)
                            bill_details_instance.InvoiceNo = bill_master_instance.InvoiceNo
                            bill_details_instance.PaymentDate = Date
                            bill_details_instance.Payments = Amount
                            bill_details_instance.save()
                        else:
                            BillwiseDetailsID = get_BillwiseDetailsID(
                                BranchID, CompanyID)
                            BillWiseDetails.objects.create(
                                CompanyID=CompanyID,
                                BranchID=BranchID,
                                BillwiseDetailsID=BillwiseDetailsID,
                                BillwiseMasterID=BillwiseMasterID,
                                InvoiceNo=bill_master_instance.InvoiceNo,
                                VoucherType=bill_master_instance.VoucherType,
                                PaymentDate=Date,
                                Payments=Amount,
                                PaymentVoucherType=VoucherType,
                                PaymentInvoiceNo=VoucherNo
                            )
                    

            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Receipt',
            #              'Edit', 'Receipt Updated Successfully.', 'Receipt Updated Successfully')
            response_data = {
                "StatusCode": 6000,
                "message": "Receipt Updated Successfully!!!",
            }

            return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        receipt_type = "Receipts" + str(VoucherType)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again"
        }

        activity_id = activity_log(request._request, CompanyID, 'Error', CreatedUserID, receipt_type,
                                   'Edit', str(e), err_descrb)
        body_params = str(request.data)
        Activity_Log.objects.filter(
            id=activity_id).update(body_params=body_params)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def list_receiptMaster(request):
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
        VoucherType = serialized1.data['VoucherType']

        if ReceiptMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType).exists():
            if page_number and items_per_page:
                instances = ReceiptMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType)
                count = len(instances)
                ledger_sort_pagination = list_pagination(
                    instances,
                    items_per_page,
                    page_number
                )
            else:
                ledger_sort_pagination = ReceiptMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType)
                count = len(ledger_sort_pagination)

            serialized = ReceiptMasterRestSerializer(ledger_sort_pagination, many=True, context={
                                                     "CompanyID": CompanyID, "PriceRounding": PriceRounding})

            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Receipt',
            #              'List', 'Receipt List viewed Successfully.', 'Receipt List viewed Successfully.')
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "count": count,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Receipt',
            #              'List', 'Receipt List viewed Failed.', 'Receipts not found in this branch')
            response_data = {
                "StatusCode": 6001,
                "message": "Receipt Master not found in this branch."
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
def list_allreceiptMasters(request):
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
        VoucherType = serialized1.data['VoucherType']

        if ReceiptMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            if page_number and items_per_page:
                instances = ReceiptMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                count = len(instances)
                ledger_sort_pagination = list_pagination(
                    instances,
                    items_per_page,
                    page_number
                )
            else:
                ledger_sort_pagination = ReceiptMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                count = len(ledger_sort_pagination)

            serialized = ReceiptMasterRestSerializer(ledger_sort_pagination, many=True, context={
                                                     "CompanyID": CompanyID, "PriceRounding": PriceRounding})

            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Receipt',
            #              'List', 'Receipt List viewed Successfully.', 'Receipt List viewed Successfully.')
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "count": count,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Receipt',
            #              'List', 'Receipt List viewed Failed.', 'Receipts not found in this branch')
            response_data = {
                "StatusCode": 6001,
                "message": "Receipt Master not found in this branch."
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
def receiptMaster(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']

    instance = None
    if ReceiptMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = ReceiptMaster.objects.get(CompanyID=CompanyID, pk=pk)
        company_instance = CompanySettings.objects.get(pk=CompanyID.id)
        serialized = ReceiptMasterRestSerializer(
            instance, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding})
        company_serialized = CompanySettingsRestSerializer(
            company_instance, context={"request": request})

        #request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Receipt',
        #              'View', 'Receipt Single viewed Successfully.', 'Receipt Single viewed Successfully')
        # JsonResponse({'billwise_ins': billwise_ins})
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data,
            "company_data": company_serialized.data,
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Receipt Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_receiptMaster(request, pk):
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
    if selecte_ids:
        if ReceiptMaster.objects.filter(CompanyID=CompanyID, pk__in=selecte_ids).exists():
            instances = ReceiptMaster.objects.filter(pk__in=selecte_ids)
    else:
        if ReceiptMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instances = ReceiptMaster.objects.filter(pk=pk)

    if instances:
        for instance in instances:
            # instance = ReceiptMaster.objects.get(CompanyID=CompanyID, pk=pk)
            ReceiptMasterID = instance.ReceiptMasterID
            BranchID = instance.BranchID
            VoucherNo = instance.VoucherNo
            VoucherType = instance.VoucherType
            ReceiptNo = instance.ReceiptNo
            LedgerID = instance.LedgerID
            EmployeeID = instance.EmployeeID
            FinancialYearID = instance.FinancialYearID
            Date = instance.Date
            TotalAmount = instance.TotalAmount
            Notes = instance.Notes
            IsActive = instance.IsActive
            Action = "D"

            ReceiptMaster_Log.objects.create(
                TransactionID=ReceiptMasterID,
                BranchID=BranchID,
                Action=Action,
                VoucherNo=VoucherNo,
                VoucherType=VoucherType,
                ReceiptNo=ReceiptNo,
                LedgerID=LedgerID,
                EmployeeID=EmployeeID,
                FinancialYearID=FinancialYearID,
                Date=Date,
                TotalAmount=TotalAmount,
                Notes=Notes,
                IsActive=IsActive,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                UpdatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            detail_instances = ReceiptDetails.objects.filter(
                CompanyID=CompanyID, ReceiptMasterID=ReceiptMasterID, BranchID=BranchID, VoucherType=VoucherType)

            for detail_instance in detail_instances:

                ReceiptDetailID = detail_instance.ReceiptDetailID
                BranchID = detail_instance.BranchID
                ReceiptMasterID = detail_instance.ReceiptMasterID
                VoucherType = detail_instance.VoucherType
                PaymentGateway = detail_instance.PaymentGateway
                RefferenceNo = detail_instance.RefferenceNo
                CardNetwork = detail_instance.CardNetwork
                PaymentStatus = detail_instance.PaymentStatus
                LedgerID = detail_instance.LedgerID
                DueDate = detail_instance.DueDate
                Amount = detail_instance.Amount
                Discount = detail_instance.Discount
                NetAmount = detail_instance.NetAmount
                Balance = detail_instance.Balance
                Narration = detail_instance.Narration

                ReceiptDetails_Log.objects.create(
                    TransactionID=ReceiptDetailID,
                    BranchID=BranchID,
                    Action=Action,
                    ReceiptMasterID=ReceiptMasterID,
                    VoucherType=VoucherType,
                    PaymentGateway=PaymentGateway,
                    RefferenceNo=RefferenceNo,
                    CardNetwork=CardNetwork,
                    PaymentStatus=PaymentStatus,
                    LedgerID=LedgerID,
                    DueDate=DueDate,
                    Amount=Amount,
                    Discount=Discount,
                    NetAmount=NetAmount,
                    Balance=Balance,
                    Narration=Narration,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    UpdatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                )

                detail_instance.delete()

            if LedgerPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=ReceiptMasterID, BranchID=BranchID, VoucherType=VoucherType).exists():
                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, 0, ReceiptMasterID, VoucherType, 0, "Cr", "update")
                ledgerPostInstances = LedgerPosting.objects.filter(
                    CompanyID=CompanyID, VoucherMasterID=ReceiptMasterID, BranchID=BranchID, VoucherType=VoucherType)

                for ledgerPostInstance in ledgerPostInstances:
                    LedgerPostingID = ledgerPostInstance.LedgerPostingID
                    BranchID = ledgerPostInstance.BranchID
                    Date = ledgerPostInstance.Date
                    VoucherMasterID = ledgerPostInstance.VoucherMasterID
                    VoucherDetailID = ledgerPostInstance.VoucherDetailID
                    VoucherNo = ledgerPostInstance.VoucherNo
                    VoucherType = ledgerPostInstance.VoucherType
                    LedgerID = ledgerPostInstance.LedgerID
                    Debit = ledgerPostInstance.Debit
                    Credit = ledgerPostInstance.Credit
                    IsActive = ledgerPostInstance.IsActive

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=VoucherMasterID,
                        VoucherDetailID=VoucherDetailID,
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

            if BillWiseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PaymentInvoiceNo=VoucherNo, PaymentVoucherType=VoucherType).exists():
                billwise_instances = BillWiseDetails.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, PaymentInvoiceNo=VoucherNo, PaymentVoucherType=VoucherType)
                for billwise_instance in billwise_instances:
                    Amount = billwise_instance.Payments
                    BillwiseMasterID = billwise_instance.BillwiseMasterID
                    if BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID).exists():
                        master_inst = BillWiseMaster.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID).first()
                        Payments = master_inst.Payments
                        Payments = converted_float(
                            Payments) - converted_float(Amount)
                        master_inst.Payments = Payments
                        master_inst.save()
                    billwise_instance.delete()
            instance.delete()
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Receipt',
                     'Delete', 'Receipt Deleted Successfully.', 'Receipt Deleted Successfully')
        response_data = {
            "StatusCode": 6000,
            "message": "Receipt Master Deleted Successfully!",
            "title": "Success"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Receipt Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def search_receipts(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    product_name = data['product_name']
    length = data['length']
    param = data['param']
    VoucherType = data['VoucherType']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if ReceiptMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType).exists():
            instances = ReceiptMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType)

            if length < 3:
                if param == "VoucherNo":
                    instances = instances.filter(
                        (Q(VoucherNo__icontains=product_name)))[:10]
                else:
                    ledger_ids = []
                    if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerName__icontains=product_name).exists():
                        ledger_ins = AccountLedger.objects.filter(
                            CompanyID=CompanyID, LedgerName__icontains=product_name)
                        for l in ledger_ins:
                            ledger_ids.append(l.LedgerID)
                    instances = instances.filter(
                        (Q(LedgerID__in=ledger_ids)))[:10]
            else:
                if param == "VoucherNo":
                    instances = instances.filter(
                        (Q(VoucherNo__icontains=product_name)))
                else:
                    ledger_ids = []
                    if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerName__icontains=product_name).exists():
                        ledger_ins = AccountLedger.objects.filter(
                            CompanyID=CompanyID, LedgerName__icontains=product_name)
                        for l in ledger_ins:
                            ledger_ids.append(l.LedgerID)
                    instances = instances.filter((Q(LedgerID__in=ledger_ids)))
            serialized = ReceiptMasterRestSerializer(instances, many=True, context={
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
def report_receipts(request):
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
        arr = np.array(LedgerList)
        is_LedgerList = np.all((arr == 0))
        if is_LedgerList:
            LedgerList = 0
        else:
            LedgerList = tuple(LedgerList)
        df, details = query_receipt_report_data(
            data["CompanyID"],
            BranchID,
            FromDate,
            ToDate,
            PriceRounding,
            LedgerList,
            VoucherType,
        )
        response_data = {
            "StatusCode": 6000,
            "new_data": details,
        }
        return Response(response_data, status=status.HTTP_200_OK)
        # if ReceiptMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType, Date__gte=FromDate, Date__lte=ToDate).exists():
        #     instances = ReceiptMaster.objects.filter(
        #         CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType, Date__gte=FromDate, Date__lte=ToDate)
        #     final_data = []
        #     new_final_data = []
        #     tot_Discount = 0
        #     tot_Amount = 0
        #     tot_NetAmount = 0
        #     for i in instances:
        #         ReceiptMasterID = i.ReceiptMasterID
        #         if ReceiptDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ReceiptMasterID=ReceiptMasterID).exists():
        #             if LedgerList:
        #                 detail_ins = ReceiptDetails.objects.filter(
        #                     CompanyID=CompanyID, BranchID=BranchID, ReceiptMasterID=ReceiptMasterID, LedgerID__in=LedgerList)
        #             else:
        #                 detail_ins = ReceiptDetails.objects.filter(
        #                     CompanyID=CompanyID, BranchID=BranchID, ReceiptMasterID=ReceiptMasterID)
        #             for l in detail_ins:
        #                 LedgerName = AccountLedger.objects.get(
        #                     CompanyID=CompanyID, BranchID=BranchID, LedgerID=l.LedgerID).LedgerName
        #                 voucher_type = get_voucher_type(l.VoucherType)
        #                 virtual_dictionary = {"VoucherNo": i.VoucherNo, "Date": i.Date, "LedgerName": LedgerName,
        #                                       "VoucherType": voucher_type, "Amount": l.Amount, "Discount": l.Discount, "NetAmount": l.NetAmount, "Narration": l.Narration}
        #                 tot_Discount += l.Discount
        #                 tot_Amount += l.Amount
        #                 tot_NetAmount += l.NetAmount
        #                 final_data.append(virtual_dictionary)
        #                 new_final_data.append(virtual_dictionary)

        #     # append Total new New array
        #     tot_dictionary = {"VoucherNo": "Total", "Date": "", "LedgerName": "",
        #                       "VoucherType": "", "Amount": tot_Amount, "Discount": tot_Discount, "NetAmount": tot_NetAmount, "Narration": ""}
        #     new_final_data.append(tot_dictionary)
        #     if final_data and new_final_data:
        #         response_data = {
        #             "StatusCode": 6000,
        #             "data": final_data,
        #             "new_data": new_final_data,
        #             "total": tot_dictionary,
        #         }
        #         return Response(response_data, status=status.HTTP_200_OK)
        #     else:
        #         response_data = {
        #             "StatusCode": 6001,
        #             "message": "Receipt details not found!"
        #         }
        #         return Response(response_data, status=status.HTTP_200_OK)

        # elif ReceiptMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists() and VoucherType == "All":
        #     instances = ReceiptMaster.objects.filter(
        #         CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)

        #     final_data = []
        #     new_final_data = []
        #     tot_Discount = 0
        #     tot_Amount = 0
        #     tot_NetAmount = 0
        #     for i in instances:
        #         ReceiptMasterID = i.ReceiptMasterID
        #         if ReceiptDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ReceiptMasterID=ReceiptMasterID).exists():
        #             if LedgerList:
        #                 detail_ins = ReceiptDetails.objects.filter(
        #                     CompanyID=CompanyID, BranchID=BranchID, ReceiptMasterID=ReceiptMasterID, LedgerID__in=LedgerList)
        #             else:
        #                 detail_ins = ReceiptDetails.objects.filter(
        #                     CompanyID=CompanyID, BranchID=BranchID, ReceiptMasterID=ReceiptMasterID)
        #             for l in detail_ins:
        #                 LedgerName = AccountLedger.objects.get(
        #                     CompanyID=CompanyID, BranchID=BranchID, LedgerID=l.LedgerID).LedgerName
        #                 voucher_type = get_voucher_type(l.VoucherType)
        #                 virtual_dictionary = {"VoucherNo": i.VoucherNo, "Date": i.Date, "LedgerName": LedgerName,
        #                                       "VoucherType": voucher_type, "Amount": l.Amount, "Discount": l.Discount, "NetAmount": l.NetAmount, "Narration": l.Narration}
        #                 tot_Discount += l.Discount
        #                 tot_Amount += l.Amount
        #                 tot_NetAmount += l.NetAmount
        #                 final_data.append(virtual_dictionary)
        #                 new_final_data.append(virtual_dictionary)

        #     # append Total new New array
        #     tot_dictionary = {"VoucherNo": "Total", "Date": "", "LedgerName": "",
        #                       "VoucherType": "", "Amount": tot_Amount, "Discount": tot_Discount, "NetAmount": tot_NetAmount, "Narration": ""}
        #     new_final_data.append(tot_dictionary)
        #     if final_data and new_final_data:
        #         response_data = {
        #             "StatusCode": 6000,
        #             "data": final_data,
        #             "new_data": new_final_data,
        #             "total": tot_dictionary,
        #         }
        #         return Response(response_data, status=status.HTTP_200_OK)
        #     else:
        #         response_data = {
        #             "StatusCode": 6001,
        #             "message": "Receipt details not found!"
        #         }
        #         return Response(response_data, status=status.HTTP_200_OK)
        # else:
        #     response_data = {
        #         "StatusCode": 6001,
        #         "message": "Receipt details not found!"
        #     }
        #     return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def receiptReport_excel(request):
    CompanyID = request.GET.get('CompanyID')
    CompanyID = get_company(CompanyID)

    try:
        PriceRounding = int(request.GET.get('PriceRounding'))
    except:
        PriceRounding = ""

    try:
        BranchID = int(request.GET.get('BranchID'))
    except:
        BranchID = ""

    FromDate = request.GET.get('FromDate')
    ToDate = request.GET.get('ToDate')
    CreatedUserID = request.GET.get('CreatedUserID')
    VoucherType = request.GET.get('VoucherType')
    LedgerList = request.GET.getlist('CashLedgers')
    print(type(LedgerList), LedgerList)
    LedgerList = [x for x in LedgerList if x]
    for x in LedgerList:
        print(str(x).split(','))
        test_list = str(x).split(',')
        for i in range(0, len(test_list)):
            test_list[i] = int(test_list[i])
        LedgerList = test_list
    response = HttpResponse(content_type='application/ms-excel')

    # decide file name
    response['Content-Disposition'] = 'attachment; filename="Receipt Report.xls"'

    # creating workbook
    wb = xlwt.Workbook(encoding='utf-8')

    data = receiptReport_excel_data(
        CompanyID, BranchID, PriceRounding, VoucherType, LedgerList, FromDate, ToDate)

    print(data)
    title = str(CompanyID.CompanyName) + str(",") + \
        str(FromDate)+str(' To ')+str(ToDate)
    export_to_excel_receiptReport(wb, data, title)

    wb.save(response)
    return response


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def print_receipt(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    voucher_type = data['voucher_type']
    voucher_id = data['voucher_id']

    instance = None
    data = None
    if voucher_type == "CR" or voucher_type == "BR":
        if ReceiptMaster.objects.filter(pk=voucher_id).exists():
            instance = ReceiptMaster.objects.get(pk=voucher_id)
            serialized = ReceiptPrintSerializer(
                instance, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding})
            data = serialized.data
    elif voucher_type == "CP" or voucher_type == "BP":
        if PaymentMaster.objects.filter(pk=voucher_id).exists():
            instance = PaymentMaster.objects.get(pk=voucher_id)
            serialized = PaymentPrintSerializer(
                instance, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding})
            data = serialized.data
    if data:
        company_instance = CompanySettings.objects.get(pk=CompanyID.id)
        company_serialized = CompanySettingsRestSerializer(
            company_instance, context={"request": request})
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data,
            "company_data": company_serialized.data,
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "data Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def list_allreceiptDetails(request):
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
        VoucherType = serialized1.data['VoucherType']

        if ReceiptDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            if page_number and items_per_page:
                instances = ReceiptDetails.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                count = len(instances)
                ledger_sort_pagination = list_pagination(
                    instances,
                    items_per_page,
                    page_number
                )
                serialized = ReceiptDetailsListSerializer(ledger_sort_pagination, many=True, context={
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
                    # "message": "Payment Master not found in this branch."
                    "message": "No Pages"
                }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                # "message": "Payment Master not found in this branch."
                "message": "No Receipts"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch you enterd is not valid."
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def search_receipt_list(request):
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
        if ReceiptDetails.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID
        ).exists():
            ledger_ids = []
            if AccountLedger.objects.filter(
                CompanyID=CompanyID, LedgerName__icontains=product_name
            ).exists():
                ledgrs = AccountLedger.objects.filter(
                    CompanyID=CompanyID, LedgerName__icontains=product_name
                )
                ledger_ids = ledgrs.values_list("LedgerID", flat=True)
            if length < 3:
                if AccountLedger.objects.filter(
                    CompanyID=CompanyID, LedgerName__icontains=product_name
                ).exists():
                    ledgrs = AccountLedger.objects.filter(
                        CompanyID=CompanyID, LedgerName__icontains=product_name
                    )
                    ledger_ids = ledgrs.values_list("LedgerID", flat=True)[:10]
                instances = ReceiptDetails.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID
                )
                instances = instances.filter(

                    (Q(LedgerID__in=ledger_ids))
                )[:10]
            else:
                instances = ReceiptDetails.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID
                )
                instances = instances.filter(
                     (Q(LedgerID__in=ledger_ids))
                )
            serialized = ReceiptDetailsListSerializer(
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

