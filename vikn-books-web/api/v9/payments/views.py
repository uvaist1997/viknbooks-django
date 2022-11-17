from django.http import HttpResponse
import numpy as np
import xlwt
from xlwt import Workbook, XFStyle, Borders, Pattern, Font, easyxf, Alignment
from api.v9.reportQuerys.functions import query_payment_report_data
from brands.models import Activity_Log, BillWiseDetails, BillWiseMaster, VoucherNoTable, PaymentMaster, PaymentMaster_Log, PaymentDetails, PaymentDetails_Log, LedgerPosting, LedgerPosting_Log, PaymentDetailsDummy,\
    TransactionTypes, CompanySettings, GeneralSettings, AccountLedger
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v9.payments.serializers import BillwiseDetailsSerializer, BillwiseMasterSerializer, PaymentDetailsListSerializer, PaymentMasterSerializer, PaymentMasterRestSerializer, PaymentDetailsSerializer, PaymentDetailsRestSerializer
from api.v9.payments.serializers import ListSerializer
from api.v9.payments.functions import export_to_excel_paymentReport, generate_serializer_errors, paymentReport_excel_data
from rest_framework import status
from api.v9.payments.functions import get_auto_id, get_auto_idMaster, get_auto_VoucherNo
from api.v9.accountLedgers.functions import get_auto_LedgerPostid, UpdateLedgerBalance
from main.functions import converted_float, get_BranchLedgerId_for_LedgerPosting, get_LedgerBalance, get_company, activity_log
import datetime
from api.v9.companySettings.serializers import CompanySettingsRestSerializer
from api.v9.sales.functions import get_BillwiseDetailsID, get_Genrate_VoucherNo
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Prefetch, F
from api.v9.receipts.functions import get_voucher_type
from django.db import transaction, IntegrityError
import re
import sys
import os
from main.functions import update_voucher_table
import time
import timeit


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
def create_payment(request):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            CreatedUserID = data['CreatedUserID']
            today = datetime.datetime.now()
            paymentsDetails = None
            BranchID = data['BranchID']
            VoucherType = data['VoucherType']
            VoucherNo = data['VoucherNo']
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
            insts = PaymentMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType)
            if insts:
                for i in insts:
                    voucher_no = i.VoucherNo
                    voucherNo = voucher_no.lower()
                    if VoucherNoLow == voucherNo:
                        is_voucherExist = True

            check_VoucherNoAutoGenerate = False
            is_PaymentsOK = True

            if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="VoucherNoAutoGenerate").exists():
                check_VoucherNoAutoGenerate = GeneralSettings.objects.get(
                    BranchID=BranchID, CompanyID=CompanyID, SettingsType="VoucherNoAutoGenerate").SettingsValue

            if is_voucherExist == True and check_VoucherNoAutoGenerate == "True":
                VoucherNo = get_Genrate_VoucherNo(
                    PaymentMaster, BranchID, CompanyID, "PT")
                is_PaymentsOK = True
            elif is_voucherExist == False:
                is_PaymentsOK = True
            else:
                is_PaymentsOK = False

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

            if is_PaymentsOK:
                update_voucher_table(
                    CompanyID, CreatedUserID, "PT", PreFix, Seperator, InvoiceNo)

                PaymentMasterID = get_auto_idMaster(
                    PaymentMaster, BranchID, CompanyID)
                PaymentMaster_Log.objects.create(
                    TransactionID=PaymentMasterID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    VoucherType=VoucherType,
                    LedgerID=MasterLedgerID,
                    EmployeeID=EmployeeID,
                    PaymentNo=VoucherNo,
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

                instance = PaymentMaster.objects.create(
                    PaymentMasterID=PaymentMasterID,
                    BranchID=BranchID,
                    Action=Action,
                    VoucherNo=VoucherNo,
                    VoucherType=VoucherType,
                    LedgerID=MasterLedgerID,
                    EmployeeID=EmployeeID,
                    PaymentNo=VoucherNo,
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

                paymentsDetails = data["PaymentDetails"]

                for paymentsDetail in paymentsDetails:
                    # BranchID = paymentsDetail['BranchID']
                    # PaymentMasterID = paymentsDetail['PaymentMasterID']
                    PaymentGateway = paymentsDetail['PaymentGateway']
                    RefferenceNo = paymentsDetail['RefferenceNo']
                    CardNetwork = paymentsDetail['CardNetwork']
                    PaymentStatus = paymentsDetail['PaymentStatus']
                    DueDate = paymentsDetail['DueDate']
                    LedgerID = paymentsDetail['LedgerID']
                    Amount = paymentsDetail['Amount']
                    Balance = paymentsDetail['Balance']
                    Discount = paymentsDetail['Discount']
                    NetAmount = paymentsDetail['NetAmount']
                    Narration = paymentsDetail['Narration']
                    if Discount == "" or Discount == None:
                        Discount = 0
                    if VoucherType == "CP":
                        transactionType = TransactionTypes.objects.get(
                            Name="Cash", CompanyID=CompanyID)
                        transactionTypeID = transactionType.TransactionTypesID
                        PaymentGateway = transactionTypeID

                        PaymentDetailsID = get_auto_id(
                            PaymentDetails, BranchID, CompanyID)

                        log_instance = PaymentDetails_Log.objects.create(
                            TransactionID=PaymentDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            PaymentMasterID=PaymentMasterID,
                            PaymentGateway=PaymentGateway,
                            RefferenceNo=RefferenceNo,
                            CardNetwork=CardNetwork,
                            PaymentStatus=PaymentStatus,
                            DueDate=DueDate,
                            LedgerID=LedgerID,
                            Amount=Amount,
                            Balance=Balance,
                            Discount=Discount,
                            NetAmount=NetAmount,
                            Narration=Narration,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                            VoucherType=VoucherType
                        )

                        PaymentDetails.objects.create(
                            PaymentDetailsID=PaymentDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            # payment_master=instance,
                            PaymentMasterID=PaymentMasterID,
                            PaymentGateway=PaymentGateway,
                            RefferenceNo=RefferenceNo,
                            CardNetwork=CardNetwork,
                            PaymentStatus=PaymentStatus,
                            DueDate=DueDate,
                            LedgerID=LedgerID,
                            Amount=Amount,
                            Balance=Balance,
                            Discount=Discount,
                            NetAmount=NetAmount,
                            Narration=Narration,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                            VoucherType=VoucherType,
                            LogID=log_instance.ID
                        )

                    if VoucherType == "BP":

                        PaymentDetailsID = get_auto_id(
                            PaymentDetails, BranchID, CompanyID)

                        log_instance = PaymentDetails_Log.objects.create(
                            TransactionID=PaymentDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            PaymentMasterID=PaymentMasterID,
                            PaymentGateway=PaymentGateway,
                            RefferenceNo=RefferenceNo,
                            CardNetwork=CardNetwork,
                            PaymentStatus=PaymentStatus,
                            DueDate=DueDate,
                            LedgerID=LedgerID,
                            Amount=Amount,
                            Balance=Balance,
                            Discount=Discount,
                            NetAmount=NetAmount,
                            Narration=Narration,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                            VoucherType=VoucherType
                        )

                        PaymentDetails.objects.create(
                            PaymentDetailsID=PaymentDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            # payment_master=instance,
                            PaymentMasterID=PaymentMasterID,
                            PaymentGateway=PaymentGateway,
                            RefferenceNo=RefferenceNo,
                            CardNetwork=CardNetwork,
                            PaymentStatus=PaymentStatus,
                            DueDate=DueDate,
                            LedgerID=LedgerID,
                            Amount=Amount,
                            Balance=Balance,
                            Discount=Discount,
                            NetAmount=NetAmount,
                            Narration=Narration,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                            VoucherType=VoucherType,
                            LogID=log_instance.ID
                        )

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PaymentMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=MasterLedgerID,
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
                        VoucherMasterID=PaymentMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=MasterLedgerID,
                        Debit=NetAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, LedgerID, PaymentMasterID, VoucherType, NetAmount, "Dr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PaymentMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=MasterLedgerID,
                        RelatedLedgerID=LedgerID,
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
                        VoucherMasterID=PaymentMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=MasterLedgerID,
                        RelatedLedgerID=LedgerID,
                        Credit=NetAmount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, MasterLedgerID, PaymentMasterID, VoucherType, NetAmount, "Cr", "create")

                    if converted_float(Discount) > 0:
                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)
                        # Discount on Payment
                        discount_on_payment = get_BranchLedgerId_for_LedgerPosting(
                            BranchID, CompanyID, 'discount_on_payment')

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PaymentMasterID,
                            VoucherDetailID=PaymentDetailsID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=discount_on_payment,
                            RelatedLedgerID=LedgerID,
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
                            VoucherMasterID=PaymentMasterID,
                            VoucherDetailID=PaymentDetailsID,
                            VoucherNo=VoucherNo,
                            VoucherType=VoucherType,
                            LedgerID=discount_on_payment,
                            RelatedLedgerID=LedgerID,
                            Credit=Discount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, discount_on_payment, PaymentMasterID, VoucherType, Discount, "Cr", "create")

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=Date,
                            VoucherMasterID=PaymentMasterID,
                            VoucherDetailID=PaymentDetailsID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=LedgerID,
                            RelatedLedgerID=discount_on_payment,
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
                            VoucherMasterID=PaymentMasterID,
                            VoucherDetailID=PaymentDetailsID,
                            VoucherNo=VoucherNo,
                            VoucherType=VoucherType,
                            LedgerID=LedgerID,
                            RelatedLedgerID=discount_on_payment,
                            Debit=Discount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        update_ledger = UpdateLedgerBalance(
                            CompanyID, BranchID, LedgerID, PaymentMasterID, VoucherType, Discount, "Dr", "create")
                        
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
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Payment',
                #              'Create', 'Payment created successfully.', 'Payment saved successfully.')
                cash_Balance = get_LedgerBalance(CompanyID, 1)
                response_data = {
                    "id": instance.id,
                    "StatusCode": 6000,
                    "message": "Payment created Successfully!!!",
                    "cash_Balance": cash_Balance
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Payment',
                             'Create', 'Payment created Failed.', 'VoucherNo already exist!')
                response_data = {
                    "StatusCode": 6001,
                    "message": "VoucherNo already exist!.Please Change Your Prefix!"
                }

                return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        payment_type = "Payments" + str(VoucherType)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again"
        }

        activity_id = activity_log(request._request, CompanyID, 'Error', CreatedUserID, payment_type,
                                   'Create', str(e), err_descrb)
        body_params = str(request.data)
        Activity_Log.objects.filter(
            id=activity_id).update(body_params=body_params)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def edit_payment(request, pk):
    try:
        with transaction.atomic():
            import time
            time.sleep(5)
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            CreatedUserID = data['CreatedUserID']

            today = datetime.datetime.now()
            paymentMaster_instance = None
            paymentsDetails_instances = None
            paymentsDetails = None
            paymentMaster_instance = PaymentMaster.objects.get(pk=pk)

            PaymentMasterID = paymentMaster_instance.PaymentMasterID
            BranchID = paymentMaster_instance.BranchID
            VoucherNo = paymentMaster_instance.VoucherNo
            PaymentNo = paymentMaster_instance.PaymentNo
            instance_VoucherType = paymentMaster_instance.VoucherType

            Action = 'M'

            VoucherType = data['VoucherType']
            MasterLedgerID = data['MasterLedgerID']
            EmployeeID = data['EmployeeID']
            FinancialYearID = data['FinancialYearID']
            Date = data['Date']
            TotalAmount = data['TotalAmount']
            Notes = data['Notes']
            IsActive = data['IsActive']

            PaymentMaster_Log.objects.create(
                TransactionID=PaymentMasterID,
                BranchID=BranchID,
                Action=Action,
                VoucherNo=VoucherNo,
                VoucherType=VoucherType,
                LedgerID=MasterLedgerID,
                EmployeeID=EmployeeID,
                PaymentNo=PaymentNo,
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
                CompanyID, BranchID, 0, PaymentMasterID, instance_VoucherType, 0, "Cr", "update")

            if LedgerPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PaymentMasterID, BranchID=BranchID, VoucherType=instance_VoucherType).exists():
                ledgerPostInstances = LedgerPosting.objects.filter(
                    CompanyID=CompanyID, VoucherMasterID=PaymentMasterID, BranchID=BranchID, VoucherType=instance_VoucherType).delete()
                # for ledgerPostInstance in ledgerPostInstances:
                #     ledgerPostInstance.delete()

            if PaymentDetails.objects.filter(CompanyID=CompanyID, PaymentMasterID=PaymentMasterID, BranchID=BranchID, VoucherType=instance_VoucherType).exists():
                paymentDetailInstances = PaymentDetails.objects.filter(
                    CompanyID=CompanyID, PaymentMasterID=PaymentMasterID, BranchID=BranchID, VoucherType=instance_VoucherType).delete()
                # for paymentDetailInstance in paymentDetailInstances:
                #     paymentDetailInstance.delete()
            paymentMaster_instance.VoucherType = VoucherType
            paymentMaster_instance.LedgerID = MasterLedgerID
            paymentMaster_instance.EmployeeID = EmployeeID
            paymentMaster_instance.FinancialYearID = FinancialYearID
            paymentMaster_instance.Date = Date
            paymentMaster_instance.TotalAmount = TotalAmount
            paymentMaster_instance.Notes = Notes
            paymentMaster_instance.IsActive = IsActive
            paymentMaster_instance.UpdatedDate = today
            paymentMaster_instance.UpdatedUserID = CreatedUserID
            paymentMaster_instance.Action = Action

            paymentMaster_instance.save()

            paymentsDetailsLogs = data["PaymentDetails"]

            for paymentsDetailsLog in paymentsDetailsLogs:

                PaymentGateway = paymentsDetailsLog['PaymentGateway']
                RefferenceNo = paymentsDetailsLog['RefferenceNo']
                CardNetwork = paymentsDetailsLog['CardNetwork']
                PaymentStatus = paymentsDetailsLog['PaymentStatus']
                DueDate = paymentsDetailsLog['DueDate']
                LedgerID = paymentsDetailsLog['LedgerID']
                Amount = paymentsDetailsLog['Amount']
                Balance = paymentsDetailsLog['Balance']
                NetAmount = paymentsDetailsLog['NetAmount']
                Narration = paymentsDetailsLog['Narration']
                detailID = paymentsDetailsLog['detailID']
                Discount = paymentsDetailsLog['Discount']
                if Discount == "" or Discount == None:
                    Discount = 0

                PaymentDetailsID = get_auto_id(
                    PaymentDetails, BranchID, CompanyID)
                if detailID == 0:
                    if VoucherType == "CP":
                        transactionType = TransactionTypes.objects.get(
                            Name="Cash", CompanyID=CompanyID)
                        transactionTypeID = transactionType.TransactionTypesID
                        PaymentGateway = transactionTypeID
                        PaymentDetailsID = get_auto_id(
                            PaymentDetails, BranchID, CompanyID)

                        log_instance = PaymentDetails_Log.objects.create(
                            TransactionID=PaymentDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            PaymentMasterID=PaymentMasterID,
                            PaymentGateway=PaymentGateway,
                            RefferenceNo=RefferenceNo,
                            CardNetwork=CardNetwork,
                            PaymentStatus=PaymentStatus,
                            DueDate=DueDate,
                            LedgerID=LedgerID,
                            Amount=Amount,
                            Balance=Balance,
                            Discount=Discount,
                            NetAmount=NetAmount,
                            Narration=Narration,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                            VoucherType=VoucherType,
                        )
                        PaymentDetails.objects.create(
                            # payment_master = paymentMaster_instance,
                            PaymentDetailsID=PaymentDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            PaymentMasterID=PaymentMasterID,
                            PaymentGateway=PaymentGateway,
                            RefferenceNo=RefferenceNo,
                            CardNetwork=CardNetwork,
                            PaymentStatus=PaymentStatus,
                            DueDate=DueDate,
                            LedgerID=LedgerID,
                            Amount=Amount,
                            Balance=Balance,
                            Discount=Discount,
                            NetAmount=NetAmount,
                            Narration=Narration,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                            VoucherType=VoucherType,
                            LogID=log_instance.ID
                        )

                    if VoucherType == "BP":
                        PaymentDetailsID = get_auto_id(
                            PaymentDetails, BranchID, CompanyID)
                        log_instance = PaymentDetails_Log.objects.create(
                            TransactionID=PaymentDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            PaymentMasterID=PaymentMasterID,
                            PaymentGateway=PaymentGateway,
                            RefferenceNo=RefferenceNo,
                            CardNetwork=CardNetwork,
                            PaymentStatus=PaymentStatus,
                            DueDate=DueDate,
                            LedgerID=LedgerID,
                            Amount=Amount,
                            Balance=Balance,
                            Discount=Discount,
                            NetAmount=NetAmount,
                            Narration=Narration,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                            VoucherType=VoucherType
                        )

                        PaymentDetails.objects.create(
                            # payment_master = paymentMaster_instance,
                            PaymentDetailsID=PaymentDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            PaymentMasterID=PaymentMasterID,
                            PaymentGateway=PaymentGateway,
                            RefferenceNo=RefferenceNo,
                            CardNetwork=CardNetwork,
                            PaymentStatus=PaymentStatus,
                            DueDate=DueDate,
                            LedgerID=LedgerID,
                            Amount=Amount,
                            Balance=Balance,
                            Discount=Discount,
                            NetAmount=NetAmount,
                            Narration=Narration,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                            VoucherType=VoucherType,
                            LogID=log_instance.ID
                        )

                    # LedgerPostingID = get_auto_LedgerPostid(
                    #     LedgerPosting, BranchID, CompanyID)

                    # LedgerPosting.objects.create(
                    #     LedgerPostingID=LedgerPostingID,
                    #     BranchID=BranchID,
                    #     Date=Date,
                    #     VoucherMasterID=PaymentMasterID,
                    #     VoucherDetailID=PaymentDetailsID,
                    #     VoucherType=VoucherType,
                    #     VoucherNo=VoucherNo,
                    #     LedgerID=LedgerID,
                    #     Debit=Amount,
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
                    #     Date=Date,
                    #     VoucherMasterID=PaymentMasterID,
                    #     VoucherDetailID=PaymentDetailsID,
                    #     VoucherNo=VoucherNo,
                    #     VoucherType=VoucherType,
                    #     LedgerID=LedgerID,
                    #     Debit=Amount,
                    #     IsActive=IsActive,
                    #     Action=Action,
                    #     CreatedUserID=CreatedUserID,
                    #     CreatedDate=today,
                    #     UpdatedDate=today,
                    #     CompanyID=CompanyID,
                    # )

                    # LedgerPostingID = get_auto_LedgerPostid(
                    #     LedgerPosting, BranchID, CompanyID)

                    # LedgerPosting.objects.create(
                    #     LedgerPostingID=LedgerPostingID,
                    #     BranchID=BranchID,
                    #     Date=Date,
                    #     VoucherMasterID=PaymentMasterID,
                    #     VoucherDetailID=PaymentDetailsID,
                    #     VoucherType=VoucherType,
                    #     VoucherNo=VoucherNo,
                    #     LedgerID=MasterLedgerID,
                    #     Credit=NetAmount,
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
                    #     Date=Date,
                    #     VoucherMasterID=PaymentMasterID,
                    #     VoucherDetailID=PaymentDetailsID,
                    #     VoucherNo=VoucherNo,
                    #     VoucherType=VoucherType,
                    #     LedgerID=MasterLedgerID,
                    #     Credit=NetAmount,
                    #     IsActive=IsActive,
                    #     Action=Action,
                    #     CreatedUserID=CreatedUserID,
                    #     CreatedDate=today,
                    #     UpdatedDate=today,
                    #     CompanyID=CompanyID,
                    # )

                    # if converted_float(Discount) > 0:
                    #     LedgerPostingID = get_auto_LedgerPostid(
                    #         LedgerPosting, BranchID, CompanyID)

                    #     LedgerPosting.objects.create(
                    #         LedgerPostingID=LedgerPostingID,
                    #         BranchID=BranchID,
                    #         Date=Date,
                    #         VoucherMasterID=PaymentMasterID,
                    #         VoucherDetailID=PaymentDetailsID,
                    #         VoucherType=VoucherType,
                    #         VoucherNo=VoucherNo,
                    #         LedgerID=82,
                    #         Credit=Discount,
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
                    #         VoucherMasterID=PaymentMasterID,
                    #         VoucherDetailID=PaymentDetailsID,
                    #         VoucherNo=VoucherNo,
                    #         VoucherType=VoucherType,
                    #         LedgerID=82,
                    #         Credit=Discount,
                    #         IsActive=IsActive,
                    #         Action=Action,
                    #         CreatedUserID=CreatedUserID,
                    #         CreatedDate=today,
                    #         UpdatedDate=today,
                    #         CompanyID=CompanyID,
                    #     )

                if detailID == 1:
                    Action = "A"
                    if VoucherType == "CP":
                        transactionType = TransactionTypes.objects.get(
                            Name="Cash", CompanyID=CompanyID)
                        transactionTypeID = transactionType.TransactionTypesID
                        PaymentGateway = transactionTypeID
                        PaymentDetailsID = get_auto_id(
                            PaymentDetails, BranchID, CompanyID)

                        log_instance = PaymentDetails_Log.objects.create(
                            TransactionID=PaymentDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            PaymentMasterID=PaymentMasterID,
                            PaymentGateway=PaymentGateway,
                            RefferenceNo=RefferenceNo,
                            CardNetwork=CardNetwork,
                            PaymentStatus=PaymentStatus,
                            DueDate=DueDate,
                            LedgerID=LedgerID,
                            Amount=Amount,
                            Balance=Balance,
                            Discount=Discount,
                            NetAmount=NetAmount,
                            Narration=Narration,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                            VoucherType=VoucherType,
                        )

                        PaymentDetails.objects.create(
                            PaymentDetailsID=PaymentDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            PaymentMasterID=PaymentMasterID,
                            PaymentGateway=PaymentGateway,
                            RefferenceNo=RefferenceNo,
                            CardNetwork=CardNetwork,
                            PaymentStatus=PaymentStatus,
                            DueDate=DueDate,
                            LedgerID=LedgerID,
                            Amount=Amount,
                            Balance=Balance,
                            Discount=Discount,
                            NetAmount=NetAmount,
                            Narration=Narration,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                            VoucherType=VoucherType,
                            LogID=log_instance.ID
                        )

                    if VoucherType == "BP":
                        PaymentDetailsID = get_auto_id(
                            PaymentDetails, BranchID, CompanyID)
                        log_instance = PaymentDetails_Log.objects.create(
                            TransactionID=PaymentDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            PaymentMasterID=PaymentMasterID,
                            PaymentGateway=PaymentGateway,
                            RefferenceNo=RefferenceNo,
                            CardNetwork=CardNetwork,
                            PaymentStatus=PaymentStatus,
                            DueDate=DueDate,
                            LedgerID=LedgerID,
                            Amount=Amount,
                            Balance=Balance,
                            Discount=Discount,
                            NetAmount=NetAmount,
                            Narration=Narration,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                            VoucherType=VoucherType,
                        )
                        PaymentDetails.objects.create(
                            PaymentDetailsID=PaymentDetailsID,
                            BranchID=BranchID,
                            Action=Action,
                            PaymentMasterID=PaymentMasterID,
                            PaymentGateway=PaymentGateway,
                            RefferenceNo=RefferenceNo,
                            CardNetwork=CardNetwork,
                            PaymentStatus=PaymentStatus,
                            DueDate=DueDate,
                            LedgerID=LedgerID,
                            Amount=Amount,
                            Balance=Balance,
                            Discount=Discount,
                            NetAmount=NetAmount,
                            Narration=Narration,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            UpdatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                            VoucherType=VoucherType,
                            LogID=log_instance.ID
                        )

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PaymentMasterID,
                    VoucherDetailID=PaymentDetailsID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=MasterLedgerID,
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
                    VoucherMasterID=PaymentMasterID,
                    VoucherDetailID=PaymentDetailsID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=LedgerID,
                    RelatedLedgerID=MasterLedgerID,
                    Debit=NetAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, LedgerID, PaymentMasterID, VoucherType, NetAmount, "Dr", "create")

                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=PaymentMasterID,
                    VoucherDetailID=PaymentDetailsID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=MasterLedgerID,
                    RelatedLedgerID=LedgerID,
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
                    VoucherMasterID=PaymentMasterID,
                    VoucherDetailID=PaymentDetailsID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=MasterLedgerID,
                    RelatedLedgerID=LedgerID,
                    Credit=NetAmount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, MasterLedgerID, PaymentMasterID, VoucherType, NetAmount, "Cr", "create")

                if converted_float(Discount) > 0:
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)
                    # Discount on Payment
                    discount_on_payment = get_BranchLedgerId_for_LedgerPosting(
                        BranchID, CompanyID, 'discount_on_payment')

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PaymentMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=discount_on_payment,
                        RelatedLedgerID=LedgerID,
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
                        VoucherMasterID=PaymentMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherNo=VoucherNo,
                        VoucherType=VoucherType,
                        LedgerID=discount_on_payment,
                        RelatedLedgerID=LedgerID,
                        Credit=Discount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, discount_on_payment, PaymentMasterID, VoucherType, Discount, "Cr", "create")

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PaymentMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=discount_on_payment,
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
                        VoucherMasterID=PaymentMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherNo=VoucherNo,
                        VoucherType=VoucherType,
                        LedgerID=LedgerID,
                        RelatedLedgerID=discount_on_payment,
                        Debit=Discount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    update_ledger = UpdateLedgerBalance(
                        CompanyID, BranchID, LedgerID, PaymentMasterID, VoucherType, Discount, "Dr", "create")

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
                        if BillWiseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, BillwiseMasterID=BillwiseMasterID, PaymentInvoiceNo=VoucherNo, PaymentVoucherType=VoucherType).exists():
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
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Payment',
                         'Edit', 'Payment Updated successfully.', 'Payment Updated successfully.')

            response_data = {
                "StatusCode": 6000,
                "message": "Payments Updated Successfully!!!",
            }

            return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        payment_type = "Payments" + str(VoucherType)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again"
        }

        activity_id = activity_log(request._request, CompanyID, 'Error', CreatedUserID, payment_type,
                                   'Edit', str(e), err_descrb)
        body_params = str(request.data)
        Activity_Log.objects.filter(
            id=activity_id).update(body_params=body_params)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def list_paymentMasters(request):
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

        if PaymentMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType).exists():

            if page_number and items_per_page:
                instances = PaymentMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType)
                count = len(instances)
                ledger_sort_pagination = list_pagination(
                    instances,
                    items_per_page,
                    page_number
                )
            else:
                ledger_sort_pagination = PaymentMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType)
                count = len(ledger_sort_pagination)
            serialized = PaymentMasterRestSerializer(ledger_sort_pagination, many=True, context={
                                                     "CompanyID": CompanyID, "PriceRounding": PriceRounding})

            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Payment',
            #              'List Payment', 'Payment List Viewed successfully.', 'Payment List Viewed successfully.')
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "count": count,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Payment',
            #              'List Payment', 'Payment List Viewed Failed.', 'Payment not found in this branch')
            response_data = {
                "StatusCode": 6001,
                # "message": "Payment Master not found in this branch."
                "message": "No Payments"
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
def list_allpaymentMasters(request):
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

        if PaymentMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():

            if page_number and items_per_page:
                instances = PaymentMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                count = len(instances)
                ledger_sort_pagination = list_pagination(
                    instances,
                    items_per_page,
                    page_number
                )
            else:
                ledger_sort_pagination = PaymentMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                count = len(ledger_sort_pagination)
            serialized = PaymentMasterRestSerializer(ledger_sort_pagination, many=True, context={
                                                     "CompanyID": CompanyID, "PriceRounding": PriceRounding})

            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Payment',
            #              'List Payment', 'Payment List Viewed successfully.', 'Payment List Viewed successfully.')
            payment_details = PaymentDetails.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
            detail_count = len(payment_details)
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "count": count,
                "detail_count": detail_count
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Payment',
            #              'List Payment', 'Payment List Viewed Failed.', 'Payment not found in this branch')
            response_data = {
                "StatusCode": 6001,
                # "message": "Payment Master not found in this branch."
                "message": "No Payments"
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
def paymentMaster(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    CreatedUserID = data['CreatedUserID']

    if PaymentMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = PaymentMaster.objects.get(pk=pk)
        company_instance = CompanySettings.objects.get(pk=CompanyID.id)
        serialized = PaymentMasterRestSerializer(
            instance, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding})
        company_serialized = CompanySettingsRestSerializer(
            company_instance, context={"request": request})

        #request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Payment', 'View Payment',
        #              'Payment Single Page Viewed successfully.', 'Payment Single Page Viewed successfully')
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data,
            "company_data": company_serialized.data,
        }
    else:
        #request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Payment',
        #              'View Payment', 'Payment Single Page Viewed Failed.', 'Payment Not Found!')
        response_data = {
            "StatusCode": 6001,
            "message": "Payment Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_paymentMaster(request, pk):
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
        if PaymentMaster.objects.filter(CompanyID=CompanyID, pk__in=selecte_ids).exists():
            instances = PaymentMaster.objects.filter(pk__in=selecte_ids)
    else:
        if PaymentMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instances = PaymentMaster.objects.filter(pk=pk)

    ledgerPostInstances = None

    if instances:
        for instance in instances:
            # instance = PaymentMaster.objects.get(pk=pk)
            PaymentMasterID = instance.PaymentMasterID
            BranchID = instance.BranchID
            VoucherNo = instance.VoucherNo
            VoucherType = instance.VoucherType
            LedgerID = instance.LedgerID
            EmployeeID = instance.EmployeeID
            PaymentNo = instance.PaymentNo
            FinancialYearID = instance.FinancialYearID
            Date = instance.Date
            TotalAmount = instance.TotalAmount
            Notes = instance.Notes
            IsActive = instance.IsActive
            Action = "D"

            PaymentMaster_Log.objects.create(
                TransactionID=PaymentMasterID,
                BranchID=BranchID,
                Action=Action,
                VoucherNo=VoucherNo,
                VoucherType=VoucherType,
                LedgerID=LedgerID,
                EmployeeID=EmployeeID,
                PaymentNo=PaymentNo,
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

            detail_instances = PaymentDetails.objects.filter(
                CompanyID=CompanyID, PaymentMasterID=PaymentMasterID, BranchID=BranchID, VoucherType=VoucherType)

            for detail_instance in detail_instances:
                PaymentDetailsID = detail_instance.PaymentDetailsID
                BranchID = detail_instance.BranchID
                PaymentMasterID = detail_instance.PaymentMasterID
                PaymentGateway = detail_instance.PaymentGateway
                RefferenceNo = detail_instance.RefferenceNo
                CardNetwork = detail_instance.CardNetwork
                PaymentStatus = detail_instance.PaymentStatus
                DueDate = detail_instance.DueDate
                LedgerID = detail_instance.LedgerID
                Amount = detail_instance.Amount
                Balance = detail_instance.Balance
                Discount = detail_instance.Discount
                NetAmount = detail_instance.NetAmount
                Narration = detail_instance.Narration
                CreatedUserID = detail_instance.CreatedUserID
                UpdatedUserID = detail_instance.UpdatedUserID

                PaymentDetails_Log.objects.create(
                    TransactionID=PaymentDetailsID,
                    BranchID=BranchID,
                    Action=Action,
                    PaymentMasterID=PaymentMasterID,
                    PaymentGateway=PaymentGateway,
                    RefferenceNo=RefferenceNo,
                    CardNetwork=CardNetwork,
                    PaymentStatus=PaymentStatus,
                    DueDate=DueDate,
                    LedgerID=LedgerID,
                    Amount=Amount,
                    Balance=Balance,
                    Discount=Discount,
                    NetAmount=NetAmount,
                    Narration=Narration,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    UpdatedUserID=UpdatedUserID,
                    CompanyID=CompanyID,
                    VoucherType=VoucherType
                )

                detail_instance.delete()

            if LedgerPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PaymentMasterID, BranchID=BranchID, VoucherType=VoucherType).exists():
                ledgerPostInstances = LedgerPosting.objects.filter(
                    CompanyID=CompanyID, VoucherMasterID=PaymentMasterID, BranchID=BranchID, VoucherType=VoucherType)

                update_ledger = UpdateLedgerBalance(
                    CompanyID, BranchID, 0, PaymentMasterID, VoucherType, 0, "Cr", "update")
                for ledgerPostInstance in ledgerPostInstances:
                    LedgerPostingID = ledgerPostInstance.LedgerPostingID
                    VoucherType = ledgerPostInstance.VoucherType
                    Debit = ledgerPostInstance.Debit
                    Credit = ledgerPostInstance.Credit
                    IsActive = ledgerPostInstance.IsActive
                    Date = ledgerPostInstance.Date
                    LedgerID = ledgerPostInstance.LedgerID
                    CreatedUserID = ledgerPostInstance.CreatedUserID
                    PaymentDetailsID = ledgerPostInstance.VoucherDetailID

                    LedgerPosting_Log.objects.create(
                        TransactionID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=Date,
                        VoucherMasterID=PaymentMasterID,
                        VoucherDetailID=PaymentDetailsID,
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
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Payment',
                     'Delete', 'Payment Deleted Successfully.', 'Payment Deleted Successfully.')

        response_data = {
            "StatusCode": 6000,
            "message": "Payment Master Deleted Successfully!",
            "title": "Success",
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID,
                     'Payment', 'Delete', 'Payment Deleted Failed.', 'Payment Not Found!')
        response_data = {
            "StatusCode": 6001,
            "message": "Payment Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def search_payments(request):
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
        if PaymentMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType).exists():
            instances = PaymentMaster.objects.filter(
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
            serialized = PaymentMasterRestSerializer(instances, many=True, context={
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
def report_payments(request):
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
        df, details = query_payment_report_data(
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
        # if PaymentMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType, Date__gte=FromDate, Date__lte=ToDate).exists():
        #     instances = PaymentMaster.objects.filter(
        #         CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType, Date__gte=FromDate, Date__lte=ToDate)
        #     final_data = []
        #     new_final_data = []
        #     tot_Discount = 0
        #     tot_Amount = 0
        #     tot_NetAmount = 0
        #     detail_ins = None
        #     for i in instances:
        #         PaymentMasterID = i.PaymentMasterID
        #         if PaymentDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID).exists():
        #             if PaymentDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID, LedgerID__in=LedgerList).exists():
        #                 detail_ins = PaymentDetails.objects.filter(
        #                     CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID, LedgerID__in=LedgerList)
        #             else:
        #                 detail_ins = PaymentDetails.objects.filter(
        #                     CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID)

        #             for l in detail_ins:
        #                 LedgerName = AccountLedger.objects.get(
        #                     CompanyID=CompanyID, BranchID=BranchID, LedgerID=l.LedgerID).LedgerName
        #                 voucher_type = get_voucher_type(i.VoucherType)
        #                 virtual_dictionary = {"VoucherNo": i.VoucherNo, "Date": i.Date, "LedgerName": LedgerName,
        #                                       "VoucherType": voucher_type, "Amount": l.Amount, "Discount": l.Discount, "NetAmount": l.NetAmount, "Narration": l.Narration}
        #                 # final_data.append(virtual_dictionary)
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
        #             "message": "Payment details not found!"
        #         }
        #         return Response(response_data, status=status.HTTP_200_OK)

        # elif PaymentMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists() and VoucherType == "All":
        #     instances = PaymentMaster.objects.filter(
        #         CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)

        #     final_data = []
        #     new_final_data = []
        #     tot_Discount = 0
        #     tot_Amount = 0
        #     tot_NetAmount = 0
        #     for i in instances:
        #         PaymentMasterID = i.PaymentMasterID
        #         if PaymentDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID).exists():
        #             if LedgerList:
        #                 detail_ins = PaymentDetails.objects.filter(
        #                     CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID, LedgerID__in=LedgerList)
        #             else:
        #                 detail_ins = PaymentDetails.objects.filter(
        #                     CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID)
        #             for l in detail_ins:
        #                 LedgerName = AccountLedger.objects.get(
        #                     CompanyID=CompanyID, BranchID=BranchID, LedgerID=l.LedgerID).LedgerName
        #                 voucher_type = get_voucher_type(i.VoucherType)
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
        #         "message": "Payment details not found!"
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
def paymentReport_excel(request):
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
    LedgerList = [x for x in LedgerList if x]
    for x in LedgerList:
        print(str(x).split(','))
        test_list = str(x).split(',')
        for i in range(0, len(test_list)):
            test_list[i] = int(test_list[i])
        LedgerList = test_list

    response = HttpResponse(content_type='application/ms-excel')

    # decide file name
    response['Content-Disposition'] = 'attachment; filename="Payment Report.xls"'

    # creating workbook
    wb = xlwt.Workbook(encoding='utf-8')

    data = paymentReport_excel_data(
        CompanyID, BranchID, PriceRounding, VoucherType, LedgerList, FromDate, ToDate)
    print(data)
    title = str(CompanyID.CompanyName) + str(",") + \
        str(FromDate)+str(' To ')+str(ToDate)
    export_to_excel_paymentReport(wb, data, title)

    wb.save(response)
    return response


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def billwise_list_customer(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    CreatedUserID = data['CreatedUserID']
    BranchID = data['BranchID']
    LedgerID = data['LedgerID']
    call_type = data['call_type']
    PaymentVoucherNo = data['PaymentVoucherNo']
    PaymentVoucherType = data['PaymentVoucherType']
    
    if call_type == "create":
        if BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, CustomerID=LedgerID, InvoiceAmount__gt=F('Payments')).exists():
            bill_wise_instances = BillWiseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, CustomerID=LedgerID, InvoiceAmount__gt=F('Payments'))
            serialized = BillwiseMasterSerializer(bill_wise_instances, many=True,context={
                "CompanyID": CompanyID, "PaymentVoucherNo": PaymentVoucherNo, "PaymentVoucherType": PaymentVoucherType, "call_type": call_type})

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "no billwise found"
            }
    else:
        if BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, CustomerID=LedgerID).exists():
            bill_wise_instances = BillWiseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, CustomerID=LedgerID)
            serialized = BillwiseMasterSerializer(bill_wise_instances, many=True, context={
                "CompanyID": CompanyID, "PaymentVoucherNo": PaymentVoucherNo, "PaymentVoucherType": PaymentVoucherType, "call_type": call_type})

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "no billwise found"
            }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def billwise_details(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    VoucherNo = data['VoucherNo']
    VoucherType = data['VoucherType']

    if BillWiseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType, InvoiceNo=VoucherNo, Payments__gt=0).exists():
        bill_wise_instances = BillWiseDetails.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType, InvoiceNo=VoucherNo, Payments__gt=0)
        serialized = BillwiseDetailsSerializer(
            bill_wise_instances, many=True, context={"CompanyID": CompanyID})

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "no billwise found"
        }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def list_allpaymentDetails(request):
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

        if PaymentDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            if page_number and items_per_page:
                instances = PaymentDetails.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                count = len(instances)
                ledger_sort_pagination = list_pagination(
                    instances,
                    items_per_page,
                    page_number
                )
                serialized = PaymentDetailsListSerializer(ledger_sort_pagination, many=True, context={
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
                "message": "No Payments"
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
def search_payment_list(request):
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
        if PaymentDetails.objects.filter(
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
                instances = PaymentDetails.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID
                )
                instances = instances.filter(

                    (Q(LedgerID__in=ledger_ids))
                )[:10]
            else:
                instances = PaymentDetails.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID
                )
                instances = instances.filter(
                     (Q(LedgerID__in=ledger_ids))
                )
            serialized = PaymentDetailsListSerializer(
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

