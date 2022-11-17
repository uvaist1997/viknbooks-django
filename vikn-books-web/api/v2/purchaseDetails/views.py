from brands.models import PurchaseDetails, PurchaseDetails_Log, PurchaseDetailsDummy
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v2.purchaseDetails.serializers import PurchaseDetailsSerializer, PurchaseDetailsRestSerializer, PurchaseDetailsDummySerializer, PurchaseDetailsDeletedDummySerializer
from api.v2.brands.serializers import ListSerializer
from api.v2.purchaseDetails.functions import generate_serializer_errors
from rest_framework import status
from api.v2.purchaseDetails.functions import get_auto_id
import datetime



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_purchaseDetails(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = PurchaseDetailsSerializer(data=request.data)
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        PurchaseMasterID = serialized.data['PurchaseMasterID']
        ProductID = purchaseDetail['ProductID']
        Qty = purchaseDetail['Qty']
        FreeQty = purchaseDetail['FreeQty']
        UnitPrice = purchaseDetail['UnitPrice']
        RateWithTax = purchaseDetail['RateWithTax']
        CostPerItem = purchaseDetail['CostPerItem']
        PriceListID = purchaseDetail['PriceListID']
        TaxID = purchaseDetail['TaxID']
        TaxType = purchaseDetail['TaxType']
        DiscountPerc = purchaseDetail['DiscountPerc']
        DiscountAmount = purchaseDetail['DiscountAmount']
        AddlDiscPerc = purchaseDetail['AddlDiscPerc']
        AddlDiscAmt = purchaseDetail['AddlDiscAmt']
        GrossAmount = purchaseDetail['GrossAmount']
        TaxableAmount = purchaseDetail['TaxableAmount']
        VATPerc = purchaseDetail['VATPerc']
        VATAmount = purchaseDetail['VATAmount']
        SGSTPerc = purchaseDetail['SGSTPerc']
        SGSTAmount = purchaseDetail['SGSTAmount']
        CGSTPerc = purchaseDetail['CGSTPerc']
        CGSTAmount = purchaseDetail['CGSTAmount']
        IGSTPerc = purchaseDetail['IGSTPerc']
        IGSTAmount = purchaseDetail['IGSTAmount']
        NetAmount = purchaseDetail['NetAmount']
        
        Action = "A"

        PurchaseDetailsID = get_auto_id(PurchaseDetails,BranchID,DataBase)

        PurchaseDetails.objects.create(
            PurchaseDetailsID=PurchaseDetailsID,
            BranchID=BranchID,
            Action=Action,
            PurchaseMasterID=PurchaseMasterID,
            ProductID=ProductID,
            Qty=Qty,
            FreeQty=FreeQty,
            UnitPrice=UnitPrice,
            RateWithTax=RateWithTax,
            CostPerItem=CostPerItem,
            PriceListID=PriceListID,
            TaxID=TaxID,
            TaxType=TaxType,
            DiscountPerc=DiscountPerc,
            DiscountAmount=DiscountAmount,
            AddlDiscPerc=AddlDiscPerc,
            AddlDiscAmt=AddlDiscAmt,
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
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            )

        PurchaseDetails_Log.objects.create(
            TransactionID=PurchaseDetailsID,
            BranchID=BranchID,
            Action=Action,
            PurchaseMasterID=PurchaseMasterID,
            ProductID=ProductID,
            Qty=Qty,
            FreeQty=FreeQty,
            UnitPrice=UnitPrice,
            RateWithTax=RateWithTax,
            CostPerItem=CostPerItem,
            PriceListID=PriceListID,
            TaxID=TaxID,
            TaxType=TaxType,
            DiscountPerc=DiscountPerc,
            DiscountAmount=DiscountAmount,
            AddlDiscPerc=AddlDiscPerc,
            AddlDiscAmt=AddlDiscAmt,
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
            CreatedDate=today,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            )

        data = {"PurchaseDetailsID" : PurchaseDetailsID}
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
def edit_purchaseDetails(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    serialized = PurchaseDetailsSerializer(data=request.data)
    instance = None
    if PurchaseDetails.objects.filter(pk=pk).exists():
        instance = PurchaseDetails.objects.get(pk=pk)

        PurchaseDetailsID = instance.PurchaseDetailsID
        BranchID = instance.BranchID
        
        if serialized.is_valid():
            PurchaseMasterID = serialized.data['PurchaseMasterID']
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


            instance.PurchaseMasterID = PurchaseMasterID
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

            PurchaseDetails_Log.objects.create(
                TransactionID=PurchaseDetailsID,
                BranchID=BranchID,
                PurchaseMasterID=PurchaseMasterID,
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

            data = {"PurchaseDetailsID" : PurchaseDetailsID}
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
            "message" : "Purchase Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def list_purchaseDetails(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    serialized1 = ListSerializer(data=request.data)

    if serialized1.is_valid():

        BranchID = serialized1.data['BranchID']
        
        if PurchaseDetails.objects.filter(BranchID=BranchID).exists():

            instances = PurchaseDetails.objects.filter(BranchID=BranchID)

            serialized = PurchaseDetailsRestSerializer(instances,many=True)

            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
            "StatusCode" : 6001,
            "message" : "Purchase Details Not Found in this BranchID!"
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
def purchaseDetail(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']
    instance = None
    if PurchaseDetails.objects.filter(pk=pk).exists():
        instance = PurchaseDetails.objects.get(pk=pk)
        serialized = PurchaseDetailsRestSerializer(instance)
        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Purchase Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def delete_purchaseDetails(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    instance = None
    if PurchaseDetails.objects.filter(pk=pk).exists():
        instance = PurchaseDetails.objects.get(pk=pk)
        PurchaseDetailsID = instance.PurchaseDetailsID
        BranchID = instance.BranchID
        PurchaseMasterID = instance.PurchaseMasterID
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

        PurchaseDetails_Log.objects.create(
            TransactionID=PurchaseDetailsID,
            BranchID=BranchID,
            PurchaseMasterID=PurchaseMasterID,
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
            "message" : "Purchase Details Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Purchase Details Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_purchasesDetailsDummy(request):

    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    PurchaseDetailsID = data['PurchaseDetailsID']
    BranchID = data['BranchID']
    ProductID = data['ProductID']
    Qty = data['Qty']
    FreeQty = data['FreeQty']
    UnitPrice = data['UnitPrice']
    RateWithTax = data['RateWithTax']
    CostPerItem = data['CostPerItem']
    PriceListID = data['PriceListID']
    DiscountPerc = data['DiscountPerc']
    DiscountAmount = data['DiscountAmount']
    AddlDiscPerc = data['AddlDiscPerc']
    AddlDiscAmt = data['AddlDiscAmt']
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
    TAX1Perc = data['TAX1Perc']
    TAX1Amount = data['TAX1Amount']
    TAX2Perc = data['TAX2Perc']
    TAX2Amount = data['TAX2Amount']
    TAX3Perc = data['TAX3Perc']
    TAX3Amount = data['TAX3Amount']


    PurchaseDetailsDummy.objects.create(
        PurchaseDetailsID=PurchaseDetailsID,
        BranchID=BranchID,
        ProductID=ProductID,
        Qty=Qty,
        FreeQty=FreeQty,
        UnitPrice=UnitPrice,
        RateWithTax=RateWithTax,
        CostPerItem=CostPerItem,
        PriceListID=PriceListID,
        DiscountPerc=DiscountPerc,
        DiscountAmount=DiscountAmount,
        AddlDiscPerc=AddlDiscPerc,
        AddlDiscAmt=AddlDiscAmt,
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
        TAX1Perc=detailID,
        TAX1Amount=detailID,
        TAX2Perc=detailID,
        TAX2Amount=detailID,
        TAX3Perc=detailID,
        TAX3Amount=detailID,
        )

    response_data = {
        "StatusCode" : 6000,
        "message" : "success!!!"
    }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def create_DummyforEditPurchase(request):

    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    dummydetails = data["DummyDetails"]
    BranchID = data["BranchID"]

    dummies = PurchaseDetailsDummy.objects.filter(BranchID=BranchID)

    for dummy in dummies:
        dummy.delete()

    for dummydetail in dummydetails:

        unq_id = dummydetail['id']
        PurchaseDetailsID = dummydetail['PurchaseDetailsID']
        BranchID = dummydetail['BranchID']
        ProductID = dummydetail['ProductID']
        Qty = dummydetail['Qty']
        FreeQty = dummydetail['FreeQty']
        UnitPrice = dummydetail['UnitPrice']
        RateWithTax = dummydetail['RateWithTax']
        CostPerItem = dummydetail['CostPerItem']
        PriceListID = dummydetail['PriceListID']
        DiscountPerc = dummydetail['DiscountPerc']
        DiscountAmount = dummydetail['DiscountAmount']
        AddlDiscPerc = dummydetail['AddlDiscPerc']
        AddlDiscAmt = dummydetail['AddlDiscAmt']
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
        TAX1Perc = dummydetail['TAX1Perc']
        TAX1Amount = dummydetail['TAX1Amount']
        TAX2Perc = dummydetail['TAX2Perc']
        TAX2Amount = dummydetail['TAX2Amount']
        TAX3Perc = dummydetail['TAX3Perc']
        TAX3Amount = dummydetail['TAX3Amount']
        detailID = 0

        PurchaseDetailsDummy.objects.create(
            PurchaseDetailsID=PurchaseDetailsID,
            BranchID=BranchID,
            ProductID=ProductID,
            Qty=Qty,
            FreeQty=FreeQty,
            UnitPrice=UnitPrice,
            RateWithTax=RateWithTax,
            CostPerItem=CostPerItem,
            PriceListID=PriceListID,
            DiscountPerc=DiscountPerc,
            DiscountAmount=DiscountAmount,
            AddlDiscPerc=AddlDiscPerc,
            AddlDiscAmt=AddlDiscAmt,
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
def list_purchasesDetailsDummy(request):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']
    
    serializedList = ListSerializer(data=request.data)

    if serializedList.is_valid():

        BranchID = serializedList.data['BranchID']
        
        if PurchaseDetailsDummy.objects.filter(BranchID=BranchID).exists():
            net_amount = 0
            gross_amount = 0
            vat_amount = 0
            discount_amount = 0
            SGSTAmount = 0
            CGSTAmount = 0
            IGSTAmount = 0
            TAX1Amount = 0
            TAX2Amount = 0
            TAX3Amount = 0

            instances = PurchaseDetailsDummy.objects.filter(BranchID=BranchID,IsDeleted=False)

            deleted_instances = PurchaseDetailsDummy.objects.filter(BranchID=BranchID,IsDeleted=True)
            
            for instance in instances:

                net_amount += instance.NetAmount

                gross_amount += instance.GrossAmount

                vat_amount += instance.VATAmount

                discount_amount += instance.DiscountAmount

                SGSTAmount += instance.SGSTAmount

                CGSTAmount += instance.CGSTAmount

                IGSTAmount += instance.IGSTAmount

                TAX1Amount += instance.TAX1Amount

                TAX2Amount += instance.TAX2Amount   

                TAX3Amount += instance.TAX3Amount

            serialized = PurchaseDetailsDummySerializer(instances,many=True,context = {"DataBase": DataBase })
            serializedDeleted = PurchaseDetailsDeletedDummySerializer(deleted_instances,many=True)

            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data,
                "deleted_data" : serializedDeleted.data,
                "TotalNetAmount" : net_amount,
                "TotalGrossAmount" : gross_amount,
                "TotalVatAmount" : vat_amount,
                "TotalDiscountAmount" : discount_amount,
                "SGSTAmount" : SGSTAmount,
                "CGSTAmount" : CGSTAmount,
                "IGSTAmount" : IGSTAmount,
                "TAX1Amount" : TAX1Amount,
                "TAX2Amount" : TAX2Amount,
                "TAX3Amount" : TAX3Amount,
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
def edit_purchasesDetailsDummy(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    if PurchaseDetailsDummy.objects.filter(pk=pk).exists():

        instance = PurchaseDetailsDummy.objects.get(pk=pk)

        PurchaseDetailsID = data['PurchaseDetailsID']
        BranchID = data['BranchID']
        ProductID = data['ProductID']
        Qty = data['Qty']
        FreeQty = data['FreeQty']
        UnitPrice = data['UnitPrice']
        RateWithTax = data['RateWithTax']
        CostPerItem = data['CostPerItem']
        PriceListID = data['PriceListID']
        DiscountPerc = data['DiscountPerc']
        DiscountAmount = data['DiscountAmount']
        AddlDiscPerc = data['AddlDiscPerc']
        AddlDiscAmt = data['AddlDiscAmt']
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
        TAX1Perc = data['TAX1Perc']
        TAX1Amount = data['TAX1Amount']
        TAX2Perc = data['TAX2Perc']
        TAX2Amount = data['TAX2Amount']
        TAX3Perc = data['TAX3Perc']
        TAX3Amount = data['TAX3Amount']

        detailID = data['detailID']

        instance.PurchaseDetailsID = PurchaseDetailsID
        instance.BranchID = BranchID
        instance.ProductID = ProductID
        instance.Qty = Qty
        instance.FreeQty = FreeQty
        instance.UnitPrice = UnitPrice
        instance.RateWithTax = RateWithTax
        instance.CostPerItem = CostPerItem
        instance.PriceListID = PriceListID
        instance.DiscountPerc = DiscountPerc
        instance.DiscountAmount = DiscountAmount
        instance.AddlDiscPerc = AddlDiscPerc
        instance.AddlDiscAmt = AddlDiscAmt
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
def delete_purchasesDetailsDummy(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']

    instance = None
    if PurchaseDetailsDummy.objects.filter(pk=pk).exists():
        instance = PurchaseDetailsDummy.objects.get(pk=pk)

        instance.IsDeleted = True
        instance.save()
        # instance.delete()

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
