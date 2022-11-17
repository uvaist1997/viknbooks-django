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


def get_auto_idMaster(model,BranchID,CompanyID):
    PurchaseReturnMasterID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('PurchaseReturnMasterID'))
    

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('PurchaseReturnMasterID'))
        

        if max_value:
            max_purchaseReturnMasterId = max_value.get('PurchaseReturnMasterID__max', 0)
            
            PurchaseReturnMasterID = max_purchaseReturnMasterId + 1
            
        else:
            PurchaseReturnMasterID = 1


    return PurchaseReturnMasterID



def get_auto_id(model,BranchID,CompanyID):
    PurchaseReturnDetailsID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('PurchaseReturnDetailsID'))
    
    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('PurchaseReturnDetailsID'))
        

        if max_value:
            max_purchaseReturnDetailsId = max_value.get('PurchaseReturnDetailsID__max', 0)
            
            PurchaseReturnDetailsID = max_purchaseReturnDetailsId + 1
            
        else:
            PurchaseReturnDetailsID = 1

    
    return PurchaseReturnDetailsID