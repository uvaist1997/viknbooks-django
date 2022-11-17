from brands.models import Branch, Branch_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v6.branchs.serializers import BranchSerializer, BranchRestSerializer
from api.v6.branchs.functions import generate_serializer_errors
from rest_framework import status
from api.v6.branchs.functions import get_auto_id
from main.functions import get_company
import datetime
from main.functions import get_company, activity_log


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_branch(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = BranchSerializer(data=request.data)
    if serialized.is_valid():

        BranchName = serialized.data['BranchName']
        BranchLocation = serialized.data['BranchLocation']

        Action = "A"

        BranchID = get_auto_id(Branch, CompanyID)

        Branch.objects.create(
            BranchID=BranchID,
            BranchName=BranchName,
            BranchLocation=BranchLocation,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            CompanyID=CompanyID,
        )

        Branch_Log.objects.create(
            TransactionID=BranchID,
            BranchName=BranchName,
            BranchLocation=BranchLocation,
            Action=Action,
            CreatedUserID=CreatedUserID,
            UpdatedDate=today,
            CompanyID=CompanyID,
        )

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Branch',
                     'Create', 'Branch created successfully.', 'Branch saved successfully.')

        data = {"BranchID": BranchID}
        data.update(serialized.data)
        response_data = {
            "StatusCode": 6000,
            "data": data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Branch', 'Create',
                     'Branch created failed.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_branch(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = BranchSerializer(data=request.data)
    instance = None
    if Branch.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = Branch.objects.get(pk=pk, CompanyID=CompanyID)

    if instance:
        BranchID = instance.BranchID
        CreatedUserID = instance.CreatedUserID

        Action = "M"

        instance.Action = Action
        instance.CreatedUserID = CreatedUserID
        instance.UpdatedDate = today
        instance.save()
        if serialized.is_valid():
            BranchName = serialized.data['BranchName']
            BranchLocation = serialized.data['BranchLocation']

            serialized.update(instance, serialized.data)
            Branch_Log.objects.create(
                TransactionID=BranchID,
                BranchName=BranchName,
                BranchLocation=BranchLocation,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Branch',
                         'Edit', 'Branch Updated Successfully.', "Branch Updated Successfully.")

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Branch', 'Edit',
                         'Branch Updated failed.', generate_serializer_errors(serialized._errors))
            response_data = {
                "StatusCode": 6001,
                "message": generate_serializer_errors(serialized._errors)
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID,
                     'Branch', 'Edit', 'Branch Updated failed.', "Branch Not Found!")
        response_data = {
            "StatusCode": 6001,
            "message": "Branch Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def branchs(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instances = Branch.objects.filter()
    serialized = BranchRestSerializer(instances, many=True)
    #request , company, log_type, user, source, action, message, description
    activity_log(request._request, CompanyID, 'Information', CreatedUserID,
                 'Branch', 'List VIew', 'Branch List Viewed.', "Branch List Viewed.")
    response_data = {
        "StatusCode": 6000,
        "data": serialized.data
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def branch(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if Branch.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = Branch.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = BranchRestSerializer(instance)
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Branch',
                     'VIew', 'Branch Single Page Viewed.', 'Branch Single Page Viewed.')
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Branch',
                     'VIew', 'Branch Single Page Viewed Failed.', 'Branch Not Found!')
        response_data = {
            "StatusCode": 6001,
            "message": "Branch Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_branch(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if Branch.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = Branch.objects.get(pk=pk, CompanyID=CompanyID)
        BranchID = instance.BranchID
        BranchName = instance.BranchName
        BranchLocation = instance.BranchLocation
        Action = "D"

        instance.delete()

        Branch_Log.objects.create(
            TransactionID=BranchID,
            BranchName=BranchName,
            BranchLocation=BranchLocation,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            CompanyID=CompanyID,
        )

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Branch',
                     'Deleted', "Branch Deleted Successfully!", "Branch Deleted Successfully!")
        response_data = {
            "StatusCode": 6000,
            "message": "Branch Deleted Successfully!"
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID,
                     'Branch', 'Delete', 'Branch Deleted Failed.', 'Branch Not Found!')
        response_data = {
            "StatusCode": 6001,
            "message": "Branch Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
# @renderer_classes((JSONRenderer,))
# def get_batch_value(request):
#     data = request.data
#     CompanyID = data['CompanyID']
#     CompanyID = get_company(CompanyID)
#     BranchID = data['BranchID']

#     if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
#         check_EnableProductBatchWise = GeneralSettings.objects.get(
#             CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
#     if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:

#     response_data = {
#         "StatusCode": 6000
#     }

#     return Response(response_data, status=status.HTTP_200_OK)
