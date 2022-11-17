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



def get_auto_id(model,DataBase):
    ColorID = 1
    latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-id")[:1]
    if latest_auto_id:
        for auto in latest_auto_id:
            ColorID = auto.ColorID + 1
    return ColorID
