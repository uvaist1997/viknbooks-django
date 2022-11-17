from brands.models import LeaveType, LeaveType_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes,authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from api.v10.leaveType.serializers import LeaveTypeSerializer, LeaveTypeRestSerializer
from api.v10.brands.serializers import ListSerializer
from api.v10.leaveType.functions import generate_serializer_errors
from rest_framework import status
from api.v10.leaveType.functions import get_auto_id, get_auto_DepartmentID
from main.functions import get_company
import datetime


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def create_leaveType(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = LeaveTypeSerializer(data=request.data)
    print(data['Type'], "QQQQQQQQQQQQQQQQQQQQ")
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']

        Name = serialized.data['Name']
        Type = serialized.data['Type']

        Action = 'A'
        LeaveTypeID = get_auto_id(LeaveType, BranchID, CompanyID)
        is_nameExist = False
        NameLow = Name.lower()
        leavetypes = LeaveType.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID)
        for leavetype in leavetypes:
            name = leavetype.Name
            A_Name = name.lower()
            if NameLow == A_Name:
                is_nameExist = True

        print(Name, 'Name')
        if not is_nameExist:
            # serialized.save(BrandID=BrandID,CreatedDate=today,ModifiedDate=today)
            LeaveType.objects.create(
                LeaveTypeID=LeaveTypeID,
                BranchID=BranchID,

                Name=Name,
                Type=Type,

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            LeaveType_Log.objects.create(
                BranchID=BranchID,
                LeaveTypeID=LeaveTypeID,

                Name=Name,
                Type=Type,

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            data = {"LeaveTypeID": LeaveTypeID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Salary Period Name Already Exist!!!"
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
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def edit_leaveType(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = LeaveTypeSerializer(data=request.data)
    instance = LeaveType.objects.get(pk=pk, CompanyID=CompanyID)
    BranchID = instance.BranchID
    LeaveTypeID = instance.LeaveTypeID
    instancename = instance.Name
    if serialized.is_valid():
        Name = serialized.data['Name']
        Type = serialized.data['Type']

        Action = 'M'
        is_nameExist = False
        leavetype_ok = False

        NameLow = Name.lower()

        leavetypes = LeaveType.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID)

        for leavetype in leavetypes:
            name = leavetype.Name

            leavetypeName = name.lower()

            if NameLow == leavetypeName:
                is_nameExist = True

            if instancename.lower() == NameLow:

                leavetype_ok = True

        if leavetype_ok:

            instance.Name = Name
            instance.Type = Type

            instance.Action = Action
            instance.UpdatedDate = today
            instance.CreatedUserID = CreatedUserID
            instance.save()

            LeaveType_Log.objects.create(
                BranchID=BranchID,

                LeaveTypeID=LeaveTypeID,

                Name=Name,
                Type=Type,

                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
            )

            data = {"LeaveTypeID": LeaveTypeID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:

            if is_nameExist:

                response_data = {
                    "StatusCode": 6001,
                    "message": "Salary Period Name Already exist with this Branch ID"
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                instance.Name = Name
                instance.Type = Type

                instance.Action = Action
                instance.UpdatedDate = today
                instance.CreatedUserID = CreatedUserID
                instance.save()

                LeaveType_Log.objects.create(
                    BranchID=BranchID,
                    LeaveTypeID=LeaveTypeID,

                    Name=Name,
                    Type=Type,

                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                )

                data = {"LeaveTypeID": LeaveTypeID}
                data.update(serialized.data)
                response_data = {
                    "StatusCode": 6000,
                    "data": data
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
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def leaveTypes(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    print(CompanyID)

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if LeaveType.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            instances = LeaveType.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)
            serialized = LeaveTypeRestSerializer(instances, many=True)
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Salary Period Not Found in this BranchID!"
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
def leaveType(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if LeaveType.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = LeaveType.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = LeaveTypeRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Salary Period Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def delete_leaveType(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if LeaveType.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = LeaveType.objects.get(pk=pk, CompanyID=CompanyID)
        BranchID = instance.BranchID
        LeaveTypeID = instance.LeaveTypeID
        Name = instance.Name
        Type = instance.Type

        Action = "D"

        instance.delete()

        LeaveType_Log.objects.create(
            BranchID=BranchID,

            LeaveTypeID=LeaveTypeID,
            Name=Name,
            Type=Type,


            CreatedDate=today,
            UpdatedDate=today,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CompanyID=CompanyID,
        )

        response_data = {
            "StatusCode": 6000,
            "message": "Leave Type Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Leave Type Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
