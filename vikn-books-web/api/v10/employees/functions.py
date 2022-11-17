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


def get_auto_id(model, BranchID, CompanyID):
    EmployeeID = 1
    # latest_auto_id =  model.objects.filter(CompanyID=CompanyID).order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.filter(
        CompanyID=CompanyID,).aggregate(Max('EmployeeID'))

    if model.objects.filter(CompanyID=CompanyID).exists():
        max_value = model.objects.filter(
            CompanyID=CompanyID).aggregate(Max('EmployeeID'))

        if max_value:
            max_employeeId = max_value.get('EmployeeID__max', 0)

            EmployeeID = max_employeeId + 1

        else:
            EmployeeID = 1

    return EmployeeID


def get_EmployeeCode(model, BranchID, CompanyID):
    latest_EmployeeCode = model.objects.filter(
        CompanyID=CompanyID).order_by("-id")[:1]
    print(latest_EmployeeCode, 'latest_EmployeeCode')
    if latest_EmployeeCode:
        for lc in latest_EmployeeCode:
            EmployeeCode = lc.EmployeeCode
            print(EmployeeCode)
            temp = re.compile("([a-zA-Z]+)([0-9]+)")
            res = temp.match(EmployeeCode).groups()

            code, number = res

            number = int(number) + 1
            EmployeeCode = str(code) + str(number)
    else:
        EmployeeCode = "EP1"
    return EmployeeCode
