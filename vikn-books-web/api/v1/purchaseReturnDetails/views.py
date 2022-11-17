from brands.models import PurchaseReturnDetails, PurchaseReturnDetails_Log, PurchaseReturnDetailsDummy
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v1.purchaseReturnDetails.serializers import PurchaseReturnDetailsSerializer, PurchaseReturnDetailsRestSerializer, PurchaseReturnDetailsDummySerializer, PurchaseReturnDetailsDeletedDummySerializer
from api.v1.brands.serializers import ListSerializer
from api.v1.purchaseReturnDetails.functions import generate_serializer_errors
from rest_framework import status
from api.v1.purchaseReturnDetails.functions import get_auto_id
import datetime



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_purchaseReturnDetails(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = PurchaseReturnDetailsSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        PurchaseReturnMasterID = serialized.data['PurchaseReturnMasterID']
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

        PurchaseReturnDetailsID = get_auto_id(PurchaseReturnDetails,BranchID,DataBase)

        PurchaseReturnDetails.objects.create(
            PurchaseReturnDetailsID=PurchaseReturnDetailsID,
            BranchID=BranchID,
            PurchaseReturnMasterID=PurchaseReturnMasterID,
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

        PurchaseReturnDetails_Log.objects.create(
            TransactionID=PurchaseReturnDetailsID,
            BranchID=BranchID,
            PurchaseReturnMasterID=PurchaseReturnMasterID,
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

        data = {"PurchaseReturnDetailsID" : PurchaseReturnDetailsID}
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
def edit_purchaseReturnDetails(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    serialized = PurchaseReturnDetailsSerializer(data=request.data)
    instance = None
    if PurchaseReturnDetails.objects.filter(pk=pk).exists():
        instance = PurchaseReturnDetails.objects.get(pk=pk)

        PurchaseReturnDetailsID = instance.PurchaseReturnDetailsID
        BranchID = instance.BranchID
        
        if serialized.is_valid():
            PurchaseReturnMasterID = serialized.data['PurchaseReturnMasterID']
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


            instance.PurchaseReturnMasterID = PurchaseReturnMasterID
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

            PurchaseReturnDetails_Log.objects.create(
                TransactionID=PurchaseReturnDetailsID,
                BranchID=BranchID,
                PurchaseReturnMasterID=PurchaseReturnMasterID,
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
            data = {"PurchaseReturnDetailsID" : PurchaseReturnDetailsID}
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
            "message" : "Purchase Return Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_purchaseReturnDetails(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']
    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if PurchaseReturnDetails.objects.filter(BranchID=BranchID).exists():

            instances = PurchaseReturnDetails.objects.filter(BranchID=BranchID)

            serialized = PurchaseReturnDetailsRestSerializer(instances,many=True)

            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
            "StatusCode" : 6001,
            "message" : "Purchase Return Details Not Found in this BranchID!"
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
def purchaseReturnDetails(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    if PurchaseReturnDetails.objects.filter(pk=pk).exists():
        instance = PurchaseReturnDetails.objects.get(pk=pk)
        serialized = PurchaseReturnDetailsRestSerializer(instance)
        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Purchase Return Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_purchaseReturnDetails(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    if PurchaseReturnDetails.objects.filter(pk=pk).exists():
        instance = PurchaseReturnDetails.objects.get(pk=pk)

        PurchaseReturnDetailsID = instance.PurchaseReturnDetailsID
        BranchID = instance.BranchID
        PurchaseReturnMasterID = instance.PurchaseReturnMasterID
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

        PurchaseReturnDetails_Log.objects.create(
            TransactionID=PurchaseReturnDetailsID,
            BranchID=BranchID,
            PurchaseReturnMasterID=PurchaseReturnMasterID,
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
            "message" : "Purchase Return Details Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Purchase Return Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_purchasesReturnDetailsDummy(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    PurchaseReturnDetailsID = data['PurchaseReturnDetailsID']
    BranchID = data['BranchID']
    PurchaseReturnMasterID = data['PurchaseReturnMasterID']
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
    detailID = data['detailID']

    AddlDiscPerc = data['AddlDiscPerc']
    AddlDiscAmt = data['AddlDiscAmt']
    TAX1Perc = data['TAX1Perc']
    TAX1Amount = data['TAX1Amount']
    TAX2Perc = data['TAX2Perc']
    TAX2Amount = data['TAX2Amount']
    TAX3Perc = data['TAX3Perc']
    TAX3Amount = data['TAX3Amount']


    PurchaseReturnDetailsDummy.objects.create(
        PurchaseReturnDetailsID=PurchaseReturnDetailsID,
        BranchID=BranchID,
        PurchaseReturnMasterID=PurchaseReturnMasterID,
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
        CreatedUserID=CreatedUserID,
        detailID=detailID,
        AddlDiscPerc=AddlDiscPerc,
        AddlDiscAmt=AddlDiscAmt,
        TAX1Perc=TAX1Perc,
        TAX1Amount=TAX1Amount,
        TAX2Perc=TAX2Perc,
        TAX2Amount=TAX2Amount,
        TAX3Perc=TAX3Perc,
        TAX3Amount=TAX3Amount,
        )

    response_data = {
        "StatusCode" : 6000,
        "message" : "success!!!"
    }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_DummyforEditPurchaseReturn(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    dummydetails = data["DummyDetails"]
    BranchID = data["BranchID"]

    dummies = PurchaseReturnDetailsDummy.objects.filter(BranchID=BranchID)

    for dummy in dummies:
        dummy.delete()

    for dummydetail in dummydetails:
        unq_id = dummydetail['id']
        PurchaseReturnDetailsID = dummydetail['PurchaseReturnDetailsID']
        BranchID = dummydetail['BranchID']
        PurchaseReturnMasterID = dummydetail['PurchaseReturnMasterID']
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

        AddlDiscPerc = dummydetail['AddlDiscPerc']
        AddlDiscAmt = dummydetail['AddlDiscAmt']
        TAX1Perc = dummydetail['TAX1Perc']
        TAX1Amount = dummydetail['TAX1Amount']
        TAX2Perc = dummydetail['TAX2Perc']
        TAX2Amount = dummydetail['TAX2Amount']
        TAX3Perc = dummydetail['TAX3Perc']
        TAX3Amount = dummydetail['TAX3Amount']
        detailID = 0

        PurchaseReturnDetailsDummy.objects.create(
            unq_id=unq_id,
            PurchaseReturnDetailsID=PurchaseReturnDetailsID,
            BranchID=BranchID,
            PurchaseReturnMasterID=PurchaseReturnMasterID,
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
            CreatedUserID=CreatedUserID,
            detailID=detailID,
            AddlDiscPerc=AddlDiscPerc,
            AddlDiscAmt=AddlDiscAmt,
            TAX1Perc=TAX1Perc,
            TAX1Amount=TAX1Amount,
            TAX2Perc=TAX2Perc,
            TAX2Amount=TAX2Amount,
            TAX3Perc=TAX3Perc,
            TAX3Amount=TAX3Amount,
            )

    response_data = {
        "StatusCode" : 6000,
        "message" : "success!!!"
    }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_purchasesReturnDetailsDummy(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if PurchaseReturnDetailsDummy.objects.filter(BranchID=BranchID).exists():
            net_amount = 0
            gross_amount = 0
            vat_amount = 0
            discount_amount = 0

            instances = PurchaseReturnDetailsDummy.objects.filter(BranchID=BranchID,IsDeleted=False)
            deleted_instances = PurchaseReturnDetailsDummy.objects.filter(BranchID=BranchID,IsDeleted=True)
            
            for instance in instances:

                net_amount += instance.NetAmount

                gross_amount += instance.GrossAmount

                vat_amount += instance.VATAmount

                discount_amount += instance.DiscountAmount

                

            serialized = PurchaseReturnDetailsDummySerializer(instances,many=True,context = {"DataBase": DataBase })
            serializedDeleted = PurchaseReturnDetailsDeletedDummySerializer(deleted_instances,many=True)

            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data,
                "deleted_data" : serializedDeleted.data,
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
def edit_purchasesReturnDetailsDummy(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']
    if PurchaseReturnDetailsDummy.objects.filter(pk=pk).exists():
        instance = PurchaseReturnDetailsDummy.objects.get(pk=pk)

        PurchaseReturnDetailsID = data['PurchaseReturnDetailsID']
        BranchID = data['BranchID']
        PurchaseReturnMasterID = data['PurchaseReturnMasterID']
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
        detailID = data['detailID']

        AddlDiscPerc = data['AddlDiscPerc']
        AddlDiscAmt = data['AddlDiscAmt']
        TAX1Perc = data['TAX1Perc']
        TAX1Amount = data['TAX1Amount']
        TAX2Perc = data['TAX2Perc']
        TAX2Amount = data['TAX2Amount']
        TAX3Perc = data['TAX3Perc']
        TAX3Amount = data['TAX3Amount']


        instance.PurchaseReturnDetailsID = PurchaseReturnDetailsID
        instance.BranchID = BranchID
        instance.PurchaseReturnMasterID = PurchaseReturnMasterID
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
        instance.CreatedUserID = CreatedUserID
        instance.detailID = detailID
        instance.AddlDiscPerc = AddlDiscPerc
        instance.AddlDiscAmt = AddlDiscAmt
        instance.TAX1Perc = TAX1Perc
        instance.TAX1Amount = TAX1Amount
        instance.TAX2Perc = TAX2Perc
        instance.TAX2Amount = TAX2Amount
        instance.TAX3Perc = TAX3Perc
        instance.TAX3Amount = TAX3Amount
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
def delete_purchasesReturnDetailsDummy(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']
    if PurchaseReturnDetailsDummy.objects.filter(pk=pk).exists():
        instance = PurchaseReturnDetailsDummy.objects.get(pk=pk)
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
