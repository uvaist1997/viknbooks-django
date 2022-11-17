from brands.models import StockTransferMaster_ID, StockTransferMasterID_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v2.stockTransferMasterID.serializers import StockTransferMaster_IDSerializer, StockTransferMaster_IDRestSerializer
from api.v2.brands.serializers import ListSerializer
from api.v2.stockTransferMasterID.functions import generate_serializer_errors
from rest_framework import status
from api.v2.stockTransferMasterID.functions import get_auto_id
import datetime



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_stockTransferMasterID(request):
    today = datetime.datetime.now()
    serialized = StockTransferMaster_IDSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        VoucherNo = serialized.data['VoucherNo']
        InvoiceNo = serialized.data['InvoiceNo']
        Date = serialized.data['Date']
        Notes = serialized.data['Notes']
        TransferredByID = serialized.data['TransferredByID']
        WarehouseFromID = serialized.data['WarehouseFromID']
        WarehouseToID = serialized.data['WarehouseToID']
        TotalQty = serialized.data['TotalQty']
        GrandTotal = serialized.data['GrandTotal']
        IsActive = serialized.data['IsActive']
        CreatedUserID = serialized.data['CreatedUserID']
        
        Action = "A"

        StockTransferMasterID = get_auto_id(StockTransferMaster_ID,BranchID)

        StockTransferMaster_ID.objects.create(
            StockTransferMasterID=StockTransferMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
            Date=Date,
            Notes=Notes,
            TransferredByID=TransferredByID,
            WarehouseFromID=WarehouseFromID,
            WarehouseToID=WarehouseToID,
            TotalQty=TotalQty,
            GrandTotal=GrandTotal,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            )

        StockTransferMasterID_Log.objects.create(
            TransactionID=StockTransferMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
            Date=Date,
            Notes=Notes,
            TransferredByID=TransferredByID,
            WarehouseFromID=WarehouseFromID,
            WarehouseToID=WarehouseToID,
            TotalQty=TotalQty,
            GrandTotal=GrandTotal,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            )

        data = {"StockTransferMasterID" : StockTransferMasterID}
        data.update(serialized.data)
        response_data = {
            "StatusCode" : 6000,
            "data" : data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_stockTransferMasterID(request,pk):
    today = datetime.datetime.now()
    serialized = StockTransferMaster_IDSerializer(data=request.data)
    instance = None
    if StockTransferMaster_ID.objects.filter(pk=pk).exists():
        instance = StockTransferMaster_ID.objects.get(pk=pk)

        StockTransferMasterID = instance.StockTransferMasterID
        BranchID = instance.BranchID
        CreatedUserID = instance.CreatedUserID
        
    if instance:
        if serialized.is_valid():
            VoucherNo = serialized.data['VoucherNo']
            InvoiceNo = serialized.data['InvoiceNo']
            Date = serialized.data['Date']
            Notes = serialized.data['Notes']
            TransferredByID = serialized.data['TransferredByID']
            WarehouseFromID = serialized.data['WarehouseFromID']
            WarehouseToID = serialized.data['WarehouseToID']
            TotalQty = serialized.data['TotalQty']
            GrandTotal = serialized.data['GrandTotal']
            IsActive = serialized.data['IsActive']

            Action = "M"


            instance.VoucherNo = VoucherNo
            instance.InvoiceNo = InvoiceNo
            instance.Date = Date
            instance.Notes = Notes
            instance.TransferredByID = TransferredByID
            instance.WarehouseFromID = WarehouseFromID
            instance.WarehouseToID = WarehouseToID
            instance.TotalQty = TotalQty
            instance.GrandTotal = GrandTotal
            instance.IsActive = IsActive
            instance.Action = Action
            instance.save()

            StockTransferMasterID_Log.objects.create(
                TransactionID=StockTransferMasterID,
                BranchID=BranchID,
                VoucherNo=VoucherNo,
                InvoiceNo=InvoiceNo,
                Date=Date,
                Notes=Notes,
                TransferredByID=TransferredByID,
                WarehouseFromID=WarehouseFromID,
                WarehouseToID=WarehouseToID,
                TotalQty=TotalQty,
                GrandTotal=GrandTotal,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
                )

            data = {"StockTransferMasterID" : StockTransferMasterID}
            data.update(serialized.data)
            response_data = {
                "StatusCode" : 6000,
                "data" : data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "StatusCode" : 6001,
                "message" : generate_serializer_errors(serialized._errors)
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Stock Transfer Master ID Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_stockTransferMasterID(request):
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if StockTransferMaster_ID.objects.filter(BranchID=BranchID).exists():

            instances = StockTransferMaster_ID.objects.filter(BranchID=BranchID)

            serialized = StockTransferMaster_IDRestSerializer(instances,many=True)

            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
            "StatusCode" : 6001,
            "message" : "Stock Transfer MasterID Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def stockTransferMasterID(request,pk):
    instance = None
    if StockTransferMaster_ID.objects.filter(pk=pk).exists():
        instance = StockTransferMaster_ID.objects.get(pk=pk)
    if instance:
        serialized = StockTransferMaster_IDRestSerializer(instance)
        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Stock Transfer Master ID Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_stockTransferMasterID(request,pk):
    today = datetime.datetime.now()
    instance = None
    if StockTransferMaster_ID.objects.filter(pk=pk).exists():
        instance = StockTransferMaster_ID.objects.get(pk=pk)
    if instance:
        StockTransferMasterID = instance.StockTransferMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        InvoiceNo = instance.InvoiceNo
        Date = instance.Date
        Notes = instance.Notes
        TransferredByID = instance.TransferredByID
        WarehouseFromID = instance.WarehouseFromID
        WarehouseToID = instance.WarehouseToID
        TotalQty = instance.TotalQty
        GrandTotal = instance.GrandTotal
        IsActive = instance.IsActive
        CreatedUserID = instance.CreatedUserID
        Action = "D"

        instance.delete()

        StockTransferMasterID_Log.objects.create(
            TransactionID=StockTransferMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
            Date=Date,
            Notes=Notes,
            TransferredByID=TransferredByID,
            WarehouseFromID=WarehouseFromID,
            WarehouseToID=WarehouseToID,
            TotalQty=TotalQty,
            GrandTotal=GrandTotal,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            )
        response_data = {
            "StatusCode" : 6000,
            "message" : "Stock Transfer Master ID Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Stock Transfer Master ID Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)