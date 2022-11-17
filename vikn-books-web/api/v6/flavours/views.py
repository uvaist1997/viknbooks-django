from brands.models import Flavours, Flavours_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v6.flavours.serializers import FlavoursSerializer, FlavoursRestSerializer
from api.v6.brands.serializers import ListSerializer
from api.v6.flavours.functions import generate_serializer_errors
from rest_framework import status
from api.v6.flavours.functions import get_auto_id
from main.functions import get_company
import datetime


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_flavour(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    serialized = FlavoursSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        FlavourName = serialized.data['FlavourName']
        BgColor = serialized.data['BgColor']
        IsActive = serialized.data['IsActive']

        Action = 'A'

        FlavourID = get_auto_id(Flavours, BranchID, CompanyID)

        is_nameExist = False

        FlavourNameLow = FlavourName.lower()

        flavours = Flavours.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID)

        for flavour in flavours:
            flavour_name = flavour.FlavourName

            flavourName = flavour_name.lower()

            if FlavourNameLow == flavourName:
                is_nameExist = True

        if not is_nameExist:
            # serialized.save(BrandID=BrandID,CreatedDate=today,ModifiedDate=today)
            Flavours.objects.create(
                FlavourID=FlavourID,
                BranchID=BranchID,
                FlavourName=FlavourName,
                BgColor=BgColor,
                IsActive=IsActive,
                Action=Action,
                CompanyID=CompanyID,
            )

            Flavours_Log.objects.create(
                BranchID=BranchID,
                TransactionID=FlavourID,
                FlavourName=FlavourName,
                BgColor=BgColor,
                IsActive=IsActive,
                Action=Action,
                CompanyID=CompanyID,
            )

            data = {"FlavourID": FlavourID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Flavours Name Already Exist!!!"
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
def edit_flavour(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = FlavoursSerializer(data=request.data)
    instance = Flavours.objects.get(pk=pk, CompanyID=CompanyID)
    BranchID = instance.BranchID
    FlavourID = instance.FlavourID
    instanceFlavourName = instance.FlavourName

    if serialized.is_valid():

        FlavourName = serialized.data['FlavourName']
        BgColor = serialized.data['BgColor']
        IsActive = serialized.data['IsActive']

        Action = 'M'

        is_nameExist = False
        flavour_ok = False

        FlavourNameLow = FlavourName.lower()

        flavours = Flavours.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID)

        for flavour in flavours:
            flavour_name = flavour.FlavourName

            flavourName = flavour_name.lower()

            if FlavourNameLow == flavourName:
                is_nameExist = True

            if instanceFlavourName.lower() == FlavourNameLow:

                flavour_ok = True

        if flavour_ok:

            instance.FlavourName = FlavourName
            instance.BgColor = BgColor
            instance.IsActive = IsActive
            instance.Action = Action
            instance.save()

            Flavours_Log.objects.create(
                BranchID=BranchID,
                TransactionID=FlavourID,
                FlavourName=FlavourName,
                BgColor=BgColor,
                IsActive=IsActive,
                Action=Action,
                CompanyID=CompanyID,
            )

            data = {"FlavourID": FlavourID}
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
                    "message": "Flavours Name Already exist with this Branch ID"
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                instance.FlavourName = FlavourName
                instance.BgColor = BgColor
                instance.IsActive = IsActive
                instance.Action = Action
                instance.save()

                Flavours_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=FlavourID,
                    FlavourName=FlavourName,
                    BgColor=BgColor,
                    IsActive=IsActive,
                    Action=Action,
                    CompanyID=CompanyID,
                )

                data = {"FlavourID": FlavourID}
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
def flavours(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if Flavours.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():
            instances = Flavours.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)
            serialized = FlavoursRestSerializer(instances, many=True)
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Flavours Not Found in this BranchID!"
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
def flavour(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    if Flavours.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = Flavours.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = FlavoursRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Flavours Not Fount!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_flavour(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    if Flavours.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = Flavours.objects.get(pk=pk, CompanyID=CompanyID)
        BranchID = instance.BranchID
        FlavourID = instance.FlavourID
        FlavourName = instance.FlavourName
        BgColor = instance.BgColor
        IsActive = instance.IsActive
        Action = "D"

        instance.delete()

        Flavours_Log.objects.create(
            BranchID=BranchID,
            TransactionID=FlavourID,
            FlavourName=FlavourName,
            BgColor=BgColor,
            IsActive=IsActive,
            Action=Action,
            CompanyID=CompanyID,
        )

        response_data = {
            "StatusCode": 6000,
            "message": "Flavours Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Flavours Not Fount!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
