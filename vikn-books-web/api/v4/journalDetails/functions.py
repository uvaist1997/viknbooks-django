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
    JournalDetailsID = 1
    max_value = None
    JournalDetailsID = None
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.all().aggregate(Max('JournalDetailsID'))
    

    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID).aggregate(Max('JournalDetailsID'))
        

        if max_value:
            max_journalDetailsId = max_value.get('JournalDetailsID__max', 0)
            
            JournalDetailsID = max_journalDetailsId + 1
            
        else:
            JournalDetailsID = 1


    return JournalDetailsID