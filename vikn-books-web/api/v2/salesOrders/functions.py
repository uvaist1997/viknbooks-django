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


def get_auto_idMaster(model,BranchID,DataBase):

    SalesOrderMasterID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.all().aggregate(Max('SalesOrderMasterID'))
    

    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID).aggregate(Max('SalesOrderMasterID'))
        

        if max_value:
            max_salesOrderMasterId = max_value.get('SalesOrderMasterID__max', 0)
            
            SalesOrderMasterID = max_salesOrderMasterId + 1
            
        else:
            SalesOrderMasterID = 1

    return SalesOrderMasterID





def get_auto_id(model,BranchID,DataBase):
    SalesOrderDetailsID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.all().aggregate(Max('SalesOrderDetailsID'))
    

    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID).aggregate(Max('SalesOrderDetailsID'))
        

        if max_value:
            max_salesOrderDetailsId = max_value.get('SalesOrderDetailsID__max', 0)
            
            SalesOrderDetailsID = max_salesOrderDetailsId + 1
            
        else:
            SalesOrderDetailsID = 1


    return SalesOrderDetailsID