from brands.models import Bank, Bank_Log, AccountLedger, AccountLedger_Log, LedgerPosting, LedgerPosting_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v5.banks.serializers import BankSerializer, BankRestSerializer
from api.v5.brands.serializers import ListSerializer
from api.v5.banks.functions import generate_serializer_errors
from rest_framework import status
from api.v5.banks.functions import get_auto_Bankid, get_BankCode
from api.v5.accountLedgers.functions import get_auto_id, get_auto_LedgerPostid
import datetime
from main.functions import get_company, activity_log
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Prefetch
from api.v5.accountLedgers.functions import get_LedgerCode, get_auto_id as generated_ledgerID


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
def create_bank(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = BankSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        Name = serialized.data['Name']
        AccountNumber = serialized.data['AccountNumber']
        CrOrDr = serialized.data['CrOrDr']
        BranchCode = serialized.data['BranchCode']
        IFSCCode = serialized.data['IFSCCode']
        MICRCode = serialized.data['MICRCode']
        Status = serialized.data['Status']
        OpeningBalance = serialized.data['OpeningBalance']
        Address = serialized.data['Address']
        City = serialized.data['City']
        State = serialized.data['State']
        Country = serialized.data['Country']
        PostalCode = serialized.data['PostalCode']
        Phone = serialized.data['Phone']
        Mobile = serialized.data['Mobile']
        Email = serialized.data['Email']
        Notes = serialized.data['Notes']

        BankID = get_auto_Bankid(Bank, BranchID, CompanyID)

        LedgerID = get_auto_id(AccountLedger, BranchID, CompanyID)

        LedgerCode = get_BankCode(Bank, BranchID, CompanyID)

        Action = 'A'

        if CrOrDr == "0":
            CrOrDr = "Dr"

        elif CrOrDr == "1":
            CrOrDr = "Cr"

        AccountGroupUnder = 8

        LedgerName = Name

        is_nameExist = False

        LedgerNameLow = LedgerName.lower()

        account_ledgers = AccountLedger.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID)

        for account_ledger in account_ledgers:

            ledger_name = account_ledger.LedgerName
            ledgerName = ledger_name.lower()

            if LedgerNameLow == ledgerName:
                is_nameExist = True

        if not is_nameExist:
            Bank.objects.create(
                BankID=BankID,
                BranchID=BranchID,
                LedgerCode=LedgerCode,
                Name=Name,
                LedgerName=LedgerName,
                AccountNumber=AccountNumber,
                CrOrDr=CrOrDr,
                BranchCode=BranchCode,
                IFSCCode=IFSCCode,
                MICRCode=MICRCode,
                Status=Status,
                OpeningBalance=OpeningBalance,
                Address=Address,
                City=City,
                State=State,
                Country=Country,
                PostalCode=PostalCode,
                Phone=Phone,
                Mobile=Mobile,
                Email=Email,
                Notes=Notes,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CompanyID=CompanyID,
            )

            Bank_Log.objects.create(
                BranchID=BranchID,
                TransactionID=BankID,
                LedgerCode=LedgerCode,
                Name=Name,
                LedgerName=LedgerName,
                AccountNumber=AccountNumber,
                CrOrDr=CrOrDr,
                BranchCode=BranchCode,
                IFSCCode=IFSCCode,
                MICRCode=MICRCode,
                Status=Status,
                OpeningBalance=OpeningBalance,
                Address=Address,
                City=City,
                State=State,
                Country=Country,
                PostalCode=PostalCode,
                Phone=Phone,
                Mobile=Mobile,
                Email=Email,
                Notes=Notes,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CompanyID=CompanyID,
            )

            AccountLedger.objects.create(
                LedgerID=LedgerID,
                BranchID=BranchID,
                LedgerName=LedgerName,
                LedgerCode=LedgerCode,
                AccountGroupUnder=AccountGroupUnder,
                OpeningBalance=OpeningBalance,
                CrOrDr=CrOrDr,
                CreatedDate=today,
                UpdatedDate=today,
                Notes=Notes,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            AccountLedger_Log.objects.create(
                BranchID=BranchID,
                TransactionID=LedgerID,
                LedgerName=LedgerName,
                LedgerCode=LedgerCode,
                AccountGroupUnder=AccountGroupUnder,
                OpeningBalance=OpeningBalance,
                CrOrDr=CrOrDr,
                CreatedDate=today,
                UpdatedDate=today,
                Notes=Notes,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            if float(OpeningBalance) > 0:
                Credit = 0.00
                Debit = 0.00

                if CrOrDr == "Cr":
                    Credit = OpeningBalance

                elif CrOrDr == "Dr":
                    Debit = OpeningBalance

                VoucherType = "LOB"

                # LedgerPostingID = get_auto_LedgerPostid(
                #     LedgerPosting, BranchID, CompanyID)

                # LedgerPosting.objects.create(
                #     LedgerPostingID=LedgerPostingID,
                #     BranchID=BranchID,
                #     Date=today,
                #     VoucherMasterID=LedgerID,
                #     VoucherType=VoucherType,
                #     LedgerID=LedgerID,
                #     Debit=Debit,
                #     Credit=Credit,
                #     Action=Action,
                #     CreatedUserID=CreatedUserID,
                #     CreatedDate=today,
                #     UpdatedDate=today,
                #     CompanyID=CompanyID,
                # )

                # LedgerPosting_Log.objects.create(
                #     TransactionID=LedgerPostingID,
                #     BranchID=BranchID,
                #     Date=today,
                #     VoucherMasterID=LedgerID,
                #     VoucherType=VoucherType,
                #     LedgerID=LedgerID,
                #     Debit=Debit,
                #     Credit=Credit,
                #     Action=Action,
                #     CreatedUserID=CreatedUserID,
                #     CreatedDate=today,
                #     UpdatedDate=today,
                #     CompanyID=CompanyID,
                # )

                if AccountLedger.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerName="Suspense Account").exists():
                    RelativeLedgerID = AccountLedger.objects.get(
                        CompanyID=CompanyID, BranchID=BranchID, LedgerName="Suspense Account").LedgerID
                else:
                    RelativeLedgerID = generated_ledgerID(
                        AccountLedger, BranchID, CompanyID)
                    SuspenseLedgerCode = get_LedgerCode(
                        AccountLedger, BranchID, CompanyID)

                    AccountLedger.objects.create(
                        LedgerID=RelativeLedgerID,
                        BranchID=BranchID,
                        LedgerName="Suspense Account",
                        LedgerCode=SuspenseLedgerCode,
                        AccountGroupUnder=26,
                        OpeningBalance=0,
                        CrOrDr="Dr",
                        Notes=Notes,
                        IsActive=True,
                        IsDefault=True,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                    )

                    AccountLedger_Log.objects.create(
                        BranchID=BranchID,
                        TransactionID=RelativeLedgerID,
                        LedgerName="Suspense Account",
                        LedgerCode=SuspenseLedgerCode,
                        AccountGroupUnder=26,
                        OpeningBalance=0,
                        CrOrDr="Dr",
                        Notes=Notes,
                        IsActive=True,
                        IsDefault=True,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                    )
                IsActive = True
                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=today,
                    VoucherMasterID=LedgerID,
                    VoucherType=VoucherType,
                    VoucherNo=LedgerCode,
                    LedgerID=LedgerID,
                    RelatedLedgerID=RelativeLedgerID,
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
                    Date=today,
                    VoucherMasterID=LedgerID,
                    VoucherNo=LedgerCode,
                    VoucherType=VoucherType,
                    LedgerID=LedgerID,
                    RelatedLedgerID=RelativeLedgerID,
                    Debit=Debit,
                    Credit=Credit,
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
                    Date=today,
                    VoucherMasterID=LedgerID,
                    VoucherType=VoucherType,
                    VoucherNo=LedgerCode,
                    LedgerID=RelativeLedgerID,
                    RelatedLedgerID=LedgerID,
                    Debit=Credit,
                    Credit=Debit,
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
                    Date=today,
                    VoucherMasterID=LedgerID,
                    VoucherNo=LedgerCode,
                    VoucherType=VoucherType,
                    LedgerID=RelativeLedgerID,
                    RelatedLedgerID=LedgerID,
                    Debit=Credit,
                    Credit=Debit,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID,
                         'Bank', 'Create', 'Bank created successfully.', 'Bank saved successfully.')

            response_data = {
                "StatusCode": 6000,
                "message": "Bank Created Successfully!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID,
                         'Bank', 'Create', 'Bank created failed.', 'Ledger Name Already Exist.')
            response_data = {
                "StatusCode": 6001,
                "message": "Ledger Name Already Exist!!!"
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Bank', 'Create',
                     'Bank created failed.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_bank(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = BankSerializer(data=request.data)
    instance = Bank.objects.get(pk=pk, CompanyID=CompanyID)

    BankID = instance.BankID
    LedgerCode = instance.LedgerCode
    BranchID = instance.BranchID
    instanceLedgerName = instance.LedgerName

    if serialized.is_valid():

        Name = serialized.data['Name']
        AccountNumber = serialized.data['AccountNumber']
        CrOrDr = serialized.data['CrOrDr']
        BranchCode = serialized.data['BranchCode']
        IFSCCode = serialized.data['IFSCCode']
        MICRCode = serialized.data['MICRCode']
        Status = serialized.data['Status']
        OpeningBalance = serialized.data['OpeningBalance']
        Address = serialized.data['Address']
        City = serialized.data['City']
        State = serialized.data['State']
        Country = serialized.data['Country']
        PostalCode = serialized.data['PostalCode']
        Phone = serialized.data['Phone']
        Mobile = serialized.data['Mobile']
        Email = serialized.data['Email']
        Notes = serialized.data['Notes']

        Action = 'M'

        if CrOrDr == "0":
            CrOrDr = "Dr"

        elif CrOrDr == "1":
            CrOrDr = "Cr"

        AccountGroupUnder = 8

        LedgerName = Name

        is_nameExist = False
        accountLedger_ok = False

        LedgerNameLow = LedgerName.lower()

        account_ledgers = AccountLedger.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID)

        for account_ledger in account_ledgers:

            ledger_name = account_ledger.LedgerName
            ledgerName = ledger_name.lower()

            if LedgerNameLow == ledgerName:
                is_nameExist = True

            if instanceLedgerName.lower() == LedgerNameLow:

                accountLedger_ok = True

        if accountLedger_ok:

            instance.Name = Name
            instance.LedgerName = LedgerName
            instance.AccountNumber = AccountNumber
            instance.CrOrDr = CrOrDr
            instance.BranchCode = BranchCode
            instance.IFSCCode = IFSCCode
            instance.MICRCode = MICRCode
            instance.Status = Status
            instance.OpeningBalance = OpeningBalance
            instance.Address = Address
            instance.City = City
            instance.State = State
            instance.Country = Country
            instance.PostalCode = PostalCode
            instance.Phone = Phone
            instance.Mobile = Mobile
            instance.Email = Email
            instance.Notes = Notes
            instance.Action = Action
            instance.CreatedUserID = CreatedUserID
            instance.UpdatedDate = today
            instance.save()

            Bank_Log.objects.create(
                BranchID=BranchID,
                TransactionID=BankID,
                LedgerCode=LedgerCode,
                Name=Name,
                LedgerName=LedgerName,
                AccountNumber=AccountNumber,
                CrOrDr=CrOrDr,
                BranchCode=BranchCode,
                IFSCCode=IFSCCode,
                MICRCode=MICRCode,
                Status=Status,
                OpeningBalance=OpeningBalance,
                Address=Address,
                City=City,
                State=State,
                Country=Country,
                PostalCode=PostalCode,
                Phone=Phone,
                Mobile=Mobile,
                Email=Email,
                Notes=Notes,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CompanyID=CompanyID,
            )

            if AccountLedger.objects.filter(LedgerName=instanceLedgerName, BranchID=BranchID, CompanyID=CompanyID).exists():
                account_ledger = AccountLedger.objects.get(
                    LedgerName=instanceLedgerName, BranchID=BranchID, CompanyID=CompanyID)
                LedgerID = account_ledger.LedgerID
                account_ledger.LedgerName = LedgerName
                account_ledger.OpeningBalance = OpeningBalance
                account_ledger.CrOrDr = CrOrDr
                account_ledger.UpdatedDate = today
                account_ledger.Notes = Notes
                account_ledger.CreatedUserID = CreatedUserID
                account_ledger.Action = Action
                account_ledger.save()

                AccountLedger_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=LedgerID,
                    LedgerName=LedgerName,
                    LedgerCode=LedgerCode,
                    AccountGroupUnder=AccountGroupUnder,
                    OpeningBalance=OpeningBalance,
                    CrOrDr=CrOrDr,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Notes=Notes,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID
                )

            if LedgerPosting.objects.filter(BranchID=BranchID, VoucherMasterID=LedgerID, VoucherType="LOB", CompanyID=CompanyID).exists():
                ledgerPostInstances = LedgerPosting.objects.filter(
                    BranchID=BranchID, VoucherMasterID=LedgerID, VoucherType="LOB", CompanyID=CompanyID)
                for ledgerPostInstance in ledgerPostInstances:
                    ledgerPostInstance.delete()

            if float(OpeningBalance) > 0:
                Credit = 0.00
                Debit = 0.00

                if CrOrDr == "Cr":
                    Credit = OpeningBalance

                elif CrOrDr == "Dr":
                    Debit = OpeningBalance

                VoucherType = "LOB"

                if AccountLedger.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerName="Suspense Account").exists():
                    RelativeLedgerID = AccountLedger.objects.get(
                        CompanyID=CompanyID, BranchID=BranchID, LedgerName="Suspense Account").LedgerID
                else:
                    RelativeLedgerID = generated_ledgerID(
                        AccountLedger, BranchID, CompanyID)
                    SuspenseLedgerCode = get_LedgerCode(
                        AccountLedger, BranchID, CompanyID)

                    AccountLedger.objects.create(
                        LedgerID=RelativeLedgerID,
                        BranchID=BranchID,
                        LedgerName="Suspense Account",
                        LedgerCode=SuspenseLedgerCode,
                        AccountGroupUnder=26,
                        OpeningBalance=0,
                        CrOrDr="Dr",
                        Notes=Notes,
                        IsActive=True,
                        IsDefault=True,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                    )

                    AccountLedger_Log.objects.create(
                        BranchID=BranchID,
                        TransactionID=RelativeLedgerID,
                        LedgerName="Suspense Account",
                        LedgerCode=SuspenseLedgerCode,
                        AccountGroupUnder=26,
                        OpeningBalance=0,
                        CrOrDr="Dr",
                        Notes=Notes,
                        IsActive=True,
                        IsDefault=True,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                    )
                IsActive = True
                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=today,
                    VoucherMasterID=LedgerID,
                    VoucherType=VoucherType,
                    VoucherNo=LedgerCode,
                    LedgerID=LedgerID,
                    RelatedLedgerID=RelativeLedgerID,
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
                    Date=today,
                    VoucherMasterID=LedgerID,
                    VoucherNo=LedgerCode,
                    VoucherType=VoucherType,
                    LedgerID=LedgerID,
                    RelatedLedgerID=RelativeLedgerID,
                    Debit=Debit,
                    Credit=Credit,
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
                    Date=today,
                    VoucherMasterID=LedgerID,
                    VoucherType=VoucherType,
                    VoucherNo=LedgerCode,
                    LedgerID=RelativeLedgerID,
                    RelatedLedgerID=LedgerID,
                    Debit=Credit,
                    Credit=Debit,
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
                    Date=today,
                    VoucherMasterID=LedgerID,
                    VoucherNo=LedgerCode,
                    VoucherType=VoucherType,
                    LedgerID=RelativeLedgerID,
                    RelatedLedgerID=LedgerID,
                    Debit=Credit,
                    Credit=Debit,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID,
                         'Bank', 'Edit', 'Bank Updated Successfully.', "Bank Updated Successfully.")
            response_data = {
                "StatusCode": 6000,
                "message": "Bank Updated Successfully!"
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:

            if is_nameExist:

                response_data = {
                    "StatusCode": 6001,
                    "message": "Ledger Name Already exist with this Branch ID"
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                instance.Name = Name
                instance.LedgerName = LedgerName
                instance.AccountNumber = AccountNumber
                instance.CrOrDr = CrOrDr
                instance.BranchCode = BranchCode
                instance.IFSCCode = IFSCCode
                instance.MICRCode = MICRCode
                instance.Status = Status
                instance.OpeningBalance = OpeningBalance
                instance.Address = Address
                instance.City = City
                instance.State = State
                instance.Country = Country
                instance.PostalCode = PostalCode
                instance.Phone = Phone
                instance.Mobile = Mobile
                instance.Email = Email
                instance.Notes = Notes
                instance.Action = Action
                instance.CreatedUserID = CreatedUserID
                instance.UpdatedDate = today
                instance.save()

                Bank_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=BankID,
                    LedgerCode=LedgerCode,
                    Name=Name,
                    LedgerName=LedgerName,
                    AccountNumber=AccountNumber,
                    CrOrDr=CrOrDr,
                    BranchCode=BranchCode,
                    IFSCCode=IFSCCode,
                    MICRCode=MICRCode,
                    Status=Status,
                    OpeningBalance=OpeningBalance,
                    Address=Address,
                    City=City,
                    State=State,
                    Country=Country,
                    PostalCode=PostalCode,
                    Phone=Phone,
                    Mobile=Mobile,
                    Email=Email,
                    Notes=Notes,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=Action,
                    CompanyID=CompanyID,
                )

                if AccountLedger.objects.filter(LedgerName=instanceLedgerName, BranchID=BranchID, CompanyID=CompanyID).exists():
                    account_ledger = AccountLedger.objects.get(
                        LedgerName=instanceLedgerName, BranchID=BranchID, CompanyID=CompanyID)
                    LedgerID = account_ledger.LedgerID
                    account_ledger.LedgerName = LedgerName
                    account_ledger.OpeningBalance = OpeningBalance
                    account_ledger.CrOrDr = CrOrDr
                    account_ledger.UpdatedDate = today
                    account_ledger.Notes = Notes
                    account_ledger.CreatedUserID = CreatedUserID
                    account_ledger.Action = Action
                    account_ledger.save()

                    AccountLedger_Log.objects.create(
                        BranchID=BranchID,
                        TransactionID=LedgerID,
                        LedgerName=LedgerName,
                        LedgerCode=LedgerCode,
                        AccountGroupUnder=AccountGroupUnder,
                        OpeningBalance=OpeningBalance,
                        CrOrDr=CrOrDr,
                        UpdatedDate=today,
                        CreatedDate=today,
                        Notes=Notes,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                    )

                if LedgerPosting.objects.filter(LedgerID=LedgerID, BranchID=BranchID, VoucherMasterID=LedgerID, VoucherType="LOB", CompanyID=CompanyID).exists():
                    ledgerPostInstance = LedgerPosting.objects.get(
                        LedgerID=LedgerID, BranchID=BranchID, VoucherMasterID=LedgerID, VoucherType="LOB", CompanyID=CompanyID)
                    ledgerPostInstance.delete()

                if float(OpeningBalance) > 0:
                    Credit = 0.00
                    Debit = 0.00

                    if CrOrDr == "Cr":
                        Credit = OpeningBalance

                    elif CrOrDr == "Dr":
                        Debit = OpeningBalance

                    VoucherType = "LOB"

                    if AccountLedger.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerName="Suspense Account").exists():
                        RelativeLedgerID = AccountLedger.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID, LedgerName="Suspense Account").LedgerID
                    else:
                        RelativeLedgerID = get_auto_id(
                            AccountLedger, BranchID, CompanyID)
                        SuspenseLedgerCode = get_LedgerCode(
                            AccountLedger, BranchID, CompanyID)

                        AccountLedger.objects.create(
                            LedgerID=RelativeLedgerID,
                            BranchID=BranchID,
                            LedgerName="Suspense Account",
                            LedgerCode=SuspenseLedgerCode,
                            AccountGroupUnder=26,
                            OpeningBalance=0,
                            CrOrDr="Dr",
                            Notes=Notes,
                            IsActive=True,
                            IsDefault=True,
                            CreatedDate=today,
                            UpdatedDate=today,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                        AccountLedger_Log.objects.create(
                            BranchID=BranchID,
                            TransactionID=RelativeLedgerID,
                            LedgerName="Suspense Account",
                            LedgerCode=SuspenseLedgerCode,
                            AccountGroupUnder=26,
                            OpeningBalance=0,
                            CrOrDr="Dr",
                            Notes=Notes,
                            IsActive=True,
                            IsDefault=True,
                            CreatedDate=today,
                            UpdatedDate=today,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )
                    IsActive = True
                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=today,
                        VoucherMasterID=LedgerID,
                        VoucherType=VoucherType,
                        VoucherNo=LedgerCode,
                        LedgerID=LedgerID,
                        RelatedLedgerID=RelativeLedgerID,
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
                        Date=today,
                        VoucherMasterID=LedgerID,
                        VoucherNo=LedgerCode,
                        VoucherType=VoucherType,
                        LedgerID=LedgerID,
                        RelatedLedgerID=RelativeLedgerID,
                        Debit=Debit,
                        Credit=Credit,
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
                        Date=today,
                        VoucherMasterID=LedgerID,
                        VoucherType=VoucherType,
                        VoucherNo=LedgerCode,
                        LedgerID=RelativeLedgerID,
                        RelatedLedgerID=LedgerID,
                        Debit=Credit,
                        Credit=Debit,
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
                        Date=today,
                        VoucherMasterID=LedgerID,
                        VoucherNo=LedgerCode,
                        VoucherType=VoucherType,
                        LedgerID=RelativeLedgerID,
                        RelatedLedgerID=LedgerID,
                        Debit=Credit,
                        Credit=Debit,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Information', CreatedUserID,
                             'Bank', 'Edit', 'Bank Updated Successfully.', "Bank Updated Successfully.")

                response_data = {
                    "StatusCode": 6000,
                    "message": "Bank Updated Successfully!"
                }

                return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Bank', 'Edit',
                     'Bank Updated Failed.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def banks(request):
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

        if Bank.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            if page_number and items_per_page:
                instances = Bank.objects.filter(
                    BranchID=BranchID, CompanyID=CompanyID)
                ledger_sort_pagination = list_pagination(
                    instances,
                    items_per_page,
                    page_number
                )

            serialized = BankRestSerializer(ledger_sort_pagination, many=True, context={
                                            "PriceRounding": PriceRounding})

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Bank',
                         'View', 'Bank List View successfully.', "Bank List View successfully.")
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "count": len(instances),
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Account Ledger Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID,
                     'Bank', 'View', 'Bank List View Failed.', "Invalid BranchID Given!")
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def bank(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    CreatedUserID = data['CreatedUserID']

    instance = None
    if Bank.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = Bank.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = BankRestSerializer(instance, context={"CompanyID": CompanyID,
                                                           "PriceRounding": PriceRounding})
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID,
                     'Bank', 'View', 'Bank single page Viewed.', 'Bank single page Viewed.')
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID,
                     'Bank', 'View', 'Bank single page View failed.', 'Bank Not Found')
        response_data = {
            "StatusCode": 6001,
            "message": "Bank Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_bank(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if Bank.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = Bank.objects.get(pk=pk, CompanyID=CompanyID)

        BankID = instance.BankID
        BranchID = instance.BranchID
        LedgerCode = instance.LedgerCode
        Name = instance.Name
        LedgerName = instance.LedgerName
        AccountNumber = instance.AccountNumber
        CrOrDr = instance.CrOrDr
        BranchCode = instance.BranchCode
        IFSCCode = instance.IFSCCode
        MICRCode = instance.MICRCode
        Status = instance.Status
        OpeningBalance = instance.OpeningBalance
        Address = instance.Address
        City = instance.City
        State = instance.State
        Country = instance.Country
        PostalCode = instance.PostalCode
        Phone = instance.Phone
        Mobile = instance.Mobile
        Email = instance.Email
        Notes = instance.Notes
        Action = "D"

        AccountGroupUnder = 8

        if AccountLedger.objects.filter(BranchID=BranchID, LedgerName=LedgerName, CompanyID=CompanyID).exists():
            account_ledger = AccountLedger.objects.get(
                BranchID=BranchID, LedgerName=LedgerName, CompanyID=CompanyID)

            LedgerID = account_ledger.LedgerID
            if not LedgerPosting.objects.filter(LedgerID=LedgerID, BranchID=BranchID, CompanyID=CompanyID).exists():
                # if not LPInstances:
                instance.delete()
                account_ledger.delete()

                Bank_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=BankID,
                    LedgerCode=LedgerCode,
                    Name=Name,
                    LedgerName=LedgerName,
                    AccountNumber=AccountNumber,
                    CrOrDr=CrOrDr,
                    BranchCode=BranchCode,
                    IFSCCode=IFSCCode,
                    MICRCode=MICRCode,
                    Status=Status,
                    OpeningBalance=OpeningBalance,
                    Address=Address,
                    City=City,
                    State=State,
                    Country=Country,
                    PostalCode=PostalCode,
                    Phone=Phone,
                    Mobile=Mobile,
                    Email=Email,
                    Notes=Notes,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=Action,
                    CompanyID=CompanyID,
                )

                AccountLedger_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=LedgerID,
                    LedgerName=LedgerName,
                    LedgerCode=LedgerCode,
                    AccountGroupUnder=AccountGroupUnder,
                    OpeningBalance=OpeningBalance,
                    CrOrDr=CrOrDr,
                    Notes=Notes,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=Action,
                    CompanyID=CompanyID,
                )

                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Bank',
                             'Deleted', 'Bank Deleted Successfully.', 'Bank Deleted Successfully')
                response_data = {
                    "StatusCode": 6000,
                    "title": "Success",
                    "message": "Bank Deleted Successfully!"
                }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "title": "Failed",
                    "message": "You Cant Delete this Bank,!"
                }

        else:
            response_data = {
                "StatusCode": 6001,
                "title": "Failed",
                "message": "You Cant Delete this Bank,this LedgerID is using somewhere!!"
            }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID,
                     'Bank', 'Deleted', 'Bank Deleted Failed.', 'Bank Not Found')
        response_data = {
            "StatusCode": 6001,
            "title": "Failed",
            "message": "Bank Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
