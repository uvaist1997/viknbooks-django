from brands.models import StockReceiptDetails, StockReceiptDetails_Log, StockReceiptDetailsDummy
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v8.stockReceiptDetails.serializers import StockReceiptDetailsSerializer, StockReceiptDetailsRestSerializer, StockReceiptDetailsDummySerializer
from api.v8.brands.serializers import ListSerializer
from api.v8.stockReceiptDetails.functions import generate_serializer_errors
from rest_framework import status
from api.v8.stockReceiptDetails.functions import get_auto_id
import datetime


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_stockReceiptDetails(request):
    today = datetime.datetime.now()
    serialized = StockReceiptDetailsSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        StockReceiptMasterID = serialized.data['StockReceiptMasterID']
        ProductID = serialized.data['ProductID']
        Qty = serialized.data['Qty']
        PriceListID = serialized.data['PriceListID']
        Rate = serialized.data['Rate']
        Amount = serialized.data['Amount']

        Action = "A"

        StockReceiptDetailsID = get_auto_id(StockReceiptDetails, BranchID)

        StockReceiptDetails.objects.create(
            StockReceiptDetailsID=StockReceiptDetailsID,
            BranchID=BranchID,
            StockReceiptMasterID=StockReceiptMasterID,
            ProductID=ProductID,
            Qty=Qty,
            PriceListID=PriceListID,
            Rate=Rate,
            Amount=Amount,
            Action=Action,
        )

        StockReceiptDetails_Log.objects.create(
            TransactionID=StockReceiptDetailsID,
            BranchID=BranchID,
            StockReceiptMasterID=StockReceiptMasterID,
            ProductID=ProductID,
            Qty=Qty,
            PriceListID=PriceListID,
            Rate=Rate,
            Amount=Amount,
            Action=Action,
        )

        data = {"StockReceiptDetailsID": StockReceiptDetailsID}
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
def edit_stockReceiptDetails(request, pk):
    serialized = StockReceiptDetailsSerializer(data=request.data)
    instance = None
    if StockReceiptDetails.objects.filter(pk=pk).exists():
        instance = StockReceiptDetails.objects.get(pk=pk)

        StockReceiptDetailsID = instance.StockReceiptDetailsID
        BranchID = instance.BranchID

    if instance:
        if serialized.is_valid():
            StockReceiptMasterID = serialized.data['StockReceiptMasterID']
            ProductID = serialized.data['ProductID']
            Qty = serialized.data['Qty']
            PriceListID = serialized.data['PriceListID']
            Rate = serialized.data['Rate']
            Amount = serialized.data['Amount']

            Action = "M"

            instance.StockReceiptMasterID = StockReceiptMasterID
            instance.ProductID = ProductID
            instance.Qty = Qty
            instance.PriceListID = PriceListID
            instance.Rate = Rate
            instance.Amount = Amount
            instance.Action = Action
            instance.save()

            StockReceiptDetails_Log.objects.create(
                TransactionID=StockReceiptDetailsID,
                BranchID=BranchID,
                StockReceiptMasterID=StockReceiptMasterID,
                ProductID=ProductID,
                Qty=Qty,
                PriceListID=PriceListID,
                Rate=Rate,
                Amount=Amount,
                Action=Action,
            )

            data = {"StockReceiptDetailsID": StockReceiptDetailsID}
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
            "message": "Stock Receipt Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_stockReceiptDetails(request):
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if StockReceiptDetails.objects.filter(BranchID=BranchID).exists():

            instances = StockReceiptDetails.objects.filter(BranchID=BranchID)

            serialized = StockReceiptDetailsRestSerializer(
                instances, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Stock Receipt Details Not Found in this BranchID!"
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
def receiptDetail(request, pk):
    instance = None
    if StockReceiptDetails.objects.filter(pk=pk).exists():
        instance = StockReceiptDetails.objects.get(pk=pk)
    if instance:
        serialized = StockReceiptDetailsRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Stock Receipt Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_stockReceiptDetails(request, pk):
    instance = None
    if StockReceiptDetails.objects.filter(pk=pk).exists():
        instance = StockReceiptDetails.objects.get(pk=pk)
    if instance:
        StockReceiptDetailsID = instance.StockReceiptDetailsID
        BranchID = instance.BranchID
        StockReceiptMasterID = instance.StockReceiptMasterID
        ProductID = instance.ProductID
        Qty = instance.Qty
        PriceListID = instance.PriceListID
        Rate = instance.Rate
        Amount = instance.Amount
        Action = "D"

        instance.delete()

        StockReceiptDetails_Log.objects.create(
            TransactionID=StockReceiptDetailsID,
            BranchID=BranchID,
            StockReceiptMasterID=StockReceiptMasterID,
            ProductID=ProductID,
            Qty=Qty,
            PriceListID=PriceListID,
            Rate=Rate,
            Amount=Amount,
            Action=Action,
        )
        response_data = {
            "StatusCode": 6000,
            "message": "Stock Receipt Details Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Stock Receipt Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_stockReceiptDetailsDummy(request):

    data = request.data

    BranchID = data['BranchID']
    StockReceiptMasterID = data['StockReceiptMasterID']
    ProductID = data['ProductID']
    Qty = data['Qty']
    PriceListID = data['PriceListID']
    Rate = data['Rate']
    Amount = data['Amount']

    detailID = 0

    StockReceiptDetailsDummy.objects.create(
        BranchID=BranchID,
        StockReceiptMasterID=StockReceiptMasterID,
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
def create_DummyforEditStockReceiptMaster(request):

    data = request.data

    dummydetails = data["DummyDetails"]
    BranchID = data["BranchID"]

    dummies = StockReceiptDetailsDummy.objects.filter(BranchID=BranchID)

    for dummy in dummies:
        dummy.delete()

    for dummydetail in dummydetails:

        BranchID = dummydetail['BranchID']
        StockReceiptMasterID = dummydetail['StockReceiptMasterID']
        ProductID = dummydetail['ProductID']
        Qty = dummydetail['Qty']
        PriceListID = dummydetail['PriceListID']
        Rate = dummydetail['Rate']
        Amount = dummydetail['Amount']

        detailID = 0

        StockReceiptDetailsDummy.objects.create(
            BranchID=BranchID,
            StockReceiptMasterID=StockReceiptMasterID,
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
def list_stockReceiptDetailsDummy(request):
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if StockReceiptDetailsDummy.objects.filter(BranchID=BranchID).exists():

            instances = StockReceiptDetailsDummy.objects.filter(
                BranchID=BranchID)

            serialized = StockReceiptDetailsDummySerializer(
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
def edit_stockReceiptDetailsDummy(request, pk):
    instance = None
    if StockReceiptDetailsDummy.objects.filter(pk=pk).exists():

        instance = StockReceiptDetailsDummy.objects.get(pk=pk)

        data = request.data

        BranchID = data['BranchID']
        StockReceiptMasterID = data['StockReceiptMasterID']
        ProductID = data['ProductID']
        Qty = data['Qty']
        PriceListID = data['PriceListID']
        Rate = data['Rate']
        Amount = data['Amount']
        detailID = data['detailID']

        instance.BranchID = BranchID
        instance.StockReceiptMasterID = StockReceiptMasterID
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
def delete_stockReceiptDetailsDummy(request, pk):
    instance = None
    if StockReceiptDetailsDummy.objects.filter(pk=pk).exists():
        instance = StockReceiptDetailsDummy.objects.get(pk=pk)
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
