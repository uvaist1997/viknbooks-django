import string
import random
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Max
import re

from brands.models import LedgerPosting



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
    LedgerID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('LedgerID'))
    
    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).aggregate(Max('LedgerID'))
        
        if max_value:
            max_ledgerId = max_value.get('LedgerID__max', 0)
            
            LedgerID = max_ledgerId + 1
        else:
            LedgerID = 1
    return LedgerID




def get_LedgerCode(model,BranchID,CompanyID):

    LedgerCode = "AL1"

    if model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).exists():
        latest_LedgerCode =  model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).order_by("LedgerID").last()

        LedgerCode = latest_LedgerCode.LedgerCode

        temp = re.compile("([a-zA-Z]+)([0-9]+)") 
        res = temp.match(LedgerCode).groups()

        code , number = res

        number = int(number) + 1

        LedgerCode = str(code) + str(number)

    return LedgerCode



def get_auto_LedgerPostid(model,BranchID,CompanyID):
    LedgerPostingID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    # latest_auto_id = model.objects.filter(
    #     CompanyID=CompanyID, BranchID=BranchID).aggregate(Max('LedgerPostingID'))
    if model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).exists():
        max_value =  model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).aggregate(Max('LedgerPostingID'))
        if max_value:
            max_ledgerPostingId = max_value.get('LedgerPostingID__max', 0)
            LedgerPostingID = max_ledgerPostingId + 1
        else:
            LedgerPostingID = 1
    return LedgerPostingID



def get_auto_idfor_party(model,BranchID,CompanyID):
    PartyID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('PartyID'))
    

    if model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).exists():
        max_value =  model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).aggregate(Max('PartyID'))
        

        if max_value:
            max_partyId = max_value.get('PartyID__max', 0)
            
            PartyID = max_partyId + 1
            
        else:
            PartyID = 1


    return PartyID
    
    
    
def get_auto_LedgerPostid1(model,BranchID,CompanyID):
    LedgerPostingID = 1
    if LedgerPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        LedgerPostingID = LedgerPosting.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID).first().LedgerPostingID
    return LedgerPostingID