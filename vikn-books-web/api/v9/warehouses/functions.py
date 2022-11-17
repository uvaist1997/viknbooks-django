import random
import string
from decimal import Decimal

from django.db.models import Max
from django.http import HttpResponse

from brands.models import Warehouse


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
    RouteID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.all().aggregate(Max("WarehouseID"))

    WarehouseID = 1

    if model.objects.filter(CompanyID=CompanyID).exists():
        max_value = model.objects.filter(CompanyID=CompanyID).aggregate(
            Max("WarehouseID")
        )

        if max_value:
            max_warehouseID = max_value.get("WarehouseID__max", 0)

            WarehouseID = max_warehouseID + 1

        else:
            WarehouseID = 1

    return WarehouseID
