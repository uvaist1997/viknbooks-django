import string
import random
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Max
from brands.models import  ExcessStockMaster, ShortageStockMaster
import re

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
    StockAdjustmentMasterID = 1
    max_value = None
    StockAdjustmentMasterID = None
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.all().aggregate(Max('StockAdjustmentMasterID'))
    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID).aggregate(Max('StockAdjustmentMasterID'))
    if max_value:
        max_stockAdjustmentMasterId = max_value.get('StockAdjustmentMasterID__max', 0)
        StockAdjustmentMasterID = max_stockAdjustmentMasterId + 1
    else:
        StockAdjustmentMasterID = 1
    return StockAdjustmentMasterID





def get_auto_id(model,BranchID):
    StockAdjustmentDetailsID = 1
    max_value = None
    StockAdjustmentDetailsID = None
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.all().aggregate(Max('StockAdjustmentDetailsID'))
    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID).aggregate(Max('StockAdjustmentDetailsID'))
    if max_value:
        max_stockAdjustmentDetailsId = max_value.get('StockAdjustmentDetailsID__max', 0)
        StockAdjustmentDetailsID = max_stockAdjustmentDetailsId + 1
    else:
        StockAdjustmentDetailsID = 1
    return StockAdjustmentDetailsID


def get_VoucherNo(VoucherType,BranchID,CompanyID):
    if VoucherType == "ES":
        new_VoucherNo = "ES1"
        if ExcessStockMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
            instance = ExcessStockMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "ES" + str(new_num)

        return new_VoucherNo
    elif VoucherType == "SS":
        new_VoucherNo = "SS1"
        if ShortageStockMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
            instance = ShortageStockMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID).first()
            OldVoucherNo = instance.VoucherNo
            res = re.search(r"\d+(\.\d+)?", OldVoucherNo)
            num = res.group(0)
            new_num = int(num) + 1
            new_VoucherNo = "SS" + str(new_num)

        return new_VoucherNo
    
    
    
def get_auto_StockMasterID(StockManagementMaster, BranchID, CompanyID):
    StockMasterID = 1
    if StockManagementMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        last_ins = StockManagementMaster.objects.filter(CompanyID=CompanyID,BranchID=BranchID).order_by('StockMasterID').last()
        current_StockMasterID = last_ins.StockMasterID
        StockMasterID = int(current_StockMasterID) + 1
    return StockMasterID


def get_auto_StockDetailsID(StockManagementDetails, BranchID, CompanyID):
    StockDetailsID = 1
    if StockManagementDetails.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
        last_ins = StockManagementDetails.objects.filter(CompanyID=CompanyID,BranchID=BranchID).order_by('StockDetailsID').last()
        print(last_ins)
        current_StockDetailsID = last_ins.StockDetailsID
        StockDetailsID = int(current_StockDetailsID) + 1
    return StockDetailsID
    
    
def get_stock_type(StockType):
    stock_type = "SA"
    if StockType == "0":
        stock_type = "ES"
    elif StockType == "1":
        stock_type = "SS"
    return stock_type