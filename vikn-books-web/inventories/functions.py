import string
import random
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Max
from brands.models import AccountGroup


def get_auto_LedgerID(model,BranchID):
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


def get_auto_Branchid(model):
    BranchID = 1
    latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    if latest_auto_id:
        for auto in latest_auto_id:
            BranchID = auto.BranchID + 1
    return BranchID


def get_auto_id(model,BranchID,DataBase):
    PurchaseDetailsID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.using(DataBase).all().aggregate(Max('PurchaseDetailsID'))
    

    if model.objects.using(DataBase).filter(BranchID=BranchID).exists():
        max_value =  model.objects.using(DataBase).filter(BranchID=BranchID).aggregate(Max('PurchaseDetailsID'))
        

    if max_value:
        max_brandId = max_value.get('PurchaseDetailsID__max', 0)
        
        PurchaseDetailsID = max_brandId + 1
        
    else:
        PurchaseDetailsID = 1

    
    # if model.objects.filter(BrandID=BrandID).exists():
    #     BrandID = 1
            

    return PurchaseDetailsID


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



def get_auto_ProductGroupID(model,DataBase, BranchID):
    ProductGroupID = 1
    if model.objects.using(DataBase).filter(BranchID=BranchID).exists():
        max_value =  model.objects.using(DataBase).filter(BranchID=BranchID).aggregate(Max('ProductGroupID'))
        
        if max_value:
            max_productGroupID = max_value.get('ProductGroupID__max', 0)
            ProductGroupID = max_productGroupID + 1
        else:
            ProductGroupID = 1

    return ProductGroupID


def get_auto_TaxID(model,DataBase, BranchID):
    TaxID = 1
    if model.objects.using(DataBase).filter(BranchID=BranchID).exists():
        max_value =  model.objects.using(DataBase).filter(BranchID=BranchID).aggregate(Max('TaxID'))
        
        if max_value:
            max_TaxID = max_value.get('TaxID__max', 0)
            TaxID = max_TaxID + 1
        else:
            TaxID = 1

    return TaxID


def get_auto_ProductCategoryID(model,DataBase, BranchID):
    ProductCategoryID = 1
    if model.objects.using(DataBase).filter(BranchID=BranchID).exists():
        max_value =  model.objects.using(DataBase).filter(BranchID=BranchID).aggregate(Max('ProductCategoryID'))
        
        if max_value:
            max_ProductCategoryID = max_value.get('ProductCategoryID__max', 0)
            ProductCategoryID = max_ProductCategoryID + 1
        else:
            ProductCategoryID = 1

    return ProductCategoryID



