import datetime
from email import message

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Prefetch, Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, renderer_classes,authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from yaml import serialize

from api.v10.accountLedgers.functions import get_auto_id
from api.v10.accountLedgers.functions import get_auto_id as generated_ledgerID
from api.v10.accountLedgers.functions import get_auto_LedgerPostid, get_LedgerCode
from api.v10.banks.functions import (
    generate_serializer_errors,
    get_auto_Bankid,
    get_BankCode,
)
from api.v10.banks.serializers import BankRestSerializer, BankSerializer, CompanyTestSerializer
from api.v10.brands.serializers import ListSerializer
from brands.models import (
    AccountLedger,
    AccountLedger_Log,
    Activity_Log,
    Bank,
    Bank_Log,
    CompanySettings,
    LedgerPosting,
    LedgerPosting_Log,
    Parties,
)
from main.functions import activity_log, converted_float, get_company


def call_paginator_all(model_object, page_number, items_per_page):
    paginator = Paginator(model_object, items_per_page)
    content = paginator.page(page_number)
    return content


def list_pagination(list_value, items_per_page, page_no):
    paginator_object = Paginator(list_value, items_per_page)
    get_value = paginator_object.page(page_no).object_list
    return get_value


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def create_bank(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]

    today = datetime.datetime.now()
    serialized = BankSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data["BranchID"]
        Name = serialized.data["Name"]
        AccountNumber = serialized.data["AccountNumber"]
        CrOrDr = serialized.data["CrOrDr"]
        BranchCode = serialized.data["BranchCode"]
        IFSCCode = serialized.data["IFSCCode"]
        MICRCode = serialized.data["MICRCode"]
        Status = serialized.data["Status"]
        OpeningBalance = serialized.data["OpeningBalance"]
        Address = serialized.data["Address"]
        City = serialized.data["City"]
        State = serialized.data["State"]
        Country = serialized.data["Country"]
        PostalCode = serialized.data["PostalCode"]
        Phone = serialized.data["Phone"]
        Mobile = serialized.data["Mobile"]
        Email = serialized.data["Email"]
        Notes = serialized.data["Notes"]
        try:
            AsOnDate = data["AsOnDate"]
        except:
            AsOnDate = None

        BankID = get_auto_Bankid(Bank, BranchID, CompanyID)

        LedgerID = get_auto_id(AccountLedger, BranchID, CompanyID)

        LedgerCode = get_BankCode(Bank, BranchID, CompanyID)

        Action = "A"

        if CrOrDr == "0":
            CrOrDr = "Dr"

        elif CrOrDr == "1":
            CrOrDr = "Cr"

        AccountGroupUnder = 8
        LedgerName = Name

        is_nameExist = False
        is_accountNoExist = False
        if AccountLedger.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerName__iexact=LedgerName
        ).exists():
            is_nameExist = True
        if Bank.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, AccountNumber__iexact=AccountNumber
        ).exists():
            is_accountNoExist = True

        # for account_ledger in account_ledgers:
        #     ledger_name = account_ledger.LedgerName
        #     ledgerName = ledger_name.lower()
        #     if LedgerNameLow == ledgerName:
        #         is_nameExist = True

        if not is_nameExist and not is_accountNoExist:
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

            Balance = 0
            if converted_float(OpeningBalance) > 0:
                if CrOrDr == "Cr":
                    Balance = converted_float(OpeningBalance) * -1

                elif CrOrDr == "Dr":
                    Balance = OpeningBalance

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
                Balance=Balance,
                as_on_date=AsOnDate,
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
                Balance=Balance,
                as_on_date=AsOnDate,
            )

            if converted_float(OpeningBalance) > 0:
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

                if AccountLedger.objects.filter(
                    CompanyID=CompanyID, LedgerName="Suspense Account"
                ).exists():
                    RelativeLedgerID = AccountLedger.objects.get(
                        CompanyID=CompanyID, LedgerName="Suspense Account"
                    ).LedgerID
                else:
                    RelativeLedgerID = generated_ledgerID(
                        AccountLedger, BranchID, CompanyID
                    )
                    SuspenseLedgerCode = get_LedgerCode(
                        AccountLedger, BranchID, CompanyID
                    )

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
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=AsOnDate,
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
                    Date=AsOnDate,
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
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=AsOnDate,
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
                    Date=AsOnDate,
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

            # request , company, log_type, user, source, action, message, description
            activity_log(
                request._request,
                CompanyID,
                "Information",
                CreatedUserID,
                "Bank",
                "Create",
                "Bank created successfully.",
                "Bank saved successfully.",
            )

            response_data = {
                "StatusCode": 6000,
                "message": "Bank Created Successfully!",
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # request , company, log_type, user, source, action, message, description
            activity_log(
                request._request,
                CompanyID,
                "Warning",
                CreatedUserID,
                "Bank",
                "Create",
                "Bank created failed.",
                "Ledger Name Already Exist.",
            )
            if is_accountNoExist:
                message = "Account Number already exist"
            if is_nameExist:
                message = "Bank Name already exist"
            response_data = {"StatusCode": 6001, "message": message}

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Error",
            CreatedUserID,
            "Bank",
            "Create",
            "Bank created failed.",
            generate_serializer_errors(serialized._errors),
        )
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors),
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def edit_bank(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]

    today = datetime.datetime.now()
    serialized = BankSerializer(data=request.data)
    instance = Bank.objects.get(pk=pk, CompanyID=CompanyID)

    BankID = instance.BankID
    LedgerCode = instance.LedgerCode
    BranchID = instance.BranchID
    instanceLedgerName = instance.LedgerName

    if serialized.is_valid():

        Name = serialized.data["Name"]
        AccountNumber = serialized.data["AccountNumber"]
        CrOrDr = serialized.data["CrOrDr"]
        BranchCode = serialized.data["BranchCode"]
        IFSCCode = serialized.data["IFSCCode"]
        MICRCode = serialized.data["MICRCode"]
        Status = serialized.data["Status"]
        OpeningBalance = serialized.data["OpeningBalance"]
        Address = serialized.data["Address"]
        City = serialized.data["City"]
        State = serialized.data["State"]
        Country = serialized.data["Country"]
        PostalCode = serialized.data["PostalCode"]
        Phone = serialized.data["Phone"]
        Mobile = serialized.data["Mobile"]
        Email = serialized.data["Email"]
        Notes = serialized.data["Notes"]
        try:
            AsOnDate = data["AsOnDate"]
        except:
            AsOnDate = None

        Action = "M"

        if CrOrDr == "0":
            CrOrDr = "Dr"

        elif CrOrDr == "1":
            CrOrDr = "Cr"

        AccountGroupUnder = 8

        LedgerName = Name

        is_nameExist = False
        is_accountNoExist = False
        accountLedger_ok = False

        LedgerNameLow = LedgerName.lower()

        account_ledgers = AccountLedger.objects.filter(CompanyID=CompanyID)
        if Bank.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, AccountNumber__iexact=AccountNumber
        ).exclude(pk=pk):
            is_accountNoExist = True

        if Bank.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, LedgerName__iexact=LedgerName
        ).exclude(pk=pk):
            is_nameExist = True

        # for account_ledger in account_ledgers:
        #     ledger_name = account_ledger.LedgerName
        #     ledgerName = ledger_name.lower()
        #     if LedgerNameLow == ledgerName:
        #         is_nameExist = True
        #     if instanceLedgerName.lower() == LedgerNameLow:
        #         accountLedger_ok = True

        if not is_nameExist and not is_accountNoExist:
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

            if AccountLedger.objects.filter(
                LedgerName=instanceLedgerName, CompanyID=CompanyID
            ).exists():
                account_ledger = AccountLedger.objects.get(
                    LedgerName=instanceLedgerName, CompanyID=CompanyID
                )

                Balance = 0
                if converted_float(OpeningBalance) > 0:
                    if CrOrDr == "Cr":
                        Balance = converted_float(OpeningBalance) * -1

                    elif CrOrDr == "Dr":
                        Balance = OpeningBalance

                instanceBalance = account_ledger.Balance
                instanceOpeningBalance = account_ledger.OpeningBalance
                instanceCrOrDr = account_ledger.CrOrDr
                if instanceCrOrDr == "Cr":
                    instanceOpeningBalance = (
                        converted_float(instanceOpeningBalance) * -1
                    )
                elif instanceCrOrDr == "Dr":
                    instanceOpeningBalance = instanceOpeningBalance

                latest_balance = converted_float(instanceBalance) - converted_float(
                    instanceOpeningBalance
                )
                Balance = converted_float(latest_balance) + converted_float(Balance)

                LedgerID = account_ledger.LedgerID
                account_ledger.LedgerName = LedgerName
                account_ledger.OpeningBalance = OpeningBalance
                account_ledger.CrOrDr = CrOrDr
                account_ledger.UpdatedDate = today
                account_ledger.Notes = Notes
                account_ledger.CreatedUserID = CreatedUserID
                account_ledger.Action = Action
                account_ledger.Balance = Balance
                account_ledger.as_on_date = AsOnDate
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
                    CompanyID=CompanyID,
                    Balance=Balance,
                    as_on_date=AsOnDate,
                )

            if LedgerPosting.objects.filter(
                BranchID=BranchID,
                VoucherMasterID=LedgerID,
                VoucherType="LOB",
                CompanyID=CompanyID,
            ).exists():
                ledgerPostInstances = LedgerPosting.objects.filter(
                    BranchID=BranchID,
                    VoucherMasterID=LedgerID,
                    VoucherType="LOB",
                    CompanyID=CompanyID,
                )
                for ledgerPostInstance in ledgerPostInstances:
                    ledgerPostInstance.delete()

            if converted_float(OpeningBalance) > 0:
                Credit = 0.00
                Debit = 0.00

                if CrOrDr == "Cr":
                    Credit = OpeningBalance

                elif CrOrDr == "Dr":
                    Debit = OpeningBalance

                VoucherType = "LOB"

                if AccountLedger.objects.filter(
                    CompanyID=CompanyID, LedgerName="Suspense Account"
                ).exists():
                    RelativeLedgerID = AccountLedger.objects.get(
                        CompanyID=CompanyID, LedgerName="Suspense Account"
                    ).LedgerID
                else:
                    RelativeLedgerID = generated_ledgerID(
                        AccountLedger, BranchID, CompanyID
                    )
                    SuspenseLedgerCode = get_LedgerCode(
                        AccountLedger, BranchID, CompanyID
                    )

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
                        as_on_date=AsOnDate,
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
                        as_on_date=AsOnDate,
                    )
                IsActive = True
                LedgerPostingID = get_auto_LedgerPostid(
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=AsOnDate,
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
                    Date=AsOnDate,
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
                    LedgerPosting, BranchID, CompanyID
                )

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=AsOnDate,
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
                    Date=AsOnDate,
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

            # request , company, log_type, user, source, action, message, description
            activity_log(
                request._request,
                CompanyID,
                "Information",
                CreatedUserID,
                "Bank",
                "Edit",
                "Bank Updated Successfully.",
                "Bank Updated Successfully.",
            )
            response_data = {
                "StatusCode": 6000,
                "message": "Bank Updated Successfully!",
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            if is_accountNoExist:
                message = "Account Number already exist"
            if is_nameExist:
                message = "Bank Name already exist"
            response_data = {"StatusCode": 6001, "message": message}
            return Response(response_data, status=status.HTTP_200_OK)
            # else:
            #     instance.Name = Name
            #     instance.LedgerName = LedgerName
            #     instance.AccountNumber = AccountNumber
            #     instance.CrOrDr = CrOrDr
            #     instance.BranchCode = BranchCode
            #     instance.IFSCCode = IFSCCode
            #     instance.MICRCode = MICRCode
            #     instance.Status = Status
            #     instance.OpeningBalance = OpeningBalance
            #     instance.Address = Address
            #     instance.City = City
            #     instance.State = State
            #     instance.Country = Country
            #     instance.PostalCode = PostalCode
            #     instance.Phone = Phone
            #     instance.Mobile = Mobile
            #     instance.Email = Email
            #     instance.Notes = Notes
            #     instance.Action = Action
            #     instance.CreatedUserID = CreatedUserID
            #     instance.UpdatedDate = today
            #     instance.save()

            #     Bank_Log.objects.create(
            #         BranchID=BranchID,
            #         TransactionID=BankID,
            #         LedgerCode=LedgerCode,
            #         Name=Name,
            #         LedgerName=LedgerName,
            #         AccountNumber=AccountNumber,
            #         CrOrDr=CrOrDr,
            #         BranchCode=BranchCode,
            #         IFSCCode=IFSCCode,
            #         MICRCode=MICRCode,
            #         Status=Status,
            #         OpeningBalance=OpeningBalance,
            #         Address=Address,
            #         City=City,
            #         State=State,
            #         Country=Country,
            #         PostalCode=PostalCode,
            #         Phone=Phone,
            #         Mobile=Mobile,
            #         Email=Email,
            #         Notes=Notes,
            #         CreatedUserID=CreatedUserID,
            #         CreatedDate=today,
            #         UpdatedDate=today,
            #         Action=Action,
            #         CompanyID=CompanyID,
            #     )

            #     if AccountLedger.objects.filter(LedgerName=instanceLedgerName, CompanyID=CompanyID).exists():
            #         account_ledger = AccountLedger.objects.get(
            #             LedgerName=instanceLedgerName, CompanyID=CompanyID)

            #         Balance = 0
            #         if converted_float(OpeningBalance) > 0:
            #             if CrOrDr == "Cr":
            #                 Balance = converted_float(OpeningBalance) * -1

            #             elif CrOrDr == "Dr":
            #                 Balance = OpeningBalance

            #         instanceBalance = account_ledger.Balance
            #         instanceOpeningBalance = account_ledger.OpeningBalance
            #         instanceCrOrDr = account_ledger.CrOrDr
            #         if instanceCrOrDr == "Cr":
            #             instanceOpeningBalance = converted_float(
            #                 instanceOpeningBalance) * -1
            #         elif instanceCrOrDr == "Dr":
            #             instanceOpeningBalance = instanceOpeningBalance
            #         latest_balance = converted_float(
            #             instanceBalance) - converted_float(instanceOpeningBalance)
            #         Balance = converted_float(latest_balance) + converted_float(Balance)

            #         LedgerID = account_ledger.LedgerID
            #         account_ledger.LedgerName = LedgerName
            #         account_ledger.OpeningBalance = OpeningBalance
            #         account_ledger.CrOrDr = CrOrDr
            #         account_ledger.UpdatedDate = today
            #         account_ledger.Notes = Notes
            #         account_ledger.CreatedUserID = CreatedUserID
            #         account_ledger.Action = Action
            #         account_ledger.Balance = Balance
            #         account_ledger.as_on_date = AsOnDate
            #         account_ledger.save()

            #         AccountLedger_Log.objects.create(
            #             BranchID=BranchID,
            #             TransactionID=LedgerID,
            #             LedgerName=LedgerName,
            #             LedgerCode=LedgerCode,
            #             AccountGroupUnder=AccountGroupUnder,
            #             OpeningBalance=OpeningBalance,
            #             CrOrDr=CrOrDr,
            #             UpdatedDate=today,
            #             CreatedDate=today,
            #             Notes=Notes,
            #             Action=Action,
            #             CreatedUserID=CreatedUserID,
            #             CompanyID=CompanyID,
            #             Balance=Balance,
            #             as_on_date=AsOnDate,
            #         )

            #     if LedgerPosting.objects.filter(LedgerID=LedgerID, BranchID=BranchID, VoucherMasterID=LedgerID, VoucherType="LOB", CompanyID=CompanyID).exists():
            #         ledgerPostInstance = LedgerPosting.objects.get(
            #             LedgerID=LedgerID, BranchID=BranchID, VoucherMasterID=LedgerID, VoucherType="LOB", CompanyID=CompanyID)
            #         ledgerPostInstance.delete()

            #     if converted_float(OpeningBalance) > 0:
            #         Credit = 0.00
            #         Debit = 0.00

            #         if CrOrDr == "Cr":
            #             Credit = OpeningBalance

            #         elif CrOrDr == "Dr":
            #             Debit = OpeningBalance

            #         VoucherType = "LOB"

            #         if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerName="Suspense Account").exists():
            #             RelativeLedgerID = AccountLedger.objects.get(
            #                 CompanyID=CompanyID, LedgerName="Suspense Account").LedgerID
            #         else:
            #             RelativeLedgerID = get_auto_id(
            #                 AccountLedger, BranchID, CompanyID)
            #             SuspenseLedgerCode = get_LedgerCode(
            #                 AccountLedger, BranchID, CompanyID)

            #             AccountLedger.objects.create(
            #                 LedgerID=RelativeLedgerID,
            #                 BranchID=BranchID,
            #                 LedgerName="Suspense Account",
            #                 LedgerCode=SuspenseLedgerCode,
            #                 AccountGroupUnder=26,
            #                 OpeningBalance=0,
            #                 CrOrDr="Dr",
            #                 Notes=Notes,
            #                 IsActive=True,
            #                 IsDefault=True,
            #                 CreatedDate=today,
            #                 UpdatedDate=today,
            #                 Action=Action,
            #                 CreatedUserID=CreatedUserID,
            #                 CompanyID=CompanyID,
            #             )

            #             AccountLedger_Log.objects.create(
            #                 BranchID=BranchID,
            #                 TransactionID=RelativeLedgerID,
            #                 LedgerName="Suspense Account",
            #                 LedgerCode=SuspenseLedgerCode,
            #                 AccountGroupUnder=26,
            #                 OpeningBalance=0,
            #                 CrOrDr="Dr",
            #                 Notes=Notes,
            #                 IsActive=True,
            #                 IsDefault=True,
            #                 CreatedDate=today,
            #                 UpdatedDate=today,
            #                 Action=Action,
            #                 CreatedUserID=CreatedUserID,
            #                 CompanyID=CompanyID,
            #             )
            #         IsActive = True
            #         LedgerPostingID = get_auto_LedgerPostid(
            #             LedgerPosting, BranchID, CompanyID)

            #         LedgerPosting.objects.create(
            #             LedgerPostingID=LedgerPostingID,
            #             BranchID=BranchID,
            #             Date=today,
            #             VoucherMasterID=LedgerID,
            #             VoucherType=VoucherType,
            #             VoucherNo=LedgerCode,
            #             LedgerID=LedgerID,
            #             RelatedLedgerID=RelativeLedgerID,
            #             Debit=Debit,
            #             Credit=Credit,
            #             IsActive=IsActive,
            #             Action=Action,
            #             CreatedUserID=CreatedUserID,
            #             CreatedDate=today,
            #             UpdatedDate=today,
            #             CompanyID=CompanyID,
            #         )

            #         LedgerPosting_Log.objects.create(
            #             TransactionID=LedgerPostingID,
            #             BranchID=BranchID,
            #             Date=today,
            #             VoucherMasterID=LedgerID,
            #             VoucherNo=LedgerCode,
            #             VoucherType=VoucherType,
            #             LedgerID=LedgerID,
            #             RelatedLedgerID=RelativeLedgerID,
            #             Debit=Debit,
            #             Credit=Credit,
            #             IsActive=IsActive,
            #             Action=Action,
            #             CreatedUserID=CreatedUserID,
            #             CreatedDate=today,
            #             UpdatedDate=today,
            #             CompanyID=CompanyID,
            #         )

            #         LedgerPostingID = get_auto_LedgerPostid(
            #             LedgerPosting, BranchID, CompanyID)

            #         LedgerPosting.objects.create(
            #             LedgerPostingID=LedgerPostingID,
            #             BranchID=BranchID,
            #             Date=today,
            #             VoucherMasterID=LedgerID,
            #             VoucherType=VoucherType,
            #             VoucherNo=LedgerCode,
            #             LedgerID=RelativeLedgerID,
            #             RelatedLedgerID=LedgerID,
            #             Debit=Credit,
            #             Credit=Debit,
            #             IsActive=IsActive,
            #             Action=Action,
            #             CreatedUserID=CreatedUserID,
            #             CreatedDate=today,
            #             UpdatedDate=today,
            #             CompanyID=CompanyID,
            #         )

            #         LedgerPosting_Log.objects.create(
            #             TransactionID=LedgerPostingID,
            #             BranchID=BranchID,
            #             Date=today,
            #             VoucherMasterID=LedgerID,
            #             VoucherNo=LedgerCode,
            #             VoucherType=VoucherType,
            #             LedgerID=RelativeLedgerID,
            #             RelatedLedgerID=LedgerID,
            #             Debit=Credit,
            #             Credit=Debit,
            #             IsActive=IsActive,
            #             Action=Action,
            #             CreatedUserID=CreatedUserID,
            #             CreatedDate=today,
            #             UpdatedDate=today,
            #             CompanyID=CompanyID,
            #         )

            # request , company, log_type, user, source, action, message, description
            activity_log(
                request._request,
                CompanyID,
                "Information",
                CreatedUserID,
                "Bank",
                "Edit",
                "Bank Updated Successfully.",
                "Bank Updated Successfully.",
            )

            response_data = {
                "StatusCode": 6000,
                "message": "Bank Updated Successfully!",
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Error",
            CreatedUserID,
            "Bank",
            "Edit",
            "Bank Updated Failed.",
            generate_serializer_errors(serialized._errors),
        )
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors),
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def banks(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]

    try:
        page_number = data["page_no"]
    except:
        page_number = ""

    try:
        items_per_page = data["items_per_page"]
    except:
        items_per_page = ""

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]
        if Bank.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            if page_number and items_per_page:
                instances = Bank.objects.filter(BranchID=BranchID, CompanyID=CompanyID)
                ledger_sort_pagination = list_pagination(
                    instances, items_per_page, page_number
                )

            serialized = BankRestSerializer(
                ledger_sort_pagination,
                many=True,
                context={"PriceRounding": PriceRounding},
            )

            # request , company, log_type, user, source, action, message, description
            # activity_id = activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Bank',
            #              'View', 'Bank List View successfully.', "Bank List View successfully.")
            # body_params = str(request.data)
            # Activity_Log.objects.filter(id=activity_id).update(body_params=body_params)
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "count": len(instances),
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Account Ledger Not Found in this BranchID!",
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Error",
            CreatedUserID,
            "Bank",
            "View",
            "Bank List View Failed.",
            "Invalid BranchID Given!",
        )
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def bank(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    PriceRounding = data["PriceRounding"]
    CreatedUserID = data["CreatedUserID"]

    instance = None
    if Bank.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = Bank.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = BankRestSerializer(
            instance, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding}
        )
        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Information",
            CreatedUserID,
            "Bank",
            "View",
            "Bank single page Viewed.",
            "Bank single page Viewed.",
        )
        response_data = {"StatusCode": 6000, "data": serialized.data}
    else:
        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Error",
            CreatedUserID,
            "Bank",
            "View",
            "Bank single page View failed.",
            "Bank Not Found",
        )
        response_data = {"StatusCode": 6001, "message": "Bank Not Found!"}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def delete_bank(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]

    try:
        selecte_ids = data["selecte_ids"]
    except:
        selecte_ids = []

    today = datetime.datetime.now()
    instances = None

    if selecte_ids:
        if Bank.objects.filter(CompanyID=CompanyID, pk__in=selecte_ids).exists():
            instances = Bank.objects.filter(pk__in=selecte_ids)
    else:
        if Bank.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instances = Bank.objects.filter(pk=pk)

    # if Bank.objects.filter(pk=pk, CompanyID=CompanyID).exists():
    #     instance = Bank.objects.get(pk=pk, CompanyID=CompanyID)
    if instances:
        for instance in instances:
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

            if AccountLedger.objects.filter(
                BranchID=BranchID, LedgerName=LedgerName, CompanyID=CompanyID
            ).exists():
                account_ledger = AccountLedger.objects.get(
                    LedgerName=LedgerName, CompanyID=CompanyID
                )

                LedgerID = account_ledger.LedgerID
                if (
                    not LedgerPosting.objects.filter(
                        LedgerID=LedgerID, CompanyID=CompanyID
                    )
                    .exclude(VoucherType="LOB")
                    .exists()
                ):
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

                    # request , company, log_type, user, source, action, message, description
                    activity_log(
                        request._request,
                        CompanyID,
                        "Information",
                        CreatedUserID,
                        "Bank",
                        "Deleted",
                        "Bank Deleted Successfully.",
                        "Bank Deleted Successfully",
                    )
                    response_data = {
                        "StatusCode": 6000,
                        "title": "Success",
                        "message": "Bank Deleted Successfully!",
                    }
                else:
                    response_data = {
                        "StatusCode": 6001,
                        "title": "Failed",
                        "message": "You Cant Delete this Bank",
                    }

            else:
                response_data = {
                    "StatusCode": 6001,
                    "title": "Failed",
                    "message": "You Cant Delete this Bank,this LedgerID is using somewhere!!",
                }
    else:
        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Error",
            CreatedUserID,
            "Bank",
            "Deleted",
            "Bank Deleted Failed.",
            "Bank Not Found",
        )
        response_data = {
            "StatusCode": 6001,
            "title": "Failed",
            "message": "Bank Not Found!",
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def check_server(request):
    instances = Parties.objects.filter(CreatedDate__lte='2022-06-30')
    serialize = CompanyTestSerializer(instances,many=True)
    response_data = {
        "StatusCode": 6000,
        "count": instances.count(),
        "data": serialize.data
        
    }

    return Response(response_data, status=status.HTTP_200_OK)
