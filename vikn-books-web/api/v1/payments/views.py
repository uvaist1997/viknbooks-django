from brands.models import PaymentMaster, PaymentMaster_Log, PaymentDetails, PaymentDetails_Log, LedgerPosting, LedgerPosting_Log, PaymentDetailsDummy, TransactionTypes,CompanySettings
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v1.payments.serializers import PaymentMasterSerializer, PaymentMasterRestSerializer, PaymentDetailsSerializer, PaymentDetailsRestSerializer
from api.v1.payments.serializers import ListSerializer
from api.v1.payments.functions import generate_serializer_errors
from rest_framework import status
from api.v1.payments.functions import get_auto_id, get_auto_idMaster, get_auto_VoucherNo
from api.v1.accountLedgers.functions import get_auto_LedgerPostid
from main.functions import get_company, activity_log
import datetime
from datetime import date
from api.v1.companySettings.serializers import CompanySettingsRestSerializer


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_payment(request):
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

    #checking voucher number already exist
    VoucherNoLow = VoucherNo.lower()
    is_voucherExist = False
    insts = PaymentMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
    if insts:
        for i in insts:
            voucher_no = i.VoucherNo
            voucherNo = voucher_no.lower()
            if VoucherNoLow == voucherNo:
                is_voucherExist = True

    if not is_voucherExist:

        PaymentMasterID = get_auto_idMaster(PaymentMaster,BranchID,CompanyID)

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
            # CreatedUserID = paymentsDetail['CreatedUserID']

            DueDate = date.today()
                
            if VoucherType=="CP":

                transactionType = TransactionTypes.objects.get(Name="Cash",CompanyID=CompanyID)
                transactionTypeID = transactionType.TransactionTypesID
                PaymentGateway = transactionTypeID

                PaymentDetailsID = get_auto_id(PaymentDetails,BranchID,CompanyID)
            
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
                    )

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
                    )

            if VoucherType=="BP":

                PaymentDetailsID = get_auto_id(PaymentDetails,BranchID,CompanyID)
                
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
                    )

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
                    )

            LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=PaymentMasterID,
                VoucherDetailID=PaymentDetailsID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                Debit=Amount,
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
                Debit=Amount,
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
                VoucherMasterID=PaymentMasterID,
                VoucherDetailID=PaymentDetailsID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=MasterLedgerID,
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
                VoucherNo=VoucherNo,
                VoucherType=VoucherType,
                LedgerID=MasterLedgerID,
                Credit=NetAmount,
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
                    VoucherMasterID=PaymentMasterID,
                    VoucherDetailID=PaymentDetailsID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=82,
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
                    Credit=Discount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                    )

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Payment', 'Create', 'Payment created successfully.', 'Payment saved successfully.')
        response_data = {
            "StatusCode" : 6000,
            "message" : "Payment created Successfully!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Payment', 'Create', 'Payment created Failed.', 'VoucherNo already exist!')
        response_data = {
        "StatusCode" : 6001,
        "message" : "VoucherNo already exist!"
        }

        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_payment(request,pk):
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

    Action = 'M'

    if LedgerPosting.objects.filter(CompanyID=CompanyID,VoucherMasterID=PaymentMasterID,BranchID=BranchID,VoucherType="CP").exists():
        ledgerPostInstances = LedgerPosting.objects.filter(CompanyID=CompanyID,VoucherMasterID=PaymentMasterID,BranchID=BranchID,VoucherType="CP") 
        for ledgerPostInstance in ledgerPostInstances:    
            ledgerPostInstance.delete()

    if PaymentDetails.objects.filter(CompanyID=CompanyID,PaymentMasterID=PaymentMasterID,BranchID=BranchID).exists():
        paymentDetailInstances = PaymentDetails.objects.filter(CompanyID=CompanyID,PaymentMasterID=PaymentMasterID,BranchID=BranchID)
        for paymentDetailInstance in paymentDetailInstances:
            paymentDetailInstance.delete()


    VoucherType = data['VoucherType']
    MasterLedgerID = data['MasterLedgerID']
    EmployeeID = data['EmployeeID']
    FinancialYearID = data['FinancialYearID']
    Date = data['Date']
    TotalAmount = data['TotalAmount']
    Notes = data['Notes']
    IsActive = data['IsActive']


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

    paymentsDetails = data["PaymentDetails"]

    for paymentsDetail in paymentsDetails:

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
        detailID = paymentsDetail['detailID']

        PaymentDetailsID = get_auto_id(PaymentDetails,BranchID,CompanyID)

        DueDate = date.today()
        
        if detailID == 0:

            if VoucherType=="CP":
                transactionType = TransactionTypes.objects.get(Name="Cash",CompanyID=CompanyID)
                transactionTypeID = transactionType.TransactionTypesID
                PaymentGateway = transactionTypeID
                PaymentDetailsID = get_auto_id(PaymentDetails,BranchID,CompanyID)
   
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
                    )

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
                    )

            if VoucherType=="BP":

                PaymentDetailsID = get_auto_id(PaymentDetails,BranchID,CompanyID)
                
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
                    )

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
                    )

            LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)

            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=PaymentMasterID,
                VoucherDetailID=PaymentDetailsID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                Debit=Amount,
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
                Debit=Amount,
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
                VoucherMasterID=PaymentMasterID,
                VoucherDetailID=PaymentDetailsID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=MasterLedgerID,
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
                VoucherNo=VoucherNo,
                VoucherType=VoucherType,
                LedgerID=MasterLedgerID,
                Credit=NetAmount,
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
                    VoucherMasterID=PaymentMasterID,
                    VoucherDetailID=PaymentDetailsID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=82,
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
                    Credit=Discount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                    )
        if detailID == 1:

            Action = "A"

            if VoucherType=="CP":

                transactionType = TransactionTypes.objects.get(Name="Cash",CompanyID=CompanyID)
                transactionTypeID = transactionType.TransactionTypesID
                PaymentGateway = transactionTypeID
                PaymentDetailsID = get_auto_id(PaymentDetails,BranchID,CompanyID)
                
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
                    )

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
                    )

            if VoucherType=="BP":

                PaymentDetailsID = get_auto_id(PaymentDetails,BranchID,CompanyID)
                
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
                    )

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
                    )

            LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID,CompanyID)


            LedgerPosting.objects.create(
                LedgerPostingID=LedgerPostingID,
                BranchID=BranchID,
                Date=Date,
                VoucherMasterID=PaymentMasterID,
                VoucherDetailID=PaymentDetailsID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=LedgerID,
                Debit=Amount,
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
                Debit=Amount,
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
                VoucherMasterID=PaymentMasterID,
                VoucherDetailID=PaymentDetailsID,
                VoucherType=VoucherType,
                VoucherNo=VoucherNo,
                LedgerID=MasterLedgerID,
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
                VoucherNo=VoucherNo,
                VoucherType=VoucherType,
                LedgerID=MasterLedgerID,
                Credit=NetAmount,
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
                    VoucherMasterID=PaymentMasterID,
                    VoucherDetailID=PaymentDetailsID,
                    VoucherType=VoucherType,
                    VoucherNo=VoucherNo,
                    LedgerID=82,
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
                    Credit=Discount,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                    )

    #request , company, log_type, user, source, action, message, description
    activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Payment', 'Edit', 'Payment Updated successfully.', 'Payment Updated successfully.')


    response_data = {
        "StatusCode" : 6000,
        "message" : "Payments Updated Successfully!!!",
    }

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
    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        VoucherType = serialized1.data['VoucherType']
        # dummies = PaymentDetailsDummy.objects.filter(CompanyID=CompanyID,BranchID=BranchID)

        # for dummy in dummies:
        #     dummy.delete()
        
        if PaymentMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,VoucherType=VoucherType).exists():
            instances = PaymentMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,VoucherType=VoucherType)
            serialized = PaymentMasterRestSerializer(instances,many=True,context = {"CompanyID": CompanyID,"PriceRounding":PriceRounding })

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Payment', 'List Payment', 'Payment List Viewed successfully.', 'Payment List Viewed successfully.')
            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Payment', 'List Payment', 'Payment List Viewed Failed.', 'Payment not found in this branch')
            response_data = {
            "StatusCode" : 6001,
            "message" : "Payment Master not found in this branch."
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
def paymentMaster(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    CreatedUserID = data['CreatedUserID']

    if PaymentMaster.objects.filter(CompanyID=CompanyID,pk=pk).exists():
        instance = PaymentMaster.objects.get(pk=pk)
        company_instance = CompanySettings.objects.get(pk=CompanyID.id)
        serialized = PaymentMasterRestSerializer(instance,context = {"CompanyID": CompanyID,"PriceRounding":PriceRounding })
        company_serialized = CompanySettingsRestSerializer(company_instance, context={"request": request})

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Payment', 'View Payment', 'Payment Single Page Viewed successfully.', 'Payment Single Page Viewed successfully')
        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data,
            "company_data": company_serialized.data,
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Payment', 'View Payment', 'Payment Single Page Viewed Failed.', 'Payment Not Found!')
        response_data = {
            "StatusCode" : 6001,
            "message" : "Payment Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_paymentMaster(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    ledgerPostInstances = None
    if PaymentMaster.objects.filter(CompanyID=CompanyID,pk=pk).exists():
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

        instance.delete()

        detail_instances = PaymentDetails.objects.filter(CompanyID=CompanyID,PaymentMasterID=PaymentMasterID,BranchID=BranchID)
        
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
                )

            detail_instance.delete()

            if LedgerPosting.objects.filter(CompanyID=CompanyID,VoucherMasterID=PaymentMasterID,BranchID=BranchID,VoucherType="CP").exists():
                ledgerPostInstances = LedgerPosting.objects.filter(CompanyID=CompanyID,VoucherMasterID=PaymentMasterID,BranchID=BranchID,VoucherType="CP")
                
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

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Payment', 'Delete', 'Payment Deleted Successfully.', 'Payment Deleted Successfully.')

        response_data = {
            "StatusCode" : 6000,
            "message" : "Payment Master Deleted Successfully!",
            "title" : "Success",
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Payment', 'Delete', 'Payment Deleted Failed.', 'Payment Not Found!')
        response_data = {
            "StatusCode" : 6001,
            "message" : "Payment Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)

