import string
import random
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Max
from brands import models
import datetime


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
    SettingsID = 1
    max_value = None
    SettingsID = None
    # latest_auto_id =  model.objects.all().order_by("-CreatedDate")[:1]
    latest_auto_id = model.objects.all().aggregate(Max('SettingsID'))

    if model.objects.filter(BranchID=BranchID).exists():
        max_value = model.objects.filter(
            BranchID=BranchID).aggregate(Max('SettingsID'))

    if max_value:
        max_settingsId = max_value.get('SettingsID__max', 0)
        SettingsID = max_settingsId + 1
    else:
        SettingsID = 1

    return SettingsID


def create_or_update_user_type_settings(User, CompanyID, BranchID, GroupName, SettingsType, SettingsValue, UserType):
    today = datetime.datetime.now()
    Action = "A"
    if not models.UserTypeSettings.objects.filter(CompanyID=CompanyID, GroupName=GroupName, SettingsType=SettingsType, UserType=UserType).exists():
        models.UserTypeSettings.objects.create(
            UserType=UserType,
            CompanyID=CompanyID,
            GroupName=GroupName,
            SettingsType=SettingsType,
            SettingsValue=SettingsValue,
            BranchID=BranchID,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=User,
            UpdatedUserID=User,
            Action=Action
        )
    elif not models.UserTypeSettings.objects.filter(CompanyID=CompanyID, GroupName=GroupName, SettingsType=SettingsType, UserType=UserType, SettingsValue=SettingsValue).exists():
        Action = "M"
        instance = models.UserTypeSettings.objects.get(
            CompanyID=CompanyID,
            BranchID=BranchID,
            GroupName=GroupName,
            SettingsType=SettingsType,
            UserType=UserType,
        )
        instance.SettingsValue = SettingsValue
        instance.UpdatedDate = today
        instance.UpdatedUserID = User
        instance.Action = Action
        instance.save()
    else:
        pass


def get_user_type_settings(CompanyID, BranchID, SettingsType, UserType):
    value = False
    if models.UserTypeSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType=SettingsType, UserType=UserType).exists():
        try:
            value = models.UserTypeSettings.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, SettingsType=SettingsType, UserType=UserType).SettingsValue
        except:
            value = models.UserTypeSettings.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, SettingsType=SettingsType, UserType=UserType)[0].SettingsValue
        if value == "True":
            value = True
        elif value == "False":
            value = False
    return value
