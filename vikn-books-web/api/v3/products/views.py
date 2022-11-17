from brands.models import Product, Product_Log, PriceList, PriceList_Log, PurchaseDetails, PurchaseOrderDetails, SalesDetails, SalesOrderDetails, StockPosting, TaxCategory, TaxCategory_Log, Brand, Brand_Log, ProductGroup, ProductGroup_Log, Unit, Unit_Log, Batch, GeneralSettings
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v3.products.serializers import ProductSerializer, SingleProductRestSerializer, ProductRestSerializer, ProductbyGrouptSerializer, BarCodeSearchSerializer, UploadSerializer, ProductSearchShortcutSerializer
from api.v3.priceLists.serializers import PriceListSerializer, PriceListRestSerializer
from api.v3.brands.serializers import ListSerializer
from api.v3.products.functions import generate_serializer_errors, generate_priceList_serializer_errors
from rest_framework import status
from api.v3.products.functions import get_auto_id, get_auto_priceListid, get_ProductCode, get_auto_AutoBarcode, get_auto_BatchNo, get_auto_AutoBatchCode
import datetime
from django.shortcuts import render, get_object_or_404
from main.functions import get_company, activity_log
import xlrd
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from api.v3.ledgerPosting.functions import convertOrderdDict
import json
from django.db.models import Q, Prefetch
from collections import OrderedDict
import os
from django.conf import settings
from api.v3.products.tasks import import_product_task
from celery.result import AsyncResult
from api.v3.products.utils import in_memory_file_to_temp
from django.db.models import Max


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def create_product(request):
    today = datetime.datetime.now()

    data = request.data
    product_serialized = ProductSerializer(data=request.data)

    ProductImage = data['ProductImage']
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    if product_serialized.is_valid():
        CreatedUserID = product_serialized.data['CreatedUserID']
        BranchID = product_serialized.data['BranchID']
        ProductName = product_serialized.data['ProductName']
        DisplayName = product_serialized.data['DisplayName']
        Description = product_serialized.data['Description']
        ProductGroupID = product_serialized.data['ProductGroupID']
        BrandID = product_serialized.data['BrandID']
        InventoryType = product_serialized.data['InventoryType']
        VatID = product_serialized.data['VatID']
        MinimumSalesPrice = product_serialized.data['MinimumSalesPrice']
        StockMinimum = product_serialized.data['StockMinimum']
        StockReOrder = product_serialized.data['StockReOrder']
        StockMaximum = product_serialized.data['StockMaximum']
        MarginPercent = product_serialized.data['MarginPercent']
        Active = product_serialized.data['Active']
        IsRawMaterial = product_serialized.data['IsRawMaterial']
        IsWeighingScale = product_serialized.data['IsWeighingScale']
        IsFinishedProduct = product_serialized.data['IsFinishedProduct']
        IsSales = product_serialized.data['IsSales']
        IsPurchase = product_serialized.data['IsPurchase']
        WeighingCalcType = product_serialized.data['WeighingCalcType']
        PLUNo = product_serialized.data['PLUNo']
        IsFavourite = product_serialized.data['IsFavourite']
        GST = product_serialized.data['GST']
        Tax1 = product_serialized.data['Tax1']
        Tax2 = product_serialized.data['Tax2']
        Tax3 = product_serialized.data['Tax3']
        ProductCode = product_serialized.data['ProductCode']
        IsKFC = product_serialized.data['IsKFC']
        HSNCode = product_serialized.data['HSNCode']

        Action = "A"

        ProductID = get_auto_id(Product, BranchID, CompanyID)
        # ProductCode = get_ProductCode(Product, BranchID,CompanyID)

        is_nameExist = False
        is_ProductCodeExist = False

        ProductNameLow = ProductName.lower()
        ProductCodeLow = ProductCode.lower()

        products = Product.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID)

        for product in products:
            product_name = product.ProductName
            product_code = product.ProductCode

            productName = product_name.lower()
            productCode = product_code.lower()

            if ProductNameLow == productName:
                is_nameExist = True
            if ProductCodeLow == productCode:
                is_ProductCodeExist = True

        if not is_nameExist and not is_ProductCodeExist:
            instance = Product.objects.create(
                ProductID=ProductID,
                BranchID=BranchID,
                ProductCode=ProductCode,
                ProductName=ProductName,
                DisplayName=DisplayName,
                Description=Description,
                ProductGroupID=ProductGroupID,
                BrandID=BrandID,
                InventoryType=InventoryType,
                VatID=VatID,
                MinimumSalesPrice=MinimumSalesPrice,
                StockMinimum=StockMinimum,
                StockReOrder=StockReOrder,
                StockMaximum=StockMaximum,
                MarginPercent=MarginPercent,
                ProductImage=ProductImage,
                Active=Active,
                IsWeighingScale=IsWeighingScale,
                IsRawMaterial=IsRawMaterial,
                IsFinishedProduct=IsFinishedProduct,
                IsSales=IsSales,
                IsPurchase=IsPurchase,
                WeighingCalcType=WeighingCalcType,
                PLUNo=PLUNo,
                IsFavourite=IsFavourite,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                GST=GST,
                Tax1=Tax1,
                Tax2=Tax2,
                Tax3=Tax3,
                Action=Action,
                CompanyID=CompanyID,
                IsKFC=IsKFC,
                HSNCode=HSNCode,
            )

            Product_Log.objects.create(
                TransactionID=ProductID,
                BranchID=BranchID,
                ProductCode=ProductCode,
                ProductName=ProductName,
                DisplayName=DisplayName,
                Description=Description,
                ProductGroupID=ProductGroupID,
                BrandID=BrandID,
                InventoryType=InventoryType,
                VatID=VatID,
                MinimumSalesPrice=MinimumSalesPrice,
                StockMinimum=StockMinimum,
                StockReOrder=StockReOrder,
                StockMaximum=StockMaximum,
                MarginPercent=MarginPercent,
                ProductImage=ProductImage,
                Active=Active,
                IsWeighingScale=IsWeighingScale,
                IsRawMaterial=IsRawMaterial,
                IsFinishedProduct=IsFinishedProduct,
                IsSales=IsSales,
                IsPurchase=IsPurchase,
                WeighingCalcType=WeighingCalcType,
                PLUNo=PLUNo,
                IsFavourite=IsFavourite,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                GST=GST,
                Tax1=Tax1,
                Tax2=Tax2,
                Tax3=Tax3,
                Action=Action,
                CompanyID=CompanyID,
                IsKFC=IsKFC,
                HSNCode=HSNCode,
            )

            try:
                priceListDetails = json.loads(data["PriceListDetails"])
            except:
                priceListDetails = data["PriceListDetails"]
            batch_count = 0
            for priceListDetail in priceListDetails:
                # UnitName = priceListDetail['UnitName']
                UnitID = priceListDetail['UnitID']
                SalesPrice = priceListDetail['SalesPrice']
                PurchasePrice = priceListDetail['PurchasePrice']
                MultiFactor = priceListDetail['MultiFactor']
                Barcode = priceListDetail['Barcode']
                # AutoBarcode = priceListDetail['AutoBarcode']
                SalesPrice1 = priceListDetail['SalesPrice1']
                SalesPrice2 = priceListDetail['SalesPrice2']
                SalesPrice3 = priceListDetail['SalesPrice3']
                DefaultUnit = priceListDetail['DefaultUnit']
                UnitInSales = priceListDetail['UnitInSales']
                UnitInPurchase = priceListDetail['UnitInPurchase']
                UnitInReports = priceListDetail['UnitInReports']
                MRP = priceListDetail['MRP']

                if UnitID:

                    PriceListID = get_auto_priceListid(
                        PriceList, BranchID, CompanyID)
                    AutoBarcode = get_auto_AutoBarcode(
                        PriceList, BranchID, CompanyID)

                    PriceList.objects.create(
                        PriceListID=PriceListID,
                        BranchID=BranchID,
                        ProductID=ProductID,
                        product=instance,
                        UnitID=UnitID,
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
                        MRP=MRP,
                        Action=Action,
                        DefaultUnit=DefaultUnit,
                        UnitInSales=UnitInSales,
                        UnitInPurchase=UnitInPurchase,
                        UnitInReports=UnitInReports,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                    )

                    PriceList_Log.objects.create(
                        TransactionID=PriceListID,
                        BranchID=BranchID,
                        ProductID=ProductID,
                        UnitID=UnitID,
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
                        CompanyID=CompanyID,
                    )

                if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                    check_EnableProductBatchWise = GeneralSettings.objects.get(
                        CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
                    if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                        if batch_count == 0:
                            # BatchNo = get_auto_BatchNo(Batch, BranchID, CompanyID)
                            BatchCode = get_auto_AutoBatchCode(
                                Batch, BranchID, CompanyID)
                            Batch.objects.create(
                                CompanyID=CompanyID,
                                BranchID=BranchID,
                                ManufactureDate=today,
                                ExpiryDate=today+datetime.timedelta(3650),
                                BatchCode=BatchCode,
                                StockIn=0,
                                StockOut=0,
                                PurchasePrice=PurchasePrice,
                                SalesPrice=SalesPrice,
                                # PurchaseCost=PurchasePrice,
                                PriceListID=PriceListID,
                                ProductID=ProductID,
                                WareHouseID=1,
                                Description=Description,
                                CreatedDate=today,
                                UpdatedDate=today,
                                CreatedUserID=CreatedUserID,
                            )
                            batch_count += 1

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product',
                         'Create', 'Product created successfully.', 'Product saved successfully.')
            response_data = {
                "StatusCode": 6000,
                "message": "Product Created Successfully!!!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            if is_nameExist and is_ProductCodeExist:
                #  request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Product', 'Create',
                             'Product created Failed.', 'Product Name and ProductCode Already Exist in this Branch.')
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Name and Product Code Already Exist in this Branch!!!"
                }
            elif is_nameExist:
                #  request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Product',
                             'Create', 'Product created Failed.', 'Product Name Already Exist in this Branch.')
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Name Already Exist in this Branch!!!"
                }
            elif is_ProductCodeExist:
                #  request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Product',
                             'Create', 'Product created Failed.', 'Product Code Already Exist in this Branch.')
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Code Already Exist in this Branch!!!"
                }

        return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(product_serialized._errors)
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def edit_product(request, pk):
    data = request.data

    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    product_instance = Product.objects.get(CompanyID=CompanyID, pk=pk)
    BranchID = product_instance.BranchID
    ProductID = product_instance.ProductID
    InstanceProductCode = product_instance.ProductCode
    instanceProductName = product_instance.ProductName
    product_serialized = ProductSerializer(data=request.data)
    ProductImage = data['ProductImage']
    if ProductImage == "" or None:
        ProductImage = product_instance.ProductImage
    if product_serialized.is_valid():
        ProductName = product_serialized.data['ProductName']
        DisplayName = product_serialized.data['DisplayName']
        Description = product_serialized.data['Description']
        ProductGroupID = product_serialized.data['ProductGroupID']
        BrandID = product_serialized.data['BrandID']
        InventoryType = product_serialized.data['InventoryType']
        VatID = product_serialized.data['VatID']
        MinimumSalesPrice = product_serialized.data['MinimumSalesPrice']
        StockMinimum = product_serialized.data['StockMinimum']
        StockReOrder = product_serialized.data['StockReOrder']
        StockMaximum = product_serialized.data['StockMaximum']
        MarginPercent = product_serialized.data['MarginPercent']

        Active = product_serialized.data['Active']
        IsRawMaterial = product_serialized.data['IsRawMaterial']
        IsWeighingScale = product_serialized.data['IsWeighingScale']
        IsFinishedProduct = product_serialized.data['IsFinishedProduct']
        IsSales = product_serialized.data['IsSales']
        IsPurchase = product_serialized.data['IsPurchase']
        WeighingCalcType = product_serialized.data['WeighingCalcType']
        PLUNo = product_serialized.data['PLUNo']
        IsFavourite = product_serialized.data['IsFavourite']
        GST = product_serialized.data['GST']
        Tax1 = product_serialized.data['Tax1']
        Tax2 = product_serialized.data['Tax2']
        Tax3 = product_serialized.data['Tax3']
        ProductCode = product_serialized.data['ProductCode']
        IsKFC = product_serialized.data['IsKFC']
        HSNCode = product_serialized.data['HSNCode']

        Action = "M"

        is_nameExist = False
        is_codeExist = False
        product_ok = False
        productCode_ok = False

        ProductNameLow = ProductName.lower()
        ProductCodeLow = ProductCode.lower()

        products = Product.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID)

        for product in products:
            product_name = product.ProductName
            product_code = str(product.ProductCode)

            productName = product_name.lower()
            productCode = product_code.lower()

            if ProductNameLow == productName:
                is_nameExist = True
            if ProductCodeLow == productCode:
                is_codeExist = True
            if instanceProductName.lower() == ProductNameLow:
                product_ok = True
            elif is_nameExist == False:
                product_ok = True
            if InstanceProductCode.lower() == ProductCodeLow:
                productCode_ok = True

        if product_ok and productCode_ok:

            product_instance.ProductName = ProductName
            product_instance.DisplayName = DisplayName
            product_instance.Description = Description
            product_instance.ProductGroupID = ProductGroupID
            product_instance.BrandID = BrandID
            product_instance.InventoryType = InventoryType
            product_instance.VatID = VatID
            product_instance.MinimumSalesPrice = MinimumSalesPrice
            product_instance.StockMinimum = StockMinimum
            product_instance.StockReOrder = StockReOrder
            product_instance.StockMaximum = StockMaximum
            product_instance.MarginPercent = MarginPercent
            product_instance.ProductImage = ProductImage
            product_instance.Active = Active
            product_instance.IsRawMaterial = IsRawMaterial
            product_instance.IsWeighingScale = IsWeighingScale
            product_instance.WeighingCalcType = WeighingCalcType
            product_instance.PLUNo = PLUNo
            product_instance.GST = GST
            product_instance.Tax1 = Tax1
            product_instance.Tax2 = Tax2
            product_instance.Tax3 = Tax3
            product_instance.IsFavourite = IsFavourite
            product_instance.IsFinishedProduct = IsFinishedProduct
            product_instance.IsSales = IsSales
            product_instance.IsPurchase = IsPurchase
            product_instance.Action = Action
            product_instance.CreatedUserID = CreatedUserID
            product_instance.UpdatedDate = today
            product_instance.IsKFC = IsKFC
            product_instance.HSNCode = HSNCode

            product_instance.save()

            Product_Log.objects.create(
                TransactionID=ProductID,
                BranchID=BranchID,
                ProductCode=ProductCode,
                ProductName=ProductName,
                DisplayName=DisplayName,
                Description=Description,
                ProductGroupID=ProductGroupID,
                BrandID=BrandID,
                InventoryType=InventoryType,
                VatID=VatID,
                StockMinimum=StockMinimum,
                MinimumSalesPrice=MinimumSalesPrice,
                StockReOrder=StockReOrder,
                StockMaximum=StockMaximum,
                MarginPercent=MarginPercent,
                ProductImage=ProductImage,
                Active=Active,
                IsWeighingScale=IsWeighingScale,
                IsRawMaterial=IsRawMaterial,
                IsFinishedProduct=IsFinishedProduct,
                IsSales=IsSales,
                IsPurchase=IsPurchase,
                WeighingCalcType=WeighingCalcType,
                PLUNo=PLUNo,
                IsFavourite=IsFavourite,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                GST=GST,
                Tax1=Tax1,
                Tax2=Tax2,
                Tax3=Tax3,
                Action=Action,
                CompanyID=CompanyID,
                IsKFC=IsKFC,
                HSNCode=HSNCode,
            )

            try:
                priceListDetails = json.loads(data["PriceListDetails"])
            except:
                priceListDetails = data["PriceListDetails"]
            print(priceListDetails)
            pk_array = []

            for priceListDetail in priceListDetails:
                pk = priceListDetail["id"]
                UnitID = priceListDetail['UnitID']
                SalesPrice = priceListDetail['SalesPrice']
                PurchasePrice = priceListDetail['PurchasePrice']
                MultiFactor = priceListDetail['MultiFactor']
                Barcode = priceListDetail['Barcode']
                SalesPrice1 = priceListDetail['SalesPrice1']
                SalesPrice2 = priceListDetail['SalesPrice2']
                SalesPrice3 = priceListDetail['SalesPrice3']
                DefaultUnit = priceListDetail['DefaultUnit']
                UnitInSales = priceListDetail['UnitInSales']
                UnitInPurchase = priceListDetail['UnitInPurchase']
                UnitInReports = priceListDetail['UnitInReports']
                MRP = priceListDetail['MRP']
                detailID = priceListDetail['detailID']

                if SalesPrice1 == '':
                    SalesPrice1 = 0
                if SalesPrice2 == '':
                    SalesPrice2 = 0
                if SalesPrice3 == '':
                    SalesPrice3 = 0

                if detailID == 0:
                    pk_array.append(pk)

                    priceLists_instance = PriceList.objects.get(
                        CompanyID=CompanyID, pk=pk)

                    PriceListID = priceLists_instance.PriceListID
                    AutoBarcode = priceLists_instance.AutoBarcode

                    priceLists_instance.UnitID = UnitID
                    priceLists_instance.MRP = MRP
                    priceLists_instance.SalesPrice = SalesPrice
                    priceLists_instance.PurchasePrice = PurchasePrice
                    priceLists_instance.MultiFactor = MultiFactor
                    priceLists_instance.Barcode = Barcode
                    priceLists_instance.SalesPrice1 = SalesPrice1
                    priceLists_instance.SalesPrice2 = SalesPrice2
                    priceLists_instance.SalesPrice3 = SalesPrice3
                    priceLists_instance.SalesPrice3 = SalesPrice3
                    priceLists_instance.Action = Action
                    priceLists_instance.DefaultUnit = DefaultUnit
                    priceLists_instance.UnitInSales = UnitInSales
                    priceLists_instance.UnitInPurchase = UnitInPurchase
                    priceLists_instance.UnitInReports = UnitInReports
                    priceLists_instance.CreatedUserID = CreatedUserID
                    priceLists_instance.UpdatedDate = today

                    priceLists_instance.save()

                    PriceList_Log.objects.create(
                        TransactionID=PriceListID,
                        BranchID=BranchID,
                        ProductID=ProductID,
                        UnitID=UnitID,
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
                        CompanyID=CompanyID,
                    )
                else:
                    PriceListID = get_auto_priceListid(
                        PriceList, BranchID, CompanyID)
                    AutoBarcode = get_auto_AutoBarcode(
                        PriceList, BranchID, CompanyID)

                    priceInstance = PriceList.objects.create(
                        PriceListID=PriceListID,
                        BranchID=BranchID,
                        ProductID=ProductID,
                        product=product_instance,
                        UnitID=UnitID,
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
                        MRP=MRP,
                        Action="A",
                        DefaultUnit=DefaultUnit,
                        UnitInSales=UnitInSales,
                        UnitInPurchase=UnitInPurchase,
                        UnitInReports=UnitInReports,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                    )

                    priceId = priceInstance.id
                    pk_array.append(priceId)

                    PriceList_Log.objects.create(
                        TransactionID=PriceListID,
                        BranchID=BranchID,
                        ProductID=ProductID,
                        UnitID=UnitID,
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
                        Action="A",
                        DefaultUnit=DefaultUnit,
                        UnitInSales=UnitInSales,
                        UnitInPurchase=UnitInPurchase,
                        UnitInReports=UnitInReports,
                        CreatedUserID=CreatedUserID,
                        CompanyID=CompanyID,
                    )

            price_ToDelete = PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).exclude(pk__in=pk_array)

            for PD in price_ToDelete:
                PD.delete()

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product',
                         'Edit', 'Product Updated successfully.', 'Product Updated successfully.')

            response_data = {
                "StatusCode": 6000,
                "message": "Product Updated Successfully!!!",
            }

            return Response(response_data, status=status.HTTP_200_OK)

        else:

            if not product_ok:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Product',
                             'Edit', 'Product Updated Failed.', 'Product Name Already exist with this Branch')
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Name Already exist with this Branch"
                }
                return Response(response_data, status=status.HTTP_200_OK)
            elif not productCode_ok:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Product',
                             'Edit', 'Product Updated Failed.', 'Product Code Already exist with this Branch')
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Code Already exist with this Branch"
                }
                return Response(response_data, status=status.HTTP_200_OK)
            elif not product_ok and not productCode_ok:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Product', 'Edit',
                             'Product Updated Failed.', 'Product Code and Product Name Already exist with this Branch')
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Name and Product Code Already exist with this Branch"
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                product_instance.ProductName = ProductName
                product_instance.DisplayName = DisplayName
                product_instance.Description = Description
                product_instance.ProductGroupID = ProductGroupID
                product_instance.BrandID = BrandID
                product_instance.InventoryType = InventoryType
                product_instance.VatID = VatID
                product_instance.MinimumSalesPrice = MinimumSalesPrice
                product_instance.StockMinimum = StockMinimum
                product_instance.StockReOrder = StockReOrder
                product_instance.StockMaximum = StockMaximum
                product_instance.MarginPercent = MarginPercent
                product_instance.ProductImage = ProductImage
                product_instance.Active = Active
                product_instance.IsRawMaterial = IsRawMaterial
                product_instance.IsWeighingScale = IsWeighingScale
                product_instance.WeighingCalcType = WeighingCalcType
                product_instance.PLUNo = PLUNo
                product_instance.GST = GST
                product_instance.Tax1 = Tax1
                product_instance.Tax2 = Tax2
                product_instance.Tax3 = Tax3
                product_instance.IsFavourite = IsFavourite
                product_instance.IsFinishedProduct = IsFinishedProduct
                product_instance.IsSales = IsSales
                product_instance.IsPurchase = IsPurchase
                product_instance.Action = Action
                product_instance.CreatedUserID = CreatedUserID
                product_instance.UpdatedDate = today
                product_instance.IsKFC = IsKFC
                product_instance.HSNCode = HSNCode
                product_instance.save()

                Product_Log.objects.create(
                    TransactionID=ProductID,
                    BranchID=BranchID,
                    ProductCode=ProductCode,
                    ProductName=ProductName,
                    DisplayName=DisplayName,
                    Description=Description,
                    ProductGroupID=ProductGroupID,
                    BrandID=BrandID,
                    InventoryType=InventoryType,
                    VatID=VatID,
                    MinimumSalesPrice=MinimumSalesPrice,
                    StockMinimum=StockMinimum,
                    StockReOrder=StockReOrder,
                    StockMaximum=StockMaximum,
                    MarginPercent=MarginPercent,
                    ProductImage=ProductImage,
                    Active=Active,
                    IsWeighingScale=IsWeighingScale,
                    IsRawMaterial=IsRawMaterial,
                    IsFinishedProduct=IsFinishedProduct,
                    IsSales=IsSales,
                    IsPurchase=IsPurchase,
                    WeighingCalcType=WeighingCalcType,
                    PLUNo=PLUNo,
                    IsFavourite=IsFavourite,
                    CreatedDate=today,
                    UpdatedDate=today,
                    CreatedUserID=CreatedUserID,
                    GST=GST,
                    Tax1=Tax1,
                    Tax2=Tax2,
                    Tax3=Tax3,
                    Action=Action,
                    CompanyID=CompanyID,
                    IsKFC=IsKFC,
                    HSNCode=HSNCode,
                )

                try:
                    priceListDetails = json.loads(data["PriceListDetails"])
                except:
                    priceListDetails = data["PriceListDetails"]

                pk_array = []

                for priceListDetail in priceListDetails:

                    pk = priceListDetail["id"]
                    UnitID = priceListDetail['UnitID']
                    SalesPrice = priceListDetail['SalesPrice']
                    PurchasePrice = priceListDetail['PurchasePrice']
                    MultiFactor = priceListDetail['MultiFactor']
                    Barcode = priceListDetail['Barcode']
                    SalesPrice1 = priceListDetail['SalesPrice1']
                    SalesPrice2 = priceListDetail['SalesPrice2']
                    SalesPrice3 = priceListDetail['SalesPrice3']
                    DefaultUnit = priceListDetail['DefaultUnit']
                    UnitInSales = priceListDetail['UnitInSales']
                    UnitInPurchase = priceListDetail['UnitInPurchase']
                    UnitInReports = priceListDetail['UnitInReports']
                    detailID = priceListDetail['detailID']

                    if SalesPrice1 == '':
                        SalesPrice1 = 0
                    if SalesPrice2 == '':
                        SalesPrice2 = 0
                    if SalesPrice3 == '':
                        SalesPrice3 = 0

                    if detailID == 0:

                        pk_array.append(pk)

                        priceLists_instance = PriceList.objects.get(
                            CompanyID=CompanyID, pk=pk)

                        PriceListID = priceLists_instance.PriceListID
                        AutoBarcode = priceLists_instance.AutoBarcode

                        priceLists_instance.UnitID = UnitID
                        priceLists_instance.SalesPrice = SalesPrice
                        priceLists_instance.PurchasePrice = PurchasePrice
                        priceLists_instance.MultiFactor = MultiFactor
                        priceLists_instance.Barcode = Barcode
                        priceLists_instance.SalesPrice1 = SalesPrice1
                        priceLists_instance.SalesPrice2 = SalesPrice2
                        priceLists_instance.SalesPrice3 = SalesPrice3
                        priceLists_instance.SalesPrice3 = SalesPrice3
                        priceLists_instance.Action = Action
                        priceLists_instance.DefaultUnit = DefaultUnit
                        priceLists_instance.UnitInSales = UnitInSales
                        priceLists_instance.UnitInPurchase = UnitInPurchase
                        priceLists_instance.UnitInReports = UnitInReports
                        priceLists_instance.CreatedUserID = CreatedUserID
                        priceLists_instance.UpdatedDate = today

                        priceLists_instance.save()

                        PriceList_Log.objects.create(
                            TransactionID=PriceListID,
                            BranchID=BranchID,
                            ProductID=ProductID,
                            UnitID=UnitID,
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
                            CompanyID=CompanyID,
                        )

                    else:
                        PriceListID = get_auto_priceListid(
                            PriceList, BranchID, CompanyID)
                        AutoBarcode = get_auto_AutoBarcode(
                            PriceList, BranchID, CompanyID)

                        priceInstance = PriceList.objects.create(
                            PriceListID=PriceListID,
                            BranchID=BranchID,
                            ProductID=ProductID,
                            product=product_instance,
                            UnitID=UnitID,
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
                            MRP=MRP,
                            Action="A",
                            DefaultUnit=DefaultUnit,
                            UnitInSales=UnitInSales,
                            UnitInPurchase=UnitInPurchase,
                            UnitInReports=UnitInReports,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                        priceId = priceInstance.id
                        pk_array.append(priceId)

                        PriceList_Log.objects.create(
                            TransactionID=PriceListID,
                            BranchID=BranchID,
                            ProductID=ProductID,
                            UnitID=UnitID,
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
                            Action="A",
                            DefaultUnit=DefaultUnit,
                            UnitInSales=UnitInSales,
                            UnitInPurchase=UnitInPurchase,
                            UnitInReports=UnitInReports,
                            CreatedUserID=CreatedUserID,
                            CompanyID=CompanyID,
                        )

                price_ToDelete = PriceList.objects.filter(
                    CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).exclude(pk__in=pk_array)

                for PD in price_ToDelete:
                    PD.delete()

                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product',
                             'Edit', 'Product Updated successfully.', 'Product Updated successfully.')
                response_data = {
                    "StatusCode": 6000,
                    "message": "Product Updated Successfully!!!",
                }

                return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": generate_serializer_errors(product_serialized._errors)
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def products(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Active=True).exists():
            instances = Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Active=True)
            serialized = ProductRestSerializer(instances, many=True, context={
                                               "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding})

            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product',
                         'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Product',
                         'List', 'Product List Viewed Failed.', 'Product Not Found in this Branch!')
            response_data = {
                "StatusCode": 6001,
                "message": "Product Not Found in this Branch!!"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def product(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    if Product.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        instance = Product.objects.get(CompanyID=CompanyID, pk=pk)
        serialized = SingleProductRestSerializer(instance, context={
            "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding})

        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product',
                     'View', 'Product Single Viewed successfully.', 'Product Single Viewed successfully.')
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        #request , company, log_type, user, source, action, message, description
        activity_log(request._request, CompanyID, 'Warning', CreatedUserID,
                     'Product', 'View', 'Product Single Viewed Failed.', 'Product Not Found.')
        response_data = {
            "StatusCode": 6001,
            "message": "Product Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def get_single_product_barcode(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    BarCode = data['BarCode']
    BranchID = data['BranchID']

    if PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, AutoBarcode=BarCode).exists():
        ProductID = PriceList.objects.get(
            CompanyID=CompanyID, BranchID=BranchID, AutoBarcode=BarCode).ProductID
        instance = Product.objects.get(
            CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
        serialized = SingleProductRestSerializer(instance, context={
            "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding})
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    elif PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Barcode=BarCode).exists():
        ProductID = PriceList.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, Barcode=BarCode).first().ProductID
        instance = Product.objects.get(
            CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
        serialized = SingleProductRestSerializer(instance, context={
            "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding})
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    elif Product.objects.filter(CompanyID=CompanyID, ProductCode=BarCode, BranchID=BranchID).exists():
        ProductID = Product.objects.get(
            CompanyID=CompanyID, BranchID=BranchID, ProductCode=BarCode).ProductID
        instance = Product.objects.get(
            CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
        serialized = SingleProductRestSerializer(instance, context={
            "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding})
        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Product Not Found!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def delete_product(request, pk):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']

    today = datetime.datetime.now()
    product_instance = None
    priceLists_instance = None
    purchaseDetails_exist = None
    purchaseOrderDetails_exist = None
    salesDetails_exist = None
    salesOrderDetails_exist = None
    stockPostings_exist = None

    if Product.objects.filter(CompanyID=CompanyID, pk=pk).exists():
        product_instance = Product.objects.get(CompanyID=CompanyID, pk=pk)
        ProductID = product_instance.ProductID
        BranchID = product_instance.BranchID

        ProductCode = product_instance.ProductCode
        ProductName = product_instance.ProductName
        DisplayName = product_instance.DisplayName
        Description = product_instance.Description
        ProductGroupID = product_instance.ProductGroupID
        BrandID = product_instance.BrandID
        InventoryType = product_instance.InventoryType
        VatID = product_instance.VatID
        StockMinimum = product_instance.StockMinimum
        StockReOrder = product_instance.StockReOrder
        StockMaximum = product_instance.StockMaximum
        MarginPercent = product_instance.MarginPercent
        ProductImage = product_instance.ProductImage
        Active = product_instance.Active
        IsRawMaterial = product_instance.IsRawMaterial
        IsFinishedProduct = product_instance.IsFinishedProduct
        IsSales = product_instance.IsSales
        IsPurchase = product_instance.IsPurchase
        IsWeighingScale = product_instance.IsWeighingScale
        WeighingCalcType = product_instance.WeighingCalcType
        PLUNo = product_instance.PLUNo
        GST = product_instance.GST
        Tax1 = product_instance.Tax1
        Tax2 = product_instance.Tax2
        Tax3 = product_instance.Tax3
        IsFavourite = product_instance.IsFavourite
        IsKFC = product_instance.IsKFC
        HSNCode = product_instance.HSNCode

        Action = "D"

        purchaseDetails_exist = PurchaseDetails.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists()
        purchaseOrderDetails_exist = PurchaseOrderDetails.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists()
        salesDetails_exist = SalesDetails.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists()
        salesOrderDetails_exist = SalesOrderDetails.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists()
        stockPostings_exist = StockPosting.objects.filter(
            CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists()

        if not purchaseDetails_exist and not purchaseOrderDetails_exist and not salesDetails_exist and not salesOrderDetails_exist and not stockPostings_exist:

            product_instance.delete()

            Product_Log.objects.create(
                TransactionID=ProductID,
                BranchID=BranchID,
                ProductCode=ProductCode,
                ProductName=ProductName,
                DisplayName=DisplayName,
                Description=Description,
                ProductGroupID=ProductGroupID,
                BrandID=BrandID,
                InventoryType=InventoryType,
                VatID=VatID,
                StockMinimum=StockMinimum,
                StockReOrder=StockReOrder,
                StockMaximum=StockMaximum,
                MarginPercent=MarginPercent,
                ProductImage=ProductImage,
                Active=Active,
                IsWeighingScale=IsWeighingScale,
                IsRawMaterial=IsRawMaterial,
                IsFinishedProduct=IsFinishedProduct,
                IsSales=IsSales,
                IsPurchase=IsPurchase,
                WeighingCalcType=WeighingCalcType,
                PLUNo=PLUNo,
                IsFavourite=IsFavourite,
                CreatedDate=today,
                UpdatedDate=today,
                CreatedUserID=CreatedUserID,
                GST=GST,
                Tax1=Tax1,
                Tax2=Tax2,
                Tax3=Tax3,
                Action=Action,
                CompanyID=CompanyID,
                IsKFC=IsKFC,
                HSNCode=HSNCode,
            )

            priceLists_instances = PriceList.objects.filter(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)

            for priceLists_instance in priceLists_instances:

                PriceListID = priceLists_instance.PriceListID
                BranchID = priceLists_instance.BranchID
                ProductID = priceLists_instance.ProductID
                UnitName = priceLists_instance.UnitName
                SalesPrice = priceLists_instance.SalesPrice
                PurchasePrice = priceLists_instance.PurchasePrice
                MultiFactor = priceLists_instance.MultiFactor
                Barcode = priceLists_instance.Barcode
                AutoBarcode = priceLists_instance.AutoBarcode
                SalesPrice1 = priceLists_instance.SalesPrice1
                SalesPrice2 = priceLists_instance.SalesPrice2
                SalesPrice3 = priceLists_instance.SalesPrice3
                DefaultUnit = priceLists_instance.DefaultUnit
                UnitInSales = priceLists_instance.UnitInSales
                UnitInPurchase = priceLists_instance.UnitInPurchase
                UnitInReports = priceLists_instance.UnitInReports

                priceLists_instance.delete()

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
                    CompanyID=CompanyID,
                )

            if Batch.objects.filter(ProductID=ProductID).exists():
                batch_ins = Batch.objects.filter(ProductID=ProductID)
                for i in batch_ins:
                    i.delete()
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product',
                         'Deleted', 'Product Deleted successfully.', 'Product Deleted successfully.')

            response_data = {
                "StatusCode": 6000,
                "title": "Success",
                "message": "Product Deleted Successfully!"
            }

        else:
            #request , company, log_type, user, source, action, message, description
            activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Product', 'Deleted',
                         'Product Deleted Failed.', 'You Cant Delete this Product,this ProductID is using somewhere')
            response_data = {
                "StatusCode": 6001,
                "title": "Failed",
                "message": "You Cant Delete this Product,this ProductID is using somewhere!!"
            }
    else:
        response_data = {
            "StatusCode": 6001,
            "title": "Failed",
            "message": "Product Not Fount!"
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def upload_product(request):
    today = datetime.datetime.now()

    data = request.data
    # serializer = UploadSerializer(data=request.data)
    # if serializer.is_valid():
    CompanyID = data['CompanyID']
    CreatedUserID = data['CreatedUserID']
    input_excel = data['file']

    BranchID = 1
    filepath = os.path.join(
        settings.MEDIA_ROOT, in_memory_file_to_temp(
            input_excel)
    )

    filepath_url = os.path.join(settings.MEDIA_ROOT, filepath)

    task = import_product_task.delay(
        filepath_url, CompanyID, CreatedUserID, BranchID)
    task_id = task.id
    #request , company, log_type, user, source, action, message, description
    CompanyID = get_company(CompanyID)
    activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product',
                 'Uploaded', 'Product Uploaded successfully.', 'Product Uploaded successfully.')
    response_data = {
        "StatusCode": 6000,
        "task_id": task_id,
        "message": "Product Uploaded Successfully!!!"
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def get_progress(request, task_id):
    result = AsyncResult(task_id)
    response_data = {
        'state': result.state,
        'details': result.info,
        'task_id': task_id,
    }
    return Response(response_data, status=status.HTTP_200_OK)


def call_paginator_all(model_object, page_number, items_per_page):
    paginator = Paginator(model_object, items_per_page)
    content = paginator.page(page_number)
    return content


def list_pagination(list_value, items_per_page, page_no):
    paginator_object = Paginator(list_value, items_per_page)
    get_value = paginator_object.page(page_no).object_list
    return get_value


# @api_view(['GET'])
# @permission_classes((AllowAny,))
# @renderer_classes((JSONRenderer,))
# def products(request):
#     if 'page_no' in request.GET:
#         page_number = int(request.GET['page_no'])
#     else:
#         page_number = None

#     if 'items_per_page' in request.GET:
#         items_per_page = int(request.GET['items_per_page'])
#     else:
#         items_per_page = None

#     if page_number and items_per_page:
#         product_object = models.Product.objects.filter(is_deleted=False)

#         product_sort_pagination = list_pagination(
#             product_object,
#             items_per_page,
#             page_number
#         )
#         product_serializer = pro_serializers.ProductSerializer(
#             product_sort_pagination,
#             many=True
#         )
#         data = product_serializer.data

#         data = {
#             "results": data,
#             "count": len(product_object)
#         }
#         return Response(
#             {
#                 'success': 6000,
#                 'data': data,
#                 'error': None
#             },
#             status=status.HTTP_200_OK
#         )
#     else:
#         success = False
#         error = "No Parameter Passed. Parameters are (items_per_page & page_number)"
#         return Response(
#             {
#                 'success': success,
#                 'data': None,
#                 'error': error
#             },
#             status=status.HTTP_400_BAD_REQUEST


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def products_test(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']

    page_number = data['page_no']
    items_per_page = data['items_per_page']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']

        if page_number and items_per_page:
            product_object = Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Active=True)

            product_sort_pagination = list_pagination(
                product_object,
                items_per_page,
                page_number
            )
            product_serializer = ProductRestSerializer(
                product_sort_pagination,
                many=True,
                context={"request": request, "CompanyID": CompanyID,
                         "PriceRounding": PriceRounding}
            )
            data = product_serializer.data

            ShowDescription = False
            ShowProductImage = False
            ShowDisplayName = False
            ShowGroupName = False
            ShowBrandName = False
            ShowTaxName = False
            if GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowDescription").exists():
                general_ins = GeneralSettings.objects.filter(
                    CompanyID=CompanyID, SettingsType="ShowDescription").first()
                ShowDescription = general_ins.SettingsValue

            if GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowProductImage").exists():
                general_ins = GeneralSettings.objects.filter(
                    CompanyID=CompanyID, SettingsType="ShowProductImage").first()
                ShowProductImage = general_ins.SettingsValue

            if GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowDisplayName").exists():
                general_ins = GeneralSettings.objects.filter(
                    CompanyID=CompanyID, SettingsType="ShowDisplayName").first()
                ShowDisplayName = general_ins.SettingsValue

            if GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowGroupName").exists():
                general_ins = GeneralSettings.objects.filter(
                    CompanyID=CompanyID, SettingsType="ShowGroupName").first()
                ShowGroupName = general_ins.SettingsValue

            if GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowBrandName").exists():
                general_ins = GeneralSettings.objects.filter(
                    CompanyID=CompanyID, SettingsType="ShowBrandName").first()
                ShowBrandName = general_ins.SettingsValue

            if GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowTaxName").exists():
                general_ins = GeneralSettings.objects.filter(
                    CompanyID=CompanyID, SettingsType="ShowTaxName").first()
                ShowTaxName = general_ins.SettingsValue

            if not data == None:
                response_data = {
                    "StatusCode": 6000,
                    "data": data,
                    "count": len(product_object),
                    "ShowDescription": ShowDescription,
                    "ShowProductImage": ShowProductImage,
                    "ShowDisplayName": ShowDisplayName,
                    "ShowGroupName": ShowGroupName,
                    "ShowBrandName": ShowBrandName,
                    "ShowTaxName": ShowTaxName,
                }
    else:
        response_data = {
            "StatusCode": 6001
        }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def products_search(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    product_name = data['product_name']
    length = data['length']
    try:
        type = data['type']
    except:
        type = "any"

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        check_EnableProductBatchWise = False
        if type == "Sales":
            print("chechkkkkkkkkkkkkkkkkk")
            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Active=True, IsSales=True).exists():
                if length < 3:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, Active=True, ProductName__icontains=product_name, IsSales=True)[:10]
                else:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, Active=True, ProductName__icontains=product_name, IsSales=True)

                product_ids = []
                for p in instances:
                    Stock = 0
                    ProductID = p.ProductID
                    check_EnableProductBatchWise = False
                    if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
                        check_EnableProductBatchWise = GeneralSettings.objects.get(
                            CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue
                    print("/./.../.././././.././././../")
                    print(check_EnableProductBatchWise)
                    if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                        if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():

                            Batch_ins = Batch.objects.filter(
                                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                            total_stockIN = 0
                            total_stockOUT = 0
                            for b in Batch_ins:
                                total_stockIN += float(b.StockIn)
                                total_stockOUT += float(b.StockOut)

                            Stock = float(total_stockIN) - \
                                float(total_stockOUT)
                        elif StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID):
                            stock_ins = StockPosting.objects.filter(
                                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                            total_stockIN = 0
                            total_stockOUT = 0
                            for s in stock_ins:
                                total_stockIN += float(s.QtyIn)
                                total_stockOUT += float(s.QtyOut)

                            Stock = float(total_stockIN) - \
                                float(total_stockOUT)
                    else:
                        print("########################correct")
                        if StockPosting.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID):
                            stock_ins = StockPosting.objects.filter(
                                CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                            total_stockIN = 0
                            total_stockOUT = 0
                            for s in stock_ins:
                                total_stockIN += float(s.QtyIn)
                                total_stockOUT += float(s.QtyOut)

                            Stock = float(total_stockIN) - \
                                float(total_stockOUT)

                    if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
                        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="ShowNegativeBatchInSales").exists():
                            check_ShowNegativeBatchInSales = GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="ShowNegativeBatchInSales").SettingsValue
                            if check_ShowNegativeBatchInSales == "False" or check_ShowNegativeBatchInSales == False:
                                if Stock > 0:
                                    product_ids.append(ProductID)
                            else:
                                product_ids.append(ProductID)
                    else:
                        if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="AllowNegativeStockSales").exists():
                            check_AllowNegativeStockSales = GeneralSettings.objects.get(
                                CompanyID=CompanyID, SettingsType="AllowNegativeStockSales").SettingsValue
                            print("check_AllowNegativeStockSales")
                            print(check_AllowNegativeStockSales)
                            if check_AllowNegativeStockSales == "False" or check_AllowNegativeStockSales == False:
                                if Stock > 0:
                                    product_ids.append(ProductID)
                                else:
                                    product_ids.append(ProductID)
                            else:
                                product_ids.append(ProductID)

                if product_ids:
                    print(product_ids)
                    if length < 3:
                        instances = Product.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_ids)
                    else:
                        instances = instances.filter(ProductID__in=product_ids)
                    serialized = ProductRestSerializer(instances, many=True, context={
                                                       "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding})

                    #request , company, log_type, user, source, action, message, description
                    # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product', 'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
                    response_data = {
                        "StatusCode": 6000,
                        "data": serialized.data
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    print("=======================////////")
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Product Not Found with Stock!!"
                    }

                    return Response(response_data, status=status.HTTP_200_OK)
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Product',
                             'List', 'Product List Viewed Failed.', 'Product Not Found in this Branch!')
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Not Found in this Branch!!"
                }

                return Response(response_data, status=status.HTTP_200_OK)
        elif type == "Purchase":
            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Active=True, IsPurchase=True).exists():
                if length < 3:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, Active=True, ProductName__icontains=product_name, IsPurchase=True)[:10]
                else:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, Active=True, ProductName__icontains=product_name, IsPurchase=True)
                serialized = ProductRestSerializer(instances, many=True, context={
                                                   "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding})

                #request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product', 'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
                response_data = {
                    "StatusCode": 6000,
                    "data": serialized.data
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Product',
                             'List', 'Product List Viewed Failed.', 'Product Not Found in this Branch!')
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Not Found in this Branch!!"
                }

                return Response(response_data, status=status.HTTP_200_OK)
        elif type == "WorkOrder":
            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
                if length < 3:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductName__icontains=product_name)[:10]
                else:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductName__icontains=product_name)
                serialized = ProductRestSerializer(instances, many=True, context={
                                                   "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding})

                #request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product', 'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
                response_data = {
                    "StatusCode": 6000,
                    "data": serialized.data
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Product',
                             'List', 'Product List Viewed Failed.', 'Product Not Found in this Branch!')
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Not Found in this Branch!!"
                }

                return Response(response_data, status=status.HTTP_200_OK)
        else:
            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
                if length < 3:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductName__icontains=product_name)[:10]
                else:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductName__icontains=product_name)
                serialized = ProductRestSerializer(instances, many=True, context={
                                                   "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding})

                #request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product', 'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
                response_data = {
                    "StatusCode": 6000,
                    "data": serialized.data
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                #request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Warning', CreatedUserID, 'Product',
                             'List', 'Product List Viewed Failed.', 'Product Not Found in this Branch!')
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Not Found in this Branch!!"
                }

                return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def products_search_shortcut(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    product_name = data['product_name']
    WarehouseID = data['WarehouseID']
    length = data['length']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if WarehouseID:
            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
                if length < 3:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID)
                    instances = instances.filter((Q(ProductName__icontains=product_name)) | (
                        Q(ProductCode__icontains=product_name)))[:10]
                else:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID)
                    instances = instances.filter((Q(ProductName__icontains=product_name)) | (
                        Q(ProductCode__icontains=product_name)))
                serialized = ProductSearchShortcutSerializer(instances, many=True, context={
                                                             "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding, "WarehouseID": WarehouseID, "product_name": "product_name"})

                #request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product', 'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
        else:
            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
                if length < 3:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID)
                    instances = instances.filter((Q(ProductName__icontains=product_name)) | (
                        Q(ProductCode__icontains=product_name)))[:10]
                else:
                    instances = Product.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID)
                    instances = instances.filter((Q(ProductName__icontains=product_name)) | (
                        Q(ProductCode__icontains=product_name)))
                serialized = ProductSearchShortcutSerializer(instances, many=True, context={
                                                             "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding, "product_name": "product_name"})

        response_data = {
            "StatusCode": 6000,
            "data": serialized.data
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def products_search_shortcut_barcode(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    product_name = data['product_name']
    WarehouseID = data['WarehouseID']
    length = data['length']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if WarehouseID:
            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
                instances = Product.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductCode=product_name).exists():
                    if length < 3:
                        instances = Product.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID)
                        instances = instances.filter((Q(ProductName__icontains=product_name)) | (
                            Q(ProductCode__icontains=product_name)))[:10]
                    else:
                        instances = Product.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID)
                        instances = instances.filter((Q(ProductName__icontains=product_name)) | (
                            Q(ProductCode__icontains=product_name)))
                    serialized = ProductSearchShortcutSerializer(instances, many=True, context={
                                                                 "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding, "WarehouseID": WarehouseID, "product_name": product_name})
                    data = serialized.data
                else:
                    serialized = ProductSearchShortcutSerializer(instances, many=True, context={
                                                                 "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding, "WarehouseID": WarehouseID, "product_name": product_name})
                    data = []
                    # 435345
                    print(serialized.data, "1751")
                    print(type(serialized.data), "1751")
                    for i in serialized.data:
                        if i["DefBarcode"] == str(product_name):
                            print("qwerty")
                            DefBarcode = i['DefBarcode']
                            ProductName = i['ProductName']
                            ProductCode = i['ProductCode']
                            PurchasePrice = i['PurchasePrice']
                            SalesPrice = i['SalesPrice']
                            Quantity = i['Quantity']
                            dic = {
                                'DefBarcode': DefBarcode,
                                'ProductName': ProductName,
                                'ProductCode': ProductCode,
                                'PurchasePrice': PurchasePrice,
                                'SalesPrice': SalesPrice,
                                'Quantity': Quantity,
                            }
                            data.append(dic)
                #request , company, log_type, user, source, action, message, description
                # activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product', 'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
        else:
            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
                instances = Product.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID)
                if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductCode=product_name).exists():
                    if length < 3:
                        instances = Product.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID)
                        instances = instances.filter((Q(ProductName__icontains=product_name)) | (
                            Q(ProductCode__icontains=product_name)))[:10]
                    else:
                        instances = Product.objects.filter(
                            CompanyID=CompanyID, BranchID=BranchID)
                        instances = instances.filter((Q(ProductName__icontains=product_name)) | (
                            Q(ProductCode__icontains=product_name)))
                    serialized = ProductSearchShortcutSerializer(instances, many=True, context={
                                                                 "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding, "product_name": "product_name"})
                    data = serialized.data
                else:
                    serialized = ProductSearchShortcutSerializer(instances, many=True, context={
                                                                 "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding, "product_name": "product_name"})
                    data = []
                    # 435345
                    print(serialized.data, "1751")
                    print(type(serialized.data), "1751")
                    for i in serialized.data:
                        if i["DefBarcode"] == str(product_name):
                            print("qwerty")
                            DefBarcode = i['DefBarcode']
                            ProductName = i['ProductName']
                            ProductCode = i['ProductCode']
                            PurchasePrice = i['PurchasePrice']
                            SalesPrice = i['SalesPrice']
                            Quantity = i['Quantity']
                            dic = {
                                'DefBarcode': DefBarcode,
                                'ProductName': ProductName,
                                'ProductCode': ProductCode,
                                'PurchasePrice': PurchasePrice,
                                'SalesPrice': SalesPrice,
                                'Quantity': Quantity,
                            }
                            data.append(dic)

                # request , company, log_type, user, source, action, message, description
                activity_log(request._request, CompanyID, 'Information', CreatedUserID, 'Product',
                             'List', 'Product List Viewed successfully.', 'Product List Viewed successfully.')
        response_data = {
            "StatusCode": 6000,
            "data": data
        }

        return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def list_productsUnderGroups(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    GroupIDs = data['GroupIDs']
    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductGroupID__in=GroupIDs).exists():
            instances = Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductGroupID__in=GroupIDs)
            print("instances###################")
            print(instances)
            serialized = ProductbyGrouptSerializer(instances, many=True, context={
                                                   "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding})

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Product Not Found under this Groups"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def list_productsbyBarcode(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    PriceRounding = data['PriceRounding']
    Barcode = data['Barcode']
    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']
        if PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, AutoBarcode=Barcode).exists():
            ProductID = PriceList.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, AutoBarcode=Barcode).first().ProductID

            if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
                instance = Product.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                serialized = ProductbyGrouptSerializer(instance, context={
                                                       "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding})

                response_data = {
                    "StatusCode": 6000,
                    "data": serialized.data,
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Not Found under this Barcode"
                }

                return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Product Not Found under this Barcode"
            }

            return Response(response_data, status=status.HTTP_200_OK)
    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def get_product_barcode(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    BranchID = data['BranchID']
    BarCode = data['BarCode']
    PriceRounding = data['PriceRounding']
    # try:
    #     WarehouseID = data['WarehouseID']
    # except:
    #     WarehouseID = 1

    check_EnableProductBatchWise = False

    if GeneralSettings.objects.filter(CompanyID=CompanyID, BranchID=BranchID, SettingsType="EnableProductBatchWise").exists():
        check_EnableProductBatchWise = GeneralSettings.objects.get(
            CompanyID=CompanyID, SettingsType="EnableProductBatchWise").SettingsValue

    if BarCode.isnumeric():
        if check_EnableProductBatchWise == "True" or check_EnableProductBatchWise == True:
            if Batch.objects.filter(CompanyID=CompanyID, BatchCode=BarCode, BranchID=BranchID).exists():
                ProductID = Batch.objects.get(
                    CompanyID=CompanyID, BatchCode=BarCode, BranchID=BranchID).ProductID
                if Product.objects.filter(CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID).exists():
                    instance = Product.objects.get(
                        CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)
                    serialized = BarCodeSearchSerializer(instance, context={
                                                         "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding, "BarCode": BarCode})

                    batch_ins = Batch.objects.get(
                        CompanyID=CompanyID, BranchID=BranchID, BatchCode=BarCode)

                    stock = float(batch_ins.StockIn) - \
                        float(batch_ins.StockOut)
                    response_data = {
                        "StatusCode": 6000,
                        "data": serialized.data,
                        "BatchCode": BarCode,
                        "Stock": stock,
                    }
                else:
                    response_data = {
                        "StatusCode": 6001,
                        "message": "Product Not Found!"
                    }
            elif PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, AutoBarcode=BarCode).exists():
                ProductID = PriceList.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, AutoBarcode=BarCode).ProductID
                instance = Product.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)
                serialized = BarCodeSearchSerializer(instance, context={
                                                     "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding, "BarCode": BarCode})
                response_data = {
                    "StatusCode": 6000,
                    "data": serialized.data
                }
            elif PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Barcode=BarCode).exists():
                ProductID = PriceList.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, Barcode=BarCode).first().ProductID
                instance = Product.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)
                serialized = BarCodeSearchSerializer(instance, context={
                                                     "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding, "BarCode": BarCode})
                response_data = {
                    "StatusCode": 6000,
                    "data": serialized.data
                }

            elif Product.objects.filter(CompanyID=CompanyID, ProductCode=BarCode, BranchID=BranchID).exists():
                ProductID = Product.objects.get(
                    CompanyID=CompanyID, BranchID=BranchID, ProductCode=BarCode).ProductID
                instance = Product.objects.get(
                    CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)
                serialized = BarCodeSearchSerializer(instance, context={
                                                     "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding, "BarCode": BarCode})
                response_data = {
                    "StatusCode": 6000,
                    "data": serialized.data
                }
            else:
                response_data = {
                    "StatusCode": 6001,
                    "message": "Product Not Found!"
                }

        elif PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, AutoBarcode=BarCode).exists():
            ProductID = PriceList.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, AutoBarcode=BarCode).ProductID
            instance = Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)
            serialized = BarCodeSearchSerializer(instance, context={
                                                 "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding, "BarCode": BarCode})
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }
        elif PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Barcode=BarCode).exists():
            ProductID = PriceList.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Barcode=BarCode).first().ProductID
            instance = Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)
            serialized = BarCodeSearchSerializer(instance, context={
                                                 "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding, "BarCode": BarCode})
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

        elif Product.objects.filter(CompanyID=CompanyID, ProductCode=BarCode, BranchID=BranchID).exists():
            ProductID = Product.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, ProductCode=BarCode).ProductID
            instance = Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)
            serialized = BarCodeSearchSerializer(instance, context={
                                                 "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding, "BarCode": BarCode})
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Product Not Found!"
            }

    else:
        if Product.objects.filter(CompanyID=CompanyID, ProductCode=BarCode, BranchID=BranchID).exists():
            ProductID = Product.objects.get(
                CompanyID=CompanyID, BranchID=BranchID, ProductCode=BarCode).ProductID
            instance = Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)
            serialized = BarCodeSearchSerializer(instance, context={
                                                 "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding, "BarCode": BarCode})
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }
        elif PriceList.objects.filter(CompanyID=CompanyID, BranchID=BranchID, Barcode=BarCode).exists():
            ProductID = PriceList.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, Barcode=BarCode).first().ProductID
            instance = Product.objects.get(
                CompanyID=CompanyID, ProductID=ProductID, BranchID=BranchID)
            serialized = BarCodeSearchSerializer(instance, context={
                                                 "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding, "BarCode": BarCode})
            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Product Not Found!"
            }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def products_search_batch(request):
    data = request.data
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    PriceRounding = data['PriceRounding']
    product_name = data['product_name']
    length = data['length']
    type = data['type']

    serialized1 = ListSerializer(data=request.data)
    if serialized1.is_valid():
        BranchID = serialized1.data['BranchID']

        if Product.objects.filter(CompanyID=CompanyID, BranchID=BranchID).exists():
            if length < 3:
                instances = Product.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductName__icontains=product_name)[:10]
            else:
                instances = Product.objects.filter(
                    CompanyID=CompanyID, BranchID=BranchID, ProductName__icontains=product_name)

            product_ids = []
            for p in instances:
                ProductID = p.ProductID
                if Batch.objects.filter(CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID).exists():
                    batch_ins = Batch.objects.filter(
                        CompanyID=CompanyID, BranchID=BranchID, ProductID=ProductID)
                    Stock = 0
                    TotalStockIn = 0
                    TotalStockOut = 0
                    for b in batch_ins:
                        TotalStockIn += float(b.StockIn)
                        TotalStockOut += float(b.StockOut)

                    Stock = float(TotalStockIn) - float(TotalStockOut)
                    if float(Stock) > 0:
                        product_ids.append(ProductID)

            instances = Product.objects.filter(
                CompanyID=CompanyID, BranchID=BranchID, ProductID__in=product_ids)

            serialized = ProductRestSerializer(instances, many=True, context={
                                               "request": request, "CompanyID": CompanyID, "PriceRounding": PriceRounding})

            response_data = {
                "StatusCode": 6000,
                "data": serialized.data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
                "StatusCode": 6001,
                "message": "Product Not Found in this Branch!!"
            }

            return Response(response_data, status=status.HTTP_200_OK)

    else:
        response_data = {
            "StatusCode": 6001,
            "message": "Branch ID You Enterd is not Valid!!!"
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def products_update(request):
    data = request.data
    today = datetime.datetime.now()
    CompanyID = data['CompanyID']
    CompanyID = get_company(CompanyID)
    CreatedUserID = data['CreatedUserID']
    ShowDescription = data['ShowDescription']
    ShowProductImage = data['ShowProductImage']
    ShowDisplayName = data['ShowDisplayName']
    ShowGroupName = data['ShowGroupName']
    ShowBrandName = data['ShowBrandName']
    ShowTaxName = data['ShowTaxName']

    print("ShowDescription########")
    print(ShowDescription)

    def max_id():
        general_settings_id = GeneralSettings.objects.filter(
            CompanyID=CompanyID).aggregate(Max('GeneralSettingsID'))
        general_settings_id = general_settings_id.get(
            'GeneralSettingsID__max', 0)
        general_settings_id += 1
        return general_settings_id

    if not GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowDescription").exists():
        Action = "A"
        GeneralSettings.objects.create(
            CompanyID=CompanyID,
            GeneralSettingsID=max_id(),
            SettingsType="ShowDescription",
            SettingsValue=ShowDescription,
            BranchID=1, GroupName="Inventory",
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            Action=Action
        )
    else:
        Action = "M"
        GeneralSettings.objects.filter(
            CompanyID=CompanyID,
            SettingsType="ShowDescription"
        ).update(
            SettingsValue=ShowDescription,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            Action=Action
        )
    if not GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowProductImage").exists():
        GeneralSettings.objects.create(
            CompanyID=CompanyID,
            GeneralSettingsID=max_id(),
            SettingsType="ShowProductImage",
            SettingsValue=ShowProductImage,
            BranchID=1, GroupName="Inventory",
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            Action=Action
        )
    else:
        GeneralSettings.objects.filter(
            CompanyID=CompanyID,
            SettingsType="ShowProductImage"
        ).update(
            SettingsValue=ShowProductImage,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            Action=Action
        )
    if not GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowDisplayName").exists():
        GeneralSettings.objects.create(
            CompanyID=CompanyID,
            GeneralSettingsID=max_id(),
            SettingsType="ShowDisplayName",
            SettingsValue=ShowDisplayName,
            BranchID=1, GroupName="Inventory",
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            Action=Action
        )
    else:
        GeneralSettings.objects.filter(
            CompanyID=CompanyID,
            SettingsType="ShowDisplayName"
        ).update(
            SettingsValue=ShowDisplayName,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            Action=Action
        )

    if not GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowGroupName").exists():
        GeneralSettings.objects.create(
            CompanyID=CompanyID,
            GeneralSettingsID=max_id(),
            SettingsType="ShowGroupName",
            SettingsValue=ShowGroupName,
            BranchID=1, GroupName="Inventory",
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            Action=Action
        )
    else:
        GeneralSettings.objects.filter(
            CompanyID=CompanyID,
            SettingsType="ShowGroupName"
        ).update(
            SettingsValue=ShowGroupName,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            Action=Action
        )
    if not GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowBrandName").exists():
        GeneralSettings.objects.create(
            CompanyID=CompanyID,
            GeneralSettingsID=max_id(),
            SettingsType="ShowBrandName",
            SettingsValue=ShowBrandName,
            BranchID=1, GroupName="Inventory",
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            Action=Action
        )
    else:
        GeneralSettings.objects.filter(
            CompanyID=CompanyID,
            SettingsType="ShowBrandName"
        ).update(
            SettingsValue=ShowBrandName,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            Action=Action
        )
    if not GeneralSettings.objects.filter(CompanyID=CompanyID, SettingsType="ShowTaxName").exists():
        GeneralSettings.objects.create(
            CompanyID=CompanyID,
            GeneralSettingsID=max_id(),
            SettingsType="ShowTaxName",
            SettingsValue=ShowTaxName,
            BranchID=1, GroupName="Inventory",
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            Action=Action
        )
    else:
        GeneralSettings.objects.filter(
            CompanyID=CompanyID,
            SettingsType="ShowTaxName"
        ).update(
            SettingsValue=ShowTaxName,
            UpdatedDate=today,
            CreatedUserID=CreatedUserID,
            Action=Action
        )

    response_data = {
        "StatusCode": 6000,
        "message": "Successfully Updated",
    }

    return Response(response_data, status=status.HTTP_200_OK)
