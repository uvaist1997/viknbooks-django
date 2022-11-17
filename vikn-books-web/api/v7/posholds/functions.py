import string
import random
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Max
from brands.models import POS_User
from random import randint
from brands import models as table
from django.contrib.auth.models import User
import re,sys, os


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
    return POSHoldDetailsID


def get_pin_no(CompanyID,BranchID):
    range_start = 10**(6-1)
    range_end = (10**6)-1
    PinNo = randint(range_start, range_end)
    if POS_User.objects.filter(CompanyID=CompanyID,BranchID=BranchID,PinNo=PinNo).exists():
        get_pin_no(CompanyID,BranchID)
    return PinNo


def get_InvoiceNo(OldVoucherNo):
    InvoiceNo = 1
    if not OldVoucherNo.isdecimal():
        res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
        num = res.group(0)
        InvoiceNo = int(num)
    return InvoiceNo


def get_VoucherNoForPOS(CompanyID,BranchID,UserID,VoucherType):
    old_invoiceNo = 0
    seperator = ""
    PreFix = VoucherType
    user_count = table.UserTable.objects.filter(CompanyID=CompanyID).count()
    if user_count == 1:
        if table.VoucherNoGenerateTable.objects.filter(CompanyID=CompanyID,UserID=UserID,VoucherType=VoucherType).exists():
            voucher = table.VoucherNoGenerateTable.objects.filter(CompanyID=CompanyID,UserID=UserID,VoucherType=VoucherType).first()
            old_invoiceNo =  voucher.LastInvoiceNo
            PreFix = voucher.PreFix
            seperator = voucher.Seperater
    else:
        user_name = User.objects.get(id=UserID).username
        PreFix = user_name[0:3]
        if table.VoucherNoGenerateTable.objects.filter(CompanyID=CompanyID,UserID=UserID,VoucherType=VoucherType).exists():
            voucher = table.VoucherNoGenerateTable.objects.filter(CompanyID=CompanyID,UserID=UserID,VoucherType=VoucherType).first()
            old_invoiceNo =  voucher.LastInvoiceNo
            PreFix = voucher.PreFix
            seperator = voucher.Seperater
            
    new_invoiceNo = old_invoiceNo + 1
    new_VoucherNo = PreFix + str(seperator) + str(new_invoiceNo) 
    return new_VoucherNo




def get_TokenNo(CompanyID,BranchID):
    TokenNo = "001"
    types = ["Online","TakeAway","Car","Dining"]
    if table.SalesOrderMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Type__in=types).exists():
        last_order = table.SalesOrderMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID,Type__in=types).first()
        last_token = int(last_order.TokenNumber)

        TokenNo = "{0:03}".format(last_token + 1)
    return TokenNo



def get_KitchenID(model,BranchID):
    KitchenID = 1
    max_value = None
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.all().aggregate(Max('KitchenID'))
    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID).aggregate(Max('KitchenID'))
    if max_value:
        max_KitchenID = max_value.get('KitchenID__max', 0)
        KitchenID = max_KitchenID + 1
    return KitchenID