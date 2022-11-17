from brands.models import PaymentMaster, PaymentMaster_Log, PaymentDetails, PaymentDetails_Log, LedgerPosting, LedgerPosting_Log, PaymentDetailsDummy,\
    TransactionTypes, CompanySettings, GeneralSettings, AccountLedger
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v5.payments.serializers import PaymentMasterSerializer, PaymentMasterRestSerializer, PaymentDetailsSerializer, PaymentDetailsRestSerializer
from api.v5.payments.serializers import ListSerializer
from api.v5.payments.functions import generate_serializer_errors
from rest_framework import status
from api.v5.payments.functions import get_auto_id, get_auto_idMaster, get_auto_VoucherNo
from api.v5.accountLedgers.functions import get_auto_LedgerPostid
from main.functions import get_company, activity_log
import datetime
from api.v5.companySettings.serializers import CompanySettingsRestSerializer
from api.v5.sales.functions import get_Genrate_VoucherNo
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Prefetch
from api.v5.receipts.functions import get_voucher_type
from django.db import transaction, IntegrityError
import re
import sys
import os


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
                CompanyID=CompanyID, BranchID=BranchID)
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
                    CompanyID=CompanyID, SettingsType="VoucherNoAutoGenerate").SettingsValue

            if is_voucherExist == True and check_VoucherNoAutoGenerate == "True":
                VoucherNo = get_Genrate_VoucherNo(
                    PaymentMaster, BranchID, CompanyID, VoucherType)
                is_PaymentsOK = True
            elif is_voucherExist == False:
                is_PaymentsOK = True
            else:
                is_PaymentsOK = False

            if is_PaymentsOK:
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

                    

                    if float(Discount) > 0:
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
                            LedgerID=82,
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
                            LedgerID=82,
                            RelatedLedgerID=LedgerID,
                            Credit=Discount,
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
                            VoucherMasterID=PaymentMasterID,
                            VoucherDetailID=PaymentDetailsID,
                            VoucherType=VoucherType,
                            VoucherNo=VoucherNo,
                            LedgerID=LedgerID,
                            RelatedLedgerID=82,
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
                            RelatedLedgerID=82,
                            Debit=Discount,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                #request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Payment',
                #              'Create', 'Payment created successfully.', 'Payment saved successfully.')
                response_data = {
                    "StatusCode": 6000,
                    "message": "Payment created Successfully!!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Payment',
                             'Create', 'Payment created Failed.', 'VoucherNo already exist!')
                response_data = {
                    "StatusCode": 6001,
                    "message": "VoucherNo already exist!"
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

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, payment_type,
                     'Create', str(e), err_descrb)
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
            VoucherType = paymentMaster_instance.VoucherType

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
                CompanyID=CompanyID,
            )

            if LedgerPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PaymentMasterID, BranchID=BranchID, VoucherType=VoucherType).exists():
                ledgerPostInstances = LedgerPosting.objects.filter(
                    CompanyID=CompanyID, VoucherMasterID=PaymentMasterID, BranchID=BranchID, VoucherType=VoucherType)
                for ledgerPostInstance in ledgerPostInstances:
                    ledgerPostInstance.delete()

            if PaymentDetails.objects.filter(CompanyID=CompanyID, PaymentMasterID=PaymentMasterID, BranchID=BranchID, VoucherType=VoucherType).exists():
                paymentDetailInstances = PaymentDetails.objects.filter(
                    CompanyID=CompanyID, PaymentMasterID=PaymentMasterID, BranchID=BranchID, VoucherType=VoucherType)
                for paymentDetailInstance in paymentDetailInstances:
                    paymentDetailInstance.delete()

            paymentMaster_instance.VoucherType = VoucherType
            paymentMaster_instance.LedgerID = MasterLedgerID
            paymentMaster_instance.EmployeeID = EmployeeID
            paymentMaster_instance.FinancialYearID = FinancialYearID
            paymentMaster_instance.Date = Date
            paymentMaster_instance.TotalAmount = TotalAmount
            paymentMaster_instance.Notes = Notes
            paymentMaster_instance.IsActive = IsActive
            paymentMaster_instance.UpdatedDate = today
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
                Discount = paymentsDetailsLog['Discount']
                NetAmount = paymentsDetailsLog['NetAmount']
                Narration = paymentsDetailsLog['Narration']
                detailID = paymentsDetailsLog['detailID']

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

                    # if float(Discount) > 0:
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

                

                if float(Discount) > 0:
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
                        LedgerID=82,
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
                        LedgerID=82,
                        RelatedLedgerID=LedgerID,
                        Credit=Discount,
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
                        VoucherMasterID=PaymentMasterID,
                        VoucherDetailID=PaymentDetailsID,
                        VoucherType=VoucherType,
                        VoucherNo=VoucherNo,
                        LedgerID=LedgerID,
                        RelatedLedgerID=82,
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
                        RelatedLedgerID=82,
                        Debit=Discount,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
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

                    # if float(Discount) > 0:
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

        activity_log(request._request, CompanyID, 'Error', CreatedUserID, payment_type,
                     'Edit', str(e), err_descrb)
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

    today = datetime.datetime.now()
    instance = None
    ledgerPostInstances = None
    if PaymentMaster.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = PaymentMaster.objects.get(pk=pk)
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
                CompanyID=CompanyID,
                VoucherType=VoucherType
            )

            detail_instance.delete()

            if LedgerPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=PaymentMasterID, BranchID=BranchID, VoucherType=VoucherType).exists():
                ledgerPostInstances = LedgerPosting.objects.filter(
                    CompanyID=CompanyID, VoucherMasterID=PaymentMasterID, BranchID=BranchID, VoucherType=VoucherType)

                for ledgerPostInstance in ledgerPostInstances:

                    LedgerPostingID = ledgerPostInstance.LedgerPostingID
                    VoucherType = ledgerPostInstance.VoucherType
                    Debit = ledgerPostInstance.Debit
                    Credit = ledgerPostInstance.Credit
                    IsActive = ledgerPostInstance.IsActive
                    Date = ledgerPostInstance.Date
                    LedgerID = ledgerPostInstance.LedgerID
                    CreatedUserID = ledgerPostInstance.CreatedUserID

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
                else:
                    ledger_ids = []
                    if AccountLedger.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerName__icontains=product_name).exists():
                        ledger_ins = AccountLedger.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, LedgerName__icontains=product_name)
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

        if PaymentMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType, Date__gte=FromDate, Date__lte=ToDate).exists():
            instances = PaymentMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, VoucherType=VoucherType, Date__gte=FromDate, Date__lte=ToDate)
            final_data = []
            for i in instances:
                PaymentMasterID = i.PaymentMasterID
                if PaymentDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID).exists():
                    if detail_ins:
                        detail_ins = PaymentDetails.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID, LedgerID__in=LedgerList)
                    else:
                        detail_ins = PaymentDetails.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID)
                    for l in detail_ins:
                        LedgerName = AccountLedger.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, LedgerID=l.LedgerID).LedgerName
                        voucher_type = get_voucher_type(i.VoucherType)
                        virtual_dictionary = {"VoucherNo": i.VoucherNo, "Date": i.Date, "LedgerName": LedgerName,
                                              "VoucherType": voucher_type, "Amount": l.Amount, "Discount": l.Discount, "NetAmount": l.NetAmount, "Narration": l.Narration}
                        final_data.append(virtual_dictionary)

            if final_data:
                response_data = {
                    "StatusCode": 6000,
                    "data": final_data
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "Receipt details not found!"
                }
                return Response(response_data, status=status.HTTP_200_OK)

        elif PaymentMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate).exists():
            instances = PaymentMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Date__gte=FromDate, Date__lte=ToDate)

            final_data = []
            for i in instances:
                PaymentMasterID = i.PaymentMasterID
                if PaymentDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID).exists():
                    if LedgerList:
                        detail_ins = PaymentDetails.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID, LedgerID__in=LedgerList)
                    else:
                        detail_ins = PaymentDetails.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID)
                    for l in detail_ins:
                        LedgerName = AccountLedger.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, LedgerID=l.LedgerID).LedgerName
                        voucher_type = get_voucher_type(i.VoucherType)
                        virtual_dictionary = {"VoucherNo": i.VoucherNo, "Date": i.Date, "LedgerName": LedgerName,
                                              "VoucherType": voucher_type, "Amount": l.Amount, "Discount": l.Discount, "NetAmount": l.NetAmount, "Narration": l.Narration}
                        final_data.append(virtual_dictionary)

            if final_data:
                response_data = {
                    "StatusCode": 6000,
                    "data": final_data
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "Receipt details not found!"
                }
                return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Receipt details not found!"
            }
            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)
