from django.contrib.auth.models import User
from brands import models
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v9.category import serializers
from api.v9.category.functions import generate_serializer_errors
from rest_framework import status
from api.v9.category.functions import get_auto_id
from main.functions import get_company, activity_log
from main.functions import get_location, get_device_name
import datetime


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_category(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    BranchID = data['BranchID']

    today = datetime.datetime.now()
    serialized = serializers.CategorySerializer(data=request.data)
    if serialized.is_valid():
        Name = serialized.data['Name']
        Code = serialized.data['Code']

        if not models.Category.objects.filter(BranchID=BranchID, CompanyID=CompanyID, Name__iexact=Name).exists():
            instance = models.Category.objects.create(
                CompanyID=CompanyID,
                BranchID=BranchID,
                Name=Name,
                Code=Code,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
            )

            models.CategoryLog.objects.create(
                CompanyID=CompanyID,
                TransactionID=instance.id,
                BranchID=BranchID,
                Name=Name,
                Code=Code,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
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
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_category(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = serializers.CategorySerializer(data=request.data)
    instance = models.Category.objects.get(pk=pk, CompanyID=CompanyID)

    BranchID = instance.BranchID

    if serialized.is_valid():
        Name = serialized.data['Name']
        Code = serialized.data['Code']
        Action = 'M'
        if not models.Category.objects.filter(BranchID=BranchID, CompanyID=CompanyID, Name__iexact=Name).exclude(Name=instance.Name):
            instance.Name = Name
            instance.Code = Code
            instance.Action = Action
            instance.CreatedUserID = CreatedUserID
            instance.UpdatedDate = today
            instance.save()

            models.CategoryLog.objects.create(
                CompanyID=CompanyID,
                TransactionID=instance.id,
                BranchID=BranchID,
                Name=Name,
                Code=Code,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
            )
            # request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID,
                         'Category', 'Edit', 'Category edited successfully.', 'Category saved successfully.')

            response_data = {
                "StatusCode": 6000,
                "message": "Successfully Updated."
            }

            return Response(response_data, status=status.HTTP_200_OK)

        elif models.Category.objects.filter(BranchID=BranchID, CompanyID=CompanyID, Name__iexact=Name).exists():
            # request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Category',
                         'Edit', 'Category already exists.', 'Category name already exist in this branch.')

            response_data = {
                "StatusCode": 6001,
                "message": "Category name already exist in this branch"
            }
            return Response(response_data, status=status.HTTP_200_OK)

        else:
            instance.Name = Name
            instance.Code = Code
            instance.Action = Action
            instance.UpdatedDate = today
            instance.CreatedUserID = CreatedUserID
            instance.save()

            models.CategoryLog.objects.create(
                BranchID=BranchID,
                TransactionID=BrandID,
                Name=Name,
                Code=Code,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID
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
def categories(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    # device_name = get_device_name(request)
    # print(device_name)

    serializer = serializers.ListSerializer(data=request.data)
    if serializer.is_valid():
        BranchID = serializer.data['BranchID']
        if models.Category.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            instances = models.Category.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)
            serialized = serializers.CategoryRestSerializer(
                instances, many=True)

            # request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Category', 'View', 'Category list', 'The user viewed Category')

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
                "message": "Category Not Found in this BranchID!"
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
def category(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if models.Category.objects.filter(pk=pk).exists():
        instance = models.Category.objects.get(pk=pk)
        serialized = serializers.CategoryRestSerializer(instance)
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
def delete_category(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    if models.Category.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = models.Category.objects.get(pk=pk, CompanyID=CompanyID)
        Action = "D"

        models.CategoryLog.objects.create(
            CompanyID=CompanyID,
            TransactionID=instance.id,
            BranchID=instance.BranchID,
            Name=instance.Name,
            Code=instance.Code,
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


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_database_sync(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    BranchID = data['BranchID']

    today = datetime.datetime.now()
    serialized = serializers.DatabaseSyncTestSerializer(data=request.data)
    if serialized.is_valid():
        Name = serialized.data['Name']

        if not models.DatabaseSyncTest.objects.filter(BranchID=BranchID, CompanyID=CompanyID, Name__iexact=Name).exists():
            instance = models.DatabaseSyncTest.objects.create(
                CompanyID=CompanyID,
                BranchID=BranchID,
                Name=Name,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                DataSyncID=1
            )

            response_data = {
                "StatusCode": 6000,
                "id": str(instance.id),
                "DataSyncID": instance.DataSyncID,
                "message": "Successfully Created."
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:

            response_data = {
                "StatusCode": 6001,
                "message": "database sync name already exist."
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_database_sync(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = serializers.DatabaseSyncTestSerializer(data=request.data)
    instance = models.DatabaseSyncTest.objects.get(pk=pk, CompanyID=CompanyID)

    BranchID = instance.BranchID

    if serialized.is_valid():
        Name = serialized.data['Name']
        Action = 'M'
        if not models.DatabaseSyncTest.objects.filter(BranchID=BranchID, CompanyID=CompanyID, Name__iexact=Name).exclude(Name=instance.Name):
            instance.Name = Name
            instance.Action = Action
            instance.CreatedUserID = CreatedUserID
            instance.UpdatedDate = today
            instance.DataSyncID = int(instance.DataSyncID) + 1
            instance.save()

            response_data = {
                "StatusCode": 6000,
                "message": "Successfully Updated."
            }

            return Response(response_data, status=status.HTTP_200_OK)

        elif models.DatabaseSyncTest.objects.filter(BranchID=BranchID, CompanyID=CompanyID, Name__iexact=Name).exists():
            response_data = {
                "StatusCode": 6001,
                "message": "Database Sync name already exist in this branch"
            }
            return Response(response_data, status=status.HTTP_200_OK)

        else:
            instance.Name = Name
            instance.Action = Action
            instance.UpdatedDate = today
            instance.DataSyncID = int(instance.DataSyncID) + 1
            instance.CreatedUserID = CreatedUserID
            instance.save()

            response_data = {
                "StatusCode": 6000,
                "message": "Successfully Updated."
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def database_sync_list(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    serializer = serializers.ListSerializer(data=request.data)
    if serializer.is_valid():
        BranchID = serializer.data['BranchID']
        if models.DatabaseSyncTest.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            instances = models.DatabaseSyncTest.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)
            serialized = serializers.DatabaseSyncTestRestSerializer(
                instances, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Category Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def database_sync(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    BranchID = data['BranchID']
    id = data['id']
    DataSyncID = data['DataSyncID']
    Name = data['Name']

    today = datetime.datetime.now()
    instance = DatabaseSyncTest.objects.get(
        id=id, BranchID=BranchID, CompanyID=CompanyID)
    if int(DataSyncID) > int(instance.DataSyncID):
        instance.CompanyID = CompanyID
        instance.BranchID = BranchID
        instance.Name = Name
        instance.DataSyncID = DataSyncID
        instance.CreatedUserID = CreatedUserID
        instance.UpdatedDate = today
        instance.save()

    response_data = {
        "StatusCode": 6000,
        "message": "Successfully Synced."
    }

    return Response(response_data, status=status.HTTP_200_OK)
