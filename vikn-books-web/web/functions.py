import string
import random
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Max



def generate_form_errors(args,formset=False):
    message = ''
    if not formset:
        for field in args:
            if field.errors:
                message += field.errors  + "|"
        for err in args.non_field_errors():
            message += str(err) + "|"

    elif formset:
        for form in args:
            for field in form:
                if field.errors:
                    message +=field.errors + "|"
            for err in form.non_field_errors():
                message += str(err) + "|"
    return message[:-1]


def get_auto_id(model,BranchID):
    BrandID = 1
    max_value = None
    BrandID = None
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.all().aggregate(Max('BrandID'))
    

    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID).aggregate(Max('BrandID'))
        

    if max_value:
        max_brandId = max_value.get('BrandID__max', 0)
        
        BrandID = max_brandId + 1
        
    else:
        BrandID = 1

    
    # if model.objects.filter(BrandID=BrandID).exists():
    #     BrandID = 1
            

    return BrandID


def get_auto_Branchid(model):
    BranchID = 1
    latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    if latest_auto_id:
        for auto in latest_auto_id:
            BranchID = auto.BranchID + 1
    return BranchID


def get_auto_LedgerID(model,BranchID, DataBase):
    LedgerID = 1
    max_value = None
    LedgerID = None
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.all().aggregate(Max('LedgerID'))
    

    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID).aggregate(Max('LedgerID'))
        

    if max_value:
        max_ledgeriD = max_value.get('LedgerID__max', 0)
        
        LedgerID = max_ledgeriD + 1
        
    else:
        LedgerID = 1

    
    # if model.objects.filter(BrandID=BrandID).exists():
    #     BrandID = 1
            

    return LedgerID


def get_auto_EmployeeID(model,BranchID,DataBase):
    EmployeeID = 1
    max_value = None
    EmployeeID = None
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.all().aggregate(Max('EmployeeID'))
    

    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID).aggregate(Max('EmployeeID'))
        

    if max_value:
        max_employeeiD = max_value.get('EmployeeID__max', 0)
        
        EmployeeID = max_employeeiD + 1
        
    else:
        EmployeeID = 1

    
    # if model.objects.filter(BrandID=BrandID).exists():
    #     BrandID = 1
            

    return EmployeeID


def check_groupforProfitandLoss(AccountGroupUnder):
    if not AccountGroupUnder == 0:
        if AccountGroup.objects.filter(AccountGroupID=AccountGroupUnder).exists():
            group_instance = AccountGroup.objects.get(AccountGroupID=AccountGroupUnder)
            AccountGroupUnder = group_instance.AccountGroupUnder
            AccountGroupName = group_instance.AccountGroupName
            if AccountGroupName == "Direct Expenses":
                return AccountGroupName
            elif AccountGroupName == "Indirect Expenses":
                return AccountGroupName
            elif AccountGroupName == "Direct Income":
                return AccountGroupName
            elif AccountGroupName == "Indirect Income":
                return AccountGroupName
            else:
                return check_groupforProfitandLoss(AccountGroupUnder)
        else:
            return False
    else:
        return False