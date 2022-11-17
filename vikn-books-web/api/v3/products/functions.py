import string
import random
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Max
import re


def generate_serializer_errors(args):
    message = ""
    for key, values in args.items():
        error_message = ""
        for value in values:
            error_message += value + ","
        error_message = error_message[:-1]

        message += "%s : %s | " % (key, error_message)
    return message[:-3]


def generate_priceList_serializer_errors(args):
    message = ""
    for key, values in args.items():
        error_message = ""
        for value in values:
            error_message += value + ","
        error_message = error_message[:-1]

        message += "%s : %s | " % (key, error_message)
    return message[:-3]


def get_auto_id(model, BranchID, CompanyID):
    ProductID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.filter(
        CompanyID=CompanyID).aggregate(Max('ProductID'))

    max_value = 0
    if model.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        max_value = model.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID).aggregate(Max('ProductID'))

    if max_value:
        max_productId = max_value.get('ProductID__max', 0)

        ProductID = max_productId + 1

    else:
        ProductID = 1

    # if model.objects.filter(CompanyID=CompanyID,BrandID=BrandID).exists():
    #     BrandID = 1

    return ProductID


def get_auto_priceListid(model, BranchID, CompanyID):
    PriceListID = 1
    max_value = None
    PriceListID = None
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.filter(
        CompanyID=CompanyID).aggregate(Max('PriceListID'))

    if model.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        max_value = model.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID).aggregate(Max('PriceListID'))

    if max_value:
        max_priceListId = max_value.get('PriceListID__max', 0)

        PriceListID = max_priceListId + 1

    else:
        PriceListID = 1

    # if model.objects.filter(CompanyID=CompanyID,BrandID=BrandID).exists():
    #     BrandID = 1

    return PriceListID


def get_ProductCode(model, BranchID, CompanyID):

    ProductCode = "PC1000"

    if model.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():

        latest_ProductCode = model.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID).order_by("ProductID").last()

        ProductCode = latest_ProductCode.ProductCode

        temp = re.compile("([a-zA-Z]+)([0-9]+)")
        res = temp.match(ProductCode).groups()

        code, number = res

        number = int(number) + 1

        ProductCode = str(code) + str(number)

    return ProductCode


def get_auto_AutoBarcode(model, BranchID, CompanyID):

    AutoBarcode = 70000
    if model.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        latest_AutoBarcode = model.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID).order_by("PriceListID").last()

        AutoBarcode = latest_AutoBarcode.AutoBarcode

        AutoBarcode = AutoBarcode + 1

    return AutoBarcode


def get_auto_AutoBatchCode(model, BranchID, CompanyID):

    BatchCode = 500000
    if model.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        latest_BatchCode = model.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID).order_by("BatchCode").last()

        BatchCode = latest_BatchCode.BatchCode

        BatchCode = int(BatchCode) + 1

    return BatchCode


def get_auto_BatchNo(model, BranchID, CompanyID):

    BatchNo = 5000
    if model.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        latest_BatchNo = model.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID).order_by("BatchNo").last()

        BatchNo = latest_BatchNo.BatchNo

        BatchNo = BatchNo + 1

    return BatchNo
