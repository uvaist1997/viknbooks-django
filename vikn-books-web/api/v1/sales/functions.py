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
    SalesMasterID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('SalesMasterID'))

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('SalesMasterID'))
        

        if max_value:
            max_salesMasterId = max_value.get('SalesMasterID__max', 0)
            
            SalesMasterID = max_salesMasterId + 1
            
        else:
            SalesMasterID = 1


    return SalesMasterID





def get_auto_id(model,BranchID,CompanyID):
    SalesDetailsID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('SalesDetailsID'))
    

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('SalesDetailsID'))
        

        if max_value:
            max_salesDetailsId = max_value.get('SalesDetailsID__max', 0)
            
            SalesDetailsID = max_salesDetailsId + 1
            
        else:
            SalesDetailsID = 1


    return SalesDetailsID


def get_auto_stockPostid(model,BranchID,CompanyID):
    StockPostingID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('StockPostingID'))
    

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('StockPostingID'))
        

        if max_value:
            max_stockPostingId = max_value.get('StockPostingID__max', 0)
            
            StockPostingID = max_stockPostingId + 1
            
        else:
            StockPostingID = 1


    return StockPostingID



def get_auto_VoucherNo(model,BranchID,CompanyID):
    VoucherNo = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('VoucherNo'))
    

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('VoucherNo'))
        

        if max_value:
            max_VoucherNo = max_value.get('VoucherNo__max', 0)
            
            VoucherNo = max_VoucherNo + 1
            
        else:
            VoucherNo = 1

    return VoucherNo
