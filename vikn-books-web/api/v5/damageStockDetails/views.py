from brands.models import DamageStockDetails, DamageStockDetails_Log, DamageStockMaster, DamageStockMaster_Log, DamageStockDetailsDummy
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from api.v5.damageStockDetails.serializers import DamageStockDetailsSerializer, DamageStockDetailsRestSerializer, DamageStockDetailsDummySerializer
from api.v5.damageStockMaster.serializers import DamageStockMasterSerializer, DamageStockMasterRestSerializer

from api.v5.brands.serializers import ListSerializer
from api.v5.damageStockDetails.functions import generate_serializer_errors
from rest_framework import status
from api.v5.damageStockDetails.functions import get_auto_id
from api.v5.damageStockMaster.functions import get_auto_idMaster
# from api.v5.damageStockDetails.functions import get_auto_idDetails
import datetime


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_damageStock(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    stockMasterSerialized = DamageStockMasterSerializer(data=request.data)
    stockDetailSerialized = DamageStockDetailsSerializer(data=request.data)

    if stockDetailSerialized.is_valid() and stockMasterSerialized.is_valid():
        BranchID = stockMasterSerialized.data['BranchID']
        VoucherNo = stockMasterSerialized.data['VoucherNo']
        InvoiceNo = stockMasterSerialized.data['InvoiceNo']
        Date = stockMasterSerialized.data['Date']
        WarehouseID = stockMasterSerialized.data['WarehouseID']
        Notes = stockMasterSerialized.data['Notes']
        TotalQty = stockMasterSerialized.data['TotalQty']
        GrandTotal = stockMasterSerialized.data['GrandTotal']
        IsActive = stockMasterSerialized.data['IsActive']

        # DamageStockMasterID = serialized.data['DamageStockMasterID']
        ProductID = stockDetailSerialized.data['ProductID']
        Qty = stockDetailSerialized.data['Qty']
        PriceListID = stockDetailSerialized.data['PriceListID']
        Rate = stockDetailSerialized.data['Rate']
        Amount = stockDetailSerialized.data['Amount']

        Action = 'A'

        DamageStockMasterID = get_auto_idMaster(
            DamageStockMaster, BranchID, DataBase)
        DamageStockDetailsID = get_auto_id(
            DamageStockDetails, BranchID, DataBase)

        DamageStockMaster.objects.create(
            DamageStockMasterID=DamageStockMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
            Date=Date,
            WarehouseID=WarehouseID,
            Notes=Notes,
            TotalQty=TotalQty,
            GrandTotal=GrandTotal,
            IsActive=IsActive,
            Action=Action,
            CreatedDate=today,
        )

        DamageStockMaster_Log.objects.create(
            TransactionID=DamageStockMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
            Date=Date,
            WarehouseID=WarehouseID,
            Notes=Notes,
            TotalQty=TotalQty,
            GrandTotal=GrandTotal,
            IsActive=IsActive,
            Action=Action,
            CreatedDate=today,
        )

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
        )

        master = {"DamageStockMasterID": DamageStockMasterID}
        details = {"DamageStockDetailsID": DamageStockDetailsID}
        master.update(stockMasterSerialized.data)
        details.update(stockDetailSerialized.data)
        response_data = {
            "StatusCode": 6000,
            "master": master,
            "details": details
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(stockDetailSerialized._errors),
            # "message" : generate_serializer_errors(stockMasterSerialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_damageStockDetails(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = DamageStockDetailsSerializer(data=request.data)
    instance = DamageStockDetails.objects.get(pk=pk)
    DamageStockDetailsID = instance.DamageStockDetailsID
    BranchID = instance.BranchID

    if serialized.is_valid():

        DamageStockMasterID = serialized.data['DamageStockMasterID']
        ProductID = serialized.data['ProductID']
        Qty = serialized.data['Qty']
        PriceListID = serialized.data['PriceListID']
        Rate = serialized.data['Rate']
        Amount = serialized.data['Amount']

        Action = 'M'

        instance.DamageStockMasterID = DamageStockMasterID
        instance.ProductID = ProductID
        instance.Qty = Qty
        instance.PriceListID = PriceListID
        instance.Rate = Rate
        instance.Amount = Amount
        instance.Action = Action

        instance.save()

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
        )

        data = {"DamageStockDetailsID": DamageStockDetailsID}
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
def list_damageStockDetails(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if DamageStockDetails.objects.filter(BranchID=BranchID).exists():
            instances = DamageStockDetails.objects.filter(BranchID=BranchID)
            serialized = DamageStockDetailsRestSerializer(instances, many=True)
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Damage Stock Details Not Found in this BranchID!"
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
def damageStockDetails(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    instance = None
    if DamageStockDetails.objects.filter(pk=pk).exists():
        instance = DamageStockDetails.objects.get(pk=pk)
        serialized = DamageStockDetailsRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
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
def delete_damageStockDetails(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    instance = None
    if DamageStockDetails.objects.filter(pk=pk).exists():
        instance = DamageStockDetails.objects.get(pk=pk)
    if instance:
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
def create_damageStockDetailsDummy(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']
    BranchID = data['BranchID']
    DamageStockMasterID = data['DamageStockMasterID']
    ProductID = data['ProductID']
    Qty = data['Qty']
    PriceListID = data['PriceListID']
    Rate = data['Rate']
    Amount = data['Amount']

    detailID = 0

    DamageStockDetailsDummy.objects.create(
        BranchID=BranchID,
        DamageStockMasterID=DamageStockMasterID,
        ProductID=ProductID,
        Qty=Qty,
        PriceListID=PriceListID,
        Rate=Rate,
        Amount=Amount,
        detailID=detailID
    )

    response_data = {
        "StatusCode": 6000,
        "message": "success!!!"
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_DummyforEditDamageStock(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    dummydetails = data["DummyDetails"]
    BranchID = data["BranchID"]
    dummies = DamageStockDetailsDummy.objects.filter(BranchID=BranchID)
    for dummy in dummies:
        dummy.delete()

    for dummydetail in dummydetails:

        BranchID = dummydetail['BranchID']
        DamageStockMasterID = dummydetail['DamageStockMasterID']
        ProductID = dummydetail['ProductID']
        Qty = dummydetail['Qty']
        PriceListID = dummydetail['PriceListID']
        Rate = dummydetail['Rate']
        Amount = dummydetail['Amount']
        detailID = 0

        DamageStockDetailsDummy.objects.create(
            BranchID=BranchID,
            DamageStockMasterID=DamageStockMasterID,
            ProductID=ProductID,
            Qty=Qty,
            PriceListID=PriceListID,
            Rate=Rate,
            Amount=Amount,
            detailID=detailID
        )

    response_data = {
        "StatusCode": 6000,
        "message": "success!!!"
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_damageStockDetailsDummy(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if DamageStockDetailsDummy.objects.filter(BranchID=BranchID).exists():
            instances = DamageStockDetailsDummy.objects.filter(
                BranchID=BranchID)
            serialized = DamageStockDetailsDummySerializer(
                instances, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Product Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "BranchID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_damageStockDetailsDummy(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    instance = None
    if DamageStockDetailsDummy.objects.filter(pk=pk).exists():
        instance = DamageStockDetailsDummy.objects.get(pk=pk)

        BranchID = data['BranchID']
        DamageStockMasterID = data['DamageStockMasterID']
        ProductID = data['ProductID']
        Qty = data['Qty']
        PriceListID = data['PriceListID']
        Rate = data['Rate']
        Amount = data['Amount']
        detailID = data['detailID']

        instance.BranchID = BranchID
        instance.DamageStockMasterID = DamageStockMasterID
        instance.ProductID = ProductID
        instance.Qty = Qty
        instance.PriceListID = PriceListID
        instance.Rate = Rate
        instance.Amount = Amount
        instance.detailID = detailID
        instance.save()

        response_data = {
            "StatusCode": 6000,
            "message": "Successfully updated!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Product Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_damageStockDetailsDummy(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    instance = None
    if DamageStockDetailsDummy.objects.filter(pk=pk).exists():
        instance = DamageStockDetailsDummy.objects.get(pk=pk)
        instance.delete()

        response_data = {
            "StatusCode": 6000,
            "message": "Product Removed Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Product Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)
