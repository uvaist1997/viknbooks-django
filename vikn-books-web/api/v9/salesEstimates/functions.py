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


def get_auto_idMaster(model,BranchID, CompanyID):

    SalesEstimateMasterID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('SalesEstimateMasterID'))
    

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('SalesEstimateMasterID'))
        

        if max_value:
            max_salesEstimateMasterId = max_value.get('SalesEstimateMasterID__max', 0)
            
            SalesEstimateMasterID = max_salesEstimateMasterId + 1
            
        else:
            SalesEstimateMasterID = 1

    return SalesEstimateMasterID





def get_auto_id(model,BranchID,CompanyID):
    SalesEstimateDetailsID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('SalesEstimateDetailsID'))
    

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('SalesEstimateDetailsID'))
        

        if max_value:
            max_salesEstimateDetailsId = max_value.get('SalesEstimateDetailsID__max', 0)
            
            SalesEstimateDetailsID = max_salesEstimateDetailsId + 1
            
        else:
            SalesEstimateDetailsID = 1


    return SalesEstimateDetailsID