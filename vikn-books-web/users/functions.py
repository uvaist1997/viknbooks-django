from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Max
import re


# def get_auto_id(model):
#     auto_id = 1
#     latest_auto_id =  model.objects.all().order_by("-id")[:1]
#     if latest_auto_id:
#         for auto in latest_auto_id:
#             auto_id = auto.auto_id + 1
#     return auto_id

def get_auto_id(model,BranchID,database):
    ID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.using(database).all().aggregate(Max('ID'))
    
    if model.objects.using(database).filter(BranchID=BranchID).exists():
        max_value =  model.objects.using(database).filter(BranchID=BranchID).aggregate(Max('ID'))
        

        if max_value:
            max_ID = max_value.get('ID__max', 0)
            
            ID = max_ID + 1
            
        else:
            ID = 1


    return ID

def get_current_role(request):
    current_role = "user"
    if request.user.is_authenticated:        
        if request.user.is_superuser:
            current_role = "superadmin"  
        elif StudentDivision.objects.filter(user=request.user).exists():
            current_role = "division"                     
    return current_role

def get_EmployeeCode(model,BranchID):
    latest_EmployeeCode =  model.objects.filter(BranchID=BranchID).order_by("-id")[:1]
    if latest_EmployeeCode:
        for lc in latest_EmployeeCode:
            EmployeeCode = lc.EmployeeCode
            temp = re.compile("([a-zA-Z]+)([0-9]+)")
            res = temp.match(EmployeeCode).groups()

            code , number = res

            number = int(number) + 1
            EmployeeCode = str(code) + str(number)
    else:
        EmployeeCode = "EP1"
    return EmployeeCode


def get_LedgerCode(model,BranchID):

    LedgerCode = "AL1"

    latest_LedgerCode =  model.objects.filter(BranchID=BranchID).order_by("-id")[:1]

    # LedgerCode = latest_LedgerCode.LedgerCode
    if latest_LedgerCode:
        for auto in latest_LedgerCode:

            LedgerCode = auto.LedgerCode

            temp = re.compile("([a-zA-Z]+)([0-9]+)") 
            res = temp.match(LedgerCode).groups()

            code , number = res

            number = int(number) + 1

            LedgerCode = str(code) + str(number)


    return LedgerCode


def get_auto_LedgerID(model,BranchID):
    LedgerID = 1
    max_value = None
    LedgerID = None
    # latest_auto_id =  model.objects.using(DataBase).all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.all().aggregate(Max('LedgerID'))
    

    if model.objects.filter(BranchID=BranchID).exists():
        max_value =  model.objects.filter(BranchID=BranchID).aggregate(Max('LedgerID'))
        

    if max_value:
        max_ledgeriD = max_value.get('LedgerID__max', 0)
        
        LedgerID = max_ledgeriD + 1
        
    else:
        LedgerID = 1

    
    # if model.objects.using(DataBase).filter(BrandID=BrandID).exists():
    #     BrandID = 1
            

    return LedgerID

def send_email(to_address,subject,name,content,phone,html_content,attachment=None,attachment2=None,attachment3=None):
        new_message = MailerMessage()
        new_message.name = name
        new_message.phone = phone
        new_message.subject = subject
        new_message.to_address = to_address
        new_message.from_address = settings.DEFAULT_FROM_EMAIL
        new_message.content = content
        print(new_message)
        new_message.html_content = html_content
        if attachment:
            new_message.add_attachment(attachment)
        if attachment2:
            new_message.add_attachment(attachment2)
        if attachment3:
            new_message.add_attachment(attachment3)
        new_message.app = "default"
        new_message.save()