from brands.models import Kitchen, Kitchen_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v3.kitchen.serializers import KitchenSerializer, KitchenRestSerializer
from api.v3.brands.serializers import ListSerializer
from api.v3.kitchen.functions import generate_serializer_errors
from rest_framework import status
from api.v3.kitchen.functions import get_auto_id
from main.functions import get_company
import datetime


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_kitchen(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    serialized = KitchenSerializer(data=request.data)

    if serialized.is_valid():
        BranchID = serialized.data['BranchID']
        KitchenName = serialized.data['KitchenName']
        PrinterName = serialized.data['PrinterName']
        IsActive = serialized.data['IsActive']
        Notes = serialized.data['Notes']

        Action = 'A'

        KitchenID = get_auto_id(Kitchen, BranchID, CompanyID)
        is_nameExist = False

        KitchenNameLow = KitchenName.lower()

        kitchens = Kitchen.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID)

        for kitchen in kitchens:
            kitchen_name = kitchen.KitchenName

            kitchenName = kitchen_name.lower()

            if KitchenNameLow == kitchenName:
                is_nameExist = True

        if not is_nameExist:

            # serialized.save(BrandID=BrandID,CreatedDate=today,ModifiedDate=today)
            Kitchen.objects.create(
                KitchenID=KitchenID,
                BranchID=BranchID,
                KitchenName=KitchenName,
                PrinterName=PrinterName,
                IsActive=IsActive,
                Notes=Notes,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            Kitchen_Log.objects.create(
                BranchID=BranchID,
                TransactionID=KitchenID,
                KitchenName=KitchenName,
                PrinterName=PrinterName,
                IsActive=IsActive,
                Notes=Notes,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )

            data = {"KitchenID": KitchenID}
            data.update(serialized.data)
            response_data = {
                "StatusCode": 6000,
                "data": data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Kitchen Name Already Exist!!!"
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
def edit_kitchen(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    serialized = KitchenSerializer(data=request.data)
    instance = Kitchen.objects.get(pk=pk, CompanyID=CompanyID)

    BranchID = instance.BranchID
    KitchenID = instance.KitchenID
    instanceKitchenName = instance.KitchenName

    if serialized.is_valid():

        KitchenName = serialized.data['KitchenName']
        PrinterName = serialized.data['PrinterName']
        IsActive = serialized.data['IsActive']
        Notes = serialized.data['Notes']

        Action = 'M'

        is_nameExist = False
        kitchen_ok = False

        KitchenNameLow = KitchenName.lower()

        kitchens = Kitchen.objects.filter(
            BranchID=BranchID, CompanyID=CompanyID)

        for kitchen in kitchens:
            kitchen_name = kitchen.KitchenName

            kitchenName = kitchen_name.lower()

            if KitchenNameLow == kitchenName:
                is_nameExist = True

            if instanceKitchenName.lower() == KitchenNameLow:

                kitchen_ok = True

        if kitchen_ok:

            instance.KitchenName = KitchenName
            instance.PrinterName = PrinterName
            instance.IsActive = IsActive
            instance.Notes = Notes
            instance.Action = Action
            instance.CreatedUserID = CreatedUserID
            instance.UpdatedDate = today
            instance.save()

            Kitchen_Log.objects.create(
                BranchID=BranchID,
                TransactionID=KitchenID,
                KitchenName=KitchenName,
                PrinterName=PrinterName,
                IsActive=IsActive,
                Notes=Notes,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                UpdatedDate=today,
                CompanyID=CompanyID,
            )
            data = {"KitchenID": KitchenID}
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
                    "message": "Kitchen Name Already exist with this Branch ID"
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                instance.KitchenName = KitchenName
                instance.PrinterName = PrinterName
                instance.IsActive = IsActive
                instance.Notes = Notes
                instance.Action = Action
                instance.CreatedUserID = CreatedUserID
                instance.UpdatedDate = today
                instance.save()

                Kitchen_Log.objects.create(
                    BranchID=BranchID,
                    TransactionID=KitchenID,
                    KitchenName=KitchenName,
                    PrinterName=PrinterName,
                    IsActive=IsActive,
                    Notes=Notes,
                    Action=Action,
                    CreatedUserID=CreatedUserID,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CompanyID=CompanyID,
                )

                data = {"KitchenID": KitchenID}
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
def kitchens(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if Kitchen.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():

            instances = Kitchen.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)

            serialized = KitchenRestSerializer(instances, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Kitchen Not Found in this BranchID!"
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
def kitchen(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    instance = None
    if Kitchen.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = Kitchen.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = KitchenRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Kitchen Not Fount!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_kitchen(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    instance = None
    if Kitchen.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = Kitchen.objects.get(pk=pk, CompanyID=CompanyID)
        BranchID = instance.BranchID
        KitchenID = instance.KitchenID
        KitchenName = instance.KitchenName
        PrinterName = instance.PrinterName
        IsActive = instance.IsActive
        Notes = instance.Notes
        Action = "D"

        instance.delete()

        Kitchen_Log.objects.create(
            BranchID=BranchID,
            TransactionID=KitchenID,
            KitchenName=KitchenName,
            PrinterName=PrinterName,
            IsActive=IsActive,
            Notes=Notes,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            UpdatedDate=today,
            CompanyID=CompanyID,
        )

        response_data = {
            "StatusCode": 6000,
            "message": "Kitchen Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Kitchen Not Fount!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
