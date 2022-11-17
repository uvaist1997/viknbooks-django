from brands.models import SalesReturnDetails, SalesReturnDetails_Log, SalesReturnDetailsDummy
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v1.salesReturnDetails.serializers import SalesReturnDetailsSerializer, SalesReturnDetailsRestSerializer, SalesReturnDetailsDummySerializer, SalesReturnDetailsDeletedDummySerializer
from api.v1.brands.serializers import ListSerializer
from api.v1.salesReturnDetails.functions import generate_serializer_errors
from rest_framework import status
from api.v1.salesReturnDetails.functions import get_auto_id
import datetime



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_salesReturnDetails(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = SalesReturnDetailsSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        SalesReturnMasterID = serialized.data['SalesReturnMasterID']
        DeliveryDetailsID = serialized.data['DeliveryDetailsID']
        OrederDetailsID = serialized.data['OrederDetailsID']
        ProductID = serialized.data['ProductID']
        Qty = serialized.data['Qty']
        FreeQty = serialized.data['FreeQty']
        UnitPrice = serialized.data['UnitPrice']
        RateWithTax = serialized.data['RateWithTax']
        CostPerPrice = serialized.data['CostPerPrice']
        PriceListID = serialized.data['PriceListID']
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
        Sauceoption = serialized.data['Sauceoption']
        
        Action = "A"

        SalesReturnDetailsID = get_auto_id(SalesReturnDetails,BranchID)

        SalesReturnDetails.objects.create(
            SalesReturnDetailsID=SalesReturnDetailsID,
            BranchID=BranchID,
            SalesReturnMasterID=SalesReturnMasterID,
            DeliveryDetailsID=DeliveryDetailsID,
            OrederDetailsID=OrederDetailsID,
            ProductID=ProductID,
            Qty=Qty,
            FreeQty=FreeQty,
            UnitPrice=UnitPrice,
            RateWithTax=RateWithTax,
            CostPerPrice=CostPerPrice,
            PriceListID=PriceListID,
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
            Sauceoption=Sauceoption,
            Action=Action,
            )

        SalesReturnDetails_Log.objects.create(
            TransactionID=SalesReturnDetailsID,
            BranchID=BranchID,
            SalesReturnMasterID=SalesReturnMasterID,
            DeliveryDetailsID=DeliveryDetailsID,
            OrederDetailsID=OrederDetailsID,
            ProductID=ProductID,
            Qty=Qty,
            FreeQty=FreeQty,
            UnitPrice=UnitPrice,
            RateWithTax=RateWithTax,
            CostPerPrice=CostPerPrice,
            PriceListID=PriceListID,
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
            Sauceoption=Sauceoption,
            Action=Action,
            )

        data = {"SalesReturnDetailsID" : SalesReturnDetailsID}
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
def edit_salesReturnDetails(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    serialized = SalesReturnDetailsSerializer(data=request.data)
    instance = None
    if SalesReturnDetails.objects.filter(pk=pk).exists():
        instance = SalesReturnDetails.objects.get(pk=pk)

        SalesReturnDetailsID = instance.SalesReturnDetailsID
        BranchID = instance.BranchID
        
        if serialized.is_valid():
            SalesReturnMasterID = serialized.data['SalesReturnMasterID']
            DeliveryDetailsID = serialized.data['DeliveryDetailsID']
            OrederDetailsID = serialized.data['OrederDetailsID']
            ProductID = serialized.data['ProductID']
            Qty = serialized.data['Qty']
            FreeQty = serialized.data['FreeQty']
            UnitPrice = serialized.data['UnitPrice']
            RateWithTax = serialized.data['RateWithTax']
            CostPerPrice = serialized.data['CostPerPrice']
            PriceListID = serialized.data['PriceListID']
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
            Sauceoption = serialized.data['Sauceoption']

            Action = "M"

            instance.SalesReturnMasterID = SalesReturnMasterID
            instance.DeliveryDetailsID = DeliveryDetailsID
            instance.OrederDetailsID = OrederDetailsID
            instance.ProductID = ProductID
            instance.Qty = Qty
            instance.FreeQty = FreeQty
            instance.UnitPrice = UnitPrice
            instance.RateWithTax = RateWithTax
            instance.CostPerPrice = CostPerPrice
            instance.PriceListID = PriceListID
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
            instance.Sauceoption = Sauceoption
            instance.Action = Action
            instance.save()

            SalesReturnDetails_Log.objects.create(
                TransactionID=SalesReturnDetailsID,
                BranchID=BranchID,
                SalesReturnMasterID=SalesReturnMasterID,
                DeliveryDetailsID=DeliveryDetailsID,
                OrederDetailsID=OrederDetailsID,
                ProductID=ProductID,
                Qty=Qty,
                FreeQty=FreeQty,
                UnitPrice=UnitPrice,
                RateWithTax=RateWithTax,
                CostPerPrice=CostPerPrice,
                PriceListID=PriceListID,
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
                Sauceoption=Sauceoption,
                Action=Action,
                )

            data = {"SalesReturnDetailsID" : SalesReturnDetailsID}
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
            "message" : "Sales Return Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_salesReturnDetails(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if SalesReturnDetails.objects.filter(BranchID=BranchID).exists():

            instances = SalesReturnDetails.objects.filter(BranchID=BranchID)

            serialized = SalesReturnDetailsRestSerializer(instances,many=True)

            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
            "StatusCode" : 6001,
            "message" : "Sales Return Details Not Found in this BranchID!"
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
def salesReturnDetails(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    instance = None
    if SalesReturnDetails.objects.filter(pk=pk).exists():
        instance = SalesReturnDetails.objects.get(pk=pk)
    if instance:
        serialized = SalesReturnDetailsRestSerializer(instance)
        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Sales Return Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_salesReturnDetails(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']
    instance = None
    if SalesReturnDetails.objects.filter(pk=pk).exists():
        instance = SalesReturnDetails.objects.get(pk=pk)

        SalesReturnDetailsID = instance.SalesReturnDetailsID
        BranchID = instance.BranchID
        SalesReturnMasterID = instance.SalesReturnMasterID
        DeliveryDetailsID = instance.DeliveryDetailsID
        OrederDetailsID = instance.OrederDetailsID
        ProductID = instance.ProductID
        Qty = instance.Qty
        FreeQty = instance.FreeQty
        UnitPrice = instance.UnitPrice
        RateWithTax = instance.RateWithTax
        CostPerPrice = instance.CostPerPrice
        PriceListID = instance.PriceListID
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
        Sauceoption = instance.Sauceoption
        Action = "D"

        instance.delete()

        SalesReturnDetails_Log.objects.create(
            TransactionID=SalesReturnDetailsID,
            BranchID=BranchID,
            SalesReturnMasterID=SalesReturnMasterID,
            DeliveryDetailsID=DeliveryDetailsID,
            OrederDetailsID=OrederDetailsID,
            ProductID=ProductID,
            Qty=Qty,
            FreeQty=FreeQty,
            UnitPrice=UnitPrice,
            RateWithTax=RateWithTax,
            CostPerPrice=CostPerPrice,
            PriceListID=PriceListID,
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
            Sauceoption=Sauceoption,
            Action=Action,
            )
        response_data = {
            "StatusCode" : 6000,
            "message" : "Sales Return Details Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Sales Return Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_salesReturnDetailsDummy(request):

    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    SalesReturnDetailsID = data['SalesReturnDetailsID']
    BranchID = data['BranchID']
    SalesReturnMasterID = data['SalesReturnMasterID']
    DeliveryDetailsID = data['DeliveryDetailsID']
    OrderDetailsID = data['OrderDetailsID']
    ProductID = data['ProductID']
    Qty = data['Qty']
    FreeQty = data['FreeQty']
    UnitPrice = data['UnitPrice']
    RateWithTax = data['RateWithTax']
    CostPerPrice = data['CostPerPrice']
    PriceListID = data['PriceListID']
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
    Flavour = data['Flavour']
    AddlDiscPercent = data['AddlDiscPercent']
    AddlDiscAmt = data['AddlDiscAmt']
    TAX1Perc = data['TAX1Perc']
    TAX1Amount = data['TAX1Amount']
    TAX2Perc = data['TAX2Perc']
    TAX2Amount = data['TAX2Amount']
    TAX3Perc = data['TAX3Perc']
    TAX3Amount = data['TAX3Amount']
    detailID = data['detailID']


    SalesReturnDetailsDummy.objects.create(
        SalesReturnDetailsID=SalesReturnDetailsID,
        BranchID=BranchID,
        SalesReturnMasterID=SalesReturnMasterID,
        DeliveryDetailsID=DeliveryDetailsID,
        OrderDetailsID=OrderDetailsID,
        ProductID=ProductID,
        Qty=Qty,
        FreeQty=FreeQty,
        UnitPrice=UnitPrice,
        RateWithTax=RateWithTax,
        CostPerPrice=CostPerPrice,
        PriceListID=PriceListID,
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
        Flavour=Flavour,
        CreatedUserID=CreatedUserID,
        AddlDiscPercent=AddlDiscPercent,
        AddlDiscAmt=AddlDiscAmt,
        TAX1Perc=TAX1Perc,
        TAX1Amount=TAX1Amount,
        TAX2Perc=TAX2Perc,
        TAX2Amount=TAX2Amount,
        TAX3Perc=TAX3Perc,
        TAX3Amount=TAX3Amount,
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
def create_DummyforEditSalesReturn(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    dummydetails = data["DummyDetails"]
    BranchID = data["BranchID"]

    dummies = SalesReturnDetailsDummy.objects.filter(BranchID=BranchID)

    for dummy in dummies:
        dummy.delete()

    for dummydetail in dummydetails:
        unq_id = dummydetail['id']
        SalesReturnDetailsID = dummydetail['SalesReturnDetailsID']
        BranchID = dummydetail['BranchID']
        SalesReturnMasterID = dummydetail['SalesReturnMasterID']
        DeliveryDetailsID = dummydetail['DeliveryDetailsID']
        OrderDetailsID = dummydetail['OrderDetailsID']
        ProductID = dummydetail['ProductID']
        Qty = dummydetail['Qty']
        FreeQty = dummydetail['FreeQty']
        UnitPrice = dummydetail['UnitPrice']
        RateWithTax = dummydetail['RateWithTax']
        CostPerPrice = dummydetail['CostPerPrice']
        PriceListID = dummydetail['PriceListID']
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
        Flavour = dummydetail['Flavour']
        AddlDiscPercent = dummydetail['AddlDiscPercent']
        AddlDiscAmt = dummydetail['AddlDiscAmt']
        TAX1Perc = dummydetail['TAX1Perc']
        TAX1Amount = dummydetail['TAX1Amount']
        TAX2Perc = dummydetail['TAX2Perc']
        TAX2Amount = dummydetail['TAX2Amount']
        TAX3Perc = dummydetail['TAX3Perc']
        TAX3Amount = dummydetail['TAX3Amount']
        detailID = 0

        SalesReturnDetailsDummy.objects.create(
            unq_id=unq_id,
            SalesReturnDetailsID=SalesReturnDetailsID,
            BranchID=BranchID,
            SalesReturnMasterID=SalesReturnMasterID,
            DeliveryDetailsID=DeliveryDetailsID,
            OrderDetailsID=OrderDetailsID,
            ProductID=ProductID,
            Qty=Qty,
            FreeQty=FreeQty,
            UnitPrice=UnitPrice,
            RateWithTax=RateWithTax,
            CostPerPrice=CostPerPrice,
            PriceListID=PriceListID,
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
            Flavour=Flavour,
            CreatedUserID=CreatedUserID,
            AddlDiscPercent=AddlDiscPercent,
            AddlDiscAmt=AddlDiscAmt,
            TAX1Perc=TAX1Perc,
            TAX1Amount=TAX1Amount,
            TAX2Perc=TAX2Perc,
            TAX2Amount=TAX2Amount,
            TAX3Perc=TAX3Perc,
            TAX3Amount=TAX3Amount,
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
def list_salesReturnDetailsDummy(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    serializedList = ListSerializer(data=request.data)

    if serializedList.is_valid():

        BranchID = serializedList.data['BranchID']
        
        if SalesReturnDetailsDummy.objects.filter(BranchID=BranchID).exists():
            net_amount = 0
            gross_amount = 0
            vat_amount = 0
            discount_amount = 0

            instances = SalesReturnDetailsDummy.objects.filter(BranchID=BranchID,IsDeleted=False)
            deleted_instances = SalesReturnDetailsDummy.objects.filter(BranchID=BranchID,IsDeleted=True)

            for instance in instances:

                net_amount += instance.NetAmount

                gross_amount += instance.GrossAmount

                vat_amount += instance.VATAmount

                discount_amount += instance.DiscountAmount

                

            serialized = SalesReturnDetailsDummySerializer(instances,many=True,context = {"DataBase": DataBase })
            serializedDeleted = SalesReturnDetailsDeletedDummySerializer(deleted_instances,many=True)

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
def edit_salesReturnDetailsDummy(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    instance = None
    if SalesReturnDetailsDummy.objects.filter(pk=pk).exists():

        instance = SalesReturnDetailsDummy.objects.get(pk=pk)

        SalesReturnDetailsID = data['SalesReturnDetailsID']
        BranchID = data['BranchID']
        SalesReturnMasterID = data['SalesReturnMasterID']
        DeliveryDetailsID = data['DeliveryDetailsID']
        OrderDetailsID = data['OrderDetailsID']
        ProductID = data['ProductID']
        Qty = data['Qty']
        FreeQty = data['FreeQty']
        UnitPrice = data['UnitPrice']
        RateWithTax = data['RateWithTax']
        CostPerPrice = data['CostPerPrice']
        PriceListID = data['PriceListID']
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
        Flavour = data['Flavour']
        AddlDiscPercent = data['AddlDiscPercent']
        AddlDiscAmt = data['AddlDiscAmt']
        TAX1Perc = data['TAX1Perc']
        TAX1Amount = data['TAX1Amount']
        TAX2Perc = data['TAX2Perc']
        TAX2Amount = data['TAX2Amount']
        TAX3Perc = data['TAX3Perc']
        TAX3Amount = data['TAX3Amount']
        detailID = data['detailID']


        instance.SalesReturnDetailsID = SalesReturnDetailsID
        instance.BranchID = BranchID
        instance.SalesReturnMasterID = SalesReturnMasterID
        instance.DeliveryDetailsID = DeliveryDetailsID
        instance.OrderDetailsID = OrderDetailsID
        instance.ProductID = ProductID
        instance.Qty = Qty
        instance.FreeQty = FreeQty
        instance.UnitPrice = UnitPrice
        instance.RateWithTax = RateWithTax
        instance.CostPerPrice = CostPerPrice
        instance.PriceListID = PriceListID
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
        instance.Flavour = Flavour
        instance.CreatedUserID = CreatedUserID
        instance.AddlDiscPercent = AddlDiscPercent
        instance.AddlDiscAmt = AddlDiscAmt
        instance.TAX1Perc = TAX1Perc
        instance.TAX1Amount = TAX1Amount
        instance.TAX2Perc = TAX2Perc
        instance.TAX2Amount = TAX2Amount
        instance.TAX3Perc = TAX3Perc
        instance.TAX3Amount = TAX3Amount
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
def delete_salesReturnDetailsDummy(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    if SalesReturnDetailsDummy.objects.filter(pk=pk).exists():
        instance = SalesReturnDetailsDummy.objects.get(pk=pk)

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