import random
import string
from decimal import Decimal

from django.db.models import Max
from django.http import HttpResponse


def generate_serializer_errors(args):
    message = ""
    for key, values in args.items():
        error_message = ""
        for value in values:
            error_message += value + ","
        error_message = error_message[:-1]

        message += "%s : %s | " % (key, error_message)
    return message[:-3]


def get_auto_id(model, CompanyID):
    AccountGroupID = 1
    if model.objects.filter(CompanyID=CompanyID).exists():
        latest_auto_id = (
            model.objects.filter(CompanyID=CompanyID).order_by("AccountGroupID").last()
        )
        AccountGroupID = latest_auto_id.AccountGroupID + 1
    return AccountGroupID
