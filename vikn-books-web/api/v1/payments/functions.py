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
    PaymentMasterID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('PaymentMasterID'))
    
    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('PaymentMasterID'))
        
        if max_value:
            max_paymentMasterId = max_value.get('PaymentMasterID__max', 0)
            
            PaymentMasterID = max_paymentMasterId + 1
            
        else:
            PaymentMasterID = 1


    return PaymentMasterID



def get_auto_id(model,BranchID,CompanyID):
    PaymentDetailsID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('PaymentDetailsID'))
    

    if model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        max_value =  model.objects.filter(CompanyID=CompanyID,BranchID=BranchID).aggregate(Max('PaymentDetailsID'))
        

        if max_value:
            max_paymentDetailsId = max_value.get('PaymentDetailsID__max', 0)
            
            PaymentDetailsID = max_paymentDetailsId + 1
            
        else:
            PaymentDetailsID = 1


    return PaymentDetailsID


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