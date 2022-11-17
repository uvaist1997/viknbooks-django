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
    DamageStockMasterID = 1
    max_value = None
    DamageStockMasterID = None
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.all().aggregate(Max('DamageStockMasterID'))
    

    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID).aggregate(Max('DamageStockMasterID'))
        

        if max_value:
            max_damageStockMasterId = max_value.get('DamageStockMasterID__max', 0)
            
            DamageStockMasterID = max_damageStockMasterId + 1
            
        else:
            DamageStockMasterID = 1

    return DamageStockMasterID



def get_auto_idMaster(model,BranchID):
    DamageStockMasterID = 1
    max_value = None
    DamageStockMasterID = None
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.all().aggregate(Max('DamageStockMasterID'))
    

    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID).aggregate(Max('DamageStockMasterID'))
        

        if max_value:
            max_damageStockMasterId = max_value.get('DamageStockMasterID__max', 0)
            
            DamageStockMasterID = max_damageStockMasterId + 1
            
        else:
            DamageStockMasterID = 1

    return DamageStockMasterID