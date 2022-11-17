import string
import random
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Max

from main.functions import convert_to_datetime



def generate_serializer_errors(args):
    message = ""
    for key, values in args.items():
        error_message = ""
        for value in values:
            error_message += value + ","
        error_message = error_message[:-1]

        message += "%s : %s | " %(key,error_message)
    return message[:-3]



def get_auto_id(model,CompanyID):
    AccountGroupID = 1
    if model.objects.filter(CompanyID=CompanyID).exists():
        latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("AccountGroupID").last()
        AccountGroupID = latest_auto_id.AccountGroupID + 1
    return AccountGroupID


def get_expense_dashboard_data(details, months):
    data = []
    idx = 0
    for a in details:
        date = convert_to_datetime(a["date"])
        total = abs(a["amount"])
        month = date.strftime('%b')
        reslt = {
            "month": month,
            "total": total,
        }
        if months[idx] == month:
            data.append(total)
            idx += 1
        else:
            # no = idx
            while not months[idx] == month:
                data.append(0)
                # no += 1
                idx += 1
            else:
                data.append(total)
                idx += 1
    return data
