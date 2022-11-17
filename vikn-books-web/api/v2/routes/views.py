from brands.models import Route, Route_Log, Parties
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v2.routes.serializers import RouteSerializer, RouteRestSerializer
from api.v2.brands.serializers import ListSerializer
from api.v2.routes.functions import generate_serializer_errors
from rest_framework import status
from api.v2.routes.functions import get_auto_id
import datetime
from main.functions import get_company, activity_log


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
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

        RouteID = get_auto_id(Route,BranchID,CompanyID)

        is_nameExist = False

        RouteNameLow = RouteName.lower()

        routes = Route.objects.filter(CompanyID=CompanyID,BranchID=BranchID)

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
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Route', 'Create', 'Route created successfully.', 'Route saved successfully.')

            data = {"RouteID" : RouteID}
            data.update(serialized.data)
            response_data = {
                "StatusCode" : 6000,
                "data" : data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Route', 'Create', 'Route created Failed.', 'Route Name Already Exist')
            response_data = {
            "StatusCode" : 6001,
            "message" : "Route Name Already Exist!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Route', 'Create', 'Route created Failed.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode" : 6001,
            "message" : generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_route(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = RouteSerializer(data=request.data)
    instance = Route.objects.get(CompanyID=CompanyID,pk=pk)
    
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

        routes = Route.objects.filter(CompanyID=CompanyID,BranchID=BranchID)

        for route in routes:
            route_name = route.RouteName

            routeName = route_name.lower()

            if RouteNameLow == routeName:
                is_nameExist = True

            if instanceRouteName.lower() == RouteNameLow:

                route_ok = True


        if  route_ok:

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
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Route', 'Edit', 'Route Updated successfully.', 'Route Updated successfully.')

            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:


            if is_nameExist:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Route', 'Edit', 'Route Updated Failed.', 'Route Name Already exist with this Branch')
                response_data = {
                    "StatusCode" : 6001,
                    "message" : "Route Name Already exist with this Branch"
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
                activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Route', 'Edit', 'Route Updated successfully.', 'Route Updated successfully.')

                response_data = {
                    "StatusCode" : 6000,
                    "data" : serialized.data
                }

                return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Route', 'Edit', 'Route Updated Failed.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode" : 6001,
            "message" : generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def routes(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if Route.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
            instances = Route.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
            serialized = RouteRestSerializer(instances,many=True)
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Route', 'List', 'Route List Viewed successfully.', 'Route List Viewed successfully.')
            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Route', 'List', 'Route List Viewed Failed.', 'Route Not Found in this Branch')
            response_data = {
            "StatusCode" : 6001,
            "message" : "Route Not Found in this Branch!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def route(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    if Route.objects.filter(CompanyID=CompanyID,pk=pk).exists():
        instance = Route.objects.get(CompanyID=CompanyID,pk=pk)
        serialized = RouteRestSerializer(instance)

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Route', 'View', 'Route Single Viewed successfully.', 'Route Single Viewed successfully.')
        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Route Not Fount!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
    

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_route(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    
    if pk == "1":
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Route', 'Delete', 'Route Deleted Failed.', 'User Tried to Delete Default Route!')
        response_data = {
                "StatusCode" : 6001,
                "message" : "You Can't Delete this Route!!!"
            }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        if Route.objects.filter(CompanyID=CompanyID,pk=pk).exists():
            instance = Route.objects.get(CompanyID=CompanyID,pk=pk)
            BranchID = instance.BranchID
            RouteID = instance.RouteID
            RouteName = instance.RouteName
            Notes = instance.Notes
            Action = "D"

            if not Parties.objects.filter(CompanyID=CompanyID,RouteID=RouteID).exists():

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
                activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Route', 'Delete', 'Route Deleted Successfully.', 'Route Deleted Successfully!')
                response_data = {
                    "StatusCode" : 6000,
                    "title" : "Success",
                    "message" : "Route Deleted Successfully!"
                }
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Route', 'Delete', 'Route Deleted Failed.', "can't Delete this Route,Party exist with this route")
                response_data = {
                    "StatusCode" : 6001,
                    "title" : "Failed",
                    "message" : "You can't Delete this Route,Party exist with this route id!!"
                }
        else:
            response_data = {
                "StatusCode" : 6001,
                "title" : "Failed",
                "message" : "Route Not Fount!"
            }

        return Response(response_data, status=status.HTTP_200_OK)