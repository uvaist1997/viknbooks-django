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


def get_auto_id(model,BranchID,CompanyID):
    RelieveRequestID = 1
    
    if model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).exists():
        max_value =  model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).aggregate(Max('RelieveRequestID')) 

        if max_value:
            max_relieveRequestId = max_value.get('RelieveRequestID__max', 0)
            
            RelieveRequestID = max_relieveRequestId + 1
            
        else:
            RelieveRequestID = 1

    return RelieveRequestID


def get_auto_DepartmentID(model,BranchID,CompanyID):
    DepartmentID = 1
    
    if model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).exists():
        max_value =  model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).aggregate(Max('DepartmentID')) 

        if max_value:
            max_DepartmentID = max_value.get('DepartmentID__max', 0)
            
            DepartmentID = max_DepartmentID + 1
            
        else:
            DepartmentID = 1

    return DepartmentID