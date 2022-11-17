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


def get_auto_id(model, BranchID):
    CompanySettingsID = 1
    max_value = None
    CompanySettingsID = None
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.all().aggregate(Max("CompanySettingsID"))

    if model.objects.filter(BranchID=BranchID).exists():
        max_value = model.objects.filter(BranchID=BranchID).aggregate(
            Max("CompanySettingsID")
        )

        if max_value:
            max_companySettingId = max_value.get("CompanySettingsID__max", 0)

            CompanySettingsID = max_companySettingId + 1

        else:
            CompanySettingsID = 1

    return CompanySettingsID
