from brands.models import Activity_Log,AccountLedger, AccountLedger_Log, LedgerPosting, LedgerPosting_Log, PurchaseOrderMaster,\
    SalesOrderMaster, Parties, Employee, AccountGroup, Parties_Log, Bank, Bank_Log, Employee_Log, UserTable, CompanySettings, GeneralSettings, State
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v8.accountLedgers.serializers import AccountLedgerSerializer, AccountLedgerRestSerializer, LedgerReportSerializer, AccountLedgerListSerializer, ListSerializerforPaymentAll
from api.v8.brands.serializers import ListSerializer
from api.v8.accountLedgers.serializers import ListSerializerforPayment
from api.v8.accountLedgers.functions import generate_serializer_errors
from rest_framework import status
from api.v8.banks.functions import get_auto_Bankid
from web.functions import get_auto_EmployeeID
from api.v8.accountLedgers.functions import get_auto_id, get_LedgerCode, get_auto_LedgerPostid, get_auto_idfor_party, get_shippingAddress
from main.functions import get_company, activity_log
import datetime
from api.v8.ledgerPosting.functions import convertOrderdDict
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Prefetch
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
def create_accountLedger(request):
    try:
        with transaction.atomic():
            today = datetime.datetime.now()
            data = request.data
            CompanyID_Uid = data['CompanyID']
            CompanyID = get_company(CompanyID_Uid)
            CreatedUserID = data['CreatedUserID']

            serialized = AccountLedgerSerializer(data=request.data)

            if serialized.is_valid():
                BranchID = serialized.data['BranchID']
                LedgerName = serialized.data['LedgerName']
                # LedgerCode = serialized.data['LedgerCode']
                AccountGroupUnder = serialized.data['AccountGroupUnder']
                OpeningBalance = serialized.data['OpeningBalance']
                CrOrDr = serialized.data['CrOrDr']
                Notes = serialized.data['Notes']
                IsActive = serialized.data['IsActive']
                IsDefault = serialized.data['IsDefault']
                if data['as_on_date'] and float(OpeningBalance) > 0:
                    as_on_date = data['as_on_date']
                else:
                    as_on_date = today

                LedgerID = get_auto_id(AccountLedger, BranchID, CompanyID)

                LedgerCode = get_LedgerCode(AccountLedger, BranchID, CompanyID)

                Action = 'A'

                if CrOrDr == "0":
                    CrOrDr = "Dr"

                elif CrOrDr == "1":
                    CrOrDr = "Cr"

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
                    Balance = 0
                    if float(OpeningBalance) > 0:
                        if CrOrDr == "Cr":
                            Balance = float(OpeningBalance) * -1

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
                        Notes=Notes,
                        IsActive=IsActive,
                        IsDefault=IsDefault,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                        as_on_date=as_on_date,
                        Balance=Balance
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
                        IsActive=IsActive,
                        IsDefault=IsDefault,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                        as_on_date=as_on_date,
                        Balance=Balance
                    )

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

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=as_on_date,
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
                            Date=as_on_date,
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

                    # saving data to party table for account group under 10 and 29
                    if AccountGroupUnder == 10 or AccountGroupUnder == 29:
                        FirstName = LedgerName
                        if AccountGroupUnder == 10:
                            PartyType = "customer"

                        elif AccountGroupUnder == 29:
                            PartyType = "supplier"

                        PartyID = get_auto_idfor_party(
                            Parties, BranchID, CompanyID)
                        PartyCode = LedgerCode

                        Country = ''
                        State = ''
                        if CompanySettings.objects.filter(id=CompanyID_Uid).exists():
                            Country = CompanySettings.objects.get(
                                id=CompanyID_Uid).Country.id
                            State = CompanySettings.objects.get(
                                id=CompanyID_Uid).State.id

                        Parties.objects.create(
                            PartyID=PartyID,
                            BranchID=BranchID,
                            PartyType=PartyType,
                            LedgerID=LedgerID,
                            PartyCode=PartyCode,
                            FirstName=FirstName,
                            DisplayName=FirstName,
                            PartyName=FirstName,
                            PriceCategoryID=1,
                            RouteID=1,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            OpeningBalance=OpeningBalance,
                            CompanyID=CompanyID,
                            State=State,
                            Country=Country,
                            State_Shipping=State,
                            Country_Shipping=Country,
                        )

                        Parties_Log.objects.create(
                            TransactionID=PartyID,
                            BranchID=BranchID,
                            PartyType=PartyType,
                            LedgerID=LedgerID,
                            PartyCode=PartyCode,
                            FirstName=FirstName,
                            DisplayName=FirstName,
                            PartyName=FirstName,
                            PriceCategoryID=1,
                            RouteID=1,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            OpeningBalance=OpeningBalance,
                            CompanyID=CompanyID,
                            State=State,
                            Country=Country,
                            State_Shipping=State,
                            Country_Shipping=Country,
                        )

                    elif AccountGroupUnder == 8:

                        BankID = get_auto_Bankid(Bank, BranchID, CompanyID)

                        Bank.objects.create(
                            BankID=BankID,
                            BranchID=BranchID,
                            LedgerCode=LedgerCode,
                            Name=LedgerName,
                            LedgerName=LedgerName,
                            CrOrDr=CrOrDr,
                            OpeningBalance=OpeningBalance,
                            Notes=Notes,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            Action=Action,
                            CompanyID=CompanyID,
                        )

                        Bank_Log.objects.create(
                            TransactionID=BankID,
                            BranchID=BranchID,
                            LedgerCode=LedgerCode,
                            Name=LedgerName,
                            LedgerName=LedgerName,
                            CrOrDr=CrOrDr,
                            OpeningBalance=OpeningBalance,
                            Notes=Notes,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            Action=Action,
                            CompanyID=CompanyID,
                        )

                    elif AccountGroupUnder == 32:

                        EmployeeID = get_auto_EmployeeID(
                            Employee, BranchID, CompanyID)

                        Employee.objects.create(
                            EmployeeID=EmployeeID,
                            BranchID=BranchID,
                            EmployeeCode=LedgerCode,
                            EmployeeName=LedgerName,
                            LedgerID=LedgerID,
                            DateOfJoining=today,
                            Notes=Notes,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                        Employee_Log.objects.create(
                            TransactionID=EmployeeID,
                            BranchID=BranchID,
                            EmployeeCode=LedgerCode,
                            EmployeeName=LedgerName,
                            LedgerID=LedgerID,
                            DateOfJoining=today,
                            Notes=Notes,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )

                    #request , company, log_type, user, source, action, message, description
                    # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'AccountLedger',
                    #              'Create', 'AccountLedger created successfully.', 'AccountLedger saved successfully.')

                    data = {"LedgerID": LedgerID}
                    data.update(serialized.data)
                    response_data = {
                        "StatusCode": 6000,
                        "data": data
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    #request , company, log_type, user, source, action, message, description
                    activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'AccountLedger',
                                 'Create', 'AccountLedger created failed.', 'AccountLedger Already Exist!')
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Ledger Name Already Exist!!!"
                    }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'error', CreatedUserID, 'AccountLedger', 'Create',
                             'AccountLedger created failed.', generate_serializer_errors(serialized._errors))
                response_data = {
                    "StatusCode": 6001,
                    "message": generate_serializer_errors(serialized._errors)
                }

                return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again"
        }

        activity_id = activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'AccountLedger',
                     'Create', str(e), err_descrb)
        body_params = str(request.data)
        Activity_Log.objects.filter(id=activity_id).update(body_params=body_params)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def edit_accountLedger(request, pk):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            CreatedUserID = data['CreatedUserID']

            today = datetime.datetime.now()
            serialized = AccountLedgerSerializer(data=request.data)
            instance = AccountLedger.objects.get(pk=pk, CompanyID=CompanyID)

            ledgerPostInstance = None

            LedgerID = instance.LedgerID
            LedgerCode = instance.LedgerCode
            BranchID = instance.BranchID
            instanceLedgerName = instance.LedgerName
            CreatedDate = instance.CreatedDate

            if serialized.is_valid():
                LedgerName = serialized.data['LedgerName']
                # LedgerCode = serialized.data['LedgerCode']
                AccountGroupUnder = serialized.data['AccountGroupUnder']
                OpeningBalance = serialized.data['OpeningBalance']
                CrOrDr = serialized.data['CrOrDr']
                Notes = serialized.data['Notes']
                IsActive = serialized.data['IsActive']
                IsDefault = serialized.data['IsDefault']
                if data['as_on_date'] and float(OpeningBalance) > 0:
                    as_on_date = data['as_on_date']
                else:
                    as_on_date = today

                Action = 'M'

                if LedgerPosting.objects.filter(VoucherMasterID=LedgerID, BranchID=BranchID, CompanyID=CompanyID, VoucherType="LOB").exists():
                    ledgerPostInstances = LedgerPosting.objects.filter(
                        VoucherMasterID=LedgerID, BranchID=BranchID, CompanyID=CompanyID, VoucherType="LOB")
                    for ledgerPostInstance in ledgerPostInstances:
                        ledgerPostInstance.delete()

                if CrOrDr == "0":
                    CrOrDr = "Dr"

                elif CrOrDr == "1":
                    CrOrDr = "Cr"

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
                    Balance = 0
                    if float(OpeningBalance) > 0:
                        if CrOrDr == "Cr":
                            Balance = float(OpeningBalance) * -1

                        elif CrOrDr == "Dr":
                            Balance = OpeningBalance

                    instanceBalance = instance.Balance
                    instanceOpeningBalance = instance.OpeningBalance
                    instanceCrOrDr = instance.CrOrDr
                    if instanceCrOrDr == "Cr":
                        instanceOpeningBalance = float(
                            instanceOpeningBalance) * -1
                    elif instanceCrOrDr == "Dr":
                        instanceOpeningBalance = instanceOpeningBalance

                    latest_balance = float(
                        instanceBalance) - float(instanceOpeningBalance)
                    Balance = float(latest_balance) + float(Balance)
                    # instance.LedgerCode = LedgerCode
                    instance.LedgerName = LedgerName
                    instance.AccountGroupUnder = AccountGroupUnder
                    instance.OpeningBalance = OpeningBalance
                    instance.CrOrDr = CrOrDr
                    instance.Notes = Notes
                    instance.IsActive = IsActive
                    instance.IsDefault = IsDefault
                    instance.Action = Action
                    instance.UpdatedDate = today
                    instance.CreatedUserID = CreatedUserID
                    instance.as_on_date = as_on_date
                    instance.Balance = Balance
                    instance.save()

                    AccountLedger_Log.objects.create(
                        BranchID=BranchID,
                        TransactionID=LedgerID,
                        LedgerName=LedgerName,
                        LedgerCode=LedgerCode,
                        AccountGroupUnder=AccountGroupUnder,
                        OpeningBalance=OpeningBalance,
                        CrOrDr=CrOrDr,
                        Notes=Notes,
                        IsActive=IsActive,
                        IsDefault=IsDefault,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        Action=Action,
                        CompanyID=CompanyID,
                        as_on_date=as_on_date,
                        Balance=Balance,
                    )

                    if float(OpeningBalance) > 0:
                        Credit = 0.00
                        Debit = 0.00
                        if CrOrDr == "Cr":
                            Credit = OpeningBalance

                        elif CrOrDr == "Dr":
                            Debit = OpeningBalance

                        VoucherType = "LOB"

                        # if LedgerPosting.objects.filter(LedgerID=LedgerID, BranchID=BranchID, VoucherMasterID=LedgerID, VoucherType="LOB", CompanyID=CompanyID).exists():
                        #     ledgerPostInstance = LedgerPosting.objects.get(
                        #         LedgerID=LedgerID, BranchID=BranchID, VoucherMasterID=LedgerID, VoucherType="LOB", CompanyID=CompanyID)
                        #     ledgerPostInstance.Date = today
                        #     ledgerPostInstance.Debit = Debit
                        #     ledgerPostInstance.Credit = Credit
                        #     ledgerPostInstance.Action = "M"
                        #     ledgerPostInstance.UpdatedDate = today
                        #     ledgerPostInstance.CreatedUserID = CreatedUserID
                        #     ledgerPostInstance.save()

                        #     LedgerPosting_Log.objects.create(
                        #         TransactionID=ledgerPostInstance.LedgerPostingID,
                        #         BranchID=BranchID,
                        #         Date=today,
                        #         VoucherMasterID=LedgerID,
                        #         VoucherType=VoucherType,
                        #         VoucherNo=LedgerCode,
                        #         LedgerID=LedgerID,
                        #         Debit=Debit,
                        #         Credit=Credit,
                        #         IsActive=IsActive,
                        #         Action=Action,
                        #         CreatedUserID=CreatedUserID,
                        #         CreatedDate=today,
                        #         UpdatedDate=today,
                        #         CompanyID=CompanyID,
                        #     )
                        # else:
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
                    # else:
                    #     Credit = 0.00
                    #     Debit = 0.00
                    #     if CrOrDr == "Cr":
                    #         Credit = OpeningBalance

                    #     elif CrOrDr == "Dr":
                    #         Debit = OpeningBalance
                    #     if LedgerPosting.objects.filter(BranchID=BranchID, VoucherMasterID=LedgerID, VoucherType="LOB", CompanyID=CompanyID).exists():
                    #         ledgerPostInstances = LedgerPosting.objects.filter( BranchID=BranchID, VoucherMasterID=LedgerID, VoucherType="LOB", CompanyID=CompanyID)
                    #         for ledgerPostInstance in ledgerPostInstances:
                    #             ledgerPostInstance.delete()
                        # ledgerPostInstance.Date = today
                        # ledgerPostInstance.Debit = Debit
                        # ledgerPostInstance.Credit = Credit
                        # ledgerPostInstance.Action = "D"
                        # ledgerPostInstance.UpdatedDate = today
                        # ledgerPost_CreatedDate = ledgerPostInstance.CreatedDate
                        # ledgerPostInstance.delete()

                    if AccountGroupUnder == 10 or AccountGroupUnder == 29:

                        FirstName = LedgerName
                        if AccountGroupUnder == 10:
                            PartyType = "customer"

                        elif AccountGroupUnder == 29:
                            PartyType = "supplier"

                        PartyCode = LedgerCode

                        if Parties.objects.filter(BranchID=BranchID, LedgerID=LedgerID, PartyType=PartyType, CompanyID=CompanyID).exists():
                            partyInstance = Parties.objects.get(
                                BranchID=BranchID, LedgerID=LedgerID, PartyType=PartyType, CompanyID=CompanyID)
                            partyInstance.FirstName = FirstName
                            partyInstance.Action = "M"
                            partyInstance.UpdatedDate = today
                            partyInstance.CreatedUserID = CreatedUserID
                            partyInstance.OpeningBalance = OpeningBalance
                            partyInstance.save()

                            Parties_Log.objects.create(
                                TransactionID=partyInstance.PartyID,
                                BranchID=BranchID,
                                PartyType=PartyType,
                                LedgerID=LedgerID,
                                PartyCode=PartyCode,
                                FirstName=FirstName,
                                PriceCategoryID=1,
                                RouteID=1,
                                IsActive=IsActive,
                                Action="M",
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                OpeningBalance=OpeningBalance,
                                CompanyID=CompanyID,
                            )

                    elif AccountGroupUnder == 8:

                        if Bank.objects.filter(BranchID=BranchID, LedgerCode=LedgerCode, CompanyID=CompanyID).exists():
                            bankInstance = Bank.objects.get(
                                BranchID=BranchID, LedgerCode=LedgerCode, CompanyID=CompanyID)
                            bankInstance.Name = LedgerName
                            bankInstance.LedgerName = LedgerName
                            bankInstance.CrOrDr = CrOrDr
                            bankInstance.OpeningBalance = OpeningBalance
                            bankInstance.Notes = Notes
                            bankInstance.CreatedUserID = CreatedUserID
                            bankInstance.UpdatedDate = today
                            bankInstance.Action = "M"
                            bankInstance.save()

                            Bank_Log.objects.create(
                                TransactionID=bankInstance.BankID,
                                BranchID=BranchID,
                                LedgerCode=LedgerCode,
                                Name=LedgerName,
                                LedgerName=LedgerName,
                                CrOrDr=CrOrDr,
                                OpeningBalance=OpeningBalance,
                                Notes=Notes,
                                CreatedUserID=CreatedUserID,
                                CreatedDate=today,
                                UpdatedDate=today,
                                Action=Action,
                                CompanyID=CompanyID,
                            )

                    elif AccountGroupUnder == 32:

                        if Employee.objects.filter(BranchID=BranchID, LedgerID=LedgerID, EmployeeCode=LedgerCode, CompanyID=CompanyID).exists():
                            employeeInstance = Employee.objects.get(
                                BranchID=BranchID, LedgerID=LedgerID, EmployeeCode=LedgerCode, CompanyID=CompanyID)
                            employeeInstance.EmployeeName = LedgerName
                            employeeInstance.Notes = Notes
                            employeeInstance.Action = "M"
                            employeeInstance.UpdatedDate = today
                            employeeInstance.CreatedUserID = CreatedUserID
                            employeeInstance.save()

                            Employee_Log.objects.create(
                                TransactionID=employeeInstance.EmployeeID,
                                BranchID=BranchID,
                                EmployeeCode=LedgerCode,
                                FirstName=LedgerName,
                                LedgerID=LedgerID,
                                DateOfJoining=today,
                                Notes=Notes,
                                Action=Action,
                                CreatedUserID=CreatedUserID,
                                UpdatedDate=today,
                                CreatedDate=today,
                                CompanyID=CompanyID,
                            )

                    #request , company, log_type, user, source, action, message, description
                    activity_log(request._request, CompanyID, 'error', CreatedUserID, 'AccountLedger',
                                 'Edit', 'AccountLedger Updated Successfully.', 'AccountLedger Updated Successfully.')
                    response_data = {
                        "StatusCode": 6000,
                        "data": serialized.data
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
                        Balance = 0
                        if float(OpeningBalance) > 0:
                            if CrOrDr == "Cr":
                                Balance = float(OpeningBalance) * -1

                            elif CrOrDr == "Dr":
                                Balance = OpeningBalance

                        instanceBalance = instance.Balance
                        instanceOpeningBalance = instance.OpeningBalance
                        instanceCrOrDr = instance.CrOrDr
                        if instanceCrOrDr == "Cr":
                            latest_balance = float(
                                instanceBalance) + float(instanceOpeningBalance)
                        elif instanceCrOrDr == "Dr":
                            latest_balance = float(
                                instanceBalance) - float(instanceOpeningBalance)

                        Balance = float(latest_balance) + float(Balance)

                        instance.LedgerName = LedgerName
                        # instance.LedgerCode = LedgerCode
                        instance.AccountGroupUnder = AccountGroupUnder
                        instance.OpeningBalance = OpeningBalance
                        instance.CrOrDr = CrOrDr
                        instance.Notes = Notes
                        instance.IsActive = IsActive
                        instance.IsDefault = IsDefault
                        instance.Action = Action
                        instance.UpdatedDate = today
                        instance.CreatedUserID = CreatedUserID
                        instance.as_on_date = as_on_date
                        instance.Balance = Balance
                        instance.save()

                        AccountLedger_Log.objects.create(
                            BranchID=BranchID,
                            TransactionID=LedgerID,
                            LedgerName=LedgerName,
                            LedgerCode=LedgerCode,
                            AccountGroupUnder=AccountGroupUnder,
                            OpeningBalance=OpeningBalance,
                            CrOrDr=CrOrDr,
                            Notes=Notes,
                            IsActive=IsActive,
                            IsDefault=IsDefault,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            Action=Action,
                            CompanyID=CompanyID,
                            as_on_date=as_on_date,
                            Balance=Balance,
                        )

                        if float(OpeningBalance) > 0:
                            Credit = 0.00
                            Debit = 0.00

                            if CrOrDr == "Cr":
                                Credit = OpeningBalance

                            elif CrOrDr == "Dr":
                                Debit = OpeningBalance

                            VoucherType = "LOB"

                            # if LedgerPosting.objects.filter(LedgerID=LedgerID, BranchID=BranchID, VoucherMasterID=LedgerID, VoucherType="LOB", CompanyID=CompanyID).exists():
                            #     ledgerPostInstance = LedgerPosting.objects.get(
                            #         LedgerID=LedgerID, BranchID=BranchID, VoucherMasterID=LedgerID, VoucherType="LOB", CompanyID=CompanyID)
                            #     ledgerPostInstance.Date = today
                            #     ledgerPostInstance.Debit = Debit
                            #     ledgerPostInstance.Credit = Credit
                            #     ledgerPostInstance.Action = "M"
                            #     ledgerPostInstance.UpdatedDate = today
                            #     ledgerPostInstance.CreatedUserID = CreatedUserID
                            #     ledgerPostInstance.save()

                            #     LedgerPosting_Log.objects.create(
                            #         TransactionID=ledgerPostInstance.LedgerPostingID,
                            #         BranchID=BranchID,
                            #         Date=today,
                            #         VoucherMasterID=LedgerID,
                            #         VoucherType=VoucherType,
                            #         VoucherNo=LedgerCode,
                            #         LedgerID=LedgerID,
                            #         Debit=Debit,
                            #         Credit=Credit,
                            #         IsActive=IsActive,
                            #         Action=Action,
                            #         CreatedUserID=CreatedUserID,
                            #         CreatedDate=today,
                            #         UpdatedDate=today,
                            #         CompanyID=CompanyID,
                            #     )
                            # else:
                            #     LedgerPostingID = get_auto_LedgerPostid(
                            #         LedgerPosting, BranchID, CompanyID)

                            #     LedgerPosting.objects.create(
                            #         LedgerPostingID=LedgerPostingID,
                            #         BranchID=BranchID,
                            #         Date=today,
                            #         VoucherMasterID=LedgerID,
                            #         VoucherType=VoucherType,
                            #         VoucherNo=LedgerCode,
                            #         LedgerID=LedgerID,
                            #         Debit=Debit,
                            #         Credit=Credit,
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
                            #         Date=today,
                            #         VoucherMasterID=LedgerID,
                            #         VoucherNo=LedgerCode,
                            #         VoucherType=VoucherType,
                            #         LedgerID=LedgerID,
                            #         Debit=Debit,
                            #         Credit=Credit,
                            #         IsActive=IsActive,
                            #         Action=Action,
                            #         CreatedUserID=CreatedUserID,
                            #         CreatedDate=today,
                            #         UpdatedDate=today,
                            #         CompanyID=CompanyID,
                            #     )
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
                        # else:
                        #     Credit = 0.00
                        #     Debit = 0.00
                        #     if CrOrDr == "Cr":
                        #         Credit = OpeningBalance

                        #     elif CrOrDr == "Dr":
                        #         Debit = OpeningBalance
                        #     # if LedgerPosting.objects.filter(LedgerID=LedgerID, BranchID=BranchID, VoucherMasterID=LedgerID, VoucherType="LOB", CompanyID=CompanyID).exists():
                        #     #     ledgerPostInstance = LedgerPosting.objects.get(
                        #     #         LedgerID=LedgerID, BranchID=BranchID, VoucherMasterID=LedgerID, VoucherType="LOB", CompanyID=CompanyID)
                        #     #     ledgerPostInstance.Date = today
                        #     #     ledgerPostInstance.Debit = Debit
                        #     #     ledgerPostInstance.Credit = Credit
                        #     #     ledgerPostInstance.Action = "D"
                        #     #     ledgerPostInstance.UpdatedDate = today
                        #     #     ledgerPostInstance.CreatedUserID = CreatedUserID
                        #     #     ledgerPost_CreatedDate = ledgerPostInstance.CreatedDate
                        #     #     ledgerPostInstance.delete()

                        #     if LedgerPosting.objects.filter(BranchID=BranchID, VoucherMasterID=LedgerID, VoucherType="LOB", CompanyID=CompanyID).exists():
                        #         ledgerPostInstances = LedgerPosting.objects.filter( BranchID=BranchID, VoucherMasterID=LedgerID, VoucherType="LOB", CompanyID=CompanyID)
                        #         for ledgerPostInstance in ledgerPostInstances:
                        #             ledgerPostInstance.delete()

                        if AccountGroupUnder == 10 or AccountGroupUnder == 29:

                            FirstName = LedgerName
                            if AccountGroupUnder == 10:
                                PartyType = "customer"

                            elif AccountGroupUnder == 29:
                                PartyType = "supplier"

                            PartyCode = LedgerCode

                            if Parties.objects.filter(BranchID=BranchID, LedgerID=LedgerID, PartyType=PartyType, CompanyID=CompanyID).exists():
                                partyInstance = Parties.objects.get(
                                    BranchID=BranchID, LedgerID=LedgerID, PartyType=PartyType, CompanyID=CompanyID)
                                partyInstance.FirstName = FirstName
                                partyInstance.Action = "M"
                                partyInstance.UpdatedDate = today
                                partyInstance.CreatedUserID = CreatedUserID
                                partyInstance.OpeningBalance = OpeningBalance
                                partyInstance.save()

                                Parties_Log.objects.create(
                                    TransactionID=partyInstance.PartyID,
                                    BranchID=BranchID,
                                    PartyType=PartyType,
                                    LedgerID=LedgerID,
                                    PartyCode=PartyCode,
                                    FirstName=FirstName,
                                    PriceCategoryID=1,
                                    RouteID=1,
                                    IsActive=IsActive,
                                    Action="M",
                                    CreatedUserID=CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    OpeningBalance=OpeningBalance,
                                    CompanyID=CompanyID,
                                )

                        elif AccountGroupUnder == 8:
                            if Bank.objects.filter(BranchID=BranchID, LedgerCode=LedgerCode, CompanyID=CompanyID).exists():
                                bankInstance = Bank.objects.get(
                                    BranchID=BranchID, LedgerCode=LedgerCode, CompanyID=CompanyID)
                                bankInstance.Name = LedgerName
                                bankInstance.LedgerName = LedgerName
                                bankInstance.CrOrDr = CrOrDr
                                bankInstance.OpeningBalance = OpeningBalance
                                bankInstance.Notes = Notes
                                bankInstance.CreatedUserID = CreatedUserID
                                bankInstance.UpdatedDate = today
                                bankInstance.Action = "M"
                                bankInstance.save()

                                Bank_Log.objects.create(
                                    TransactionID=bankInstance.bankInstanceBankID,
                                    BranchID=BranchID,
                                    LedgerCode=LedgerCode,
                                    Name=LedgerName,
                                    LedgerName=LedgerName,
                                    CrOrDr=CrOrDr,
                                    OpeningBalance=OpeningBalance,
                                    Notes=Notes,
                                    CreatedUserID=CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    Action=Action,
                                    CompanyID=CompanyID,
                                )

                        elif AccountGroupUnder == 32:
                            if Employee.objects.filter(BranchID=BranchID, LedgerID=LedgerID, EmployeeCode=LedgerCode, CompanyID=CompanyID).exists():
                                employeeInstance = Employee.objects.filter(
                                    BranchID=BranchID, LedgerID=LedgerID, EmployeeCode=LedgerCode, CompanyID=CompanyID)
                                employeeInstance.EmployeeName = LedgerName
                                employeeInstance.Notes = Notes
                                employeeInstance.Action = "M"
                                employeeInstance.UpdatedDate = today
                                employeeInstance.CreatedUserID = CreatedUserID
                                employeeInstance.save()

                                Employee_Log.objects.create(
                                    TransactionID=EmployeeID,
                                    BranchID=BranchID,
                                    EmployeeCode=LedgerCode,
                                    EmployeeName=LedgerName,
                                    LedgerID=LedgerID,
                                    DateOfJoining=today,
                                    Notes=Notes,
                                    Action=Action,
                                    CreatedUserID=CreatedUserID,
                                    CreatedDate=today,
                                    UpdatedDate=today,
                                    CompanyID=CompanyID,
                                )
                        #request , company, log_type, user, source, action, message, description
                        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'AccountLedger',
                        #              'Edit', 'AccountLedger Updated Successfully.', 'AccountLedger Updated Successfully.')
                        response_data = {
                            "StatusCode": 6000,
                            "data": serialized.data
                        }

                        return Response(response_data, status=status.HTTP_200_OK)
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'AccountLedger', 'Edit',
                             'AccountLedger Updated Failed.', generate_serializer_errors(serialized._errors))
                response_data = {
                    "StatusCode": 6001,
                    "message": generate_serializer_errors(serialized._errors)
                }

                return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again"
        }

        activity_id = activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'AccountLedger',
                     'Edit', str(e), err_descrb)
        body_params = str(request.data)
        Activity_Log.objects.filter(id=activity_id).update(body_params=body_params)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def accountLedgers(request):
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

    try:
        ledger_name = data['ledger_name']
    except:
        ledger_name = ""

    try:
        length = data['length']
    except:
        length = ""

    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if AccountLedger.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            if page_number and items_per_page:
                if ledger_name:
                    if float(length) < 3:
                        ledger_sort_pagination = AccountLedger.objects.filter(
                            BranchID=BranchID, LedgerName__icontains=ledger_name, CompanyID=CompanyID)[:10]
                    else:
                        ledger_sort_pagination = AccountLedger.objects.filter(
                            BranchID=BranchID, LedgerName__icontains=ledger_name, CompanyID=CompanyID)
                    count = len(ledger_sort_pagination)
                else:
                    instances = AccountLedger.objects.filter(
                        BranchID=BranchID, CompanyID=CompanyID)
                    count = len(instances)
                    ledger_sort_pagination = list_pagination(
                        instances,
                        items_per_page,
                        page_number
                    )
            else:
                ledger_sort_pagination = AccountLedger.objects.filter(
                    BranchID=BranchID, CompanyID=CompanyID)
                count = len(ledger_sort_pagination)
            serialized = AccountLedgerRestSerializer(ledger_sort_pagination, many=True, context={"CompanyID": CompanyID,
                                                                                                 "PriceRounding": PriceRounding})

            orderdDict = serialized.data
            jsnDatas = convertOrderdDict(orderdDict)

            final_Array = []
            for i in jsnDatas:
                id = i['id']
                BranchID = i['BranchID']
                LedgerName = i['LedgerName']
                LedgerID = i['LedgerID']
                LedgerCode = i['LedgerCode']
                AccountGroupUnder = i['AccountGroupUnder']
                AccountGroupName = i['AccountGroupName']
                OpeningBalance = i['OpeningBalance']
                CrOrDr = i['CrOrDr']
                Notes = i['Notes']
                IsActive = i['IsActive']
                IsDefault = i['IsDefault']
                CreatedDate = i['CreatedDate']
                UpdatedDate = i['UpdatedDate']
                CreatedUserID = i['CreatedUserID']
                Action = i['Action']
                as_on_date = i['as_on_date']

                ledger_instances = LedgerPosting.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID)
                TotalDebit = 0
                TotalCredit = 0

                for i in ledger_instances:
                    TotalDebit += float(i.Debit)
                    TotalCredit += float(i.Credit)

                Balance = float(TotalDebit) - float(TotalCredit)

                final_dict = {
                    "id": id,
                    "BranchID": BranchID,
                    "LedgerName": LedgerName,
                    "LedgerID": LedgerID,
                    "LedgerCode": LedgerCode,
                    "AccountGroupUnder": AccountGroupUnder,
                    "AccountGroupName": AccountGroupName,
                    "OpeningBalance": OpeningBalance,
                    "CrOrDr": CrOrDr,
                    "Notes": Notes,
                    "IsActive": IsActive,
                    "IsDefault": IsDefault,
                    "CreatedDate": CreatedDate,
                    "UpdatedDate": UpdatedDate,
                    "CreatedUserID": CreatedUserID,
                    "Action": Action,
                    "Balance": round(Balance, PriceRounding),
                    "as_on_date": as_on_date
                }

                final_Array.append(final_dict)

            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'AccountLedger',
            #              'View', 'AccountLedger List Viewd.', "User Viewd AccountLedger List.")

            response_data = {
                "StatusCode": 6000,
                "data": final_Array,
                "count": count,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'AccountLedger', 'View',
            #              'AccountLedger List Viewd failed.', "Account Ledger Not Found under this Branch")
            response_data = {
                "StatusCode": 6001,
                "message": "Account Ledger Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'AccountLedger',
        #              'View', 'AccountLedger List Viewd failed.', "InValid BranchID Given!")
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def accountLedger(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']

    instance = None

    if AccountLedger.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = AccountLedger.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = AccountLedgerRestSerializer(instance, context={"CompanyID": CompanyID,
                                                                    "PriceRounding": PriceRounding})
        #request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'AccountLedger',
        #              'View', 'AccountLedger Single Viewd.', "User AccountLedger Single Page Viewd.")
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'AccountLedger',
                     'View', 'AccountLedger Single View failed.', "AccountLedger Not Found.")
        response_data = {
            "StatusCode": 6001,
            "message": "Account Ledger Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_accountLedger(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instances = None
    ledgerPostInstance = None
    LPInstances = None
    purchaseOrderMaster_exist = None
    salesOrderMaster_exist = None
    parties_exist = None
    employees_exist = None

    try:
        selecte_ids = data['selecte_ids']
    except:
        selecte_ids = []

    if selecte_ids:
        if AccountLedger.objects.filter(CompanyID=CompanyID, pk__in=selecte_ids).exists():
            instances = AccountLedger.objects.filter(pk__in=selecte_ids)
    else:
        if AccountLedger.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instances = AccountLedger.objects.filter(pk=pk)

    # if AccountLedger.objects.filter(pk=pk).exists():
    #     instance = AccountLedger.objects.get(pk=pk)
    if instances:
        for instance in instances:
            BranchID = instance.BranchID
            LedgerID = instance.LedgerID
            LedgerName = instance.LedgerName
            LedgerCode = instance.LedgerCode
            AccountGroupUnder = instance.AccountGroupUnder
            OpeningBalance = instance.OpeningBalance
            CrOrDr = instance.CrOrDr
            Notes = instance.Notes
            IsActive = instance.IsActive
            IsDefault = instance.IsDefault
            Action = "D"

            LPInstances = LedgerPosting.objects.filter(
                BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID).exclude(VoucherType="LOB")

            purchaseOrderMaster_exist = PurchaseOrderMaster.objects.filter(
                BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID).exists()
            salesOrderMaster_exist = SalesOrderMaster.objects.filter(
                BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID).exists()
            parties_exist = Parties.objects.filter(
                BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID).exists()
            employees_exist = Employee.objects.filter(
                BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID).exists()

            if not employees_exist and not parties_exist and not salesOrderMaster_exist and not purchaseOrderMaster_exist and not LPInstances:
                # if not LPInstances:
                instance.delete()

                AccountLedger_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=LedgerID,
                    LedgerName=LedgerName,
                    LedgerCode=LedgerCode,
                    AccountGroupUnder=AccountGroupUnder,
                    OpeningBalance=OpeningBalance,
                    CrOrDr=CrOrDr,
                    Notes=Notes,
                    IsActive=IsActive,
                    IsDefault=IsDefault,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=Action,
                    CompanyID=CompanyID,
                )

                if LedgerPosting.objects.filter(VoucherMasterID=LedgerID, BranchID=BranchID, VoucherType="LOB", CompanyID=CompanyID).exists():
                    ledgerPostInstances = LedgerPosting.objects.filter(
                        VoucherMasterID=LedgerID, BranchID=BranchID, VoucherType="LOB", CompanyID=CompanyID)

                    for ledgerPostInstance in ledgerPostInstances:
                        LedgerPostingID = ledgerPostInstance.LedgerPostingID
                        VoucherType = ledgerPostInstance.VoucherType
                        LedgerID = ledgerPostInstance.LedgerID
                        RelatedLedgerID = ledgerPostInstance.RelatedLedgerID
                        Debit = ledgerPostInstance.Debit
                        Credit = ledgerPostInstance.Credit
                        IsActive = ledgerPostInstance.IsActive
                        ledgerPostInstance.delete()

                        LedgerPosting_Log.objects.create(
                            TransactionID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=today,
                            VoucherMasterID=LedgerID,
                            VoucherType=VoucherType,
                            LedgerID=LedgerID,
                            RelatedLedgerID=RelatedLedgerID,
                            Debit=Debit,
                            Credit=Credit,
                            IsActive=IsActive,
                            Action=Action,
                            CreatedUserID=CreatedUserID,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CompanyID=CompanyID,
                        )
                party_group = [10, 29]
                if AccountGroupUnder == 8:
                    if Bank.objects.filter(BranchID=BranchID, LedgerCode=LedgerCode, CompanyID=CompanyID).exists():
                        bankInstance = Bank.objects.get(
                            BranchID=BranchID, LedgerCode=LedgerCode, CompanyID=CompanyID)
                        bankInstance.delete()

                if AccountGroupUnder in party_group:
                    if Parties.objects.filter(BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID).exists():
                        partyInstances = Parties.objects.filter(
                            BranchID=BranchID, LedgerID=LedgerID, CompanyID=CompanyID)
                        for i in partyInstances:
                            i.delete()

                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'AccountLedger',
                             'Delete', 'AccountLedger Deleted Successfully.', "AccountLedger Deleted Successfully.")

                response_data = {
                    "StatusCode": 6000,
                    "title": "Success",
                    "message": "Account Ledger Deleted Successfully!"
                }

            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'AccountLedger', 'Delete',
                             'AccountLedger Deleted Failed.', "Cant Delete this AccountLedger,this LedgerID is using somewhere")
                response_data = {
                    "StatusCode": 6001,
                    "title": "Failed",
                    "message": "You Cant Delete this AccountLedger,this LedgerID is using somewhere!!"
                }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'AccountLedger',
                     'Delete', 'AccountLedger Deleted Failed.', "Account Ledger Not Found!")
        response_data = {
            "StatusCode": 6001,
            "title": "Failed",
            "message": "Account Ledger Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def ledgerListByID(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    try:
        type_invoice = data['type_invoice']
    except:
        type_invoice = "None"

    try:
        ledger_name = data['ledger_name']
    except:
        ledger_name = ""

    try:
        length = data['length']
    except:
        length = ""

    try:
        load_data = data['load_data']
    except:
        load_data = False

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        check_ShowSupplierInSales = False
        check_ShowCustomerInPurchase = False
        check_ShowEmployeesInSales = False
        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="ShowSupplierInSales").exists():
            check_ShowSupplierInSales = GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="ShowSupplierInSales").SettingsValue

        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="ShowCustomerInPurchase").exists():
            check_ShowCustomerInPurchase = GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="ShowCustomerInPurchase").SettingsValue

        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="ShowEmployeesInSales").exists():
            check_ShowEmployeesInSales = GeneralSettings.objects.get(
                CompanyID=CompanyID, SettingsType="ShowEmployeesInSales").SettingsValue

        if AccountLedger.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            if UserTable.objects.filter(CompanyID=CompanyID, customer__user__pk=CreatedUserID, DefaultAccountForUser=True).exists():
                Cash_Account = UserTable.objects.get(
                    CompanyID=CompanyID, customer__user__pk=CreatedUserID).Cash_Account
                Bank_Account = UserTable.objects.get(
                    CompanyID=CompanyID, customer__user__pk=CreatedUserID).Bank_Account
                AccountGroupUnder_list = [10, 29]
                if type_invoice == "SalesInvoice":
                    if check_ShowSupplierInSales == False or check_ShowSupplierInSales == "False":
                        AccountGroupUnder_list = [10]
                    if check_ShowEmployeesInSales == True or check_ShowEmployeesInSales == "True":
                        AccountGroupUnder_list.append(32)
                elif type_invoice == "PurchaseInvoice":
                    if check_ShowCustomerInPurchase == False or check_ShowCustomerInPurchase == "False":
                        AccountGroupUnder_list = [29]
                account_groupunder_instances = AccountLedger.objects.filter(
                    BranchID=BranchID, CompanyID=CompanyID, AccountGroupUnder__in=AccountGroupUnder_list)
                ledger = [Cash_Account, Bank_Account]
                for account_groupunder in account_groupunder_instances:
                    LedgerID = account_groupunder.LedgerID
                    ledger.append(LedgerID)

                if ledger_name:
                    if float(length) < 3:
                        instances = AccountLedger.objects.filter(
                            BranchID=BranchID, CompanyID=CompanyID, LedgerName__icontains=ledger_name, LedgerID__in=ledger)[:10]
                    else:
                        instances = AccountLedger.objects.filter(
                            BranchID=BranchID, CompanyID=CompanyID, LedgerName__icontains=ledger_name, LedgerID__in=ledger)
                        print(instances)
                elif load_data:
                    instances = AccountLedger.objects.filter(
                        BranchID=BranchID, CompanyID=CompanyID, LedgerID__in=[Cash_Account, Bank_Account])
                else:
                    instances = AccountLedger.objects.filter(
                        BranchID=BranchID, CompanyID=CompanyID, LedgerID__in=ledger)
            else:
                AccountGroupUnder_list = [8, 9]
                if type_invoice == "SalesInvoice":
                    AccountGroupUnder_list = [8, 9, 10]
                    if check_ShowSupplierInSales == True or check_ShowSupplierInSales == "True":
                        AccountGroupUnder_list.append(29)
                        # AccountGroupUnder_list = [8,9,10]
                    if check_ShowEmployeesInSales == True or check_ShowEmployeesInSales == "True":
                        AccountGroupUnder_list.append(32)
                        # AccountGroupUnder_list = [8,9,10]
                elif type_invoice == "PurchaseInvoice":
                    AccountGroupUnder_list = [8, 9, 29]
                    if check_ShowCustomerInPurchase == True or check_ShowCustomerInPurchase == "True":
                        AccountGroupUnder_list.append(10)
                else:
                    AccountGroupUnder_list = [8, 9, 10, 29]

                if ledger_name:
                    if float(length) < 3:
                        instances = AccountLedger.objects.filter(
                            BranchID=BranchID, CompanyID=CompanyID, LedgerName__icontains=ledger_name, AccountGroupUnder__in=AccountGroupUnder_list)[:10]
                    else:
                        instances = AccountLedger.objects.filter(
                            BranchID=BranchID, CompanyID=CompanyID, LedgerName__icontains=ledger_name, AccountGroupUnder__in=AccountGroupUnder_list)
                elif load_data:
                    instances = AccountLedger.objects.filter(
                        BranchID=BranchID, CompanyID=CompanyID, AccountGroupUnder__in=AccountGroupUnder_list)[:10]
                else:
                    instances = AccountLedger.objects.filter(
                        BranchID=BranchID, CompanyID=CompanyID, AccountGroupUnder__in=AccountGroupUnder_list)

            serialized = AccountLedgerListSerializer(instances, many=True, context={"CompanyID": CompanyID,
                                                                                    "PriceRounding": PriceRounding})

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Account Ledger Not Found in this BranchID!"
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
def ledgerListforPayments(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']

    try:
        is_multiple = data['is_multiple']
    except:
        is_multiple = False

    serialized1 = ListSerializerforPayment(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']
        AccountGroupUnder = serialized1.data['AccountGroupUnder']

        if AccountLedger.objects.filter(BranchID=BranchID, AccountGroupUnder=AccountGroupUnder, CompanyID=CompanyID).exists():
            instances = AccountLedger.objects.filter(
                BranchID=BranchID, AccountGroupUnder=AccountGroupUnder, CompanyID=CompanyID)
            serialized = AccountLedgerListSerializer(instances, many=True, context={"CompanyID": CompanyID,
                                                                                    "PriceRounding": PriceRounding})

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Account Ledger Not Found in this BranchID!"
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
def ledgerListforPayments_all(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']

    serialized1 = ListSerializerforPaymentAll(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if AccountLedger.objects.filter(BranchID=BranchID, AccountGroupUnder__in=[8, 9], CompanyID=CompanyID).exists():
            instances = AccountLedger.objects.filter(
                BranchID=BranchID, AccountGroupUnder__in=[8, 9], CompanyID=CompanyID)
            serialized = AccountLedgerListSerializer(instances, many=True, context={"CompanyID": CompanyID,
                                                                                    "PriceRounding": PriceRounding})

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Account Ledger Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def get_balance_ledger(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    LedgerID = data['LedgerID']

    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if AccountLedger.objects.filter(BranchID=BranchID, CompanyID=CompanyID, LedgerID=LedgerID).exists():

            instance = AccountLedger.objects.get(
                BranchID=BranchID, CompanyID=CompanyID, LedgerID=LedgerID)

            serialized = AccountLedgerRestSerializer(instance, context={"CompanyID": CompanyID,
                                                                        "PriceRounding": PriceRounding})

            orderdDict = serialized.data
            jsnDatas = convertOrderdDict(orderdDict)

            final_Array = []
            id = jsnDatas['id']
            BranchID = jsnDatas['BranchID']
            LedgerName = jsnDatas['LedgerName']
            LedgerID = jsnDatas['LedgerID']
            LedgerCode = jsnDatas['LedgerCode']
            AccountGroupUnder = jsnDatas['AccountGroupUnder']
            AccountGroupName = jsnDatas['AccountGroupName']
            OpeningBalance = jsnDatas['OpeningBalance']
            CrOrDr = jsnDatas['CrOrDr']
            Notes = jsnDatas['Notes']
            IsActive = jsnDatas['IsActive']
            IsDefault = jsnDatas['IsDefault']
            CreatedDate = jsnDatas['CreatedDate']
            UpdatedDate = jsnDatas['UpdatedDate']
            CreatedUserID = jsnDatas['CreatedUserID']
            Mobile = jsnDatas['Mobile']
            Action = jsnDatas['Action']

            ledger_instances = LedgerPosting.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID)
            TotalDebit = 0
            TotalCredit = 0

            for i in ledger_instances:
                TotalDebit += i.Debit
                TotalCredit += i.Credit

            Balance = float(TotalDebit) - float(TotalCredit)
            GST_Treatment = ""
            VAT_Treatment = ""
            State_Code = ""
            CustomerState = ""
            CustomerCountry = ""
            GSTNumber = ""
            CustomerStateName = ""
            BillingAddress = ""
            Attention = ""
            Address1 = ""
            City = ""
            PostalCode = ""

            if Parties.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).exists():
                pary_ins = Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).first()

                GST_Treatment = pary_ins.GST_Treatment
                VAT_Treatment = pary_ins.VAT_Treatment
                State_Code = pary_ins.State_Code
                CustomerCountry = pary_ins.Country
                if pary_ins.PlaceOfSupply and not pary_ins.PlaceOfSupply == "null":
                    CustomerState = pary_ins.PlaceOfSupply
                else:
                    CustomerState = pary_ins.State

                if CustomerState:
                    if State.objects.filter(id=CustomerState).exists():
                        CustomerStateName = State.objects.get(
                            id=CustomerState).Name

                GSTNumber = pary_ins.GSTNumber
                Mobile = pary_ins.Mobile
                Attention = pary_ins.Attention
                Address1 = pary_ins.Address1
                City = pary_ins.City
                PostalCode = pary_ins.PostalCode
            BillingAddress = ""
            if Attention or Address1 or City or CustomerStateName or PostalCode:
                BillingAddress = str(Attention) + str(",") + str(Address1) + str(",") + str(
                    City) + str(",") + str(CustomerStateName) + str(',') + str(PostalCode)
            shipping_addresses = get_shippingAddress(
                CompanyID, BranchID, LedgerID)
            final_dict = {
                "id": id,
                "BranchID": BranchID,
                "LedgerName": LedgerName,
                "LedgerID": LedgerID,
                "LedgerCode": LedgerCode,
                "AccountGroupUnder": AccountGroupUnder,
                "AccountGroupName": AccountGroupName,
                "OpeningBalance": OpeningBalance,
                "CrOrDr": CrOrDr,
                "Notes": Notes,
                "IsActive": IsActive,
                "IsDefault": IsDefault,
                "CreatedDate": CreatedDate,
                "UpdatedDate": UpdatedDate,
                "CreatedUserID": CreatedUserID,
                "Action": Action,
                "Balance": Balance,
                "GST_Treatment": GST_Treatment,
                "VAT_Treatment": VAT_Treatment,
                "GSTNumber": GSTNumber,
                "State_Code": State_Code,
                "CustomerCountry": CustomerCountry,
                "CustomerState": CustomerState,
                "Mobile": Mobile,
                "CustomerStateName": CustomerStateName,
                "BillingAddress": BillingAddress,
                "shipping_addresses": shipping_addresses,
            }

            # final_Array.append(final_dict)

            response_data = {
                "StatusCode": 6000,
                "data": final_dict
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Account Ledger Not Found in this BranchID!"
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
def ledgerListByGroupUnder(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    GroupUnder = data['GroupUnder']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if AccountLedger.objects.filter(BranchID=BranchID, CompanyID=CompanyID, AccountGroupUnder=GroupUnder).exists():

            instances = AccountLedger.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID, AccountGroupUnder=GroupUnder)

            serialized = AccountLedgerListSerializer(instances, many=True, context={"CompanyID": CompanyID,
                                                                                    "PriceRounding": PriceRounding})

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Account Ledger Not Found in this BranchID!"
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
def ledgerListforPayments_Receipts(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']

    try:
        ledger_name = data['ledger_name']
    except:
        ledger_name = ""

    try:
        length = data['length']
    except:
        length = ""

    try:
        load_data = data['load_data']
    except:
        load_data = False

    print("=========================1557")
    print(ledger_name)

    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        exclude_groups = [33, 87, 81, 83, 85, 79, 15, 7, 22, 80, 82, 84,
                          78, 79, 30, 86, 94, 89, 31, 39, 45, 55, 58, 62, 73, 74, 77, 48]
        exclude_ledgers = [89, 90, 91]

        if AccountLedger.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():

            instances = AccountLedger.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID).exclude(LedgerID__in=exclude_ledgers)
            instances = instances.exclude(AccountGroupUnder__in=exclude_groups)

            if ledger_name:
                if float(length) < 3:
                    instances = instances.filter(
                        LedgerName__icontains=ledger_name)[:10]
                else:
                    instances = instances.filter(
                        LedgerName__icontains=ledger_name)
            elif load_data:
                instances = instances[:10]
            else:
                instances = instances

            serialized = AccountLedgerRestSerializer(instances, many=True, context={"CompanyID": CompanyID,
                                                                                    "PriceRounding": PriceRounding})

            orderdDict = serialized.data
            jsnDatas = convertOrderdDict(orderdDict)

            final_Array = []
            for i in jsnDatas:
                id = i['id']
                BranchID = i['BranchID']
                LedgerName = i['LedgerName']
                LedgerID = i['LedgerID']
                LedgerCode = i['LedgerCode']
                AccountGroupUnder = i['AccountGroupUnder']
                AccountGroupName = i['AccountGroupName']
                OpeningBalance = i['OpeningBalance']
                CrOrDr = i['CrOrDr']
                Notes = i['Notes']
                IsActive = i['IsActive']
                IsDefault = i['IsDefault']
                CreatedDate = i['CreatedDate']
                UpdatedDate = i['UpdatedDate']
                CreatedUserID = i['CreatedUserID']
                Action = i['Action']

                ledger_instances = LedgerPosting.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID)
                TotalDebit = 0
                TotalCredit = 0

                for i in ledger_instances:
                    TotalDebit += i.Debit
                    TotalCredit += i.Credit

                Balance = float(TotalDebit) - float(TotalCredit)

                final_dict = {
                    "id": id,
                    "BranchID": BranchID,
                    "LedgerName": LedgerName,
                    "LedgerID": LedgerID,
                    "LedgerCode": LedgerCode,
                    "AccountGroupUnder": AccountGroupUnder,
                    "AccountGroupName": AccountGroupName,
                    "OpeningBalance": OpeningBalance,
                    "CrOrDr": CrOrDr,
                    "Notes": Notes,
                    "IsActive": IsActive,
                    "IsDefault": IsDefault,
                    "CreatedDate": CreatedDate,
                    "UpdatedDate": UpdatedDate,
                    "CreatedUserID": CreatedUserID,
                    "Action": Action,
                    "Balance": round(Balance, PriceRounding)
                }

                final_Array.append(final_dict)

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'AccountLedger',
                         'View', 'AccountLedger List Viewd.', "User Viewd AccountLedger List.")

            response_data = {
                "StatusCode": 6000,
                "data": final_Array
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'AccountLedger', 'View',
                         'AccountLedger List Viewd failed.', "Account Ledger Not Found under this Branch")
            response_data = {
                "StatusCode": 6001,
                "message": "Account Ledger Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'AccountLedger',
                     'View', 'AccountLedger List Viewd failed.', "InValid BranchID Given!")
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def search_ledgers(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']

    try:
        ledger_name = data['ledger_name']
    except:
        ledger_name = ""

    try:
        length = data['length']
    except:
        length = ""

    try:
        load_data = data['load_data']
    except:
        load_data = False

    print("=========================1557")
    print(ledger_name)

    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']
        if AccountLedger.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():

            if ledger_name:
                if float(length) < 3:
                    instances = AccountLedger.objects.filter(
                        BranchID=BranchID, LedgerName__icontains=ledger_name, CompanyID=CompanyID)[:10]
                else:
                    instances = AccountLedger.objects.filter(
                        BranchID=BranchID, LedgerName__icontains=ledger_name, CompanyID=CompanyID)
            elif load_data:
                instances = AccountLedger.objects.filter(
                    BranchID=BranchID, CompanyID=CompanyID)[:10]
            else:
                instances = AccountLedger.objects.filter(
                    BranchID=BranchID, CompanyID=CompanyID)

            serialized = AccountLedgerRestSerializer(instances, many=True, context={"CompanyID": CompanyID,
                                                                                    "PriceRounding": PriceRounding})
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'AccountLedger',
                         'View', 'AccountLedger List Viewd.', "User Viewd AccountLedger List.")

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'AccountLedger', 'View',
                         'AccountLedger List Viewd failed.', "Account Ledger Not Found under this Branch")
            response_data = {
                "StatusCode": 6001,
                "message": "Account Ledger Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'AccountLedger',
                     'View', 'AccountLedger List Viewd failed.', "InValid BranchID Given!")
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def ledgerListByGroups(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    GroupUnder = data['GroupUnder']

    try:
        name = data['name']
    except:
        name = ""

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if AccountLedger.objects.filter(BranchID=BranchID, CompanyID=CompanyID, AccountGroupUnder__in=GroupUnder).exists():

            instances = AccountLedger.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID, AccountGroupUnder__in=GroupUnder)
            if name:
                instances = instances.filter(LedgerName__icontains=name)

            serialized = AccountLedgerListSerializer(instances, many=True, context={"CompanyID": CompanyID,
                                                                                    "PriceRounding": PriceRounding})

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Account Ledger Not Found in this BranchID!"
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
def search_accountLedgers(request):
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
        if AccountLedger.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instances = AccountLedger.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
            group_ids = []
            if AccountGroup.objects.filter(CompanyID=CompanyID, AccountGroupName__icontains=product_name).exists():
                group_ins = AccountGroup.objects.filter(
                    CompanyID=CompanyID, AccountGroupName__icontains=product_name)
                for g in group_ins:
                    GroupID = g.AccountGroupID
                    group_ids.append(GroupID)
            if length < 3:
                if param == "name":
                    instances = instances.filter(
                        (Q(LedgerName__icontains=product_name)))[:10]
                elif param == "code":
                    instances = instances.filter(
                        (Q(LedgerCode__icontains=product_name)))[:10]
                else:
                    instances = instances.filter(
                        (Q(AccountGroupUnder__in=group_ids)))[:10]
            else:
                if param == "name":
                    instances = instances.filter(
                        (Q(LedgerName__icontains=product_name)))
                elif param == "code":
                    instances = instances.filter(
                        (Q(LedgerCode__icontains=product_name)))
                else:
                    instances = instances.filter(
                        (Q(AccountGroupUnder__in=group_ids)))
            serialized = AccountLedgerRestSerializer(instances, many=True, context={
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
def search_ledger_list(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    product_name = data['product_name']
    length = data['length']
    
    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if AccountLedger.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            group_ids = []
            if AccountGroup.objects.filter(CompanyID=CompanyID, AccountGroupName__icontains=product_name).exists():
                group_ins = AccountGroup.objects.filter(
                    CompanyID=CompanyID, AccountGroupName__icontains=product_name)
                for g in group_ins:
                    GroupID = g.AccountGroupID
                    group_ids.append(GroupID)
            if length < 3:
                instances = AccountLedger.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                instances = instances.filter((Q(LedgerName__icontains=product_name)) | (
                    Q(LedgerCode__icontains=product_name)))[:10]
                if not instances:
                    instances = AccountLedger.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                    instances = instances.filter(
                        (Q(AccountGroupUnder__in=group_ids)))[:10]
            else:
                instances = AccountLedger.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                instances = instances.filter((Q(LedgerName__icontains=product_name)) | (
                    Q(LedgerCode__icontains=product_name)))
                if not instances:
                    instances = AccountLedger.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                    instances = instances.filter(
                        (Q(AccountGroupUnder__in=group_ids)))
            serialized = AccountLedgerRestSerializer(instances, many=True, context={
                                                             "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding,"product_name": "product_name"})
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": "Ledger not found!"
            }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)