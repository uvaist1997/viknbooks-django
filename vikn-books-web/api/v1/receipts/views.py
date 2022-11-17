from brands.models import ReceiptMaster, ReceiptMaster_Log, ReceiptDetails, ReceiptDetails_Log, LedgerPosting, LedgerPosting_Log, ReceiptDetailsDummy, TransactionTypes,CompanySettings
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v1.receipts.serializers import ReceiptMasterSerializer, ReceiptMasterRestSerializer, ReceiptDetailsSerializer, ReceiptDetailsRestSerializer
from api.v1.payments.serializers import ListSerializer
from api.v1.receipts.functions import generate_serializer_errors
from rest_framework import status
from api.v1.receipts.functions import get_auto_id, get_auto_idMaster
from api.v1.accountLedgers.functions import get_auto_LedgerPostid
import datetime
from datetime import date
from main.functions import get_company, activity_log
from api.v1.companySettings.serializers import CompanySettingsRestSerializer


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_receipt(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

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

    #checking voucher number already exist
    VoucherNoLow = VoucherNo.lower()
    is_voucherExist = False
    insts = ReceiptMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
    if insts:
        for i in insts:
            voucher_no = i.VoucherNo
            voucherNo = voucher_no.lower()
            if VoucherNoLow == voucherNo:
                is_voucherExist = True

    if not is_voucherExist:

        ReceiptMasterID = get_auto_idMaster(ReceiptMaster,BranchID,CompanyID)

        ReceiptNo = str(VoucherType) + str(VoucherNo)

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
            CompanyID=CompanyID,
            )

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
            CompanyID=CompanyID,
            )

        receiptDetails = data["ReceiptDetails"]

        for receiptDetail in receiptDetails:

            PaymentGateway = receiptDetail['PaymentGateway']
            RefferenceNo = receiptDetail['RefferenceNo']
            CardNetwork = receiptDetail['CardNetwork']
            PaymentStatus = receiptDetail['PaymentStatus']
            LedgerID = receiptDetail['LedgerID']
            DueDate = receiptDetail['DueDate']
            Amount = receiptDetail['Amount']
            Discount = receiptDetail['Discount']
            NetAmount = receiptDetail['NetAmount']
            Balance = receiptDetail['Balance']
            Narration = receiptDetail['Narration']


            DueDate = date.today()

            if VoucherType=="CR":
                transactionType = TransactionTypes.objects.get(CompanyID=CompanyID,Name="Cash")
                transactionTypeID = transactionType.TransactionTypesID
                PaymentGateway = transactionTypeID
                
                ReceiptDetailID = get_auto_id(ReceiptDetails,BranchID,CompanyID)
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
                    CompanyID=CompanyID,
                    )

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
                    CompanyID=CompanyID,
                    )

            if VoucherType=="BR":

                ReceiptDetailID = get_auto_id(ReceiptDetails,BranchID,CompanyID)

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
                    CompanyID=CompanyID,
                    )

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
                    CompanyID=CompanyID,
                    )

            LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=ReceiptMasterID,
                VoucherDetailID=ReceiptDetailID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                Credit=Amount,
                IsActive=IsActive,
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
                Credit=Amount,
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
                VoucherMasterID=ReceiptMasterID,
                VoucherDetailID=ReceiptDetailID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=MasterLedgerID,
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
                VoucherNo=VoucherNo,
                VoucherType=VoucherType,
                LedgerID=MasterLedgerID,
                Debit=NetAmount,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
                )

            if float(Discount) > 0:
                LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ReceiptMasterID,
                    VoucherDetailID=ReceiptDetailID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=72,
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
                    LedgerID=72,
                    Debit=Discount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                    )

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Receipt', 'Create', 'Receipt created successfully.', 'Receipt saved successfully.')

        response_data = {
            "StatusCode" : 6000,
            "message" : "Receipt created Successfully!!!",
            "title" : "Success"
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Receipt', 'Create', 'Receipt created Failed.', 'VoucherNo already exist')
        response_data = {
        "StatusCode" : 6001,
        "message" : "VoucherNo already exist!"
        }

        return Response(response_data, status=status.HTTP_200_OK)

   
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_receipt(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    receiptMaster_instance = None
    receiptDetails_instance = None
    receiptDetails = None
    ledgerPostInstances = None

    receiptMaster_instance = ReceiptMaster.objects.get(CompanyID=CompanyID,pk=pk)

    ReceiptMasterID = receiptMaster_instance.ReceiptMasterID
    BranchID = receiptMaster_instance.BranchID
    VoucherNo = receiptMaster_instance.VoucherNo
    ReceiptNo = receiptMaster_instance.ReceiptNo

    if LedgerPosting.objects.filter(CompanyID=CompanyID,VoucherMasterID=ReceiptMasterID,BranchID=BranchID).exists():

        ledgerPostInstances = LedgerPosting.objects.filter(CompanyID=CompanyID,VoucherMasterID=ReceiptMasterID,BranchID=BranchID)
        
        for ledgerPostInstance in ledgerPostInstances:

            ledgerPostInstance.delete()

    if ReceiptDetails.objects.filter(CompanyID=CompanyID,ReceiptMasterID=ReceiptMasterID,BranchID=BranchID).exists():

        receiptDetailInstances = ReceiptDetails.objects.filter(CompanyID=CompanyID,ReceiptMasterID=ReceiptMasterID,BranchID=BranchID)

        for receiptDetailInstance in receiptDetailInstances:

            receiptDetailInstance.delete()

        
    VoucherType = data['VoucherType']
    MasterLedgerID = data['MasterLedgerID']
    EmployeeID = data['EmployeeID']
    FinancialYearID = data['FinancialYearID']
    Date = data['Date']
    TotalAmount = data['TotalAmount']
    Notes = data['Notes']
    IsActive = data['IsActive']

    Action = "M"


    receiptMaster_instance.VoucherType = VoucherType
    receiptMaster_instance.LedgerID = MasterLedgerID
    receiptMaster_instance.EmployeeID = EmployeeID
    receiptMaster_instance.FinancialYearID = FinancialYearID
    receiptMaster_instance.Date = Date
    receiptMaster_instance.TotalAmount = TotalAmount
    receiptMaster_instance.Notes = Notes
    receiptMaster_instance.IsActive = IsActive
    receiptMaster_instance.Action = Action
    receiptMaster_instance.CreatedUserID = CreatedUserID
    receiptMaster_instance.UpdatedDate = today
    receiptMaster_instance.save()

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
        CompanyID=CompanyID,
        )

    receiptDetails = data["ReceiptDetails"]

    for receiptDetail in receiptDetails:

        PaymentGateway = receiptDetail['PaymentGateway']
        RefferenceNo = receiptDetail['RefferenceNo']
        CardNetwork = receiptDetail['CardNetwork']
        PaymentStatus = receiptDetail['PaymentStatus']
        LedgerID = receiptDetail['LedgerID']
        DueDate = receiptDetail['DueDate']
        Amount = receiptDetail['Amount']
        Discount = receiptDetail['Discount']
        NetAmount = receiptDetail['NetAmount']
        Balance = receiptDetail['Balance']
        Narration = receiptDetail['Narration']
        detailID = receiptDetail['detailID']

        DueDate = date.today()
        
        if detailID == 0:
            if VoucherType=="CR":
                transactionType = TransactionTypes.objects.get(CompanyID=CompanyID,Name="Cash")
                transactionTypeID = transactionType.TransactionTypesID
                PaymentGateway = transactionTypeID
                ReceiptDetailID = get_auto_id(ReceiptDetails,BranchID,CompanyID)  
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
                    CompanyID=CompanyID,
                    # receipt_master = receiptMaster_instance,
                    )

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
                    CompanyID=CompanyID,
                    )

            if VoucherType=="BR":

                ReceiptDetailID = get_auto_id(ReceiptDetails,BranchID,CompanyID)

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
                    CompanyID=CompanyID,
                    )

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
                    CompanyID=CompanyID,
                    )

            LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)


            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=ReceiptMasterID,
                VoucherDetailID=ReceiptDetailID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                Credit=Amount,
                IsActive=IsActive,
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
                Credit=Amount,
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
                VoucherMasterID=ReceiptMasterID,
                VoucherDetailID=ReceiptDetailID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=MasterLedgerID,
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
                VoucherNo=VoucherNo,
                VoucherType=VoucherType,
                LedgerID=MasterLedgerID,
                Debit=NetAmount,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
                )

            if float(Discount) > 0:
                LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ReceiptMasterID,
                    VoucherDetailID=ReceiptDetailID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=72,
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
                    LedgerID=72,
                    Debit=Discount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                    )
        if detailID == 1:
            Action = "A"
            if VoucherType=="CR":
                transactionType = TransactionTypes.objects.get(CompanyID=CompanyID,Name="Cash")
                transactionTypeID = transactionType.TransactionTypesID
                PaymentGateway = transactionTypeID  
                ReceiptDetailID = get_auto_id(ReceiptDetails,BranchID,CompanyID)

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
                    CompanyID=CompanyID,
                    )

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
                    CompanyID=CompanyID,
                    )

            if VoucherType=="BR":

                ReceiptDetailID = get_auto_id(ReceiptDetails,BranchID,CompanyID)

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
                    CompanyID=CompanyID,
                    )

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
                    CompanyID=CompanyID,
                    )

            LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)


            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=ReceiptMasterID,
                VoucherDetailID=ReceiptDetailID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                Credit=Amount,
                IsActive=IsActive,
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
                Credit=Amount,
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
                VoucherMasterID=ReceiptMasterID,
                VoucherDetailID=ReceiptDetailID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=MasterLedgerID,
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
                VoucherNo=VoucherNo,
                VoucherType=VoucherType,
                LedgerID=MasterLedgerID,
                Debit=NetAmount,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
                )

            if float(Discount) > 0:
                LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=Date,
                    VoucherMasterID=ReceiptMasterID,
                    VoucherDetailID=ReceiptDetailID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=72,
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
                    LedgerID=72,
                    Debit=Discount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                    )

    #request , company, log_type, user, source, action, message, description
    activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Receipt', 'Edit', 'Receipt Updated Successfully.', 'Receipt Updated Successfully')
    response_data = {
        "StatusCode" : 6000,
        "message" : "Receipt Updated Successfully!!!",
    }

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

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']
        VoucherType = serialized1.data['VoucherType']

        if ReceiptMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,VoucherType=VoucherType).exists():

            instances = ReceiptMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,VoucherType=VoucherType)

            serialized = ReceiptMasterRestSerializer(instances,many=True,context = {"CompanyID": CompanyID,"PriceRounding":PriceRounding })

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Receipt', 'List', 'Receipt List viewed Successfully.', 'Receipt List viewed Successfully.')
            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Receipt', 'List', 'Receipt List viewed Failed.', 'Receipts not found in this branch')
            response_data = {
            "StatusCode" : 6001,
            "message" : "Receipt Master not found in this branch."
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
def receiptMaster(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    
    instance = None
    if ReceiptMaster.objects.filter(CompanyID=CompanyID,pk=pk).exists():
        instance = ReceiptMaster.objects.get(CompanyID=CompanyID,pk=pk)
        company_instance = CompanySettings.objects.get(pk=CompanyID.id)
        serialized = ReceiptMasterRestSerializer(instance,context = {"CompanyID": CompanyID,"PriceRounding":PriceRounding })
        company_serialized = CompanySettingsRestSerializer(company_instance, context={"request": request})

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Receipt', 'View', 'Receipt Single viewed Successfully.', 'Receipt Single viewed Successfully')
        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data,
            "company_data": company_serialized.data,
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Receipt Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_receiptMaster(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if ReceiptMaster.objects.filter(CompanyID=CompanyID,pk=pk).exists():
        instance = ReceiptMaster.objects.get(CompanyID=CompanyID,pk=pk)

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
            CompanyID=CompanyID,
            )

        instance.delete()

        detail_instances = ReceiptDetails.objects.filter(CompanyID=CompanyID,ReceiptMasterID=ReceiptMasterID,BranchID=BranchID)

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
                CompanyID=CompanyID,
                )

            detail_instance.delete()

            if LedgerPosting.objects.filter(CompanyID=CompanyID,VoucherMasterID=ReceiptMasterID,BranchID=BranchID).exists():

                ledgerPostInstances = LedgerPosting.objects.filter(CompanyID=CompanyID,VoucherMasterID=ReceiptMasterID,BranchID=BranchID)
                
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

                    ledgerPostInstance.delete()

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

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Receipt', 'Delete', 'Receipt Deleted Successfully.', 'Receipt Deleted Successfully')
        response_data = {
            "StatusCode" : 6000,
            "message" : "Receipt Master Deleted Successfully!",
            "title" : "Success"
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Receipt Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)