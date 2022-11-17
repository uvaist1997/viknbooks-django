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


def get_auto_id(model,BranchID,CompanyID):
    PartyID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('PartyID'))
    
    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('PartyID'))
        
        if max_value:
            max_partyId = max_value.get('PartyID__max', 0)
            
            PartyID = max_partyId + 1
            
        else:
            PartyID = 1


    return PartyID



# def get_auto_idLedger(model,BranchID,CompanyID):
#     LedgerID = 1
#     # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
#     latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('LedgerID'))
#     if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
#         max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('LedgerID'))
#         if max_value:
#             max_ledgerId = max_value.get('LedgerID__max', 0)
#             LedgerID = max_ledgerId + 1
#         else:
#             LedgerID = 1
#     return LedgerID

def get_auto_idLedger(AccountLedger, BranchID, CompanyID):
    LedgerID = 1
    if AccountLedger.objects.filter(CompanyID=CompanyID).exists():
        last_ins = AccountLedger.objects.filter(CompanyID=CompanyID).order_by('LedgerID').last()
        current_LedgerID = last_ins.LedgerID
        LedgerID = int(current_LedgerID) + 1
    return LedgerID


def get_PartyCode(model,BranchID,CompanyID, PartyType):

    if PartyType == "customer":
        if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID,PartyType=PartyType).exists():
            latest_PartyCode =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID,PartyType=PartyType).order_by("PartyID").last()
            
            PartyCode = latest_PartyCode.PartyCode
            temp = re.compile("([a-zA-Z]+)([0-9]+)") 
            res = temp.match(PartyCode).groups()

            code , number = res

            number = int(number) + 1
            PartyCode = str(code) + str(number)
        else:
            PartyCode = "CMR1"
        return PartyCode
    elif PartyType == "supplier":
        if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID,PartyType=PartyType).exists():
            latest_PartyCode =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID,PartyType=PartyType).order_by("PartyID").last()
            PartyCode = latest_PartyCode.PartyCode

            temp = re.compile("([a-zA-Z]+)([0-9]+)") 
            res = temp.match(PartyCode).groups()

            code , number = res

            number = int(number) + 1
            PartyCode = str(code) + str(number)
        else:
            PartyCode = "SLR1"
        return PartyCode