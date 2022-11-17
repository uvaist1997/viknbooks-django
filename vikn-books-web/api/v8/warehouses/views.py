from brands.models import POS_Settings,Warehouse, Warehouse_Log, SalesMaster, PurchaseMaster, StockPosting, UserTable, GeneralSettings
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v8.warehouses.serializers import WarehouseSerializer, WarehouseRestSerializer
from api.v8.brands.serializers import ListSerializer
from api.v8.warehouses.functions import generate_serializer_errors
from rest_framework import status
from api.v8.warehouses.functions import get_auto_id
import datetime
from main.functions import get_company, activity_log
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Prefetch


def call_paginator_all(model_object, page_number, items_per_page):
    paginator = Paginator(model_object, items_per_page)
    content = paginator.page(page_number)
    return content


def list_pagination(list_value, items_per_page, page_no):
    paginator_object = Paginator(list_value, items_per_page)
    get_value = paginator_object.page(page_no).object_list
    return get_value


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_warehouse(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    serialized = WarehouseSerializer(data=request.data)

    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        WarehouseName = serialized.data['WarehouseName']
        Notes = serialized.data['Notes']

        Action = "A"

        WarehouseID = get_auto_id(Warehouse, BranchID, CompanyID)
        if not Warehouse.objects.filter(CompanyID=CompanyID, BranchID=BranchID, WarehouseName__iexact=WarehouseName):

            # serialized.save(UnitID=UnitID,CreatedDate=today,ModifiedDate=today)
            Warehouse.objects.create(
                WarehouseID=WarehouseID,
                BranchID=BranchID,
                WarehouseName=WarehouseName,
                Notes=Notes,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID
            )

            Warehouse_Log.objects.create(
                BranchID=BranchID,
                TransactionID=WarehouseID,
                WarehouseName=WarehouseName,
                Notes=Notes,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID
            )

            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Warehouse',
            #              'Create', 'Warehouse created successfully.', 'Warehouse saved successfully.')

            data = {"WarehouseID": WarehouseID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Warehouse',
                         'Create', 'Warehouse created Failed.', 'WareHouse Name Already Exist')
            response_data = {
                "StatusCode": 6001,
                "message": "Warehouse name already exists."
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Warehouse', 'Create',
                     'Warehouse created Failed.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_warehouse(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    serialized = WarehouseSerializer(data=request.data)
    instance = Warehouse.objects.get(CompanyID=CompanyID, pk=pk)

    BranchID = instance.BranchID
    WarehouseID = instance.WarehouseID
    instanceWarehouseName = instance.WarehouseName

    if serialized.is_valid():

        WarehouseName = serialized.data['WarehouseName']
        Notes = serialized.data['Notes']

        Action = "M"

        if not Warehouse.objects.filter(CompanyID=CompanyID, BranchID=BranchID, WarehouseName__iexact=WarehouseName).exclude(WarehouseName=instanceWarehouseName):
            instance.WarehouseName = WarehouseName
            instance.Notes = Notes
            instance.Action = Action
            instance.CreatedUserID = CreatedUserID
            instance.UpdatedDate = today
            instance.save()

            Warehouse_Log.objects.create(
                BranchID=BranchID,
                TransactionID=WarehouseID,
                WarehouseName=WarehouseName,
                Notes=Notes,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID
            )

            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Warehouse',
            #              'Edit', 'Warehouse Updated Successfully.', 'Warehouse Updated Successfully.')

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Warehouse', 'Edit',
                         'Warehouse Updated Failed.', 'Warehouse Name Already exist with this Branch')
            if Warehouse.objects.filter(CompanyID=CompanyID, BranchID=BranchID, WarehouseName__iexact=WarehouseName):
                response_data = {
                    "StatusCode": 6001,
                    "message": "Warehouse Name Already exist with this Branch"
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                instance.WarehouseName = WarehouseName
                instance.Notes = Notes
                instance.Action = Action
                instance.CreatedUserID = CreatedUserID
                instance.UpdatedDate = today
                instance.save()

                Warehouse_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=WarehouseID,
                    WarehouseName=WarehouseName,
                    Notes=Notes,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID
                )

                #request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Warehouse',
                #              'Edit', 'Warehouse Updated Successfully.', 'Warehouse Updated Successfully')

                response_data = {
                    "StatusCode": 6000,
                    "data": serialized.data
                }

                return Response(response_data, status=status.HTTP_200_OK)

    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Warehouse', 'Edit',
                     'Warehouse Updated Failed.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def warehouses(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    try:
        page_number = data['page_no']
    except:
        page_number = ""

    try:
        items_per_page = data['items_per_page']
    except:
        items_per_page = ""

    serialized1 = ListSerializer(data=request.data)
    DefaultAccountForUser = None
    Cash_Account = None
    Bank_Account = None
    Sales_Account = None
    if UserTable.objects.filter(CompanyID=CompanyID, customer__user__pk=CreatedUserID).exists():
        DefaultAccountForUser = UserTable.objects.get(
            CompanyID=CompanyID, customer__user__pk=CreatedUserID).DefaultAccountForUser
        Cash_Account = UserTable.objects.get(
            CompanyID=CompanyID, customer__user__pk=CreatedUserID).Cash_Account
        Bank_Account = UserTable.objects.get(
            CompanyID=CompanyID, customer__user__pk=CreatedUserID).Bank_Account
        Sales_Account = UserTable.objects.get(
            CompanyID=CompanyID, customer__user__pk=CreatedUserID).Sales_Account

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        POS_Warehouse = None
        if POS_Settings.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
            Pos_ins = POS_Settings.objects.filter(CompanyID=CompanyID,BranchID=BranchID).first()
            POS_Warehouse = Pos_ins.Warehouse.id

        if Warehouse.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            if page_number and items_per_page:
                instances = Warehouse.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                count = len(instances)
                ledger_sort_pagination = list_pagination(
                    instances,
                    items_per_page,
                    page_number
                )
                print(ledger_sort_pagination)
                # serialized = WarehouseRestSerializer(ledger_sort_pagination, many=True)
                # data = serialized.data
            else:
                ledger_sort_pagination = Warehouse.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                count = len(ledger_sort_pagination)
            serialized = WarehouseRestSerializer(
                ledger_sort_pagination, many=True)
            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Warehouse',
            #              'List', 'Warehouse List Viewed Successfully', "Warehouse List Viewed Successfully")

            ExpiryDays = 365
            if GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ExpiryDays").exists():
                general_ins = GeneralSettings.objects.filter(
                    CompanyID=CompanyID, SettingsType="ExpiryDays").first()
                ExpiryDays = general_ins.SettingsValue

            ShowTotalTax = False
            if GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowTotalTax").exists():
                general_ins = GeneralSettings.objects.filter(
                    CompanyID=CompanyID, SettingsType="ShowTotalTax").first()
                ShowTotalTax = general_ins.SettingsValue

            ShowTotalTaxInPurchase = False
            if GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowTotalTaxInPurchase").exists():
                general_ins = GeneralSettings.objects.filter(
                    CompanyID=CompanyID, SettingsType="ShowTotalTaxInPurchase").first()
                ShowTotalTaxInPurchase = general_ins.SettingsValue

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "DefaultAccountForUser": DefaultAccountForUser,
                "Cash_Account": Cash_Account,
                "Bank_Account": Bank_Account,
                "Sales_Account": Sales_Account,
                "ExpiryDays": ExpiryDays,
                "ShowTotalTax": ShowTotalTax,
                "ShowTotalTaxInPurchase": ShowTotalTaxInPurchase,
                "count": count,
                "POS_Warehouse":POS_Warehouse
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Warehouse',
            #              'List', 'Warehouse List Viewed Failed', "Warehouse Not Found in this Branch")
            response_data = {
                "StatusCode": 6001,
                "message": "Warehouse Not Found in this Branch!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def warehouse(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    instance = None

    if Warehouse.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = Warehouse.objects.get(CompanyID=CompanyID, pk=pk)
        serialized = WarehouseRestSerializer(instance)

        #request , company, log_type, user, source, action, message, description
        # activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Warehouse', 'View',
        #              'Warehouse Single Viewed Successfully', "Warehouse Single Viewed Successfully")
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Warehouse',
                     'View', 'Warehouse Single Viewed Failed', "Warehouse Not Found in this Branch")
        response_data = {
            "StatusCode": 6001,
            "message": "Ware House Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_warehouse(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    instances = None
    purchaseMaster_exist = None
    salesMaster_exist = None
    stockPostings_exist = None

    try:
        selecte_ids = data['selecte_ids']
    except:
        selecte_ids = []

    if pk == "1":
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Warehouse',
                     'Delete', 'Warehouse Deleted Failed', "User Tried to Delete Default Warehouse!")
        response_data = {
            "StatusCode": 6001,
            "message": "You Can't Delete this WareHouse!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        if selecte_ids:
            if Warehouse.objects.filter(CompanyID=CompanyID, pk__in=selecte_ids).exists():
                instances = Warehouse.objects.filter(pk__in=selecte_ids)
        else:
            if Warehouse.objects.filter(CompanyID=CompanyID, pk=pk).exists():
                instances = Warehouse.objects.filter(pk=pk)

        if instances:
            for instance in instances:    
                # if Warehouse.objects.filter(CompanyID=CompanyID, pk=pk).exists():
                # instance = Warehouse.objects.get(CompanyID=CompanyID, pk=pk)
                BranchID = instance.BranchID
                WarehouseID = instance.WarehouseID
                WarehouseName = instance.WarehouseName
                Notes = instance.Notes
                Action = "D"

                purchaseMaster_exist = PurchaseMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, WarehouseID=WarehouseID).exists()
                salesMaster_exist = SalesMaster.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, WarehouseID=WarehouseID).exists()
                stockPostings_exist = StockPosting.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, WareHouseID=WarehouseID).exists()

                if not purchaseMaster_exist and not salesMaster_exist and not stockPostings_exist:
                    instance.delete()

                    Warehouse_Log.objects.create(
                        BranchID=BranchID,
                        TransactionID=WarehouseID,
                        WarehouseName=WarehouseName,
                        Notes=Notes,
                        Action=Action,
                        CreatedUserID=CreatedUserID,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID
                    )

                    #request , company, log_type, user, source, action, message, description
                    activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Warehouse',
                                 'Delete', 'Warehouse Deleted Successfully', "Warehouse Deleted Successfully")
                    response_data = {
                        "StatusCode": 6000,
                        "title": "Success",
                        "message": "WareHouse Deleted Successfully!"
                    }
                else:
                    #request , company, log_type, user, source, action, message, description
                    activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Warehouse', 'Delete',
                                 'Warehouse Deleted Failed', "Cant Delete this Warehouse,this WarehouseID is using somewhere")
                    response_data = {
                        "StatusCode": 6001,
                        "title": "Failed",
                        "message": "You Cant Delete this Warehouse,this WarehouseID is using somewhere!!"
                    }
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Warehouse',
                         'Delete', 'Warehouse Deleted Failed', "WareHouse Not Found under this Branch")
            response_data = {
                "StatusCode": 6001,
                "title": "Failed",
                "message": "WareHouse Not Found!"
            }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def search_warehouses(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    product_name = data['product_name']
    length = data['length']
    param = data['param']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if Warehouse.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instances = Warehouse.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

            if length < 3:
                if param == "WarehouseName":
                    instances = instances.filter(
                        (Q(WarehouseName__icontains=product_name)))[:10]
            else:
                if param == "WarehouseName":
                    instances = instances.filter(
                        (Q(WarehouseName__icontains=product_name)))

            serialized = WarehouseRestSerializer(instances, many=True, context={
                "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding, "product_name": "product_name"})

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def list_warehouses(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    BranchID = data['BranchID']

    if Warehouse.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
        instances = Warehouse.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID)
        serialized = WarehouseRestSerializer(instances, many=True)

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Warehouses Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
