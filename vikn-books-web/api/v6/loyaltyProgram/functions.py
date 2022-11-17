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
    LoyaltyProgramID = 1
    
    if model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).exists():
        max_value =  model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).aggregate(Max('LoyaltyProgramID')) 

        if max_value:
            max_loyaltyProgramId = max_value.get('LoyaltyProgramID__max', 0)
            
            LoyaltyProgramID = max_loyaltyProgramId + 1
            
        else:
            LoyaltyProgramID = 1

    return LoyaltyProgramID


def get_point_auto_id(model,BranchID,CompanyID):
    LoyaltyPointID = 1
    
    if model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).exists():
        max_value =  model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).aggregate(Max('LoyaltyPointID')) 

        if max_value:
            max_loyaltyPointId = max_value.get('LoyaltyPointID__max', 0)
            
            LoyaltyPointID = max_loyaltyPointId + 1
            
        else:
            LoyaltyPointID = 1

    return LoyaltyPointID


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