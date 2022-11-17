import string
import random
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Max
from mailqueue.models import MailerMessage
from django.conf import settings
import random

def random_string():
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    password = ''
    for c in range(8):
        password += random.choice(chars)
    return password


def generate_serializer_errors(args):
    message = ""
    for key, values in args.items():
        error_message = ""
        for value in values:
            error_message += value + ","
        error_message = error_message[:-1]

        message += "%s : %s | " %(key,error_message)
    return message[:-3]


def get_auto_id(model,BranchID,CompanyID):
    ID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('ID'))
    

    if model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).exists():
        max_value =  model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).aggregate(Max('ID'))
        

        if max_value:
            max_userId = max_value.get('ID__max', 0)
            
            ID = max_userId + 1
            
        else:
            ID = 1

    return ID


def get_master_auto_id(model,BranchID,CompanyID):
    MasterTypeID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).aggregate(Max('MasterTypeID'))
    

    if model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).exists():
        max_value =  model.objects.filter(BranchID=BranchID,CompanyID=CompanyID).aggregate(Max('MasterTypeID'))
        

        if max_value:
            max_userId = max_value.get('MasterTypeID__max', 0)
            
            MasterTypeID = max_userId + 1
            
        else:
            MasterTypeID = 1

    return MasterTypeID


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