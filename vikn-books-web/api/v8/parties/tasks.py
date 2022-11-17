import string
from django.contrib.auth.models import User
from main.functions import get_company
from django.utils.crypto import get_random_string
from celery_progress.backend import ProgressRecorder
from celery import shared_task
from brands import models
from api.v8.parties.utils import DataframeUtil
from api.v8.parties.functions import get_auto_id, get_auto_idLedger, get_PartyCode
from api.v8.accountLedgers.functions import get_auto_LedgerPostid
import datetime
import xlrd


@shared_task(bind=True)
def import_party_task(self, input_excel, CompanyID, CreatedUserID, BranchID):
    progress_recorder = ProgressRecorder(self)
    today = datetime.datetime.now()
    CompanyID = get_company(CompanyID)

    dataframe = DataframeUtil.get_validated_dataframe(input_excel)
    total = dataframe.shape[0]

    today = datetime.datetime.now()
    IsActive = True
    Action = 'A'
    count = 0
    for index, row in dataframe.iterrows():
        count += 1
        PartyType = row.get('PartyType')
        if row.get('PartyCode'):
            PartyCode = row.get('PartyCode')
        else:
            PartyCode = get_PartyCode(
                models.Parties, BranchID, CompanyID, PartyType.lower())
        if row.get('PartyName'):
            PartyName = row.get('PartyName')
        else:
            PartyName = ""
        if row.get('DisplayName'):
            DisplayName = row.get('DisplayName')
        else:
            DisplayName = ""
        if row.get('Address1'):
            Address1 = row.get('Address1')
        else:
            Address1 = ""
        if row.get('Address2'):
            Address2 = row.get('Address2')
        else:
            Address2 = ""
        if row.get('City'):
            City = row.get('City')
        else:
            City = ""
        if row.get('State'):
            State = row.get('State')
        else:
            State = ""
        if row.get('Country'):
            Country = row.get('Country')
        else:
            Country = ""
        if row.get('PostalCode'):
            PostalCode = row.get('PostalCode')
        else:
            PostalCode = ""
        if row.get('OfficePhone'):
            OfficePhone = row.get('OfficePhone')
        else:
            OfficePhone = ""
        if row.get('WorkPhone'):
            WorkPhone = row.get('WorkPhone')
        else:
            WorkPhone = ""
        if row.get('Mobile'):
            Mobile = row.get('Mobile')
        else:
            Mobile = ""
        if row.get('WebURL'):
            WebURL = row.get('WebURL')
        else:
            WebURL = ""
        if row.get('Email'):
            Email = row.get('Email')
        else:
            Email = ""
        if row.get('IsBillwiseApplicable'):
            IsBillwiseApplicable = row.get('IsBillwiseApplicable')
        else:
            IsBillwiseApplicable = ""
        if row.get('CreditPeriod'):
            CreditPeriod = row.get('CreditPeriod')
        else:
            CreditPeriod = ""
        if row.get('CreditLimit'):
            CreditLimit = row.get('CreditLimit')
        else:
            CreditLimit = ""
        if row.get('RouteName'):
            RouteName = row.get('RouteName')
        else:
            RouteName = ""
        if row.get('VATNumber'):
            VATNumber = row.get('VATNumber')
        else:
            VATNumber = ""
        if row.get('GSTNumber'):
            GSTNumber = row.get('GSTNumber')
        else:
            GSTNumber = ""
        if row.get('Tax1Number'):
            Tax1Number = row.get('Tax1Number')
        else:
            Tax1Number = ""
        if row.get('Tax2Number'):
            Tax2Number = row.get('Tax2Number')
        else:
            Tax2Number = ""
        if row.get('Tax3Number'):
            Tax3Number = row.get('Tax3Number')
        else:
            Tax3Number = ""
        if row.get('PanNumber'):
            PanNumber = row.get('PanNumber')
        else:
            PanNumber = ""
        if row.get('CRNo'):
            CRNo = row.get('CRNo')
        else:
            CRNo = ""
        if row.get('BankName1'):
            BankName1 = row.get('BankName1')
        else:
            BankName1 = ""
        if row.get('AccountName1'):
            AccountName1 = row.get('AccountName1')
        else:
            AccountName1 = ""
        if row.get('AccountNo1'):
            AccountNo1 = row.get('AccountNo1')
        else:
            AccountNo1 = ""
        if row.get('IBANOrIFSCCode1'):
            IBANOrIFSCCode1 = row.get('IBANOrIFSCCode1')
        else:
            IBANOrIFSCCode1 = ""
        if row.get('BankName2'):
            BankName2 = row.get('BankName2')
        else:
            BankName2 = ""
        if row.get('AccountName2'):
            AccountName2 = row.get('AccountName2')
        else:
            AccountName2 = ""
        if row.get('AccountNo2'):
            AccountNo2 = row.get('AccountNo2')
        else:
            AccountNo2 = ""
        if row.get('IBANOrIFSCCode2'):
            IBANOrIFSCCode2 = row.get('IBANOrIFSCCode2')
        else:
            IBANOrIFSCCode2 = ""
        if row.get('OpeningBalance'):
            OpeningBalance = row.get('OpeningBalance')
        else:
            OpeningBalance = ""
        if row.get("CrOrDr"):
            CrOrDr = row.get("CrOrDr")
        else:
            CrOrDr = ""

        if OpeningBalance == None or OpeningBalance == "":
            OpeningBalance = 0

        LedgerID = get_auto_idLedger(models.AccountLedger, BranchID, CompanyID)
        LedgerName = PartyName

        if PartyType.lower() == "customer":
            PartyType = "customer"
            AccountGroupUnder = 10

        elif PartyType.lower() == "supplier":
            PartyType = "supplier"
            AccountGroupUnder = 29

        if not models.Parties.objects.filter(BranchID=BranchID, CompanyID=CompanyID, PartyName__iexact=PartyName).exists():
            if not models.AccountLedger.objects.filter(BranchID=BranchID, CompanyID=CompanyID, LedgerName__iexact=LedgerName).exists():
                models.AccountLedger.objects.create(
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
                    Notes="",
                )

                models.AccountLedger_Log.objects.create(
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

                    if CrOrDr.lower() == "cr":
                        Credit = OpeningBalance

                    elif CrOrDr.lower() == "dr":
                        Debit = OpeningBalance

                    VoucherType = "LOB"

                    LedgerPostingID = get_auto_LedgerPostid(
                        models.LedgerPosting, BranchID, CompanyID)

                    models.LedgerPosting.objects.create(
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

                    models.LedgerPosting_Log.objects.create(
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

            # else:
            #     response_data = {
            #         "StatusCode": 6001,
            #         "message": "Party Name Already Exist!!!"
            #     }

            #     return Response(response_data, status=status.HTTP_200_OK)
            if Country:
                if models.Country.objects.filter(Country_Name__iexact=Country).exists():
                    Country = models.Country.objects.get(
                        Country_Name__iexact=Country).id
                else:
                    Country_create = models.Country.objects.create(
                        Country_Name=Country)
                    Country = Country_create.id
            if State:
                if models.State.objects.filter(Country__pk=Country, State_Name__iexact=State).exists():
                    State = models.State.objects.get(
                        Country__pk=Country, State_Name__iexact=State).id
                else:
                    State_create = models.State.objects.create(
                        Country__pk=Country, State_Name__iexact=State)
                    State = State_create.id

            if RouteName:
                if models.Route.objects.filter(CompanyID=CompanyID, RouteName__iexact=RouteName).exists():
                    RouteID = models.Route.objects.get(
                        CompanyID=CompanyID, RouteName__iexact=RouteName).RouteID
                else:
                    from api.v1.routes.functions import get_auto_id as route_auto_id

                    RouteID = route_auto_id(models.Route, BranchID, CompanyID)
                    Route_create = models.Route.objects.create(
                        RouteID=RouteID,
                        BranchID=BranchID,
                        RouteName=RouteName,
                        Action="A",
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                        Notes="",
                    )
                    RouteID = Route_create.RouteID

            PartyID = get_auto_id(models.Parties, BranchID, CompanyID)
            models.Parties.objects.create(
                PartyID=PartyID,
                BranchID=BranchID,
                PartyType=PartyType,
                LedgerID=LedgerID,
                PartyCode=PartyCode,
                PartyName=PartyName,
                DisplayName=DisplayName,
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
                CompanyID=CompanyID,
                PriceCategoryID=1,
                CurrencyID=0,
                FirstName="",
                LastName="",
                Attention="",
                Attention_Shipping="",
                Address1_Shipping="",
                Address2_Shipping="",
                State_Shipping="",
                Country_Shipping="",
                City_Shipping="",
                PostalCode_Shipping="",
                Phone_Shipping="",
            )

            models.Parties_Log.objects.create(
                TransactionID=PartyID,
                BranchID=BranchID,
                PartyType=PartyType,
                LedgerID=LedgerID,
                PartyCode=PartyCode,
                PartyName=PartyName,
                DisplayName=DisplayName,
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
                CompanyID=CompanyID,
            )
        progress_recorder.set_progress(
            int(count), int(total), description="hello world")

    return '{} items created successfully!'.format(total)
