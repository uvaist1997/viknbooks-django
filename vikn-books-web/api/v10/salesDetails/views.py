from brands.models import SalesDetails, SalesDetails_Log, SalesDetailsDummy, SalesReturnDetailsDummy, SalesOrderDetailsDummy, PurchaseDetailsDummy, PurchaseOrderDetailsDummy, PurchaseReturnDetailsDummy, PaymentDetailsDummy, ReceiptDetailsDummy, JournalDetailsDummy, OpeningStockDetailsDummy
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes,authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from api.v10.salesDetails.serializers import SalesDetailsSerializer, SalesDetailsRestSerializer, SalesDetailsDummySerializer, SalesDetailsDeletedDummySerializer
from api.v10.brands.serializers import ListSerializer
from api.v10.salesDetails.functions import generate_serializer_errors
from rest_framework import status
from api.v10.salesDetails.functions import get_auto_id
import datetime


@api_view(['POST'])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def create_salesDetails(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = SalesDetailsSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        SalesMasterID = serialized.data['SalesMasterID']
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
        Sauceoption = serialized.data['Sauceoption']

        Action = "A"

        SalesDetailsID = get_auto_id(SalesDetails, BranchID, DataBase)

        SalesDetails.objects.create(
            SalesDetailsID=SalesDetailsID,
            BranchID=BranchID,
            SalesMasterID=SalesMasterID,
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
            Sauceoption=Sauceoption,
            Action=Action,
        )

        SalesDetails_Log.objects.create(
            TransactionID=SalesDetailsID,
            BranchID=BranchID,
            SalesMasterID=SalesMasterID,
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
            Sauceoption=Sauceoption,
            Action=Action,
        )

        data = {"SalesDetailsID": SalesDetailsID}
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
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def edit_salesDetails(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    serialized = SalesDetailsSerializer(data=request.data)
    instance = None
    if SalesDetails.objects.filter(pk=pk).exists():
        instance = SalesDetails.objects.get(pk=pk)

        SalesDetailsID = instance.SalesDetailsID
        BranchID = instance.BranchID

        if serialized.is_valid():
            SalesMasterID = serialized.data['SalesMasterID']
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
            Sauceoption = serialized.data['Sauceoption']

            Action = "M"

            instance.SalesMasterID = SalesMasterID
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
            instance.Sauceoption = Sauceoption
            instance.Action = Action
            instance.save()

            SalesDetails_Log.objects.create(
                TransactionID=SalesDetailsID,
                BranchID=BranchID,
                SalesMasterID=SalesMasterID,
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
                Sauceoption=Sauceoption,
                Action=Action,
            )

            data = {"SalesDetailsID": SalesDetailsID}
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
            "message": "Sales Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def list_salesDetails(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if SalesDetails.objects.filter(BranchID=BranchID).exists():

            instances = SalesDetails.objects.filter(BranchID=BranchID)

            serialized = SalesDetailsRestSerializer(instances, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Sales Details Not Found in this BranchID!"
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
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def salesDetail(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    if SalesDetails.objects.filter(pk=pk).exists():
        instance = SalesDetails.objects.get(pk=pk)
        serialized = SalesDetailsRestSerializer(instance)
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Sales Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def delete_salesDetails(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']
    if SalesDetails.objects.filter(pk=pk).exists():
        instance = SalesDetails.objects.get(pk=pk)
    if instance:

        SalesDetailsID = instance.SalesDetailsID
        BranchID = instance.BranchID
        SalesMasterID = instance.SalesMasterID
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
        Sauceoption = instance.Sauceoption
        Action = "D"

        instance.delete()

        SalesDetails_Log.objects.create(
            TransactionID=SalesDetailsID,
            BranchID=BranchID,
            SalesMasterID=SalesMasterID,
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
            Sauceoption=Sauceoption,
            Action=Action,
        )
        response_data = {
            "StatusCode": 6000,
            "message": "Sales Details Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Sales Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def create_salesDetailsDummy(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    SalesDetailsID = data['SalesDetailsID']
    BranchID = data['BranchID']
    ProductID = data['ProductID']
    ProductName = data['ProductName']
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
    Flavour = data['Flavour']
    totalQty = data['totalQty']
    detailID = data['detailID']
    TAX1Perc = data['TAX1Perc']
    TAX2Perc = data['TAX2Perc']
    TAX3Perc = data['TAX3Perc']
    TAX3Amount = data['TAX3Amount']
    TAX1Amount = data['TAX1Amount']
    TAX2Amount = data['TAX2Amount']

    SalesDetailsDummy.objects.create(
        SalesDetailsID=SalesDetailsID,
        BranchID=BranchID,
        ProductID=ProductID,
        ProductName=ProductName,
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
        Flavour=Flavour,
        totalQty=totalQty,
        detailID=detailID,
        TAX1Perc=TAX1Perc,
        TAX2Perc=TAX2Perc,
        TAX3Perc=TAX3Perc,
        TAX3Amount=TAX3Amount,
        TAX1Amount=TAX1Amount,
        TAX2Amount=TAX2Amount,
    )

    response_data = {
        "StatusCode": 6000,
        "message": "success!!!"
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def create_DummyforEditMaster(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    dummydetails = data["DummyDetails"]
    BranchID = data["BranchID"]

    dummies = SalesDetailsDummy.objects.filter(BranchID=BranchID)

    for dummy in dummies:
        dummy.delete()

    for dummydetail in dummydetails:

        unq_id = dummydetail['id']
        SalesDetailsID = dummydetail['SalesDetailsID']
        BranchID = dummydetail['BranchID']
        ProductID = dummydetail['ProductID']
        ProductName = dummydetail['ProductName']
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
        Flavour = dummydetail['Flavour']
        TAX1Perc = dummydetail['TAX1Perc']
        TAX2Perc = dummydetail['TAX2Perc']
        TAX3Perc = dummydetail['TAX3Perc']
        TAX3Amount = dummydetail['TAX3Amount']
        TAX1Amount = dummydetail['TAX1Amount']
        TAX2Amount = dummydetail['TAX2Amount']
        detailID = 0

        SalesDetailsDummy.objects.create(
            unq_id=unq_id,
            SalesDetailsID=SalesDetailsID,
            BranchID=BranchID,
            ProductID=ProductID,
            ProductName=ProductName,
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
            Flavour=Flavour,
            detailID=detailID,
            TAX1Perc=TAX1Perc,
            TAX2Perc=TAX2Perc,
            TAX3Perc=TAX3Perc,
            TAX3Amount=TAX3Amount,
            TAX1Amount=TAX1Amount,
            TAX2Amount=TAX2Amount,
        )

    response_data = {
        "StatusCode": 6000,
        "message": "success!!!"
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def list_salesDetailsDummy(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']

        if SalesDetailsDummy.objects.filter(BranchID=BranchID).exists():
            net_amount = 0
            gross_amount = 0
            vat_amount = 0
            discount_amount = 0

            instances = SalesDetailsDummy.objects.filter(
                BranchID=BranchID, IsDeleted=False)
            deleted_instances = SalesDetailsDummy.objects.filter(
                BranchID=BranchID, IsDeleted=True)

            for instance in instances:

                net_amount += instance.NetAmount

                gross_amount += instance.GrossAmount

                vat_amount += instance.VATAmount

                discount_amount += instance.DiscountAmount

            serialized = SalesDetailsDummySerializer(
                instances, many=True, context={"DataBase": DataBase})
            serializedDeleted = SalesDetailsDeletedDummySerializer(
                deleted_instances, many=True)

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
                "deleted_data": serializedDeleted.data,
                "TotalNetAmount": net_amount,
                "TotalGrossAmount": gross_amount,
                "TotalVatAmount": vat_amount,
                "TotalDiscountAmount": discount_amount,
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
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def edit_salesDetailsDummy(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    if SalesDetailsDummy.objects.filter(pk=pk).exists():

        instance = SalesDetailsDummy.objects.get(pk=pk)

        SalesDetailsID = data['SalesDetailsID']
        BranchID = data['BranchID']
        ProductID = data['ProductID']
        ProductName = data['ProductName']
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
        Flavour = data['Flavour']
        totalQty = data['totalQty']
        TAX1Perc = data['TAX1Perc']
        TAX2Perc = data['TAX2Perc']
        TAX3Perc = data['TAX3Perc']
        TAX3Amount = data['TAX3Amount']
        TAX1Amount = data['TAX1Amount']
        TAX2Amount = data['TAX2Amount']

        detailID = data['detailID']

        instance.SalesDetailsID = SalesDetailsID
        instance.BranchID = BranchID
        instance.ProductID = ProductID
        instance.ProductName = ProductName
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
        instance.Flavour = Flavour
        instance.totalQty = totalQty
        instance.detailID = detailID
        instance.TAX1Perc = TAX1Perc
        instance.TAX2Perc = TAX2Perc
        instance.TAX3Perc = TAX3Perc
        instance.TAX3Amount = TAX3Amount
        instance.TAX1Amount = TAX1Amount
        instance.TAX2Amount = TAX2Amount
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
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def delete_salesDetailsDummy(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    if SalesDetailsDummy.objects.filter(pk=pk).exists():
        instance = SalesDetailsDummy.objects.get(pk=pk)

        instance.IsDeleted = True
        instance.save()

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


@api_view(['POST'])
@permission_classes((AllowAny,))
@authentication_classes((JWTTokenUserAuthentication,))
@renderer_classes((JSONRenderer,))
def clear_dummies(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']
    BranchID = data['BranchID']

    if SalesDetailsDummy.objects.filter(BranchID=BranchID).exists():
        instances = SalesDetailsDummy.objects.filter(BranchID=BranchID)
        for i in instances:
            i.delete()
    else:
        pass
    if SalesReturnDetailsDummy.objects.filter(BranchID=BranchID).exists():
        instances = SalesReturnDetailsDummy.objects.filter(BranchID=BranchID)
        for i in instances:
            i.delete()
    else:
        pass
    if SalesOrderDetailsDummy.objects.filter(BranchID=BranchID).exists():
        instances = SalesOrderDetailsDummy.objects.filter(BranchID=BranchID)
        for i in instances:
            i.delete()
    else:
        pass
    if PurchaseDetailsDummy.objects.filter(BranchID=BranchID).exists():
        instances = PurchaseDetailsDummy.objects.filter(BranchID=BranchID)
        for i in instances:
            i.delete()
    else:
        pass
    if PurchaseOrderDetailsDummy.objects.filter(BranchID=BranchID).exists():
        instances = PurchaseOrderDetailsDummy.objects.filter(BranchID=BranchID)
        for i in instances:
            i.delete()
    else:
        pass
    if PaymentDetailsDummy.objects.filter(BranchID=BranchID).exists():
        instances = PaymentDetailsDummy.objects.filter(BranchID=BranchID)
        for i in instances:
            i.delete()
    else:
        pass
    if SalesDetailsDummy.objects.filter(BranchID=BranchID).exists():
        instances = SalesDetailsDummy.objects.filter(BranchID=BranchID)
        for i in instances:
            i.delete()
    else:
        pass
    if ReceiptDetailsDummy.objects.filter(BranchID=BranchID).exists():
        instances = ReceiptDetailsDummy.objects.filter(BranchID=BranchID)
        for i in instances:
            i.delete()
    else:
        pass
    if JournalDetailsDummy.objects.filter(BranchID=BranchID).exists():
        instances = JournalDetailsDummy.objects.filter(BranchID=BranchID)
        for i in instances:
            i.delete()
    else:
        pass
    if OpeningStockDetailsDummy.objects.filter(BranchID=BranchID).exists():
        instances = OpeningStockDetailsDummy.objects.filter(BranchID=BranchID)
        for i in instances:
            i.delete()
    else:
        pass

    response_data = {
        "StatusCode": 6000,
        "message": "Dummy Cleared Successfully!"
    }

    return Response(response_data, status=status.HTTP_200_OK)
