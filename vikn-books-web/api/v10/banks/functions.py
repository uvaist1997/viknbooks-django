import random
import re
import string
from decimal import Decimal

from django.db.models import Max
from django.http import HttpResponse


def generate_serializer_errors(args):
    message = ""
    for key, values in args.items():
        error_message = ""
        for value in values:
            error_message += value + ","
        error_message = error_message[:-1]

        message += "%s : %s | " % (key, error_message)
    return message[:-3]


def get_auto_Bankid(model, BranchID, CompanyID):
    BankID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.filter(CompanyID=CompanyID).aggregate(Max("BankID"))
    if model.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():

        max_value = model.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID
        ).aggregate(Max("BankID"))

        if max_value:
            max_bankId = max_value.get("BankID__max", 0)

            BankID = max_bankId + 1

        else:
            BankID = 1

    return BankID


# def get_BankCode(model, BranchID, CompanyID):
#     latest_LedgerCode = model.objects.filter(
#         BranchID=BranchID, CompanyID=CompanyID
#     ).order_by("-id")[:1]
#     if latest_LedgerCode:
#         for lc in latest_LedgerCode:
#             LedgerCode = lc.LedgerCode
#             temp = re.compile("([a-zA-Z]+)([0-9]+)")
#             res = temp.match(LedgerCode).groups()
#             code, number = res
#             number = int(number) + 1
#             LedgerCode = str(code) + str(number)
#     else:
#         LedgerCode = "BK1"
#     return LedgerCode


def get_BankCode(model, BranchID, CompanyID):
    LedgerCode = "AL1"
    if model.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
        latest_LedgerCode = model.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID).order_by("LedgerCode").last()
        LedgerCode = latest_LedgerCode.LedgerCode
        if not LedgerCode.isdecimal():
            temp = re.compile("([a-zA-Z]+)([0-9]+)")
            if temp.match(LedgerCode):
                res = temp.match(LedgerCode).groups()
                code, number = res
                number = int(number) + 1
                LedgerCode = str(code) + str(number)
            else:
                if LedgerCode == '':
                    LedgerCode = "0"
                if re.findall(r'\d+', LedgerCode):
                    LedgerCodeNumber = re.findall(r'\d+', LedgerCode)[-1]
                    rest = LedgerCode.split(LedgerCodeNumber)[0]
                    LedgerCode = str(int(LedgerCodeNumber) +
                                     1).zfill(len(LedgerCodeNumber))
                    LedgerCode = str(rest) + str(LedgerCode)
                else:
                    LedgerCode = str(LedgerCode) + str(1)
        else:
            code = str(float(LedgerCode) + 1)
            code = code.rstrip('0').rstrip('.') if '.' in code else code
            LedgerCode = code.zfill(len(LedgerCode))
    return LedgerCode
