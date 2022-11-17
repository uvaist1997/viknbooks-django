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


def get_auto_idMaster(model, BranchID, CompanyID):
    StockTransferMasterID = 1
    max_value = None
    StockTransferMasterID = None
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.filter(
        CompanyID=CompanyID).aggregate(Max('StockTransferMasterID'))

    if model.objects.filter(CompanyID=CompanyID).exists():
        max_value = model.objects.filter(
            CompanyID=CompanyID).aggregate(Max('StockTransferMasterID'))

    if max_value:
        max_stockTransferMasterId = max_value.get(
            'StockTransferMasterID__max', 0)

        StockTransferMasterID = max_stockTransferMasterId + 1

    else:
        StockTransferMasterID = 1

    return StockTransferMasterID


def get_auto_id(model, BranchID, CompanyID):
    StockTransferDetailsID = 1
    max_value = None
    StockTransferDetailsID = None
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.filter(
        CompanyID=CompanyID).aggregate(Max('StockTransferDetailsID'))

    if model.objects.filter(CompanyID=CompanyID).exists():
        max_value = model.objects.filter(
            CompanyID=CompanyID).aggregate(Max('StockTransferDetailsID'))

    if max_value:
        max_stockTransferDetailsId = max_value.get(
            'StockTransferDetailsID__max', 0)

        StockTransferDetailsID = max_stockTransferDetailsId + 1
    else:
        StockTransferDetailsID = 1

    return StockTransferDetailsID
