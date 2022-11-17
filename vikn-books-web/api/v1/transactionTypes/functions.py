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


def get_auto_id(model,BranchID,CompanyID):
    TransactionTypesID = 1
    max_value = None
    TransactionTypesID = None
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('TransactionTypesID'))
    

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('TransactionTypesID'))
        
    if max_value:
        max_transactionTypeId = max_value.get('TransactionTypesID__max', 0)
        TransactionTypesID = max_transactionTypeId + 1
    else:
        TransactionTypesID = 1
    # if model.objects.filter(BrandID=BrandID).exists():
    #     BrandID = 1
    return TransactionTypesID