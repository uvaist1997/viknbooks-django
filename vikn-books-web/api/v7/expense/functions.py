import string
import random
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Max



def generate_serializer_errors(args):
    message = ""
    for key, values in args.items():
        error_message = ""
        for value in values:
            error_message += value + ","
        error_message = error_message[:-1]

        message += "%s : %s | " %(key,error_message)
    return message[:-3]


def get_masterID(model,BranchID,CompanyID):
    ExpenseMasterID = 1
    latest_auto_id =  model.objects.all().aggregate(Max('ExpenseMasterID'))
    if model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).exists():
        max_value =  model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).aggregate(Max('ExpenseMasterID'))
        if max_value:
            max_ExpenseMasterID = max_value.get('ExpenseMasterID__max', 0)
            ExpenseMasterID = max_ExpenseMasterID + 1
        else:
            ExpenseMasterID = 1
    return ExpenseMasterID


def get_detailID(model,BranchID,CompanyID):
    ExpenseDetailsID = 1
    latest_auto_id =  model.objects.all().aggregate(Max('ExpenseDetailsID'))
    if model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).exists():
        max_value =  model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).aggregate(Max('ExpenseDetailsID'))
        if max_value:
            max_ExpenseDetailsID = max_value.get('ExpenseDetailsID__max', 0)
            ExpenseDetailsID = max_ExpenseDetailsID + 1
        else:
            ExpenseDetailsID = 1
    return ExpenseDetailsID