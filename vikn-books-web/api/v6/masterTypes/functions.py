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


def get_auto_id(model,BranchID,DataBase):
    MasterTypeID = 1
    max_value = None
    MasterTypeID = None
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('MasterTypeID'))
    

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('MasterTypeID'))
        

        if max_value:
            max_masterTypeId = max_value.get('MasterTypeID__max', 0)
            
            MasterTypeID = max_masterTypeId + 1
        else:
            MasterTypeID = 1

    return MasterTypeID