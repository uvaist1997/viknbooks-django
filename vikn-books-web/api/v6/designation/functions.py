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
    DesignationID = 1
    
    if model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).exists():
        max_value =  model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).aggregate(Max('DesignationID')) 

        if max_value:
            max_designationId = max_value.get('DesignationID__max', 0)
            
            DesignationID = max_designationId + 1
            
        else:
            DesignationID = 1

    return DesignationID


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