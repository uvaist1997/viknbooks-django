from brands.models import Parties, Parties_Log, AccountLedger, AccountLedger_Log, LedgerPosting, LedgerPosting_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v4.parties.serializers import PartiesSerializer, PartiesRestSerializer, PartyListSerializer
# from api.v4.accountLedgers.serializers import AccountLedgerSerializer
# from api.v4.brands.serializers import ListSerializer
from api.v4.parties.functions import generate_serializer_errors
from rest_framework import status
from api.v4.parties.functions import get_auto_id, get_auto_idLedger, get_PartyCode
from api.v4.accountLedgers.functions import get_auto_LedgerPostid
from main.functions import get_company, activity_log
from api.v4.general.functions import isValidMasterCardNo
from api.v4.parties.tasks import import_party_task
from api.v4.parties.utils import in_memory_file_to_temp
from django.conf import settings
import datetime
import os
from api.v4.brands.serializers import ListSerializer
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
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_party(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    party_serialized = PartiesSerializer(data=request.data)
    PartyImage = data['PartyImage']
    # if PartyImage == "":
    #     PartyImage = instance.PartyImage

    if party_serialized.is_valid():

        GSTNumber = party_serialized.data['GSTNumber']
        try:
            CountryName = data['CountryName']
        except:
            CountryName = ""

        is_Gstn_validate = True
        if GSTNumber:
            if CountryName == "India":
                is_Gstn_validate = False
                print("KAYAR?YYYYYYYYYYYYYYYYYYYYYYYYYYYYY")
                is_Gstn_validate = isValidMasterCardNo(GSTNumber)
        print(is_Gstn_validate,GSTNumber)
        if is_Gstn_validate:
            BranchID = party_serialized.data['BranchID']
            PartyType = party_serialized.data['PartyType']
            # PartyCode = party_serialized.data['PartyCode']
            PartyName = party_serialized.data['PartyName']
            DisplayName = party_serialized.data['DisplayName']
            FirstName = party_serialized.data['FirstName']
            LastName = party_serialized.data['LastName']
            Attention = party_serialized.data['Attention']
            Address1 = party_serialized.data['Address1']
            Address2 = party_serialized.data['Address2']
            City = party_serialized.data['City']
            State = party_serialized.data['State']
            Country = party_serialized.data['Country']
            PostalCode = party_serialized.data['PostalCode']
            OfficePhone = party_serialized.data['OfficePhone']
            WorkPhone = party_serialized.data['WorkPhone']
            Mobile = party_serialized.data['Mobile']
            WebURL = party_serialized.data['WebURL']
            Email = party_serialized.data['Email']
            IsBillwiseApplicable = party_serialized.data['IsBillwiseApplicable']
            CreditPeriod = party_serialized.data['CreditPeriod']
            CreditLimit = party_serialized.data['CreditLimit']
            PriceCategoryID = party_serialized.data['PriceCategoryID']
            CurrencyID = party_serialized.data['CurrencyID']
            InterestOrNot = party_serialized.data['InterestOrNot']
            RouteID = party_serialized.data['RouteID']
            VATNumber = party_serialized.data['VATNumber']
            Tax1Number = party_serialized.data['Tax1Number']
            Tax2Number = party_serialized.data['Tax2Number']
            Tax3Number = party_serialized.data['Tax3Number']
            PanNumber = party_serialized.data['PanNumber']
            CRNo = party_serialized.data['CRNo']
            BankName1 = party_serialized.data['BankName1']
            AccountName1 = party_serialized.data['AccountName1']
            AccountNo1 = party_serialized.data['AccountNo1']
            IBANOrIFSCCode1 = party_serialized.data['IBANOrIFSCCode1']
            BankName2 = party_serialized.data['BankName2']
            AccountName2 = party_serialized.data['AccountName2']
            AccountNo2 = party_serialized.data['AccountNo2']
            IBANOrIFSCCode2 = party_serialized.data['IBANOrIFSCCode2']
            IsActive = party_serialized.data['IsActive']
            OpeningBalance = party_serialized.data['OpeningBalance']
            Attention_Shipping = party_serialized.data['Attention_Shipping']
            Address1_Shipping = party_serialized.data['Address1_Shipping']
            Address2_Shipping = party_serialized.data['Address2_Shipping']
            State_Shipping = party_serialized.data['State_Shipping']
            Country_Shipping = party_serialized.data['Country_Shipping']
            City_Shipping = party_serialized.data['City_Shipping']
            PostalCode_Shipping = party_serialized.data['PostalCode_Shipping']
            Phone_Shipping = party_serialized.data['Phone_Shipping']

            try:
                GST_Treatment = party_serialized.data['GST_Treatment']
            except:
                GST_Treatment = ""

            try:
                State_Code = party_serialized.data['State_Code']
            except:
                State_Code = ""

            Action = 'A'

            if OpeningBalance == None or OpeningBalance == "":
                OpeningBalance = 0

            LedgerID = get_auto_idLedger(AccountLedger, BranchID, CompanyID)

            CrOrDr = data["CrOrDr"]

            LedgerName = PartyName

            if PartyType == "1":
                PartyType = "customer"
                AccountGroupUnder = 10

            elif PartyType == "2":
                PartyType = "supplier"
                AccountGroupUnder = 29

            PartyCode = get_PartyCode(Parties, BranchID, CompanyID, PartyType)

            if CrOrDr == "0":
                CrOrDr = "Dr"

            elif CrOrDr == "1":
                CrOrDr = "Cr"

            is_nameExist = False

            PartyNameLow = PartyName.lower()

            parties = Parties.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
            for party in parties:
                party_name = party.PartyName

                party_FirstName = party_name.lower()

                if PartyNameLow == party_FirstName:
                    is_nameExist = True

            if not is_nameExist:

                is_LedgernameExist = False

                LedgerNameLow = LedgerName.lower()

                accountLedgers = AccountLedger.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)

                for accountLedger in accountLedgers:
                    ledger_name = accountLedger.LedgerName

                    ledgerName = ledger_name.lower()

                    if LedgerNameLow == ledgerName:
                        is_LedgernameExist = True

                if not is_LedgernameExist:
                    AccountLedger.objects.create(
                        LedgerID=LedgerID,
                        BranchID=BranchID,
                        LedgerName=LedgerName,
                        LedgerCode=PartyCode,
                        AccountGroupUnder=AccountGroupUnder,
                        OpeningBalance=OpeningBalance,
                        CrOrDr=CrOrDr,
                        IsActive=IsActive,
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
                        LedgerCode=PartyCode,
                        AccountGroupUnder=AccountGroupUnder,
                        OpeningBalance=OpeningBalance,
                        CrOrDr=CrOrDr,
                        IsActive=IsActive,
                        CreatedDate=today,
                        UpdatedDate=today,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                    )

                    if float(OpeningBalance) > 0:
                        Credit = 0
                        Debit = 0

                        if CrOrDr == "Cr":
                            Credit = OpeningBalance

                        elif CrOrDr == "Dr":
                            Debit = OpeningBalance

                        VoucherType = "LOB"

                        LedgerPostingID = get_auto_LedgerPostid(
                            LedgerPosting, BranchID, CompanyID)

                        LedgerPosting.objects.create(
                            LedgerPostingID=LedgerPostingID,
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

                else:
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Party Name Already Exist!!!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)

                PartyID = get_auto_id(Parties, BranchID, CompanyID)
                Parties.objects.create(
                    PartyID=PartyID,
                    BranchID=BranchID,
                    PartyType=PartyType,
                    LedgerID=LedgerID,
                    PartyCode=PartyCode,
                    PartyName=PartyName,
                    DisplayName=DisplayName,
                    FirstName=FirstName,
                    LastName=LastName,
                    Attention=Attention,
                    Address1=Address1,
                    Address2=Address2,
                    City=City,
                    State=State,
                    Country=Country,
                    PostalCode=PostalCode,
                    OfficePhone=OfficePhone,
                    WorkPhone=WorkPhone,
                    Mobile=Mobile,
                    WebURL=WebURL,
                    Email=Email,
                    IsBillwiseApplicable=IsBillwiseApplicable,
                    CreditPeriod=CreditPeriod,
                    CreditLimit=CreditLimit,
                    PriceCategoryID=PriceCategoryID,
                    CurrencyID=CurrencyID,
                    InterestOrNot=InterestOrNot,
                    RouteID=RouteID,
                    VATNumber=VATNumber,
                    GSTNumber=GSTNumber,
                    Tax1Number=Tax1Number,
                    Tax2Number=Tax2Number,
                    Tax3Number=Tax3Number,
                    PanNumber=PanNumber,
                    CRNo=CRNo,
                    BankName1=BankName1,
                    AccountName1=AccountName1,
                    AccountNo1=AccountNo1,
                    IBANOrIFSCCode1=IBANOrIFSCCode1,
                    BankName2=BankName2,
                    AccountName2=AccountName2,
                    AccountNo2=AccountNo2,
                    IBANOrIFSCCode2=IBANOrIFSCCode2,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    OpeningBalance=OpeningBalance,
                    PartyImage=PartyImage,
                    CompanyID=CompanyID,
                    Attention_Shipping=Attention_Shipping,
                    Address1_Shipping=Address1_Shipping,
                    Address2_Shipping=Address2_Shipping,
                    State_Shipping=State_Shipping,
                    Country_Shipping=Country_Shipping,
                    City_Shipping=City_Shipping,
                    PostalCode_Shipping=PostalCode_Shipping,
                    Phone_Shipping=Phone_Shipping,
                    GST_Treatment=GST_Treatment,
                    State_Code=State_Code
                )

                Parties_Log.objects.create(
                    TransactionID=PartyID,
                    BranchID=BranchID,
                    PartyType=PartyType,
                    LedgerID=LedgerID,
                    PartyCode=PartyCode,
                    PartyName=PartyName,
                    DisplayName=DisplayName,
                    FirstName=FirstName,
                    LastName=LastName,
                    Attention=Attention,
                    Address1=Address1,
                    Address2=Address2,
                    City=City,
                    State=State,
                    Country=Country,
                    PostalCode=PostalCode,
                    OfficePhone=OfficePhone,
                    WorkPhone=WorkPhone,
                    Mobile=Mobile,
                    WebURL=WebURL,
                    Email=Email,
                    IsBillwiseApplicable=IsBillwiseApplicable,
                    CreditPeriod=CreditPeriod,
                    CreditLimit=CreditLimit,
                    PriceCategoryID=PriceCategoryID,
                    CurrencyID=CurrencyID,
                    InterestOrNot=InterestOrNot,
                    RouteID=RouteID,
                    VATNumber=VATNumber,
                    GSTNumber=GSTNumber,
                    Tax1Number=Tax1Number,
                    Tax2Number=Tax2Number,
                    Tax3Number=Tax3Number,
                    PanNumber=PanNumber,
                    CRNo=CRNo,
                    BankName1=BankName1,
                    AccountName1=AccountName1,
                    AccountNo1=AccountNo1,
                    IBANOrIFSCCode1=IBANOrIFSCCode1,
                    BankName2=BankName2,
                    AccountName2=AccountName2,
                    AccountNo2=AccountNo2,
                    IBANOrIFSCCode2=IBANOrIFSCCode2,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    OpeningBalance=OpeningBalance,
                    PartyImage=PartyImage,
                    CompanyID=CompanyID,
                    Attention_Shipping=Attention_Shipping,
                    Address1_Shipping=Address1_Shipping,
                    Address2_Shipping=Address2_Shipping,
                    State_Shipping=State_Shipping,
                    Country_Shipping=Country_Shipping,
                    City_Shipping=City_Shipping,
                    PostalCode_Shipping=PostalCode_Shipping,
                    Phone_Shipping=Phone_Shipping,
                    GST_Treatment=GST_Treatment,
                    State_Code=State_Code
                )

                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Party',
                             'Create', 'Party created successfully.', 'Party saved successfully.')

                data = {"PartyID": PartyID}
                data.update(party_serialized.data)
                response_data = {
                    "StatusCode": 6000,
                    "data": data
                }

                return Response(response_data, status=status.HTTP_200_OK)

            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Party',
                             'Create', 'Party created Failed.', "Party Name Already exists")
                response_data = {
                    "StatusCode": 6001,
                    "message": "Party Name Already Exist!!!"
                }

                return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            response_data = {
                "StatusCode": 6001,
                "message": "Invalid GSTNumber!!!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Party', 'Create',
                     'Party created Failed.', generate_serializer_errors(party_serialized._errors))
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(party_serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_party(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    PartyImage = data['PartyImage']
    party_instance = Parties.objects.get(CompanyID=CompanyID, pk=pk)


    if PartyImage == "" or None:
        PartyImage = party_instance.PartyImage

    # serialized = PartiesSerializer(data=request.data)
    ledgerPostInstance = None
    party_serialized = PartiesSerializer(data=request.data)
    LedgerID = party_instance.LedgerID
    instancePartyName = party_instance.PartyName
    BranchID = party_instance.BranchID
    accountLedgerInstance = AccountLedger.objects.get(
        CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)
    LedgerCode = accountLedgerInstance.LedgerCode

    if LedgerPosting.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID, VoucherType="LOB").exists():
        ledgerPostInstance = LedgerPosting.objects.get(
            CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID, VoucherType="LOB")
        ledgerPostInstance.delete()

    PartyID = party_instance.PartyID
    PartyCode = party_instance.PartyCode
    PartyType = party_instance.PartyType

    if party_serialized.is_valid():
        GSTNumber = party_serialized.data['GSTNumber']

        try:
            CountryName = data['CountryName']
        except:
            CountryName = ""

        is_Gstn_validate = True
        if GSTNumber:
            if CountryName == "India":
                is_Gstn_validate = False
                is_Gstn_validate = isValidMasterCardNo(GSTNumber)
        if is_Gstn_validate:
            PartyType = party_serialized.data['PartyType']
            # PartyCode = party_serialized.data['PartyCode']
            PartyName = party_serialized.data['PartyName']
            DisplayName = party_serialized.data['DisplayName']
            FirstName = party_serialized.data['FirstName']
            Attention = party_serialized.data['Attention']
            LastName = party_serialized.data['LastName']
            Address1 = party_serialized.data['Address1']
            Address2 = party_serialized.data['Address2']
            City = party_serialized.data['City']
            State = party_serialized.data['State']
            Country = party_serialized.data['Country']
            PostalCode = party_serialized.data['PostalCode']
            OfficePhone = party_serialized.data['OfficePhone']
            WorkPhone = party_serialized.data['WorkPhone']
            Mobile = party_serialized.data['Mobile']
            WebURL = party_serialized.data['WebURL']
            Email = party_serialized.data['Email']
            IsBillwiseApplicable = party_serialized.data['IsBillwiseApplicable']
            CreditPeriod = party_serialized.data['CreditPeriod']
            CreditLimit = party_serialized.data['CreditLimit']
            PriceCategoryID = party_serialized.data['PriceCategoryID']
            CurrencyID = party_serialized.data['CurrencyID']
            InterestOrNot = party_serialized.data['InterestOrNot']
            RouteID = party_serialized.data['RouteID']
            VATNumber = party_serialized.data['VATNumber']
            GSTNumber = party_serialized.data['GSTNumber']
            Tax1Number = party_serialized.data['Tax1Number']
            Tax2Number = party_serialized.data['Tax2Number']
            Tax3Number = party_serialized.data['Tax3Number']
            PanNumber = party_serialized.data['PanNumber']
            CRNo = party_serialized.data['CRNo']
            BankName1 = party_serialized.data['BankName1']
            AccountName1 = party_serialized.data['AccountName1']
            AccountNo1 = party_serialized.data['AccountNo1']
            IBANOrIFSCCode1 = party_serialized.data['IBANOrIFSCCode1']
            BankName2 = party_serialized.data['BankName2']
            AccountName2 = party_serialized.data['AccountName2']
            AccountNo2 = party_serialized.data['AccountNo2']
            IBANOrIFSCCode2 = party_serialized.data['IBANOrIFSCCode2']
            IsActive = party_serialized.data['IsActive']
            OpeningBalance = party_serialized.data['OpeningBalance']
            Attention_Shipping = party_serialized.data['Attention_Shipping']
            Address1_Shipping = party_serialized.data['Address1_Shipping']
            Address2_Shipping = party_serialized.data['Address2_Shipping']
            State_Shipping = party_serialized.data['State_Shipping']
            Country_Shipping = party_serialized.data['Country_Shipping']
            City_Shipping = party_serialized.data['City_Shipping']
            PostalCode_Shipping = party_serialized.data['PostalCode_Shipping']
            Phone_Shipping = party_serialized.data['Phone_Shipping']

            Action = 'M'

            try:
                GST_Treatment = party_serialized.data['GST_Treatment']
            except:
                GST_Treatment = ""

            try:
                State_Code = party_serialized.data['State_Code']
            except:
                State_Code = ""

            data = request.data
            CrOrDr = data["CrOrDr"]

            LedgerName = PartyName

            if PartyType == "1":
                PartyType = "customer"
                AccountGroupUnder = 10

            elif PartyType == "2":
                PartyType = "supplier"
                AccountGroupUnder = 29

            if CrOrDr == "0":
                CrOrDr = "Dr"

            elif CrOrDr == "1":
                CrOrDr = "Cr"

            is_nameExist = False
            party_ok = False

            PartyNameLow = PartyName.lower()

            parties = Parties.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

            for party in parties:
                party_name = party.PartyName

                party_FirstName = party_name.lower()

                if PartyNameLow == party_FirstName:
                    is_nameExist = True

                if instancePartyName.lower() == PartyNameLow:

                    party_ok = True

            if party_ok:

                accountLedgerInstance.LedgerName = LedgerName
                # accountLedgerInstance.LedgerCode = LedgerCode
                accountLedgerInstance.AccountGroupUnder = AccountGroupUnder
                accountLedgerInstance.OpeningBalance = OpeningBalance
                accountLedgerInstance.CrOrDr = CrOrDr
                accountLedgerInstance.IsActive = IsActive
                accountLedgerInstance.Action = Action
                accountLedgerInstance.CreatedUserID = CreatedUserID
                accountLedgerInstance.UpdatedDate = today
                accountLedgerInstance.save()

                AccountLedger_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=LedgerID,
                    LedgerName=LedgerName,
                    LedgerCode=LedgerCode,
                    AccountGroupUnder=AccountGroupUnder,
                    OpeningBalance=OpeningBalance,
                    CrOrDr=CrOrDr,
                    IsActive=IsActive,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    Action=Action,
                    CompanyID=CompanyID,
                )

                if float(OpeningBalance) > 0:
                    Credit = 0
                    Debit = 0

                    if CrOrDr == "Cr":
                        Credit = OpeningBalance

                    elif CrOrDr == "Dr":
                        Debit = OpeningBalance

                    VoucherType = "LOB"

                    LedgerPostingID = get_auto_LedgerPostid(
                        LedgerPosting, BranchID, CompanyID)

                    LedgerPosting.objects.create(
                        LedgerPostingID=LedgerPostingID,
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

                party_instance.PartyName = PartyName
                party_instance.DisplayName = DisplayName
                party_instance.FirstName = FirstName
                party_instance.LastName = LastName
                party_instance.Attention = Attention
                party_instance.PartyCode = PartyCode
                party_instance.Address1 = Address1
                party_instance.Address2 = Address2
                party_instance.City = City
                party_instance.Country = Country
                party_instance.State = State
                party_instance.PostalCode = PostalCode
                party_instance.OfficePhone = OfficePhone
                party_instance.WorkPhone = WorkPhone
                party_instance.Mobile = Mobile
                party_instance.WebURL = WebURL
                party_instance.Email = Email
                party_instance.IsBillwiseApplicable = IsBillwiseApplicable
                party_instance.CreditPeriod = CreditPeriod
                party_instance.CreditLimit = CreditLimit
                party_instance.PriceCategoryID = PriceCategoryID
                party_instance.CurrencyID = CurrencyID
                party_instance.InterestOrNot = InterestOrNot
                party_instance.RouteID = RouteID
                party_instance.VATNumber = VATNumber
                party_instance.GSTNumber = GSTNumber
                party_instance.Tax1Number = Tax1Number
                party_instance.Tax2Number = Tax2Number
                party_instance.Tax3Number = Tax3Number
                party_instance.PanNumber = PanNumber
                party_instance.CRNo = CRNo
                party_instance.BankName1 = BankName1
                party_instance.AccountName1 = AccountName1
                party_instance.AccountNo1 = AccountNo1
                party_instance.IBANOrIFSCCode1 = IBANOrIFSCCode1
                party_instance.BankName2 = BankName2
                party_instance.AccountName2 = AccountName2
                party_instance.AccountNo2 = AccountNo2
                party_instance.IBANOrIFSCCode2 = IBANOrIFSCCode2
                party_instance.IsActive = IsActive
                party_instance.Action = Action
                party_instance.OpeningBalance = OpeningBalance
                party_instance.CreatedUserID = CreatedUserID
                party_instance.UpdatedDate = today
                party_instance.Attention_Shipping = Attention_Shipping
                party_instance.Address1_Shipping = Address1_Shipping
                party_instance.Address2_Shipping = Address2_Shipping
                party_instance.State_Shipping = State_Shipping
                party_instance.Country_Shipping = Country_Shipping
                party_instance.City_Shipping = City_Shipping
                party_instance.PostalCode_Shipping = PostalCode_Shipping
                party_instance.Phone_Shipping = Phone_Shipping
                party_instance.PartyImage = PartyImage
                party_instance.GST_Treatment = GST_Treatment
                party_instance.State_Code = State_Code
                party_instance.save()

                Parties_Log.objects.create(
                    TransactionID=PartyID,
                    BranchID=BranchID,
                    PartyType=PartyType,
                    LedgerID=LedgerID,
                    PartyCode=PartyCode,
                    PartyName=PartyName,
                    DisplayName=DisplayName,
                    FirstName=FirstName,
                    LastName=LastName,
                    Attention=Attention,
                    Address1=Address1,
                    Address2=Address2,
                    City=City,
                    State=State,
                    Country=Country,
                    PostalCode=PostalCode,
                    OfficePhone=OfficePhone,
                    WorkPhone=WorkPhone,
                    Mobile=Mobile,
                    WebURL=WebURL,
                    Email=Email,
                    IsBillwiseApplicable=IsBillwiseApplicable,
                    CreditPeriod=CreditPeriod,
                    CreditLimit=CreditLimit,
                    PriceCategoryID=PriceCategoryID,
                    CurrencyID=CurrencyID,
                    InterestOrNot=InterestOrNot,
                    RouteID=RouteID,
                    VATNumber=VATNumber,
                    GSTNumber=GSTNumber,
                    Tax1Number=Tax1Number,
                    Tax2Number=Tax2Number,
                    Tax3Number=Tax3Number,
                    PanNumber=PanNumber,
                    CRNo=CRNo,
                    BankName1=BankName1,
                    AccountName1=AccountName1,
                    AccountNo1=AccountNo1,
                    IBANOrIFSCCode1=IBANOrIFSCCode1,
                    BankName2=BankName2,
                    AccountName2=AccountName2,
                    AccountNo2=AccountNo2,
                    IBANOrIFSCCode2=IBANOrIFSCCode2,
                    IsActive=IsActive,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    OpeningBalance=OpeningBalance,
                    PartyImage=PartyImage,
                    CompanyID=CompanyID,
                    Attention_Shipping=Attention_Shipping,
                    Address1_Shipping=Address1_Shipping,
                    Address2_Shipping=Address2_Shipping,
                    State_Shipping=State_Shipping,
                    Country_Shipping=Country_Shipping,
                    City_Shipping=City_Shipping,
                    PostalCode_Shipping=PostalCode_Shipping,
                    Phone_Shipping=Phone_Shipping,
                    GST_Treatment=GST_Treatment,
                    State_Code=State_Code,
                )

                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Party',
                             'Edit', 'Party Updated successfully.', 'Party Updated successfully.')

                response_data = {
                    "StatusCode": 6000,
                    "data": party_serialized.data
                }

                return Response(response_data, status=status.HTTP_200_OK)

            else:
                if is_nameExist:
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Party Name Already exist with this Branch ID"
                    }
                    return Response(response_data, status=status.HTTP_200_OK)

                else:

                    is_LedgernameExist = False

                    LedgerNameLow = LedgerName.lower()

                    accountLedgers = AccountLedger.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID)

                    for accountLedger in accountLedgers:
                        ledger_name = accountLedger.LedgerName

                        ledgerName = ledger_name.lower()

                        if LedgerNameLow == ledgerName:
                            is_LedgernameExist = True

                    if is_LedgernameExist:

                        response_data = {
                            "StatusCode": 6001,
                            "message": "Party Name Already exist with this Branch ID"
                        }
                        return Response(response_data, status=status.HTTP_200_OK)

                    else:
                        accountLedgerInstance.LedgerName = LedgerName
                        # accountLedgerInstance.LedgerCode = LedgerCode
                        accountLedgerInstance.AccountGroupUnder = AccountGroupUnder
                        accountLedgerInstance.OpeningBalance = OpeningBalance
                        accountLedgerInstance.CrOrDr = CrOrDr
                        accountLedgerInstance.Action = Action
                        accountLedgerInstance.UpdatedDate = today
                        accountLedgerInstance.CreatedUserID = CreatedUserID
                        accountLedgerInstance.save()

                        AccountLedger_Log.objects.create(
                            BranchID=BranchID,
                            TransactionID=LedgerID,
                            LedgerName=LedgerName,
                            LedgerCode=LedgerCode,
                            AccountGroupUnder=AccountGroupUnder,
                            OpeningBalance=OpeningBalance,
                            CrOrDr=CrOrDr,
                            IsActive=IsActive,
                            CreatedDate=today,
                            UpdatedDate=today,
                            CreatedUserID=CreatedUserID,
                            Action=Action,
                            CompanyID=CompanyID,
                        )

                        if float(OpeningBalance) > 0:
                            Credit = 0
                            Debit = 0

                            if CrOrDr == "Cr":
                                Credit = OpeningBalance

                            elif CrOrDr == "Dr":
                                Debit = OpeningBalance

                            VoucherType = "LOB"

                            LedgerPostingID = get_auto_LedgerPostid(
                                LedgerPosting, BranchID, CompanyID)

                            LedgerPosting.objects.create(
                                LedgerPostingID=LedgerPostingID,
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

                    party_instance.PartyName = PartyName
                    party_instance.DisplayName = DisplayName
                    party_instance.FirstName = FirstName
                    party_instance.LastName = LastName
                    party_instance.Attention = Attention
                    party_instance.PartyType = PartyType
                    party_instance.LedgerID = LedgerID
                    party_instance.PartyCode = PartyCode
                    party_instance.Address1 = Address1
                    party_instance.Address2 = Address2
                    party_instance.City = City
                    party_instance.Country = Country
                    party_instance.PostalCode = PostalCode
                    party_instance.OfficePhone = OfficePhone
                    party_instance.WorkPhone = WorkPhone
                    party_instance.Mobile = Mobile
                    party_instance.WebURL = WebURL
                    party_instance.Email = Email
                    party_instance.IsBillwiseApplicable = IsBillwiseApplicable
                    party_instance.CreditPeriod = CreditPeriod
                    party_instance.CreditLimit = CreditLimit
                    party_instance.PriceCategoryID = PriceCategoryID
                    party_instance.CurrencyID = CurrencyID
                    party_instance.InterestOrNot = InterestOrNot
                    party_instance.RouteID = RouteID
                    party_instance.VATNumber = VATNumber
                    party_instance.GSTNumber = GSTNumber
                    party_instance.Tax1Number = Tax1Number
                    party_instance.Tax2Number = Tax2Number
                    party_instance.Tax3Number = Tax3Number
                    party_instance.PanNumber = PanNumber
                    party_instance.CRNo = CRNo
                    party_instance.BankName1 = BankName1
                    party_instance.AccountName1 = AccountName1
                    party_instance.AccountNo1 = AccountNo1
                    party_instance.IBANOrIFSCCode1 = IBANOrIFSCCode1
                    party_instance.BankName2 = BankName2
                    party_instance.AccountName2 = AccountName2
                    party_instance.AccountNo2 = AccountNo2
                    party_instance.IBANOrIFSCCode2 = IBANOrIFSCCode2
                    party_instance.IsActive = IsActive
                    party_instance.Action = Action
                    party_instance.OpeningBalance = OpeningBalance
                    party_instance.CreatedUserID = CreatedUserID
                    party_instance.UpdatedDate = today
                    party_instance.Attention_Shipping = Attention_Shipping
                    party_instance.Address1_Shipping = Address1_Shipping
                    party_instance.Address2_Shipping = Address2_Shipping
                    party_instance.State_Shipping = State_Shipping
                    party_instance.Country_Shipping = Country_Shipping
                    party_instance.City_Shipping = City_Shipping
                    party_instance.PostalCode_Shipping = PostalCode_Shipping
                    party_instance.Phone_Shipping = Phone_Shipping
                    party_instance.PartyImage = PartyImage
                    party_instance.save()

                    Parties_Log.objects.create(
                        TransactionID=PartyID,
                        BranchID=BranchID,
                        PartyType=PartyType,
                        LedgerID=LedgerID,
                        PartyCode=PartyCode,
                        PartyName=PartyName,
                        DisplayName=DisplayName,
                        FirstName=FirstName,
                        LastName=LastName,
                        Attention=Attention,
                        Address1=Address1,
                        Address2=Address2,
                        City=City,
                        State=State,
                        Country=Country,
                        PostalCode=PostalCode,
                        OfficePhone=OfficePhone,
                        WorkPhone=WorkPhone,
                        Mobile=Mobile,
                        WebURL=WebURL,
                        Email=Email,
                        IsBillwiseApplicable=IsBillwiseApplicable,
                        CreditPeriod=CreditPeriod,
                        CreditLimit=CreditLimit,
                        PriceCategoryID=PriceCategoryID,
                        CurrencyID=CurrencyID,
                        InterestOrNot=InterestOrNot,
                        RouteID=RouteID,
                        VATNumber=VATNumber,
                        GSTNumber=GSTNumber,
                        Tax1Number=Tax1Number,
                        Tax2Number=Tax2Number,
                        Tax3Number=Tax3Number,
                        PanNumber=PanNumber,
                        CRNo=CRNo,
                        BankName1=BankName1,
                        AccountName1=AccountName1,
                        AccountNo1=AccountNo1,
                        IBANOrIFSCCode1=IBANOrIFSCCode1,
                        BankName2=BankName2,
                        AccountName2=AccountName2,
                        AccountNo2=AccountNo2,
                        IBANOrIFSCCode2=IBANOrIFSCCode2,
                        IsActive=IsActive,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        OpeningBalance=OpeningBalance,
                        PartyImage=PartyImage,
                        CompanyID=CompanyID,
                        Attention_Shipping=Attention_Shipping,
                        Address1_Shipping=Address1_Shipping,
                        Address2_Shipping=Address2_Shipping,
                        State_Shipping=State_Shipping,
                        Country_Shipping=Country_Shipping,
                        City_Shipping=City_Shipping,
                        PostalCode_Shipping=PostalCode_Shipping,
                        Phone_Shipping=Phone_Shipping,
                    )

                    response_data = {
                        "StatusCode": 6000,
                        "data": party_serialized.data
                    }

                    return Response(response_data, status=status.HTTP_200_OK)

        else:
            #request , company, log_type, user, source, action, message, description
            response_data = {
                "StatusCode": 6001,
                "message": "Invalid GSTNumber!!!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Party', 'Edit',
                     'Party Updated Failed.', generate_serializer_errors(party_serialized._errors))
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(party_serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def parties(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    CreatedUserID = data['CreatedUserID']

    try:
        page_number = data['page_no']
    except:
        page_number = ""

    try:
        items_per_page = data['items_per_page']
    except:
        items_per_page = ""

    serialized1 = PartyListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        PartyType = serialized1.data['PartyType']

        if PartyType == "1":
            PartyType = "customer"

        elif PartyType == "2":
            PartyType = "supplier"

        if PartyType == "0":

            if Parties.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
                if page_number and items_per_page:
                    instances = Parties.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID)
                    count = len(instances)
                    ledger_sort_pagination = list_pagination(
                        instances,
                        items_per_page,
                        page_number
                    )
                else:
                    ledger_sort_pagination = Parties.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID)
                    count = len(ledger_sort_pagination)
                serialized = PartiesRestSerializer(ledger_sort_pagination, many=True, context={
                                                   "CompanyID": CompanyID, "PriceRounding": PriceRounding})

                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Party',
                             'List Viewed', 'Party List Viewed Successfully.', 'Party List Viewed Successfully.')
                response_data = {
                    "StatusCode": 6000,
                    "data": serialized.data,
                    "count": count,
                }

                return Response(response_data, status=status.HTTP_200_OK)

            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Party',
                             'List Viewed', 'Party List Viewed Failed.', "Parties not found in this branch.")
                response_data = {
                    "StatusCode": 6001,
                    "message": "Parties not found in this branch."
                }

                return Response(response_data, status=status.HTTP_200_OK)

        elif Parties.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PartyType=PartyType).exists():

            if page_number and items_per_page:
                instances = Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, PartyType=PartyType)
                count = len(instances)
                ledger_sort_pagination = list_pagination(
                    instances,
                    items_per_page,
                    page_number
                )
            else:
                ledger_sort_pagination = Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, PartyType=PartyType)
                count = len(ledger_sort_pagination)

            serialized = PartiesRestSerializer(ledger_sort_pagination, many=True, context={
                                               "CompanyID": CompanyID, "PriceRounding": PriceRounding})

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Party',
                         'List Viewed', 'Party List Viewed Successfully.', 'Party List Viewed Successfully.')
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "count": count,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Party',
                         'List Viewed', 'Party List Viewed Failed.', "Parties not found in this branch.")
            response_data = {
                "StatusCode": 6001,
                "message": "Parties not found in this branch."
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch you enterd is not Valid."
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def party(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']

    if Parties.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = Parties.objects.get(CompanyID=CompanyID, pk=pk)
        serialized = PartiesRestSerializer(
            instance, context={"CompanyID": CompanyID, "PriceRounding": PriceRounding})

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Party', 'Viewe',
                     'Party Single Page Viewed Successfully.', 'Party Single Page Viewed Successfully.')
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Party',
                     'Single Page Viewed', 'Party Single Page Viewed Failed.', "Party not found in this branch.")
        response_data = {
            "StatusCode": 6001,
            "message": "party Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_party(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    accountLedgerInstance = None
    ledgerPostInstance = None
    if Parties.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = Parties.objects.get(CompanyID=CompanyID, pk=pk)

        BranchID = instance.BranchID
        PartyID = instance.PartyID
        PartyType = instance.PartyType
        LedgerID = instance.LedgerID
        PartyCode = instance.PartyCode
        PartyName = instance.PartyName
        DisplayName = instance.DisplayName
        FirstName = instance.FirstName
        LastName = instance.LastName
        Attention = instance.Attention
        Address1 = instance.Address1
        Address2 = instance.Address2
        City = instance.City
        State = instance.State
        Country = instance.Country
        PostalCode = instance.PostalCode
        OfficePhone = instance.OfficePhone
        WorkPhone = instance.WorkPhone
        Mobile = instance.Mobile
        WebURL = instance.WebURL
        Email = instance.Email
        IsBillwiseApplicable = instance.IsBillwiseApplicable
        CreditPeriod = instance.CreditPeriod
        CreditLimit = instance.CreditLimit
        PriceCategoryID = instance.PriceCategoryID
        CurrencyID = instance.CurrencyID
        InterestOrNot = instance.InterestOrNot
        RouteID = instance.RouteID
        VATNumber = instance.VATNumber
        GSTNumber = instance.GSTNumber
        Tax1Number = instance.Tax1Number
        Tax2Number = instance.Tax2Number
        Tax3Number = instance.Tax3Number
        PanNumber = instance.PanNumber
        CRNo = instance.CRNo
        BankName1 = instance.BankName1
        AccountName1 = instance.AccountName1
        AccountNo1 = instance.AccountNo1
        IBANOrIFSCCode1 = instance.IBANOrIFSCCode1
        BankName2 = instance.BankName2
        AccountName2 = instance.AccountName2
        AccountNo2 = instance.AccountNo2
        IBANOrIFSCCode2 = instance.IBANOrIFSCCode2
        IsActive = instance.IsActive
        OpeningBalance = instance.OpeningBalance
        PartyImage = instance.PartyImage
        Attention_Shipping = instance.Attention_Shipping
        Address1_Shipping = instance.Address1_Shipping
        Address2_Shipping = instance.Address2_Shipping
        State_Shipping = instance.State_Shipping
        Country_Shipping = instance.Country_Shipping
        City_Shipping = instance.City_Shipping
        PostalCode_Shipping = instance.PostalCode_Shipping
        Phone_Shipping = instance.Phone_Shipping
        GST_Treatment = instance.GST_Treatment
        State_Code = instance.State_Code
        Action = "D"

        instance.delete()
        Parties_Log.objects.create(
            TransactionID=PartyID,
            BranchID=BranchID,
            PartyType=PartyType,
            LedgerID=LedgerID,
            PartyCode=PartyCode,
            PartyName=PartyName,
            DisplayName=DisplayName,
            FirstName=FirstName,
            LastName=LastName,
            Attention=Attention,
            Address1=Address1,
            Address2=Address2,
            City=City,
            State=State,
            Country=Country,
            PostalCode=PostalCode,
            OfficePhone=OfficePhone,
            WorkPhone=WorkPhone,
            Mobile=Mobile,
            WebURL=WebURL,
            Email=Email,
            IsBillwiseApplicable=IsBillwiseApplicable,
            CreditPeriod=CreditPeriod,
            CreditLimit=CreditLimit,
            PriceCategoryID=PriceCategoryID,
            CurrencyID=CurrencyID,
            InterestOrNot=InterestOrNot,
            RouteID=RouteID,
            VATNumber=VATNumber,
            GSTNumber=GSTNumber,
            Tax1Number=Tax1Number,
            Tax2Number=Tax2Number,
            Tax3Number=Tax3Number,
            PanNumber=PanNumber,
            CRNo=CRNo,
            BankName1=BankName1,
            AccountName1=AccountName1,
            AccountNo1=AccountNo1,
            IBANOrIFSCCode1=IBANOrIFSCCode1,
            BankName2=BankName2,
            AccountName2=AccountName2,
            AccountNo2=AccountNo2,
            IBANOrIFSCCode2=IBANOrIFSCCode2,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            OpeningBalance=OpeningBalance,
            PartyImage=PartyImage,
            CompanyID=CompanyID,
            Attention_Shipping=Attention_Shipping,
            Address1_Shipping=Address1_Shipping,
            Address2_Shipping=Address2_Shipping,
            State_Shipping=State_Shipping,
            Country_Shipping=Country_Shipping,
            City_Shipping=City_Shipping,
            PostalCode_Shipping=PostalCode_Shipping,
            Phone_Shipping=Phone_Shipping,
            GST_Treatment=GST_Treatment,
            State_Code=State_Code
        )

        if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID).exists():
            accountLedgerInstance = AccountLedger.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)

            LedgerName = accountLedgerInstance.LedgerName
            LedgerCode = accountLedgerInstance.LedgerCode
            AccountGroupUnder = accountLedgerInstance.AccountGroupUnder
            OpeningBalance = accountLedgerInstance.OpeningBalance
            CrOrDr = accountLedgerInstance.CrOrDr
            Notes = accountLedgerInstance.Notes
            IsActive = accountLedgerInstance.IsActive
            IsDefault = accountLedgerInstance.IsDefault
            CreatedUserID = accountLedgerInstance.CreatedUserID

            accountLedgerInstance.delete()

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

        if LedgerPosting.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID).exists():
            ledgerPostInstance = LedgerPosting.objects.get(
                CompanyID=CompanyID, LedgerID=LedgerID, BranchID=BranchID)

            LedgerPostingID = ledgerPostInstance.LedgerPostingID
            VoucherType = ledgerPostInstance.VoucherType
            Debit = ledgerPostInstance.Debit
            Credit = ledgerPostInstance.Credit
            IsActive = ledgerPostInstance.IsActive
            CreatedUserID = ledgerPostInstance.CreatedUserID

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

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Party',
                     'Delete', 'Party Deleted Successfully.', 'Party Deleted Successfully.')

        response_data = {
            "StatusCode": 6000,
            "message": "Party Deleted Successfully!",
            "title": "Success",
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID,
                     'Party', 'Delete', 'Party Deleted Failed.', 'Party Not Found!')
        response_data = {
            "StatusCode": 6001,
            "message": "Party Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def upload_party(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']
    input_excel = data['file']

    BranchID = 1
    filepath = os.path.join(
        settings.MEDIA_ROOT, in_memory_file_to_temp(
            input_excel)
    )

    filepath_url = os.path.join(settings.MEDIA_ROOT, filepath)

    task = import_party_task.delay(
        filepath_url, CompanyID, CreatedUserID, BranchID)
    task_id = task.id

    CompanyID = get_company(CompanyID)
    activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Customer Supplier',
                 'Uploaded', 'Customer Supplier Uploaded successfully.', 'Customer Supplier Uploaded successfully.')
    response_data = {
        "StatusCode": 6000,
        "task_id": task_id,
        "message": "Customer Uploaded Successfully!!!"
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def search_parties(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    product_name = data['product_name']
    length = data['length']
    param = data['param']
    Type = data['Type']
    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if Parties.objects.filter(CompanyID=CompanyID, BranchID=BranchID, PartyType=Type).exists():
            instances = Parties.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, PartyType=Type)

            if length < 3:
                if param == "PartyName":
                    instances = instances.filter(
                        (Q(PartyName__icontains=product_name)))[:10]
                elif param == "PartyID":
                    instances = instances.filter(PartyID=product_name)[:10]
                elif param == "FirstName":
                    instances = instances.filter(
                        (Q(FirstName__icontains=product_name)))[:10]
                else:
                    instances = instances.filter(
                        (Q(LastName__icontains=product_name)))[:10]
            else:
                if param == "PartyName":
                    instances = instances.filter(
                        (Q(PartyName__icontains=product_name)))
                elif param == "PartyID":
                    instances = instances.filter(PartyID=product_name)
                elif param == "FirstName":
                    instances = instances.filter(
                        (Q(FirstName__icontains=product_name)))
                else:
                    instances = instances.filter(
                        (Q(LastName__icontains=product_name)))
            serialized = PartiesRestSerializer(instances, many=True, context={
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
