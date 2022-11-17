import datetime

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from api.v9.accountGroups.functions import generate_serializer_errors, get_auto_id
from api.v9.accountGroups.serializers import (
    AccountGroupRestSerializer,
    AccountGroupSerializer,
)
from api.v9.brands.serializers import ListSerializer
from brands.models import AccountGroup, AccountGroup_Log
from main.functions import activity_log, converted_float, get_company
from users.models import CustomerUser, DatabaseStore


def call_paginator_all(model_object, page_number, items_per_page):
    paginator = Paginator(model_object, items_per_page)
    content = paginator.page(page_number)
    return content


def list_pagination(list_value, items_per_page, page_no):
    paginator_object = Paginator(list_value, items_per_page)
    get_value = paginator_object.page(page_no).object_list
    return get_value


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_accountGroup(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]

    today = datetime.datetime.now()
    serialized = AccountGroupSerializer(data=request.data)
    if serialized.is_valid():

        AccountGroupName = serialized.data["AccountGroupName"]
        GroupCode = serialized.data["GroupCode"]
        AccountGroupUnder = serialized.data["AccountGroupUnder"]
        Notes = serialized.data["Notes"]
        IsActive = serialized.data["IsActive"]
        IsDefault = serialized.data["IsDefault"]

        Action = "A"

        AccountGroupID = get_auto_id(AccountGroup, CompanyID)
        if not AccountGroup.objects.filter(
            CompanyID=CompanyID, AccountGroupName=AccountGroupName
        ):

            AccountGroup.objects.create(
                AccountGroupID=AccountGroupID,
                AccountGroupName=AccountGroupName,
                GroupCode=GroupCode,
                AccountGroupUnder=AccountGroupUnder,
                Notes=Notes,
                IsActive=IsActive,
                IsDefault=IsDefault,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            AccountGroup_Log.objects.create(
                AccountGroupName=AccountGroupName,
                TransactionID=AccountGroupID,
                GroupCode=GroupCode,
                AccountGroupUnder=AccountGroupUnder,
                Notes=Notes,
                IsActive=IsActive,
                IsDefault=IsDefault,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            # request , company, log_type, user, source, action, message, description
            activity_log(
                request._request,
                CompanyID,
                "Information",
                CreatedUserID,
                "AccountGroup",
                "Create",
                "AccountGroup created successfully.",
                "AccountGroup saved successfully.",
            )

            data = {"AccountGroupID": AccountGroupID}
            data.update(serialized.data)
            response_data = {"StatusCode": 6000, "data": data}

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "AccountGroup Name Already exist",
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:

        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Error",
            CreatedUserID,
            "AccountGroup",
            "Create",
            "AccountGroup field not valid.",
            generate_serializer_errors(serialized._errors),
        )

        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors),
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_accountGroup(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]

    today = datetime.datetime.now()
    serialized = AccountGroupSerializer(data=request.data)
    instance = None
    if AccountGroup.objects.filter(pk=pk).exists():
        instance = AccountGroup.objects.get(pk=pk)

        AccountGroupName = instance.AccountGroupName
        if serialized.is_valid():
            AccountGroupName = serialized.data["AccountGroupName"]
            GroupCode = serialized.data["GroupCode"]
            AccountGroupUnder = serialized.data["AccountGroupUnder"]
            Notes = serialized.data["Notes"]
            IsActive = serialized.data["IsActive"]
            IsDefault = serialized.data["IsDefault"]

            AccountGroupID = instance.AccountGroupID
            Action = "M"

            instance.Action = Action
            instance.CreatedUserID = CreatedUserID
            instance.UpdatedDate = today
            instance.save()

            serialized.update(instance, serialized.data)

            AccountGroup_Log.objects.create(
                CompanyID=CompanyID,
                AccountGroupName=AccountGroupName,
                TransactionID=AccountGroupID,
                GroupCode=GroupCode,
                AccountGroupUnder=AccountGroupUnder,
                Notes=Notes,
                IsActive=IsActive,
                IsDefault=IsDefault,
                Action=Action,
                CreatedUserID=CreatedUserID,
                UpdatedDate=today,
            )

            # request , company, log_type, user, source, action, message, description
            activity_log(
                request._request,
                CompanyID,
                "Information",
                CreatedUserID,
                "AccountGroup",
                "Edit",
                "AccountGroup Updated successfully.",
                "AccountGroup saved successfully.",
            )

            response_data = {"StatusCode": 6000, "data": serialized.data}

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            # request , company, log_type, user, source, action, message, description
            activity_log(
                request._request,
                CompanyID,
                "Error",
                CreatedUserID,
                "AccountGroup",
                "Edit",
                "AccountGroup Updated Failed.",
                generate_serializer_errors(serialized._errors),
            )
            response_data = {
                "StatusCode": 6001,
                "message": generate_serializer_errors(serialized._errors),
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Error",
            CreatedUserID,
            "AccountGroup",
            "Edit",
            "AccountGroup Updated Failed.",
            "AccountGroup Not Found!.",
        )
        response_data = {"StatusCode": 6001, "message": "Account Group Not Found!"}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def accountGroups(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]

    try:
        page_number = data["page_no"]
    except:
        page_number = ""

    try:
        items_per_page = data["items_per_page"]
    except:
        items_per_page = ""

    exclude_item = [0, 1, 2]

    if page_number and items_per_page:
        instances = (
            AccountGroup.objects.filter(CompanyID=CompanyID)
            .exclude(AccountGroupID__in=exclude_item)
            .order_by("-AccountGroupID")
        )
        count = len(instances)
        ledger_sort_pagination = list_pagination(instances, items_per_page, page_number)
    else:
        ledger_sort_pagination = (
            AccountGroup.objects.filter(CompanyID=CompanyID)
            .exclude(AccountGroupID__in=exclude_item)
            .order_by("-AccountGroupID")
        )
        count = len(ledger_sort_pagination)
    serialized = AccountGroupRestSerializer(
        ledger_sort_pagination, many=True, context={"CompanyID": CompanyID}
    )

    # request , company, log_type, user, source, action, message, description
    activity_log(
        request._request,
        CompanyID,
        "Information",
        CreatedUserID,
        "AccountGroup",
        "View",
        "AccountGroup List",
        "The user viewed AccountGroups",
    )
    response_data = {
        "StatusCode": 6000,
        "data": serialized.data,
        "count": count,
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def search_accountGroups(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    product_name = data["product_name"]
    length = data["length"]
    param = data["param"]

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]
        exclude_item = [0, 1, 2]
        if AccountGroup.objects.filter(CompanyID=CompanyID).exists():
            instances = AccountGroup.objects.filter(CompanyID=CompanyID).exclude(
                AccountGroupID__in=exclude_item
            )
            if length < 3:
                if param == "name":
                    instances = instances.filter(
                        (Q(AccountGroupName__icontains=product_name))
                    )[:10]
                elif param == "code":
                    instances = instances.filter(
                        (Q(GroupCode__icontains=product_name))
                    )[:10]
                else:
                    instances = instances.filter(
                        (Q(AccountGroupUnder__in=product_name))
                    )[:10]
            else:
                if param == "name":
                    instances = instances.filter(
                        (Q(AccountGroupName__icontains=product_name))
                    )
                elif param == "code":
                    instances = instances.filter((Q(GroupCode__icontains=product_name)))
                else:
                    instances = instances.filter(
                        (Q(AccountGroupUnder__in=product_name))
                    )
            serialized = AccountGroupRestSerializer(
                instances,
                many=True,
                context={
                    "request": request,
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "product_name": "product_name",
                },
            )

        response_data = {"StatusCode": 6000, "data": serialized.data}

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def accountGroup(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]

    instance = None
    if AccountGroup.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = AccountGroup.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = AccountGroupRestSerializer(
            instance, context={"CompanyID": CompanyID}
        )

        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Information",
            CreatedUserID,
            "AccountGroup",
            "View",
            "AccountGroup Single page",
            "The user viewed AccountGroup",
        )
        response_data = {"StatusCode": 6000, "data": serialized.data}
    else:
        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Error",
            CreatedUserID,
            "AccountGroup",
            "View",
            "AccountGroup Single page",
            "AccountGroup Not Found!",
        )
        response_data = {"StatusCode": 6001, "message": "Account Group Not Found!"}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_accountGroup(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]

    today = datetime.datetime.now()
    instance = None
    if AccountGroup.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = AccountGroup.objects.get(pk=pk, CompanyID=CompanyID)
        AccountGroupName = instance.AccountGroupName
        AccountGroupID = instance.AccountGroupID
        GroupCode = instance.GroupCode
        AccountGroupUnder = instance.AccountGroupUnder
        Notes = instance.Notes
        IsActive = instance.IsActive
        IsDefault = instance.IsDefault
        Action = "D"
        instance.delete()
        AccountGroup_Log.objects.create(
            CompanyID=CompanyID,
            AccountGroupName=AccountGroupName,
            TransactionID=AccountGroupID,
            GroupCode=GroupCode,
            AccountGroupUnder=AccountGroupUnder,
            Notes=Notes,
            IsActive=IsActive,
            IsDefault=IsDefault,
            CreatedUserID=CreatedUserID,
            Action=Action,
            UpdatedDate=today,
            CreatedDate=today,
        )
        response_data = {
            "StatusCode": 6000,
            "title": "Success",
            "message": "Account Group Deleted Successfully!",
        }
        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Information",
            CreatedUserID,
            "AccountGroup",
            "Delete",
            "AccountGroup Deleted",
            "AccountGroup Deleted Successfully!",
        )
    else:
        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Error",
            CreatedUserID,
            "AccountGroup",
            "Delete",
            "AccountGroup Deleted failed",
            "AccountGroup Deleted failed,AccountGroup Not Found!",
        )
        response_data = {
            "StatusCode": 6001,
            "title": "Failed",
            "message": "Account Group Not Found!",
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def search_group_list(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    PriceRounding = data["PriceRounding"]
    product_name = data["product_name"]
    length = data["length"]

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        if AccountGroup.objects.filter(
            CompanyID=CompanyID, AccountGroupName__icontains=product_name
        ).exists():
            group_ins = AccountGroup.objects.filter(
                CompanyID=CompanyID, AccountGroupName__icontains=product_name
            )
            if length < 3:
                group_ins = group_ins[:10]

            serialized = AccountGroupRestSerializer(
                group_ins,
                many=True,
                context={
                    "request": request,
                    "CompanyID": CompanyID,
                    "PriceRounding": PriceRounding,
                    "product_name": "product_name",
                },
            )
            response_data = {"StatusCode": 6000, "data": serialized.data}
        else:
            response_data = {"StatusCode": 6001, "data": "Ledger not found!"}

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch You Enterd is not Valid!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)
