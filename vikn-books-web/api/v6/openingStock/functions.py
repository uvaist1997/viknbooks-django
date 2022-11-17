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
    OpeningStockMasterID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('OpeningStockMasterID'))
    

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('OpeningStockMasterID'))
        
        if max_value:
            max_openingStockMasterId = max_value.get('OpeningStockMasterID__max', 0)
            
            OpeningStockMasterID = max_openingStockMasterId + 1
            
        else:
            OpeningStockMasterID = 1

    return OpeningStockMasterID



def get_auto_id(model,BranchID,CompanyID):
    OpeningStockDetailsID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('OpeningStockDetailsID'))
    

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('OpeningStockDetailsID'))
        

        if max_value:
            max_openingStockDetailsId = max_value.get('OpeningStockDetailsID__max', 0)
            
            OpeningStockDetailsID = max_openingStockDetailsId + 1
            
        else:
            OpeningStockDetailsID = 1


    return OpeningStockDetailsID