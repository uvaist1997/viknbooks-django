from brands.models import OpeningStockMaster, OpeningStockMaster_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v3.openingStockMaster.serializers import OpeningStockMasterSerializer, OpeningStockMasterRestSerializer
from api.v3.brands.serializers import ListSerializer
from api.v3.openingStockMaster.functions import generate_serializer_errors
from rest_framework import status
from api.v3.openingStockMaster.functions import get_auto_id
import datetime


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_openingStockMaster(request):
    today = datetime.datetime.now()
    serialized = OpeningStockMasterSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        VoucherNo = serialized.data['VoucherNo']
        Date = serialized.data['Date']
        WarehouseID = serialized.data['WarehouseID']
        Notes = serialized.data['Notes']
        TotalQty = serialized.data['TotalQty']
        GrandTotal = serialized.data['GrandTotal']
        IsActive = serialized.data['IsActive']
        CreatedUserID = serialized.data['CreatedUserID']
        Action = "A"

        OpeningStockMasterID = get_auto_id(OpeningStockMaster, BranchID)

        OpeningStockMaster.objects.create(
            OpeningStockMasterID=OpeningStockMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            Date=Date,
            WarehouseID=WarehouseID,
            Notes=Notes,
            TotalQty=TotalQty,
            GrandTotal=GrandTotal,
            IsActive=IsActive,
            CreatedDate=today,
            CreatedUserID=CreatedUserID,
            Action=Action,
        )

        OpeningStockMaster_Log.objects.create(
            TransactionID=OpeningStockMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            Date=Date,
            WarehouseID=WarehouseID,
            Notes=Notes,
            TotalQty=TotalQty,
            GrandTotal=GrandTotal,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
        )

        data = {"OpeningStockMasterID": OpeningStockMasterID}
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
def edit_openingStockMaster(request, pk):
    today = datetime.datetime.now()
    serialized = OpeningStockMasterSerializer(data=request.data)
    instance = None
    if OpeningStockMaster.objects.filter(pk=pk).exists():
        instance = OpeningStockMaster.objects.get(pk=pk)

        OpeningStockMasterID = instance.OpeningStockMasterID
        BranchID = instance.BranchID
        CreatedUserID = instance.CreatedUserID

    if instance:
        if serialized.is_valid():
            VoucherNo = serialized.data['VoucherNo']
            Date = serialized.data['Date']
            WarehouseID = serialized.data['WarehouseID']
            Notes = serialized.data['Notes']
            TotalQty = serialized.data['TotalQty']
            GrandTotal = serialized.data['GrandTotal']
            IsActive = serialized.data['IsActive']

            Action = "M"

            instance.VoucherNo = VoucherNo
            instance.Date = Date
            instance.WarehouseID = WarehouseID
            instance.Notes = Notes
            instance.TotalQty = TotalQty
            instance.GrandTotal = GrandTotal
            instance.IsActive = IsActive
            instance.Action = Action
            instance.save()

            OpeningStockMaster_Log.objects.create(
                TransactionID=OpeningStockMasterID,
                BranchID=BranchID,
                VoucherNo=VoucherNo,
                Date=Date,
                WarehouseID=WarehouseID,
                Notes=Notes,
                TotalQty=TotalQty,
                GrandTotal=GrandTotal,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
            )

            data = {"OpeningStockMasterID": OpeningStockMasterID}
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

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Opening Stock Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def openingStockMasters(request):
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if OpeningStockMaster.objects.filter(BranchID=BranchID).exists():

            instances = OpeningStockMaster.objects.filter(BranchID=BranchID)

            serialized = OpeningStockMasterRestSerializer(instances, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Opening Stock Master not found in this branch."
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch you enterd is not valid."
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def openingStockMaster(request, pk):
    instance = None
    if OpeningStockMaster.objects.filter(pk=pk).exists():
        instance = OpeningStockMaster.objects.get(pk=pk)
    if instance:
        serialized = OpeningStockMasterRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Opening Stock Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_openingStockMaster(request, pk):
    today = datetime.datetime.now()
    instance = None
    if OpeningStockMaster.objects.filter(pk=pk).exists():
        instance = OpeningStockMaster.objects.get(pk=pk)
    if instance:

        OpeningStockMasterID = instance.OpeningStockMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        Date = instance.Date
        WarehouseID = instance.WarehouseID
        Notes = instance.Notes
        TotalQty = instance.TotalQty
        GrandTotal = instance.GrandTotal
        IsActive = instance.IsActive
        CreatedUserID = instance.CreatedUserID
        Action = "D"

        instance.delete()

        OpeningStockMaster_Log.objects.create(
            TransactionID=OpeningStockMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            Date=Date,
            WarehouseID=WarehouseID,
            Notes=Notes,
            TotalQty=TotalQty,
            GrandTotal=GrandTotal,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
        )
        response_data = {
            "StatusCode": 6000,
            "message": "Opening Stock Master Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Opening Stock Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
