from brands.models import Unit, Unit_Log, Product, PriceList
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v4.units.serializers import UnitSerializer, UnitRestSerializer, ListSerializer
from api.v4.units.functions import generate_serializer_errors, get_auto_id
from rest_framework import status
from main.functions import get_company, activity_log
import datetime
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
def create_unit(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = UnitSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        UnitName = serialized.data['UnitName']
        Notes = serialized.data['Notes']

        Action = 'A'
        UnitID = get_auto_id(Unit, BranchID, CompanyID)

        is_nameExist = False

        UnitNameLow = UnitName.lower()

        if Unit.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            units = Unit.objects.filter(BranchID=BranchID, CompanyID=CompanyID)
            for unit in units:
                unit_name = unit.UnitName

                unitName = unit_name.lower()

                if UnitNameLow == unitName:
                    is_nameExist = True

        # if not Unit.objects.filter(UnitName=UnitName,BranchID=BranchID).exists():

            # serialized.save(UnitID=UnitID,CreatedDate=today,ModifiedDate=today)

        if is_nameExist == False:

            Unit.objects.create(
                UnitID=UnitID,
                BranchID=BranchID,
                UnitName=UnitName,
                Notes=Notes,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID
            )

            Unit_Log.objects.create(
                BranchID=BranchID,
                TransactionID=UnitID,
                UnitName=UnitName,
                Notes=Notes,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID
            )

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Units',
                         'Create', 'Units created successfully.', 'Units saved successfully.')

            data = {"UnitID": UnitID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID,
                         'Units', 'Create', 'Units created Failed.', 'Unit Name Already Exist')
            response_data = {
                "StatusCode": 6001,
                "message": "Unit Name Already Exist!!!"
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Units', 'Create',
                     'Units created Failed.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_unit(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = UnitSerializer(data=request.data)
    instance = Unit.objects.get(pk=pk, CompanyID=CompanyID)

    BranchID = instance.BranchID
    UnitID = instance.UnitID
    instanceUnitName = instance.UnitName

    if serialized.is_valid():
        UnitName = serialized.data['UnitName']
        Notes = serialized.data['Notes']

        Action = 'M'

        is_nameExist = False
        unit_ok = False

        UnitNameLow = UnitName.lower()

        units = Unit.objects.filter(BranchID=BranchID, CompanyID=CompanyID)

        for unit in units:
            unit_name = unit.UnitName

            unitName = unit_name.lower()
            if UnitNameLow == unitName:
                is_nameExist = True

            if instanceUnitName.lower() == UnitNameLow:

                unit_ok = True

        if unit_ok:

            instance.UnitName = UnitName
            instance.Notes = Notes
            instance.Action = Action
            instance.CreatedUserID = CreatedUserID
            instance.UpdatedDate = today
            instance.save()

            Unit_Log.objects.create(
                BranchID=BranchID,
                TransactionID=UnitID,
                UnitName=UnitName,
                Notes=Notes,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID
            )
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Units',
                         'Edit', 'Units Updated successfully.', 'Units Updated successfully.')
            data = {"UnitID": UnitID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Units',
                         'Edit', 'Units Updated Failed.', 'Unit Name Already exist with this Branch')

            if is_nameExist == True:
                response_data = {
                    "StatusCode": 6001,
                    "message": "Unit Name Already exist with this Branch"
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                instance.UnitName = UnitName
                instance.Notes = Notes
                instance.Action = Action
                instance.UpdatedDate = today
                instance.CreatedUserID = CreatedUserID
                instance.save()

                Unit_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=UnitID,
                    UnitName=UnitName,
                    Notes=Notes,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    Action=Action,
                    CompanyID=CompanyID
                )

                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Units',
                             'Edit', 'Units Updated successfully.', 'Units Updated successfully.')

                data = {"UnitID": UnitID}
                data.update(serialized.data)
                response_data = {
                    "StatusCode": 6000,
                    "data": data
                }

                return Response(response_data, status=status.HTTP_200_OK)

    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Units', 'Edit',
                     'Units Updated Failed.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def units(request):
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
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if Unit.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():

            if page_number and items_per_page:
                instances = Unit.objects.filter(
                    BranchID=BranchID, CompanyID=CompanyID)
                count = len(instances)
                ledger_sort_pagination = list_pagination(
                    instances,
                    items_per_page,
                    page_number
                )
            else:
                ledger_sort_pagination = Unit.objects.filter(
                    BranchID=BranchID, CompanyID=CompanyID)
                count = len(ledger_sort_pagination)
            serialized = UnitRestSerializer(ledger_sort_pagination, many=True)

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Units',
                         'List', 'Units List Viewed Successfully.', "Units List Viewed Successfully.")
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "count": count
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Units',
                         'List', 'Units List Viewed Failed.', "Units Not Found in this Branch")
            response_data = {
                "StatusCode": 6001,
                "message": "Units Not Found in this Branch!"
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
def unit(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if Unit.objects.filter(pk=pk).exists():
        instance = Unit.objects.get(pk=pk)
        serialized = UnitRestSerializer(instance)

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Units',
                     'View', 'Units Single Viewed Successfully.', "Units Single Viewed Successfully.")
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Unit Not Fount!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_unit(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if pk == "1":
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Units',
                     'Delete', 'Units Deleted Failed.', "User Tried to Delete Default Unit")
        response_data = {
            "StatusCode": 6001,
            "message": "You Can't Delete this Unit!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        if Unit.objects.filter(pk=pk).exists():
            instance = Unit.objects.get(pk=pk)
            BranchID = instance.BranchID
            UnitID = instance.UnitID
            UnitName = instance.UnitName
            Notes = instance.Notes
            Action = "D"

            if not PriceList.objects.filter(BranchID=BranchID, UnitID=UnitID, CompanyID=CompanyID).exists():

                instance.delete()

                Unit_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=UnitID,
                    UnitName=UnitName,
                    Notes=Notes,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    Action=Action,
                    CompanyID=CompanyID
                )

                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Units',
                             'Delete', 'Units Deleted Successfully.', "Units Deleted Successfully.")

                response_data = {
                    "StatusCode": 6000,
                    "message": "Unit Deleted Successfully!"
                }
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Units', 'Delete',
                             'Units Deleted Failed.', "can't Delete this Unit,Product exist with this unit")
                response_data = {
                    "StatusCode": 6001,
                    "message": "You can't Delete this Unit,Product exist with this unit!"
                }
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Unit Not Found!"
            }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def search_units(request):
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
        if Unit.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            instances = Unit.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

            if length < 3:
                if param == "UnitName":
                    instances = instances.filter(
                        (Q(UnitName__icontains=product_name)))[:10]
            else:
                if param == "UnitName":
                    instances = instances.filter(
                        (Q(UnitName__icontains=product_name)))

            serialized = UnitRestSerializer(instances, many=True, context={
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
