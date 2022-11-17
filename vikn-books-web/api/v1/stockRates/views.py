from brands.models import StockPosting, StockPosting_Log
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v1.stockPostings.serializers import StockPostingSerializer, StockPostingRestSerializer
from api.v1.brands.serializers import ListSerializer
from api.v1.stockPostings.functions import generate_serializer_errors
from rest_framework import status
from api.v1.stockPostings.functions import get_auto_id
import datetime
from main.functions import get_company


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_stockRate(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    serialized = StockPostingSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        Date = serialized.data['Date']
        VoucherMasterID = serialized.data['VoucherMasterID']
        ProductID = serialized.data['ProductID']
        BatchID = serialized.data['BatchID']
        WareHouseID = serialized.data['WareHouseID']
        QtyIn = serialized.data['QtyIn']
        QtyOut = serialized.data['QtyOut']
        Rate = serialized.data['Rate']
        PriceListID = serialized.data['PriceListID']
        IsActive = serialized.data['IsActive']
        
        Action = "A"

        StockPostingID = get_auto_id(StockPosting,BranchID,CompanyID)

        StockPosting.objects.create(
            StockPostingID=StockPostingID,
            BranchID=BranchID,
            Action=Action,
            Date=Date,
            VoucherMasterID=VoucherMasterID,
            ProductID=ProductID,
            BatchID=BatchID,
            WareHouseID=WareHouseID,
            QtyIn=QtyIn,
            QtyOut=QtyOut,
            Rate=Rate,
            PriceListID=PriceListID,
            IsActive=IsActive,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            CompanyID=CompanyID
            )

        StockPosting_Log.objects.create(
            TransactionID=StockPostingID,
            BranchID=BranchID,
            Action=Action,
            Date=Date,
            VoucherMasterID=VoucherMasterID,
            ProductID=ProductID,
            BatchID=BatchID,
            WareHouseID=WareHouseID,
            QtyIn=QtyIn,
            QtyOut=QtyOut,
            Rate=Rate,
            PriceListID=PriceListID,
            IsActive=IsActive,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            CompanyID=CompanyID
            )

        data = {"StockPostingID" : StockPostingID}
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
def edit_stockRate(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    serialized = StockPostingSerializer(data=request.data)
    instance = None
    if StockPosting.objects.filter(CompanyID=CompanyID,pk=pk).exists():
        instance = StockPosting.objects.get(CompanyID=CompanyID,pk=pk)

        StockPostingID = instance.StockPostingID
        BranchID = instance.BranchID
        
    if instance:
        if serialized.is_valid():
            Date = serialized.data['Date']
            VoucherMasterID = serialized.data['VoucherMasterID']
            ProductID = serialized.data['ProductID']
            BatchID = serialized.data['BatchID']
            WareHouseID = serialized.data['WareHouseID']
            QtyIn = serialized.data['QtyIn']
            QtyOut = serialized.data['QtyOut']
            Rate = serialized.data['Rate']
            PriceListID = serialized.data['PriceListID']
            IsActive = serialized.data['IsActive']

            Action = "M"


            instance.Date = Date
            instance.VoucherMasterID = VoucherMasterID
            instance.ProductID = ProductID
            instance.BatchID = BatchID
            instance.WareHouseID = WareHouseID
            instance.QtyIn = QtyIn
            instance.QtyOut = QtyOut
            instance.Rate = Rate
            instance.PriceListID = PriceListID
            instance.IsActive = IsActive
            instance.Action = Action
            instance.UpdatedDate = today
            instance.CreatedUserID = CreatedUserID
            instance.save()

            StockPosting_Log.objects.create(
                TransactionID=StockPostingID,
                BranchID=BranchID,
                Action=Action,
                Date=Date,
                VoucherMasterID=VoucherMasterID,
                ProductID=ProductID,
                BatchID=BatchID,
                WareHouseID=WareHouseID,
                QtyIn=QtyIn,
                QtyOut=QtyOut,
                Rate=Rate,
                PriceListID=PriceListID,
                IsActive=IsActive,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                CompanyID=CompanyID,
                )

            data = {"StockPostingID" : StockPostingID}
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
            "message" : "Stock Posting Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def stockRates(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if StockPosting.objects.filter(CompanyID=CompanyID,BranchID=BranchID).exists():
            instances = StockPosting.objects.filter(CompanyID=CompanyID,BranchID=BranchID)
            serialized = StockPostingRestSerializer(instances,many=True)
            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
            "StatusCode" : 6001,
            "message" : "Stock Posting Not Found in this BranchID!"
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
def stockRate(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    instance = None
    if StockPosting.objects.filter(CompanyID=CompanyID,pk=pk).exists():
        instance = StockPosting.objects.get(CompanyID=CompanyID,pk=pk)
    if instance:
        serialized = StockPostingRestSerializer(instance)
        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "StockPosting Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_stockRate(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    today = datetime.datetime.now()
    instance = None
    if StockPosting.objects.filter(CompanyID=CompanyID,pk=pk).exists():
        instance = StockPosting.objects.get(CompanyID=CompanyID,pk=pk)
        StockPostingID = instance.StockPostingID
        BranchID = instance.BranchID
        Date = instance.Date
        VoucherMasterID = instance.VoucherMasterID
        ProductID = instance.ProductID
        BatchID = instance.BatchID
        WareHouseID = instance.WareHouseID
        QtyIn = instance.QtyIn
        QtyOut = instance.QtyOut
        Rate = instance.Rate
        PriceListID = instance.PriceListID
        IsActive = instance.IsActive
        Action = "D"

        instance.delete()

        StockPosting_Log.objects.create(
            TransactionID=StockPostingID,
            BranchID=BranchID,
            Action=Action,
            Date=Date,
            VoucherMasterID=VoucherMasterID,
            ProductID=ProductID,
            BatchID=BatchID,
            WareHouseID=WareHouseID,
            QtyIn=QtyIn,
            QtyOut=QtyOut,
            Rate=Rate,
            PriceListID=PriceListID,
            IsActive=IsActive,
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            CompanyID=CompanyID,
            )
        response_data = {
            "StatusCode" : 6000,
            "message" : "Stock Posting Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Stock Posting Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)