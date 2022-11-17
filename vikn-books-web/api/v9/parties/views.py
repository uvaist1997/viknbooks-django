from itertools import chain
from locale import currency
from django.http import HttpResponse
from pytz import country_names
from regex import P
from brands.models import BillWiseDetails, BillWiseMaster, PartyBankDetails, PaymentDetails, PaymentMaster, PurchaseMaster, PurchaseOrderMaster, PurchaseReturnMaster, ReceiptDetails, ReceiptMaster, SalesEstimateMaster, SalesMaster, SalesOrderMaster, SalesReturnMaster, State,Activity_Log, Branch, BranchSettings, Country, PriceCategory, Route, UserAdrress, Parties, Parties_Log, AccountLedger, AccountLedger_Log, LedgerPosting, LedgerPosting_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v9.parties.serializers import PartiesSerializer, PartiesRestSerializer, PartyImageSerializer, PartyListSerializer, UserAdrressSerializer
# from api.v9.accountLedgers.serializers import AccountLedgerSerializer
# from api.v9.brands.serializers import ListSerializer
from api.v9.parties.functions import generate_serializer_errors, get_Allparties
from rest_framework import status
from api.v9.parties.functions import get_auto_id, get_auto_idLedger, get_PartyCode
from api.v9.accountLedgers.functions import get_auto_LedgerPostid, get_shippingAddress
from main.functions import converted_float, get_BalanceFromLedgerPost, get_GeneralSettings, get_company, activity_log, get_first_date_of_month, get_no_of_days_in_month, get_treatment, get_week_start_end_date
from api.v9.general.functions import isValidMasterCardNo
from api.v9.parties.tasks import import_party_task
from api.v9.parties.utils import in_memory_file_to_temp
from django.conf import settings
import datetime
from django.db import transaction, IntegrityError
import re
import sys
import os
from api.v9.brands.serializers import ListSerializer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Sum, F
from api.v9.accountLedgers.functions import get_LedgerCode, get_auto_id as generated_ledgerID
from brands import models as model
import json
from api.v9.branchs.functions import get_branch_settings
import pandas as pd
from sqlalchemy import create_engine
from django.utils.timezone import now

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
def create_party(request):
    try:
        with transaction.atomic():
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
                        is_Gstn_validate = isValidMasterCardNo(GSTNumber)
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
                    CurrencyID = request.data['CurrencyID']
                    if CurrencyID == None or CurrencyID == '':
                        CurrencyID = 0
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
                    if not OpeningBalance:
                        OpeningBalance = 0
                    if data['as_on_date'] and converted_float(OpeningBalance) > 0:
                        as_on_date = data['as_on_date']
                    else:
                        as_on_date = today

                    try:
                        GST_Treatment = party_serialized.data['GST_Treatment']
                    except:
                        GST_Treatment = ""

                    try:
                        VAT_Treatment = party_serialized.data['VAT_Treatment']
                    except:
                        VAT_Treatment = ""

                    try:
                        State_Code = party_serialized.data['State_Code']
                    except:
                        State_Code = ""

                    try:
                        PlaceOfSupply = party_serialized.data['PlaceOfSupply']
                    except:
                        PlaceOfSupply = ""

                    try:
                        BankDetails = data['BankDetails']
                    except:
                        BankDetails = []

                    try:
                        District = data['District']
                    except:
                        District = ""

                    try:
                        AdditionalNo = data['AdditionalNo']
                    except:
                        AdditionalNo = ""

                    try:
                        District_shipping = data['District_shipping']
                    except:
                        District_shipping = ""

                    try:
                        AdditionalNo_shipping = data['AdditionalNo_shipping']
                    except:
                        AdditionalNo_shipping = ""

                    Action = 'A'

                    if OpeningBalance == None or OpeningBalance == "":
                        OpeningBalance = 0

                    LedgerID = get_auto_idLedger(
                        AccountLedger, BranchID, CompanyID)

                    CrOrDr = data["CrOrDr"]

                    LedgerName = PartyName

                    if PartyType == "1":
                        PartyType = "customer"
                        AccountGroupUnder = 10

                    elif PartyType == "2":
                        PartyType = "supplier"
                        AccountGroupUnder = 29
                    try:
                        PartyCode = data["PartyCode"]
                    except:
                        PartyCode = get_PartyCode(
                            Parties, BranchID, CompanyID, PartyType)

                    if CrOrDr == "0":
                        CrOrDr = "Dr"

                    elif CrOrDr == "1":
                        CrOrDr = "Cr"

                    is_nameExist = False
                    is_partyCodeExist = False

                    PartyNameLow = PartyName.lower()

                    parties = Parties.objects.filter(
                        CompanyID=CompanyID)
                    customersForAllBranches = get_branch_settings(
                        CompanyID, "customersForAllBranches")
                    suppliersForAllBranches = get_branch_settings(
                        CompanyID, "suppliersForAllBranches")
                    if (PartyType == "customer" and customersForAllBranches == False) or (PartyType == "supplier" and suppliersForAllBranches == False):
                        parties = parties.filter(BranchID=BranchID)

                    if parties.filter(PartyName=LedgerName,PartyType=PartyType).exists():
                        is_nameExist = True
                    if parties.filter(PartyCode=PartyCode).exists():
                        is_partyCodeExist = True

                    # for party in parties:
                    #     party_name = party.PartyName
                    #     party_code = party.PartyCode
                    #     if party_name:
                    #         party_FirstName = party_name.lower()
                    #         if PartyNameLow == party_FirstName:
                    #             is_nameExist = True
                    #     if party_code:
                    #         if PartyCode.lower() == party_code.lower():
                    #             is_partyCodeExist = True

                    if not is_nameExist and not is_partyCodeExist:
                        is_LedgernameExist = False
                        LedgerNameLow = LedgerName.lower()
                        accountLedgers = AccountLedger.objects.filter(
                            CompanyID=CompanyID)
                        for accountLedger in accountLedgers:
                            ledger_name = accountLedger.LedgerName
                            ledgerName = ledger_name.lower()
                            if LedgerNameLow == ledgerName:
                                is_LedgernameExist = True

                        if not is_LedgernameExist:
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
                                as_on_date=as_on_date,
                                Balance=Balance,
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
                                as_on_date=as_on_date,
                                Balance=Balance,
                            )

                            if converted_float(OpeningBalance) > 0:
                                Credit = 0
                                Debit = 0

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
                                #     Date=today,
                                #     VoucherMasterID=LedgerID,
                                #     VoucherType=VoucherType,
                                #     LedgerID=LedgerID,
                                #     Debit=Debit,
                                #     Credit=Credit,
                                #     IsActive=IsActive,
                                #     Action=Action,
                                #     CreatedUserID=CreatedUserID,
                                #     CreatedDate=today,
                                #     UpdatedDate=today,
                                #     CompanyID=CompanyID,
                                # )

                                if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerName="Suspense Account").exists():
                                    RelativeLedgerID = AccountLedger.objects.get(
                                        CompanyID=CompanyID, LedgerName="Suspense Account").LedgerID
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
                                        Notes="",
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
                                        Notes="",
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
                                    VoucherNo=PartyCode,
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
                                    VoucherNo=PartyCode,
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
                                    VoucherNo=PartyCode,
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
                                    VoucherNo=PartyCode,
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

                        else:
                            response_data = {
                                "StatusCode": 6001,
                                "message": "Party Name Already Exist"
                            }

                            return Response(response_data, status=status.HTTP_200_OK)

                        PartyID = get_auto_id(Parties, BranchID, CompanyID)
                        party_instance = Parties.objects.create(
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
                            VAT_Treatment=VAT_Treatment,
                            State_Code=State_Code,
                            PlaceOfSupply=PlaceOfSupply,
                            District=District,
                            AdditionalNo=AdditionalNo,
                            District_shipping=District_shipping,
                            AdditionalNo_shipping=AdditionalNo_shipping,
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
                            VAT_Treatment=VAT_Treatment,
                            State_Code=State_Code,
                            PlaceOfSupply=PlaceOfSupply,
                            District=District,
                            AdditionalNo=AdditionalNo,
                            District_shipping=District_shipping,
                            AdditionalNo_shipping=AdditionalNo_shipping,
                        )

                        branch = Branch.objects.get(
                            CompanyID=CompanyID, BranchID=BranchID)
                        state = None
                        country = None
                        state_Shipping = None
                        country_Shipping = None
                        if State:
                            state = model.State.objects.get(id=State)
                        if Country:
                            country = model.Country.objects.get(id=Country)

                        if Attention or Address1 or Address2 or City or state or country or PostalCode or Mobile:
                            UserAdrress.objects.create(
                                CompanyID=CompanyID,
                                Branch=branch,
                                Type="BillingAddress",
                                Party=party_instance,
                                Attention=Attention,
                                Address1=Address1,
                                Address2=Address2,
                                City=City,
                                state=state,
                                country=country,
                                PostalCode=PostalCode,
                                OfficePhone=OfficePhone,
                                WorkPhone=WorkPhone,
                                Mobile=Mobile,
                                WebURL=WebURL,
                                Email=Email,
                                District=District,
                                AdditionalNo=AdditionalNo,
                            )

                        if State_Shipping:
                            state_Shipping = model.State.objects.get(
                                id=State_Shipping)
                        if Country_Shipping:
                            country_Shipping = model.Country.objects.get(
                                id=Country_Shipping)

                        if Attention_Shipping or Address1_Shipping or Address2_Shipping or State_Shipping or Country_Shipping or City_Shipping or PostalCode_Shipping or Phone_Shipping:
                            UserAdrress.objects.create(
                                CompanyID=CompanyID,
                                Branch=branch,
                                Type="ShippingAddress",
                                Party=party_instance,
                                Attention=Attention_Shipping,
                                Address1=Address1_Shipping,
                                Address2=Address2_Shipping,
                                City=City_Shipping,
                                state=state_Shipping,
                                country=country_Shipping,
                                PostalCode=PostalCode_Shipping,
                                OfficePhone=OfficePhone,
                                WorkPhone=WorkPhone,
                                Mobile=Phone_Shipping,
                                WebURL=WebURL,
                                Email=Email,
                                District=District_shipping,
                                AdditionalNo=AdditionalNo_shipping,
                            )

                        if BankDetails:
                            ret = request.POST
                            BankDetails = json.loads(ret['BankDetails'])
                            for b in BankDetails:
                                model.PartyBankDetails.objects.create(
                                    CompanyID=CompanyID,
                                    Branch=branch,
                                    Party=party_instance,
                                    BankName1=b['BankName1'],
                                    AccountName1=b['AccountName1'],
                                    AccountNo1=b['AccountNo1'],
                                    IBANOrIFSCCode1=b['IBANOrIFSCCode1'],
                                )

                        #request , company, log_type, user, source, action, message, description
                        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Party',
                        #              'Create', 'Party created successfully.', 'Party saved successfully.')

                        data = {"PartyID": PartyID}
                        data.update(party_serialized.data)
                        response_data = {
                            "StatusCode": 6000,
                            "data": data
                        }

                        return Response(response_data, status=status.HTTP_200_OK)

                    else:
                        message = "Party Name already Exist"
                        if is_partyCodeExist:
                            message = "Party Code already exist"
                        #request , company, log_type, user, source, action, message, description
                        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Party',
                                     'Create', 'Party created Failed.', "Party Name Already exists")
                        response_data = {
                            "StatusCode": 6001,
                            "message": message
                        }

                        return Response(response_data, status=status.HTTP_200_OK)
                else:
                    #request , company, log_type, user, source, action, message, description
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Invalid GSTNumber"
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
    except Exception as e:
        try:
            PartyType = data['PartyType']
        except:
            PartyType = "1"

        if PartyType == "1":
            PartyType = "customer"
        else:
            PartyType = "supplier"
        party_type = "Party-" + str(PartyType)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again",
            "err": str(e),
            "err_descrb": err_descrb
        }

        activity_id = activity_log(request._request, CompanyID, 'Error', CreatedUserID, party_type,
                     'Create', str(e), err_descrb)
        body_params = str(request.data)
        Activity_Log.objects.filter(id=activity_id).update(body_params=body_params)
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def edit_party(request, pk):
    try:
        with transaction.atomic():
            data = request.data
            CompanyID = data['CompanyID']
            CompanyID = get_company(CompanyID)
            CreatedUserID = data['CreatedUserID']

            today = datetime.datetime.now()
            PartyImage = data['PartyImage']
            party_instance = Parties.objects.get(CompanyID=CompanyID, pk=pk)
            try:
                is_remove_img = data['is_remove_img']
            except:
                is_remove_img = "false"

            try:
                BankDetails = data['BankDetails']
            except:
                BankDetails = []

            try:
                District = data['District']
            except:
                District = ""

            try:
                AdditionalNo = data['AdditionalNo']
            except:
                AdditionalNo = ""

            try:
                District_shipping = data['District_shipping']
            except:
                District_shipping = ""

            try:
                AdditionalNo_shipping = data['AdditionalNo_shipping']
            except:
                AdditionalNo_shipping = ""

            if is_remove_img == "false" and (PartyImage == "" or PartyImage == None):
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

            if LedgerPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=LedgerID, BranchID=BranchID, VoucherType="LOB").exists():
                ledgerPostInstances = LedgerPosting.objects.filter(
                    CompanyID=CompanyID, VoucherMasterID=LedgerID, BranchID=BranchID, VoucherType="LOB").delete()
                # for ledgerPostInstance in ledgerPostInstances:
                #     ledgerPostInstance.delete()

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
                    CurrencyID = request.data['CurrencyID']
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
                    if not OpeningBalance:
                        OpeningBalance = 0
                    if data['as_on_date'] and converted_float(OpeningBalance) > 0:
                        as_on_date = data['as_on_date']
                    else:
                        as_on_date = today

                    Action = 'M'
                    try:
                        GST_Treatment = party_serialized.data['GST_Treatment']
                    except:
                        GST_Treatment = ""

                    try:
                        VAT_Treatment = party_serialized.data['VAT_Treatment']
                    except:
                        VAT_Treatment = ""

                    try:
                        State_Code = party_serialized.data['State_Code']
                    except:
                        State_Code = ""

                    try:
                        PlaceOfSupply = party_serialized.data['PlaceOfSupply']
                    except:
                        PlaceOfSupply = ""

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
                    party_ok = True

                    # PartyNameLow = PartyName.lower()
                    parties = Parties.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID,PartyName__iexact=LedgerName,PartyType=PartyType).exclude(pk=pk)
                    if parties:
                        is_nameExist = True
                    # for party in parties:
                    #     party_name = party.PartyName
                    #     party_FirstName = party_name.lower()
                    #     if PartyNameLow == party_FirstName:
                    #         is_nameExist = True
                    #     if instancePartyName.lower() == PartyNameLow:
                    #         party_ok = True
                    if not is_nameExist:
                        Balance = 0
                        if converted_float(OpeningBalance) > 0:
                            if CrOrDr == "Cr":
                                Balance = converted_float(OpeningBalance) * -1

                            elif CrOrDr == "Dr":
                                Balance = OpeningBalance

                        instanceBalance = accountLedgerInstance.Balance
                        instanceOpeningBalance = accountLedgerInstance.OpeningBalance
                        instanceCrOrDr = accountLedgerInstance.CrOrDr
                        if instanceCrOrDr == "Cr":
                            instanceOpeningBalance = converted_float(
                                instanceOpeningBalance) * -1
                        elif instanceCrOrDr == "Dr":
                            instanceOpeningBalance = instanceOpeningBalance

                        latest_balance = converted_float(
                            instanceBalance) - converted_float(instanceOpeningBalance)
                        Balance = converted_float(latest_balance) + converted_float(Balance)
                        # accountLedgerInstance.LedgerCode = LedgerCode
                        accountLedgerInstance.LedgerName = LedgerName
                        accountLedgerInstance.AccountGroupUnder = AccountGroupUnder
                        accountLedgerInstance.OpeningBalance = OpeningBalance
                        accountLedgerInstance.CrOrDr = CrOrDr
                        accountLedgerInstance.IsActive = IsActive
                        accountLedgerInstance.Action = Action
                        accountLedgerInstance.CreatedUserID = CreatedUserID
                        accountLedgerInstance.UpdatedDate = today
                        accountLedgerInstance.as_on_date = as_on_date
                        accountLedgerInstance.Balance = Balance
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
                            as_on_date=as_on_date,
                            Balance=Balance,
                        )

                        if converted_float(OpeningBalance) > 0:
                            Credit = 0
                            Debit = 0

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
                            #     Date=today,
                            #     VoucherMasterID=LedgerID,
                            #     VoucherType=VoucherType,
                            #     LedgerID=LedgerID,
                            #     Debit=Debit,
                            #     Credit=Credit,
                            #     IsActive=IsActive,
                            #     Action=Action,
                            #     CreatedUserID=CreatedUserID,
                            #     CreatedDate=today,
                            #     UpdatedDate=today,
                            #     CompanyID=CompanyID,
                            # )

                            if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerName="Suspense Account").exists():
                                RelativeLedgerID = AccountLedger.objects.get(
                                    CompanyID=CompanyID, LedgerName="Suspense Account").LedgerID
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
                                    Notes="Suspense Account",
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
                                    Notes="Suspense Account",
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
                                VoucherNo=PartyCode,
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
                                VoucherNo=PartyCode,
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
                                VoucherNo=PartyCode,
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
                                VoucherNo=PartyCode,
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
                        party_instance.VAT_Treatment = VAT_Treatment
                        party_instance.State_Code = State_Code
                        party_instance.PlaceOfSupply = PlaceOfSupply
                        party_instance.District = District
                        party_instance.AdditionalNo = AdditionalNo
                        party_instance.District_shipping = District_shipping
                        party_instance.AdditionalNo_shipping = AdditionalNo_shipping
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
                            VAT_Treatment=VAT_Treatment,
                            State_Code=State_Code,
                            PlaceOfSupply=PlaceOfSupply,
                            District=District,
                            AdditionalNo=AdditionalNo,
                            District_shipping=District_shipping,
                            AdditionalNo_shipping=AdditionalNo_shipping,
                        )

                        #request , company, log_type, user, source, action, message, description
                        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Party',
                                     'Edit', 'Party Updated successfully.', 'Party Updated successfully.')

                        response_data = {
                            "StatusCode": 6000,
                            "data": party_serialized.data
                        }

                        # return Response(response_data, status=status.HTTP_200_OK)

                    else:
                        # if is_nameExist:
                        response_data = {
                            "StatusCode": 6001,
                            "message": "Party Name already Exist"
                        }
                        return Response(response_data, status=status.HTTP_200_OK)

                        # else:
                        #     # is_LedgernameExist = False
                        #     # LedgerNameLow = LedgerName.lower()
                        #     accountLedgers = AccountLedger.objects.filter(
                        #         CompanyID=CompanyID,LedgerName=LedgerName).exclude(LedgerName__iexact=instancePartyName)

                        #     # for accountLedger in accountLedgers:
                        #     #     ledger_name = accountLedger.LedgerName

                        #     #     ledgerName = ledger_name.lower()

                        #     #     if LedgerNameLow == ledgerName:
                        #     #         is_LedgernameExist = True

                        #     if accountLedgers:
    
                        #         response_data = {
                        #             "StatusCode": 6001,
                        #             "message": "Party Name Already exist with this Branch ID"
                        #         }
                        #         return Response(response_data, status=status.HTTP_200_OK)

                        #     else:
                        #         Balance = 0
                        #         if converted_float(OpeningBalance) > 0:
                        #             if CrOrDr == "Cr":
                        #                 Balance = converted_float(OpeningBalance) * -1

                        #             elif CrOrDr == "Dr":
                        #                 Balance = OpeningBalance

                        #         instanceBalance = accountLedgerInstance.Balance
                        #         instanceOpeningBalance = accountLedgerInstance.OpeningBalance
                        #         instanceCrOrDr = accountLedgerInstance.CrOrDr
                        #         if instanceCrOrDr == "Cr":
                        #             instanceOpeningBalance = converted_float(
                        #                 instanceOpeningBalance) * -1
                        #         elif instanceCrOrDr == "Dr":
                        #             instanceOpeningBalance = instanceOpeningBalance

                        #         latest_balance = converted_float(
                        #             instanceBalance) - converted_float(instanceOpeningBalance)
                        #         Balance = converted_float(
                        #             latest_balance) + converted_float(Balance)
                        #         # accountLedgerInstance.LedgerCode = LedgerCode
                        #         accountLedgerInstance.LedgerName = LedgerName
                        #         accountLedgerInstance.AccountGroupUnder = AccountGroupUnder
                        #         accountLedgerInstance.OpeningBalance = OpeningBalance
                        #         accountLedgerInstance.CrOrDr = CrOrDr
                        #         accountLedgerInstance.Action = Action
                        #         accountLedgerInstance.UpdatedDate = today
                        #         accountLedgerInstance.CreatedUserID = CreatedUserID
                        #         accountLedgerInstance.as_on_date = as_on_date
                        #         accountLedgerInstance.Balance = Balance
                        #         accountLedgerInstance.save()

                        #         AccountLedger_Log.objects.create(
                        #             BranchID=BranchID,
                        #             TransactionID=LedgerID,
                        #             LedgerName=LedgerName,
                        #             LedgerCode=LedgerCode,
                        #             AccountGroupUnder=AccountGroupUnder,
                        #             OpeningBalance=OpeningBalance,
                        #             CrOrDr=CrOrDr,
                        #             IsActive=IsActive,
                        #             CreatedDate=today,
                        #             UpdatedDate=today,
                        #             CreatedUserID=CreatedUserID,
                        #             Action=Action,
                        #             CompanyID=CompanyID,
                        #             as_on_date=as_on_date,
                        #             Balance=Balance,
                        #         )

                        #         if converted_float(OpeningBalance) > 0:
                        #             Credit = 0
                        #             Debit = 0

                        #             if CrOrDr == "Cr":
                        #                 Credit = OpeningBalance

                        #             elif CrOrDr == "Dr":
                        #                 Debit = OpeningBalance

                        #             VoucherType = "LOB"

                        #             # LedgerPostingID = get_auto_LedgerPostid(
                        #             #     LedgerPosting, BranchID, CompanyID)

                        #             # LedgerPosting.objects.create(
                        #             #     LedgerPostingID=LedgerPostingID,
                        #             #     BranchID=BranchID,
                        #             #     Date=today,
                        #             #     VoucherMasterID=LedgerID,
                        #             #     VoucherType=VoucherType,
                        #             #     LedgerID=LedgerID,
                        #             #     Debit=Debit,
                        #             #     Credit=Credit,
                        #             #     IsActive=IsActive,
                        #             #     Action=Action,
                        #             #     CreatedUserID=CreatedUserID,
                        #             #     CreatedDate=today,
                        #             #     UpdatedDate=today,
                        #             #     CompanyID=CompanyID,
                        #             # )

                        #             # LedgerPosting_Log.objects.create(
                        #             #     TransactionID=LedgerPostingID,
                        #             #     BranchID=BranchID,
                        #             #     Date=today,
                        #             #     VoucherMasterID=LedgerID,
                        #             #     VoucherType=VoucherType,
                        #             #     LedgerID=LedgerID,
                        #             #     Debit=Debit,
                        #             #     Credit=Credit,
                        #             #     IsActive=IsActive,
                        #             #     Action=Action,
                        #             #     CreatedUserID=CreatedUserID,
                        #             #     CreatedDate=today,
                        #             #     UpdatedDate=today,
                        #             #     CompanyID=CompanyID,
                        #             # )

                        #             if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerName="Suspense Account").exists():
                        #                 RelativeLedgerID = AccountLedger.objects.get(
                        #                     CompanyID=CompanyID, LedgerName="Suspense Account").LedgerID
                        #             else:
                        #                 RelativeLedgerID = get_auto_id(
                        #                     AccountLedger, BranchID, CompanyID)
                        #                 SuspenseLedgerCode = get_LedgerCode(
                        #                     AccountLedger, BranchID, CompanyID)

                        #                 AccountLedger.objects.create(
                        #                     LedgerID=RelativeLedgerID,
                        #                     BranchID=BranchID,
                        #                     LedgerName="Suspense Account",
                        #                     LedgerCode=SuspenseLedgerCode,
                        #                     AccountGroupUnder=26,
                        #                     OpeningBalance=0,
                        #                     CrOrDr="Dr",
                        #                     Notes="Suspense Account",
                        #                     IsActive=True,
                        #                     IsDefault=True,
                        #                     CreatedDate=today,
                        #                     UpdatedDate=today,
                        #                     Action=Action,
                        #                     CreatedUserID=CreatedUserID,
                        #                     CompanyID=CompanyID,
                        #                 )

                        #                 AccountLedger_Log.objects.create(
                        #                     BranchID=BranchID,
                        #                     TransactionID=RelativeLedgerID,
                        #                     LedgerName="Suspense Account",
                        #                     LedgerCode=SuspenseLedgerCode,
                        #                     AccountGroupUnder=26,
                        #                     OpeningBalance=0,
                        #                     CrOrDr="Dr",
                        #                     Notes="Suspense Account",
                        #                     IsActive=True,
                        #                     IsDefault=True,
                        #                     CreatedDate=today,
                        #                     UpdatedDate=today,
                        #                     Action=Action,
                        #                     CreatedUserID=CreatedUserID,
                        #                     CompanyID=CompanyID,
                        #                 )

                        #             LedgerPostingID = get_auto_LedgerPostid(
                        #                 LedgerPosting, BranchID, CompanyID)

                        #             LedgerPosting.objects.create(
                        #                 LedgerPostingID=LedgerPostingID,
                        #                 BranchID=BranchID,
                        #                 Date=as_on_date,
                        #                 VoucherMasterID=LedgerID,
                        #                 VoucherType=VoucherType,
                        #                 VoucherNo=PartyCode,
                        #                 LedgerID=LedgerID,
                        #                 RelatedLedgerID=RelativeLedgerID,
                        #                 Debit=Debit,
                        #                 Credit=Credit,
                        #                 IsActive=IsActive,
                        #                 Action=Action,
                        #                 CreatedUserID=CreatedUserID,
                        #                 CreatedDate=today,
                        #                 UpdatedDate=today,
                        #                 CompanyID=CompanyID,
                        #             )

                        #             LedgerPosting_Log.objects.create(
                        #                 TransactionID=LedgerPostingID,
                        #                 BranchID=BranchID,
                        #                 Date=as_on_date,
                        #                 VoucherMasterID=LedgerID,
                        #                 VoucherNo=PartyCode,
                        #                 VoucherType=VoucherType,
                        #                 LedgerID=LedgerID,
                        #                 RelatedLedgerID=RelativeLedgerID,
                        #                 Debit=Debit,
                        #                 Credit=Credit,
                        #                 IsActive=IsActive,
                        #                 Action=Action,
                        #                 CreatedUserID=CreatedUserID,
                        #                 CreatedDate=today,
                        #                 UpdatedDate=today,
                        #                 CompanyID=CompanyID,
                        #             )

                        #             LedgerPostingID = get_auto_LedgerPostid(
                        #                 LedgerPosting, BranchID, CompanyID)

                        #             LedgerPosting.objects.create(
                        #                 LedgerPostingID=LedgerPostingID,
                        #                 BranchID=BranchID,
                        #                 Date=today,
                        #                 VoucherMasterID=LedgerID,
                        #                 VoucherType=VoucherType,
                        #                 VoucherNo=PartyCode,
                        #                 LedgerID=RelativeLedgerID,
                        #                 RelatedLedgerID=LedgerID,
                        #                 Debit=Credit,
                        #                 Credit=Debit,
                        #                 IsActive=IsActive,
                        #                 Action=Action,
                        #                 CreatedUserID=CreatedUserID,
                        #                 CreatedDate=today,
                        #                 UpdatedDate=today,
                        #                 CompanyID=CompanyID,
                        #             )

                        #             LedgerPosting_Log.objects.create(
                        #                 TransactionID=LedgerPostingID,
                        #                 BranchID=BranchID,
                        #                 Date=today,
                        #                 VoucherMasterID=LedgerID,
                        #                 VoucherNo=PartyCode,
                        #                 VoucherType=VoucherType,
                        #                 LedgerID=RelativeLedgerID,
                        #                 RelatedLedgerID=LedgerID,
                        #                 Debit=Credit,
                        #                 Credit=Debit,
                        #                 IsActive=IsActive,
                        #                 Action=Action,
                        #                 CreatedUserID=CreatedUserID,
                        #                 CreatedDate=today,
                        #                 UpdatedDate=today,
                        #                 CompanyID=CompanyID,
                        #             )

                        #     party_instance.PartyName = PartyName
                        #     party_instance.DisplayName = DisplayName
                        #     party_instance.FirstName = FirstName
                        #     party_instance.LastName = LastName
                        #     party_instance.Attention = Attention
                        #     party_instance.PartyType = PartyType
                        #     party_instance.LedgerID = LedgerID
                        #     party_instance.PartyCode = PartyCode
                        #     party_instance.Address1 = Address1
                        #     party_instance.Address2 = Address2
                        #     party_instance.City = City
                        #     party_instance.Country = Country
                        #     party_instance.PostalCode = PostalCode
                        #     party_instance.OfficePhone = OfficePhone
                        #     party_instance.WorkPhone = WorkPhone
                        #     party_instance.Mobile = Mobile
                        #     party_instance.WebURL = WebURL
                        #     party_instance.Email = Email
                        #     party_instance.IsBillwiseApplicable = IsBillwiseApplicable
                        #     party_instance.CreditPeriod = CreditPeriod
                        #     party_instance.CreditLimit = CreditLimit
                        #     party_instance.PriceCategoryID = PriceCategoryID
                        #     party_instance.CurrencyID = CurrencyID
                        #     party_instance.InterestOrNot = InterestOrNot
                        #     party_instance.RouteID = RouteID
                        #     party_instance.VATNumber = VATNumber
                        #     party_instance.GSTNumber = GSTNumber
                        #     party_instance.Tax1Number = Tax1Number
                        #     party_instance.Tax2Number = Tax2Number
                        #     party_instance.Tax3Number = Tax3Number
                        #     party_instance.PanNumber = PanNumber
                        #     party_instance.CRNo = CRNo
                        #     party_instance.BankName1 = BankName1
                        #     party_instance.AccountName1 = AccountName1
                        #     party_instance.AccountNo1 = AccountNo1
                        #     party_instance.IBANOrIFSCCode1 = IBANOrIFSCCode1
                        #     party_instance.BankName2 = BankName2
                        #     party_instance.AccountName2 = AccountName2
                        #     party_instance.AccountNo2 = AccountNo2
                        #     party_instance.IBANOrIFSCCode2 = IBANOrIFSCCode2
                        #     party_instance.IsActive = IsActive
                        #     party_instance.Action = Action
                        #     party_instance.OpeningBalance = OpeningBalance
                        #     party_instance.CreatedUserID = CreatedUserID
                        #     party_instance.UpdatedDate = today
                        #     party_instance.Attention_Shipping = Attention_Shipping
                        #     party_instance.Address1_Shipping = Address1_Shipping
                        #     party_instance.Address2_Shipping = Address2_Shipping
                        #     party_instance.State_Shipping = State_Shipping
                        #     party_instance.Country_Shipping = Country_Shipping
                        #     party_instance.City_Shipping = City_Shipping
                        #     party_instance.PostalCode_Shipping = PostalCode_Shipping
                        #     party_instance.Phone_Shipping = Phone_Shipping
                        #     party_instance.PartyImage = PartyImage
                        #     party_instance.PlaceOfSupply = PlaceOfSupply
                        #     party_instance.District = District
                        #     party_instance.AdditionalNo = AdditionalNo
                        #     party_instance.District_shipping = District_shipping
                        #     party_instance.AdditionalNo_shipping = AdditionalNo_shipping
                        #     party_instance.GST_Treatment = GST_Treatment
                        #     party_instance.VAT_Treatment = VAT_Treatment
                        #     party_instance.save()

                        #     Parties_Log.objects.create(
                        #         TransactionID=PartyID,
                        #         BranchID=BranchID,
                        #         PartyType=PartyType,
                        #         LedgerID=LedgerID,
                        #         PartyCode=PartyCode,
                        #         PartyName=PartyName,
                        #         DisplayName=DisplayName,
                        #         FirstName=FirstName,
                        #         LastName=LastName,
                        #         Attention=Attention,
                        #         Address1=Address1,
                        #         Address2=Address2,
                        #         City=City,
                        #         State=State,
                        #         Country=Country,
                        #         PostalCode=PostalCode,
                        #         OfficePhone=OfficePhone,
                        #         WorkPhone=WorkPhone,
                        #         Mobile=Mobile,
                        #         WebURL=WebURL,
                        #         Email=Email,
                        #         IsBillwiseApplicable=IsBillwiseApplicable,
                        #         CreditPeriod=CreditPeriod,
                        #         CreditLimit=CreditLimit,
                        #         PriceCategoryID=PriceCategoryID,
                        #         CurrencyID=CurrencyID,
                        #         InterestOrNot=InterestOrNot,
                        #         RouteID=RouteID,
                        #         VATNumber=VATNumber,
                        #         GSTNumber=GSTNumber,
                        #         Tax1Number=Tax1Number,
                        #         Tax2Number=Tax2Number,
                        #         Tax3Number=Tax3Number,
                        #         PanNumber=PanNumber,
                        #         CRNo=CRNo,
                        #         BankName1=BankName1,
                        #         AccountName1=AccountName1,
                        #         AccountNo1=AccountNo1,
                        #         IBANOrIFSCCode1=IBANOrIFSCCode1,
                        #         BankName2=BankName2,
                        #         AccountName2=AccountName2,
                        #         AccountNo2=AccountNo2,
                        #         IBANOrIFSCCode2=IBANOrIFSCCode2,
                        #         IsActive=IsActive,
                        #         Action=Action,
                        #         CreatedUserID=CreatedUserID,
                        #         CreatedDate=today,
                        #         UpdatedDate=today,
                        #         OpeningBalance=OpeningBalance,
                        #         PartyImage=PartyImage,
                        #         CompanyID=CompanyID,
                        #         Attention_Shipping=Attention_Shipping,
                        #         Address1_Shipping=Address1_Shipping,
                        #         Address2_Shipping=Address2_Shipping,
                        #         State_Shipping=State_Shipping,
                        #         Country_Shipping=Country_Shipping,
                        #         City_Shipping=City_Shipping,
                        #         PostalCode_Shipping=PostalCode_Shipping,
                        #         Phone_Shipping=Phone_Shipping,
                        #         PlaceOfSupply=PlaceOfSupply,
                        #         District=District,
                        #         AdditionalNo=AdditionalNo,
                        #         District_shipping=District_shipping,
                        #         AdditionalNo_shipping=AdditionalNo_shipping,
                        #     )

                        # response_data = {
                        #     "StatusCode": 6000,
                        #     "data": party_serialized.data
                        # }

                            # return Response(response_data, status=status.HTTP_200_OK)

                    print(">>>>--------------------------------->")
                    branch = Branch.objects.get(
                        CompanyID=CompanyID, BranchID=BranchID)
                    state = None
                    country = None
                    State_Shipping = None
                    Country_Shipping = None
                    if State:
                        state = model.State.objects.get(id=State)
                    if Country:
                        country = model.Country.objects.get(id=Country)

                    if State_Shipping:
                        State_Shipping = model.State.objects.get(
                            id=State_Shipping)
                    if Country_Shipping:
                        Country_Shipping = model.Country.objects.get(
                            id=Country_Shipping)

                    if UserAdrress.objects.filter(CompanyID=CompanyID, Branch=branch, Party=party_instance, Type="BillingAddress").exists():
                        userAddress_bill = UserAdrress.objects.filter(
                            CompanyID=CompanyID, Branch=branch, Party=party_instance, Type="BillingAddress").first()
                        userAddress_bill.Attention = Attention
                        userAddress_bill.Address1 = Address1
                        userAddress_bill.Address2 = Address2
                        userAddress_bill.City = City
                        userAddress_bill.state = state
                        userAddress_bill.country = country
                        userAddress_bill.PostalCode = PostalCode
                        userAddress_bill.OfficePhone = OfficePhone
                        userAddress_bill.WorkPhone = WorkPhone
                        userAddress_bill.Mobile = Mobile
                        userAddress_bill.WebURL = WebURL
                        userAddress_bill.Email = Email
                        userAddress_bill.AdditionalNo = AdditionalNo
                        userAddress_bill.District = District
                        userAddress_bill.save()
                    else:
                        if Attention or Address1 or Address2 or City or state or country or PostalCode or Mobile:
                            UserAdrress.objects.create(
                                CompanyID=CompanyID,
                                Branch=branch,
                                Type="BillingAddress",
                                Party=party_instance,
                                Attention=Attention,
                                Address1=Address1,
                                Address2=Address2,
                                City=City,
                                state=state,
                                country=country,
                                PostalCode=PostalCode,
                                OfficePhone=OfficePhone,
                                WorkPhone=WorkPhone,
                                Mobile=Mobile,
                                WebURL=WebURL,
                                Email=Email,
                                AdditionalNo=AdditionalNo,
                                District=District,
                            )
                    if UserAdrress.objects.filter(CompanyID=CompanyID, Branch=branch, Party=party_instance, Type="ShippingAddress").exists():
                        userAddress_ship = UserAdrress.objects.filter(
                            CompanyID=CompanyID, Branch=branch, Party=party_instance, Type="ShippingAddress").first()
                        userAddress_ship.Attention = Attention_Shipping
                        userAddress_ship.Address1 = Address1_Shipping
                        userAddress_ship.Address2 = Address2_Shipping
                        userAddress_ship.City = City_Shipping
                        userAddress_ship.state = State_Shipping
                        userAddress_ship.country = Country_Shipping
                        userAddress_ship.PostalCode = PostalCode_Shipping
                        userAddress_ship.OfficePhone = OfficePhone
                        userAddress_ship.WorkPhone = WorkPhone
                        userAddress_ship.Mobile = Phone_Shipping
                        userAddress_ship.WebURL = WebURL
                        userAddress_ship.Email = Email
                        userAddress_ship.AdditionalNo = District_shipping
                        userAddress_ship.District = AdditionalNo_shipping
                        userAddress_ship.save()
                    else:
                        if Attention_Shipping or Address1_Shipping or Address2_Shipping or State_Shipping or Country_Shipping or City_Shipping or PostalCode_Shipping or Phone_Shipping:
                            UserAdrress.objects.create(
                                CompanyID=CompanyID,
                                Branch=branch,
                                Type="ShippingAddress",
                                Party=party_instance,
                                Attention=Attention_Shipping,
                                Address1=Address1_Shipping,
                                Address2=Address2_Shipping,
                                City=City_Shipping,
                                state=State_Shipping,
                                country=Country_Shipping,
                                PostalCode=PostalCode_Shipping,
                                OfficePhone=OfficePhone,
                                WorkPhone=WorkPhone,
                                Mobile=Phone_Shipping,
                                WebURL=WebURL,
                                Email=Email,
                                AdditionalNo=District_shipping,
                                District=AdditionalNo_shipping,
                            )

                    if BankDetails:
                        ret = request.POST
                        BankDetails = json.loads(ret['BankDetails'])
                        for b in BankDetails:
                            if b['detailID'] == 1:
                                model.PartyBankDetails.objects.create(
                                    CompanyID=CompanyID,
                                    Branch=branch,
                                    Party=party_instance,
                                    BankName1=b['BankName1'],
                                    AccountName1=b['AccountName1'],
                                    AccountNo1=b['AccountNo1'],
                                    IBANOrIFSCCode1=b['IBANOrIFSCCode1'],
                                )
                            else:
                                bank_detail_instance = model.PartyBankDetails.objects.get(
                                    id=b['id'])
                                bank_detail_instance.BankName1 = b['BankName1']
                                bank_detail_instance.AccountName1 = b['AccountName1']
                                bank_detail_instance.AccountNo1 = b['AccountNo1']
                                bank_detail_instance.IBANOrIFSCCode1 = b['IBANOrIFSCCode1']
                                bank_detail_instance.save()

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
    except Exception as e:
        try:
            PartyType = data['PartyType']
        except:
            PartyType = "1"

        if PartyType == "1":
            PartyType = "customer"
        else:
            PartyType = "supplier"
        party_type = "Party-" + str(PartyType)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err_descrb = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        response_data = {
            "StatusCode": 6001,
            "message": "some error occured..please try again",
            "err": str(e),
            "err_descrb": err_descrb
        }

        activity_id = activity_log(request._request, CompanyID, 'Error', CreatedUserID, party_type,
                     'Edit', str(e), err_descrb)
        body_params = str(request.data)
        Activity_Log.objects.filter(id=activity_id).update(body_params=body_params)
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

    check_suppliersForAllBranches = False
    check_customersForAllBranches = False
    if BranchSettings.objects.filter(CompanyID=CompanyID, SettingsType="suppliersForAllBranches").exists():
        check_suppliersForAllBranches = BranchSettings.objects.get(
            CompanyID=CompanyID, SettingsType="suppliersForAllBranches").SettingsValue
    if BranchSettings.objects.filter(CompanyID=CompanyID, SettingsType="customersForAllBranches").exists():
        check_customersForAllBranches = BranchSettings.objects.get(
            CompanyID=CompanyID, SettingsType="customersForAllBranches").SettingsValue


    serialized1 = PartyListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        PartyType = serialized1.data['PartyType']

        if PartyType == "1":
            PartyType = "customer"
            if check_customersForAllBranches == True or check_customersForAllBranches == "True":

                parties_instances = Parties.objects.filter(
                    CompanyID=CompanyID, PartyType=PartyType)
            else:
                parties_instances = Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, PartyType=PartyType)

        elif PartyType == "2":
            PartyType = "supplier"
            if check_suppliersForAllBranches == True or check_suppliersForAllBranches == "True":

                parties_instances = Parties.objects.filter(
                    CompanyID=CompanyID, PartyType=PartyType)
            else:
                parties_instances = Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, PartyType=PartyType)

        if PartyType == "0":
            if check_customersForAllBranches == True or check_customersForAllBranches == "True" and check_suppliersForAllBranches == True or check_suppliersForAllBranches == "True":
                customer_list = Parties.objects.filter(
                    CompanyID=CompanyID,  PartyType=1)
                supplier_list = Parties.objects.filter(
                    CompanyID=CompanyID, PartyType=2)
                parties_instances = list(chain(customer_list, supplier_list))
            elif check_customersForAllBranches == True or check_customersForAllBranches == "True" and check_suppliersForAllBranches == False or check_suppliersForAllBranches == "False":
                customer_list = Parties.objects.filter(
                    CompanyID=CompanyID,  PartyType=1)
                supplier_list = Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, PartyType=2)
                parties_instances = list(chain(customer_list, supplier_list))
            elif check_customersForAllBranches == False or check_customersForAllBranches == "False" and check_suppliersForAllBranches == True or check_suppliersForAllBranches == "True":

                customer_list = Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, PartyType=1)
                supplier_list = Parties.objects.filter(
                    CompanyID=CompanyID, PartyType=2)
                parties_instances = list(chain(customer_list, supplier_list))
            else:
                parties_instances = Parties.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)

            if parties_instances.exists():
                if page_number and items_per_page:
                    instances = parties_instances
                    count = len(instances)
                    ledger_sort_pagination = list_pagination(
                        instances,
                        items_per_page,
                        page_number
                    )
                else:
                    ledger_sort_pagination = parties_instances
                    count = len(ledger_sort_pagination)
                serialized = PartiesRestSerializer(ledger_sort_pagination, many=True, context={
                                                   "CompanyID": CompanyID, "PriceRounding": PriceRounding})

                #request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Party',
                #              'List Viewed', 'Party List Viewed Successfully.', 'Party List Viewed Successfully.')
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

        elif parties_instances.exists():
            # for i in parties_instances:
            print(parties_instances.count(),"STOCKVALUEREPORT")

            if page_number and items_per_page:
                instances = parties_instances
                count = len(instances)
                ledger_sort_pagination = list_pagination(
                    instances,
                    items_per_page,
                    page_number
                )
            else:
                ledger_sort_pagination = parties_instances
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
        # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Party', 'Viewe',
        #              'Party Single Page Viewed Successfully.', 'Party Single Page Viewed Successfully.')
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

    try:
        selecte_ids = data['selecte_ids']
    except:
        selecte_ids = []

    today = datetime.datetime.now()
    instances = None
    accountLedgerInstance = None
    ledgerPostInstance = None

    if selecte_ids:
        if Parties.objects.filter(CompanyID=CompanyID, pk__in=selecte_ids).exists():
            instances = Parties.objects.filter(pk__in=selecte_ids)
    else:
        if Parties.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instances = Parties.objects.filter(pk=pk)

    # if Parties.objects.filter(CompanyID=CompanyID, pk=pk).exists():
    #     instance = Parties.objects.get(CompanyID=CompanyID, pk=pk)
    if instances:
        for instance in instances:
            if not LedgerPosting.objects.filter(CompanyID=CompanyID, LedgerID=instance.LedgerID).exclude(VoucherType="LOB").exists():
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
                VAT_Treatment = instance.VAT_Treatment
                State_Code = instance.State_Code
                PlaceOfSupply = instance.PlaceOfSupply
                District = instance.District
                AdditionalNo = instance.AdditionalNo
                District_shipping = instance.District_shipping
                AdditionalNo_shipping = instance.AdditionalNo_shipping

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
                    VAT_Treatment=VAT_Treatment,
                    State_Code=State_Code,
                    PlaceOfSupply=PlaceOfSupply,
                    District=District,
                    AdditionalNo=AdditionalNo,
                    District_shipping=District_shipping,
                    AdditionalNo_shipping=AdditionalNo_shipping,
                )

                if AccountLedger.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():
                    accountLedgerInstance = AccountLedger.objects.get(
                        CompanyID=CompanyID, LedgerID=LedgerID)

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

                if LedgerPosting.objects.filter(CompanyID=CompanyID, VoucherMasterID=LedgerID, VoucherType="LOB", BranchID=BranchID).exists():
                    ledgerPostInstances = LedgerPosting.objects.filter(
                        CompanyID=CompanyID, VoucherMasterID=LedgerID, VoucherType="LOB", BranchID=BranchID)
                    for ledgerPostInstance in ledgerPostInstances:
                        LedgerPostingID = ledgerPostInstance.LedgerPostingID
                        VoucherType = ledgerPostInstance.VoucherType
                        LedgerID = ledgerPostInstance.LedgerID
                        RelatedLedgerID = ledgerPostInstance.RelatedLedgerID
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

                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Party',
                             'Delete', 'Party Deleted Successfully.', 'Party Deleted Successfully.')

                response_data = {
                    "StatusCode": 6000,
                    "message": "Party Deleted Successfully!",
                    "title": "Success",
                }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "Can't delete this party!"
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
    PartyType = data['PartyType']

    BranchID = 1
    filepath = os.path.join(
        settings.MEDIA_ROOT, in_memory_file_to_temp(
            input_excel)
    )

    filepath_url = os.path.join(settings.MEDIA_ROOT, filepath)

    task = import_party_task.delay(
        filepath_url, CompanyID, CreatedUserID, BranchID,PartyType)
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

        check_suppliersForAllBranches = False
        check_customersForAllBranches = False
        if BranchSettings.objects.filter(CompanyID=CompanyID, SettingsType="suppliersForAllBranches").exists():
            check_suppliersForAllBranches = BranchSettings.objects.get(
                CompanyID=CompanyID, SettingsType="suppliersForAllBranches").SettingsValue
        if BranchSettings.objects.filter(CompanyID=CompanyID, SettingsType="customersForAllBranches").exists():
            check_customersForAllBranches = BranchSettings.objects.get(
                CompanyID=CompanyID, SettingsType="customersForAllBranches").SettingsValue

        print(check_suppliersForAllBranches, 'customersForAllBranches')
        print(check_customersForAllBranches, 'suppliersForAllBranches')
        if check_customersForAllBranches == True or check_customersForAllBranches == "True" or check_suppliersForAllBranches == True or check_suppliersForAllBranches == "True":
            parties_instance = Parties.objects.filter(
                CompanyID=CompanyID, PartyType=Type)
        else:
            parties_instance = Parties.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, PartyType=Type)

        if parties_instance.exists():
            instances = parties_instance

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


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def user_address_list(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    LedgerID = data['LedgerID']
    shipping_addresses = get_shippingAddress(CompanyID, BranchID, LedgerID)
    response_data = {
        "StatusCode": 6000,
        "shipping_addresses": shipping_addresses,
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def user_address_create(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    LedgerID = data['LedgerID']
    Attention = data['Attention']
    try:
        Address1 = data['Address1']
    except:
        Address1 = ""
    try:
        Address2 = data['Address2']
    except:
        Address2 = ""
    try:
        City = data['City']
    except:
        City = ""
    state = data['state']
    country = data['country']
    try:
        Mobile = data['Mobile']
    except:
        Mobile = ""
    try:
        District = data['District']
    except:
        District = ""
    try:
        PostalCode = data['PostalCode']
    except:
        PostalCode = ""
    
    try:
        Type = data['Type']
    except:
        Type = "ShippingAddress"

    shipping_addresses = []
    if Parties.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():
        party_instance = Parties.objects.get(
            CompanyID=CompanyID, LedgerID=LedgerID)

        branch = Branch.objects.get(CompanyID=CompanyID, BranchID=BranchID)
        state_ins = None
        country_ins = None
        if state:
            state_ins = model.State.objects.filter(id=state).first()
        if country:
            country_ins = model.Country.objects.filter(id=country).first()
        branch = Branch.objects.get(CompanyID=CompanyID, BranchID=BranchID)
        branch = Branch.objects.get(CompanyID=CompanyID, BranchID=BranchID)
        userAdrr_ins = UserAdrress.objects.create(
            CompanyID=CompanyID,
            Branch=branch,
            Type=Type,
            Party=party_instance,
            Attention=Attention,
            Address1=Address1,
            Address2=Address2,
            City=City,
            state=state_ins,
            country=country_ins,
            PostalCode=PostalCode,
            District=District,
            Mobile=Mobile,
        )

        # shipping_addresses.append({
        #     "id": userAdrr_ins.id,
        #     "Attention": Attention,
        #     "Address1": Address1,
        #     "Address2": Address2,
        #     "City": City,
        #     "state": state,
        #     "country": country,
        #     "Mobile": Mobile,
        # })

        shipping_addresses = get_shippingAddress(CompanyID, BranchID, LedgerID,Type)

        response_data = {
            "StatusCode": 6000,
            "shipping_addresses": shipping_addresses,
            "userAdrr_id": userAdrr_ins.id
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Party not found",
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def search_party_list(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    product_name = data['product_name']
    length = data['length']
    PartyType = data['PartyType']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        check_suppliersForAllBranches = False
        check_customersForAllBranches = False
        if BranchSettings.objects.filter(CompanyID=CompanyID, SettingsType="suppliersForAllBranches").exists():
            check_suppliersForAllBranches = BranchSettings.objects.get(
                CompanyID=CompanyID, SettingsType="suppliersForAllBranches").SettingsValue
        if BranchSettings.objects.filter(CompanyID=CompanyID, SettingsType="customersForAllBranches").exists():
            check_customersForAllBranches = BranchSettings.objects.get(
                CompanyID=CompanyID, SettingsType="customersForAllBranches").SettingsValue

        print(check_suppliersForAllBranches, 'customersForAllBranches')
        print(check_customersForAllBranches, 'suppliersForAllBranches')
        if check_customersForAllBranches == True or check_customersForAllBranches == "True" or check_suppliersForAllBranches == True or check_suppliersForAllBranches == "True":
            parties_instance = Parties.objects.filter(
                CompanyID=CompanyID, PartyType=PartyType)
        else:
            parties_instance = Parties.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, PartyType=PartyType)

        if parties_instance.exists():
            if length < 3:
                instances = parties_instance
                instances = instances.filter((Q(PartyName__icontains=product_name)) | (
                    Q(DisplayName__icontains=product_name)) | (
                    Q(FirstName__icontains=product_name)))[:10]
            else:
                instances = parties_instance
                instances = instances.filter((Q(PartyName__icontains=product_name)) | (
                    Q(DisplayName__icontains=product_name)) | (
                    Q(FirstName__icontains=product_name)))
            serialized = PartiesRestSerializer(instances, many=True, context={
                "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding, })
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "data": "Party not found!"
            }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def user_address_update(request):
    data = request.data
    id = data['id']
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    LedgerID = data['LedgerID']
    Attention = data['Attention']
    Address1 = data['Address1']
    Address2 = data['Address2']
    City = data['City']
    state = data['state']
    country = data['country']
    Mobile = data['Mobile']
    District = data['District']
    PostalCode = data['PostalCode']
    
    try:
        Type = data['Type']
    except:
        Type = "ShippingAddress"

    shipping_addresses = []
    if Parties.objects.filter(CompanyID=CompanyID, LedgerID=LedgerID).exists():
        party_instance = Parties.objects.get(
            CompanyID=CompanyID, LedgerID=LedgerID)

        branch = Branch.objects.get(CompanyID=CompanyID, BranchID=BranchID)
        state_ins = None
        country_ins = None
        if state:
            state_ins = model.State.objects.filter(id=state).first()
        if country:
            country_ins = model.Country.objects.filter(id=country).first()
        branch = Branch.objects.get(CompanyID=CompanyID, BranchID=BranchID)
        branch = Branch.objects.get(CompanyID=CompanyID, BranchID=BranchID)

        if UserAdrress.objects.filter(id=id).exists():
            user_addrsss = UserAdrress.objects.get(id=id)
            user_addrsss.Attention = Attention
            user_addrsss.Address1 = Address1
            user_addrsss.Address2 = Address2
            user_addrsss.City = City
            user_addrsss.state = state_ins
            user_addrsss.country = country_ins
            user_addrsss.PostalCode = PostalCode
            user_addrsss.District = District
            user_addrsss.Mobile = Mobile
            user_addrsss.save()
            shipping_addresses = get_shippingAddress(
                CompanyID, BranchID, LedgerID,Type)

            response_data = {
                "StatusCode": 6000,
                "shipping_addresses": shipping_addresses,
                "userAdrr_id": user_addrsss.id
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Address not found",
            }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Party not found",
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def upload_parties(request):
    today = datetime.datetime.now()

    data = request.data
    # serializer = UploadSerializer(data=request.data)
    # if serializer.is_valid():
    BranchID = data['BranchID']
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)

    CreatedUserID = data['CreatedUserID']
    input_excel = data['file']
    Type = data['Type']

    filepath = os.path.join(
        settings.MEDIA_ROOT, in_memory_file_to_temp(
            input_excel)
    )

    filepath_url = os.path.join(settings.MEDIA_ROOT, filepath)
    df = pd.read_excel(filepath_url)
    # json_records = df.reset_index().to_json(orient ='records')
    details = json.loads(df.to_json(orient='records'))
    print(details)
    # del json_records['index']
    # details = json.loads(json_records)
    party_list = []
    for i in details:
        dic = {
            "PartyType":"customer",
        }
        party_list.append(i)

    Parties.objects.bulk_create([
        Parties(
        **{key:value for key, value in i.items()},
        BranchID=BranchID,
        CompanyID=CompanyID,
        )
        for i in details
    ])
 
    
   
    activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product',
                 'Uploaded', 'Product Uploaded successfully.', 'Product Uploaded successfully.')
    response_data = {
        "StatusCode": 6000,
        # "task_id": task_id,
        "message": "Product Uploaded Successfully!!!"
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def customer_summary(request):
    today = datetime.datetime.now()
    data = request.data
    unq_id = data['unq_id']
    BranchID = data['BranchID']
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    
    if Parties.objects.filter(id=unq_id).exists():
        instance = Parties.objects.get(id=unq_id)
        LedgerID = instance.LedgerID
        ledger_instance = AccountLedger.objects.filter(CompanyID=CompanyID,LedgerID=LedgerID).first()
        PriceCategoryName = ""
        RouteName = ""
        TreatmentName = ""
        is_gst = get_GeneralSettings(CompanyID, BranchID, "GST")
        is_vat = False
        if is_gst == False:
            is_vat = get_GeneralSettings(CompanyID, BranchID, "VAT")
        treatment_type = ""
        treatment = ""
        if is_gst == True:
            treatment_type = "gst"
            treatment = instance.GST_Treatment
        if is_vat == True:
            treatment_type = "vat"
            treatment = instance.VAT_Treatment
        TreatmentName = get_treatment(treatment_type, treatment)
        PriceCategoryName = ""
        RouteName = ""
        if PriceCategory.objects.filter(CompanyID=CompanyID, PriceCategoryID=instance.PriceCategoryID,BranchID=BranchID).exists():
            PriceCategoryName = PriceCategory.objects.filter(
                CompanyID=CompanyID, PriceCategoryID=instance.PriceCategoryID, BranchID=BranchID).first().PriceCategoryName
        if Route.objects.filter(CompanyID=CompanyID, RouteID=instance.RouteID, BranchID=BranchID).exists():
            RouteName = Route.objects.filter(
                CompanyID=CompanyID, RouteID=instance.RouteID, BranchID=BranchID).first().RouteName
        
        country_name = ""
        ship_country_name = ""
        state_name = ""
        ship_state_name = ""
        currency = "Rs"
        CountryCode = "INR"
        Countryid = ""
        StateId = ""
        ShippingCountryid = ""
        ShippingStateId = ""
        
        if instance.Country and Country.objects.filter(id=instance.Country).exists():
            country_ins = Country.objects.get(id=instance.Country)
            country_name = country_ins.Country_Name
            currency = country_ins.Symbol
            CountryCode = country_ins.CountryCode
            Countryid = country_ins.id
        if instance.Country_Shipping and Country.objects.filter(id=instance.Country_Shipping).exists():
            ship_country_ins = Country.objects.get(id=instance.Country_Shipping)
            ShippingCountryid = ship_country_ins.id
        if instance.State and State.objects.filter(id=instance.State).exists():
            state_ins = State.objects.get(id=instance.State)
            state_name = state_ins.Name
            StateId = state_ins.id
        if instance.State_Shipping and State.objects.filter(id=instance.State_Shipping).exists():
            ship_state_ins = State.objects.get(id=instance.State_Shipping)
            ShippingStateId = ship_state_ins.id
        if instance.Country_Shipping and Country.objects.filter(id=instance.Country_Shipping).exists():
            ship_country_name = Country.objects.get(
                id=instance.Country_Shipping).Country_Name
        if instance.State_Shipping and State.objects.filter(id=instance.State_Shipping).exists():
            ship_state_name = State.objects.get(
                id=instance.State_Shipping).Name
        BankDetails = []
        if PartyBankDetails.objects.filter(CompanyID=CompanyID, Party=instance).exists():
            party_bankdetails = PartyBankDetails.objects.filter(
                CompanyID=CompanyID, Party=instance)
            for p in party_bankdetails:
                BankDetails.append({
                    "BankName1": p.BankName1,
                    "AccountName1": p.AccountName1,
                    "AccountNo1": p.AccountNo1,
                    "IBANOrIFSCCode1": p.IBANOrIFSCCode1
                })
        customer_image = None
        if instance.PartyImage:
            image_serialized = PartyImageSerializer(
                instance, context={"CompanyID": CompanyID, "request": request}
            )
            customer_image = image_serialized.data.get("PartyImage")
        MainDetails = [{
            "CustomerName": instance.PartyName,
            "DisplayName": instance.DisplayName,
            "PartyCode": instance.PartyCode,
            "OpeningBalance": instance.OpeningBalance,
            "CrOrDr": ledger_instance.CrOrDr,
            "as_on_date": ledger_instance.as_on_date,
            "Email": instance.Email,
            "WorkPhone": instance.WorkPhone,
            "WebURL": instance.WebURL,
            "PartyImage": customer_image
        }]
        
        Transactions = [{
            "CreditPeriod": instance.CreditPeriod,
            "CreditLimit": instance.CreditLimit,
            "PriceCategoryName": PriceCategoryName,
            "RouteName": RouteName,
            "CRNo": instance.CRNo,
            "PanNumber": instance.PanNumber,
            "TreatmentName": TreatmentName,
        }]
        
        AddressDetails = []
        ShipAddressDetails = []
        if UserAdrress.objects.filter(CompanyID=CompanyID, Party=instance).exists():
            user_addr_ins = UserAdrress.objects.filter(
                CompanyID=CompanyID, Party=instance)
            if user_addr_ins.filter(Type="BillingAddress").exists():
                user_Billaddr_ins = user_addr_ins.filter(Type="BillingAddress")
                for b in user_Billaddr_ins:
                    AddressDetails.append({
                        "Attention": b.Attention,
                        "Address1": b.Address1,
                        "Address2": b.Address2,
                        "City": b.City,
                        "District": b.District,
                        "country_name": country_name,
                        "state_name": state_name,
                        "PostalCode": b.PostalCode,
                        "Mobile": b.Mobile,
                    })
                
            shipping_type = ["ShippingAddress", "ShippingAddressAdded"]
            if user_addr_ins.filter(Type__in=shipping_type).exists():
                user_Billaddr_ins = user_addr_ins.filter(Type__in=shipping_type)
                for s in user_Billaddr_ins:
                    ShipAddressDetails.append({
                        "Attention_Shipping": s.Attention,
                        "Address1_Shipping": s.Address1,
                        "Address2_Shipping": s.Address2,
                        "City_Shipping": s.City,
                        "District_shipping": s.District,
                        "ship_country_name": ship_country_name,
                        "ship_state_name": ship_state_name,
                        "PostalCode_Shipping": s.PostalCode,
                        "Phone_Shipping": s.Mobile,
                    })
        
        response_data = {
            "StatusCode": 6000,
            "Transactions": Transactions,
            "MainDetails": MainDetails,
            "AddressDetails": AddressDetails,
            "ShipAddressDetails" : ShipAddressDetails,
            "BankDetails": BankDetails,
            "currency": currency,
            "CountryCode": CountryCode,
            "Countryid": Countryid,
            "StateId": StateId,
            "LedgerID": ledger_instance.LedgerID,
            "ShippingCountryid": ShippingCountryid,
            "ShippingStateId": ShippingStateId
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "not found"
        }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def customer_summary_overview(request):
    today = datetime.datetime.now()
    data = request.data
    unq_id = data['unq_id']
    BranchID = data['BranchID']
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)

    if Parties.objects.filter(id=unq_id).exists():
        instance = Parties.objects.get(id=unq_id)
        LedgerBalance = get_BalanceFromLedgerPost(
            CompanyID, instance.LedgerID, BranchID)
        PaymentDue = 0
        TopAmounts = []
        PendingInvoices = []
        if BillWiseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, CustomerID=instance.LedgerID).exists():
            billwise_instances = BillWiseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, CustomerID=instance.LedgerID)
            invoice_amt_sum = billwise_instances.aggregate(Sum('InvoiceAmount'))
            invoice_amt_sum = invoice_amt_sum['InvoiceAmount__sum']
            payment_sum = billwise_instances.aggregate(
                Sum('Payments'))
            payment_sum = payment_sum['Payments__sum']
            PaymentDue = converted_float(
                invoice_amt_sum) - converted_float(payment_sum)
            TopAmounts.append({
                "LedgerBalance": LedgerBalance,
                "PaymentDue": PaymentDue,
            })
            
            pending_invoiceNos = billwise_instances.filter(
                VoucherType="SI", InvoiceAmount__gt=F('Payments')).values_list("InvoiceNo",flat=True)
            if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, VoucherNo__in=pending_invoiceNos).exists():
                pending_sales = SalesMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, VoucherNo__in=pending_invoiceNos)
                for p in pending_sales:
                    InvoiceNo = p.VoucherNo
                    date = p.Date
                    LedgerName = instance.PartyName
                    GrossAmount = p.TotalGrossAmt
                    TotalTax = p.TotalTax
                    GrandTotal = p.GrandTotal
                    PendingInvoices.append({
                        "InvoiceNo": InvoiceNo,
                        "date": date,
                        "LedgerName": LedgerName,
                        "GrossAmount": GrossAmount,
                        "TotalTax": TotalTax,
                        "GrandTotal": GrandTotal,
                    })
            
        response_data = {
            "StatusCode": 6000,
            "TopAmounts": TopAmounts,
            "PendingInvoices": PendingInvoices
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "not found"
        }
    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def customer_summary_overview_graph(request):
    today = datetime.datetime.now()
    from datetime import date
    from django.db.models.functions import ExtractMonth, ExtractWeekDay, ExtractDay
    data = request.data
    unq_id = data['unq_id']
    BranchID = data['BranchID']
    filterValue = data['filterValue']
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)

    if Parties.objects.filter(id=unq_id).exists():
        instance = Parties.objects.get(id=unq_id)
        LedgerID = instance.LedgerID
        current_date = date.today()
        months_ago = filterValue
        month_previous_date = current_date - \
            datetime.timedelta(days=(months_ago * 365 / 12))
        result = []
        if filterValue == 3 or filterValue == 6:
            sales_invoices = SalesMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Date__gte=month_previous_date, LedgerID=LedgerID
            ).values(
                month=ExtractMonth('Date')
            ).annotate(
                sum_total=Sum('GrandTotal')
            ).order_by('SalesMasterID')

            # order = {r['month']: r['sum_total'] for r in sales_invoices}
            months = []
            order = {}
            for r in sales_invoices:
                if not r['month'] in months:
                    order[r['month']] = r['sum_total']
                    months.append(r['month'])
                else:
                    total = order.get(r['month'])
                    order[r['month']] = converted_float(
                        total) + converted_float(r['sum_total'])

            month = now().month
            # result = [
            #     {'month': (m % 12)+1, 'sum_total': order.get((m % 12) + 1, 0)}
            #     for m in range(month-1, month-8, -1)
            # ]
            no_mnth = months_ago + 1
            result = [
                order.get((m % 12) + 1, 0)
                for m in range(month-1, month - no_mnth, -1)
            ]
            result = sorted(result, key=float)
            print(result)
        
        if filterValue == 2:
            month_previous_date = get_first_date_of_month()
            sales_invoices = SalesMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Date__gte=month_previous_date,LedgerID=LedgerID
            ).values(
                day=ExtractDay('Date')
            ).annotate(
                sum_total=Sum('GrandTotal')
            ).order_by('SalesMasterID')
            # order = {r['day']: r['sum_total'] for r in sales_invoices}
            
            days = []
            order = {}
            for r in sales_invoices:
                if not r['day'] in days:
                    order[r['day']] = r['sum_total']
                    days.append(r['day'])
                else:
                    total = order.get(r['day'])
                    order[r['day']] = converted_float(
                        total) + converted_float(r['sum_total'])
            
            no_mnth = get_no_of_days_in_month(
                month_previous_date.year, month_previous_date.month)
            
            result = [
                order.get((m % no_mnth), 0)
                for m in range(1, no_mnth, 1)
            ]
            # result = sorted(result, key=float)

        if filterValue == 1:
            from datetime import date
            to_day = date.today()
            start_date, end_date = get_week_start_end_date(
                str(to_day))
            sales_invoices = SalesMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Date__gte=start_date, Date__lte=end_date, LedgerID=LedgerID
            ).values(
                weekday=ExtractWeekDay('Date')
            ).annotate(
                sum_total=Sum('GrandTotal')
            ).order_by('SalesMasterID')
            week_days = []
            order = {}
            for r in sales_invoices:
                if not r['weekday'] in week_days:
                    order[r['weekday']] = r['sum_total']
                    week_days.append(r['weekday'])
                else:
                    total = order.get(r['weekday'])
                    order[r['weekday']] = converted_float(
                        total) + converted_float(r['sum_total'])
                    
            # order = {r['weekday']: r['sum_total'] for r in sales_invoices}
            print(order)
            result = [
                order.get((m % 7), 0)
                for m in range(1, 7, 1)
            ]
        result = [float(i) for i in result]
        TotalSales = sum(result)
        response_data = {
            "StatusCode": 6000,
            "graph_datas": result,
            "TotalSales": TotalSales
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "not found"
        }
    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def customer_summary_overview_invoices(request):
    today = datetime.datetime.now()
    data = request.data
    unq_id = data['unq_id']
    BranchID = data['BranchID']
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)

    if Parties.objects.filter(id=unq_id).exists():
        instance = Parties.objects.get(id=unq_id)
        LedgerID = instance.LedgerID
        PartyName = instance.PartyName
        SalesEstimateDatas = []
        SalesOrderDatas = []
        SalesInvoiceDatas = []
        SalesReturnDatas = []
        PurchaseInvoieDatas = []
        PurchaseOrderDatas = []
        PurchaseOrderDatas = []
        PurchaseReturnDatas = []
        ReceiptDatas = []
        PaymentDatas = []
        
        if SalesEstimateMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID,LedgerID=LedgerID).exists():
            estimate_instances = SalesEstimateMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).order_by("-Date")[:5]
            for e in estimate_instances:
                InvoiceNo = e.VoucherNo
                Date = e.Date
                LedgerName = PartyName
                TotalGrossAmt = e.TotalGrossAmt
                TotalTax = e.TotalTax
                GrandTotal = e.GrandTotal
                id = e.id
                SalesEstimateDatas.append({
                    "id": id,
                    "InvoiceNo": InvoiceNo,
                    "Date": Date,
                    "LedgerName": LedgerName,
                    "TotalGrossAmt": TotalGrossAmt,
                    "TotalTax": TotalTax,
                    "GrandTotal": GrandTotal
                })
                
        if SalesOrderMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).exists():
            order_instances = SalesOrderMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).order_by("-Date")[:5]
            for o in order_instances:
                InvoiceNo = o.VoucherNo
                Date = o.Date
                LedgerName = PartyName
                TotalGrossAmt = o.TotalGrossAmt
                TotalTax = o.TotalTax
                GrandTotal = o.GrandTotal
                id = o.id
                SalesOrderDatas.append({
                    "id": id,
                    "InvoiceNo": InvoiceNo,
                    "Date": Date,
                    "LedgerName": LedgerName,
                    "TotalGrossAmt": TotalGrossAmt,
                    "TotalTax": TotalTax,
                    "GrandTotal": GrandTotal
                })
                
        if SalesMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).exists():
            invoice_instances = SalesMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).order_by("-Date")[:5]
            for i in invoice_instances:
                InvoiceNo = i.VoucherNo
                Date = i.Date
                LedgerName = PartyName
                TotalGrossAmt = i.TotalGrossAmt
                TotalTax = i.TotalTax
                GrandTotal = i.GrandTotal
                is_billwised = False
                id = i.id
                if BillWiseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=InvoiceNo, VoucherType="SI", Payments__gt=0).exists():
                    billwise_detail_ins = BillWiseDetails.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=InvoiceNo, VoucherType="SI", Payments__gt=0)
                    if len(billwise_detail_ins) > 0:
                        is_billwised =True
                SalesInvoiceDatas.append({
                    "id": id,
                    "InvoiceNo": InvoiceNo,
                    "Date": Date,
                    "LedgerName": LedgerName,
                    "TotalGrossAmt": TotalGrossAmt,
                    "TotalTax": TotalTax,
                    "GrandTotal": GrandTotal,
                    "is_billwised": is_billwised,
                })
                
        if SalesReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).exists():
            invoice_instances = SalesReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).order_by("-VoucherDate")[:5]
            for i in invoice_instances:
                InvoiceNo = i.VoucherNo
                Date = i.VoucherDate
                LedgerName = PartyName
                TotalGrossAmt = i.TotalGrossAmt
                TotalTax = i.TotalTax
                GrandTotal = i.GrandTotal
                is_billwised = False
                id = i.id
                if BillWiseDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=InvoiceNo, VoucherType="SR", Payments__gt=0).exists():
                    billwise_detail_ins = BillWiseDetails.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, InvoiceNo=InvoiceNo, VoucherType="SR", Payments__gt=0)
                    if len(billwise_detail_ins) > 0:
                        is_billwised = True
                SalesReturnDatas.append({
                    "id": id,
                    "InvoiceNo": InvoiceNo,
                    "Date": Date,
                    "LedgerName": LedgerName,
                    "TotalGrossAmt": TotalGrossAmt,
                    "TotalTax": TotalTax,
                    "GrandTotal": GrandTotal,
                    "is_billwised": is_billwised,
                })
        
        if PurchaseMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).exists():
            invoice_instances = PurchaseMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).order_by("-Date")[:5]
            for i in invoice_instances:
                InvoiceNo = i.VoucherNo
                Date = i.Date
                LedgerName = PartyName
                TotalGrossAmt = i.TotalGrossAmt
                TotalTax = i.TotalTax
                GrandTotal = i.GrandTotal
                id = i.id
                PurchaseInvoieDatas.append({
                    "id": id,
                    "InvoiceNo": InvoiceNo,
                    "Date": Date,
                    "LedgerName": LedgerName,
                    "TotalGrossAmt": TotalGrossAmt,
                    "TotalTax": TotalTax,
                    "GrandTotal": GrandTotal,
                })
                
        if PurchaseOrderMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).exists():
            invoice_instances = PurchaseOrderMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).order_by("-Date")[:5]
            for i in invoice_instances:
                InvoiceNo = i.VoucherNo
                Date = i.Date
                LedgerName = PartyName
                TotalGrossAmt = i.TotalGrossAmt
                TotalTax = i.TotalTax
                GrandTotal = i.GrandTotal
                id = i.id
                PurchaseOrderDatas.append({
                    "id": id,
                    "InvoiceNo": InvoiceNo,
                    "Date": Date,
                    "LedgerName": LedgerName,
                    "TotalGrossAmt": TotalGrossAmt,
                    "TotalTax": TotalTax,
                    "GrandTotal": GrandTotal,
                })
                
        if PurchaseReturnMaster.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).exists():
            invoice_instances = PurchaseReturnMaster.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).order_by("-VoucherDate")[:5]
            for i in invoice_instances:
                InvoiceNo = i.VoucherNo
                Date = i.VoucherDate
                LedgerName = PartyName
                TotalGrossAmt = i.TotalGrossAmt
                TotalTax = i.TotalTax
                GrandTotal = i.GrandTotal
                id = i.id
                PurchaseReturnDatas.append({
                    "id": id,
                    "InvoiceNo": InvoiceNo,
                    "Date": Date,
                    "LedgerName": LedgerName,
                    "TotalGrossAmt": TotalGrossAmt,
                    "TotalTax": TotalTax,
                    "GrandTotal": GrandTotal,
                })
                
        if ReceiptDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).exists():
            receipt_instances = ReceiptDetails.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).order_by("-ReceiptMasterID")[:5]
            for i in receipt_instances:
                ReceiptMasterID = i.ReceiptMasterID
                master_instance = ReceiptMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ReceiptMasterID=ReceiptMasterID).first()
                InvoiceNo = master_instance.VoucherNo
                Date = master_instance.Date
                VoucherType = master_instance.VoucherType
                LedgerName = PartyName
                Amount = i.Amount
                Discount = i.Discount
                NetAmount = i.NetAmount
                id = master_instance.id
                ReceiptDatas.append({
                    "id": id,
                    "InvoiceNo": InvoiceNo,
                    "Date": Date,
                    "LedgerName": LedgerName,
                    "Amount": Amount,
                    "Discount": Discount,
                    "NetAmount": NetAmount,
                    "VoucherType": VoucherType
                })
        
        if PaymentDetails.objects.filter(CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).exists():
            payment_instances = PaymentDetails.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, LedgerID=LedgerID).order_by("-PaymentMasterID")[:5]
            for i in payment_instances:
                PaymentMasterID = i.PaymentMasterID
                master_instance = PaymentMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, PaymentMasterID=PaymentMasterID).first()
                InvoiceNo = master_instance.VoucherNo
                Date = master_instance.Date
                VoucherType = master_instance.VoucherType
                LedgerName = PartyName
                Amount = i.Amount
                Discount = i.Discount
                NetAmount = i.NetAmount
                id = master_instance.id
                PaymentDatas.append({
                    "id": id,
                    "InvoiceNo": InvoiceNo,
                    "Date": Date,
                    "LedgerName": LedgerName,
                    "Amount": Amount,
                    "Discount": Discount,
                    "NetAmount": NetAmount,
                    "VoucherType": VoucherType
                })
                
        response_data = {
            "StatusCode": 6000,
            "SalesEstimateDatas":SalesEstimateDatas,
            "SalesOrderDatas":SalesOrderDatas,
            "SalesInvoiceDatas":SalesInvoiceDatas,
            "SalesReturnDatas":SalesReturnDatas,
            "PurchaseInvoieDatas": PurchaseInvoieDatas,
            "PurchaseOrderDatas": PurchaseOrderDatas,
            "PurchaseReturnDatas": PurchaseReturnDatas,
            "ReceiptDatas": ReceiptDatas,
            "PaymentDatas": PaymentDatas
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "not found"
        }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def parties_export_excel(request):
    # content-type of response
    CompanyID = request.GET.get("CompanyID")
    BranchID = request.GET.get("BranchID")

    UserID = request.GET.get("UserID")
    PriceRounding = request.GET.get("PriceRounding")
    PartyType = request.GET.get("PartyType")

    response = HttpResponse(content_type="application/ms-excel")

    # decide file name
    # response["Content-Disposition"] = 'attachment; filename="Customer.xls"'
    response["Content-Disposition"] = 'attachment; filename="{}.xlsx"'.format(
            PartyType
        )
    # creating workbook
    df = get_Allparties(CompanyID, UserID, PriceRounding, BranchID,PartyType)
    df.to_excel(response,index=False)
    return response