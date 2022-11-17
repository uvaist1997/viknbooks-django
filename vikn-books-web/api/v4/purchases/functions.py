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
    PurchaseMasterID = 1
    
    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('PurchaseMasterID'))
        

        if max_value:
            max_purchaseMasterId = max_value.get('PurchaseMasterID__max', 0)
            
            PurchaseMasterID = max_purchaseMasterId + 1
            
        else:
            PurchaseMasterID = 1
     

    return PurchaseMasterID



def get_auto_id(model,BranchID,CompanyID):
    PurchaseDetailsID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('PurchaseDetailsID'))
    

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('PurchaseDetailsID'))
        

        if max_value:
            max_purchaseDetailsId = max_value.get('PurchaseDetailsID__max', 0)
            
            PurchaseDetailsID = max_purchaseDetailsId + 1
            
        else:
            PurchaseDetailsID = 1

    return PurchaseDetailsID



def get_auto_StockRateID(model,BranchID,CompanyID):
    StockRateID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('StockRateID'))
    

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('StockRateID'))
        

        if max_value:
            max_stockRateId = max_value.get('StockRateID__max', 0)
            
            StockRateID = max_stockRateId + 1
            
        else:
            StockRateID = 1

    return StockRateID


def get_auto_StockTransID(model,BranchID,CompanyID):
    StockTransID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('StockTransID'))
    

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('StockTransID'))
        

        if max_value:
            max_stockTransId = max_value.get('StockTransID__max', 0)
            
            StockTransID = max_stockTransId + 1
            
        else:
            StockTransID = 1


    return StockTransID