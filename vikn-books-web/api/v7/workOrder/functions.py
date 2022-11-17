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
    WorkOrderMasterID = 1
    
    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('WorkOrderMasterID'))
        

        if max_value:
            max_WorkOrderMasterID = max_value.get('WorkOrderMasterID__max', 0)
            
            WorkOrderMasterID = max_WorkOrderMasterID + 1
            
        else:
            WorkOrderMasterID = 1
     

    return WorkOrderMasterID



def get_auto_id(model,BranchID,CompanyID):
    WorkOrderDetailsID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('WorkOrderDetailsID'))
    

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('WorkOrderDetailsID'))
        

        if max_value:
            max_WorkOrderDetailsID = max_value.get('WorkOrderDetailsID__max', 0)
            
            WorkOrderDetailsID = max_WorkOrderDetailsID + 1
            
        else:
            WorkOrderDetailsID = 1

    return WorkOrderDetailsID



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