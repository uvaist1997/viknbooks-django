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

        message += "%s : %s | " % (key, error_message)
    return message[:-3]


def get_auto_id(model, BranchID, CompanyID):
    ProductGroupID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.filter(
        CompanyID=CompanyID).aggregate(Max('ProductGroupID'))

    if model.objects.filter(CompanyID=CompanyID).exists():
        max_value = model.objects.filter(
            CompanyID=CompanyID).aggregate(Max('ProductGroupID'))

        if max_value:
            max_productGroupID = max_value.get('ProductGroupID__max', 0)

            ProductGroupID = max_productGroupID + 1

        else:
            ProductGroupID = 1

    return ProductGroupID
