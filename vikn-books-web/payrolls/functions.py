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


def get_auto_id_department(model,BranchID,DataBase):
    DepartmentID = 1
    max_value = None
    DepartmentID = None
    # latest_auto_id =  model.objects.using(DataBase).all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.using(DataBase).all().aggregate(Max('DepartmentID'))
    

    if model.objects.using(DataBase).filter(BranchID=BranchID).exists():
        max_value =  model.objects.using(DataBase).filter(BranchID=BranchID).aggregate(Max('DepartmentID')) 

        if max_value:
            max_departmentId = max_value.get('DepartmentID__max', 0)
            
            DepartmentID = max_departmentId + 1
            
        else:
            DepartmentID = 1

    return DepartmentID