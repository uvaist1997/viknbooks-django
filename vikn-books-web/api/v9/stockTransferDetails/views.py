from brands.models import StockTransferDetails, StockTransferDetails_Log, StockTransferDetailsDummy
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v9.stockTransferDetails.serializers import StockTransferDetailsSerializer, StockTransferDetailsRestSerializer, StockTransferDetailsDummySerializer
from api.v9.brands.serializers import ListSerializer
from api.v9.stockTransferDetails.functions import generate_serializer_errors
from rest_framework import status
from api.v9.stockTransferDetails.functions import get_auto_id
import datetime


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_stockTransferDetails(request):
    today = datetime.datetime.now()
    serialized = StockTransferDetailsSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        StockTransferMasterID = serialized.data['StockTransferMasterID']
        ProductID = serialized.data['ProductID']
        Qty = serialized.data['Qty']
        PriceListID = serialized.data['PriceListID']
        Rate = serialized.data['Rate']
        Amount = serialized.data['Amount']

        Action = "A"

        StockTransferDetailsID = get_auto_id(StockTransferDetails, BranchID)

        StockTransferDetails.objects.create(
            StockTransferDetailsID=StockTransferDetailsID,
            BranchID=BranchID,
            StockTransferMasterID=StockTransferMasterID,
            ProductID=ProductID,
            Qty=Qty,
            PriceListID=PriceListID,
            Rate=Rate,
            Amount=Amount,
            Action=Action,
        )

        StockTransferDetails_Log.objects.create(
            TransactionID=StockTransferDetailsID,
            BranchID=BranchID,
            StockTransferMasterID=StockTransferMasterID,
            ProductID=ProductID,
            Qty=Qty,
            PriceListID=PriceListID,
            Rate=Rate,
            Amount=Amount,
            Action=Action,
        )

        data = {"StockTransferDetailsID": StockTransferDetailsID}
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
def edit_stockTransferDetails(request, pk):
    serialized = StockTransferDetailsSerializer(data=request.data)
    instance = None
    if StockTransferDetails.objects.filter(pk=pk).exists():
        instance = StockTransferDetails.objects.get(pk=pk)

        StockTransferDetailsID = instance.StockTransferDetailsID
        BranchID = instance.BranchID

    if instance:
        if serialized.is_valid():
            StockTransferMasterID = serialized.data['StockTransferMasterID']
            ProductID = serialized.data['ProductID']
            Qty = serialized.data['Qty']
            PriceListID = serialized.data['PriceListID']
            Rate = serialized.data['Rate']
            Amount = serialized.data['Amount']

            Action = "M"

            instance.StockTransferMasterID = StockTransferMasterID
            instance.ProductID = ProductID
            instance.Qty = Qty
            instance.PriceListID = PriceListID
            instance.Rate = Rate
            instance.Amount = Amount
            instance.Action = Action
            instance.save()

            StockTransferDetails_Log.objects.create(
                TransactionID=StockTransferDetailsID,
                BranchID=BranchID,
                StockTransferMasterID=StockTransferMasterID,
                ProductID=ProductID,
                Qty=Qty,
                PriceListID=PriceListID,
                Rate=Rate,
                Amount=Amount,
                Action=Action,
            )

            data = {"StockTransferDetailsID": StockTransferDetailsID}
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
            "message": "Stock Transfer Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_stockTransferDetails(request):
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if StockTransferDetails.objects.filter(BranchID=BranchID).exists():

            instances = StockTransferDetails.objects.filter(BranchID=BranchID)

            serialized = StockTransferDetailsRestSerializer(
                instances, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Stock Transfer Details Not Found in this BranchID!"
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
def stockTransferDetails(request, pk):
    instance = None
    if StockTransferDetails.objects.filter(pk=pk).exists():
        instance = StockTransferDetails.objects.get(pk=pk)
    if instance:
        serialized = StockTransferDetailsRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Stock Transfer Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_stockTransferDetails(request, pk):
    instance = None
    if StockTransferDetails.objects.filter(pk=pk).exists():
        instance = StockTransferDetails.objects.get(pk=pk)
    if instance:
        StockTransferDetailsID = instance.StockTransferDetailsID
        BranchID = instance.BranchID
        StockTransferMasterID = instance.StockTransferMasterID
        ProductID = instance.ProductID
        Qty = instance.Qty
        PriceListID = instance.PriceListID
        Rate = instance.Rate
        Amount = instance.Amount
        Action = "D"

        instance.delete()

        StockTransferDetails_Log.objects.create(
            TransactionID=StockTransferDetailsID,
            BranchID=BranchID,
            StockTransferMasterID=StockTransferMasterID,
            ProductID=ProductID,
            Qty=Qty,
            PriceListID=PriceListID,
            Rate=Rate,
            Amount=Amount,
            Action=Action,
        )

        response_data = {
            "StatusCode": 6000,
            "message": "Stock Transfer Details Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Stock Transfer Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_stockTransferDetailsDummy(request):

    data = request.data

    StockTransferDetailsID = data['StockTransferDetailsID']
    BranchID = data['BranchID']
    StockTransferMasterID = data['StockTransferMasterID']
    ProductID = data['ProductID']
    Qty = data['Qty']
    PriceListID = data['PriceListID']
    Rate = data['Rate']
    Amount = data['Amount']

    detailID = data['detailID']

    StockTransferDetailsDummy.objects.create(
        StockTransferDetailsID=StockTransferDetailsID,
        BranchID=BranchID,
        StockTransferMasterID=StockTransferMasterID,
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
def create_DummyforEditStockTransferMaster(request):

    data = request.data

    dummydetails = data["DummyDetails"]
    BranchID = data["BranchID"]

    dummies = StockTransferDetailsDummy.objects.filter(BranchID=BranchID)

    for dummy in dummies:
        dummy.delete()

    for dummydetail in dummydetails:
        unq_id = dummydetail['id']
        StockTransferDetailsID = dummydetail['StockTransferDetailsID']
        BranchID = dummydetail['BranchID']
        StockTransferMasterID = dummydetail['StockTransferMasterID']
        ProductID = dummydetail['ProductID']
        Qty = dummydetail['Qty']
        PriceListID = dummydetail['PriceListID']
        Rate = dummydetail['Rate']
        Amount = dummydetail['Amount']

        detailID = 0

        StockTransferDetailsDummy.objects.create(
            unq_id=unq_id,
            StockTransferDetailsID=StockTransferDetailsID,
            BranchID=BranchID,
            StockTransferMasterID=StockTransferMasterID,
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
def list_stockTransferDetailsDummy(request):
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if StockTransferDetailsDummy.objects.filter(BranchID=BranchID).exists():

            instances = StockTransferDetailsDummy.objects.filter(
                BranchID=BranchID)

            serialized = StockTransferDetailsDummySerializer(
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
def edit_stockTransferDetailsDummy(request, pk):
    instance = None
    if StockTransferDetailsDummy.objects.filter(pk=pk).exists():

        instance = StockTransferDetailsDummy.objects.get(pk=pk)

        data = request.data
        StockTransferDetailsID = data['StockTransferDetailsID']
        BranchID = data['BranchID']
        StockTransferMasterID = data['StockTransferMasterID']
        ProductID = data['ProductID']
        Qty = data['Qty']
        PriceListID = data['PriceListID']
        Rate = data['Rate']
        Amount = data['Amount']
        detailID = data['detailID']

        instance.StockTransferDetailsID = StockTransferDetailsID
        instance.BranchID = BranchID
        instance.StockTransferMasterID = StockTransferMasterID
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
def delete_stockTransferDetailsDummy(request, pk):
    instance = None
    if StockTransferDetailsDummy.objects.filter(pk=pk).exists():
        instance = StockTransferDetailsDummy.objects.get(pk=pk)
    if instance:

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
