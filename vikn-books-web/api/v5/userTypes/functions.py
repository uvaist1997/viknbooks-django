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
    BrandID = 1
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.all().aggregate(Max('ID'))

    if model.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
        max_value = model.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID).aggregate(Max('ID'))

        if max_value:
            max_brandId = max_value.get('ID__max', 0)

            BrandID = max_brandId + 1

        else:
            BrandID = 1

    return BrandID


def get_timezone(request):
    if "set_user_timezone" in request.session:
        user_time_zone = request.session['set_user_timezone']
    else:
        user_time_zone = "Asia/Riyadh"
    return user_time_zone
