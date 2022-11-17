from brands.models import StockAdjustmentDetails, StockAdjustmentDetails_Log, StockAdjustmentDetailsDummy
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v5.stockAdjustmentDetails.serializers import StockAdjustmentDetailsSerializer, StockAdjustmentDetailsRestSerializer, StockAdjustmentDetailsDummySerializer
from api.v5.brands.serializers import ListSerializer
from api.v5.stockAdjustmentDetails.functions import generate_serializer_errors
from rest_framework import status
from api.v5.stockAdjustmentDetails.functions import get_auto_id
import datetime


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_stockAdjustmentDetails(request):
    today = datetime.datetime.now()
    serialized = StockAdjustmentDetailsSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        StockAdjustmentMasterID = serialized.data['StockAdjustmentMasterID']
        ProductID = serialized.data['ProductID']
        PriceListID = serialized.data['PriceListID']
        ActualStock = serialized.data['ActualStock']
        PhysicalStock = serialized.data['PhysicalStock']
        Difference = serialized.data['Difference']

        Action = "A"

        StockAdjustmentDetailsID = get_auto_id(
            StockAdjustmentDetails, BranchID)

        StockAdjustmentDetails.objects.create(
            StockAdjustmentDetailsID=StockAdjustmentDetailsID,
            BranchID=BranchID,
            StockAdjustmentMasterID=StockAdjustmentMasterID,
            ProductID=ProductID,
            PriceListID=PriceListID,
            ActualStock=ActualStock,
            PhysicalStock=PhysicalStock,
            Difference=Difference,
            Action=Action,
        )

        StockAdjustmentDetails_Log.objects.create(
            TransactionID=StockAdjustmentDetailsID,
            BranchID=BranchID,
            StockAdjustmentMasterID=StockAdjustmentMasterID,
            ProductID=ProductID,
            PriceListID=PriceListID,
            ActualStock=ActualStock,
            PhysicalStock=PhysicalStock,
            Difference=Difference,
            Action=Action,
        )

        data = {"StockAdjustmentDetailsID": StockAdjustmentDetailsID}
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
def edit_stockAdjustmentDetails(request, pk):
    serialized = StockAdjustmentDetailsSerializer(data=request.data)
    instance = None
    if StockAdjustmentDetails.objects.filter(pk=pk).exists():
        instance = StockAdjustmentDetails.objects.get(pk=pk)

        StockAdjustmentDetailsID = instance.StockAdjustmentDetailsID
        BranchID = instance.BranchID

    if instance:
        if serialized.is_valid():
            StockAdjustmentMasterID = serialized.data['StockAdjustmentMasterID']
            ProductID = serialized.data['ProductID']
            PriceListID = serialized.data['PriceListID']
            ActualStock = serialized.data['ActualStock']
            PhysicalStock = serialized.data['PhysicalStock']
            Difference = serialized.data['Difference']

            Action = "M"

            instance.StockAdjustmentMasterID = StockAdjustmentMasterID
            instance.ProductID = ProductID
            instance.PriceListID = PriceListID
            instance.ActualStock = ActualStock
            instance.PhysicalStock = PhysicalStock
            instance.Difference = Difference
            instance.Action = Action
            instance.save()

            StockAdjustmentDetails_Log.objects.create(
                TransactionID=StockAdjustmentDetailsID,
                BranchID=BranchID,
                StockAdjustmentMasterID=StockAdjustmentMasterID,
                ProductID=ProductID,
                PriceListID=PriceListID,
                ActualStock=ActualStock,
                PhysicalStock=PhysicalStock,
                Difference=Difference,
                Action=Action,
            )

            data = {"StockAdjustmentDetailsID": StockAdjustmentDetailsID}
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
            "message": "Stock Adjustment Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_stockAdjustmentDetails(request):
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if StockAdjustmentDetails.objects.filter(BranchID=BranchID).exists():

            instances = StockAdjustmentDetails.objects.filter(
                BranchID=BranchID)

            serialized = StockAdjustmentDetailsRestSerializer(
                instances, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Stock Adjustment Details Not Found in this BranchID!"
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
def stockAdjustmentDetails(request, pk):
    instance = None
    if StockAdjustmentDetails.objects.filter(pk=pk).exists():
        instance = StockAdjustmentDetails.objects.get(pk=pk)
    if instance:
        serialized = StockAdjustmentDetailsRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Stock Adjustment Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_stockAdjustmentDetails(request, pk):
    instance = None
    if StockAdjustmentDetails.objects.filter(pk=pk).exists():
        instance = StockAdjustmentDetails.objects.get(pk=pk)
    if instance:
        StockAdjustmentDetailsID = instance.StockAdjustmentDetailsID
        BranchID = instance.BranchID
        StockAdjustmentMasterID = instance.StockAdjustmentMasterID
        ProductID = instance.ProductID
        PriceListID = instance.PriceListID
        ActualStock = instance.ActualStock
        PhysicalStock = instance.PhysicalStock
        Difference = instance.Difference
        Action = "D"

        instance.delete()

        StockAdjustmentDetails_Log.objects.create(
            TransactionID=StockAdjustmentDetailsID,
            BranchID=BranchID,
            StockAdjustmentMasterID=StockAdjustmentMasterID,
            ProductID=ProductID,
            PriceListID=PriceListID,
            ActualStock=ActualStock,
            PhysicalStock=PhysicalStock,
            Difference=Difference,
            Action=Action,
        )
        response_data = {
            "StatusCode": 6000,
            "message": "Stock Adjustment Details Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Stock Adjustment Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_stockAdjustmentDetailsDummy(request):

    data = request.data

    BranchID = data['BranchID']
    StockAdjustmentMasterID = data['StockAdjustmentMasterID']
    ProductID = data['ProductID']
    PriceListID = data['PriceListID']
    ActualStock = data['ActualStock']
    PhysicalStock = data['PhysicalStock']
    Difference = data['Difference']

    detailID = 0

    StockAdjustmentDetailsDummy.objects.create(
        BranchID=BranchID,
        StockAdjustmentMasterID=StockAdjustmentMasterID,
        ProductID=ProductID,
        PriceListID=PriceListID,
        ActualStock=ActualStock,
        PhysicalStock=PhysicalStock,
        Difference=Difference,
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
def create_DummyforEditStockAdjustmentMaster(request):

    data = request.data

    dummydetails = data["DummyDetails"]
    BranchID = data["BranchID"]

    dummies = StockAdjustmentDetailsDummy.objects.filter(BranchID=BranchID)

    for dummy in dummies:
        dummy.delete()

    for dummydetail in dummydetails:

        BranchID = dummydetail['BranchID']
        StockAdjustmentMasterID = dummydetail['StockAdjustmentMasterID']
        ProductID = dummydetail['ProductID']
        PriceListID = dummydetail['PriceListID']
        ActualStock = dummydetail['ActualStock']
        PhysicalStock = dummydetail['PhysicalStock']
        Difference = dummydetail['Difference']

        detailID = 0

        StockAdjustmentDetailsDummy.objects.create(
            BranchID=BranchID,
            StockAdjustmentMasterID=StockAdjustmentMasterID,
            ProductID=ProductID,
            PriceListID=PriceListID,
            ActualStock=ActualStock,
            PhysicalStock=PhysicalStock,
            Difference=Difference,
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
def list_stockAdjustmentDetailsDummy(request):
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if StockAdjustmentDetailsDummy.objects.filter(BranchID=BranchID).exists():

            instances = StockAdjustmentDetailsDummy.objects.filter(
                BranchID=BranchID)

            serialized = StockAdjustmentDetailsDummySerializer(
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
def edit_stockAdjustmentDetailsDummy(request, pk):
    instance = None
    if StockAdjustmentDetailsDummy.objects.filter(pk=pk).exists():

        instance = StockAdjustmentDetailsDummy.objects.get(pk=pk)

        data = request.data

        BranchID = data['BranchID']
        StockAdjustmentMasterID = data['StockAdjustmentMasterID']
        ProductID = data['ProductID']
        PriceListID = data['PriceListID']
        ActualStock = data['ActualStock']
        PhysicalStock = data['PhysicalStock']
        Difference = data['Difference']
        detailID = data['detailID']

        instance.BranchID = BranchID
        instance.StockAdjustmentMasterID = StockAdjustmentMasterID
        instance.ProductID = ProductID
        instance.PriceListID = PriceListID
        instance.ActualStock = ActualStock
        instance.PhysicalStock = PhysicalStock
        instance.Difference = Difference
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
def delete_stockAdjustmentDetailsDummy(request, pk):
    instance = None
    if StockAdjustmentDetailsDummy.objects.filter(pk=pk).exists():
        instance = StockAdjustmentDetailsDummy.objects.get(pk=pk)
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
