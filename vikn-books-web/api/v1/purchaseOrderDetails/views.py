from brands.models import PurchaseOrderDetails, PurchaseOrderDetails_Log, PurchaseOrderDetailsDummy
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v1.purchaseOrderDetails.serializers import PurchaseOrderDetailsSerializer, PurchaseOrderDetailsRestSerializer, PurchaseOrderDetailsDummySerializer
from api.v1.brands.serializers import ListSerializer
from api.v1.purchaseOrderDetails.functions import generate_serializer_errors
from rest_framework import status
from api.v1.purchaseOrderDetails.functions import get_auto_id
import datetime



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_purchaseOrderDetails(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = PurchaseOrderDetailsSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        PurchaseOrderMasterID = serialized.data['PurchaseOrderMasterID']
        DeliveryDetailsID = serialized.data['DeliveryDetailsID']
        OrederDetailsID = serialized.data['OrederDetailsID']
        ProductID = serialized.data['ProductID']
        Qty = serialized.data['Qty']
        FreeQty = serialized.data['FreeQty']
        UnitPrice = serialized.data['UnitPrice']
        RateWithTax = serialized.data['RateWithTax']
        CostPerPrice = serialized.data['CostPerPrice']
        PriceListID = serialized.data['PriceListID']
        TaxID = serialized.data['TaxID']
        TaxType = serialized.data['TaxType']
        DiscountPerc = serialized.data['DiscountPerc']
        DiscountAmount = serialized.data['DiscountAmount']
        GrossAmount = serialized.data['GrossAmount']
        TaxableAmount = serialized.data['TaxableAmount']
        VATPerc = serialized.data['VATPerc']
        VATAmount = serialized.data['VATAmount']
        SGSTPerc = serialized.data['SGSTPerc']
        SGSTAmount = serialized.data['SGSTAmount']
        CGSTPerc = serialized.data['CGSTPerc']
        CGSTAmount = serialized.data['CGSTAmount']
        IGSTPerc = serialized.data['IGSTPerc']
        IGSTAmount = serialized.data['IGSTAmount']
        NetAmount = serialized.data['NetAmount']
        
        Action = "A"

        PurchaseOrderDetailsID = get_auto_id(PurchaseOrderDetails,BranchID,DataBase)

        PurchaseOrderDetails.objects.create(
            PurchaseOrderDetailsID=PurchaseOrderDetailsID,
            BranchID=BranchID,
            PurchaseOrderMasterID=PurchaseOrderMasterID,
            DeliveryDetailsID=DeliveryDetailsID,
            OrederDetailsID=OrederDetailsID,
            ProductID=ProductID,
            Qty=Qty,
            FreeQty=FreeQty,
            UnitPrice=UnitPrice,
            RateWithTax=RateWithTax,
            CostPerPrice=CostPerPrice,
            PriceListID=PriceListID,
            TaxID=TaxID,
            TaxType=TaxType,
            DiscountPerc=DiscountPerc,
            DiscountAmount=DiscountAmount,
            GrossAmount=GrossAmount,
            TaxableAmount=TaxableAmount,
            VATPerc=VATPerc,
            VATAmount=VATAmount,
            SGSTPerc=SGSTPerc,
            SGSTAmount=SGSTAmount,
            CGSTPerc=CGSTPerc,
            CGSTAmount=CGSTAmount,
            IGSTPerc=IGSTPerc,
            IGSTAmount=IGSTAmount,
            NetAmount=NetAmount,
            Action=Action,
            )

        PurchaseOrderDetails_Log.objects.create(
            TransactionID=PurchaseOrderDetailsID,
            BranchID=BranchID,
            PurchaseOrderMasterID=PurchaseOrderMasterID,
            DeliveryDetailsID=DeliveryDetailsID,
            OrederDetailsID=OrederDetailsID,
            ProductID=ProductID,
            Qty=Qty,
            FreeQty=FreeQty,
            UnitPrice=UnitPrice,
            RateWithTax=RateWithTax,
            CostPerPrice=CostPerPrice,
            PriceListID=PriceListID,
            TaxID=TaxID,
            TaxType=TaxType,
            DiscountPerc=DiscountPerc,
            DiscountAmount=DiscountAmount,
            GrossAmount=GrossAmount,
            TaxableAmount=TaxableAmount,
            VATPerc=VATPerc,
            VATAmount=VATAmount,
            SGSTPerc=SGSTPerc,
            SGSTAmount=SGSTAmount,
            CGSTPerc=CGSTPerc,
            CGSTAmount=CGSTAmount,
            IGSTPerc=IGSTPerc,
            IGSTAmount=IGSTAmount,
            NetAmount=NetAmount,
            Action=Action,
            )

        data = {"PurchaseOrderDetailsID" : PurchaseOrderDetailsID}
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
def edit_purchaseOrderDetails(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    serialized = PurchaseOrderDetailsSerializer(data=request.data)
    instance = None
    if PurchaseOrderDetails.objects.filter(pk=pk).exists():
        instance = PurchaseOrderDetails.objects.get(pk=pk)

        PurchaseOrderDetailsID = instance.PurchaseOrderDetailsID
        BranchID = instance.BranchID
        
    if instance:
        if serialized.is_valid():
            PurchaseOrderMasterID = serialized.data['PurchaseOrderMasterID']
            DeliveryDetailsID = serialized.data['DeliveryDetailsID']
            OrederDetailsID = serialized.data['OrederDetailsID']
            ProductID = serialized.data['ProductID']
            Qty = serialized.data['Qty']
            FreeQty = serialized.data['FreeQty']
            UnitPrice = serialized.data['UnitPrice']
            RateWithTax = serialized.data['RateWithTax']
            CostPerPrice = serialized.data['CostPerPrice']
            PriceListID = serialized.data['PriceListID']
            TaxID = serialized.data['TaxID']
            TaxType = serialized.data['TaxType']
            DiscountPerc = serialized.data['DiscountPerc']
            DiscountAmount = serialized.data['DiscountAmount']
            GrossAmount = serialized.data['GrossAmount']
            TaxableAmount = serialized.data['TaxableAmount']
            VATPerc = serialized.data['VATPerc']
            VATAmount = serialized.data['VATAmount']
            SGSTPerc = serialized.data['SGSTPerc']
            SGSTAmount = serialized.data['SGSTAmount']
            CGSTPerc = serialized.data['CGSTPerc']
            CGSTAmount = serialized.data['CGSTAmount']
            IGSTPerc = serialized.data['IGSTPerc']
            IGSTAmount = serialized.data['IGSTAmount']
            NetAmount = serialized.data['NetAmount']

            Action = "M"


            instance.PurchaseOrderMasterID = PurchaseOrderMasterID
            instance.DeliveryDetailsID = DeliveryDetailsID
            instance.OrederDetailsID = OrederDetailsID
            instance.ProductID = ProductID
            instance.Qty = Qty
            instance.FreeQty = FreeQty
            instance.UnitPrice = UnitPrice
            instance.RateWithTax = RateWithTax
            instance.CostPerPrice = CostPerPrice
            instance.PriceListID = PriceListID
            instance.TaxID = TaxID
            instance.TaxType = TaxType
            instance.DiscountPerc = DiscountPerc
            instance.DiscountAmount = DiscountAmount
            instance.GrossAmount = GrossAmount
            instance.TaxableAmount = TaxableAmount
            instance.VATPerc = VATPerc
            instance.VATAmount = VATAmount
            instance.SGSTPerc = SGSTPerc
            instance.SGSTAmount = SGSTAmount
            instance.CGSTPerc = CGSTPerc
            instance.CGSTAmount = CGSTAmount
            instance.IGSTPerc = IGSTPerc
            instance.IGSTAmount = IGSTAmount
            instance.NetAmount = NetAmount
            instance.Action = Action
            instance.save()

            PurchaseOrderDetails_Log.objects.create(
                TransactionID=PurchaseOrderDetailsID,
                BranchID=BranchID,
                PurchaseOrderMasterID=PurchaseOrderMasterID,
                DeliveryDetailsID=DeliveryDetailsID,
                OrederDetailsID=OrederDetailsID,
                ProductID=ProductID,
                Qty=Qty,
                FreeQty=FreeQty,
                UnitPrice=UnitPrice,
                RateWithTax=RateWithTax,
                CostPerPrice=CostPerPrice,
                PriceListID=PriceListID,
                TaxID=TaxID,
                TaxType=TaxType,
                DiscountPerc=DiscountPerc,
                DiscountAmount=DiscountAmount,
                GrossAmount=GrossAmount,
                TaxableAmount=TaxableAmount,
                VATPerc=VATPerc,
                VATAmount=VATAmount,
                SGSTPerc=SGSTPerc,
                SGSTAmount=SGSTAmount,
                CGSTPerc=CGSTPerc,
                CGSTAmount=CGSTAmount,
                IGSTPerc=IGSTPerc,
                IGSTAmount=IGSTAmount,
                NetAmount=NetAmount,
                Action=Action,
                )

            data = {"PurchaseOrderDetailsID" : PurchaseOrderDetailsID}
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
            "message" : "Purchase Order Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_purchaseOrderDetails(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']
        
        if PurchaseOrderDetails.objects.filter(BranchID=BranchID).exists():

            instances = PurchaseOrderDetails.objects.filter(BranchID=BranchID)

            serialized = PurchaseOrderDetailsRestSerializer(instances,many=True)

            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
            "StatusCode" : 6001,
            "message" : "Purchase Order Details Not Found in this BranchID!"
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
def purchaseOrderDetails(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    instance = None
    if PurchaseOrderDetails.objects.filter(pk=pk).exists():
        instance = PurchaseOrderDetails.objects.get(pk=pk)
    if instance:
        serialized = PurchaseOrderDetailsRestSerializer(instance)
        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Purchase Order Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_purchaseOrderDetails(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    instance = None
    if PurchaseOrderDetails.objects.filter(pk=pk).exists():
        instance = PurchaseOrderDetails.objects.get(pk=pk)
    if instance:

        PurchaseOrderDetailsID = instance.PurchaseOrderDetailsID
        BranchID = instance.BranchID
        PurchaseOrderMasterID = instance.PurchaseOrderMasterID
        DeliveryDetailsID = instance.DeliveryDetailsID
        OrederDetailsID = instance.OrederDetailsID
        ProductID = instance.ProductID
        Qty = instance.Qty
        FreeQty = instance.FreeQty
        UnitPrice = instance.UnitPrice
        RateWithTax = instance.RateWithTax
        CostPerPrice = instance.CostPerPrice
        PriceListID = instance.PriceListID
        TaxID = instance.TaxID
        TaxType = instance.TaxType
        DiscountPerc = instance.DiscountPerc
        DiscountAmount = instance.DiscountAmount
        GrossAmount = instance.GrossAmount
        TaxableAmount = instance.TaxableAmount
        VATPerc = instance.VATPerc
        VATAmount = instance.VATAmount
        SGSTPerc = instance.SGSTPerc
        SGSTAmount = instance.SGSTAmount
        CGSTPerc = instance.CGSTPerc
        CGSTAmount = instance.CGSTAmount
        IGSTPerc = instance.IGSTPerc
        IGSTAmount = instance.IGSTAmount
        NetAmount = instance.NetAmount
        Action = "D"

        instance.delete()

        PurchaseOrderDetails_Log.objects.create(
            TransactionID=PurchaseOrderDetailsID,
            BranchID=BranchID,
            PurchaseOrderMasterID=PurchaseOrderMasterID,
            DeliveryDetailsID=DeliveryDetailsID,
            OrederDetailsID=OrederDetailsID,
            ProductID=ProductID,
            Qty=Qty,
            FreeQty=FreeQty,
            UnitPrice=UnitPrice,
            RateWithTax=RateWithTax,
            CostPerPrice=CostPerPrice,
            PriceListID=PriceListID,
            TaxID=TaxID,
            TaxType=TaxType,
            DiscountPerc=DiscountPerc,
            DiscountAmount=DiscountAmount,
            GrossAmount=GrossAmount,
            TaxableAmount=TaxableAmount,
            VATPerc=VATPerc,
            VATAmount=VATAmount,
            SGSTPerc=SGSTPerc,
            SGSTAmount=SGSTAmount,
            CGSTPerc=CGSTPerc,
            CGSTAmount=CGSTAmount,
            IGSTPerc=IGSTPerc,
            IGSTAmount=IGSTAmount,
            NetAmount=NetAmount,
            Action=Action,
            )
        response_data = {
            "StatusCode" : 6000,
            "message" : "Purchase Order Details Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Purchase Order Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_purchaseOrderDetailsDummy(request):

    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    BranchID = data['BranchID']
    PurchaseOrderMasterID = data['PurchaseOrderMasterID']
    DeliveryDetailsID = data['DeliveryDetailsID']
    OrderDetailsID = data['OrderDetailsID']
    ProductID = data['ProductID']
    Qty = data['Qty']
    FreeQty = data['FreeQty']
    UnitPrice = data['UnitPrice']
    RateWithTax = data['RateWithTax']
    CostPerPrice = data['CostPerPrice']
    PriceListID = data['PriceListID']
    TaxID = data['TaxID']
    TaxType = data['TaxType']
    DiscountPerc = data['DiscountPerc']
    DiscountAmount = data['DiscountAmount']
    GrossAmount = data['GrossAmount']
    TaxableAmount = data['TaxableAmount']
    VATPerc = data['VATPerc']
    VATAmount = data['VATAmount']
    SGSTPerc = data['SGSTPerc']
    SGSTAmount = data['SGSTAmount']
    CGSTPerc = data['CGSTPerc']
    CGSTAmount = data['CGSTAmount']
    IGSTPerc = data['IGSTPerc']
    IGSTAmount = data['IGSTAmount']
    NetAmount = data['NetAmount']
    BatchID = data['BatchID']
    detailID = 0


    PurchaseOrderDetailsDummy.objects.create(
        BranchID=BranchID,
        BatchID=BatchID,
        PurchaseOrderMasterID=PurchaseOrderMasterID,
        DeliveryDetailsID=DeliveryDetailsID,
        OrderDetailsID=OrderDetailsID,
        ProductID=ProductID,
        Qty=Qty,
        FreeQty=FreeQty,
        UnitPrice=UnitPrice,
        RateWithTax=RateWithTax,
        CostPerPrice=CostPerPrice,
        PriceListID=PriceListID,
        TaxID=TaxID,
        TaxType=TaxType,
        DiscountPerc=DiscountPerc,
        DiscountAmount=DiscountAmount,
        GrossAmount=GrossAmount,
        TaxableAmount=TaxableAmount,
        VATPerc=VATPerc,
        VATAmount=VATAmount,
        SGSTPerc=SGSTPerc,
        SGSTAmount=SGSTAmount,
        CGSTPerc=CGSTPerc,
        CGSTAmount=CGSTAmount,
        IGSTPerc=IGSTPerc,
        IGSTAmount=IGSTAmount,
        NetAmount=NetAmount,
        detailID=detailID,
        )

    response_data = {
        "StatusCode" : 6000,
        "message" : "success!!!"
    }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_DummyforEditPurchaseOrder(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    dummydetails = data["DummyDetails"]
    BranchID = data["BranchID"]

    dummies = PurchaseOrderDetailsDummy.objects.filter(BranchID=BranchID)

    for dummy in dummies:
        dummy.delete()

    for dummydetail in dummydetails:

        BranchID = dummydetail['BranchID']
        PurchaseOrderMasterID = dummydetail['PurchaseOrderMasterID']
        DeliveryDetailsID = dummydetail['DeliveryDetailsID']
        OrderDetailsID = dummydetail['OrderDetailsID']
        ProductID = dummydetail['ProductID']
        Qty = dummydetail['Qty']
        FreeQty = dummydetail['FreeQty']
        UnitPrice = dummydetail['UnitPrice']
        RateWithTax = dummydetail['RateWithTax']
        CostPerPrice = dummydetail['CostPerPrice']
        PriceListID = dummydetail['PriceListID']
        TaxID = dummydetail['TaxID']
        TaxType = dummydetail['TaxType']
        DiscountPerc = dummydetail['DiscountPerc']
        DiscountAmount = dummydetail['DiscountAmount']
        GrossAmount = dummydetail['GrossAmount']
        TaxableAmount = dummydetail['TaxableAmount']
        VATPerc = dummydetail['VATPerc']
        VATAmount = dummydetail['VATAmount']
        SGSTPerc = dummydetail['SGSTPerc']
        SGSTAmount = dummydetail['SGSTAmount']
        CGSTPerc = dummydetail['CGSTPerc']
        CGSTAmount = dummydetail['CGSTAmount']
        IGSTPerc = dummydetail['IGSTPerc']
        IGSTAmount = dummydetail['IGSTAmount']
        NetAmount = dummydetail['NetAmount']
        BatchID = dummydetail['BatchID']
        detailID = 0



        PurchaseOrderDetailsDummy.objects.create(
            BranchID=BranchID,
            BatchID=BatchID,
            PurchaseOrderMasterID=PurchaseOrderMasterID,
            DeliveryDetailsID=DeliveryDetailsID,
            OrderDetailsID=OrderDetailsID,
            ProductID=ProductID,
            Qty=Qty,
            FreeQty=FreeQty,
            UnitPrice=UnitPrice,
            RateWithTax=RateWithTax,
            CostPerPrice=CostPerPrice,
            PriceListID=PriceListID,
            TaxID=TaxID,
            TaxType=TaxType,
            DiscountPerc=DiscountPerc,
            DiscountAmount=DiscountAmount,
            GrossAmount=GrossAmount,
            TaxableAmount=TaxableAmount,
            VATPerc=VATPerc,
            VATAmount=VATAmount,
            SGSTPerc=SGSTPerc,
            SGSTAmount=SGSTAmount,
            CGSTPerc=CGSTPerc,
            CGSTAmount=CGSTAmount,
            IGSTPerc=IGSTPerc,
            IGSTAmount=IGSTAmount,
            NetAmount=NetAmount,
            detailID=detailID,
            )

    response_data = {
        "StatusCode" : 6000,
        "message" : "success!!!"
    }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_purchaseOrderDetailsDummy(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if PurchaseOrderDetailsDummy.objects.filter(BranchID=BranchID).exists():
            net_amount = 0
            gross_amount = 0
            vat_amount = 0
            discount_amount = 0

            instances = PurchaseOrderDetailsDummy.objects.filter(BranchID=BranchID)

            for instance in instances:

                net_amount += instance.NetAmount

                gross_amount += instance.GrossAmount

                vat_amount += instance.VATAmount

                discount_amount += instance.DiscountAmount

                

            serialized = PurchaseOrderDetailsDummySerializer(instances,many=True,context = {"DataBase": DataBase })

            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data,
                "TotalNetAmount" : net_amount,
                "TotalGrossAmount" : gross_amount,
                "TotalVatAmount" : vat_amount,
                "TotalDiscountAmount" : discount_amount,
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
def edit_purchaseOrderDetailsDummy(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    if PurchaseOrderDetailsDummy.objects.filter(pk=pk).exists():

        instance = PurchaseOrderDetailsDummy.objects.get(pk=pk)

        BranchID = data['BranchID']
        PurchaseOrderMasterID = data['PurchaseOrderMasterID']
        DeliveryDetailsID = data['DeliveryDetailsID']
        OrderDetailsID = data['OrderDetailsID']
        ProductID = data['ProductID']
        Qty = data['Qty']
        FreeQty = data['FreeQty']
        UnitPrice = data['UnitPrice']
        RateWithTax = data['RateWithTax']
        CostPerPrice = data['CostPerPrice']
        PriceListID = data['PriceListID']
        TaxID = data['TaxID']
        TaxType = data['TaxType']
        DiscountPerc = data['DiscountPerc']
        DiscountAmount = data['DiscountAmount']
        GrossAmount = data['GrossAmount']
        TaxableAmount = data['TaxableAmount']
        VATPerc = data['VATPerc']
        VATAmount = data['VATAmount']
        SGSTPerc = data['SGSTPerc']
        SGSTAmount = data['SGSTAmount']
        CGSTPerc = data['CGSTPerc']
        CGSTAmount = data['CGSTAmount']
        IGSTPerc = data['IGSTPerc']
        IGSTAmount = data['IGSTAmount']
        NetAmount = data['NetAmount']
        BatchID = data['BatchID']
        detailID = data['detailID']

        instance.BranchID = BranchID
        instance.PurchaseOrderMasterID = PurchaseOrderMasterID
        instance.DeliveryDetailsID = DeliveryDetailsID
        instance.OrderDetailsID = OrderDetailsID
        instance.ProductID = ProductID
        instance.Qty = Qty
        instance.FreeQty = FreeQty
        instance.UnitPrice = UnitPrice
        instance.RateWithTax = RateWithTax
        instance.CostPerPrice = CostPerPrice
        instance.PriceListID = PriceListID
        instance.TaxID = TaxID
        instance.TaxType = TaxType
        instance.DiscountPerc = DiscountPerc
        instance.DiscountAmount = DiscountAmount
        instance.GrossAmount = GrossAmount
        instance.TaxableAmount = TaxableAmount
        instance.VATPerc = VATPerc
        instance.VATAmount = VATAmount
        instance.SGSTPerc = SGSTPerc
        instance.SGSTAmount = SGSTAmount
        instance.CGSTPerc = CGSTPerc
        instance.CGSTAmount = CGSTAmount
        instance.IGSTPerc = IGSTPerc
        instance.IGSTAmount = IGSTAmount
        instance.NetAmount = NetAmount
        instance.BatchID = BatchID
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
def delete_purchaseOrderDetailsDummy(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']
    instance = None
    if PurchaseOrderDetailsDummy.objects.filter(pk=pk).exists():
        instance = PurchaseOrderDetailsDummy.objects.get(pk=pk)
    if instance:

        instance.delete()

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