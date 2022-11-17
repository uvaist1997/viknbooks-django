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
    ReceiptMasterID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('ReceiptMasterID'))
    
    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('ReceiptMasterID'))
        

        if max_value:
            max_receiptMasterId = max_value.get('ReceiptMasterID__max', 0)
            
            ReceiptMasterID = max_receiptMasterId + 1
            
        else:
            ReceiptMasterID = 1
    

    return ReceiptMasterID



def get_auto_id(model,BranchID,CompanyID):
    ReceiptDetailID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID,).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('ReceiptDetailID'))
    
    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('ReceiptDetailID'))
        

        if max_value:
            max_receiptDetailId = max_value.get('ReceiptDetailID__max', 0)
            
            ReceiptDetailID = max_receiptDetailId + 1
            
        else:
            ReceiptDetailID = 1


    return ReceiptDetailID



def get_auto_VoucherNo(model,BranchID,CompanyID):
    VoucherNo = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID,).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('VoucherNo'))
    
    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('VoucherNo'))
        
        if max_value:
            max_VoucherNo = max_value.get('VoucherNo__max', 0)
            
            VoucherNo = max_VoucherNo + 1
            
        else:
            VoucherNo = 1


    return VoucherNo