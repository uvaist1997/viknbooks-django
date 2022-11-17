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
    FlavourID = 1
    # latest_auto_id =  model.objects.filter().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('FlavourID'))
    

    if model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).exists():
        max_value =  model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).aggregate(Max('FlavourID'))
        

        if max_value:
            max_falvourId = max_value.get('FlavourID__max', 0)
            
            FlavourID = max_falvourId + 1
            
        else:
            FlavourID = 1


    return FlavourID

def get_auto_id_flavour(model,BranchID):
    FlavourID = 1
    # latest_auto_id =  model.objects.filter().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('FlavourID'))
    

    if model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).exists():
        max_value =  model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).aggregate(Max('FlavourID'))
        

        if max_value:
            max_falvourId = max_value.get('FlavourID__max', 0)
            
            FlavourID = max_falvourId + 1
            
        else:
            FlavourID = 1


    return FlavourID