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


def get_auto_idMaster(model,BranchID):
    POSHoldMasterID = 1
    max_value = None
    POSHoldMasterID = None
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.all().aggregate(Max('POSHoldMasterID'))
    

    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID).aggregate(Max('POSHoldMasterID'))
        

    if max_value:
        max_posHoldMasterId = max_value.get('POSHoldMasterID__max', 0)
        
        POSHoldMasterID = max_posHoldMasterId + 1
        
    else:
        POSHoldMasterID = 1

    
    # if model.objects.filter(BrandID=BrandID).exists():
    #     BrandID = 1
            
    POSHoldMasterID
    return POSHoldMasterID





def get_auto_id(model,BranchID):
    POSHoldDetailsID = 1
    max_value = None
    POSHoldDetailsID = None
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.all().aggregate(Max('POSHoldDetailsID'))
    

    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID).aggregate(Max('POSHoldDetailsID'))
        

    if max_value:
        max_posHoldDetailsId = max_value.get('POSHoldDetailsID__max', 0)
        
        POSHoldDetailsID = max_posHoldDetailsId + 1
        
    else:
        POSHoldDetailsID = 1

    
    # if model.objects.filter(BrandID=BrandID).exists():
    #     BrandID = 1
            

    return POSHoldDetailsID