from brands.models import MasterType, MasterType_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v8.masterTypes.serializers import MasterTypeSerializer, MasterTypeRestSerializer
from api.v8.brands.serializers import ListSerializer
from api.v8.masterTypes.functions import generate_serializer_errors
from rest_framework import status
from api.v8.masterTypes.functions import get_auto_id
from main.functions import get_company
import datetime


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_masterType(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    serialized = MasterTypeSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        Name = serialized.data['Name']
        Description = serialized.data['Description']
        IsDefault = serialized.data['IsDefault']

        Action = 'A'

        MasterTypeID = get_auto_id(MasterType, BranchID, CompanyID)

        is_nameExist = False

        NameLow = Name.lower()

        mastertypes = MasterType.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID)

        for mastertype in mastertypes:
            masterType_name = mastertype.Name

            mastertypeName = masterType_name.lower()

            if NameLow == mastertypeName:
                is_nameExist = True

        if not is_nameExist:

            # serialized.save(BrandID=BrandID,CreatedDate=today,ModifiedDate=today)
            MasterType.objects.create(
                MasterTypeID=MasterTypeID,
                BranchID=BranchID,
                Name=Name,
                Description=Description,
                IsDefault=IsDefault,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID
            )

            MasterType_Log.objects.create(
                BranchID=BranchID,
                TransactionID=MasterTypeID,
                Name=Name,
                Description=Description,
                IsDefault=IsDefault,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                Action=Action,
                CompanyID=CompanyID
            )

            data = {"MasterTypeID": MasterTypeID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Master Type Name Already Exist!!!"
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
def edit_masterType(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = MasterTypeSerializer(data=request.data)
    instance = MasterType.objects.get(CompanyID=CompanyID, pk=pk)

    BranchID = instance.BranchID
    MasterTypeID = instance.MasterTypeID
    instanceName = instance.Name

    if serialized.is_valid():
        Name = serialized.data['Name']
        Description = serialized.data['Description']
        IsDefault = serialized.data['IsDefault']

        Action = 'M'

        is_nameExist = False
        mastertype_ok = False

        NameLow = Name.lower()

        mastertypes = MasterType.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID)

        for mastertype in mastertypes:
            masterType_name = mastertype.Name

            mastertypeName = masterType_name.lower()

            if NameLow == mastertypeName:
                is_nameExist = True

            if instanceName.lower() == NameLow:

                mastertype_ok = True

        if mastertype_ok:

            instance.Name = Name
            instance.Description = Description
            instance.IsDefault = IsDefault
            instance.Action = Action
            instance.CreatedUserID = CreatedUserID
            instance.UpdatedDate = today
            instance.save()

            MasterType_Log.objects.create(
                BranchID=BranchID,
                TransactionID=MasterTypeID,
                Name=Name,
                Description=Description,
                IsDefault=IsDefault,
                CreatedDate=today,
                UpdatedDate=today,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID
            )
            data = {"MasterTypeID": MasterTypeID}
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
                    "message": "MasterType Name Already exist with this Branch ID"
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                instance.Name = Name
                instance.Description = Description
                instance.IsDefault = IsDefault
                instance.Action = Action
                instance.CreatedUserID = CreatedUserID
                instance.UpdatedDate = today
                instance.save()

                MasterType_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=MasterTypeID,
                    Name=Name,
                    Description=Description,
                    IsDefault=IsDefault,
                    CreatedDate=today,
                    UpdatedDate=today,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CompanyID=CompanyID,
                )

                data = {"MasterTypeID": MasterTypeID}
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
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def masterTypes(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if MasterType.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():

            instances = MasterType.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID)

            serialized = MasterTypeRestSerializer(instances, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Master Type Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def masterType(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None

    if MasterType.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = MasterType.objects.get(CompanyID=CompanyID, pk=pk)
        serialized = MasterTypeRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Master Type Not Fount!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_masterType(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if MasterType.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = MasterType.objects.get(CompanyID=CompanyID, pk=pk)

        BranchID = instance.BranchID
        MasterTypeID = instance.MasterTypeID
        Name = instance.Name
        Description = instance.Description
        IsDefault = instance.IsDefault
        Action = "D"

        instance.delete()

        MasterType_Log.objects.create(
            BranchID=BranchID,
            TransactionID=MasterTypeID,
            Name=Name,
            Description=Description,
            IsDefault=IsDefault,
            CreatedDate=today,
            UpdatedDate=today,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CompanyID=CompanyID,
        )

        response_data = {
            "StatusCode": 6000,
            "message": "MasterType Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "MasterType Not Fount!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
