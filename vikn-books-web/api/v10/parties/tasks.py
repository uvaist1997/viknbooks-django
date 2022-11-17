import string
from django.contrib.auth.models import User
from main.functions import converted_float, get_company
from django.utils.crypto import get_random_string
from celery_progress.backend import ProgressRecorder
from celery import shared_task
from brands import models
from api.v10.parties.utils import DataframeUtil
from api.v10.parties.functions import get_auto_id, get_auto_idLedger, get_PartyCode
from api.v10.accountLedgers.functions import get_auto_LedgerPostid
import datetime
import xlrd


@shared_task(bind=True)
def import_party_task(self, input_excel, CompanyID, CreatedUserID, BranchID,PartyType):
    progress_recorder = ProgressRecorder(self)
    today = datetime.datetime.now()
    CompanyID = get_company(CompanyID)

    dataframe = DataframeUtil.get_validated_dataframe(input_excel)
    total = dataframe.shape[0]

    today = datetime.datetime.now()
    IsActive = True
    Action = 'A'
    count = 0
    LedgerID = get_auto_idLedger(models.AccountLedger, BranchID, CompanyID)
    LedgerPostingID = get_auto_LedgerPostid(
                        models.LedgerPosting, BranchID, CompanyID)
    PartyID = get_auto_id(models.Parties, BranchID, CompanyID)
    message = '{} partyS created successfully!'
    str_count = ""
    
    accoundLedger_list = []
    accoundLedger_list_log = []
    ledgerPosting_list = []
    ledgerPosting_list_log = []
    party_list = []
    party_list_log = []

    for index, row in dataframe.iterrows():
        # count += 1
        # PartyType = row.get('PartyType')
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
            IsBillwiseApplicable = False
        # if row.get('InterestOrNot'):
        #     InterestOrNot = row.get('InterestOrNot')
        # else:
        #     InterestOrNot = False
        if row.get('CreditPeriod'):
            CreditPeriod = row.get('CreditPeriod')
        else:
            CreditPeriod = 0
        if row.get('CreditLimit'):
            CreditLimit = row.get('CreditLimit')
        else:
            CreditLimit = 0
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

        LedgerName = PartyName

        if PartyType.lower() == "customer":
            PartyType = "customer"
            AccountGroupUnder = 10

        elif PartyType.lower() == "supplier":
            PartyType = "supplier"
            AccountGroupUnder = 29

        if not models.Parties.objects.filter(BranchID=BranchID, CompanyID=CompanyID, PartyName__iexact=PartyName).exists():
            print(count,"NOT PARTIE EXIST",PartyName)
            if not models.AccountLedger.objects.filter(CompanyID=CompanyID, LedgerName__iexact=LedgerName).exists():
                print("NOT ACCOUNT EXIST",PartyName)
                LedgerID = int(LedgerID)+count
                # models.AccountLedger.objects.create(
                #     LedgerID=LedgerID,
                #     BranchID=BranchID,
                #     LedgerName=LedgerName,
                #     LedgerCode=PartyCode,
                #     AccountGroupUnder=AccountGroupUnder,
                #     OpeningBalance=OpeningBalance,
                #     CrOrDr=CrOrDr,
                #     IsActive=IsActive,
                #     CreatedDate=today,
                #     UpdatedDate=today,
                #     Action=Action,
                #     CreatedUserID=CreatedUserID,
                #     CompanyID=CompanyID,
                #     Notes="",
                # )

                # models.AccountLedger_Log.objects.create(
                #     BranchID=BranchID,
                #     TransactionID=LedgerID,
                #     LedgerName=LedgerName,
                #     LedgerCode=PartyCode,
                #     AccountGroupUnder=AccountGroupUnder,
                #     OpeningBalance=OpeningBalance,
                #     CrOrDr=CrOrDr,
                #     IsActive=IsActive,
                #     CreatedDate=today,
                #     UpdatedDate=today,
                #     Action=Action,
                #     CreatedUserID=CreatedUserID,
                #     CompanyID=CompanyID,
                # )
                accoundLedger_list.append({
                    "LedgerID":LedgerID,
                    "LedgerName":LedgerName,
                    "LedgerCode":PartyCode,
                    "AccountGroupUnder":AccountGroupUnder,
                    "OpeningBalance":OpeningBalance,
                    "CrOrDr":CrOrDr,
                    "IsActive":IsActive,
                    "CreatedDate":today,
                    "UpdatedDate":today,
                    "Action":Action,
                    "CreatedUserID":CreatedUserID,
                    "Notes":"",
                })
                accoundLedger_list_log.append({
                    "TransactionID":LedgerID,
                    "LedgerName":LedgerName,
                    "LedgerCode":PartyCode,
                    "AccountGroupUnder":AccountGroupUnder,
                    "OpeningBalance":OpeningBalance,
                    "CrOrDr":CrOrDr,
                    "IsActive":IsActive,
                    "CreatedDate":today,
                    "UpdatedDate":today,
                    "Action":Action,
                    "CreatedUserID":CreatedUserID,
                    "Notes":"",
                })
                

                if converted_float(OpeningBalance) > 0:
                    Credit = 0
                    Debit = 0

                    if CrOrDr.lower() == "cr":
                        Credit = OpeningBalance

                    elif CrOrDr.lower() == "dr":
                        Debit = OpeningBalance

                    VoucherType = "LOB"
                    

                    # models.LedgerPosting.objects.create(
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

                    # models.LedgerPosting_Log.objects.create(
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
                    ledgerPosting_list.append({
                        "LedgerPostingID":int(LedgerPostingID)+count,
                        "Date":today,
                        "VoucherMasterID":LedgerID,
                        "VoucherType":VoucherType,
                        "LedgerID":LedgerID,
                        "Debit":Debit,
                        "Credit":Credit,
                        "IsActive":IsActive,
                        "Action":Action,
                        "CreatedUserID":CreatedUserID,
                        "CreatedDate":today,
                        "UpdatedDate":today,
                    })
                    ledgerPosting_list_log.append({
                        "TransactionID":int(LedgerPostingID)+count,
                        "Date":today,
                        "VoucherMasterID":LedgerID,
                        "VoucherType":VoucherType,
                        "LedgerID":LedgerID,
                        "Debit":Debit,
                        "Credit":Credit,
                        "IsActive":IsActive,
                        "Action":Action,
                        "CreatedUserID":CreatedUserID,
                        "CreatedDate":today,
                        "UpdatedDate":today,
                    })

            else:
                str_count += str(count+1)+str(",")
                message = 'Party Name is exists in Sheet line number:' + \
                    str(str_count)
                print(total, str_count)
            if Country:
                if models.Country.objects.filter(Country_Name__iexact=Country).exists():
                    Country = models.Country.objects.get(
                        Country_Name__iexact=Country).id
                else:
                    Country_create = models.Country.objects.create(
                        Country_Name=Country)
                    Country = Country_create.id
            
            if State:
                if models.State.objects.filter(Country_id=Country,Name__iexact=State).exists():
                    State = models.State.objects.get(
                        Country_id=Country, Name__iexact=State).id
                else:
                    State_create = models.State.objects.create(
                        Country_id=Country, Name=State)
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

            party_list.append({
                "PartyID":int(PartyID)+count,
                "PartyType":PartyType,
                "LedgerID":LedgerID,
                "PartyCode":PartyCode,
                "PartyName":PartyName,
                "DisplayName":DisplayName,
                "Address1":Address1,
                "Address2":Address2,
                "City":City,
                "State":State,
                "Country":Country,
                "PostalCode":PostalCode,
                "OfficePhone":OfficePhone,
                "WorkPhone":WorkPhone,
                "Mobile":Mobile,
                "WebURL":WebURL,
                "Email":Email,
                "IsBillwiseApplicable":IsBillwiseApplicable,
                "CreditPeriod":CreditPeriod,
                "CreditLimit":CreditLimit,
                "RouteID":RouteID,
                "VATNumber":VATNumber,
                "GSTNumber":GSTNumber,
                "Tax1Number":Tax1Number,
                "Tax2Number":Tax2Number,
                "Tax3Number":Tax3Number,
                "PanNumber":PanNumber,
                "CRNo":CRNo,
                "BankName1":BankName1,
                "AccountName1":AccountName1,
                "AccountNo1":AccountNo1,
                "IBANOrIFSCCode1":IBANOrIFSCCode1,
                "BankName2":BankName2,
                "AccountName2":AccountName2,
                "AccountNo2":AccountNo2,
                "IBANOrIFSCCode2":IBANOrIFSCCode2,
                "IsActive":IsActive,
                "Action":Action,
                "CreatedUserID":CreatedUserID,
                "CreatedDate":today,
                "UpdatedDate":today,
                "OpeningBalance":OpeningBalance,
                "PriceCategoryID":1,
                "CurrencyID":0,
                "FirstName":"",
                "LastName":"",
                "Attention":"",
                "Attention_Shipping":"",
                "Address1_Shipping":"",
                "Address2_Shipping":"",
                "State_Shipping":"",
                "Country_Shipping":"",
                "City_Shipping":"",
                "PostalCode_Shipping":"",
                "Phone_Shipping":"",
                
            })
            party_list_log.append({
                "TransactionID":int(PartyID)+count,
                "PartyType":PartyType,
                "LedgerID":LedgerID,
                "PartyCode":PartyCode,
                "PartyName":PartyName,
                "DisplayName":DisplayName,
                "Address1":Address1,
                "Address2":Address2,
                "City":City,
                "State":State,
                "Country":Country,
                "PostalCode":PostalCode,
                "OfficePhone":OfficePhone,
                "WorkPhone":WorkPhone,
                "Mobile":Mobile,
                "WebURL":WebURL,
                "Email":Email,
                "IsBillwiseApplicable":IsBillwiseApplicable,
                "CreditPeriod":CreditPeriod,
                "CreditLimit":CreditLimit,
                "RouteID":RouteID,
                "VATNumber":VATNumber,
                "GSTNumber":GSTNumber,
                "Tax1Number":Tax1Number,
                "Tax2Number":Tax2Number,
                "Tax3Number":Tax3Number,
                "PanNumber":PanNumber,
                "CRNo":CRNo,
                "BankName1":BankName1,
                "AccountName1":AccountName1,
                "AccountNo1":AccountNo1,
                "IBANOrIFSCCode1":IBANOrIFSCCode1,
                "BankName2":BankName2,
                "AccountName2":AccountName2,
                "AccountNo2":AccountNo2,
                "IBANOrIFSCCode2":IBANOrIFSCCode2,
                "IsActive":IsActive,
                "Action":Action,
                "CreatedUserID":CreatedUserID,
                "CreatedDate":today,
                "UpdatedDate":today,
                "OpeningBalance":OpeningBalance,
                
                "PriceCategoryID":1,
                "CurrencyID":0,
                "FirstName":"",
                "LastName":"",
                "Attention":"",
                "Attention_Shipping":"",
                "Address1_Shipping":"",
                "Address2_Shipping":"",
                "State_Shipping":"",
                "Country_Shipping":"",
                "City_Shipping":"",
                "PostalCode_Shipping":"",
                "Phone_Shipping":"",
                
            })
            count+=1
        
        else:
            str_count += str(count+1)+str(",")
            message = 'Party Name is exists in Sheet line number:' + \
                str(str_count)
            print(total, str_count)
        progress_recorder.set_progress(
            int(count), int(total), description="hello world")

    
    bulk_accountLedger = models.AccountLedger.objects.bulk_create([
        models.AccountLedger(
        **{key:value for key, value in i.items()},
        BranchID=BranchID,
        CompanyID=CompanyID,
        )
        for i in accoundLedger_list
    ])
    bulk_accountLedger_log = models.AccountLedger_Log.objects.bulk_create([
        models.AccountLedger_Log(
        **{key:value for key, value in i.items()},
        BranchID=BranchID,
        CompanyID=CompanyID,
        )
        for i in accoundLedger_list_log
    ])
    bulk_ledgerPosting = models.LedgerPosting.objects.bulk_create([
        models.LedgerPosting(
        **{key:value for key, value in i.items()},
        BranchID=BranchID,
        CompanyID=CompanyID,
        )
        for i in ledgerPosting_list
    ])
    bulk_ledgerPosting_log = models.LedgerPosting_Log.objects.bulk_create([
        models.LedgerPosting_Log(
        **{key:value for key, value in i.items()},
        BranchID=BranchID,
        CompanyID=CompanyID,
        )
        for i in ledgerPosting_list_log
    ])
    bulk_party = models.Parties.objects.bulk_create([
        models.Parties(
        **{key:value for key, value in i.items()},
        BranchID=BranchID,
        CompanyID=CompanyID,
        )
        for i in party_list
    ])
    bulk_party_log = models.Parties_Log.objects.bulk_create([
        models.Parties_Log(
        **{key:value for key, value in i.items()},
        BranchID=BranchID,
        CompanyID=CompanyID,
        )
        for i in party_list_log
    ])
    return message.format(total)
