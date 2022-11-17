from brands.models import StockReceiptMaster_ID, StockReceiptMasterID_Log, StockReceiptDetails, StockReceiptDetails_Log, StockReceiptDetailsDummy
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v1.stockReceipts.serializers import StockReceiptMaster_IDSerializer, StockReceiptMaster_IDRestSerializer, StockReceiptDetailsSerializer, StockReceiptDetailsRestSerializer
from api.v1.brands.serializers import ListSerializer
from api.v1.stockReceipts.functions import generate_serializer_errors
from rest_framework import status
from api.v1.stockReceipts.functions import get_auto_id, get_auto_idMaster
import datetime



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_stockReceipt(request):
    today = datetime.datetime.now()

    data = request.data

    BranchID = data['BranchID']
    VoucherNo = data['VoucherNo']
    InvoiceNo = data['InvoiceNo']
    Date = data['Date']
    Notes = data['Notes']
    WarehouseFromID = data['WarehouseFromID']
    WarehouseToID = data['WarehouseToID']
    IsActive = data['IsActive']
    CreatedUserID = data['CreatedUserID']

    Action = "A"

    StockReceiptMasterID = get_auto_idMaster(StockReceiptMaster_ID,BranchID)

    StockReceiptMaster_ID.objects.create(
        StockReceiptMasterID=StockReceiptMasterID,
        BranchID=BranchID,
        VoucherNo=VoucherNo,
        InvoiceNo=InvoiceNo,
        Date=Date,
        Notes=Notes,
        WarehouseFromID=WarehouseFromID,
        WarehouseToID=WarehouseToID,
        IsActive=IsActive,
        Action=Action,
        CreatedUserID=CreatedUserID,
        CreatedDate=today,
        )

    StockReceiptMasterID_Log.objects.create(
        TransactionID=StockReceiptMasterID,
        BranchID=BranchID,
        VoucherNo=VoucherNo,
        InvoiceNo=InvoiceNo,
        Date=Date,
        Notes=Notes,
        WarehouseFromID=WarehouseFromID,
        WarehouseToID=WarehouseToID,
        IsActive=IsActive,
        Action=Action,
        CreatedUserID=CreatedUserID,
        CreatedDate=today,
        )


    stockReceiptDetails = data["StockReceiptDetails"]

    for stockReceiptDetail in stockReceiptDetails:

        # StockReceiptMasterID = serialized.data['StockReceiptMasterID']
        ProductID = stockReceiptDetail['ProductID']
        Qty = stockReceiptDetail['Qty']
        PriceListID = stockReceiptDetail['PriceListID']
        Rate = stockReceiptDetail['Rate']
        Amount = stockReceiptDetail['Amount']

        StockReceiptDetailsID = get_auto_id(StockReceiptDetails,BranchID)

        
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

    response_data = {
        "StatusCode" : 6000,
        "message" : "Stock Receipt created Successfully!!!",
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def edit_stockReceipt(request,pk):
    today = datetime.datetime.now()

    stockReceiptMaster_instance = None

    stockReceiptDetails = None

    stockReceiptMaster_instance = StockReceiptMaster_ID.objects.get(pk=pk)

    StockReceiptMasterID = stockReceiptMaster_instance.StockReceiptMasterID
    BranchID = stockReceiptMaster_instance.BranchID
    CreatedUserID = stockReceiptMaster_instance.CreatedUserID


    data = request.data

    VoucherNo = data['VoucherNo']
    InvoiceNo = data['InvoiceNo']
    Date = data['Date']
    Notes = data['Notes']
    WarehouseFromID = data['WarehouseFromID']
    WarehouseToID = data['WarehouseToID']
    IsActive = data['IsActive']

    Action = 'M'

    stockReceiptMaster_instance.VoucherNo = VoucherNo
    stockReceiptMaster_instance.InvoiceNo = InvoiceNo
    stockReceiptMaster_instance.Date = Date
    stockReceiptMaster_instance.Notes = Notes
    stockReceiptMaster_instance.WarehouseFromID = WarehouseFromID
    stockReceiptMaster_instance.WarehouseToID = WarehouseToID
    stockReceiptMaster_instance.IsActive = IsActive
    stockReceiptMaster_instance.Action = Action

    stockReceiptMaster_instance.save()


    StockReceiptMasterID_Log.objects.create(
        TransactionID=StockReceiptMasterID,
        BranchID=BranchID,
        VoucherNo=VoucherNo,
        InvoiceNo=InvoiceNo,
        Date=Date,
        Notes=Notes,
        WarehouseFromID=WarehouseFromID,
        WarehouseToID=WarehouseToID,
        IsActive=IsActive,
        Action=Action,
        CreatedUserID=CreatedUserID,
        CreatedDate=today,
        )


    stockReceiptDetails = data["StockReceiptDetails"]

    for stockReceiptDetail in stockReceiptDetails:
        # BranchID = stockReceiptDetail["BranchID"]
        # DamageStockMasterID = stockReceiptDetail["DamageStockMasterID"]
        pk = stockReceiptDetail["id"]

        ProductID = stockReceiptDetail['ProductID']
        Qty = stockReceiptDetail['Qty']
        PriceListID = stockReceiptDetail['PriceListID']
        Rate = stockReceiptDetail['Rate']
        Amount = stockReceiptDetail['Amount']


        stockReceiptDetails = StockReceiptDetails.objects.get(pk=pk,StockReceiptMasterID=StockReceiptMasterID,BranchID=BranchID)


        StockReceiptDetailsID = stockReceiptDetails.StockReceiptDetailsID

        stockReceiptDetails.ProductID = ProductID
        stockReceiptDetails.Qty = Qty
        stockReceiptDetails.PriceListID = PriceListID
        stockReceiptDetails.Rate = Rate
        stockReceiptDetails.Amount = Amount
        stockReceiptDetails.Action = Action

        stockReceiptDetails.save()


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
        "StatusCode" : 6000,
        "message" : "Stock Receipt Updated Successfully!!!",
    }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_stockReceiptMasterID(request):
    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if StockReceiptMaster_ID.objects.filter(BranchID=BranchID).exists():

            instances = StockReceiptMaster_ID.objects.filter(BranchID=BranchID)

            serialized = StockReceiptMaster_IDRestSerializer(instances,many=True)

            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
            "StatusCode" : 6001,
            "message" : "Stock Receipt Master_ID Not Found in this BranchID!"
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
def stockReceiptMasterID(request,pk):
    instance = None
    if StockReceiptMaster_ID.objects.filter(pk=pk).exists():
        instance = StockReceiptMaster_ID.objects.get(pk=pk)
    if instance:
        serialized = StockReceiptMaster_IDRestSerializer(instance)
        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Stock Receipt Master ID Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_stockReceiptDetails(request,pk):
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
            "StatusCode" : 6000,
            "message" : "Stock Receipt Details Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Stock Receipt Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_stockReceiptMasterID(request,pk):
    today = datetime.datetime.now()
    instance = None
    if StockReceiptMaster_ID.objects.filter(pk=pk).exists():
        instance = StockReceiptMaster_ID.objects.get(pk=pk)
    if instance:
        StockReceiptMasterID = instance.StockReceiptMasterID
        BranchID = instance.BranchID
        VoucherNo = instance.VoucherNo
        InvoiceNo = instance.InvoiceNo
        Date = instance.Date
        Notes = instance.Notes
        WarehouseFromID = instance.WarehouseFromID
        WarehouseToID = instance.WarehouseToID
        IsActive = instance.IsActive
        CreatedUserID = instance.CreatedUserID
        Action = "D"

        instance.delete()

        detail_instances = StockReceiptDetails.objects.filter(StockReceiptMasterID=StockReceiptMasterID,BranchID=BranchID)

        for detail_instance in detail_instances:

            StockReceiptDetailsID = detail_instance.StockReceiptDetailsID
            BranchID = detail_instance.BranchID
            StockReceiptMasterID = detail_instance.StockReceiptMasterID
            ProductID = detail_instance.ProductID
            Qty = detail_instance.Qty
            PriceListID = detail_instance.PriceListID
            Rate = detail_instance.Rate
            Amount = detail_instance.Amount

            detail_instance.delete()

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

        StockReceiptMasterID_Log.objects.create(
            TransactionID=StockReceiptMasterID,
            BranchID=BranchID,
            VoucherNo=VoucherNo,
            InvoiceNo=InvoiceNo,
            Date=Date,
            Notes=Notes,
            WarehouseFromID=WarehouseFromID,
            WarehouseToID=WarehouseToID,
            IsActive=IsActive,
            Action=Action,
            CreatedUserID=CreatedUserID,
            CreatedDate=today,
            )

        response_data = {
            "StatusCode" : 6000,
            "message" : "Stock Receipt Master ID Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Stock Receipt Master ID Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)