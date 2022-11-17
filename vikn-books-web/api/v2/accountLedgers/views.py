from brands.models import AccountLedger, AccountLedger_Log, LedgerPosting, LedgerPosting_Log, PurchaseOrderMaster,\
SalesOrderMaster, Parties, Employee, AccountGroup, Parties_Log, Bank, Bank_Log, Employee_Log,UserTable, CompanySettings
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v2.accountLedgers.serializers import AccountLedgerSerializer, AccountLedgerRestSerializer, LedgerReportSerializer, AccountLedgerListSerializer
from api.v2.brands.serializers import ListSerializer
from api.v2.accountLedgers.serializers import ListSerializerforPayment
from api.v2.accountLedgers.functions import generate_serializer_errors
from rest_framework import status
from api.v2.banks.functions import get_auto_Bankid
from web.functions import get_auto_EmployeeID
from api.v2.accountLedgers.functions import get_auto_id, get_LedgerCode, get_auto_LedgerPostid, get_auto_idfor_party
from main.functions import get_company, activity_log
import datetime
from api.v2.ledgerPosting.functions import convertOrderdDict



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_accountLedger(request):
    data = request.data
    CompanyID_Uid = data['CompanyID']
    CompanyID = get_company(CompanyID_Uid)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
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
        
        LedgerID = get_auto_id(AccountLedger,BranchID, CompanyID)

        LedgerCode = get_LedgerCode(AccountLedger, BranchID, CompanyID)

        Action = 'A'

        if CrOrDr == "0":
            CrOrDr = "Dr"

        elif CrOrDr == "1":
            CrOrDr = "Cr"


        is_nameExist = False

        LedgerNameLow = LedgerName.lower()

        account_ledgers = AccountLedger.objects.filter(BranchID=BranchID,CompanyID=CompanyID)

        for account_ledger in account_ledgers:

            ledger_name = account_ledger.LedgerName
            ledgerName = ledger_name.lower()

            if LedgerNameLow == ledgerName:
                is_nameExist = True

        if not is_nameExist:

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
                )

            if float(OpeningBalance) > 0:
                Credit = 0.00
                Debit = 0.00

                if CrOrDr == "Cr":
                    Credit = OpeningBalance

                elif CrOrDr == "Dr":
                    Debit = OpeningBalance

                VoucherType = "LOB"

                LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID, CompanyID)

                LedgerPosting.objects.create(
                    LedgerPostingID=LedgerPostingID,
                    BranchID=BranchID,
                    Date=today,
                    VoucherMasterID=LedgerID,
                    VoucherType=VoucherType,
                    VoucherNo=LedgerCode,
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
                    Date=today,
                    VoucherMasterID=LedgerID,
                    VoucherNo=LedgerCode,
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

            #saving data to party table for account group under 10 and 29
            if AccountGroupUnder == 10 or AccountGroupUnder == 29:
                FirstName = LedgerName
                if AccountGroupUnder == 10:
                    PartyType = "customer"


                elif AccountGroupUnder == 29:
                    PartyType = "supplier"

                PartyID = get_auto_idfor_party(Parties,BranchID, CompanyID)
                PartyCode = LedgerCode

                Country = ''
                State = ''
                if CompanySettings.objects.filter(id=CompanyID_Uid).exists():
                    Country = CompanySettings.objects.get(id=CompanyID_Uid).Country.id
                    State = CompanySettings.objects.get(id=CompanyID_Uid).State.id

                Parties.objects.create(
                    PartyID=PartyID,
                    BranchID=BranchID,
                    PartyType=PartyType,
                    LedgerID=LedgerID,
                    PartyCode=PartyCode,
                    FirstName=FirstName,
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
                    Country_Shipping=Country
                    )

                Parties_Log.objects.create(
                    TransactionID=PartyID,
                    BranchID=BranchID,
                    PartyType=PartyType,
                    LedgerID=LedgerID,
                    PartyCode=PartyCode,
                    FirstName=FirstName,
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
                    Country_Shipping=Country
                    )

            elif AccountGroupUnder == 8:
        
                BankID = get_auto_Bankid(Bank,BranchID, CompanyID)

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
            
                EmployeeID = get_auto_EmployeeID(Employee,BranchID, CompanyID)

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
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'AccountLedger', 'Create', 'AccountLedger created successfully.', 'AccountLedger saved successfully.')

            data = {"LedgerID" : LedgerID}
            data.update(serialized.data)
            response_data = {
                "StatusCode" : 6000,
                "data" : data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'AccountLedger', 'Create', 'AccountLedger created failed.', 'AccountLedger Already Exist!')
            response_data = {
            "StatusCode" : 6001,
            "message" : "Ledger Name Already Exist!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'error', CreatedUserID, 'AccountLedger', 'Create', 'AccountLedger created failed.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode" : 6001,
            "message" : generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_accountLedger(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = AccountLedgerSerializer(data=request.data)
    instance = AccountLedger.objects.get(pk=pk,CompanyID=CompanyID)

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

        Action = 'M'

        if CrOrDr == "0":
            CrOrDr = "Dr"

        elif CrOrDr == "1":
            CrOrDr = "Cr"


        is_nameExist = False
        accountLedger_ok = False

        LedgerNameLow = LedgerName.lower()

        account_ledgers = AccountLedger.objects.filter(BranchID=BranchID,CompanyID=CompanyID)

        for account_ledger in account_ledgers:

            ledger_name = account_ledger.LedgerName
            ledgerName = ledger_name.lower()

            if LedgerNameLow == ledgerName:
                is_nameExist = True

            if instanceLedgerName.lower() == LedgerNameLow:

                accountLedger_ok = True


        if  accountLedger_ok:

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
                )


            if float(OpeningBalance) > 0:
                Credit = 0.00
                Debit = 0.00
                if CrOrDr == "Cr":
                    Credit = OpeningBalance

                elif CrOrDr == "Dr":
                    Debit = OpeningBalance

                VoucherType = "LOB"

                if LedgerPosting.objects.filter(LedgerID=LedgerID,BranchID=BranchID,VoucherMasterID=LedgerID,VoucherType="LOB",CompanyID=CompanyID).exists():
                    ledgerPostInstance = LedgerPosting.objects.get(LedgerID=LedgerID,BranchID=BranchID,VoucherMasterID=LedgerID,VoucherType="LOB",CompanyID=CompanyID)
                    # ledgerPostInstance.Date = today
                    ledgerPostInstance.Debit = Debit
                    ledgerPostInstance.Credit = Credit
                    ledgerPostInstance.Action = "M"
                    ledgerPostInstance.UpdatedDate = today
                    ledgerPostInstance.CreatedUserID = CreatedUserID
                    ledgerPostInstance.save()

                    LedgerPosting_Log.objects.create(
                        TransactionID=ledgerPostInstance.LedgerPostingID,
                        BranchID=BranchID,
                        Date=today,
                        VoucherMasterID=LedgerID,
                        VoucherType=VoucherType,
                        VoucherNo=LedgerCode,
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
                else:
                    LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
                        BranchID=BranchID,
                        Date=today,
                        VoucherMasterID=LedgerID,
                        VoucherType=VoucherType,
                        VoucherNo=LedgerCode,
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
                        Date=today,
                        VoucherMasterID=LedgerID,
                        VoucherNo=LedgerCode,
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
            else:
                Credit = 0.00
                Debit = 0.00
                if CrOrDr == "Cr":
                    Credit = OpeningBalance

                elif CrOrDr == "Dr":
                    Debit = OpeningBalance
                if LedgerPosting.objects.filter(LedgerID=LedgerID,BranchID=BranchID,VoucherMasterID=LedgerID,VoucherType="LOB",CompanyID=CompanyID).exists():
                    ledgerPostInstance = LedgerPosting.objects.get(LedgerID=LedgerID,BranchID=BranchID,VoucherMasterID=LedgerID,VoucherType="LOB",CompanyID=CompanyID)
                    ledgerPostInstance.Date = today
                    ledgerPostInstance.Debit = Debit
                    ledgerPostInstance.Credit = Credit
                    ledgerPostInstance.Action = "D"
                    ledgerPostInstance.UpdatedDate = today
                    ledgerPost_CreatedDate = ledgerPostInstance.CreatedDate
                    ledgerPostInstance.delete()

            if AccountGroupUnder == 10 or AccountGroupUnder == 29:

                FirstName = LedgerName
                if AccountGroupUnder == 10:
                    PartyType = "customer"


                elif AccountGroupUnder == 29:
                    PartyType = "supplier"

                PartyCode = LedgerCode

                if Parties.objects.filter(BranchID=BranchID,LedgerID=LedgerID,PartyType=PartyType,CompanyID=CompanyID).exists():
                    partyInstance = Parties.objects.get(BranchID=BranchID,LedgerID=LedgerID,PartyType=PartyType,CompanyID=CompanyID)
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
            
                if Bank.objects.filter(BranchID=BranchID,LedgerCode=LedgerCode,CompanyID=CompanyID).exists():
                    bankInstance = Bank.objects.get(BranchID=BranchID,LedgerCode=LedgerCode,CompanyID=CompanyID)
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
            
                if Employee.objects.filter(BranchID=BranchID,LedgerID=LedgerID,EmployeeCode=LedgerCode,CompanyID=CompanyID).exists():
                    employeeInstance = Employee.objects.get(BranchID=BranchID,LedgerID=LedgerID,EmployeeCode=LedgerCode,CompanyID=CompanyID)
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
            activity_log(request._request, CompanyID, 'error', CreatedUserID, 'AccountLedger', 'Edit', 'AccountLedger Updated Successfully.', 'AccountLedger Updated Successfully.')
            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:


            if is_nameExist:

                response_data = {
                    "StatusCode" : 6001,
                    "message" : "Ledger Name Already exist with this Branch ID"
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
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
                    )

                if float(OpeningBalance) > 0:
                    Credit = 0.00
                    Debit = 0.00

                    if CrOrDr == "Cr":
                        Credit = OpeningBalance

                    elif CrOrDr == "Dr":
                        Debit = OpeningBalance

                    VoucherType = "LOB"

                    if LedgerPosting.objects.filter(LedgerID=LedgerID,BranchID=BranchID,VoucherMasterID=LedgerID,VoucherType="LOB",CompanyID=CompanyID).exists():
                        ledgerPostInstance = LedgerPosting.objects.get(LedgerID=LedgerID,BranchID=BranchID,VoucherMasterID=LedgerID,VoucherType="LOB",CompanyID=CompanyID)
                        ledgerPostInstance.Date = today
                        ledgerPostInstance.Debit = Debit
                        ledgerPostInstance.Credit = Credit
                        ledgerPostInstance.Action = "M"
                        ledgerPostInstance.UpdatedDate = today
                        ledgerPostInstance.CreatedUserID = CreatedUserID
                        ledgerPostInstance.save()

                        LedgerPosting_Log.objects.create(
                            TransactionID=ledgerPostInstance.LedgerPostingID,
                            BranchID=BranchID,
                            Date=today,
                            VoucherMasterID=LedgerID,
                            VoucherType=VoucherType,
                            VoucherNo=LedgerCode,
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
                    else:
                        LedgerPostingID = get_auto_LedgerPostid(LedgerPosting,BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
                            BranchID=BranchID,
                            Date=today,
                            VoucherMasterID=LedgerID,
                            VoucherType=VoucherType,
                            VoucherNo=LedgerCode,
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
                            Date=today,
                            VoucherMasterID=LedgerID,
                            VoucherNo=LedgerCode,
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
                else:
                    Credit = 0.00
                    Debit = 0.00
                    if CrOrDr == "Cr":
                        Credit = OpeningBalance

                    elif CrOrDr == "Dr":
                        Debit = OpeningBalance
                    if LedgerPosting.objects.filter(LedgerID=LedgerID,BranchID=BranchID,VoucherMasterID=LedgerID,VoucherType="LOB",CompanyID=CompanyID).exists():
                        ledgerPostInstance = LedgerPosting.objects.get(LedgerID=LedgerID,BranchID=BranchID,VoucherMasterID=LedgerID,VoucherType="LOB",CompanyID=CompanyID)
                        ledgerPostInstance.Date = today
                        ledgerPostInstance.Debit = Debit
                        ledgerPostInstance.Credit = Credit
                        ledgerPostInstance.Action = "D"
                        ledgerPostInstance.UpdatedDate = today
                        ledgerPostInstance.CreatedUserID = CreatedUserID
                        ledgerPost_CreatedDate = ledgerPostInstance.CreatedDate
                        ledgerPostInstance.delete()

                if AccountGroupUnder == 10 or AccountGroupUnder == 29:

                    FirstName = LedgerName
                    if AccountGroupUnder == 10:
                        PartyType = "customer"


                    elif AccountGroupUnder == 29:
                        PartyType = "supplier"

                    PartyCode = LedgerCode

                    if Parties.objects.filter(BranchID=BranchID,LedgerID=LedgerID,PartyType=PartyType,CompanyID=CompanyID).exists():
                        partyInstance = Parties.objects.get(BranchID=BranchID,LedgerID=LedgerID,PartyType=PartyType,CompanyID=CompanyID)
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
                
                    if Bank.objects.filter(BranchID=BranchID,LedgerCode=LedgerCode,CompanyID=CompanyID).exists():
                        bankInstance = Bank.objects.get(BranchID=BranchID,LedgerCode=LedgerCode,CompanyID=CompanyID)
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
                
                    if Employee.objects.filter(BranchID=BranchID,LedgerID=LedgerID,EmployeeCode=LedgerCode,CompanyID=CompanyID).exists():
                        employeeInstance = Employee.objects.filter(BranchID=BranchID,LedgerID=LedgerID,EmployeeCode=LedgerCode,CompanyID=CompanyID)
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
                activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'AccountLedger', 'Edit', 'AccountLedger Updated Successfully.', 'AccountLedger Updated Successfully.')
                response_data = {
                    "StatusCode" : 6000,
                    "data" : serialized.data
                }

                return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'AccountLedger', 'Edit', 'AccountLedger Updated Failed.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode" : 6001,
            "message" : generate_serializer_errors(serialized._errors)
        }

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
 
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if AccountLedger.objects.filter(BranchID=BranchID,CompanyID=CompanyID).exists():

            instances = AccountLedger.objects.filter(BranchID=BranchID,CompanyID=CompanyID)

            serialized = AccountLedgerRestSerializer(instances,many=True,context = {"CompanyID": CompanyID,
            "PriceRounding" : PriceRounding })

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

                ledger_instances = LedgerPosting.objects.filter(CompanyID=CompanyID,BranchID=BranchID,LedgerID=LedgerID)
                TotalDebit = 0
                TotalCredit = 0

                for i in ledger_instances:
                    TotalDebit += i.Debit
                    TotalCredit += i.Credit

                Balance = float(TotalDebit) - float(TotalCredit)

                final_dict = {
                    "id" : id,
                    "BranchID" : BranchID,
                    "LedgerName" : LedgerName,
                    "LedgerID" : LedgerID,
                    "LedgerCode" : LedgerCode,
                    "AccountGroupUnder" : AccountGroupUnder,
                    "AccountGroupName" : AccountGroupName,
                    "OpeningBalance" : OpeningBalance,
                    "CrOrDr" : CrOrDr,
                    "Notes" : Notes,
                    "IsActive" : IsActive,
                    "IsDefault" : IsDefault,
                    "CreatedDate" : CreatedDate,
                    "UpdatedDate" : UpdatedDate,
                    "CreatedUserID" : CreatedUserID,
                    "Action" : Action,
                    "Balance" : round(Balance,PriceRounding)
                }

                final_Array.append(final_dict)

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'AccountLedger', 'View', 'AccountLedger List Viewd.', "User Viewd AccountLedger List.")

            response_data = {
                "StatusCode" : 6000,
                "data" : final_Array
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'AccountLedger', 'View', 'AccountLedger List Viewd failed.', "Account Ledger Not Found under this Branch")
            response_data = {
            "StatusCode" : 6001,
            "message" : "Account Ledger Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'AccountLedger', 'View', 'AccountLedger List Viewd failed.', "InValid BranchID Given!")
        response_data = {
            "StatusCode" : 6001,
            "message" : "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def accountLedger(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']

    instance = None

    if AccountLedger.objects.filter(pk=pk,CompanyID=CompanyID).exists():
        instance = AccountLedger.objects.get(pk=pk,CompanyID=CompanyID)
        serialized = AccountLedgerRestSerializer(instance, context = {"CompanyID": CompanyID,
        "PriceRounding" : PriceRounding })
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'AccountLedger', 'View', 'AccountLedger Single Viewd.', "User AccountLedger Single Page Viewd.")
        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'AccountLedger', 'View', 'AccountLedger Single View failed.', "AccountLedger Not Found.")
        response_data = {
            "StatusCode" : 6001,
            "message" : "Account Ledger Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_accountLedger(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']


    today = datetime.datetime.now()
    instance = None
    ledgerPostInstance = None
    LPInstances = None
    purchaseOrderMaster_exist = None
    salesOrderMaster_exist = None
    parties_exist = None
    employees_exist = None
    if AccountLedger.objects.filter(pk=pk).exists():
        instance = AccountLedger.objects.get(pk=pk)
    if instance:
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
        
        LPInstances = LedgerPosting.objects.filter(BranchID=BranchID,LedgerID=LedgerID,CompanyID=CompanyID).exclude(VoucherType="LOB")
            
        purchaseOrderMaster_exist = PurchaseOrderMaster.objects.filter(BranchID=BranchID,LedgerID=LedgerID,CompanyID=CompanyID).exists()
        salesOrderMaster_exist = SalesOrderMaster.objects.filter(BranchID=BranchID,LedgerID=LedgerID,CompanyID=CompanyID).exists()
        parties_exist = Parties.objects.filter(BranchID=BranchID,LedgerID=LedgerID,CompanyID=CompanyID).exists()
        employees_exist = Employee.objects.filter(BranchID=BranchID,LedgerID=LedgerID,CompanyID=CompanyID).exists()


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

            if LedgerPosting.objects.filter(LedgerID=LedgerID,BranchID=BranchID,VoucherType="LOB",CompanyID=CompanyID).exists():
                ledgerPostInstances = LedgerPosting.objects.filter(LedgerID=LedgerID,BranchID=BranchID,VoucherType="LOB",CompanyID=CompanyID)
                
                for ledgerPostInstance in ledgerPostInstances:
                    LedgerPostingID = ledgerPostInstance.LedgerPostingID
                    VoucherType = ledgerPostInstance.VoucherType
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
                        Debit=Debit,
                        Credit=Credit,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                        )
            party_group = [10,29]
            if AccountGroupUnder == 8:
                if Bank.objects.filter(BranchID=BranchID,LedgerCode=LedgerCode,CompanyID=CompanyID).exists():
                    bankInstance = Bank.objects.get(BranchID=BranchID,LedgerCode=LedgerCode,CompanyID=CompanyID)
                    bankInstance.delete()

            if AccountGroupUnder in party_group:
                if Parties.objects.filter(BranchID=BranchID,LedgerID=LedgerID,CompanyID=CompanyID).exists():
                    partyInstances = Parties.objects.filter(BranchID=BranchID,LedgerID=LedgerID,CompanyID=CompanyID)
                    for i in partyInstances:
                        i.delete()

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'AccountLedger', 'Delete', 'AccountLedger Deleted Successfully.', "AccountLedger Deleted Successfully.")

            response_data = {
                "StatusCode" : 6000,
                "title" : "Success",
                "message" : "Account Ledger Deleted Successfully!"
            }

        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'AccountLedger', 'Delete', 'AccountLedger Deleted Failed.', "Cant Delete this AccountLedger,this LedgerID is using somewhere")
            response_data = {
                "StatusCode" : 6001,
                "title" : "Failed",
                "message" : "You Cant Delete this AccountLedger,this LedgerID is using somewhere!!"
            }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'AccountLedger', 'Delete', 'AccountLedger Deleted Failed.', "Account Ledger Not Found!")
        response_data = {
            "StatusCode" : 6001,
            "title" : "Failed",
            "message" : "Account Ledger Not Found!"
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

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if AccountLedger.objects.filter(BranchID=BranchID,CompanyID=CompanyID).exists():
            if UserTable.objects.filter(CompanyID=CompanyID,customer__user__pk=CreatedUserID,DefaultAccountForUser=True).exists():
                Cash_Account = UserTable.objects.get(CompanyID=CompanyID,customer__user__pk=CreatedUserID).Cash_Account
                Bank_Account = UserTable.objects.get(CompanyID=CompanyID,customer__user__pk=CreatedUserID).Bank_Account
                account_groupunder_instances = AccountLedger.objects.filter(BranchID=BranchID,CompanyID=CompanyID,AccountGroupUnder__in=[10,29])
                ledger = [Cash_Account,Bank_Account]
                for account_groupunder in account_groupunder_instances:
                    LedgerID = account_groupunder.LedgerID
                    ledger.append(LedgerID)
                instances = AccountLedger.objects.filter(BranchID=BranchID,CompanyID=CompanyID,LedgerID__in=ledger)
            else:
                instances = AccountLedger.objects.filter(BranchID=BranchID,CompanyID=CompanyID,AccountGroupUnder__in=[8,9,10,29])

            serialized = AccountLedgerListSerializer(instances,many=True, context = {"CompanyID": CompanyID,
            "PriceRounding" : PriceRounding })
            
            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
            "StatusCode" : 6001,
            "message" : "Account Ledger Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {                                                                                                                                                           
            "StatusCode" : 6001,
            "message" : "Branch ID You Enterd is not Valid!!!"
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

    serialized1 = ListSerializerforPayment(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']
        AccountGroupUnder = serialized1.data['AccountGroupUnder']

        if AccountLedger.objects.filter(BranchID=BranchID,AccountGroupUnder=AccountGroupUnder,CompanyID=CompanyID).exists():
            instances = AccountLedger.objects.filter(BranchID=BranchID,AccountGroupUnder=AccountGroupUnder,CompanyID=CompanyID)
            serialized = AccountLedgerListSerializer(instances,many=True, context = {"CompanyID": CompanyID,
            "PriceRounding" : PriceRounding })

            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
            "StatusCode" : 6001,
            "message" : "Account Ledger Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Branch ID You Enterd is not Valid!!!"
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

        if AccountLedger.objects.filter(BranchID=BranchID,CompanyID=CompanyID,LedgerID=LedgerID).exists():

            instance = AccountLedger.objects.get(BranchID=BranchID,CompanyID=CompanyID,LedgerID=LedgerID)

            serialized = AccountLedgerRestSerializer(instance,context = {"CompanyID": CompanyID,
            "PriceRounding" : PriceRounding })

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
            Action = jsnDatas['Action']

            ledger_instances = LedgerPosting.objects.filter(CompanyID=CompanyID,BranchID=BranchID,LedgerID=LedgerID)
            TotalDebit = 0
            TotalCredit = 0

            for i in ledger_instances:
                TotalDebit += float(i.Debit)
                TotalCredit += float(i.Credit)

            Balance = float(TotalDebit) - float(TotalCredit)

            final_dict = {
                "id" : id,
                "BranchID" : BranchID,
                "LedgerName" : LedgerName,
                "LedgerID" : LedgerID,
                "LedgerCode" : LedgerCode,
                "AccountGroupUnder" : AccountGroupUnder,
                "AccountGroupName" : AccountGroupName,
                "OpeningBalance" : OpeningBalance,
                "CrOrDr" : CrOrDr,
                "Notes" : Notes,
                "IsActive" : IsActive,
                "IsDefault" : IsDefault,
                "CreatedDate" : CreatedDate,
                "UpdatedDate" : UpdatedDate,
                "CreatedUserID" : CreatedUserID,
                "Action" : Action,
                "Balance" : Balance,
            }

            # final_Array.append(final_dict)

            response_data = {
                "StatusCode" : 6000,
                "data" : final_dict
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
            "StatusCode" : 6001,
            "message" : "Account Ledger Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Branch ID You Enterd is not Valid!!!"
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

        if AccountLedger.objects.filter(BranchID=BranchID,CompanyID=CompanyID,AccountGroupUnder=GroupUnder).exists():

            instances = AccountLedger.objects.filter(BranchID=BranchID,CompanyID=CompanyID,AccountGroupUnder=GroupUnder)

            serialized = AccountLedgerListSerializer(instances,many=True, context = {"CompanyID": CompanyID,
            "PriceRounding" : PriceRounding })
            
            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
            "StatusCode" : 6001,
            "message" : "Account Ledger Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {                                                                                                                                                           
            "StatusCode" : 6001,
            "message" : "Branch ID You Enterd is not Valid!!!"
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
 
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        exclude_groups = [33,87,81,83,85,79,15,7,22,80,82,84,78,79,30,86,94,89,31,39,45,55,58,62,73,74,77,48]
        exclude_ledgers = [89,90,91]

        if AccountLedger.objects.filter(BranchID=BranchID,CompanyID=CompanyID).exists():

            instances = AccountLedger.objects.filter(BranchID=BranchID,CompanyID=CompanyID).exclude(LedgerID__in=exclude_ledgers)
            instances = instances.exclude(AccountGroupUnder__in=exclude_groups)
            
            serialized = AccountLedgerRestSerializer(instances,many=True,context = {"CompanyID": CompanyID,
            "PriceRounding" : PriceRounding })

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

                ledger_instances = LedgerPosting.objects.filter(CompanyID=CompanyID,BranchID=BranchID,LedgerID=LedgerID)
                TotalDebit = 0
                TotalCredit = 0

                for i in ledger_instances:
                    TotalDebit += i.Debit
                    TotalCredit += i.Credit

                Balance = float(TotalDebit) - float(TotalCredit)

                final_dict = {
                    "id" : id,
                    "BranchID" : BranchID,
                    "LedgerName" : LedgerName,
                    "LedgerID" : LedgerID,
                    "LedgerCode" : LedgerCode,
                    "AccountGroupUnder" : AccountGroupUnder,
                    "AccountGroupName" : AccountGroupName,
                    "OpeningBalance" : OpeningBalance,
                    "CrOrDr" : CrOrDr,
                    "Notes" : Notes,
                    "IsActive" : IsActive,
                    "IsDefault" : IsDefault,
                    "CreatedDate" : CreatedDate,
                    "UpdatedDate" : UpdatedDate,
                    "CreatedUserID" : CreatedUserID,
                    "Action" : Action,
                    "Balance" : round(Balance,PriceRounding)
                }

                final_Array.append(final_dict)

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'AccountLedger', 'View', 'AccountLedger List Viewd.', "User Viewd AccountLedger List.")

            response_data = {
                "StatusCode" : 6000,
                "data" : final_Array
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'AccountLedger', 'View', 'AccountLedger List Viewd failed.', "Account Ledger Not Found under this Branch")
            response_data = {
            "StatusCode" : 6001,
            "message" : "Account Ledger Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'AccountLedger', 'View', 'AccountLedger List Viewd failed.', "InValid BranchID Given!")
        response_data = {
            "StatusCode" : 6001,
            "message" : "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)