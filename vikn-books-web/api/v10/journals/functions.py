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
    JournalMasterID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('JournalMasterID'))
    

    if model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).exists():
        max_value =  model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).aggregate(Max('JournalMasterID'))
        

        if max_value:
            max_journalMasterId = max_value.get('JournalMasterID__max', 0)
            
            JournalMasterID = max_journalMasterId + 1
            
        else:
            JournalMasterID = 1
                

    return JournalMasterID





def get_auto_id(model,BranchID,CompanyID):
    JournalDetailsID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('JournalDetailsID'))
    

    if model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).exists():
        max_value =  model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).aggregate(Max('JournalDetailsID'))
        
        if max_value:
            max_journalDetailsId = max_value.get('JournalDetailsID__max', 0)
            
            JournalDetailsID = max_journalDetailsId + 1

    return JournalDetailsID