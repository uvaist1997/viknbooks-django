from brands.models import OpeningStockDetails, OpeningStockDetails_Log, OpeningStockDetailsDummy
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v2.openingStockDetails.serializers import OpeningStockDetailsSerializer, OpeningStockDetailsRestSerializer, OpeningStockDetailsDummySerializer, OpeningStockDetailsDeletedDummySerializer
from api.v2.brands.serializers import ListSerializer
from api.v2.openingStockDetails.functions import generate_serializer_errors
from rest_framework import status
from api.v2.openingStockDetails.functions import get_auto_id
import datetime



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_openingStockDetails(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = OpeningStockDetailsSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        OpeningStockMasterID = serialized.data['OpeningStockMasterID']
        ProductID = serialized.data['ProductID']
        Qty = serialized.data['Qty']
        PriceListID = serialized.data['PriceListID']
        Rate = serialized.data['Rate']
        Amount = serialized.data['Amount']
       
        Action = "A"
        OpeningStockDetailsID = get_auto_id(OpeningStockDetails,BranchID,DataBase)
        OpeningStockDetails.objects.create(
            OpeningStockDetailsID=OpeningStockDetailsID,
            BranchID=BranchID,
            OpeningStockMasterID=OpeningStockMasterID,
            ProductID=ProductID,
            Qty=Qty,
            PriceListID=PriceListID,
            Rate=Rate,
            Amount=Amount,
            Action=Action,
            )

        OpeningStockDetails_Log.objects.create(
            TransactionID=OpeningStockDetailsID,
            BranchID=BranchID,
            OpeningStockMasterID=OpeningStockMasterID,
            ProductID=ProductID,
            Qty=Qty,
            PriceListID=PriceListID,
            Rate=Rate,
            Amount=Amount,
            Action=Action,
            )

        data = {"OpeningStockDetailsID" : OpeningStockDetailsID}
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
def edit_openingStockDetails(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    serialized = OpeningStockDetailsSerializer(data=request.data)
    instance = None
    if OpeningStockDetails.objects.filter(pk=pk).exists():
        instance = OpeningStockDetails.objects.get(pk=pk)

        OpeningStockDetailsID = instance.OpeningStockDetailsID
        BranchID = instance.BranchID

        if serialized.is_valid():
            OpeningStockMasterID = serialized.data['OpeningStockMasterID']
            ProductID = serialized.data['ProductID']
            Qty = serialized.data['Qty']
            PriceListID = serialized.data['PriceListID']
            Rate = serialized.data['Rate']
            Amount = serialized.data['Amount']
            Action = "M"

            instance.OpeningStockMasterID = OpeningStockMasterID
            instance.ProductID = ProductID
            instance.Qty = Qty
            instance.PriceListID = PriceListID
            instance.Rate = Rate
            instance.Amount = Amount
            instance.Action = Action
            instance.save()

            OpeningStockDetails_Log.objects.create(
                TransactionID=OpeningStockDetailsID,
                BranchID=BranchID,
                OpeningStockMasterID=OpeningStockMasterID,
                ProductID=ProductID,
                Qty=Qty,
                PriceListID=PriceListID,
                Rate=Rate,
                Amount=Amount,
                Action=Action,
                )

            data = {"OpeningStockDetailsID" : OpeningStockDetailsID}
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
            "message" : "Opening Stock Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_openingStockDetailss(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']  
        if OpeningStockDetails.objects.filter(BranchID=BranchID).exists():
            instances = OpeningStockDetails.objects.filter(BranchID=BranchID)
            serialized = OpeningStockDetailsRestSerializer(instances,many=True)

            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
            "StatusCode" : 6001,
            "message" : "Opening Stock Details Not Found in this BranchID!"
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
def openingStockDetails(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    if OpeningStockDetails.objects.filter(pk=pk).exists():
        instance = OpeningStockDetails.objects.get(pk=pk)
        serialized = OpeningStockDetailsRestSerializer(instance)
        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Opening Stock Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_openingStockDetails(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    if OpeningStockDetails.objects.filter(pk=pk).exists():
        instance = OpeningStockDetails.objects.get(pk=pk)
        OpeningStockDetailsID = instance.OpeningStockDetailsID
        BranchID = instance.BranchID
        OpeningStockMasterID = instance.OpeningStockMasterID
        ProductID = instance.ProductID
        Qty = instance.Qty
        PriceListID = instance.PriceListID
        Rate = instance.Rate
        Amount = instance.Amount
        Action = "D"

        instance.delete()

        OpeningStockDetails_Log.objects.create(
            TransactionID=OpeningStockDetailsID,
            BranchID=BranchID,
            OpeningStockMasterID=OpeningStockMasterID,
            ProductID=ProductID,
            Qty=Qty,
            PriceListID=PriceListID,
            Rate=Rate,
            Amount=Amount,
            Action=Action,
            )
        response_data = {
            "StatusCode" : 6000,
            "message" : "Opening Stock Details Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Opening Stock Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_openingStockDetailsDummy(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    BranchID = data['BranchID']
    OpeningStockMasterID = data['OpeningStockMasterID']
    OpeningStockDetailsID = data['OpeningStockDetailsID']
    ProductID = data['ProductID']
    Qty = data['Qty']
    PriceListID = data['PriceListID']
    Rate = data['Rate']
    Amount = data['Amount']
    detailID = data['detailID']

    detailID = 0

    OpeningStockDetailsDummy.objects.create(
        BranchID=BranchID,
        OpeningStockMasterID=OpeningStockMasterID,
        OpeningStockDetailsID=OpeningStockDetailsID,
        ProductID=ProductID,
        Qty=Qty,
        PriceListID=PriceListID,
        Rate=Rate,
        Amount=Amount,
        detailID=detailID
        )

    response_data = {
        "StatusCode" : 6000,
        "message" : "success!!!"
    }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_DummyforEditOpeningStock(request):

    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    dummydetails = data["DummyDetails"]
    BranchID = data["BranchID"]

    dummies = OpeningStockDetailsDummy.objects.filter(BranchID=BranchID)

    for dummy in dummies:
        dummy.delete()

    for dummydetail in dummydetails:
        unq_id = dummydetail['id']
        OpeningStockDetailsID = dummydetail['OpeningStockDetailsID']
        BranchID = dummydetail['BranchID']
        OpeningStockMasterID = dummydetail['OpeningStockMasterID']
        ProductID = dummydetail['ProductID']
        Qty = dummydetail['Qty']
        PriceListID = dummydetail['PriceListID']
        Rate = dummydetail['Rate']
        Amount = dummydetail['Amount']
        detailID = 0

        OpeningStockDetailsDummy.objects.create(
            unq_id=unq_id,
            BranchID=BranchID,
            OpeningStockDetailsID=OpeningStockDetailsID,
            OpeningStockMasterID=OpeningStockMasterID,
            ProductID=ProductID,
            Qty=Qty,
            PriceListID=PriceListID,
            Rate=Rate,
            Amount=Amount,
            detailID=detailID
            )

    response_data = {
        "StatusCode" : 6000,
        "message" : "success!!!"
    }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_openingStockDetailsDummy(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']  
        if OpeningStockDetailsDummy.objects.filter(BranchID=BranchID).exists():
            TotalAmount = 0
            TotalQty = 0
            instances = OpeningStockDetailsDummy.objects.filter(BranchID=BranchID,IsDeleted=False)
            for i in instances:
                TotalAmount += i.Amount
                TotalQty += i.Qty
            deleted_instances = OpeningStockDetailsDummy.objects.filter(BranchID=BranchID,IsDeleted=True)

            serialized = OpeningStockDetailsDummySerializer(instances,many=True,context = {"DataBase": DataBase })
            serializedDeleted = OpeningStockDetailsDeletedDummySerializer(deleted_instances,many=True)

            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data,
                "deleted_data" : serializedDeleted.data,
                "TotalAmount" : TotalAmount,
                "TotalQty" : TotalQty,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
            "StatusCode" : 6001,
            "message" : "Product Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "BranchID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_openingStockDetailsDummy(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    if OpeningStockDetailsDummy.objects.filter(pk=pk).exists():
        instance = OpeningStockDetailsDummy.objects.get(pk=pk)

        BranchID = data['BranchID']
        OpeningStockMasterID = data['OpeningStockMasterID']
        OpeningStockDetailsID = data['OpeningStockDetailsID']
        ProductID = data['ProductID']
        Qty = data['Qty']
        PriceListID = data['PriceListID']
        Rate = data['Rate']
        Amount = data['Amount']
        detailID = data['detailID']

        instance.BranchID = BranchID
        instance.OpeningStockMasterID = OpeningStockMasterID
        instance.OpeningStockDetailsID = OpeningStockDetailsID
        instance.ProductID = ProductID
        instance.Qty = Qty
        instance.PriceListID = PriceListID
        instance.Rate = Rate
        instance.Amount = Amount
        instance.detailID = detailID
        instance.save()

        response_data = {
            "StatusCode" : 6000,
            "message" : "Successfully updated!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Product Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_openingStockDetailsDummy(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    if OpeningStockDetailsDummy.objects.filter(pk=pk).exists():
        instance = OpeningStockDetailsDummy.objects.get(pk=pk)
        instance.IsDeleted = True
        instance.save()

        response_data = {
            "StatusCode" : 6000,
            "message" : "Product Removed Successfully!"
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Product Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)