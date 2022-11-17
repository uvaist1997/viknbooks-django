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


def get_auto_id(model,BranchID):
    ReceiptMasterID = 1
    max_value = None
    ReceiptMasterID = None
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.all().aggregate(Max('ReceiptMasterID'))
    

    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID).aggregate(Max('ReceiptMasterID'))
        

    if max_value:
        max_receiptMasterId = max_value.get('ReceiptMasterID__max', 0)
        
        ReceiptMasterID = max_receiptMasterId + 1
        
    else:
        ReceiptMasterID = 1

    
    # if model.objects.filter(BrandID=BrandID).exists():
    #     BrandID = 1
            

    return ReceiptMasterID