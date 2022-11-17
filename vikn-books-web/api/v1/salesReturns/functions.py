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
    SalesReturnMasterID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('SalesReturnMasterID'))
    

    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('SalesReturnMasterID'))
        
        if max_value:
            max_salesReturnMasterId = max_value.get('SalesReturnMasterID__max', 0)
            if max_salesReturnMasterId:
                SalesReturnMasterID = max_salesReturnMasterId + 1
     
    return SalesReturnMasterID


def get_auto_id(model,BranchID,CompanyID):
    SalesReturnDetailsID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('SalesReturnDetailsID'))
    
    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('SalesReturnDetailsID'))
        
        if max_value:
            max_salesReturnDetailsId = max_value.get('SalesReturnDetailsID__max', 0)
            
            SalesReturnDetailsID = max_salesReturnDetailsId + 1
        else:
            SalesReturnDetailsID = 1

    return SalesReturnDetailsID