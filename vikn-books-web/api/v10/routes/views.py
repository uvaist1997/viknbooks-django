from brands.models import Route, Route_Log, Parties, Branch
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes,authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from api.v10.routes.serializers import RouteSerializer, RouteRestSerializer
from api.v10.brands.serializers import ListSerializer
from api.v10.routes.functions import generate_serializer_errors
from rest_framework import status
from api.v10.routes.functions import get_auto_id
import datetime
from main.functions import get_company, activity_log
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Prefetch
from api.v10.branchs.functions import get_branch_settings
from api.v10.parties.functions import get_PartyCode


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
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def create_route(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = RouteSerializer(data=request.data)

    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        RouteName = serialized.data['RouteName']
        Notes = serialized.data['Notes']

        Action = 'A'

        RouteID = get_auto_id(Route, BranchID, CompanyID)

        is_nameExist = False

        RouteNameLow = RouteName.lower()
        customersForAllBranches = get_branch_settings(
            CompanyID, "customersForAllBranches	")

        suppliersForAllBranches = get_branch_settings(
            CompanyID, "suppliersForAllBranches	")

        if customersForAllBranches == True or suppliersForAllBranches == True:
            routes = Route.objects.filter(CompanyID=CompanyID)
        else:
            routes = Route.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

        for route in routes:
            route_name = route.RouteName

            routeName = route_name.lower()

            if RouteNameLow == routeName:
                is_nameExist = True

        if not is_nameExist:

            # serialized.save(UnitID=UnitID,CreatedDate=today,ModifiedDate=today)
            Route.objects.create(
                RouteID=RouteID,
                BranchID=BranchID,
                RouteName=RouteName,
                Notes=Notes,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            Route_Log.objects.create(
                BranchID=BranchID,
                TransactionID=RouteID,
                RouteName=RouteName,
                Notes=Notes,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Route',
                         'Create', 'Route created successfully.', 'Route saved successfully.')

            data = {"RouteID": RouteID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID,
                         'Route', 'Create', 'Route created Failed.', 'Route Name Already Exist')
            response_data = {
                "StatusCode": 6001,
                "message": "Route Name Already Exist!!!"
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Route', 'Create',
                     'Route created Failed.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def edit_route(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = RouteSerializer(data=request.data)
    instance = Route.objects.get(CompanyID=CompanyID, pk=pk)

    BranchID = instance.BranchID
    RouteID = instance.RouteID
    instanceRouteName = instance.RouteName

    if serialized.is_valid():

        RouteName = serialized.data['RouteName']
        Notes = serialized.data['Notes']

        Action = 'M'

        is_nameExist = False
        route_ok = False

        RouteNameLow = RouteName.lower()
        customersForAllBranches = get_branch_settings(
            CompanyID, "customersForAllBranches	")

        suppliersForAllBranches = get_branch_settings(
            CompanyID, "suppliersForAllBranches	")

        if customersForAllBranches == True or suppliersForAllBranches == True:
            routes = Route.objects.filter(CompanyID=CompanyID)
        else:
            routes = Route.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

        for route in routes:
            route_name = route.RouteName

            routeName = route_name.lower()

            if RouteNameLow == routeName:
                is_nameExist = True

            if instanceRouteName.lower() == RouteNameLow:

                route_ok = True

        if route_ok:

            instance.RouteName = RouteName
            instance.Notes = Notes
            instance.Action = Action
            instance.CreatedUserID = CreatedUserID
            instance.UpdatedDate = today
            instance.save()

            Route_Log.objects.create(
                BranchID=BranchID,
                TransactionID=RouteID,
                RouteName=RouteName,
                Notes=Notes,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Route',
                         'Edit', 'Route Updated successfully.', 'Route Updated successfully.')

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:

            if is_nameExist:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Route',
                             'Edit', 'Route Updated Failed.', 'Route Name Already exist with this Branch')
                response_data = {
                    "StatusCode": 6001,
                    "message": "Route Name Already exist with this Branch"
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                instance.RouteName = RouteName
                instance.Notes = Notes
                instance.Action = Action
                instance.CreatedUserID = CreatedUserID
                instance.UpdatedDate = today
                instance.save()

                Route_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=RouteID,
                    RouteName=RouteName,
                    Notes=Notes,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Route',
                             'Edit', 'Route Updated successfully.', 'Route Updated successfully.')

                response_data = {
                    "StatusCode": 6000,
                    "data": serialized.data
                }

                return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Route', 'Edit',
                     'Route Updated Failed.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def routes(request):
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
    
    try:
        PartyType = data["PartyType"]
    except:
        PartyType = "customer"

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        customersForAllBranches = get_branch_settings(
            CompanyID, "customersForAllBranches")

        suppliersForAllBranches = get_branch_settings(
            CompanyID, "suppliersForAllBranches")

        if customersForAllBranches == True or suppliersForAllBranches == True:
            routes = Route.objects.filter(CompanyID=CompanyID)
        else:
            routes = Route.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
        if routes:
            if page_number and items_per_page:
                instances = routes
                count = len(instances)
                ledger_sort_pagination = list_pagination(
                    instances,
                    items_per_page,
                    page_number
                )
            else:
                ledger_sort_pagination = routes
                count = len(ledger_sort_pagination)
            serialized = RouteRestSerializer(ledger_sort_pagination, many=True)
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Route',
                         'List', 'Route List Viewed successfully.', 'Route List Viewed successfully.')
            branch_state = ""
            if Branch.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
                branch_ins = Branch.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID)
                if branch_ins.state:
                    branch_state = branch_ins.state.id

            PartyCode = get_PartyCode(Parties, BranchID, CompanyID, PartyType)
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "count": count,
                "branch_state": branch_state,
                "PartyCode":PartyCode            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Route',
                         'List', 'Route List Viewed Failed.', 'Route Not Found in this Branch')
            response_data = {
                "StatusCode": 6001,
                "message": "Route Not Found in this Branch!"
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
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def route(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    if Route.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = Route.objects.get(CompanyID=CompanyID, pk=pk)
        serialized = RouteRestSerializer(instance)

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Route',
                     'View', 'Route Single Viewed successfully.', 'Route Single Viewed successfully.')
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Route Not Fount!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def delete_route(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    try:
        selecte_ids = data['selecte_ids']
    except:
        selecte_ids = []

    if selecte_ids:
        if Route.objects.filter(CompanyID=CompanyID, pk__in=selecte_ids).exists():
            instances = Route.objects.filter(pk__in=selecte_ids)
    else:
        if Route.objects.filter(CompanyID=CompanyID, pk=pk).exists():
            instances = Route.objects.filter(pk=pk)

    if pk == "1":
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Route',
                     'Delete', 'Route Deleted Failed.', 'User Tried to Delete Default Route!')
        response_data = {
            "StatusCode": 6001,
            "message": "You Can't Delete this Route!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        if instances:
            for instance in instances:
                BranchID = instance.BranchID
                RouteID = instance.RouteID
                RouteName = instance.RouteName
                Notes = instance.Notes
                Action = "D"

                if not Parties.objects.filter(CompanyID=CompanyID, RouteID=RouteID).exists():
                    instance.delete()
                    Route_Log.objects.create(
                        BranchID=BranchID,
                        TransactionID=RouteID,
                        RouteName=RouteName,
                        Notes=Notes,
                        CreatedUserID=CreatedUserID,
                        Action=Action,
                        CreatedDate=today,
                        UpdatedDate=today,
                        CompanyID=CompanyID,
                    )

                    #request , company, log_type, user, source, action, message, description
                    activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Route',
                                 'Delete', 'Route Deleted Successfully.', 'Route Deleted Successfully!')
                    response_data = {
                        "StatusCode": 6000,
                        "title": "Success",
                        "message": "Route Deleted Successfully!"
                    }
                else:
                    #request , company, log_type, user, source, action, message, description
                    activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Route', 'Delete',
                                 'Route Deleted Failed.', "can't Delete this Route,Party exist with this route")
                    response_data = {
                        "StatusCode": 6001,
                        "title": "Failed",
                        "message": "You can't Delete this Route,Party exist with this route id!!"
                    }
        else:
            response_data = {
                "StatusCode": 6001,
                "title": "Failed",
                "message": "Route Not Fount!"
            }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def search_routes(request):
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
        customersForAllBranches = get_branch_settings(
            CompanyID, "customersForAllBranches	")

        suppliersForAllBranches = get_branch_settings(
            CompanyID, "suppliersForAllBranches	")

        if customersForAllBranches == True or suppliersForAllBranches == True:
            routes = Route.objects.filter(CompanyID=CompanyID)
        else:
            routes = Route.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)
        if routes:
            instances = routes

            if length < 3:
                if param == "RouteName":
                    instances = instances.filter(
                        (Q(RouteName__icontains=product_name)))[:10]
            else:
                if param == "RouteName":
                    instances = instances.filter(
                        (Q(RouteName__icontains=product_name)))

            serialized = RouteRestSerializer(instances, many=True, context={
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
