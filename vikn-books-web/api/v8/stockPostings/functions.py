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
    StockPostingID = 1
    latest_auto_id =  model.objects.all(CompanyID=CompanyID).aggregate(Max('StockPostingID'))

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('StockPostingID'))
        if max_value:
            max_stockPostingId = max_value.get('StockPostingID__max', 0)
            
            StockPostingID = max_stockPostingId + 1
            
        else:
            StockPostingID = 1

    return StockPostingID


def get_auto_excessMasterID(model,BranchID,CompanyID):
    ExcessStockMasterID = 1
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('ExcessStockMasterID'))

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('ExcessStockMasterID'))

        if max_value:
            max_excessid = max_value.get('ExcessStockMasterID__max', 0)
            ExcessStockMasterID = max_excessid + 1

    return ExcessStockMasterID



def get_auto_excessDetailsID(model,BranchID,CompanyID):
    ExcessStockDetailsID = 1
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('ExcessStockDetailsID'))

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('ExcessStockDetailsID'))

        if max_value:
            max_excessDetailid = max_value.get('ExcessStockDetailsID__max', 0)
            ExcessStockDetailsID = max_excessDetailid + 1

    return ExcessStockDetailsID



def get_auto_shortageMasterID(model,BranchID,CompanyID):
    ShortageStockMasterID = 1
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('ShortageStockMasterID'))

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('ShortageStockMasterID'))

        if max_value:
            max_shortageid = max_value.get('ShortageStockMasterID__max', 0)
            ShortageStockMasterID = max_shortageid + 1

    return ShortageStockMasterID



def get_auto_shortageDetailsID(model,BranchID,CompanyID):
    ShortageStockDetailsID = 1
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('ShortageStockDetailsID'))

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('ShortageStockDetailsID'))

        if max_value:
            max_shortageDetailid = max_value.get('ShortageStockDetailsID__max', 0)
            ShortageStockDetailsID = max_shortageDetailid + 1

    return ShortageStockDetailsID



def get_auto_damageMasterID(model,BranchID,CompanyID):
    DamageStockMasterID = 1
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('DamageStockMasterID'))

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('DamageStockMasterID'))

        if max_value:
            max_damageid = max_value.get('DamageStockMasterID__max', 0)
            DamageStockMasterID = max_damageid + 1

    return DamageStockMasterID



def get_auto_damageDetailsID(model,BranchID,CompanyID):
    DamageStockDetailsID = 1
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('DamageStockDetailsID'))

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('DamageStockDetailsID'))

        if max_value:
            max_damageDetailid = max_value.get('DamageStockDetailsID__max', 0)
            DamageStockDetailsID = max_damageDetailid + 1

    return DamageStockDetailsID



def get_auto_usedMasterID(model,BranchID,CompanyID):
    UsedStockMasterID = 1
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('UsedStockMasterID'))

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('UsedStockMasterID'))

        if max_value:
            max_usedid = max_value.get('UsedStockMasterID__max', 0)
            UsedStockMasterID = max_usedid + 1

    return UsedStockMasterID



def get_auto_usedDetailsID(model,BranchID,CompanyID):
    UsedStockDetailsID = 1
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('UsedStockDetailsID'))

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('UsedStockDetailsID'))

        if max_value:
            max_usedDetailid = max_value.get('UsedStockDetailsID__max', 0)
            UsedStockDetailsID = max_usedDetailid + 1

    return UsedStockDetailsID