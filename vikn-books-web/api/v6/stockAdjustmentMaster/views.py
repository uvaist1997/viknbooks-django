from brands.models import StockAdjustmentMaster, StockAdjustmentMaster_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v6.stockAdjustmentMaster.serializers import StockAdjustmentMasterSerializer, StockAdjustmentMasterRestSerializer
from api.v6.brands.serializers import ListSerializer
from api.v6.stockAdjustmentMaster.functions import generate_serializer_errors
from rest_framework import status
from api.v6.stockAdjustmentMaster.functions import get_auto_id
import datetime


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_stockAdjustmentMaster(request):
    today = datetime.datetime.now()
    serialized = StockAdjustmentMasterSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        VoucherNo = serialized.data['VoucherNo']
        InvoiceNo = serialized.data['InvoiceNo']
        Date = serialized.data['Date']
        WarehouseID = serialized.data['WarehouseID']
        Notes = serialized.data['Notes']
        GroupWise = serialized.data['GroupWise']
        ProductGroupID = serialized.data['ProductGroupID']
        IsActive = serialized.data['IsActive']
        CreatedUserID = serialized.data['CreatedUserID']

        Action = "A"

        StockAdjustmentMasterID = get_auto_id(StockAdjustmentMaster, BranchID)

        StockAdjustmentMaster.objects.create(
            StockAdjustmentMasterID=StockAdjustmentMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
            Date=Date,
            WarehouseID=WarehouseID,
            Notes=Notes,
            GroupWise=GroupWise,
            ProductGroupID=ProductGroupID,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
        )

        StockAdjustmentMaster_Log.objects.create(
            TransactionID=StockAdjustmentMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
            Date=Date,
            WarehouseID=WarehouseID,
            Notes=Notes,
            GroupWise=GroupWise,
            ProductGroupID=ProductGroupID,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
        )

        data = {"StockAdjustmentMasterID": StockAdjustmentMasterID}
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
def edit_stockAdjustmentMaster(request, pk):
    today = datetime.datetime.now()
    serialized = StockAdjustmentMasterSerializer(data=request.data)
    instance = None
    if StockAdjustmentMaster.objects.filter(pk=pk).exists():
        instance = StockAdjustmentMaster.objects.get(pk=pk)

        StockAdjustmentMasterID = instance.StockAdjustmentMasterID
        BranchID = instance.BranchID
        CreatedUserID = instance.CreatedUserID

    if instance:
        if serialized.is_valid():
            VoucherNo = serialized.data['VoucherNo']
            InvoiceNo = serialized.data['InvoiceNo']
            Date = serialized.data['Date']
            WarehouseID = serialized.data['WarehouseID']
            Notes = serialized.data['Notes']
            GroupWise = serialized.data['GroupWise']
            ProductGroupID = serialized.data['ProductGroupID']
            IsActive = serialized.data['IsActive']

            Action = "M"

            instance.VoucherNo = VoucherNo
            instance.InvoiceNo = InvoiceNo
            instance.Date = Date
            instance.WarehouseID = WarehouseID
            instance.Notes = Notes
            instance.GroupWise = GroupWise
            instance.ProductGroupID = ProductGroupID
            instance.IsActive = IsActive
            instance.Action = Action
            instance.save()

            StockAdjustmentMaster_Log.objects.create(
                TransactionID=StockAdjustmentMasterID,
                BranchID=BranchID,
                VoucherNo=VoucherNo,
                InvoiceNo=InvoiceNo,
                Date=Date,
                WarehouseID=WarehouseID,
                Notes=Notes,
                GroupWise=GroupWise,
                ProductGroupID=ProductGroupID,
                IsActive=IsActive,
                Action=Action,
                CreatedUserID=CreatedUserID,
                CreatedDate=today,
            )

            data = {"StockAdjustmentMasterID": StockAdjustmentMasterID}
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
            "message": "Stock Adjustment Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_stockAdjustmentMaster(request):
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if StockAdjustmentMaster.objects.filter(BranchID=BranchID).exists():

            instances = StockAdjustmentMaster.objects.filter(BranchID=BranchID)

            serialized = StockAdjustmentMasterRestSerializer(
                instances, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Stock Adjustment Master Not Found in this BranchID!"
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
def stockAdjustmentMaster(request, pk):
    instance = None
    if StockAdjustmentMaster.objects.filter(pk=pk).exists():
        instance = StockAdjustmentMaster.objects.get(pk=pk)
    if instance:
        serialized = StockAdjustmentMasterRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Stock Adjustment Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_stockAdjustmentMaster(request, pk):
    today = datetime.datetime.now()
    instance = None
    if StockAdjustmentMaster.objects.filter(pk=pk).exists():
        instance = StockAdjustmentMaster.objects.get(pk=pk)
    if instance:
        StockAdjustmentMasterID = instance.StockAdjustmentMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        InvoiceNo = instance.InvoiceNo
        Date = instance.Date
        WarehouseID = instance.WarehouseID
        Notes = instance.Notes
        GroupWise = instance.GroupWise
        ProductGroupID = instance.ProductGroupID
        IsActive = instance.IsActive
        CreatedUserID = instance.CreatedUserID
        Action = "D"

        instance.delete()

        StockAdjustmentMaster_Log.objects.create(
            TransactionID=StockAdjustmentMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
            Date=Date,
            WarehouseID=WarehouseID,
            Notes=Notes,
            GroupWise=GroupWise,
            ProductGroupID=ProductGroupID,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
        )
        response_data = {
            "StatusCode": 6000,
            "message": "Stock Adjustment Master Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Stock Adjustment Master Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
