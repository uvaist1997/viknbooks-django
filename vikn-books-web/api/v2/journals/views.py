from brands.models import JournalMaster, JournalMaster_Log, JournalDetails, JournalDetails_Log, LedgerPosting, LedgerPosting_Log, JournalDetailsDummy,FinancialYear
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v2.journals.serializers import JournalMasterSerializer, JournalMasterRestSerializer, JournalDetailsSerializer, JournalDetailsRestSerializer
from api.v2.brands.serializers import ListSerializer
from api.v2.journals.functions import generate_serializer_errors
from rest_framework import status
from api.v2.journals.functions import get_auto_id, get_auto_idMaster
from api.v2.sales.functions import get_auto_VoucherNo
import datetime
from api.v2.accountLedgers.functions import get_auto_LedgerPostid
from main.functions import get_company, activity_log



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
    insts = JournalMaster.objects.filter(BranchID=BranchID,CompanyID=CompanyID)
    if insts:
        for i in insts:
            voucher_no = i.VoucherNo
            voucherNo = voucher_no.lower()
            if VoucherNoLow == voucherNo:
                is_voucherExist = True

    if not is_voucherExist:

        JournalMasterID = get_auto_idMaster(JournalMaster,BranchID, CompanyID)
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

        journalDetails = data["JournalDetails"]

        for journalDetail in journalDetails:

            LedgerID = journalDetail['LedgerID']
            Debit = journalDetail['Debit']
            Credit = journalDetail['Credit']
            Narration = journalDetail['Narration']

            JournalDetailsID = get_auto_id(JournalDetails,BranchID, CompanyID)

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
                )

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


            VoucherType = "JL"

            LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID, CompanyID)

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
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Journal', 'Create', 'Journal created successfully.', 'Journal saved successfully.')

        response_data = {
            "StatusCode" : 6000,
            "message" : "Journal created Successfully!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Journal', 'Create', 'Journal created Failed.', 'VoucherNo already exist')
        response_data = {
        "StatusCode" : 6001,
        "message" : "VoucherNo already exist!"
        }

        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_journal(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    
    journalMaster_instance = None
    journalDetails = None
    journalMaster_instance = JournalMaster.objects.get(pk=pk,CompanyID=CompanyID)
    JournalMasterID = journalMaster_instance.JournalMasterID
    BranchID = journalMaster_instance.BranchID
    VoucherNo = journalMaster_instance.VoucherNo

    if LedgerPosting.objects.filter(VoucherMasterID=JournalMasterID,BranchID=BranchID,CompanyID=CompanyID).exists():
        ledgerPostInstances = LedgerPosting.objects.filter(VoucherMasterID=JournalMasterID,BranchID=BranchID,CompanyID=CompanyID) 
        for ledgerPostInstance in ledgerPostInstances:
            ledgerPostInstance.delete()

    if JournalDetails.objects.filter(JournalMasterID=JournalMasterID,BranchID=BranchID,CompanyID=CompanyID).exists():
        journalDetailInstances = JournalDetails.objects.filter(JournalMasterID=JournalMasterID,BranchID=BranchID,CompanyID=CompanyID)
        for journalDetailInstance in journalDetailInstances:
            journalDetailInstance.delete()

    Date = data['Date']
    Notes = data['Notes']
    TotalDebit = data['TotalDebit']
    TotalCredit = data['TotalCredit']
    Difference = data['Difference']
    IsActive = data['IsActive']

    Action = "M"

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

    journalDetails = data["JournalDetails"]

    for journalDetail in journalDetails:

        detailID = journalDetail['detailID']
        LedgerID = journalDetail['LedgerID']
        Debit = journalDetail['Debit']
        Credit = journalDetail['Credit']
        Narration = journalDetail['Narration']

        if detailID==0:
            JournalDetailsID = get_auto_id(JournalDetails,BranchID,CompanyID)
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
                )

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


            VoucherType = "JL"

            LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

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

        if detailID==1:
            Action = "A"
            JournalDetailsID = get_auto_id(JournalDetails,BranchID,CompanyID)

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
                )

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

            VoucherType = "JL"

            LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

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
    activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Journal', 'Edit', 'Journal Updated successfully.', 'Journal Updated successfully.')

    response_data = {
        "StatusCode" : 6000,
        "message" : "Journal Updated Successfully!!!",
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
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']
        
        if JournalMaster.objects.filter(BranchID=BranchID,CompanyID=CompanyID).exists():

            instances = JournalMaster.objects.filter(BranchID=BranchID,CompanyID=CompanyID)

            serialized = JournalMasterRestSerializer(instances,many=True,context = {"CompanyID": CompanyID,
            "PriceRounding" : PriceRounding })

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Journal', 'View', 'Journal List Viewed successfully.', 'User Viewed Journal List.')
            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Journal', 'View', 'Journal List Viewed Failed.', 'Journal List is Not Foound Under this Branch.')
            response_data = {
            "StatusCode" : 6001,
            "message" : "Journal Master not found in this branch."
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Branch you enterd is not valid."
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def journal(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    instance = None
    if JournalMaster.objects.filter(pk=pk,CompanyID=CompanyID).exists():
        instance = JournalMaster.objects.get(pk=pk,CompanyID=CompanyID)
        serialized = JournalMasterRestSerializer(instance,context = {"CompanyID": CompanyID,
        "PriceRounding" : PriceRounding })

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Journal', 'View', 'Journal Single Page Viewed Successfully.', 'Journal Single Page Viewed Successfully.')
        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Journal', 'View', 'Journal Single Page Viewed Failed.', 'Journal Not Found')
        response_data = {
            "StatusCode" : 6001,
            "message" : "Journal Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_journalDetail(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    instance = None
    if JournalDetails.objects.filter(pk=pk,CompanyID=CompanyID).exists():
        instance = JournalDetails.objects.get(pk=pk,CompanyID=CompanyID)
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
            "StatusCode" : 6000,
            "message" : "Journal Details Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Journal Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_journal(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    instance = None
    ledgerPostInstances = None
    
    if JournalMaster.objects.filter(pk=pk,CompanyID=CompanyID).exists():
        instance = JournalMaster.objects.get(pk=pk,CompanyID=CompanyID)
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

        instance.delete()

        detail_instances = JournalDetails.objects.filter(JournalMasterID=JournalMasterID,BranchID=BranchID,CompanyID=CompanyID)

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

        if LedgerPosting.objects.filter(VoucherMasterID=JournalMasterID,BranchID=BranchID,CompanyID=CompanyID).exists():
            ledgerPostInstances = LedgerPosting.objects.filter(VoucherMasterID=JournalMasterID,BranchID=BranchID,CompanyID=CompanyID)
            
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

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Journal', 'Delete', 'Journal Deleted Successfully', 'Journal Deleted Successfully')
        response_data = {
            "StatusCode" : 6000,
            "title" : "Success",
            "message" : "Journal Deleted Successfully!"
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Journal', 'Delete', 'Journal Deleted Failed', 'Journal Not Found')
        response_data = {
            "StatusCode" : 6001,
            "title" : "Failed!",
            "message" : "Journal Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)