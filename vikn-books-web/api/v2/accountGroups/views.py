from brands.models import AccountGroup, AccountGroup_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v2.accountGroups.serializers import AccountGroupSerializer, AccountGroupRestSerializer
from api.v2.accountGroups.functions import generate_serializer_errors
from rest_framework import status
from api.v2.accountGroups.functions import get_auto_id
from django.shortcuts import get_object_or_404
from users.models import CustomerUser, DatabaseStore
from main.functions import get_company,activity_log
import datetime



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_accountGroup(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    
    today = datetime.datetime.now()
    serialized = AccountGroupSerializer(data=request.data)
    if serialized.is_valid():

        AccountGroupName = serialized.data['AccountGroupName']
        GroupCode = serialized.data['GroupCode']
        AccountGroupUnder = serialized.data['AccountGroupUnder']
        Notes = serialized.data['Notes']
        IsActive = serialized.data['IsActive']
        IsDefault = serialized.data['IsDefault']

        Action = "A"

        AccountGroupID = get_auto_id(AccountGroup,CompanyID)

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

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'AccountGroup', 'Create', 'AccountGroup created successfully.', 'AccountGroup saved successfully.')

        data = {"AccountGroupID" : AccountGroupID}
        data.update(serialized.data)
        response_data = {
            "StatusCode" : 6000,
            "data" : data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'AccountGroup', 'Create', 'AccountGroup field not valid.',generate_serializer_errors(serialized._errors))

        response_data = {
            "StatusCode" : 6001,
            "message" : generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_accountGroup(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = AccountGroupSerializer(data=request.data)
    instance = None
    if AccountGroup.objects.filter(pk=pk).exists():
        instance = AccountGroup.objects.get(pk=pk)

        AccountGroupName = instance.AccountGroupName
        if serialized.is_valid():
            AccountGroupName = serialized.data['AccountGroupName']
            GroupCode = serialized.data['GroupCode']
            AccountGroupUnder = serialized.data['AccountGroupUnder']
            Notes = serialized.data['Notes']
            IsActive = serialized.data['IsActive']
            IsDefault = serialized.data['IsDefault']

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

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'AccountGroup', 'Edit', 'AccountGroup Updated successfully.', 'AccountGroup saved successfully.')

            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'AccountGroup', 'Edit', 'AccountGroup Updated Failed.', generate_serializer_errors(serialized._errors))
            response_data = {
                "StatusCode" : 6001,
                "message" : generate_serializer_errors(serialized._errors)
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'AccountGroup', 'Edit', 'AccountGroup Updated Failed.', 'AccountGroup Not Found!.')
        response_data = {
            "StatusCode" : 6001,
            "message" : "Account Group Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def accountGroups(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    exclude_item = [0,1,2]

    instances = AccountGroup.objects.filter(CompanyID=CompanyID).exclude(AccountGroupID__in=exclude_item)
    serialized = AccountGroupRestSerializer(instances,many=True,context = {"CompanyID": CompanyID })

    #request , company, log_type, user, source, action, message, description
    activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'AccountGroup', 'View', 'AccountGroup List', 'The user viewed AccountGroups')
    response_data = {
        "StatusCode" : 6000,
        "data" : serialized.data
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def accountGroup(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if AccountGroup.objects.filter(pk=pk,CompanyID=CompanyID).exists():
        instance = AccountGroup.objects.get(pk=pk,CompanyID=CompanyID)
        serialized = AccountGroupRestSerializer(instance,context = {"CompanyID": CompanyID })

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'AccountGroup', 'View', 'AccountGroup Single page', 'The user viewed AccountGroup')
        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'AccountGroup', 'View', 'AccountGroup Single page', 'AccountGroup Not Found!')
        response_data = {
            "StatusCode" : 6001,
            "message" : "Account Group Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_accountGroup(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if AccountGroup.objects.filter(pk=pk,CompanyID=CompanyID).exists():
        instance = AccountGroup.objects.get(pk=pk,CompanyID=CompanyID)
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
            CreatedDate=today
            )
        response_data = {
            "StatusCode" : 6000,
            "title" : "Success",
            "message" : "Account Group Deleted Successfully!"
        }
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'AccountGroup', 'Delete', 'AccountGroup Deleted', 'AccountGroup Deleted Successfully!')
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'AccountGroup', 'Delete', 'AccountGroup Deleted failed', 'AccountGroup Deleted failed,AccountGroup Not Found!')
        response_data = {
            "StatusCode" : 6001,
            "title" : "Failed",
            "message" : "Account Group Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)