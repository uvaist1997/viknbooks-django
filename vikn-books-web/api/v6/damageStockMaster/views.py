from brands.models import DamageStockMaster, DamageStockMaster_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v6.damageStockMaster.serializers import DamageStockMasterSerializer, DamageStockMasterRestSerializer
from api.v6.damageStockDetails.serializers import DamageStockDetailsSerializer, DamageStockDetailsRestSerializer
from api.v6.brands.serializers import ListSerializer
from api.v6.damageStockMaster.functions import generate_serializer_errors
from rest_framework import status
from api.v6.damageStockMaster.functions import get_auto_id
import datetime


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_damageStockMaster(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = DamageStockMasterSerializer(data=request.data)
    if serialized.is_valid():
        BranchID = serialized.data['BranchID']
        VoucherNo = serialized.data['VoucherNo']
        Date = serialized.data['Date']
        WarehouseID = serialized.data['WarehouseID']
        Notes = serialized.data['Notes']
        TotalQty = serialized.data['TotalQty']
        GrandTotal = serialized.data['GrandTotal']
        IsActive = serialized.data['IsActive']

        Action = 'A'
        DamageStockMasterID = get_auto_id(
            DamageStockMaster, BranchID, DataBase)
        DamageStockMaster.objects.create(
            DamageStockMasterID=DamageStockMasterID,
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
            UpdatedDate=today,
        )
        DamageStockMaster_Log.objects.create(
            TransactionID=DamageStockMasterID,
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
            UpdatedDate=today,
        )

        data = {"DamageStockMasterID": DamageStockMasterID}
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
def edit_damageStockMaster(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = DamageStockMasterSerializer(data=request.data)
    instance = DamageStockMaster.objects.get(pk=pk)
    DamageStockMasterID = instance.DamageStockMasterID
    BranchID = instance.BranchID

    if serialized.is_valid():

        VoucherNo = serialized.data['VoucherNo']
        Date = serialized.data['Date']
        WarehouseID = serialized.data['WarehouseID']
        Notes = serialized.data['Notes']
        TotalQty = serialized.data['TotalQty']
        GrandTotal = serialized.data['GrandTotal']
        IsActive = serialized.data['IsActive']

        Action = 'M'
        instance.VoucherNo = VoucherNo
        instance.WarehouseID = WarehouseID
        instance.Notes = Notes
        instance.TotalQty = TotalQty
        instance.GrandTotal = GrandTotal
        instance.IsActive = IsActive
        instance.Action = Action
        instance.CreatedUserID = CreatedUserID
        instance.UpdatedDate = today

        instance.save()

        DamageStockMaster_Log.objects.create(
            TransactionID=DamageStockMasterID,
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
            UpdatedDate=today,
        )

        data = {"DamageStockMasterID": DamageStockMasterID}
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
def list_damageStockMaster(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if DamageStockMaster.objects.filter(BranchID=BranchID).exists():
            instances = DamageStockMaster.objects.filter(BranchID=BranchID)
            serialized = DamageStockMasterRestSerializer(
                instances, many=True, context={"DataBase": DataBase})
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Damage Stock Master Not Found in this BranchID!"
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
def damageStockMaster(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    instance = None
    if DamageStockMaster.objects.filter(DamageStockMasterID=pk).exists():
        instances = DamageStockMaster.objects.get(DamageStockMasterID=pk)

        serialized = DamageStockMasterRestSerializer(
            instances, context={"DataBase": DataBase})
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data,
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Damage Stock Master Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_damageStockMaster(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if DamageStockMaster.objects.filter(pk=pk).exists():
        instance = DamageStockMaster.objects.get(pk=pk)
    if instance:
        DamageStockMasterID = instance.DamageStockMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        Date = instance.Date
        WarehouseID = instance.WarehouseID
        Notes = instance.Notes
        TotalQty = instance.TotalQty
        GrandTotal = instance.GrandTotal
        IsActive = instance.IsActive
        DamageStockMasterID = instance.DamageStockMasterID
        Action = "D"
        instance.delete()

        DamageStockMaster_Log.objects.create(
            TransactionID=DamageStockMasterID,
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
            UpdatedDate=today,
        )
        response_data = {
            "StatusCode": 6000,
            "message": "Damage Stock Master Details Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Damage Stock Master Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
