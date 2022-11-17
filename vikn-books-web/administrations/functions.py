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
    # latest_auto_id =  model.objects.filter(CompanyID = CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID = CompanyID).aggregate(Max('LedgerID'))
    

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


def get_auto_id_department(model,BranchID,CompanyID):
    DepartmentID = 1
    max_value = None
    DepartmentID = None
    # latest_auto_id =  model.objects.filter(CompanyID = CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID = CompanyID).aggregate(Max('DepartmentID'))
    

    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID).aggregate(Max('DepartmentID')) 

        if max_value:
            max_departmentId = max_value.get('DepartmentID__max', 0)
            
            DepartmentID = max_departmentId + 1
            
        else:
            DepartmentID = 1

    return DepartmentID


def get_auto_id_user_type(model,BranchID,CompanyID):
    UserTypeID = 1
    # latest_auto_id =  model.objects.filter(CompanyID = CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID = CompanyID).aggregate(Max('ID'))
    

    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID).aggregate(Max('ID'))
        

        if max_value:
            max_user_type_Id = max_value.get('ID__max', 0)
            
            UserTypeID = max_user_type_Id + 1
            
        else:
            UserTypeID = 1

    return UserTypeID


def get_auto_id_financial_year(model,CompanyID):
    FinancialYearID = 1
    # latest_auto_id =  model.objects.filter(CompanyID = CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID = CompanyID).aggregate(Max('FinancialYearID'))
    

    max_value =  model.objects.filter(CompanyID = CompanyID).aggregate(Max('FinancialYearID'))
        

    if max_value:
        max_user_type_Id = max_value.get('ID__max', 0)
        
        FinancialYearID = max_user_type_Id + 1
        
    else:
        FinancialYearID = 1

    return FinancialYearID