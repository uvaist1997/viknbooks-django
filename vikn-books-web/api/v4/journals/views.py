from brands.models import JournalMaster, JournalMaster_Log, JournalDetails, JournalDetails_Log, LedgerPosting, LedgerPosting_Log, JournalDetailsDummy, FinancialYear,\
    GeneralSettings
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v4.journals.serializers import JournalMasterSerializer, JournalMasterRestSerializer, JournalDetailsSerializer, JournalDetailsRestSerializer
from api.v4.brands.serializers import ListSerializer
from api.v4.journals.functions import generate_serializer_errors
from rest_framework import status
from api.v4.journals.functions import get_auto_id, get_auto_idMaster
from api.v4.sales.functions import get_auto_VoucherNo
import datetime
from api.v4.accountLedgers.functions import get_auto_LedgerPostid
from main.functions import get_company, activity_log
from api.v4.sales.functions import get_Genrate_VoucherNo
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Prefetch


def call_paginator_all(model_object, page_number, items_per_page):
    paginator = Paginator(model_object, items_per_page)
    content = paginator.page(page_number)
    return content


def list_pagination(list_value, items_per_page, page_no):
    paginator_object = Paginator(list_value, items_per_page)
    get_value = paginator_object.page(page_no).object_list
    return get_value


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_journal(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    BranchID = data['BranchID']
    VoucherNo = data['VoucherNo']
    Date = data['Date']
    Notes = data['Notes']
    TotalDebit = data['TotalDebit']
    TotalCredit = data['TotalCredit']
    Difference = data['Difference']
    IsActive = data['IsActive']
    Action = "A"

    VoucherNoLow = VoucherNo.lower()
    is_voucherExist = False
    insts = JournalMaster.objects.filter(
        BranchID=BranchID, CompanyID=CompanyID)
    if insts:
        for i in insts:
            voucher_no = i.VoucherNo
            voucherNo = voucher_no.lower()
            if VoucherNoLow == voucherNo:
                is_voucherExist = True

    check_VoucherNoAutoGenerate = False
    is_JournalOK = True

    if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="VoucherNoAutoGenerate").exists():
        check_VoucherNoAutoGenerate = GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="VoucherNoAutoGenerate").SettingsValue

    if is_voucherExist == True and check_VoucherNoAutoGenerate == "True":
        VoucherNo = get_Genrate_VoucherNo(
            JournalMaster, BranchID, CompanyID, "JL")
        is_JournalOK = True
    elif is_voucherExist == False:
        is_JournalOK = True
    else:
        is_JournalOK = False

    if is_JournalOK:

        JournalMasterID = get_auto_idMaster(JournalMaster, BranchID, CompanyID)
        JournalMaster_Log.objects.create(
            TransactionID=JournalMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            Date=Date,
            Notes=Notes,
            TotalDebit=TotalDebit,
            TotalCredit=TotalCredit,
            Difference=Difference,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            CompanyID=CompanyID,
        )

        JournalMaster.objects.create(
            JournalMasterID=JournalMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            Date=Date,
            Notes=Notes,
            TotalDebit=TotalDebit,
            TotalCredit=TotalCredit,
            Difference=Difference,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            CompanyID=CompanyID,
        )

        journalDetailsLogs = data["JournalDetails"]

        for journalDetailLog in journalDetailsLogs:

            LedgerID = journalDetailLog['LedgerID']
            Debit = journalDetailLog['Debit']
            Credit = journalDetailLog['Credit']
            Narration = journalDetailLog['Narration']

            JournalDetailsID = get_auto_id(JournalDetails, BranchID, CompanyID)

            ledger_instance = JournalDetails_Log.objects.create(
                TransactionID=JournalDetailsID,
                BranchID=BranchID,
                JournalMasterID=JournalMasterID,
                LedgerID=LedgerID,
                Debit=Debit,
                Credit=Credit,
                Narration=Narration,
                Action=Action,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            JournalDetails.objects.create(
                JournalDetailsID=JournalDetailsID,
                BranchID=BranchID,
                JournalMasterID=JournalMasterID,
                LedgerID=LedgerID,
                Debit=Debit,
                Credit=Credit,
                Narration=Narration,
                Action=Action,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
                LogID=ledger_instance.ID
            )


            VoucherType = "JL"

            LedgerPostingID = get_auto_LedgerPostid(
                LedgerPosting, BranchID, CompanyID)

            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=JournalMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
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

            LedgerPosting_Log.objects.create(
                TransactionID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=JournalMasterID,
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
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Journal',
                     'Create', 'Journal created successfully.', 'Journal saved successfully.')

        response_data = {
            "StatusCode": 6000,
            "message": "Journal created Successfully!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Journal',
                     'Create', 'Journal created Failed.', 'VoucherNo already exist')
        response_data = {
            "StatusCode": 6001,
            "message": "VoucherNo already exist!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_journal(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()

    journalMaster_instance = None
    journalDetails = None
    journalMaster_instance = JournalMaster.objects.get(
        pk=pk, CompanyID=CompanyID)
    JournalMasterID = journalMaster_instance.JournalMasterID
    BranchID = journalMaster_instance.BranchID
    VoucherNo = journalMaster_instance.VoucherNo
    # VoucherType = journalMaster_instance.VoucherType

    VoucherType = "JL"

    Date = data['Date']
    Notes = data['Notes']
    TotalDebit = data['TotalDebit']
    TotalCredit = data['TotalCredit']
    Difference = data['Difference']
    IsActive = data['IsActive']

    Action = "M"

    JournalMaster_Log.objects.create(
        TransactionID=JournalMasterID,
        BranchID=BranchID,
        VoucherNo=VoucherNo,
        Date=Date,
        Notes=Notes,
        TotalDebit=TotalDebit,
        TotalCredit=TotalCredit,
        Difference=Difference,
        IsActive=IsActive,
        Action=Action,
        CreatedUserID=CreatedUserID,
        CreatedDate=today,
        UpdatedDate=today,
        CompanyID=CompanyID,
    )

    if LedgerPosting.objects.filter(VoucherMasterID=JournalMasterID, BranchID=BranchID, CompanyID=CompanyID, VoucherType=VoucherType).exists():
        ledgerPostInstances = LedgerPosting.objects.filter(
            VoucherMasterID=JournalMasterID, BranchID=BranchID, CompanyID=CompanyID, VoucherType=VoucherType)
        for ledgerPostInstance in ledgerPostInstances:
            ledgerPostInstance.delete()

    if JournalDetails.objects.filter(JournalMasterID=JournalMasterID, BranchID=BranchID, CompanyID=CompanyID).exists():
        journalDetailInstances = JournalDetails.objects.filter(
            JournalMasterID=JournalMasterID, BranchID=BranchID, CompanyID=CompanyID)
        for journalDetailInstance in journalDetailInstances:
            journalDetailInstance.delete()

    

    journalMaster_instance.Date = Date
    journalMaster_instance.Notes = Notes
    journalMaster_instance.TotalDebit = TotalDebit
    journalMaster_instance.TotalCredit = TotalCredit
    journalMaster_instance.Difference = Difference
    journalMaster_instance.IsActive = IsActive
    journalMaster_instance.UpdatedDate = today
    journalMaster_instance.CreatedUserID = CreatedUserID
    journalMaster_instance.Action = Action

    journalMaster_instance.save()

    journalDetails = data["JournalDetails"]

    for journalDetail in journalDetails:

        detailID = journalDetail['detailID']
        LedgerID = journalDetail['LedgerID']
        Debit = journalDetail['Debit']
        Credit = journalDetail['Credit']
        Narration = journalDetail['Narration']

        if detailID == 0:
            JournalDetailsID = get_auto_id(JournalDetails, BranchID, CompanyID)

            log_instance = JournalDetails_Log.objects.create(
                TransactionID=JournalDetailsID,
                BranchID=BranchID,
                JournalMasterID=JournalMasterID,
                LedgerID=LedgerID,
                Debit=Debit,
                Credit=Credit,
                Narration=Narration,
                Action=Action,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )
            JournalDetails.objects.create(
                JournalDetailsID=JournalDetailsID,
                BranchID=BranchID,
                JournalMasterID=JournalMasterID,
                LedgerID=LedgerID,
                Debit=Debit,
                Credit=Credit,
                Narration=Narration,
                Action=Action,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
                LogID=log_instance.ID
            )


            VoucherType = "JL"

            LedgerPostingID = get_auto_LedgerPostid(
                LedgerPosting, BranchID, CompanyID)

            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=JournalMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
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

            LedgerPosting_Log.objects.create(
                TransactionID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=JournalMasterID,
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

        if detailID == 1:
            Action = "A"
            JournalDetailsID = get_auto_id(JournalDetails, BranchID, CompanyID)

            log_instance = JournalDetails_Log.objects.create(
                TransactionID=JournalDetailsID,
                BranchID=BranchID,
                JournalMasterID=JournalMasterID,
                LedgerID=LedgerID,
                Debit=Debit,
                Credit=Credit,
                Narration=Narration,
                Action=Action,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            JournalDetails.objects.create(
                JournalDetailsID=JournalDetailsID,
                BranchID=BranchID,
                JournalMasterID=JournalMasterID,
                LedgerID=LedgerID,
                Debit=Debit,
                Credit=Credit,
                Narration=Narration,
                Action=Action,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
                LogID=log_instance.ID
            )

            VoucherType = "JL"

            LedgerPostingID = get_auto_LedgerPostid(
                LedgerPosting, BranchID, CompanyID)

            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=JournalMasterID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
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

            LedgerPosting_Log.objects.create(
                TransactionID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=JournalMasterID,
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

    
    #request , company, log_type, user, source, action, message, description
    activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Journal',
                 'Edit', 'Journal Updated successfully.', 'Journal Updated successfully.')

    response_data = {
        "StatusCode": 6000,
        "message": "Journal Updated Successfully!!!",
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def journals(request):
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

        if JournalMaster.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():

            if page_number and items_per_page:
                instances = JournalMaster.objects.filter(
                    BranchID=BranchID, CompanyID=CompanyID)
                count = len(instances)
                ledger_sort_pagination = list_pagination(
                    instances,
                    items_per_page,
                    page_number
                )
            else:
                ledger_sort_pagination = JournalMaster.objects.filter(
                    BranchID=BranchID, CompanyID=CompanyID)
                count = len(ledger_sort_pagination)

            serialized = JournalMasterRestSerializer(ledger_sort_pagination, many=True, context={"CompanyID": CompanyID,
                                                                                                 "PriceRounding": PriceRounding})

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Journal',
                         'View', 'Journal List Viewed successfully.', 'User Viewed Journal List.')
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "count": count,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Journal', 'View',
                         'Journal List Viewed Failed.', 'Journal List is Not Foound Under this Branch.')
            response_data = {
                "StatusCode": 6001,
                "message": "Journal Master not found in this branch."
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch you enterd is not valid."
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def journal(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    instance = None
    if JournalMaster.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = JournalMaster.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = JournalMasterRestSerializer(instance, context={"CompanyID": CompanyID,
                                                                    "PriceRounding": PriceRounding})

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Journal', 'View',
                     'Journal Single Page Viewed Successfully.', 'Journal Single Page Viewed Successfully.')
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Journal',
                     'View', 'Journal Single Page Viewed Failed.', 'Journal Not Found')
        response_data = {
            "StatusCode": 6001,
            "message": "Journal Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_journalDetail(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    instance = None
    if JournalDetails.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = JournalDetails.objects.get(pk=pk, CompanyID=CompanyID)
        JournalDetailsID = instance.JournalDetailsID
        BranchID = instance.BranchID
        JournalMasterID = instance.JournalMasterID
        LedgerID = instance.LedgerID
        Debit = instance.Debit
        Credit = instance.Credit
        Narration = instance.Narration
        Action = "D"

        instance.delete()

        JournalDetails_Log.objects.create(
            TransactionID=JournalDetailsID,
            BranchID=BranchID,
            JournalMasterID=JournalMasterID,
            LedgerID=LedgerID,
            Debit=Debit,
            Credit=Credit,
            Narration=Narration,
            Action=Action,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            CompanyID=CompanyID,
        )
        response_data = {
            "StatusCode": 6000,
            "message": "Journal Details Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Journal Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_journal(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    instance = None
    ledgerPostInstances = None

    if JournalMaster.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = JournalMaster.objects.get(pk=pk, CompanyID=CompanyID)
    if instance:
        JournalMasterID = instance.JournalMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        Date = instance.Date
        Notes = instance.Notes
        TotalDebit = instance.TotalDebit
        TotalCredit = instance.TotalCredit
        Difference = instance.Difference
        IsActive = instance.IsActive
        Action = "D"

        VoucherType = "JL"

        JournalMaster_Log.objects.create(
            TransactionID=JournalMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            Date=Date,
            Notes=Notes,
            TotalDebit=TotalDebit,
            TotalCredit=TotalCredit,
            Difference=Difference,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            CompanyID=CompanyID,
        )


        detail_instances = JournalDetails.objects.filter(
            JournalMasterID=JournalMasterID, BranchID=BranchID, CompanyID=CompanyID)

        for detail_instance in detail_instances:

            JournalDetailsID = detail_instance.JournalDetailsID
            BranchID = detail_instance.BranchID
            JournalMasterID = detail_instance.JournalMasterID
            LedgerID = detail_instance.LedgerID
            Debit = detail_instance.Debit
            Credit = detail_instance.Credit
            Narration = detail_instance.Narration

            detail_instance.delete()

            JournalDetails_Log.objects.create(
                TransactionID=JournalDetailsID,
                BranchID=BranchID,
                JournalMasterID=JournalMasterID,
                LedgerID=LedgerID,
                Debit=Debit,
                Credit=Credit,
                Narration=Narration,
                Action=Action,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

        if LedgerPosting.objects.filter(VoucherMasterID=JournalMasterID, BranchID=BranchID, CompanyID=CompanyID, VoucherType=VoucherType).exists():
            ledgerPostInstances = LedgerPosting.objects.filter(
                VoucherMasterID=JournalMasterID, BranchID=BranchID, CompanyID=CompanyID, VoucherType=VoucherType)

            for ledgerPostInstance in ledgerPostInstances:

                LedgerPostingID = ledgerPostInstance.LedgerPostingID
                VoucherType = ledgerPostInstance.VoucherType
                Debit = ledgerPostInstance.Debit
                Credit = ledgerPostInstance.Credit
                IsActive = ledgerPostInstance.IsActive
                Date = ledgerPostInstance.Date
                LedgerID = ledgerPostInstance.LedgerID

                ledgerPostInstance.delete()

                LedgerPosting_Log.objects.create(
                    TransactionID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=JournalMasterID,
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

        instance.delete()

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Journal',
                     'Delete', 'Journal Deleted Successfully', 'Journal Deleted Successfully')
        response_data = {
            "StatusCode": 6000,
            "title": "Success",
            "message": "Journal Deleted Successfully!"
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID,
                     'Journal', 'Delete', 'Journal Deleted Failed', 'Journal Not Found')
        response_data = {
            "StatusCode": 6001,
            "title": "Failed!",
            "message": "Journal Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def search_journals(request):
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
        if JournalMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instances = JournalMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

            if length < 3:
                if param == "VoucherNo":
                    instances = instances.filter(
                        (Q(VoucherNo__icontains=product_name)))[:10]
                else:
                    instances = instances.filter(
                        (Q(Date__icontains=product_name)))[:10]
            else:
                if param == "VoucherNo":
                    instances = instances.filter(
                        (Q(VoucherNo__icontains=product_name)))
                else:
                    instances = instances.filter(
                        (Q(Date__icontains=product_name)))
            serialized = JournalMasterRestSerializer(instances, many=True, context={
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
