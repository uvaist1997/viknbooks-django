from brands.models import StockReceiptMaster_ID, StockReceiptMasterID_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v4.stockReceiptMasterID.serializers import StockReceiptMaster_IDSerializer, StockReceiptMaster_IDRestSerializer
from api.v4.brands.serializers import ListSerializer
from api.v4.stockReceiptMasterID.functions import generate_serializer_errors
from rest_framework import status
from api.v4.stockReceiptMasterID.functions import get_auto_id
import datetime


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_stockReceiptMasterID(request):
    today = datetime.datetime.now()
    serialized = StockReceiptMaster_IDSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        VoucherNo = serialized.data['VoucherNo']
        InvoiceNo = serialized.data['InvoiceNo']
        Date = serialized.data['Date']
        Notes = serialized.data['Notes']
        WarehouseFromID = serialized.data['WarehouseFromID']
        WarehouseToID = serialized.data['WarehouseToID']
        IsActive = serialized.data['IsActive']
        CreatedUserID = serialized.data['CreatedUserID']

        Action = "A"

        StockReceiptMasterID = get_auto_id(StockReceiptMaster_ID, BranchID)

        StockReceiptMaster_ID.objects.create(
            StockReceiptMasterID=StockReceiptMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
            Date=Date,
            Notes=Notes,
            WarehouseFromID=WarehouseFromID,
            WarehouseToID=WarehouseToID,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
        )

        StockReceiptMasterID_Log.objects.create(
            TransactionID=StockReceiptMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
            Date=Date,
            Notes=Notes,
            WarehouseFromID=WarehouseFromID,
            WarehouseToID=WarehouseToID,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
        )

        data = {"StockReceiptMasterID": StockReceiptMasterID}
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
def edit_stockReceiptMasterID(request, pk):
    today = datetime.datetime.now()
    serialized = StockReceiptMaster_IDSerializer(data=request.data)
    instance = None
    if StockReceiptMaster_ID.objects.filter(pk=pk).exists():
        instance = StockReceiptMaster_ID.objects.get(pk=pk)

        StockReceiptMasterID = instance.StockReceiptMasterID
        BranchID = instance.BranchID
        CreatedUserID = instance.CreatedUserID

    if instance:
        if serialized.is_valid():
            VoucherNo = serialized.data['VoucherNo']
            InvoiceNo = serialized.data['InvoiceNo']
            Date = serialized.data['Date']
            Notes = serialized.data['Notes']
            WarehouseFromID = serialized.data['WarehouseFromID']
            WarehouseToID = serialized.data['WarehouseToID']
            IsActive = serialized.data['IsActive']

            Action = "M"

            instance.VoucherNo = VoucherNo
            instance.InvoiceNo = InvoiceNo
            instance.Date = Date
            instance.Notes = Notes
            instance.WarehouseFromID = WarehouseFromID
            instance.WarehouseToID = WarehouseToID
            instance.IsActive = IsActive
            instance.Action = Action
            instance.save()

            StockReceiptMasterID_Log.objects.create(
                TransactionID=StockReceiptMasterID,
                BranchID=BranchID,
                VoucherNo=VoucherNo,
                InvoiceNo=InvoiceNo,
                Date=Date,
                Notes=Notes,
                WarehouseFromID=WarehouseFromID,
                WarehouseToID=WarehouseToID,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
            )

            data = {"StockReceiptMasterID": StockReceiptMasterID}
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
            "message": "Stock Receipt Master ID Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_stockReceiptMasterID(request):
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if StockReceiptMaster_ID.objects.filter(BranchID=BranchID).exists():

            instances = StockReceiptMaster_ID.objects.filter(BranchID=BranchID)

            serialized = StockReceiptMaster_IDRestSerializer(
                instances, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Stock Receipt Master_ID Not Found in this BranchID!"
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
def stockReceiptMasterID(request, pk):
    instance = None
    if StockReceiptMaster_ID.objects.filter(pk=pk).exists():
        instance = StockReceiptMaster_ID.objects.get(pk=pk)
    if instance:
        serialized = StockReceiptMaster_IDRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Stock Receipt Master ID Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_stockReceiptMasterID(request, pk):
    today = datetime.datetime.now()
    instance = None
    if StockReceiptMaster_ID.objects.filter(pk=pk).exists():
        instance = StockReceiptMaster_ID.objects.get(pk=pk)
    if instance:
        StockReceiptMasterID = instance.StockReceiptMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        InvoiceNo = instance.InvoiceNo
        Date = instance.Date
        Notes = instance.Notes
        WarehouseFromID = instance.WarehouseFromID
        WarehouseToID = instance.WarehouseToID
        IsActive = instance.IsActive
        CreatedUserID = instance.CreatedUserID
        Action = "D"

        instance.delete()

        StockReceiptMasterID_Log.objects.create(
            TransactionID=StockReceiptMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
            Date=Date,
            Notes=Notes,
            WarehouseFromID=WarehouseFromID,
            WarehouseToID=WarehouseToID,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
        )

        response_data = {
            "StatusCode": 6000,
            "message": "Stock Receipt Master ID Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Stock Receipt Master ID Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
