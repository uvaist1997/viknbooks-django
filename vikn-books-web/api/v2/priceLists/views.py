from brands.models import PriceList, PriceList_Log, TaxCategory, Product,StockPosting
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v2.priceLists.serializers import PriceListSerializer, PriceListRestSerializer, ListSerializer
from api.v2.priceLists.functions import generate_serializer_errors
from rest_framework import status
from api.v2.priceLists.functions import get_auto_id
from api.v2.products.functions import get_auto_AutoBarcode
import datetime
from main.functions import get_company, activity_log



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_priceList(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = PriceListSerializer(data=request.data)   
    if serialized.is_valid():

        BranchID = serialized.data['BranchID']
        ProductID = serialized.data['ProductID']
        UnitName = serialized.data['UnitName']
        SalesPrice = serialized.data['SalesPrice']
        PurchasePrice = serialized.data['PurchasePrice']
        MultiFactor = serialized.data['MultiFactor']
        Barcode = serialized.data['Barcode']
        # AutoBarcode = serialized.data['AutoBarcode']
        SalesPrice1 = serialized.data['SalesPrice1']
        SalesPrice2 = serialized.data['SalesPrice2']
        SalesPrice3 = serialized.data['SalesPrice3']
        DefaultUnit = serialized.data['DefaultUnit']
        UnitInSales = serialized.data['UnitInSales']
        UnitInPurchase = serialized.data['UnitInPurchase']
        UnitInReports = serialized.data['UnitInReports']

        Action = 'A'

        PriceListID = get_auto_id(PriceList,BranchID,CompanyID)
        AutoBarcode = get_auto_AutoBarcode(PriceList,BranchID,CompanyID)


        PriceList.objects.create(
            PriceListID=PriceListID,
            BranchID=BranchID,
            ProductID=ProductID,
            UnitName=UnitName,
            SalesPrice=SalesPrice,
            PurchasePrice=PurchasePrice,
            MultiFactor=MultiFactor,
            Barcode=Barcode,
            AutoBarcode=AutoBarcode,
            SalesPrice1=SalesPrice1,
            SalesPrice2=SalesPrice2,
            SalesPrice3=SalesPrice3,
            CreatedDate=today,
            UpdatedDate=today,
            Action=Action,
            DefaultUnit=DefaultUnit,
            UnitInSales=UnitInSales,
            UnitInPurchase=UnitInPurchase,
            UnitInReports=UnitInReports,
            CreatedUserID=CreatedUserID,
            )

        PriceList_Log.objects.create(
            TransactionID=PriceListID,
            BranchID=BranchID,
            ProductID=ProductID,
            UnitName=UnitName,
            SalesPrice=SalesPrice,
            PurchasePrice=PurchasePrice,
            MultiFactor=MultiFactor,
            Barcode=Barcode,
            AutoBarcode=AutoBarcode,
            SalesPrice1=SalesPrice1,
            SalesPrice2=SalesPrice2,
            SalesPrice3=SalesPrice3,
            CreatedDate=today,
            UpdatedDate=today,
            Action=Action,
            DefaultUnit=DefaultUnit,
            UnitInSales=UnitInSales,
            UnitInPurchase=UnitInPurchase,
            UnitInReports=UnitInReports,
            CreatedUserID=CreatedUserID,
            )

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'PriceList', 'Create', 'PriceList created successfully.', 'PriceList saved successfully.')

        data = {"PriceListID" : PriceListID}
        data.update(serialized.data)
        response_data = {
            "StatusCode" : 6000,
            "data" : data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'PriceList', 'Create', 'PriceList created Failed.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode" : 6001,
            "message" : generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_priceList(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    serialized = PriceListSerializer(data=request.data)
    instance = PriceList.objects.get(CompanyID=CompanyID,pk=pk)
    
    PriceListID = instance.PriceListID
    BranchID = instance.BranchID
    AutoBarcode = instance.AutoBarcode   
    if serialized.is_valid():

        ProductID = serialized.data['ProductID']
        UnitName = serialized.data['UnitName']
        SalesPrice = serialized.data['SalesPrice']
        PurchasePrice = serialized.data['PurchasePrice']
        MultiFactor = serialized.data['MultiFactor']
        Barcode = serialized.data['Barcode']
        SalesPrice1 = serialized.data['SalesPrice1']
        SalesPrice2 = serialized.data['SalesPrice2']
        SalesPrice3 = serialized.data['SalesPrice3']
        DefaultUnit = serialized.data['DefaultUnit']
        UnitInSales = serialized.data['UnitInSales']
        UnitInPurchase = serialized.data['UnitInPurchase']
        UnitInReports = serialized.data['UnitInReports']

        Action = 'M'

        instance.ProductID = ProductID
        instance.UnitName = UnitName
        instance.SalesPrice = SalesPrice
        instance.PurchasePrice = PurchasePrice
        instance.MultiFactor = MultiFactor
        instance.Barcode = Barcode
        instance.AutoBarcode = AutoBarcode
        instance.SalesPrice1 = SalesPrice1
        instance.SalesPrice2 = SalesPrice2
        instance.SalesPrice3 = SalesPrice3
        instance.SalesPrice3 = SalesPrice3
        instance.Action = Action
        instance.DefaultUnit = DefaultUnit
        instance.UnitInSales = UnitInSales
        instance.UnitInPurchase = UnitInPurchase
        instance.UnitInReports = UnitInReports
        instance.UpdatedDate = today
        instance.CreatedUserID = CreatedUserID

        instance.save()
        PriceList_Log.objects.create(
            TransactionID=PriceListID,
            BranchID=BranchID,
            ProductID=ProductID,
            UnitName=UnitName,
            SalesPrice=SalesPrice,
            PurchasePrice=PurchasePrice,
            MultiFactor=MultiFactor,
            Barcode=Barcode,
            AutoBarcode=AutoBarcode,
            SalesPrice1=SalesPrice1,
            SalesPrice2=SalesPrice2,
            SalesPrice3=SalesPrice3,
            CreatedDate=today,
            UpdatedDate=today,
            Action=Action,
            DefaultUnit=DefaultUnit,
            UnitInSales=UnitInSales,
            UnitInPurchase=UnitInPurchase,
            UnitInReports=UnitInReports,
            CreatedUserID=CreatedUserID,
            )

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'PriceList', 'Edit', 'PriceList Updated successfully.', 'PriceList Updated successfully.')

        data = {"PriceListID" : PriceListID}
        data.update(serialized.data)
        response_data = {
            "StatusCode" : 6000,
            "data" : data
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Error', CreatedUserID, 'PriceList', 'Edit', 'PriceList Updated Failed.', generate_serializer_errors(serialized._errors))
        response_data = {
            "StatusCode" : 6001,
            "message" : generate_serializer_errors(serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def priceLists(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        ProductID = serialized1.data['ProductID'] 
        if PriceList.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ProductID=ProductID).exists():
            instances = PriceList.objects.filter(CompanyID=CompanyID,BranchID=BranchID,ProductID=ProductID)
            serialized = PriceListRestSerializer(instances,many=True,context={"CompanyID":CompanyID,"PriceRounding":PriceRounding})

            product_instance = get_object_or_404(Product.objects.filter(CompanyID=CompanyID,ProductID=ProductID,BranchID=BranchID))
            TaxID1 = product_instance.Tax1
            TaxID2 = product_instance.Tax2
            TaxID3 = product_instance.Tax3
            GST = product_instance.GST
            VatID = product_instance.VatID

            Tax1_PurchaseTax = 0
            Tax2_PurchaseTax = 0
            Tax3_PurchaseTax = 0
            GST_PurchaseTax = 0
            Vat_PurchaseTax = 0

            Tax1_Inclusive = ""
            if TaxCategory.objects.filter(CompanyID=CompanyID,TaxID=TaxID1,BranchID=BranchID).exists():
                tax = TaxCategory.objects.get(CompanyID=CompanyID,TaxID=TaxID1,BranchID=BranchID)
                PurchaseTax = tax.PurchaseTax
                Tax1_PurchaseTax = round(PurchaseTax,2)
                Tax1_Inclusive = tax.Inclusive

            Tax2_Inclusive = ""
            if TaxCategory.objects.filter(CompanyID=CompanyID,TaxID=TaxID2,BranchID=BranchID).exists():
                tax = TaxCategory.objects.get(CompanyID=CompanyID,TaxID=TaxID2,BranchID=BranchID)
                PurchaseTax = tax.PurchaseTax
                Tax2_PurchaseTax = round(PurchaseTax,2)
                Tax2_Inclusive = tax.Inclusive

            Tax3_Inclusive = ""
            if TaxCategory.objects.filter(CompanyID=CompanyID,TaxID=TaxID3,BranchID=BranchID).exists():
                tax = TaxCategory.objects.get(CompanyID=CompanyID,TaxID=TaxID3,BranchID=BranchID)
                PurchaseTax = tax.PurchaseTax
                Tax3_PurchaseTax = round(PurchaseTax,2)
                Tax3_Inclusive = tax.Inclusive

            GST_Inclusive = ""
            if TaxCategory.objects.filter(CompanyID=CompanyID,TaxID=GST,BranchID=BranchID).exists():
                tax = TaxCategory.objects.get(CompanyID=CompanyID,TaxID=GST,BranchID=BranchID)
                PurchaseTax = tax.PurchaseTax
                GST_PurchaseTax = round(PurchaseTax,2)
                GST_Inclusive = tax.Inclusive

            Vat_Inclusive = ""
            if TaxCategory.objects.filter(CompanyID=CompanyID,TaxID=VatID,BranchID=BranchID).exists():
                tax = TaxCategory.objects.get(CompanyID=CompanyID,TaxID=VatID,BranchID=BranchID)
                PurchaseTax = tax.PurchaseTax
                Vat_PurchaseTax = round(PurchaseTax,2)
                Vat_Inclusive = tax.Inclusive


            MinimumSalesPrice = Product.objects.get(ProductID=ProductID,CompanyID=CompanyID,BranchID=BranchID).MinimumSalesPrice
            IsKFC = Product.objects.get(ProductID=ProductID,CompanyID=CompanyID,BranchID=BranchID).IsKFC
            

            response_data = {
                "StatusCode" : 6000,
                "data" : serialized.data,
                "Tax1_PurchaseTax" : float(Tax1_PurchaseTax),
                "Tax2_PurchaseTax" : float(Tax2_PurchaseTax),
                "Tax3_PurchaseTax" : float(Tax3_PurchaseTax),
                "GST_PurchaseTax" : float(GST_PurchaseTax),
                "Vat_PurchaseTax" : float(Vat_PurchaseTax),
                "Tax1_Inclusive" : Tax1_Inclusive,
                "Tax2_Inclusive" : Tax2_Inclusive,
                "Tax3_Inclusive" : Tax3_Inclusive,
                "GST_Inclusive" : GST_Inclusive,
                "Vat_Inclusive" : Vat_Inclusive,
                "MinimumSalesPrice" : MinimumSalesPrice,
                "is_kfc" : IsKFC
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
            "StatusCode" : 6001,
            "message" : "PriceList Not Found in this BranchID!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def priceList(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    if PriceList.objects.filter(CompanyID=CompanyID,pk=pk).exists():
        instance = PriceList.objects.get(CompanyID=CompanyID,pk=pk)
        serialized = PriceListRestSerializer(instance,context = {"CompanyID": CompanyID,
            "PriceRounding" : PriceRounding })
        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Price List Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def single_priceList(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceListID = data['PriceListID']
    PriceRounding = data['PriceRounding']
    BranchID = data['BranchID']

    if PriceList.objects.filter(CompanyID=CompanyID,PriceListID=PriceListID,BranchID=BranchID).exists():
        TotalQtyIn = 0
        TotalQtyOut = 0
        if StockPosting.objects.filter(CompanyID=CompanyID,PriceListID=PriceListID,BranchID=BranchID).exists():
            stockpostIns = StockPosting.objects.filter(CompanyID=CompanyID,PriceListID=PriceListID,BranchID=BranchID)
            for i in stockpostIns:
                TotalQtyIn += i.QtyIn
                TotalQtyOut += i.QtyOut

        Stock = float(TotalQtyIn) - float(TotalQtyOut)

        instance = PriceList.objects.get(CompanyID=CompanyID,PriceListID=PriceListID,BranchID=BranchID)
        serialized = PriceListRestSerializer(instance,context = {"CompanyID": CompanyID,
            "PriceRounding" : PriceRounding })
        response_data = {
            "StatusCode" : 6000,
            "data" : serialized.data,
            "Stock" : round(Stock,PriceRounding)
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Price List Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_priceList(request,pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    if PriceList.objects.filter(CompanyID=CompanyID,pk=pk).exists():
        instance = PriceList.objects.get(CompanyID=CompanyID,pk=pk)
        PriceListID = instance.PriceListID
        BranchID = instance.BranchID
        ProductID = instance.ProductID
        UnitName = instance.UnitName
        SalesPrice = instance.SalesPrice
        PurchasePrice = instance.PurchasePrice
        MultiFactor = instance.MultiFactor
        Barcode = instance.Barcode
        AutoBarcode = instance.AutoBarcode
        SalesPrice1 = instance.SalesPrice1
        SalesPrice2 = instance.SalesPrice2
        SalesPrice3 = instance.SalesPrice3
        DefaultUnit = instance.DefaultUnit
        UnitInSales = instance.UnitInSales
        UnitInPurchase = instance.UnitInPurchase
        UnitInReports = instance.UnitInReports
        Action = "D"

        instance.delete()

        PriceList_Log.objects.create(
            TransactionID=PriceListID,
            BranchID=BranchID,
            ProductID=ProductID,
            UnitName=UnitName,
            SalesPrice=SalesPrice,
            PurchasePrice=PurchasePrice,
            MultiFactor=MultiFactor,
            Barcode=Barcode,
            AutoBarcode=AutoBarcode,
            SalesPrice1=SalesPrice1,
            SalesPrice2=SalesPrice2,
            SalesPrice3=SalesPrice3,
            CreatedDate=today,
            UpdatedDate=today,
            Action=Action,
            DefaultUnit=DefaultUnit,
            UnitInSales=UnitInSales,
            UnitInPurchase=UnitInPurchase,
            UnitInReports=UnitInReports,
            CreatedUserID=CreatedUserID,
            )

        response_data = {
            "StatusCode" : 6000,
            "message" : "Price List Deleted Successfully!"
        }
    else:
        response_data = {
            "StatusCode" : 6001,
            "message" : "Price List Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)