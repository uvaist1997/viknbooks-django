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


def get_auto_id(model,BranchID,DataBase):
    PurchaseOrderDetailsID = 1
    max_value = None
    PurchaseOrderDetailsID = None
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.all().aggregate(Max('PurchaseOrderDetailsID'))
    

    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID).aggregate(Max('PurchaseOrderDetailsID'))
        

    if max_value:
        max_purchaseOrderDetailsId = max_value.get('PurchaseOrderDetailsID__max', 0)
        
        PurchaseOrderDetailsID = max_purchaseOrderDetailsId + 1
        
    else:
        PurchaseOrderDetailsID = 1

    
    # if model.objects.filter(BrandID=BrandID).exists():
    #     BrandID = 1
            

    return PurchaseOrderDetailsID