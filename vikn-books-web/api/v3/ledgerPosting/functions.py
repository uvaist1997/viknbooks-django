import string
import random
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Max
from json import loads, dumps



def generate_serializer_errors(args):
    message = ""
    for key, values in args.items():
        error_message = ""
        for value in values:
            error_message += value + ","
        error_message = error_message[:-1]

        message += "%s : %s | " %(key,error_message)
    return message[:-3]


def get_auto_id(model,BranchID,DataBase):
    LedgerPostingID = 1
    max_value = None
    LedgerPostingID = None
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('LedgerPostingID'))
    

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('LedgerPostingID'))
        

        if max_value:
            max_ledgerPostingId = max_value.get('LedgerPostingID__max', 0)
            
            LedgerPostingID = max_ledgerPostingId + 1
            
        else:
            LedgerPostingID = 1

   
    return LedgerPostingID



def convertOrderdDict(input_ordered_dict):
    return loads(dumps(input_ordered_dict))



def get_VoucherName(VoucherType):
    if VoucherType == 'SI':
        VoucherName = 'Sales Invoice'
    elif VoucherType == 'SR':
        VoucherName = 'Sales Return'
    elif VoucherType == 'SO':
        VoucherName = 'Sales Order'
    elif VoucherType == 'PI':
        VoucherName = 'Purchase Invoice'
    elif VoucherType == 'PR':
        VoucherName = 'Purchase Return'
    elif VoucherType == 'PO':
        VoucherName = 'Purchase Order'
    elif VoucherType == 'OS':
        VoucherName = 'Opening Stock'
    elif VoucherType == 'JL':
        VoucherName = 'Journal'
    elif VoucherType == 'CP':
        VoucherName = 'Cash Payment'
    elif VoucherType == 'BP':
        VoucherName = 'Bank Payment'
    elif VoucherType == 'CR':
        VoucherName = 'Cash Receipt'
    elif VoucherType == 'BR':
        VoucherName = 'Bank Receipt'
    elif VoucherType == 'ST':
        VoucherName = 'Stock Transfer'
    elif VoucherType == 'AG':
        VoucherName = 'Account Group'
    elif VoucherType == 'LOB':
        VoucherName = 'Opening Balance'

    return VoucherName