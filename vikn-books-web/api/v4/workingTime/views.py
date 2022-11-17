from django.contrib.auth.models import User
from brands import models
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v4.workingTime import serializers
from api.v4.workingTime.functions import generate_serializer_errors
from rest_framework import status
from api.v4.workingTime.functions import get_auto_id
from main.functions import get_company, activity_log
from main.functions import get_location, get_device_name
import datetime


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_working_time(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    BranchID = data['BranchID']
    Action = "A"

    today = datetime.datetime.now()
    serialized = serializers.WorkingTimeSerializer(data=request.data)
    if serialized.is_valid():
        Name = serialized.data['Name']
        ShiftStartTime = serialized.data['ShiftStartTime']
        ShiftEndTime = serialized.data['ShiftEndTime']
        BreakStartTime = serialized.data['BreakStartTime']
        BreakEndTime = serialized.data['BreakEndTime']
        print(ShiftStartTime,'ShiftStartTime')

        if not models.WorkingTime.objects.filter(BranchID=BranchID, CompanyID=CompanyID, Name__iexact=Name).exists():
            instance = models.WorkingTime.objects.create(
                CompanyID=CompanyID,
                BranchID=BranchID,
                Name=Name,
                ShiftStartTime=ShiftStartTime,
                ShiftEndTime=ShiftEndTime,
                BreakStartTime=BreakStartTime,
                BreakEndTime=BreakEndTime,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
            )

            models.WorkingTimeLog.objects.create(
                CompanyID=CompanyID,
                TransactionID=instance.id,
                BranchID=BranchID,
                Name=Name,
                ShiftStartTime=ShiftStartTime,
                ShiftEndTime=ShiftEndTime,
                BreakStartTime=BreakStartTime,
                BreakEndTime=BreakEndTime,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
            )
            # request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Category',
                         'Create', 'Category created successfully.', 'Category saved successfully.')

            response_data = {
                "StatusCode": 6000,
                "message": "Successfully Created."
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID,
                         'Category', 'Create', 'Category name already exist.', 'same name exists.')

            response_data = {
                "StatusCode": 6001,
                "message": "Category name already exist."
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        # request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Category', 'Create',
                     'Category field not valid.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_working_time(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    BranchID = data['BranchID']

    today = datetime.datetime.now()
    serialized = serializers.WorkingTimeSerializer(data=request.data)
    instance = models.WorkingTime.objects.get(pk=pk, CompanyID=CompanyID)

    BranchID = instance.BranchID

    if serialized.is_valid():
        Name = serialized.data['Name']
        ShiftStartTime = serialized.data['ShiftStartTime']
        ShiftEndTime = serialized.data['ShiftEndTime']
        BreakStartTime = serialized.data['BreakStartTime']
        BreakEndTime = serialized.data['BreakEndTime']
        Action = 'M'
        if not models.WorkingTime.objects.filter(BranchID=BranchID, CompanyID=CompanyID, Name__iexact=Name).exclude(Name=instance.Name):
            instance.Name = Name
            instance.ShiftStartTime = ShiftStartTime
            instance.ShiftEndTime = ShiftEndTime
            instance.BreakStartTime = BreakStartTime
            instance.BreakEndTime = BreakEndTime
            instance.Action = Action
            instance.CreatedUserID = CreatedUserID
            instance.UpdatedDate = today
            instance.save()

            models.WorkingTimeLog.objects.create(
                CompanyID=CompanyID,
                TransactionID=instance.id,
                BranchID=BranchID,
                Name=Name,
                ShiftStartTime=ShiftStartTime,
                ShiftEndTime=ShiftEndTime,
                BreakStartTime=BreakStartTime,
                BreakEndTime=BreakEndTime,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
            )
            # request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID,
                         'Category', 'Edit', 'Category edited successfully.', 'Category saved successfully.')

            response_data = {
                "StatusCode": 6000,
                "message": "Successfully Updated."
            }

            return Response(response_data, status=status.HTTP_200_OK)

        elif models.WorkingTime.objects.filter(BranchID=BranchID, CompanyID=CompanyID, Name__iexact=Name).exists():
            # request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Category',
                         'Edit', 'Category already exists.', 'Category name already exist in this branch.')

            response_data = {
                "StatusCode": 6001,
                "message": "Category name already exist in this branch"
            }
            return Response(response_data, status=status.HTTP_200_OK)

        else:
            instance.Name = Name,
            instance.ShiftStartTime = ShiftStartTime,
            instance.ShiftEndTime = ShiftEndTime,
            instance.BreakStartTime = BreakStartTime,
            instance.BreakEndTime = BreakEndTime,
            instance.Action = Action
            instance.UpdatedDate = today
            instance.CreatedUserID = CreatedUserID
            instance.save()

            models.WorkingTimeLog.objects.create(
                CompanyID=CompanyID,
                TransactionID=instance.id,
                BranchID=BranchID,
                Name=Name,
                ShiftStartTime=ShiftStartTime,
                ShiftEndTime=ShiftEndTime,
                BreakStartTime=BreakStartTime,
                BreakEndTime=BreakEndTime,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
            )
            # request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID,
                         'Category', 'Edit', 'Category edited successfully.', 'Category saved successfully.')

            response_data = {
                "StatusCode": 6000,
                "message": "Successfully Updated."
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        # request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Category', 'Edit',
                     'Category edited failed.', generate_serializer_errors(serialized._errors))

        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def working_times(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    # device_name = get_device_name(request)
    # print(device_name)

    serializer = serializers.ListSerializer(data=request.data)
    if serializer.is_valid():
        BranchID = serializer.data['BranchID']
        if models.WorkingTime.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            instances = models.WorkingTime.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)
            serialized = serializers.WorkingTimeRestSerializer(
                instances, many=True)

            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Category', 'View', 'Category list', 'The user viewed brands')

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information',
                         CreatedUserID, 'Category', 'View', 'Category list', 'Category not found')
            response_data = {
                "StatusCode": 6001,
                "message": "Brands Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        # request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information',
                     CreatedUserID, 'Category', 'View', 'Category list', 'Category not valid')
        response_data = {
            "StatusCode": 6001,
            "message": "Branch You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def working_time(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if models.WorkingTime.objects.filter(pk=pk).exists():
        instance = models.WorkingTime.objects.get(pk=pk)
        serialized = serializers.WorkingTimeRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
        # request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID,
                     'Category', 'View', 'Category Single Page', 'User viewed a Brand')
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Category Not Fount!"
        }

        # request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID,
                     'Category', 'View', 'Category Single Page', 'Category not Found!')

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_working_time(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    if models.WorkingTime.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = models.WorkingTime.objects.get(pk=pk, CompanyID=CompanyID)
        Action = "D"

        models.WorkingTimeLog.objects.create(
            CompanyID=CompanyID,
            TransactionID=instance.id,
            BranchID=instance.BranchID,
            Name=instance.Name,
            ShiftStartTime=instance.ShiftStartTime,
            ShiftEndTime=instance.ShiftEndTime,
            BreakStartTime=instance.BreakStartTime,
            BreakEndTime=instance.BreakEndTime,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            Action=Action,
        )
        instance.delete()
        # request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Category',
                     'Delete', 'Category Deleted Successfully', 'Category Deleted Successfully')

        response_data = {
            "StatusCode": 6000,
            "message": "Category Deleted Successfully!"
        }

    else:
        # request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID,
                     'Category', 'Delete', 'Category Deleted Failed', 'Category Not Found!')
        response_data = {
            "StatusCode": 6001,
            "message": "Category Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
