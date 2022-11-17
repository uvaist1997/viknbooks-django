from brands.models import UserType, UserTypeLog, Product, Activity_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v5.userTypes.serializers import UserTypeSerializer, UserTypeRestSerializer, ListSerializer
from api.v5.userTypes.functions import generate_serializer_errors
from rest_framework import status
from api.v5.userTypes.functions import get_auto_id
from main.functions import get_company, activity_log
import datetime


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_user_type(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    serialized = UserTypeSerializer(data=request.data)
    if serialized.is_valid():
        BranchID = serialized.data['BranchID']
        UserTypeName = serialized.data['UserTypeName']
        Action = 'A'
        ID = get_auto_id(UserType, BranchID, CompanyID)

        if not UserType.objects.filter(BranchID=BranchID, CompanyID=CompanyID, UserTypeName__iexact=UserTypeName).exists():
            UserType.objects.create(
                ID=ID,
                BranchID=BranchID,
                UserTypeName=UserTypeName,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID
            )

            UserTypeLog.objects.create(
                TransactionID=ID,
                BranchID=BranchID,
                UserTypeName=UserTypeName,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID
            )
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Brand',
                         'Create', 'Brand created successfully.', 'Brand saved successfully.')

            response_data = {
                "StatusCode": 6000,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID,
                         'User Type', 'Create', 'User Type name already exist.', 'same name exists.')

            response_data = {
                "StatusCode": 6001,
                "message": "User Type already exist."
            }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'User Type', 'Create',
                     'User Type field not valid.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_brand(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = BrandSerializer(data=request.data)
    instance = UserType.objects.get(pk=pk, CompanyID=CompanyID)

    BranchID = instance.BranchID
    BrandID = instance.BrandID
    instanceBrandname = instance.BrandName

    if serialized.is_valid():
        BrandName = serialized.data['BrandName']
        Notes = serialized.data['Notes']
        Action = 'M'
        if not UserType.objects.filter(BranchID=BranchID, CompanyID=CompanyID, BrandName__iexact=BrandName).exclude(BrandName=instanceBrandname):
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
                CompanyID=CompanyID
            )
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID,
                         'Brand', 'Edit', 'Brand edited successfully.', 'Brand saved successfully.')

            data = {"BrandID": BrandID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        elif UserType.objects.filter(BranchID=BranchID, CompanyID=CompanyID, BrandName__iexact=BrandName).exists():
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Brand',
                         'Edit', 'Brand already exists.', 'Brand name already exist in this branch.')

            response_data = {
                "StatusCode": 6001,
                "message": "Brand name already exist in this branch"
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
                CompanyID=CompanyID
            )
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID,
                         'Brand', 'Edit', 'Brand edited successfully.', 'Brand saved successfully.')

            data = {"BrandID": BrandID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'Brand', 'Edit',
                     'Brand edited failed.', generate_serializer_errors(serialized._errors))

        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def user_types(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if UserType.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            instances = UserType.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)
            serialized = UserTypeRestSerializer(instances, many=True)

            #request , company, log_type, user, source, action, message, description
            # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Brand', 'View', 'Brand list', 'The user viewed brands')

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information',
                         CreatedUserID, 'UserType', 'View', 'UserType list', 'UserType not found')
            response_data = {
                "StatusCode": 6001,
                "message": "Brands Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information',
                     CreatedUserID, 'Brand', 'View', 'Brand list', 'brand not valid')
        response_data = {
            "StatusCode": 6001,
            "message": "Branch You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def brand(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if UserType.objects.filter(pk=pk).exists():
        instance = UserType.objects.get(pk=pk)
        serialized = UserTypeRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID,
                     'Brand', 'View', 'Brand Single Page', 'User viewed a Brand')
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Brand Not Fount!"
        }

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID,
                     'Brand', 'View', 'Brand Single Page', 'Brand not Found!')

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_brand(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if pk == "1":
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Brand',
                     'Delete', 'Brand Deleted failed', 'Tried to Delete Default Brand!')
        response_data = {
            "StatusCode": 6001,
            "message": "You Can't Delete this Brand!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        if UserType.objects.filter(pk=pk).exists():
            instance = UserType.objects.get(pk=pk)
        if instance:
            BranchID = instance.BranchID
            BrandID = instance.BrandID
            BrandName = instance.BrandName
            Notes = instance.Notes
            Action = "D"

            if not Product.objects.filter(BranchID=BranchID, BrandID=BrandID, CompanyID=CompanyID).exists():

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
                    CompanyID=CompanyID
                )
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Brand',
                             'Delete', 'Brand Deleted Successfully', 'Brand Deleted Successfully')

                response_data = {
                    "StatusCode": 6000,
                    "message": "Brand Deleted Successfully!"
                }
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Brand', 'Delete',
                             'Brand Deleted Failed', 'Brand Deleted Failed,Product has Created with this Brand')
                response_data = {
                    "StatusCode": 6001,
                    "message": "You can't Delete this Brand,Product exist with this Brand!!"
                }
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Error', CreatedUserID,
                         'Brand', 'Delete', 'Brand Deleted Failed', 'Brand Not Found!')
            response_data = {
                "StatusCode": 6001,
                "message": "Brand Not Found!"
            }

        return Response(response_data, status=status.HTTP_200_OK)
