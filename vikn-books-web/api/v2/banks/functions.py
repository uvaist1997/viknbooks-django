import string
import random
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Max
import re



def generate_serializer_errors(args):
    message = ""
    for key, values in args.items():
        error_message = ""
        for value in values:
            error_message += value + ","
        error_message = error_message[:-1]

        message += "%s : %s | " %(key,error_message)
    return message[:-3]


def get_auto_Bankid(model,BranchID,CompanyID):
    BankID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('BankID'))
    if model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).exists():
        
        max_value =  model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).aggregate(Max('BankID'))

        
        if max_value:
            max_bankId = max_value.get('BankID__max', 0)
            
            BankID = max_bankId + 1
            
        else:
            BankID = 1

    return BankID


def get_BankCode(model,BranchID,CompanyID): 
    latest_LedgerCode =  model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).order_by("-id")[:1]
    if latest_LedgerCode:
        for lc in latest_LedgerCode:
            LedgerCode = lc.LedgerCode
            temp = re.compile("([a-zA-Z]+)([0-9]+)") 
            res = temp.match(LedgerCode).groups()

            code , number = res

            number = int(number) + 1
            LedgerCode = str(code) + str(number)
    else:
        LedgerCode = "BK1"
    return LedgerCode






    