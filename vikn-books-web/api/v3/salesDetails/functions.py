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
    SalesDetailsID = 1
    max_value = None
    SalesDetailsID = None
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.all().aggregate(Max('SalesDetailsID'))
    

    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID).aggregate(Max('SalesDetailsID'))
        

    if max_value:
        max_saleDetailId = max_value.get('SalesDetailsID__max', 0)
        
        SalesDetailsID = max_saleDetailId + 1
        
    else:
        SalesDetailsID = 1

    
    # if model.objects.filter(BrandID=BrandID).exists():
    #     BrandID = 1
            

    return SalesDetailsID