from datetime import datetime
import string
import random
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Max
from api.v9.accountLedgers import functions as accoundLedger_function

from brands.models import AccountLedger, Branch, BranchSettings


def generate_serializer_errors(args):
    message = ""
    for key, values in args.items():
        error_message = ""
        for value in values:
            error_message += value + ","
        error_message = error_message[:-1]

        message += "%s : %s | " % (key, error_message)
    return message[:-3]


def get_auto_id(model, CompanyID):
    BranchID = 1
    latest_auto_id = model.objects.filter(
        CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    if latest_auto_id:
        for auto in latest_auto_id:
            BranchID = auto.BranchID + 1
    return BranchID


def get_ledger_instance(LedgerID, BranchID, CompanyID):
    instance = None
    if AccountLedger.objects.filter(LedgerID=LedgerID, CompanyID=CompanyID).exists():
        instance = AccountLedger.objects.get(
            LedgerID=LedgerID, CompanyID=CompanyID)
    return instance


def get_pk_ledger_instance(pk, CompanyID):
    instance = None
    if AccountLedger.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = AccountLedger.objects.get(
            pk=pk, CompanyID=CompanyID)
    return instance


def create_ledger_instance(dic, branch_instance, CompanyID, CreatedUserID):
    LedgerID = accoundLedger_function.get_auto_id(
        AccountLedger, branch_instance.BranchID, CompanyID)
    LedgerCode = accoundLedger_function.get_LedgerCode(
        AccountLedger, branch_instance.BranchID, CompanyID)
    today = datetime.now()
    ledger_name = str(branch_instance.BranchName) + \
        str(" ")+str(dic['LedgerName'])

    instance = AccountLedger.objects.create(
        LedgerID=LedgerID,
        BranchID=branch_instance.BranchID,
        LedgerName=ledger_name,
        LedgerCode=LedgerCode,
        AccountGroupUnder=dic['AccountGroupUnder'],
        OpeningBalance=dic['OpeningBalance'],
        CrOrDr=dic['CrOrDr'],
        Notes=dic['Notes'],
        IsActive=True,
        IsDefault=True,
        CreatedDate=today,
        UpdatedDate=today,
        Action="A",
        CreatedUserID=CreatedUserID,
        CompanyID=CompanyID,
        Balance=dic['OpeningBalance']
    )
    return instance


def max_id(CompanyID):
    branch_settings_id = 0
    if BranchSettings.objects.filter(CompanyID=CompanyID).exists():
        branch_settings = BranchSettings.objects.filter(
            CompanyID=CompanyID).aggregate(Max('BranchSettingsID'))
        branch_settings_id = branch_settings.get(
            'BranchSettingsID__max', 0)
    print(branch_settings_id, 'branch_settingsbranch_settings')
    branch_settings_id += 1
    return branch_settings_id


def create_or_update_branch_settings(CompanyID, SettingsType, SettingsValue, User):
    today = datetime.now()
    if not BranchSettings.objects.filter(CompanyID=CompanyID, SettingsType=SettingsType).exists():
        Action = "A"
        BranchSettings.objects.create(
            CompanyID=CompanyID,
            BranchSettingsID=max_id(CompanyID),
            SettingsType=SettingsType,
            SettingsValue=SettingsValue,
            # BranchID=1, GroupName=GroupName,
            UpdatedDate=today,
            CreatedUserID=User,
            Action=Action
        )
    else:
        Action = "M"
        BranchSettings.objects.filter(
            CompanyID=CompanyID,
            SettingsType=SettingsType
        ).update(
            SettingsValue=SettingsValue,
            UpdatedDate=today,
            CreatedUserID=User,
            Action=Action
        )


def get_branch_settings(CompanyID, SettingsType):
    settings_value = False
    if(SettingsType == "AllowNegativeStockSales"):
        settings_value = True
    if BranchSettings.objects.filter(CompanyID=CompanyID, SettingsType=SettingsType).exists():
        settings_value = BranchSettings.objects.get(
            CompanyID=CompanyID, SettingsType=SettingsType).SettingsValue
        if settings_value == "True" or settings_value == "true":
            settings_value = True
        else:
            settings_value = False
    return settings_value
