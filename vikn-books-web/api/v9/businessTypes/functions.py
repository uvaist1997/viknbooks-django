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


def get_auto_id(model, BranchID, CompanyID):
    CountryID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.all().aggregate(Max("CountryID"))

    if model.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
        max_value = model.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID
        ).aggregate(Max("CountryID"))

        if max_value:
            max_brandId = max_value.get("CountryID__max", 0)

            CountryID = max_brandId + 1

        else:
            CountryID = 1

    return CountryID
