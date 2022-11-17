from brands.models import DamageStockDetails, DamageStockDetails_Log, DamageStockDetailsDummy
from brands.models import DamageStockMaster, DamageStockMaster_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v5.damageStock.serializers import DamageStockMasterRestSerializer, DamageStockDetailsRestSerializer
from api.v5.brands.serializers import ListSerializer
from api.v5.damageStockDetails.functions import generate_serializer_errors
from rest_framework import status
from api.v5.damageStock.functions import get_auto_id, get_auto_idMaster
# from api.v5.damageStockDetails.functions import get_auto_idDetails
from main.functions import get_company
import datetime


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_damageStock(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    damageStockDetails = None

    BranchID = data["BranchID"]
    VoucherNo = data["VoucherNo"]
    Date = data["Date"]
    WarehouseID = data["WarehouseID"]
    Notes = data["Notes"]
    TotalQty = data["TotalQty"]
    GrandTotal = data["GrandTotal"]
    IsActive = data["IsActive"]

    Action = 'A'

    DamageStockMasterID = get_auto_idMaster(
        DamageStockMaster, BranchID, CompanyID)

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
        CompanyID=CompanyID,
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
        CompanyID=CompanyID,
    )

    damageStockDetails = data["DamageStockDetails"]

    for damageStockDetail in damageStockDetails:
        # BranchID = damageStockDetail["BranchID"]
        # DamageStockMasterID = damageStockDetail["DamageStockMasterID"]
        ProductID = damageStockDetail["ProductID"]
        Qty = damageStockDetail["Qty"]
        PriceListID = damageStockDetail["PriceListID"]
        Rate = damageStockDetail["Rate"]
        Amount = damageStockDetail["Amount"]

        DamageStockDetailsID = get_auto_id(
            DamageStockDetails, BranchID, CompanyID)

        DamageStockDetails.objects.create(
            DamageStockDetailsID=DamageStockDetailsID,
            BranchID=BranchID,
            DamageStockMasterID=DamageStockMasterID,
            ProductID=ProductID,
            Qty=Qty,
            PriceListID=PriceListID,
            Rate=Rate,
            Amount=Amount,
            Action=Action,
            CompanyID=CompanyID,
        )

        DamageStockDetails_Log.objects.create(
            TransactionID=DamageStockDetailsID,
            BranchID=BranchID,
            DamageStockMasterID=DamageStockMasterID,
            ProductID=ProductID,
            Qty=Qty,
            PriceListID=PriceListID,
            Rate=Rate,
            Amount=Amount,
            Action=Action,
            CompanyID=CompanyID,
        )

    dummies = DamageStockDetailsDummy.objects.filter(
        BranchID=BranchID, CompanyID=CompanyID)

    for dummy in dummies:
        dummy.delete()

    response_data = {
        "StatusCode": 6000,
        "message": "damageStock created Successfully!!!",
    }

    return Response(response_data, status=status.HTTP_200_OK)
    # else:
    #     response_data = {
    #         "StatusCode" : 6001,
    #         "message" : "Please enter a valid datas!!!",
    #         "master message" : generate_serializer_errors(stockMasterSerialized._errors),
    #         # "details message" : generate_serializer_errors(stockDetailSerialized._errors),
    #     }

    #     return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_damageStock(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    damageStockMaster_instance = None
    damageStockDetails = None

    damageStockMaster_instance = DamageStockMaster.objects.get(
        pk=pk, CompanyID=CompanyID)
    DamageStockMasterID = damageStockMaster_instance.DamageStockMasterID
    BranchID = damageStockMaster_instance.BranchID

    VoucherNo = data["VoucherNo"]
    Date = data["Date"]
    WarehouseID = data["WarehouseID"]
    Notes = data["Notes"]
    TotalQty = data["TotalQty"]
    GrandTotal = data["GrandTotal"]
    IsActive = data["IsActive"]

    Action = 'M'

    damageStockMaster_instance.VoucherNo = VoucherNo
    damageStockMaster_instance.Date = Date
    damageStockMaster_instance.WarehouseID = WarehouseID
    damageStockMaster_instance.Notes = Notes
    damageStockMaster_instance.TotalQty = TotalQty
    damageStockMaster_instance.GrandTotal = GrandTotal
    damageStockMaster_instance.IsActive = IsActive
    damageStockMaster_instance.Action = Action
    damageStockMaster_instance.CreatedUserID = CreatedUserID
    damageStockMaster_instance.UpdatedDate = today

    damageStockMaster_instance.save()

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
        CompanyID=CompanyID,
    )

    damageStockDetails = data["DamageStockDetails"]

    for damageStockDetail in damageStockDetails:
        # BranchID = damageStockDetail["BranchID"]
        # DamageStockMasterID = damageStockDetail["DamageStockMasterID"]
        pk = damageStockDetail["id"]
        ProductID = damageStockDetail["ProductID"]
        Qty = damageStockDetail["Qty"]
        PriceListID = damageStockDetail["PriceListID"]
        Rate = damageStockDetail["Rate"]
        Amount = damageStockDetail["Amount"]

        damageStockDetails_instance = DamageStockDetails.objects.get(
            pk=pk, CompanyID=CompanyID)
        DamageStockDetailsID = damageStockDetails_instance.DamageStockDetailsID
        damageStockDetails_instance.ProductID = ProductID
        damageStockDetails_instance.Qty = Qty
        damageStockDetails_instance.PriceListID = PriceListID
        damageStockDetails_instance.Rate = Rate
        damageStockDetails_instance.Amount = Amount
        damageStockDetails_instance.Action = Action

        damageStockDetails_instance.save()

        DamageStockDetails_Log.objects.create(
            TransactionID=DamageStockDetailsID,
            BranchID=BranchID,
            DamageStockMasterID=DamageStockMasterID,
            ProductID=ProductID,
            Qty=Qty,
            PriceListID=PriceListID,
            Rate=Rate,
            Amount=Amount,
            Action=Action,
            CompanyID=CompanyID,
        )

    # stockMasterSerialized = DamageStockMasterSerializer(DamageStockMasterID,BranchID)

    response_data = {
        "StatusCode": 6000,
        "message": "damageStock Updated Successfully!!!",
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def damageStockMaster(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    instance = None
    if DamageStockMaster.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instances = DamageStockMaster.objects.get(pk=pk, CompanyID=CompanyID)
        serialized = DamageStockMasterRestSerializer(
            instances, context={"CompanyID": CompanyID})
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
def list_damageStockMaster(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if DamageStockMaster.objects.filter(BranchID=BranchID, CompanyID=CompanyID).exists():

            instances = DamageStockMaster.objects.filter(
                BranchID=BranchID, CompanyID=CompanyID)

            serialized = DamageStockMasterRestSerializer(
                instances, many=True, context={"CompanyID": CompanyID})

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


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_damageStockDetails(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if DamageStockDetails.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = DamageStockDetails.objects.get(pk=pk, CompanyID=CompanyID)

        DamageStockDetailsID = instance.DamageStockDetailsID
        BranchID = instance.BranchID
        DamageStockMasterID = instance.DamageStockMasterID
        ProductID = instance.ProductID
        Qty = instance.Qty
        PriceListID = instance.PriceListID
        Rate = instance.Rate
        Amount = instance.Amount
        Action = "D"
        instance.delete()

        DamageStockDetails_Log.objects.create(
            TransactionID=DamageStockDetailsID,
            BranchID=BranchID,
            DamageStockMasterID=DamageStockMasterID,
            ProductID=ProductID,
            Qty=Qty,
            PriceListID=PriceListID,
            Rate=Rate,
            Amount=Amount,
            Action=Action,
            CompanyID=CompanyID,
        )
        response_data = {
            "StatusCode": 6000,
            "message": "Damage Stock Details Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Damage Stock Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_damageStockMaster(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if DamageStockMaster.objects.filter(pk=pk, CompanyID=CompanyID).exists():
        instance = DamageStockMaster.objects.get(pk=pk)
        DamageStockMasterID = instance.DamageStockMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        Date = instance.Date
        WarehouseID = instance.WarehouseID
        Notes = instance.Notes
        TotalQty = instance.TotalQty
        GrandTotal = instance.GrandTotal
        IsActive = instance.IsActive
        Action = "D"
        instance.delete()

        detail_instances = DamageStockDetails.objects.filter(
            DamageStockMasterID=DamageStockMasterID, BranchID=BranchID, CompanyID=CompanyID)

        for detail_instance in detail_instances:

            DamageStockDetailsID = detail_instance.DamageStockDetailsID
            BranchID = detail_instance.BranchID
            DamageStockMasterID = detail_instance.DamageStockMasterID
            ProductID = detail_instance.ProductID
            Qty = detail_instance.Qty
            PriceListID = detail_instance.PriceListID
            Rate = detail_instance.Rate
            Amount = detail_instance.Amount

            detail_instance.delete()

            DamageStockDetails_Log.objects.create(
                TransactionID=DamageStockDetailsID,
                BranchID=BranchID,
                DamageStockMasterID=DamageStockMasterID,
                ProductID=ProductID,
                Qty=Qty,
                PriceListID=PriceListID,
                Rate=Rate,
                Amount=Amount,
                Action=Action,
                CompanyID=CompanyID,
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
            CompanyID=CompanyID,
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
