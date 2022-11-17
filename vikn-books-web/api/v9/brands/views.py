import datetime
from genericpath import exists
import os
import sys

from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import IntegrityError, transaction
from django.db.models import Prefetch, Q,Sum
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from api.v4.accountLedgers.functions import get_auto_LedgerPostid
from api.v9.accountLedgers.functions import UpdateLedgerBalance

from api.v9.branchs.functions import get_branch_settings
from api.v9.brands.functions import generate_serializer_errors, get_auto_id
from api.v9.brands.serializers import (
    BrandRestSerializer,
    BrandSerializer,
    ListSerializer,
)
from api.v9.brands.tasks import create_random_user_accounts
from brands.models import (
    AccountLedger,
    Activity_Log,
    Brand,
    Brand_Log,
    CompanySettings,
    ExpenseDetails,
    ExpenseMaster,
    LedgerPosting,
    LedgerPosting_Log,
    Parties,
    PriceList,
    Product,
    PurchaseMaster,
    PurchaseOrderMaster,
    PurchaseReturnMaster,
    ReceiptDetails,
    ReceiptMaster,
    SalesEstimateMaster,
    SalesMaster,
    SalesOrderMaster,
    SalesReturnMaster,
    UserAdrress,
)
from main.functions import (
    activity_log,
    converted_float,
    get_BranchLedgerId_for_LedgerPosting,
    get_BranchSettings,
    get_company,
    get_ModelInstance,
)
from django.db.models import F


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
def create_brand(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]

    today = datetime.datetime.now()
    serialized = BrandSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data["BranchID"]
        BrandName = serialized.data["BrandName"]
        Notes = serialized.data["Notes"]

        Action = "A"
        BrandID = get_auto_id(Brand, BranchID, CompanyID)
        if not Brand.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID, BrandName__iexact=BrandName
        ).exists():

            Brand.objects.create(
                BrandID=BrandID,
                BranchID=BranchID,
                BrandName=BrandName,
                Notes=Notes,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID,
            )

            Brand_Log.objects.create(
                BranchID=BranchID,
                TransactionID=BrandID,
                BrandName=BrandName,
                Notes=Notes,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID,
            )
            # request , company, log_type, user, source, action, message, description
            activity_log(
                request._request,
                CompanyID,
                "Information",
                CreatedUserID,
                "Brand",
                "Create",
                "Brand created successfully.",
                "Brand saved successfully.",
            )

            data = {"BrandID": BrandID}
            data.update(serialized.data)
            response_data = {"StatusCode": 6000, "data": data}

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # request , company, log_type, user, source, action, message, description
            activity_log(
                request._request,
                CompanyID,
                "Warning",
                CreatedUserID,
                "Brand",
                "Create",
                "Brand name already exist.",
                "same name exists.",
            )

            response_data = {"StatusCode": 6001, "message": "Brand name already exist."}

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Error",
            CreatedUserID,
            "Brand",
            "Create",
            "Brand field not valid.",
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
def edit_brand(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]

    today = datetime.datetime.now()
    serialized = BrandSerializer(data=request.data)
    instance = Brand.objects.get(pk=pk, CompanyID=CompanyID)

    BranchID = instance.BranchID
    BrandID = instance.BrandID
    instanceBrandname = instance.BrandName

    if serialized.is_valid():
        BrandName = serialized.data["BrandName"]
        Notes = serialized.data["Notes"]
        Action = "M"
        if not Brand.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID, BrandName__iexact=BrandName
        ).exclude(BrandName=instanceBrandname):
            instance.BrandName = BrandName
            instance.Notes = Notes
            instance.Action = Action
            instance.CreatedUserID = CreatedUserID
            instance.UpdatedDate = today
            instance.save()

            Brand_Log.objects.create(
                BranchID=BranchID,
                TransactionID=BrandID,
                BrandName=BrandName,
                Notes=Notes,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID,
            )
            # request , company, log_type, user, source, action, message, description
            activity_log(
                request._request,
                CompanyID,
                "Information",
                CreatedUserID,
                "Brand",
                "Edit",
                "Brand edited successfully.",
                "Brand saved successfully.",
            )

            data = {"BrandID": BrandID}
            data.update(serialized.data)
            response_data = {"StatusCode": 6000, "data": data}

            return Response(response_data, status=status.HTTP_200_OK)

        elif Brand.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID, BrandName__iexact=BrandName
        ).exists():
            # request , company, log_type, user, source, action, message, description
            activity_log(
                request._request,
                CompanyID,
                "Information",
                CreatedUserID,
                "Brand",
                "Edit",
                "Brand already exists.",
                "Brand name already exist in this branch.",
            )

            response_data = {
                "StatusCode": 6001,
                "message": "Brand name already exist in this branch",
            }
            return Response(response_data, status=status.HTTP_200_OK)

        else:
            instance.BrandName = BrandName
            instance.Notes = Notes
            instance.Action = Action
            instance.UpdatedDate = today
            instance.CreatedUserID = CreatedUserID
            instance.save()

            Brand_Log.objects.create(
                BranchID=BranchID,
                TransactionID=BrandID,
                BrandName=BrandName,
                Notes=Notes,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID,
            )
            # request , company, log_type, user, source, action, message, description
            activity_log(
                request._request,
                CompanyID,
                "Information",
                CreatedUserID,
                "Brand",
                "Edit",
                "Brand edited successfully.",
                "Brand saved successfully.",
            )

            data = {"BrandID": BrandID}
            data.update(serialized.data)
            response_data = {"StatusCode": 6000, "data": data}

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Error",
            CreatedUserID,
            "Brand",
            "Edit",
            "Brand edited failed.",
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
def brands(request):
    from main.functions import get_device_name, get_location

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

    # from django.contrib.gis.geoip2 import GeoIP2

    location = get_location(request)
    # device_name = get_device_name(request)
    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]
        productsForAllBranches = get_branch_settings(
            CompanyID, "productsForAllBranches"
        )
        instances = None
        if productsForAllBranches == True:
            if Brand.objects.filter(CompanyID=CompanyID).exists():
                instances = Brand.objects.filter(CompanyID=CompanyID)
        else:
            if Brand.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
                instances = Brand.objects.filter(BranchID=BranchID, CompanyID=CompanyID)
        if instances:
            if page_number and items_per_page:
                count = len(instances)
                ledger_sort_pagination = list_pagination(
                    instances, items_per_page, page_number
                )
            else:
                ledger_sort_pagination = instances
                count = len(ledger_sort_pagination)
            serialized = BrandRestSerializer(ledger_sort_pagination, many=True)

            # request , company, log_type, user, source, action, message, description
            activity_log(
                request._request,
                CompanyID,
                "Information",
                CreatedUserID,
                "Brand",
                "View",
                "Brand list",
                "The user viewed brands",
            )

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "count": count,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # request , company, log_type, user, source, action, message, description
            activity_log(
                request._request,
                CompanyID,
                "Information",
                CreatedUserID,
                "Brand",
                "View",
                "Brand list",
                "brand not found",
            )
            response_data = {
                "StatusCode": 6001,
                "message": "Brands Not Found in this BranchID!",
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Information",
            CreatedUserID,
            "Brand",
            "View",
            "Brand list",
            "brand not valid",
        )
        response_data = {
            "StatusCode": 6001,
            "message": "Branch You Enterd is not Valid!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def brand(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]

    instance = None
    if Brand.objects.filter(pk=pk).exists():
        instance = Brand.objects.get(pk=pk)
        serialized = BrandRestSerializer(instance)
        response_data = {"StatusCode": 6000, "data": serialized.data}
        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Information",
            CreatedUserID,
            "Brand",
            "View",
            "Brand Single Page",
            "User viewed a Brand",
        )
    else:
        response_data = {"StatusCode": 6001, "message": "Brand Not Fount!"}

        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Error",
            CreatedUserID,
            "Brand",
            "View",
            "Brand Single Page",
            "Brand not Found!",
        )

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_brand(request, pk):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]

    try:
        selecte_ids = data["selecte_ids"]
    except:
        selecte_ids = []

    today = datetime.datetime.now()
    instances = None
    if pk == "1":
        # request , company, log_type, user, source, action, message, description
        activity_log(
            request._request,
            CompanyID,
            "Warning",
            CreatedUserID,
            "Brand",
            "Delete",
            "Brand Deleted failed",
            "Tried to Delete Default Brand!",
        )
        response_data = {
            "StatusCode": 6001,
            "message": "You Can't Delete this Brand!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        if selecte_ids:
            if Brand.objects.filter(CompanyID=CompanyID, pk__in=selecte_ids).exists():
                instances = Brand.objects.filter(pk__in=selecte_ids)
        else:
            if Brand.objects.filter(CompanyID=CompanyID, pk=pk).exists():
                instances = Brand.objects.filter(pk=pk)

        if instances:
            for instance in instances:
                BranchID = instance.BranchID
                BrandID = instance.BrandID
                BrandName = instance.BrandName
                Notes = instance.Notes
                Action = "D"

                if not Product.objects.filter(
                    BranchID=BranchID, BrandID=BrandID, CompanyID=CompanyID
                ).exists():

                    instance.delete()

                    Brand_Log.objects.create(
                        BranchID=BranchID,
                        TransactionID=BrandID,
                        BrandName=BrandName,
                        Notes=Notes,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CreatedUserID=CreatedUserID,
                        Action=Action,
                        CompanyID=CompanyID,
                    )
                    # request , company, log_type, user, source, action, message, description
                    activity_log(
                        request._request,
                        CompanyID,
                        "Information",
                        CreatedUserID,
                        "Brand",
                        "Delete",
                        "Brand Deleted Successfully",
                        "Brand Deleted Successfully",
                    )

                    response_data = {
                        "StatusCode": 6000,
                        "message": "Brand Deleted Successfully!",
                    }
                else:
                    # request , company, log_type, user, source, action, message, description
                    activity_log(
                        request._request,
                        CompanyID,
                        "Warning",
                        CreatedUserID,
                        "Brand",
                        "Delete",
                        "Brand Deleted Failed",
                        "Brand Deleted Failed,Product has Created with this Brand",
                    )
                    response_data = {
                        "StatusCode": 6001,
                        "message": "You can't Delete this Brand,Product exist with this Brand!!",
                    }
        else:
            # request , company, log_type, user, source, action, message, description
            activity_log(
                request._request,
                CompanyID,
                "Error",
                CreatedUserID,
                "Brand",
                "Delete",
                "Brand Deleted Failed",
                "Brand Not Found!",
            )
            response_data = {"StatusCode": 6001, "message": "Brand Not Found!"}

        return Response(response_data, status=status.HTTP_200_OK)




# from django.contrib import messages
# from django.views.generic.edit import FormView
# from django.shortcuts import redirect

# from .forms import GenerateRandomUserForm


# class GenerateRandomUserView(FormView):
#     template_name = 'core/generate_random_users.html'
#     form_class = GenerateRandomUserForm

#     def form_valid(self, form):
#         total = form.cleaned_data.get('total')
#         create_random_user_accounts.delay(total)
#         messages.success(
#             self.request, 'We are generating your random users! Wait a moment and refresh this page.')
#         return redirect('users_list')


@api_view(["POST"])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def generate_random_users(request):
    total = int(request.data["total"])
    print(total)
    create_random_user_accounts.delay(int(total))

    response_data = {
        "StatusCode": 6000,
        "message": "users generated successfully",
        "total": total,
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def search_brands(request):
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
        if Brand.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instances = Brand.objects.filter(CompanyID=CompanyID, BranchID=BranchID)

            if length < 3:
                if param == "BrandName":
                    instances = instances.filter(
                        (Q(BrandName__icontains=product_name))
                    )[:10]
            else:
                if param == "BrandName":
                    instances = instances.filter((Q(BrandName__icontains=product_name)))

            serialized = BrandRestSerializer(
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
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
@transaction.atomic
def torunqryTest(request):
    print("startttttttttttttttttttttttt")
    CompanyID = CompanySettings.objects.get(
        id="cbba36e8-8cb9-4570-9161-2aecf7cf8e8a")
    if Product.objects.filter(CompanyID=CompanyID).exists():
        products = Product.objects.filter(CompanyID=CompanyID)
        for p in products:
            price_lists = PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=p.ProductID)
            list_count = price_lists.count()
            all_false_count = price_lists.filter(UnitInSales=False, UnitInPurchase=False, UnitInReports=False).count()
            if list_count == all_false_count:
                default_price_list = price_lists.filter(DefaultUnit=True).first()
                default_price_list.UnitInSales = True
                default_price_list.UnitInPurchase = True
                default_price_list.UnitInReports = True
                default_price_list.save()
    # Query for expense ledgerposting change change end
    print(
        "------------------------->.................>>>>>>>>>>>>>>>>>>>>>......suucess"
    )

    response_data = {"StatusCode": 6000,
                     "message": "success", "list_count": list_count, "all_false_count": all_false_count}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def setDefault_brands(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    BranchID = data["BranchID"]
    id = data["id"]
    value = data["value"]
    StatusCode = 6001
    if Brand.objects.filter(id=id).exists():
        Brand.objects.filter(CompanyID=CompanyID).update(IsDefault=False)
        if value == True:
            Brand.objects.filter(id=id).update(IsDefault=True)
        else:
            Brand.objects.filter(CompanyID=CompanyID, BrandID=1).update(IsDefault=True)
        StatusCode = 6000

    response_data = {
        "StatusCode": StatusCode,
    }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def search_brand_list(request):
    data = request.data
    CompanyID = data["CompanyID"]
    CompanyID = get_company(CompanyID)
    CreatedUserID = data["CreatedUserID"]
    PriceRounding = data["PriceRounding"]
    product_name = data["product_name"]
    length = data["length"]

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data["BranchID"]
        if Brand.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            if length < 3:
                instances = Brand.objects.filter(CompanyID=CompanyID, BranchID=BranchID)
                instances = instances.filter((Q(BrandName__icontains=product_name)))[
                    :10
                ]
            else:
                instances = Brand.objects.filter(CompanyID=CompanyID, BranchID=BranchID)
                instances = instances.filter((Q(BrandName__icontains=product_name)))
            serialized = BrandRestSerializer(
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
            "message": "Branch You Enterd is not Valid!!!",
        }

        return Response(response_data, status=status.HTTP_200_OK)
